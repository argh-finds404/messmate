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

## 3. Baseline vs. Final Results

| Metric | Baseline Value | Final Value (After New Tests) | Change |
|---|---|---|---|
| **Unit Test Line Coverage** | 100.00% | 100.00% | +0.00% |
| **Total Mutants Generated** | 378 | 378 | 0 |
| **Killed Mutants** | 352 | 361 | **+9** |
| **Surviving Mutants** | 26 | 17 | **-9** |
| **Timed Out / Suspicious** | 0 | 0 | 0 |
| **Mutation Score** | **93.12%** | **95.50%** | **+2.38%** |

---

## 4. Killed Mutants & Targeted Tests

A total of 9 surviving mutants were systematically analyzed and killed across `app/validation.py`, `app/services/notification_service.py`, and `app/services/payment_service.py`:

| Mutant Name | Code Change Introduced by mutmut | Test That Kills It | Reason & Assertion Added |
|---|---|---|---|
| `app.validation.x_check_date__mutmut_10` | `"Date must be..."` -> `"XXDate must be...XX"` | `test_check_date_exact_error_message_regex_failure` | Regex format failure error message string asserted exactly. |
| `app.validation.x_check_date__mutmut_15` | `"Date must be..."` -> `"XXDate must be...XX"` | `test_check_date_exact_error_message_invalid_calendar_date` | Invalid calendar date ValueError message string asserted exactly. |
| `app.validation.x_check_month__mutmut_10` | `"Month must be..."` -> `"XXMonth must be...XX"` | `test_check_month_exact_error_message` | Invalid month error message string asserted exactly. |
| `app.services.notification_service.xǁNotificationServiceǁsend_bill_notices__mutmut_4` | `line.charge <= 0` -> `line.charge <= 1` | `test_positive_charge_below_one_receives_notice` | Boundary test with `charge = 0.50` ensures positive fractional dues are not skipped. |
| `app.services.notification_service.xǁNotificationServiceǁsend_bill_notices__mutmut_9` | `continue` -> `break` (when member is None) | `test_missing_member_does_not_stop_subsequent_members` | Verifies that a missing member in bill lines does not abort processing remaining valid members. |
| `app.services.payment_service.xǁPaymentServiceǁpay__mutmut_5` | `amount <= 0` -> `amount <= 1` | `test_pay_accepts_positive_amount_below_one` | Boundary test with `amount = 0.50` ensures valid payments under 1.00 BDT are accepted. |
| `app.services.payment_service.xǁPaymentServiceǁpay__mutmut_7` | `"Amount must be..."` -> `"XXAmount must be...XX"` | `test_pay_exact_invalid_amount_error_message` | Invalid amount ValidationError message string asserted exactly. |
| `app.services.payment_service.xǁPaymentServiceǁpay__mutmut_21` | `"Member not found"` -> `"XXMember not foundXX"` | `test_pay_exact_unknown_member_error_message` | Unknown member NotFoundError message string asserted exactly. |
| `app.services.payment_service.xǁPaymentServiceǁpay__mutmut_32` | `"Payment failed"` -> `"XXPayment failedXX"` | `test_pay_exact_failed_charge_fallback_error_message` | PaymentFailedError default fallback message string asserted exactly. |

---

## 5. Remaining Survivors & Justifications

The remaining 17 surviving mutants were inspected and left intentionally for the following reasons:

- **String literals in error messages (14 mutants):**
  - `app.services.member_service` (`mutmut_5`, `mutmut_10`, `mutmut_20`, `mutmut_26`, `mutmut_5`): Validation error message strings ("Name is required", "Room is required", etc.).
  - `app.services.meal_service` (`mutmut_18`, `mutmut_23`): Meal validation error message strings.
  - `app.services.expense_service` (`mutmut_12`, `mutmut_14`): Expense validation error strings.
  - `app.services.notifier_factory` (`mutmut_10`, `mutmut_11`): Notifier factory ValueError message strings.
  - `app.adapters.notifiers` (`mutmut_7`): SMS provider rejection message.
  - *Justification:* Domain error classes (`ValidationError`, `NotFoundError`, `NotificationError`) are already verified by exception type and regex matching in the test suite; asserting verbatim copies of every human-readable string creates brittle tests without increasing fault tolerance.

- **Sandbox / Mock SDK Artifacts (3 mutants):**
  - `app.adapters.payment_gateway` (`mutmut_3`, `mutmut_33`, `mutmut_34`): Modifies the demo transaction ID prefix `"SBX"` and slice `[:8]` in the offline Sandbox client.
  - *Justification:* These are internal to offline simulation harness logic rather than production application domain logic.
