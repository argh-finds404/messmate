import datetime
import re

from app.errors import ValidationError


def check_date(value: str) -> str:
    """Validate that value is a real calendar date in YYYY-MM-DD format."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValidationError("Date must be a real date in YYYY-MM-DD format")
    try:
        datetime.date.fromisoformat(value)
    except ValueError as err:
        raise ValidationError("Date must be a real date in YYYY-MM-DD format") from err
    return value


def check_month(value: str) -> str:
    """Validate that value is a month string in YYYY-MM format."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        raise ValidationError("Month must be in YYYY-MM format")
    return value
