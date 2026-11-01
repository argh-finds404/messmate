# Mutation Testing Report

## 1. What is Mutation Testing?

Mutation testing evaluates the true quality and defect-detection power of an existing test suite by deliberately injecting synthetic faults (mutants), such as flipping boolean conditions, changing comparison operators, or mutating string literals and numeric bounds, directly into the source code. Each generated mutant represents a specific bug introduced into the system. If running the existing test suite against a mutant produces at least one test failure, the mutant is considered "killed", whereas if all tests continue to pass despite the defect, the mutant has "survived", indicating a gap in test assertions or missing boundary checks.

---

## 2. Environment & Execution Scope

- **Operating System / Distribution:** Ubuntu 26.04 LTS running on Windows Subsystem for Linux (WSL 2)
- **Python Version:** Python 3.14.4 (inside `~/mutation-venv`)
- **Mutation Tool:** `mutmut` version 3.8.1
- **Target Scope:**
  - `app/services/` (all domain business services and strategies)
  - `app/adapters/` (external gateways and notification adapters)
  - `app/validation.py` (date and month format validators)
- **Excluded:**
  - Repositories (`app/repositories/` containing raw SQL strings)
  - Web UI routes and templates (`app/web/`)
  - End-to-end browser tests (`pytest.ini` skips `-m e2e` automatically)

### Commands Used
```bash
cd /mnt/d/MessMate
source ~/mutation-venv/bin/activate
mutmut run
mutmut results
mutmut show <mutant_name>
```

---

## 3. Baseline Mutation Testing Results

At the baseline run, the unit test suite achieved 100% statement coverage across `app/`, but mutation testing revealed 26 surviving mutants:

| Metric | Baseline Value |
|---|---|
| **Unit Test Line Coverage** | 100.00% |
| **Total Mutants Generated** | 378 |
| **Killed Mutants** | 352 |
| **Surviving Mutants** | 26 |
| **Timed Out / Suspicious** | 0 |
| **Baseline Mutation Score** | **93.12%** (352 / 378) |

### Surviving Mutants (Grouped by File)

#### `app/validation.py` (3 survivors)
- `app.validation.x_check_date__mutmut_10`
- `app.validation.x_check_date__mutmut_15`
- `app.validation.x_check_month__mutmut_10`

#### `app/services/payment_service.py` (4 survivors)
- `app.services.payment_service.xǁPaymentServiceǁpay__mutmut_5`
- `app.services.payment_service.xǁPaymentServiceǁpay__mutmut_7`
- `app.services.payment_service.xǁPaymentServiceǁpay__mutmut_21`
- `app.services.payment_service.xǁPaymentServiceǁpay__mutmut_32`

#### `app/services/notification_service.py` (2 survivors)
- `app.services.notification_service.xǁNotificationServiceǁsend_bill_notices__mutmut_4`
- `app.services.notification_service.xǁNotificationServiceǁsend_bill_notices__mutmut_9`

#### `app/services/notifier_factory.py` (2 survivors)
- `app.services.notifier_factory.xǁNotifierFactoryǁcreate__mutmut_10`
- `app.services.notifier_factory.xǁNotifierFactoryǁcreate__mutmut_11`

#### `app/services/member_service.py` (5 survivors)
- `app.services.member_service.xǁMemberServiceǁregister__mutmut_5`
- `app.services.member_service.xǁMemberServiceǁregister__mutmut_10`
- `app.services.member_service.xǁMemberServiceǁregister__mutmut_20`
- `app.services.member_service.xǁMemberServiceǁregister__mutmut_26`
- `app.services.member_service.xǁMemberServiceǁget__mutmut_5`

#### `app/services/meal_service.py` (3 survivors)
- `app.services.meal_service.xǁMealServiceǁrecord__mutmut_10`
- `app.services.meal_service.xǁMealServiceǁrecord__mutmut_18`
- `app.services.meal_service.xǁMealServiceǁrecord__mutmut_23`

#### `app/services/expense_service.py` (3 survivors)
- `app.services.expense_service.xǁExpenseServiceǁadd_expense__mutmut_5`
- `app.services.expense_service.xǁExpenseServiceǁadd_expense__mutmut_12`
- `app.services.expense_service.xǁExpenseServiceǁadd_expense__mutmut_14`

#### `app/adapters/notifiers.py` (1 survivor)
- `app.adapters.notifiers.xǁSmsNotifierǁsend__mutmut_7`

#### `app/adapters/payment_gateway.py` (3 survivors)
- `app.adapters.payment_gateway.xǁSandboxWalletClientǁmake_payment__mutmut_3`
- `app.adapters.payment_gateway.xǁSandboxWalletClientǁmake_payment__mutmut_33`
- `app.adapters.payment_gateway.xǁSandboxWalletClientǁmake_payment__mutmut_34`
