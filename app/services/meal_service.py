from app.errors import NotFoundError, ValidationError
from app.models.meal import MealEntry
from app.repositories.meal_repository import MealRepository
from app.repositories.member_repository import MemberRepository
from app.validation import check_date, check_month


class MealService:
    """Business logic and validation for recording and summing meals."""

    def __init__(self, meal_repo: MealRepository, member_repo: MemberRepository) -> None:
        self.meal_repo = meal_repo
        self.member_repo = member_repo

    def record(self, member_id: int, meal_date: str, meal_count: int) -> MealEntry:
        """Validate inputs and record the daily meal count for an active member."""
        if type(meal_count) is not int or not (0 <= meal_count <= 3):
            raise ValidationError("Meal count must be a whole number from 0 to 3")
        check_date(meal_date)
        member = self.member_repo.get(member_id)
        if member is None:
            raise NotFoundError("Member not found")
        if not member.active:
            raise ValidationError("Member is inactive")
        return self.meal_repo.set_meals(member_id, meal_date, meal_count)

    def monthly_totals(self, month: str) -> dict[int, int]:
        """Validate the month format and return meal totals per member id."""
        check_month(month)
        return self.meal_repo.month_totals(month)
