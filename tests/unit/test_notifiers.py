from unittest.mock import Mock

import pytest

from app.adapters.notifiers import (
    ConsoleNotifier,
    NotificationError,
    Notifier,
    SandboxSmsClient,
    SmsNotifier,
)


def test_notifier_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Notifier()


def test_console_notifier_writes_formatted_line():
    out = Mock()
    ConsoleNotifier(out).send("01711111111", "hello")
    out.assert_called_once_with("[notify] to 01711111111: hello")


def test_sms_notifier_sends_through_client():
    client = Mock()
    client.send_sms.return_value = True
    SmsNotifier(client).send("01711111111", "hello")
    client.send_sms.assert_called_once_with(to="01711111111", text="hello")


def test_sms_notifier_raises_when_provider_rejects():
    client = Mock()
    client.send_sms.return_value = False
    with pytest.raises(NotificationError, match="SMS provider rejected the message"):
        SmsNotifier(client).send("01711111111", "hello")


def test_sandbox_client_remembers_messages():
    client = SandboxSmsClient()
    assert client.send_sms("01711111111", "hi") is True
    assert client.sent == [("01711111111", "hi")]
