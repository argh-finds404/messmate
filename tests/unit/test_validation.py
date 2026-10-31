import pytest

from app.errors import ValidationError
from app.validation import check_date, check_month


def test_check_date_returns_valid_date():
    assert check_date("2026-10-31") == "2026-10-31"


def test_check_date_accepts_leap_day():
    assert check_date("2024-02-29") == "2024-02-29"


@pytest.mark.parametrize(
    "value",
    ["", "2026-10-1", "31-10-2026", "2026-13-01", "2026-02-30", "2026/10/31", None, 20261031],
)
def test_check_date_rejects_bad_values(value):
    with pytest.raises(ValidationError, match="Date must be"):
        check_date(value)


def test_check_month_returns_valid_month():
    assert check_month("2026-10") == "2026-10"


@pytest.mark.parametrize("value", ["", "2026-1", "2026-00", "2026-13", "October", "2026-10-01", None])
def test_check_month_rejects_bad_values(value):
    with pytest.raises(ValidationError, match="Month must be"):
        check_month(value)
