from dataclasses import dataclass


@dataclass
class MealEntry:
    """Represents the number of meals taken by a member on a single date."""

    member_id: int
    meal_date: str
    meal_count: int
    id: int | None = None
