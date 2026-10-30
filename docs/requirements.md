# Requirements

## Functional Requirements

- **FR1:** Register a member with name, room and phone.
- **FR2:** Reject an empty name, an empty room, a phone that is not 11 digits starting with `01`, and a phone that is already registered.
- **FR3:** List members and deactivate a member. Inactive members are excluded from meal entry and billing.
- **FR4:** Record the number of meals (`0` to `3`) for an active member on a date. Recording again for the same member and date overwrites the earlier value.
- **FR5:** Show the total meals per member for a month.
- **FR6:** Record a bazar expense with date, description and an amount greater than `0`.
- **FR7:** List a month's expenses and show their total.
- **FR8:** Generate the monthly bill with a selectable strategy: per-meal rate (`total expense / total meals`, times the member's meals) or equal split.
- **FR9:** Record a payment through a mobile-wallet gateway. A payment the gateway rejects is not stored.
- **FR10:** Show paid and due amounts per member for a month.
- **FR11:** Send bill notices through the configured channel (`console` or `sms`). If one message fails, the others are still sent.
- **FR12:** Keep all data in SQLite so it survives a restart.

## Non-Functional Requirements

- **NFR1 Extensibility:** A new billing strategy, payment gateway or notification channel is added by writing one class and registering it in one place, without editing existing logic.
- **NFR2 Testability:** Every external dependency (database, payment, SMS) sits behind an interface so it can be mocked; unit tests run without network or browser.
- **NFR3 Reliability:** Invalid input shows a clear message and never a crash page.
- **NFR4 Security:** SQL is parameterised; all input is validated in the service layer.
- **NFR5 Usability:** Every task is reachable from the top navigation in one click, using plain forms.
- **NFR6 Portability:** Runs on Windows and Linux with Python 3.13 and no external services.
- **NFR7 Maintainability:** Layered design (`web -> services -> repositories/adapters -> db`); a layer never imports from a layer above it.

## User Stories

1. **Register a member**
   - As a mess manager, I want to register a resident with name, room and phone number so that they can take meals and be billed.
   - Acceptance criteria:
     - Submitting a valid name, room and 11-digit `01...` phone saves the member as active.
     - Submitting an empty name, empty room, invalid phone format, or duplicate phone is rejected with an error message.

2. **Deactivate a member who left**
   - As a mess manager, I want to deactivate a member who moved out so that they are not included in new meal entries or monthly bills.
   - Acceptance criteria:
     - Clicking deactivate marks the member as inactive in the database.
     - Inactive members cannot have new meals recorded and are excluded from generated bills.

3. **Record daily meals**
   - As a mess manager, I want to record how many meals (`0` to `3`) an active member took on a date so that monthly meal counts are accurate.
   - Acceptance criteria:
     - Entering `0` to `3` meals for an active member on a valid `YYYY-MM-DD` date saves the entry.
     - Entering meals again for the same member and date updates the existing entry instead of creating a duplicate row.
     - Meal counts outside `0..3` or for an inactive member are rejected.

4. **Record a bazar expense**
   - As a mess manager, I want to record each bazar purchase with date, description and amount so that total monthly mess cost is tracked.
   - Acceptance criteria:
     - Submitting a valid date, non-empty description and amount greater than `0` stores the expense rounded to two decimals.
     - Viewing a month lists its expenses in date order and displays the monthly total.

5. **Generate the monthly bill and choose how it is calculated**
   - As a mess manager, I want to generate a month's bill using either per-meal rate or equal split so that charges match our mess rules.
   - Acceptance criteria:
     - Selecting per-meal rate charges each active member `meals * (total_expense / total_meals)` rounded to two decimals.
     - Selecting equal split divides `total_expense` equally among all active members.
     - If total meals is zero under per-meal rate, every member's charge is `0.00`.

6. **Record a member's payment**
   - As a mess manager, I want to charge a member's mobile wallet and save the payment so that paid amounts and transaction references are recorded.
   - Acceptance criteria:
     - A payment approved by the wallet gateway is saved with the returned transaction reference.
     - A payment rejected by the wallet gateway shows the failure reason and is not stored in the database.

7. **See who still owes money**
   - As a mess manager, I want to see each member's charge, paid amount and remaining due for a month so that I know who has not settled their bill.
   - Acceptance criteria:
     - Each member row shows their monthly bill charge, total paid for that month, and `due = charge - paid`.
     - Recording a new payment reduces the member's due amount for that month immediately.

8. **Send bill notices**
   - As a mess manager, I want to send bill notifications to members who have a positive charge so that they know how much to pay.
   - Acceptance criteria:
     - Members with a charge greater than `0` receive a notice containing their name, month and bill amount.
     - Members with `0.00` charge are skipped, and a failure on one member's notice does not stop notices to the remaining members.

### Use Cases

#### UC1: Register Member
- **Actor:** Mess Manager
- **Precondition:** The manager is on the Members page.
- **Main Flow:**
  1. Manager enters the resident's name, room number and 11-digit phone number starting with `01`.
  2. System strips leading/trailing spaces and validates the name, room and phone format.
  3. System checks that no existing member has the same phone number.
  4. System saves the new active member in SQLite and shows the updated member list.
- **Alternative Flows:**
  - *2a. Name or room is empty, or phone is not 11 digits starting with `01`:* System rejects the request with a validation error message and does not save.
  - *3a. Phone is already registered:* System rejects the request with `"Phone already registered"` and does not save.
- **Postcondition:** A new active member record is stored in the `members` table.

#### UC2: Generate Monthly Bill
- **Actor:** Mess Manager
- **Precondition:** Active members, meal entries and bazar expenses exist for the selected month (`YYYY-MM`).
- **Main Flow:**
  1. Manager selects a month (`YYYY-MM`) and a billing strategy (`per_meal` or `equal`).
  2. System loads all active members, each member's total meals for the month, and the total bazar expense for the month.
  3. System calculates each active member's charge using the chosen `BillingStrategy`.
  4. System displays the bill table with member name, meal count, charge, paid amount and remaining due.
- **Alternative Flows:**
  - *1a. Month format is invalid:* System raises `"Month must be in YYYY-MM format"`.
  - *3a. Total meals for the month is zero under per-meal strategy:* System assigns a charge of `0.00` to every active member without dividing by zero.
- **Postcondition:** Monthly bill lines are computed and displayed for all active members.

#### UC3: Pay Dues
- **Actor:** Mess Manager
- **Precondition:** The member is registered and the manager is on the Billing/Payments view for a valid month (`YYYY-MM`).
- **Main Flow:**
  1. Manager selects a member, enters a positive payment amount for the month, and submits the payment form.
  2. System validates that the amount is greater than `0`, the month is in `YYYY-MM` format, and the member exists.
  3. System calls the payment gateway adapter using the member's phone number and rounded amount.
  4. Gateway returns a successful `PaymentResult` with a transaction reference.
  5. System stores the payment in SQLite and updates the member's paid and due totals.
- **Alternative Flows:**
  - *2a. Amount is zero, negative, or non-numeric:* System rejects the input with `"Amount must be a number greater than 0"` before contacting the gateway.
  - *4a. Gateway rejects the payment (e.g., insufficient balance):* System raises `PaymentFailedError` with the gateway message, does not save a payment row, and leaves the member's due unchanged.
- **Postcondition:** On success, a payment record with its transaction reference is persisted in the `payments` table.

## Process Model and Justification

**Chosen Model:** Incremental Model.

**Justification:**
- The six functional modules (`member`, `meal`, `expense`, `billing`, `payment`, `notification`) are fairly independent, so each module can be designed, built with TDD, tested in CI, and merged as one self-contained increment (one pull request per increment).
- Working, tested software exists after the very first increments rather than waiting until the end of the project.
- The requirements for a hostel mess manager are small and stable up front.
- Because there is only one developer, Scrum ceremonies (daily stand-ups, sprint planning, retrospectives) would add overhead without benefit.

**Alternatives Rejected:**
- **Waterfall:** Produces no working software until the end of the schedule, making any late design or integration mistake expensive to fix.
- **Scrum:** Designed for multi-person teams with a Product Owner, Scrum Master, and time-boxed sprints; unnecessary ceremony for a single developer lab project.

### Planned Increments and Branches

| Increment | Planned Branch | Deliverable |
| --- | --- | --- |
| Foundation | `feature/database-setup` | SQLite connection helper, table schema, app factory database wiring |
| Increment 1: Member | `feature/member-module` | `Member` model, `MemberRepository`, `MemberService` with validation |
| Increment 2: Meal | `feature/meal-tracking` | Date/month validators, `MealEntry` model, `MealRepository`, `MealService` |
| Increment 3: Expense | `feature/expense-module` | `Expense` model, `ExpenseRepository`, `ExpenseService` |
| Increment 4: Billing | `feature/billing-strategy` | `BillingStrategy` (`PerMealRateStrategy`, `EqualSplitStrategy`), `BillLine`, `BillingService` |
| Increment 5: Payment | `feature/payment-adapter` | `PaymentGateway`, `WalletGatewayAdapter`, `SandboxWalletClient`, `PaymentRepository`, `PaymentService` |
| Increment 6: Notification | `feature/notification-module` | `Notifier`, `SmsNotifier`, `ConsoleNotifier`, `NotifierFactory`, `NotificationService` |
| Increment 7: Web UI | `feature/web-ui` | Flask routes and Jinja2 templates connecting all services |
| Increment 8: E2E Tests | `test/selenium-e2e` | Headless Selenium browser tests covering end-to-end user flows |
| Increment 9: Mutation Testing | `test/mutation-testing` | `mutmut` configuration, mutation score analysis, and surviving-mutant tests |

## Prototype

Static, low-fidelity HTML mock-ups live under `docs/prototype/` (with `docs/prototype/index.html` linking to all screens):

- `docs/prototype/members.html`: Shows the member registration form (name, room, phone) and the registered members table with status and a Deactivate button.
- `docs/prototype/meals.html`: Shows the daily meal entry form (`0` to `3` meals per active member), monthly meal totals, the bazar expense entry form, and the monthly expense table.
- `docs/prototype/billing.html`: Shows the monthly bill generator with strategy selector (per-meal rate or equal split), the per-member bill/paid/due table, a button to send bill notices, and the mobile-wallet payment form.
