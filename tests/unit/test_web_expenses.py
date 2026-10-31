import pytest

from tests.unit.web_helpers import add_expense, cells


def test_expenses_page_starts_empty(client):
    html = client.get("/expenses?month=2026-10").get_data(as_text=True)
    assert 'id="no-expenses"' in html
    assert '<p id="month-total">Total: 0.00</p>' in html


def test_adding_an_expense_lists_it_and_updates_the_total(client):
    html = add_expense(client, "2026-10-02", "Rice", "400").get_data(as_text=True)
    assert "Expense added" in html
    assert cells(html, "description") == ["Rice"]
    assert cells(html, "amount") == ["400.00"]
    assert '<p id="month-total">Total: 400.00</p>' in html


def test_total_adds_up_several_expenses(client):
    add_expense(client, "2026-10-02", "Rice", "400")
    html = add_expense(client, "2026-10-05", "Fish", "250.50").get_data(as_text=True)
    assert '<p id="month-total">Total: 650.50</p>' in html


@pytest.mark.parametrize("amount", ["abc", "0", "-5", "", "nan", "inf"])
def test_invalid_amount_shows_error(client, amount):
    html = add_expense(client, "2026-10-02", "Rice", amount).get_data(as_text=True)
    assert "Amount must be a number greater than 0" in html


def test_empty_description_shows_error(client):
    html = add_expense(client, "2026-10-02", "  ", "100").get_data(as_text=True)
    assert "Description is required" in html


def test_bad_date_shows_error(client):
    html = add_expense(client, "2026-13-02", "Rice", "100").get_data(as_text=True)
    assert "Date must be" in html
