# MessMate Test and Coverage Report

This report documents the testing strategy, test suites, statement coverage, mock usage, Test-Driven Development (TDD) evidence, and Continuous Integration status for the MessMate application.

---

## 1. Test Suite Summary

The MessMate automated test suite is divided into two distinct suites: fast, isolated unit tests and full-stack Selenium browser acceptance tests.

| Suite | Type | Test Count | Execution Time | Command |
| :--- | :--- | :--- | :--- | :--- |
| **Unit Test Suite** | Isolated unit / integration | 205 passed | ~4.5 seconds | `pytest` |
| **Browser E2E Suite** | End-to-end acceptance (Selenium) | 5 passed | ~30 seconds | `pytest -m e2e -o addopts=` |
| **Total Automated Tests** | All suites combined | **210 passed** | | |

In `pytest.ini`, browser tests are marked with `@pytest.mark.e2e` and excluded from default test invocations via `addopts = -m "not e2e"`. This separation ensures that daily developer feedback loops and unit test runs remain nearly instantaneous.

---

## 2. Statement Coverage Report

Code coverage was measured across the entire `app/` codebase using `pytest-cov`. MessMate achieves **100% statement coverage** with zero missed statements.

```text
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.13.3-final-0 _______________

Name                                     Stmts   Miss  Cover   Missing
----------------------------------------------------------------------
app\__init__.py                             17      0   100%
app\adapters\__init__.py                     0      0   100%
app\adapters\notifiers.py                   22      0   100%
app\adapters\payment_gateway.py             27      0   100%
app\config.py                                6      0   100%
app\container.py                            27      0   100%
app\db.py                                   10      0   100%
app\errors.py                                3      0   100%
app\models\__init__.py                       0      0   100%
app\models\bill.py                           7      0   100%
app\models\expense.py                        7      0   100%
app\models\meal.py                           7      0   100%
app\models\member.py                         8      0   100%
app\models\payment.py                        8      0   100%
app\repositories\__init__.py                 0      0   100%
app\repositories\expense_repository.py      17      0   100%
app\repositories\meal_repository.py         20      0   100%
app\repositories\member_repository.py       25      0   100%
app\repositories\payment_repository.py      17      0   100%
app\services\__init__.py                     0      0   100%
app\services\billing_service.py             19      0   100%
app\services\billing_strategies.py          17      0   100%
app\services\expense_service.py             21      0   100%
app\services\meal_service.py                22      0   100%
app\services\member_service.py              29      0   100%
app\services\notification_service.py        22      0   100%
app\services\notifier_factory.py            11      0   100%
app\services\payment_service.py             30      0   100%
app\validation.py                           15      0   100%
app\web\__init__.py                          0      0   100%
app\web\routes.py                          129      0   100%
----------------------------------------------------------------------
TOTAL                                      543      0   100%
Required test coverage of 97% reached. Total coverage: 100.00%
205 passed, 5 deselected in 4.55s
```

---

## 3. How Each Kind of Test is Run

### Unit Tests
Unit tests exercise models, validation rules, repositories against in-memory SQLite (`:memory:`), service logic with mocked dependencies, and Flask web endpoints with the Flask test client.
```bash
pytest
```

### Selenium End-to-End Acceptance Tests
E2E tests spin up the real Flask WSGI application on an ephemeral background socket and drive a real headless Google Chrome browser via Selenium WebDriver.
```bash
pytest -m e2e -o addopts=
```

### Coverage Gate
Verifies that coverage does not drop below 97% (enforced in CI):
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=97
```

### Mutation Testing (`mutmut`)
Runs mutation analysis across core domain logic (`app/services/`, `app/adapters/`, `app/validation.py`) on WSL / Linux:
```bash
mutmut run
mutmut results
```

---

## 4. Isolation and Mock Usage

To test business logic independently of external services, side effects, and I/O latency, constructor injection and `unittest.mock.Mock` are used:

| Test File | Mocked Dependency | Reason for Mocking |
| :--- | :--- | :--- |
| `tests/unit/test_member_service.py` | `MemberRepository` | Isolates member validation and business rules from SQLite queries. |
| `tests/unit/test_meal_service.py` | `MealRepository`, `MemberRepository` | Tests meal validation and calculation logic without database state. |
| `tests/unit/test_expense_service.py` | `ExpenseRepository` | Tests expense validation and monthly summation rules in isolation. |
| `tests/unit/test_billing_service.py` | `MemberRepository`, `MealRepository`, `ExpenseRepository` | Verifies strategy dispatching and bill assembly without querying tables. |
| `tests/unit/test_payment_gateway.py` | `SandboxWalletClient` | Verifies the adapter's dictionary parsing and response mapping without network calls. |
| `tests/unit/test_payment_service.py` | `PaymentRepository`, `MemberRepository`, `PaymentGateway` | Tests payment validation, due calculation, and error raising without making actual gateway charges. |
| `tests/unit/test_notification_service.py` | `MemberRepository`, `Notifier` | Verifies member notice filtering and message dispatching without printing to console or sending real SMS. |
| `tests/unit/test_notifier_factory.py` | `SandboxSmsClient` | Validates factory instantiation and parameter validation without calling SMS vendor APIs. |

Repositories themselves are tested directly against fresh in-memory SQLite connections (`connect(":memory:")`), guaranteeing that SQL syntax, constraints, foreign keys, and autoincrements work correctly.

---

## 5. Test-Driven Development (TDD) Evidence

All domain modules and endpoints were built following strict **Red-Green-Refactor** TDD cycles. For every increment, failing test suites were committed before any implementation code was written.

### Feature 1: Member Module (Stage 5)
```text
6cbfa12 test(member): add failing tests for member repository    [RED]
8e16999 feat(member): add member model and repository             [GREEN]
0fa5400 test(member): add failing tests for member service        [RED]
31b9881 feat(member): add member service with validation          [GREEN]
```

### Feature 2: Meal Tracking Module (Stage 6)
```text
1205315 test(meal): add failing tests for date and month validation [RED]
e0938a4 feat(meal): add date and month validation                 [GREEN]
4621539 test(meal): add failing tests for meal repository          [RED]
eb679a9 feat(meal): add meal entry model and repository           [GREEN]
e405f63 test(meal): add failing tests for meal service             [RED]
06bbf5d feat(meal): add meal service                              [GREEN]
```

---

## 6. Continuous Integration (CI) Status

Continuous Integration is automated using GitHub Actions (`.github/workflows/ci.yml`):
- **Trigger:** Runs on every `push` and `pull_request` against `main`.
- **Jobs:**
  - `unit-tests`: Executes 205 unit tests and enforces the 97% minimum statement coverage threshold (`--cov-fail-under=97`).
  - `browser-tests`: Installs headless Google Chrome and executes the Selenium end-to-end acceptance tests.
- **Workflow Health:** All 14 pull requests merged into `main` have passed 100% of their CI checks without failures or broken builds.
