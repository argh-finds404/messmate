import pytest

from app.models.member import Member
from app.models.payment import Payment
from app.repositories.member_repository import MemberRepository
from app.repositories.payment_repository import PaymentRepository


def make_member(conn, phone="01711111111"):
    return MemberRepository(conn).add(Member("Rafi", "101", phone))


def test_add_assigns_id_and_persists(conn):
    member = make_member(conn)
    saved = PaymentRepository(conn).add(Payment(member.id, "2026-10", 500.0, "TX1"))
    assert saved.id is not None


def test_total_paid_sums_only_that_member_and_month(conn):
    first = make_member(conn, "01711111111")
    second = make_member(conn, "01722222222")
    repo = PaymentRepository(conn)
    repo.add(Payment(first.id, "2026-10", 500.0, "TX1"))
    repo.add(Payment(first.id, "2026-10", 250.5, "TX2"))
    repo.add(Payment(first.id, "2026-11", 100.0, "TX3"))
    repo.add(Payment(second.id, "2026-10", 999.0, "TX4"))
    assert repo.total_paid(first.id, "2026-10") == pytest.approx(750.5)


def test_total_paid_is_zero_when_nothing_paid(conn):
    member = make_member(conn)
    assert PaymentRepository(conn).total_paid(member.id, "2026-10") == 0.0


def test_list_for_month_returns_that_month_only_in_order(conn):
    member = make_member(conn)
    repo = PaymentRepository(conn)
    repo.add(Payment(member.id, "2026-10", 100.0, "TX1"))
    repo.add(Payment(member.id, "2026-11", 200.0, "TX2"))
    repo.add(Payment(member.id, "2026-10", 300.0, "TX3"))
    assert [p.reference for p in repo.list_for_month("2026-10")] == ["TX1", "TX3"]
