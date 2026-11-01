# messmate

A clean, modular hostel and mess meal management system built with Python, Flask, and SQLite.

MessMate simplifies hostel and student mess life by automating daily meal tracking, monthly bazar expense logging, multi-strategy billing calculations (per-meal rate or equal split), sandbox digital wallet payments, and SMS/console billing notices.

---

## Features & The Six Modules

1. **Member Module (`app/models/member.py`, `app/repositories/member_repository.py`, `app/services/member_service.py`):**
   Register mess boarders with validation (name, room, unique 11-digit Bangladeshi phone number starting with `01`), query members, and toggle active status.
2. **Meal Tracking Module (`app/models/meal.py`, `app/repositories/meal_repository.py`, `app/services/meal_service.py`):**
   Record daily meal counts (0–3 per active member) with strict `YYYY-MM-DD` validation and calculate monthly meal aggregations.
3. **Expense Module (`app/models/expense.py`, `app/repositories/expense_repository.py`, `app/services/expense_service.py`):**
   Log daily bazar purchases and expenses with date and positive amount checks, and compute monthly totals.
4. **Billing Module (`app/models/bill.py`, `app/services/billing_strategies.py`, `app/services/billing_service.py`):**
   Calculate monthly bills using pluggable strategies (per-meal consumption rate or equal cost split) with clean two-decimal precision.
5. **Payment Module (`app/models/payment.py`, `app/repositories/payment_repository.py`, `app/adapters/payment_gateway.py`, `app/services/payment_service.py`):**
   Process member dues via an adapter-wrapped mobile wallet gateway, persist successful transactions with transaction references, and calculate dues in real time.
6. **Notification Module (`app/adapters/notifiers.py`, `app/services/notifier_factory.py`, `app/services/notification_service.py`):**
   Generate and dispatch bill notifications to members via console or SMS using a unified notifier abstraction.

---

## Quick Start

### Prerequisites
- Python 3.10+ (tested with Python 3.13 / 3.14)
- Google Chrome browser (for Selenium end-to-end tests)

### Windows (PowerShell)
```powershell
# 1. Clone repository
git clone https://github.com/argh-finds404/messmate.git
cd messmate

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Run application
python run.py
```
Open `http://localhost:5000` in your browser.

### Linux / macOS / WSL (Bash)
```bash
# 1. Clone repository
git clone https://github.com/argh-finds404/messmate.git
cd messmate

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Run application
python run.py
```
Open `http://localhost:5000` in your browser.

---

## How to Test

MessMate has a complete testing suite: unit tests, Selenium browser acceptance tests, code coverage analysis, and mutation testing.

### 1. Run Unit Tests
```bash
pytest
```
*Note: Browser tests are marked with `@pytest.mark.e2e` and automatically excluded by default in `pytest.ini` (`-m "not e2e"`) to keep fast unit test feedback loops.*

### 2. Run Selenium End-to-End Browser Tests
Launches a live test server on an ephemeral port and executes acceptance workflows on headless Chrome:
```bash
pytest -m e2e -o addopts=
```

### 3. Check Code Coverage
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=97
```
The test suite achieves **100% statement coverage** across all modules in `app/`.

### 4. Mutation Testing (`mutmut`)
*Note: `mutmut` utilizes POSIX process forking and runs natively on Linux, macOS, and Windows Subsystem for Linux (WSL).*

Inside WSL / Linux:
```bash
# Install mutation testing dependency
pip install -r requirements-mutation.txt

# Run mutation analysis across app/services/, app/adapters/, app/validation.py
mutmut run

# View mutation results
mutmut results

