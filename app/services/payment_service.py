from app.adapters.payment_gateway import PaymentGateway
from app.errors import NotFoundError, PaymentFailedError, ValidationError
from app.models.payment import Payment
from app.repositories.member_repository import MemberRepository
from app.repositories.payment_repository import PaymentRepository
from app.validation import check_month


class PaymentService:
    """Business logic for charging mobile wallets and tracking monthly dues."""

    def __init__(
        self,
        payment_repo: PaymentRepository,
        member_repo: MemberRepository,
        gateway: PaymentGateway,
    ) -> None:
        self.payment_repo = payment_repo
        self.member_repo = member_repo
        self.gateway = gateway

    def pay(self, member_id: int, month: str, amount: float) -> Payment:
        """Charge the member's wallet through the gateway and save the payment on success."""
        if type(amount) not in (int, float) or amount <= 0:
            raise ValidationError("Amount must be a number greater than 0")
        amount = round(amount, 2)
        check_month(month)
        member = self.member_repo.get(member_id)
        if member is None:
            raise NotFoundError("Member not found")
        result = self.gateway.charge(member.phone, amount)
        if not result.success:
            raise PaymentFailedError(result.message or "Payment failed")
        return self.payment_repo.add(Payment(member_id, month, amount, result.reference))

    def total_paid(self, member_id: int, month: str) -> float:
        """Return the total amount paid by a member for a month."""
        return self.payment_repo.total_paid(member_id, month)

    def due_for(self, member_id: int, month: str, charge: float) -> float:
        """Return remaining due (charge minus total paid) rounded to two decimals."""
        return round(charge - self.payment_repo.total_paid(member_id, month), 2)

    def list_for_month(self, month: str) -> list[Payment]:
        """Validate the month format and return all payments for that month."""
        check_month(month)
        return self.payment_repo.list_for_month(month)
