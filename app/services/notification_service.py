from app.adapters.notifiers import NotificationError, Notifier
from app.models.bill import BillLine
from app.repositories.member_repository import MemberRepository


class NotificationService:
    """Sends monthly bill notices to members with a positive charge."""

    def __init__(self, member_repo: MemberRepository, notifier: Notifier) -> None:
        self.member_repo = member_repo
        self.notifier = notifier

    def send_bill_notices(self, month: str, lines: list[BillLine]) -> int:
        """Deliver a bill notice for each line with charge > 0 and return sent count."""
        sent = 0
        for line in lines:
            if line.charge <= 0:
                continue
            member = self.member_repo.get(line.member_id)
            if member is None:
                continue
            message = f"Dear {member.name}, your mess bill for {month} is {line.charge:.2f} BDT."
            try:
                self.notifier.send(member.phone, message)
                sent += 1
            except NotificationError:
                continue
        return sent
