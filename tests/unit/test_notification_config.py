from app.config import Config


def test_notify_channel_defaults_to_console():
    assert Config.NOTIFY_CHANNEL == "console"
