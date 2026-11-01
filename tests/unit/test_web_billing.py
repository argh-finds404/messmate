from tests.unit.web_helpers import add_member, cells, pay, seed_october


def test_per_meal_bill(client):
    seed_october(client)
    html = client.get("/billing?month=2026-10&strategy=per_meal").get_data(as_text=True)
    assert cells(html, "member-name") == ["Rafi", "Sami"]
    assert cells(html, "meals") == ["3", "1"]
    assert cells(html, "charge") == ["300.00", "100.00"]
    assert cells(html, "due") == ["300.00", "100.00"]
    assert '<p id="bill-total">Total charges: 400.00</p>' in html


def test_equal_split_bill(client):
    seed_october(client)
    html = client.get("/billing?month=2026-10&strategy=equal").get_data(as_text=True)
    assert cells(html, "charge") == ["200.00", "200.00"]


def test_per_meal_is_the_default_strategy(client):
    seed_october(client)
    html = client.get("/billing?month=2026-10").get_data(as_text=True)
    assert cells(html, "charge") == ["300.00", "100.00"]


def test_unknown_strategy_shows_error_and_falls_back(client):
    seed_october(client)
    html = client.get("/billing?month=2026-10&strategy=lottery").get_data(as_text=True)
    assert "Unknown billing strategy" in html
    assert cells(html, "charge") == ["300.00", "100.00"]


def test_bad_month_shows_error_and_still_renders(client):
    response = client.get("/billing?month=oops")
    assert response.status_code == 200
    assert "Month must be in YYYY-MM format" in response.get_data(as_text=True)


def test_payment_reduces_the_due_amount(client):
    seed_october(client)
    pay(client, 2, "2026-10", "100")
    html = client.get("/billing?month=2026-10&strategy=per_meal").get_data(as_text=True)
    assert cells(html, "paid") == ["0.00", "100.00"]
    assert cells(html, "due") == ["300.00", "0.00"]


def test_inactive_members_are_not_billed(client):
    seed_october(client)
    client.post("/members/2/deactivate")
    html = client.get("/billing?month=2026-10&strategy=equal").get_data(as_text=True)
    assert cells(html, "member-name") == ["Rafi"]
    assert cells(html, "charge") == ["400.00"]


def test_notify_sends_one_notice_per_member_who_owes(client, capsys):
    seed_october(client)
    html = client.post(
        "/billing/notify", data={"month": "2026-10", "strategy": "per_meal"}, follow_redirects=True
    ).get_data(as_text=True)
    assert "Sent 2 bill notices" in html
    printed = capsys.readouterr().out
    assert "[notify] to 01711111111: Dear Rafi, your mess bill for 2026-10 is 300.00 BDT." in printed


def test_notify_with_nothing_to_send(client):
    add_member(client)
    html = client.post(
        "/billing/notify", data={"month": "2026-10", "strategy": "per_meal"}, follow_redirects=True
    ).get_data(as_text=True)
    assert "Sent 0 bill notices" in html


def test_notify_with_bad_month_shows_error(client):
    html = client.post(
        "/billing/notify", data={"month": "oops", "strategy": "per_meal"}, follow_redirects=True
    ).get_data(as_text=True)
    assert "Month must be in YYYY-MM format" in html
