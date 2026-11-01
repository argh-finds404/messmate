# Design

## Architecture

The application follows a strict layered architecture: `web -> services -> repositories/adapters -> db`. A lower layer never imports from a layer above it. SQLite access is isolated inside repository classes (`MemberRepository`, `MealRepository`, `ExpenseRepository`, `PaymentRepository`), and service classes receive their repositories, strategies, gateways, and notifiers through constructor arguments so every dependency can be replaced with a mock in unit tests.

## UML Class Diagram

The full Mermaid class diagram is stored in [`docs/uml/class-diagram.md`](uml/class-diagram.md).

## Pattern 1: Strategy Pattern (Behavioral)

- **Category:** Behavioral
- **Location in code:** `app/services/billing_strategies.py`, used by `BillingService` in `app/services/billing_service.py`.

### Problem It Solves

Different messes split their monthly bazar expense in different ways—some charge strictly by per-meal rate (`total_expense / total_meals * member_meals`), while others split the total cost equally among active members or may later add guest-meal rules. `BillingService` is responsible for gathering active members, meal totals, and total expenses, and it should not have to be modified every time a new cost-splitting formula is added.

### How It Works

`BillingStrategy` is an abstract base class with a single method `calculate(meals_by_member, total_expense) -> dict[int, float]`. `PerMealRateStrategy` and `EqualSplitStrategy` implement this interface with their respective math and two-decimal rounding. `BillingService.generate_bill(month, strategy)` collects the month's data from the repositories, passes it to `strategy.calculate(...)`, and builds the list of `BillLine` objects from the returned dictionary.

### Alternative Rejected

Putting an `if strategy_name == "per_meal": ... elif strategy_name == "equal": ...` chain directly inside `BillingService.generate_bill`. That approach was rejected because adding a new billing rule would require editing already-tested `BillingService` code (violating the Open/Closed Principle) and would prevent testing the billing math separately from repository lookups.

## Pattern 2: Adapter Pattern (Structural)

- **Category:** Structural
- **Location in code:** `app/adapters/payment_gateway.py`, used by `PaymentService` in `app/services/payment_service.py`.

### Problem It Solves

External mobile-wallet SDKs (`SandboxWalletClient`) use vendor-specific method names and parameter formats (`make_payment(wallet_no, amount)` taking a formatted string) and return raw dictionaries such as `{"status": "COMPLETED", "trxID": "..."}` or `{"status": "FAILED", "error": "..."}`. If that vendor-specific dictionary shape leaked into `PaymentService`, our domain logic would be tightly coupled to one payment provider.

### How It Works

`PaymentGateway` defines the domain interface our application expects: `charge(phone, amount) -> PaymentResult`. `WalletGatewayAdapter` subclasses `PaymentGateway` and holds a `SandboxWalletClient` instance. When `charge(phone, amount)` is called, the adapter formats the amount to two decimal places, calls `client.make_payment(wallet_no=phone, amount=...)`, inspects the returned dictionary, and translates it into a typed `PaymentResult(success, reference, message)` object.

### Alternative Rejected

Calling `SandboxWalletClient.make_payment` directly inside `PaymentService.pay`. That was rejected because `PaymentService` would depend on the third-party SDK's parameter and dictionary keys, unit testing `PaymentService` would require mocking raw SDK dictionaries instead of a clean domain interface, and switching to another wallet provider would force changes inside `PaymentService`.

## Pattern 3: Factory Pattern (Creational - Simple Factory)

- **Category:** Creational (Simple Factory idiom, a simplified relative of the GoF Factory Method)
- **Location in code:** `app/services/notifier_factory.py`, creating concrete `Notifier` classes from `app/adapters/notifiers.py`.

### Problem It Solves

Whether bill notices are printed to the console (`ConsoleNotifier`) or sent via an SMS client (`SmsNotifier`) is decided by a configuration string (`Config.NOTIFY_CHANNEL`). Callers such as the web layer or CLI scripts should not need to know which concrete class to import, what constructor arguments each notifier requires, or how to validate the channel name.

### How It Works

`Notifier` is the abstract interface declaring `send(phone, message) -> None`, implemented by `ConsoleNotifier` and `SmsNotifier`. `NotifierFactory.create(channel, sms_client=None, out=print)` inspects the `channel` string in one place: it returns `ConsoleNotifier(out)` for `"console"`, validates that `sms_client` is provided and returns `SmsNotifier(sms_client)` for `"sms"`, and raises a `ValueError` for unknown channels. Note: this is the Simple Factory idiom rather than a full GoF Factory Method hierarchy or Abstract Factory.

### Alternative Rejected

Repeating `if channel == "sms": ... else: ...` conditionals in every caller that needs a `Notifier`, which duplicates construction and error-checking logic. We also rejected the full GoF Abstract Factory pattern because `messmate` only creates a single product (`Notifier`), not families of related products, so Abstract Factory would be unnecessary over-engineering.

## Also Used (Not Counted as GoF Patterns)

- **Repository (`app/repositories/`):** One repository class per SQLite table (`MemberRepository`, `MealRepository`, `ExpenseRepository`, `PaymentRepository`) keeps all SQL queries out of the service layer.
- **Constructor Dependency Injection:** Services accept their repositories, gateways, and notifiers in `__init__`, making unit testing with `unittest.mock.Mock` straightforward.
- **Service Container (`app/container.py`):** `ServiceContainer.build(conn, config)` wires SQLite connections, repositories, adapters, and services together into a single strongly-typed container stored on `app.extensions["container"]`, providing clean inversion of control to Flask route handlers.
