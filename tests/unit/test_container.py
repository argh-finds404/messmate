import pytest

from app.container import build_services

CONFIG = {"PAYMENT_MODE": "sandbox", "NOTIFY_CHANNEL": "console"}


def test_every_module_is_wired(conn):
    services = build_services(CONFIG, conn)
    for name in ["members", "meals", "expenses", "billing", "payments", "notifications"]:
        assert getattr(services, name) is not None


def test_strategy_registry_holds_both_strategies(conn):
    assert set(build_services(CONFIG, conn).strategies) == {"per_meal", "equal"}


def test_unknown_payment_mode_is_rejected(conn):
    with pytest.raises(ValueError, match="Unknown payment mode: paypal"):
        build_services({**CONFIG, "PAYMENT_MODE": "paypal"}, conn)


def test_unknown_notify_channel_is_rejected(conn):
    with pytest.raises(ValueError, match="Unknown notification channel: pigeon"):
        build_services({**CONFIG, "NOTIFY_CHANNEL": "pigeon"}, conn)


def test_app_exposes_services(app):
    assert app.extensions["services"].members is not None
