import time

import pytest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

pytestmark = pytest.mark.e2e


def fill(driver, field_id, value):
    box = driver.find_element(By.ID, field_id)
    box.clear()
    box.send_keys(value)


def texts(driver, selector):
    for _ in range(10):
        try:
            return [element.text for element in driver.find_elements(By.CSS_SELECTOR, selector)]
        except StaleElementReferenceException:
            time.sleep(0.2)
    return [element.text for element in driver.find_elements(By.CSS_SELECTOR, selector)]


def add_member(driver, base, name, room, phone):
    driver.get(f"{base}/members")
    fill(driver, "name", name)
    fill(driver, "room", room)
    fill(driver, "phone", phone)
    driver.find_element(By.ID, "add-member").click()
    driver.find_element(By.CSS_SELECTOR, ".flash")


def record_meals(driver, base, member_name, meal_date, count):
    driver.get(f"{base}/meals")
    Select(driver.find_element(By.ID, "member_id")).select_by_visible_text(member_name)
    fill(driver, "meal_date", meal_date)
    fill(driver, "meal_count", count)
    driver.find_element(By.ID, "save-meals").click()
    driver.find_element(By.CSS_SELECTOR, ".flash")


def add_expense(driver, base, expense_date, description, amount):
    driver.get(f"{base}/expenses")
    fill(driver, "expense_date", expense_date)
    fill(driver, "description", description)
    fill(driver, "amount", amount)
    driver.find_element(By.ID, "add-expense").click()
    driver.find_element(By.CSS_SELECTOR, ".flash")


def make_payment(driver, base, member_name, month, amount):
    driver.get(f"{base}/payments")
    Select(driver.find_element(By.ID, "member_id")).select_by_visible_text(member_name)
    fill(driver, "month", month)
    fill(driver, "amount", amount)
    driver.find_element(By.ID, "pay").click()
    driver.find_element(By.CSS_SELECTOR, ".flash")


def bill_column(driver, css_class):
    names = texts(driver, "#bill-table tbody .member-name")
    values = texts(driver, f"#bill-table tbody .{css_class}")
    return dict(zip(names, values))


def test_register_member_through_the_browser(driver, live_server_url):
    add_member(driver, live_server_url, "Rafi", "101", "01711111111")
    assert texts(driver, "#member-table .member-name") == ["Rafi"]
    assert "Added Rafi" in driver.find_element(By.CSS_SELECTOR, ".flash.success").text


def test_invalid_phone_shows_error_in_the_browser(driver, live_server_url):
    add_member(driver, live_server_url, "Rafi", "101", "123")
    assert "Phone must be 11 digits" in driver.find_element(By.CSS_SELECTOR, ".flash.error").text
    assert driver.find_elements(By.ID, "no-members")


def test_monthly_bill_and_payment_flow(driver, live_server_url):
    base = live_server_url
    add_member(driver, base, "Rafi", "101", "01711111111")
    add_member(driver, base, "Sami", "102", "01722222222")
    record_meals(driver, base, "Rafi", "2026-10-01", "3")
    record_meals(driver, base, "Sami", "2026-10-01", "1")
    add_expense(driver, base, "2026-10-02", "Rice and lentils", "400")

    driver.get(f"{base}/billing?month=2026-10&strategy=per_meal")
    assert bill_column(driver, "charge") == {"Rafi": "300.00", "Sami": "100.00"}

    make_payment(driver, base, "Sami", "2026-10", "100")
    assert "Payment recorded" in driver.find_element(By.CSS_SELECTOR, ".flash.success").text

    driver.get(f"{base}/billing?month=2026-10&strategy=per_meal")
    assert bill_column(driver, "due") == {"Rafi": "300.00", "Sami": "0.00"}


def test_equal_split_can_be_chosen_in_the_browser(driver, live_server_url):
    base = live_server_url
    add_member(driver, base, "Rafi", "101", "01711111111")
    add_member(driver, base, "Sami", "102", "01722222222")
    record_meals(driver, base, "Rafi", "2026-10-01", "3")
    add_expense(driver, base, "2026-10-02", "Rice", "400")

    driver.get(f"{base}/billing?month=2026-10")
    Select(driver.find_element(By.ID, "strategy")).select_by_value("equal")
    driver.find_element(By.ID, "show-bill").click()
    WebDriverWait(driver, 5).until(lambda d: "strategy=equal" in d.current_url)
    assert bill_column(driver, "charge") == {"Rafi": "200.00", "Sami": "200.00"}


def test_failed_payment_is_not_recorded(driver, live_server_url):
    base = live_server_url
    add_member(driver, base, "Tina", "103", "01000000000")
    make_payment(driver, base, "Tina", "2026-10", "100")
    assert "Insufficient balance" in driver.find_element(By.CSS_SELECTOR, ".flash.error").text

    driver.get(f"{base}/payments?month=2026-10")
    assert driver.find_elements(By.ID, "no-payments")
