from unittest.mock import Mock

import pytest

from app.adapters.payment_gateway import PaymentGateway, PaymentResult
from app.errors import NotFoundError, PaymentFailedError, ValidationError
from app.models.member import Member
from app.models.payment import Payment
from app.services.payment_service import PaymentService


@pytest.fixture
def parts():
    payment_repo, member_repo = Mock(), Mock()
    gateway = Mock(spec=PaymentGateway)
    member_repo.get.return_value = Member("Rafi", "101", "01711111111", id=1)
    gateway.charge.return_value = PaymentResult(True, reference="TX1")
    payment_repo.add.side_effect = lambda p: Payment(p.member_id, p.month, p.amount, p.reference, id=1)
    return PaymentService(payment_repo, member_repo, gateway), payment_repo, member_repo, gateway


def test_pay_charges_gateway_and_saves_payment(parts):
    service, payment_repo, _, gateway = parts
    payment = service.pay(1, "2026-10", 500.0)
    gateway.charge.assert_called_once_with("01711111111", 500.0)
    saved = payment_repo.add.call_args[0][0]
    assert (saved.member_id, saved.month, saved.amount, saved.reference) == (1, "2026-10", 500.0, "TX1")
    assert payment.id == 1


def test_pay_rounds_amount_to_two_decimals(parts):
    service, payment_repo, _, gateway = parts
    service.pay(1, "2026-10", 100.456)
    gateway.charge.assert_called_once_with("01711111111", 100.46)
    assert payment_repo.add.call_args[0][0].amount == 100.46


def test_failed_charge_raises_and_saves_nothing(parts):
    service, payment_repo, _, gateway = parts
    gateway.charge.return_value = PaymentResult(False, message="Insufficient balance")
    with pytest.raises(PaymentFailedError, match="Insufficient balance"):
        service.pay(1, "2026-10", 500.0)
    payment_repo.add.assert_not_called()


def test_failed_charge_without_message_uses_default(parts):
    service, _, _, gateway = parts
    gateway.charge.return_value = PaymentResult(False)
    with pytest.raises(PaymentFailedError, match="Payment failed"):
        service.pay(1, "2026-10", 500.0)


@pytest.mark.parametrize("amount", [0, -10, "500", None])
def test_invalid_amount_never_reaches_gateway(parts, amount):
    service, payment_repo, _, gateway = parts
    with pytest.raises(ValidationError, match="Amount must be a number greater than 0"):
        service.pay(1, "2026-10", amount)
    gateway.charge.assert_not_called()
    payment_repo.add.assert_not_called()


def test_invalid_month_never_reaches_gateway(parts):
    service, _, _, gateway = parts
    with pytest.raises(ValidationError, match="Month must be"):
        service.pay(1, "October", 500.0)
    gateway.charge.assert_not_called()


def test_unknown_member_never_reaches_gateway(parts):
    service, _, member_repo, gateway = parts
    member_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Member not found"):
        service.pay(9, "2026-10", 500.0)
    gateway.charge.assert_not_called()


def test_due_is_charge_minus_paid(parts):
    service, payment_repo, _, _ = parts
    payment_repo.total_paid.return_value = 400.0
    assert service.due_for(1, "2026-10", 1000.0) == 600.0
    payment_repo.total_paid.assert_called_once_with(1, "2026-10")


def test_overpayment_gives_negative_due(parts):
    service, payment_repo, _, _ = parts
    payment_repo.total_paid.return_value = 1200.0
    assert service.due_for(1, "2026-10", 1000.0) == -200.0


def test_due_is_rounded_to_two_decimals(parts):
    service, payment_repo, _, _ = parts
    payment_repo.total_paid.return_value = 33.333
    assert service.due_for(1, "2026-10", 100.0) == 66.67


def test_total_paid_delegates_to_repo(parts):
    service, payment_repo, _, _ = parts
    payment_repo.total_paid.return_value = 250.0
    assert service.total_paid(1, "2026-10") == 250.0
    payment_repo.total_paid.assert_called_once_with(1, "2026-10")


def test_list_for_month_validates_and_delegates(parts):
    service, payment_repo, _, _ = parts
    payment_repo.list_for_month.return_value = []
    assert service.list_for_month("2026-10") == []
    payment_repo.list_for_month.assert_called_once_with("2026-10")
    with pytest.raises(ValidationError, match="Month must be"):
        service.list_for_month("2026-13")


def test_pay_accepts_positive_amount_below_one(parts):
    service, _, _, gateway = parts
    payment = service.pay(1, "2026-10", 0.50)
    gateway.charge.assert_called_once_with("01711111111", 0.50)
    assert payment.amount == 0.50


def test_pay_exact_invalid_amount_error_message(parts):
    service, _, _, _ = parts
    with pytest.raises(ValidationError) as exc_info:
        service.pay(1, "2026-10", 0)
    assert str(exc_info.value) == "Amount must be a number greater than 0"


def test_pay_exact_unknown_member_error_message(parts):
    service, _, member_repo, _ = parts
    member_repo.get.return_value = None
    with pytest.raises(NotFoundError) as exc_info:
        service.pay(99, "2026-10", 100.0)
    assert str(exc_info.value) == "Member not found"


def test_pay_exact_failed_charge_fallback_error_message(parts):
    service, _, _, gateway = parts
    gateway.charge.return_value = PaymentResult(False, message="")
    with pytest.raises(PaymentFailedError) as exc_info:
        service.pay(1, "2026-10", 100.0)
    assert str(exc_info.value) == "Payment failed"
