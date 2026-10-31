from tests.unit.web_helpers import add_member, cells


def test_home_redirects_to_members(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/members")


def test_members_page_starts_empty(client):
    response = client.get("/members")
    assert response.status_code == 200
    assert 'id="no-members"' in response.get_data(as_text=True)


def test_adding_a_member_shows_it_in_the_table(client):
    html = add_member(client).get_data(as_text=True)
    assert cells(html, "member-name") == ["Rafi"]
    assert cells(html, "member-status") == ["Active"]
    assert "Added Rafi" in html
    assert 'id="no-members"' not in html


def test_invalid_phone_shows_error_and_adds_nothing(client):
    html = add_member(client, phone="123").get_data(as_text=True)
    assert "Phone must be 11 digits starting with 01" in html
    assert 'id="no-members"' in html


def test_empty_name_shows_error(client):
    html = add_member(client, name="").get_data(as_text=True)
    assert "Name is required" in html


def test_duplicate_phone_is_rejected(client):
    add_member(client)
    html = add_member(client, name="Sami").get_data(as_text=True)
    assert "Phone already registered" in html
    assert cells(html, "member-name") == ["Rafi"]


def test_deactivating_a_member_marks_them_inactive(client):
    add_member(client)
    html = client.post("/members/1/deactivate", follow_redirects=True).get_data(as_text=True)
    assert cells(html, "member-status") == ["Inactive"]
    assert 'id="deactivate-1"' not in html


def test_deactivating_unknown_member_shows_error(client):
    html = client.post("/members/99/deactivate", follow_redirects=True).get_data(as_text=True)
    assert "Member not found" in html
