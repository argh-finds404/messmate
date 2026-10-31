# Merge Conflict Resolution Note

## 1. Branches Involved
- **Base / Incoming branch:** `main` (at merge commit `e81df15`, after merging PR #9 `feature/payment-adapter`)
- **Current / Feature branch:** `feature/notification-module` (at commit `43780e2`, PR #10)
- **Common ancestor:** `5664352` (Stage 8 `feature/billing-strategy` merge commit on `main`)

## 2. Conflicting File and Lines
- **File:** `app/config.py`
- **Location:** Line 4 inside `class Config` (immediately after `TESTING = False`).
- **Observed conflict markers (`git diff`):**
```diff
diff --cc app/config.py
index da2501f,81748af..0000000
--- a/app/config.py
+++ b/app/config.py
@@@ -1,4 -1,4 +1,8 @@@
  class Config:
      DATABASE = "messmate.db"
      TESTING = False
++<<<<<<< HEAD
 +    NOTIFY_CHANNEL = "console"
++=======
+     PAYMENT_MODE = "sandbox"
++>>>>>>> main
```

## 3. Why the Conflict Happened
Both `feature/payment-adapter` (Stage 9) and `feature/notification-module` (Stage 10) were branched from the same base commit (`5664352`) on `main` to simulate two developers working in parallel on independent modules. Each branch appended a new default setting at the exact same line (line 4 of `app/config.py`):
- `feature/payment-adapter` added `PAYMENT_MODE = "sandbox"` (commit `18acddd`, merged to `main` as `e81df15`).
- `feature/notification-module` added `NOTIFY_CHANNEL = "console"` (commit `43780e2`).

When `main` was merged into `feature/notification-module`, Git could not automatically decide whether one setting replaced the other or whether both should be kept, triggering a three-way content conflict (`both modified: app/config.py`).

## 4. How It Was Resolved
Because `PAYMENT_MODE` and `NOTIFY_CHANNEL` configure two independent subsystems (the wallet payment adapter and the bill notification factory), both settings are required in `Config`. We resolved `app/config.py` by keeping both attributes and removing the `<<<<<<< HEAD`, `=======`, and `>>>>>>> main` conflict markers:

```python
class Config:
    DATABASE = "messmate.db"
    TESTING = False
    PAYMENT_MODE = "sandbox"
    NOTIFY_CHANNEL = "console"
```

We then staged the resolved file (`git add app/config.py`) and recorded the merge commit (`3994dec`, `merge: resolve config conflict between payment and notification branches`).

## 5. How the Resolution Was Verified
1. Ran the full test suite (`pytest -q`), confirming all **144 unit tests** pass, including both `tests/unit/test_payment_config.py` (`Config.PAYMENT_MODE == "sandbox"`) and `tests/unit/test_notification_config.py` (`Config.NOTIFY_CHANNEL == "console"`).
2. Verified `git status` reported a clean working tree with no remaining unmerged paths or conflict markers.

## 6. How to Avoid Similar Conflicts in Future Work
- **Pull `main` frequently:** Rebase or merge `origin/main` into active feature branches as soon as another PR merges, rather than letting parallel branches diverge over multiple commits.
- **Group config settings by section:** Organize `app/config.py` into commented sections (e.g., `# Database`, `# Payments`, `# Notifications`) so parallel additions land in separate regions of the file instead of colliding on the final line.
- **Keep feature branches short-lived:** Merge small, focused PRs promptly so shared files like `app/config.py` and `app/__init__.py` rarely have concurrent edits in flight.
