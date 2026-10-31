from unittest.mock import Mock

import pytest

from app.adapters.notifiers import ConsoleNotifier, SmsNotifier
from app.services.notifier_factory import NotifierFactory


def test_creates_console_notifier():
    assert isinstance(NotifierFactory.create("console"), ConsoleNotifier)


def test_console_notifier_uses_given_output():
    out = Mock()
    NotifierFactory.create("console", out=out).send("01711111111", "hi")
    out.assert_called_once()


def test_creates_sms_notifier_with_client():
    client = Mock()
    notifier = NotifierFactory.create("sms", sms_client=client)
    assert isinstance(notifier, SmsNotifier)
    assert notifier.client is client


def test_sms_channel_needs_a_client():
    with pytest.raises(ValueError, match="needs an sms_client"):
        NotifierFactory.create("sms")


def test_unknown_channel_is_rejected():
    with pytest.raises(ValueError, match="Unknown notification channel: pigeon"):
        NotifierFactory.create("pigeon")
