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

## Process Model and Justification

## Prototype
