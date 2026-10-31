from unittest.mock import Mock

import pytest

from app.errors import NotFoundError, ValidationError
from app.models.meal import MealEntry
from app.models.member import Member
from app.services.meal_service import MealService


@pytest.fixture
def parts():
    meal_repo, member_repo = Mock(), Mock()
    member_repo.get.return_value = Member("Rafi", "101", "01711111111", id=1)
    meal_repo.set_meals.side_effect = lambda mid, day, count: MealEntry(mid, day, count, id=1)
    return MealService(meal_repo, member_repo), meal_repo, member_repo


def test_record_saves_entry(parts):
    service, meal_repo, _ = parts
    entry = service.record(1, "2026-10-01", 2)
    meal_repo.set_meals.assert_called_once_with(1, "2026-10-01", 2)
    assert entry.meal_count == 2


@pytest.mark.parametrize("count", [0, 3])
def test_boundary_counts_are_accepted(parts, count):
    service, meal_repo, _ = parts
    service.record(1, "2026-10-01", count)
    meal_repo.set_meals.assert_called_once_with(1, "2026-10-01", count)


@pytest.mark.parametrize("count", [-1, 4, "2", 2.5, None])
def test_invalid_counts_are_rejected(parts, count):
    service, meal_repo, _ = parts
    with pytest.raises(ValidationError, match="Meal count must be a whole number from 0 to 3"):
        service.record(1, "2026-10-01", count)
    meal_repo.set_meals.assert_not_called()


@pytest.mark.parametrize("bad_date", ["2026-13-01", "01-10-2026", "", "2026-10-1", "2026-02-30"])
def test_invalid_dates_are_rejected(parts, bad_date):
    service, meal_repo, _ = parts
    with pytest.raises(ValidationError, match="Date must be"):
        service.record(1, bad_date, 2)
    meal_repo.set_meals.assert_not_called()


def test_unknown_member_is_rejected(parts):
    service, meal_repo, member_repo = parts
    member_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Member not found"):
        service.record(9, "2026-10-01", 2)
    meal_repo.set_meals.assert_not_called()


def test_inactive_member_is_rejected(parts):
    service, meal_repo, member_repo = parts
    member_repo.get.return_value = Member("Rafi", "101", "01711111111", active=False, id=1)
    with pytest.raises(ValidationError, match="Member is inactive"):
        service.record(1, "2026-10-01", 2)
    meal_repo.set_meals.assert_not_called()


def test_monthly_totals_delegates_to_repo(parts):
    service, meal_repo, _ = parts
    meal_repo.month_totals.return_value = {1: 5}
    assert service.monthly_totals("2026-10") == {1: 5}
    meal_repo.month_totals.assert_called_once_with("2026-10")


def test_monthly_totals_rejects_bad_month(parts):
    service, meal_repo, _ = parts
    with pytest.raises(ValidationError, match="Month must be"):
        service.monthly_totals("2026-13")
    meal_repo.month_totals.assert_not_called()
