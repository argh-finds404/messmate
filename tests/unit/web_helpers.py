import re


def add_member(client, name="Rafi", room="101", phone="01711111111"):
    return client.post(
        "/members", data={"name": name, "room": room, "phone": phone}, follow_redirects=True
    )


def add_meal(client, member_id, meal_date, meal_count):
    return client.post(
        "/meals",
        data={"member_id": str(member_id), "meal_date": meal_date, "meal_count": str(meal_count)},
        follow_redirects=True,
    )


def add_expense(client, expense_date, description, amount):
    return client.post(
        "/expenses",
        data={"expense_date": expense_date, "description": description, "amount": amount},
        follow_redirects=True,
    )


def pay(client, member_id, month, amount):
    return client.post(
        "/payments",
        data={"member_id": str(member_id), "month": month, "amount": amount},
        follow_redirects=True,
    )


def seed_october(client):
    """Rafi eats 3 meals, Sami 1, and the mess spent 400: per-meal rate is 100."""
    add_member(client, "Rafi", "101", "01711111111")
    add_member(client, "Sami", "102", "01722222222")
    add_meal(client, 1, "2026-10-01", 3)
    add_meal(client, 2, "2026-10-01", 1)
    add_expense(client, "2026-10-02", "Rice", "400")


def cells(html, css_class):
    """Text of every <td class="css_class"> in the page, in order."""
    return re.findall(rf'<td class="{css_class}">([^<]*)</td>', html)
