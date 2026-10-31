from tests.unit.web_helpers import add_meal, add_member, cells


def test_meals_page_lists_active_members_with_zero_totals(client):
    add_member(client)
    html = client.get("/meals?month=2026-10").get_data(as_text=True)
    assert cells(html, "member-name") == ["Rafi"]
    assert cells(html, "meal-total") == ["0"]


def test_recording_meals_updates_the_monthly_total(client):
    add_member(client)
    add_meal(client, 1, "2026-10-01", 2)
    html = add_meal(client, 1, "2026-10-02", 3).get_data(as_text=True)
    assert "Meals saved" in html
    assert cells(html, "meal-total") == ["5"]


def test_same_day_entry_is_overwritten(client):
    add_member(client)
    add_meal(client, 1, "2026-10-01", 2)
    html = add_meal(client, 1, "2026-10-01", 1).get_data(as_text=True)
    assert cells(html, "meal-total") == ["1"]


def test_invalid_meal_count_shows_error(client):
    add_member(client)
    html = add_meal(client, 1, "2026-10-01", 7).get_data(as_text=True)
    assert "Meal count must be a whole number from 0 to 3" in html


def test_non_numeric_meal_count_shows_error(client):
    add_member(client)
    html = add_meal(client, 1, "2026-10-01", "abc").get_data(as_text=True)
    assert "Meal count must be a whole number from 0 to 3" in html


def test_unknown_member_shows_error(client):
    html = add_meal(client, 99, "2026-10-01", 2).get_data(as_text=True)
    assert "Member not found" in html


def test_bad_date_shows_error(client):
    add_member(client)
    html = add_meal(client, 1, "01-10-2026", 2).get_data(as_text=True)
    assert "Date must be" in html


def test_inactive_member_is_not_listed(client):
    add_member(client)
    client.post("/members/1/deactivate")
    html = client.get("/meals?month=2026-10").get_data(as_text=True)
    assert cells(html, "member-name") == []


def test_bad_month_in_url_shows_error_and_still_renders(client):
    response = client.get("/meals?month=oops")
    assert response.status_code == 200
    assert "Month must be in YYYY-MM format" in response.get_data(as_text=True)
