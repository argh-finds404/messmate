from unittest.mock import Mock

import pytest

from app.errors import ValidationError
from app.models.bill import BillLine
from app.models.member import Member
from app.services.billing_service import BillingService
from app.services.billing_strategies import EqualSplitStrategy, PerMealRateStrategy


@pytest.fixture
def parts():
    member_repo, meal_repo, expense_repo = Mock(), Mock(), Mock()
    member_repo.list_all.return_value = [
        Member("Rafi", "101", "01711111111", id=1),
        Member("Sami", "102", "01722222222", id=2),
    ]
    meal_repo.month_totals.return_value = {1: 10, 2: 20}
    expense_repo.total_for_month.return_value = 3000.0
    service = BillingService(member_repo, meal_repo, expense_repo)
    return service, member_repo, meal_repo, expense_repo


def test_per_meal_bill(parts):
    service, *_ = parts
    assert service.generate_bill("2026-10", PerMealRateStrategy()) == [
        BillLine(1, "Rafi", 10, 1000.0),
        BillLine(2, "Sami", 20, 2000.0),
    ]


def test_equal_split_bill_keeps_meal_counts(parts):
    service, *_ = parts
    assert service.generate_bill("2026-10", EqualSplitStrategy()) == [
        BillLine(1, "Rafi", 10, 1500.0),
        BillLine(2, "Sami", 20, 1500.0),
    ]


def test_only_active_members_are_billed(parts):
    service, member_repo, *_ = parts
    service.generate_bill("2026-10", PerMealRateStrategy())
    member_repo.list_all.assert_called_once_with(active_only=True)


def test_member_without_meal_entries_gets_zero_meals(parts):
    service, _, meal_repo, _ = parts
    meal_repo.month_totals.return_value = {2: 20}
    lines = service.generate_bill("2026-10", PerMealRateStrategy())
    assert lines[0] == BillLine(1, "Rafi", 0, 0.0)
    assert lines[1] == BillLine(2, "Sami", 20, 3000.0)


def test_service_uses_whatever_strategy_it_is_given(parts):
    service, *_ = parts
    strategy = Mock()
    strategy.calculate.return_value = {1: 5.0, 2: 6.0}
    lines = service.generate_bill("2026-10", strategy)
    strategy.calculate.assert_called_once_with({1: 10, 2: 20}, 3000.0)
    assert [line.charge for line in lines] == [5.0, 6.0]


def test_bad_month_is_rejected(parts):
    service, *_ = parts
    with pytest.raises(ValidationError, match="Month must be"):
        service.generate_bill("2026-13", PerMealRateStrategy())
