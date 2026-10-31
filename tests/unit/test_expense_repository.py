import pytest

from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository


def test_add_assigns_id_and_persists(conn):
    repo = ExpenseRepository(conn)
    saved = repo.add(Expense("2026-10-03", "Rice", 850.5))
    assert saved.id is not None
    assert repo.list_for_month("2026-10")[0].description == "Rice"


def test_list_for_month_filters_and_orders_by_date(conn):
    repo = ExpenseRepository(conn)
    repo.add(Expense("2026-10-05", "Fish", 300.0))
    repo.add(Expense("2026-10-02", "Rice", 500.0))
    repo.add(Expense("2026-11-01", "Oil", 200.0))
    assert [e.description for e in repo.list_for_month("2026-10")] == ["Rice", "Fish"]


def test_total_for_month_sums_amounts_of_that_month_only(conn):
    repo = ExpenseRepository(conn)
    repo.add(Expense("2026-10-05", "Fish", 300.0))
    repo.add(Expense("2026-10-02", "Rice", 500.5))
    repo.add(Expense("2026-11-01", "Oil", 200.0))
    assert repo.total_for_month("2026-10") == pytest.approx(800.5)


def test_total_for_month_is_zero_when_empty(conn):
    assert ExpenseRepository(conn).total_for_month("2026-10") == 0.0
