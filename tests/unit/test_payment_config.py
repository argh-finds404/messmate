from app.config import Config


def test_payment_mode_defaults_to_sandbox():
    assert Config.PAYMENT_MODE == "sandbox"
