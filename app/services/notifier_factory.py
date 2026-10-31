from app.adapters.notifiers import ConsoleNotifier, Notifier, SmsNotifier


class NotifierFactory:
    """Simple factory creating the configured Notifier implementation."""

    @staticmethod
    def create(channel: str, sms_client=None, out=print) -> Notifier:
        """Return a Notifier instance for the given channel name."""
        if channel == "console":
            return ConsoleNotifier(out)
        if channel == "sms":
            if sms_client is None:
                raise ValueError("The sms channel needs an sms_client")
            return SmsNotifier(sms_client)
        raise ValueError(f"Unknown notification channel: {channel}")
