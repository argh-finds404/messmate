from tests.unit.web_helpers import add_member, cells, pay


def test_payments_page_starts_empty(client):
    html = client.get("/payments?month=2026-10").get_data(as_text=True)
    assert 'id="no-payments"' in html


def test_member_is_offered_in_the_payment_form(client):
    add_member(client)
    html = client.get("/payments?month=2026-10").get_data(as_text=True)
    assert '<option value="1">Rafi</option>' in html


def test_successful_payment_is_recorded_and_listed(client):
    add_member(client)
    html = pay(client, 1, "2026-10", "100").get_data(as_text=True)
    assert "Payment recorded (ref SBX" in html
    assert cells(html, "member-name") == ["Rafi"]
    assert cells(html, "amount") == ["100.00"]
    assert cells(html, "reference")[0].startswith("SBX")


def test_payment_is_listed_under_its_own_month_only(client):
    add_member(client)
    pay(client, 1, "2026-10", "100")
    html = client.get("/payments?month=2026-11").get_data(as_text=True)
    assert 'id="no-payments"' in html


def test_failed_payment_shows_gateway_message_and_saves_nothing(client):
    add_member(client, "Tina", "103", "01000000000")
    html = pay(client, 1, "2026-10", "100").get_data(as_text=True)
    assert "Insufficient balance" in html
    html = client.get("/payments?month=2026-10").get_data(as_text=True)
    assert 'id="no-payments"' in html


def test_invalid_amount_shows_error(client):
    add_member(client)
    for amount in ["abc", "-5", "0", ""]:
        html = pay(client, 1, "2026-10", amount).get_data(as_text=True)
        assert "Amount must be a number greater than 0" in html


def test_unknown_member_shows_error(client):
    html = pay(client, 99, "2026-10", "100").get_data(as_text=True)
    assert "Member not found" in html


def test_bad_month_shows_error(client):
    add_member(client)
    html = pay(client, 1, "oops", "100").get_data(as_text=True)
    assert "Month must be in YYYY-MM format" in html
