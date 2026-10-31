from unittest.mock import Mock

import pytest

from app.errors import ValidationError
from app.models.expense import Expense
from app.services.expense_service import ExpenseService


@pytest.fixture
def repo():
    repo = Mock()
    repo.add.side_effect = lambda e: Expense(e.expense_date, e.description, e.amount, id=1)
    return repo


@pytest.fixture
def service(repo):
    return ExpenseService(repo)


def test_add_expense_saves_valid_expense(service, repo):
    expense = service.add_expense("2026-10-03", "Rice and lentils", 850.5)
    saved = repo.add.call_args[0][0]
    assert saved.expense_date == "2026-10-03"
    assert saved.description == "Rice and lentils"
    assert saved.amount == 850.5
    assert expense.id == 1


def test_add_expense_strips_description(service, repo):
    service.add_expense("2026-10-03", "  Rice  ", 100)
    assert repo.add.call_args[0][0].description == "Rice"


def test_add_expense_rounds_amount_to_two_decimals(service, repo):
    service.add_expense("2026-10-03", "Rice", 100.456)
    assert repo.add.call_args[0][0].amount == 100.46


@pytest.mark.parametrize(
    "day, description, amount, message",
    [
        ("2026-10-03", "", 100, "Description is required"),
        ("2026-10-03", "   ", 100, "Description is required"),
        ("2026-10-03", "Rice", 0, "Amount must be a number greater than 0"),
        ("2026-10-03", "Rice", -5, "Amount must be a number greater than 0"),
        ("2026-10-03", "Rice", "100", "Amount must be a number greater than 0"),
        ("03-10-2026", "Rice", 100, "Date must be"),
    ],
)
def test_add_expense_rejects_invalid_input(service, repo, day, description, amount, message):
    with pytest.raises(ValidationError, match=message):
        service.add_expense(day, description, amount)
    repo.add.assert_not_called()


def test_list_for_month_delegates(service, repo):
    repo.list_for_month.return_value = []
    assert service.list_for_month("2026-10") == []
    repo.list_for_month.assert_called_once_with("2026-10")


def test_total_for_month_delegates(service, repo):
    repo.total_for_month.return_value = 800.5
    assert service.total_for_month("2026-10") == 800.5
    repo.total_for_month.assert_called_once_with("2026-10")


@pytest.mark.parametrize("method", ["list_for_month", "total_for_month"])
def test_month_queries_reject_bad_month(service, method):
    with pytest.raises(ValidationError, match="Month must be"):
        getattr(service, method)("October")
