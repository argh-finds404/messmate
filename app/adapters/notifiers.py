from abc import ABC, abstractmethod


class NotificationError(Exception):
    """Raised when a message could not be delivered."""


class Notifier(ABC):
    """A way of delivering a text message to a phone number."""

    @abstractmethod
    def send(self, phone: str, message: str) -> None:
        """Deliver `message` to `phone` or raise NotificationError."""


class SandboxSmsClient:
    """Pretend SMS provider. Remembers messages instead of sending them."""

    def __init__(self):
        self.sent = []

    def send_sms(self, to: str, text: str) -> bool:
        self.sent.append((to, text))
        return True


class SmsNotifier(Notifier):
    def __init__(self, client):
        self.client = client

    def send(self, phone: str, message: str) -> None:
        if not self.client.send_sms(to=phone, text=message):
            raise NotificationError("SMS provider rejected the message")


class ConsoleNotifier(Notifier):
    """Prints the message. Used for development and demos."""

    def __init__(self, out=print):
        self.out = out

    def send(self, phone: str, message: str) -> None:
        self.out(f"[notify] to {phone}: {message}")