# Inspect a specific mutant
mutmut show <mutant_id>
```
MessMate achieves a **95.50% mutation score** (361 killed, 17 acceptable non-functional survivors). Full analysis is in [`docs/mutation-testing.md`](docs/mutation-testing.md).

---

## Project Structure

```text
messmate/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # CI pipeline: unit tests & headless Chrome E2E tests
│       └── mutation.yml           # Manual mutation testing workflow (workflow_dispatch)
├── app/
│   ├── adapters/                  # Pattern: Adapter & Notifiers
│   │   ├── notifiers.py           # ConsoleNotifier, SmsNotifier, SandboxSmsClient
│   │   └── payment_gateway.py     # PaymentGateway, WalletGatewayAdapter, SandboxWalletClient
│   ├── models/                    # Pure dataclass models
│   │   ├── bill.py                # BillLine
│   │   ├── expense.py             # Expense
│   │   ├── meal.py                # MealEntry
│   │   ├── member.py              # Member
│   │   └── payment.py             # Payment
│   ├── repositories/              # SQLite data access layer
│   │   ├── expense_repository.py
│   │   ├── meal_repository.py
│   │   ├── member_repository.py
│   │   └── payment_repository.py
│   ├── services/                  # Business logic & domain coordination
│   │   ├── billing_service.py     # Monthly billing coordinator
│   │   ├── billing_strategies.py  # Pattern: Strategy (PerMealRateStrategy, EqualSplitStrategy)
│   │   ├── expense_service.py     # Bazar expenses
│   │   ├── meal_service.py        # Daily meals
│   │   ├── member_service.py      # Member registration & lifecycle
│   │   ├── notification_service.py# Notice dispatching
│   │   └── notifier_factory.py    # Pattern: Simple Factory (NotifierFactory)
│   ├── web/                       # Flask presentation layer
│   │   ├── routes.py              # Web endpoints (members, meals, expenses, billing, payments)
│   │   └── templates/             # Jinja2 HTML templates
│   ├── config.py                  # Environment configuration classes
│   ├── container.py               # Dependency injection service container
│   ├── db.py                      # SQLite connection helper & DDL schema
│   ├── errors.py                  # Custom domain exceptions
│   └── validation.py              # Input validation helpers (dates, months)
├── docs/                          # Architecture, specifications, and reports
│   ├── prototype/                 # Low-fidelity static HTML prototypes
│   ├── uml/                       # Mermaid UML class diagrams
│   ├── ai-usage.md                # AI transparency log
│   ├── design.md                  # Architecture & design pattern rationale
│   ├── mutation-testing.md        # Mutation test scores and mutant justifications
│   ├── requirements.md            # User stories, use cases, and process model
│   └── test-report.md             # Comprehensive test and coverage report
├── tests/
│   ├── conftest.py                # Shared fixtures (in-memory db, test client, container)
│   ├── e2e/                       # Selenium end-to-end acceptance tests
│   │   ├── conftest.py            # Live server and headless Chrome fixtures
│   │   └── test_browser_flows.py  # User workflow browser tests
│   └── unit/                      # 205 isolated unit tests
├── pytest.ini                     # Pytest configuration and marker settings
├── requirements.txt               # Production dependencies (Flask)
├── requirements-dev.txt           # Testing dependencies (pytest, pytest-cov, selenium)
├── requirements-mutation.txt      # Mutation testing dependencies (mutmut)
├── run.py                         # Application entrypoint
└── setup.cfg                      # mutmut configuration
```

---

## Architecture and Layering Rule

MessMate strictly enforces a unidirectional four-layer architecture:

$$\text{Web (Presentation)} \longrightarrow \text{Services (Domain Logic)} \longrightarrow \text{Repositories / Adapters} \longrightarrow \text{Database (SQLite)}$$

**Layering Rules:**
1. A layer may only call into the layer directly beneath it or through an injected interface.
2. A lower layer never imports from a layer above it (e.g., repositories and models never import from services or web).
3. The database layer and raw SQL queries are completely hidden inside repository classes.
4. Business logic is pure and independent of Flask request objects.
5. All external dependencies (gateways, notifiers, repositories) are constructor-injected via `app/container.py`.

---

## Design Patterns

| Pattern | Category | Primary Location | One-Line Reason |
| :--- | :--- | :--- | :--- |
| **Strategy** | Behavioral | `app/services/billing_strategies.py` | Encapsulates interchangeable meal cost allocation algorithms (`PerMealRateStrategy`, `EqualSplitStrategy`) without modifying `BillingService`. |
| **Adapter** | Structural | `app/adapters/payment_gateway.py` | Wraps third-party wallet client dictionary responses into a typed, consistent `PaymentResult` domain interface expected by `PaymentService`. |
| **Factory** | Creational | `app/services/notifier_factory.py` | Encapsulates the instantiation and configuration of concrete `Notifier` channels (`ConsoleNotifier`, `SmsNotifier`) based on application configuration. |

---

## How to Extend

MessMate is designed to adhere to the **Open/Closed Principle**: new capabilities can be added with minimal changes to existing code.

### 1. Add a New Billing Strategy
1. Create a class implementing `BillingStrategy` in `app/services/billing_strategies.py`:
   ```python
   class FixedBasePlusMealStrategy(BillingStrategy):
       def calculate(self, meals_by_member: dict[int, int], total_expense: float) -> dict[int, float]:
           # custom math here
           return charges
   ```
2. Register the strategy in `app/container.py` inside `ServiceContainer.build`:
   ```python
   strategies = {
       "per_meal": PerMealRateStrategy(),
       "equal": EqualSplitStrategy(),
       "fixed_plus_meal": FixedBasePlusMealStrategy(),  # added here
   }
   ```

### 2. Add a New Notification Channel
1. Create a concrete class implementing `Notifier` in `app/adapters/notifiers.py`:
   ```python
   class EmailNotifier(Notifier):
       def __init__(self, email_client):
           self.client = email_client
       def send(self, phone: str, message: str) -> None:
           self.client.send_email(to=phone, body=message)
   ```
2. Add a branch in `NotifierFactory.create` in `app/services/notifier_factory.py`:
   ```python
   elif channel == "email":
       return EmailNotifier(email_client)
   ```

### 3. Add a New Payment Provider
1. Create an adapter implementing `PaymentGateway` in `app/adapters/payment_gateway.py`:
   ```python
   class BkashGatewayAdapter(PaymentGateway):
       def __init__(self, bkash_client):
           self.client = bkash_client
       def charge(self, phone: str, amount: float) -> PaymentResult:
           res = self.client.execute_payment(phone, amount)
           return PaymentResult(success=res["ok"], reference=res["trx"], message=res["msg"])
   ```
2. Add a branch in `build_gateway(config)` in `app/container.py` to instantiate the new adapter.

---

## Git Workflow & Branching

MessMate follows a disciplined incremental Git feature-branch workflow:
- **Base Branch:** `main` (protected against direct pushes, updated only through pull requests).
- **Branch Naming Conventions:**
  - `feature/<module>` for new functional increments.
  - `test/<suite>` for test infrastructure and mutation testing.
  - `docs/<topic>` for specifications, diagrams, and reports.
  - `chore/<task>` for scaffolding and dependencies.
  - `ci/<workflow>` for continuous integration setups.
- **Commit Format:** Conventional Commits standard: `type(scope): message`.
- **Pull Requests:** Every increment was developed on an isolated branch, tested locally, reviewed, approved, and merged using **Create a merge commit** to preserve a clean topological history.

---

## Continuous Integration (GitHub Actions)

MessMate uses GitHub Actions configured in `.github/workflows/ci.yml` and `.github/workflows/mutation.yml`:
- **`unit-tests` Job:**
  - Runs on Ubuntu latest across multiple Python versions.
  - Executes the 205 unit tests.
  - Enforces a strict code coverage gate: fails the build if test coverage drops below 97% (`--cov-fail-under=97`). Total coverage is **100%**.
- **`browser-tests` Job:**
  - Sets up headless Google Chrome and ChromeDriver.
  - Executes Selenium end-to-end acceptance tests.
- **`mutation-testing` Job (`.github/workflows/mutation.yml`):**
  - Manually triggered via `workflow_dispatch` to prevent slowing down daily PR merges while providing full verification on demand.

---

## Tools Used

- **Web Framework:** Flask (Python)
- **Database:** SQLite3
- **Unit Testing:** `pytest`, `pytest-cov`, `unittest.mock`
- **End-to-End Testing:** Selenium WebDriver, Headless Google Chrome
- **Mutation Testing:** `mutmut` 3.8.1 (self-learned advanced testing tool)
- **CI / CD:** GitHub Actions
- **UML & Diagrams:** Mermaid.js

---

## AI Usage Statement

The project was drafted with the Antigravity coding agent, every stage is logged in `docs/ai-usage.md`, AI-assisted commits carry an `AI-assisted: Antigravity` line, and the author reviewed and can explain the code.
