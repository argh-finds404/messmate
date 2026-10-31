from abc import ABC, abstractmethod


class BillingStrategy(ABC):
    """Decides how much each member pays for a month."""

    @abstractmethod
    def calculate(self, meals_by_member: dict[int, int], total_expense: float) -> dict[int, float]:
        """Return the charge for every member id in meals_by_member."""


class PerMealRateStrategy(BillingStrategy):
    """Charge = member meals x (total expense / total meals)."""

    def calculate(self, meals_by_member: dict[int, int], total_expense: float) -> dict[int, float]:
        total_meals = sum(meals_by_member.values())
        if total_meals == 0:
            return {member_id: 0.0 for member_id in meals_by_member}
        rate = total_expense / total_meals
        return {member_id: round(meals * rate, 2) for member_id, meals in meals_by_member.items()}


class EqualSplitStrategy(BillingStrategy):
    """Everyone pays the same share, whatever they ate."""

    def calculate(self, meals_by_member: dict[int, int], total_expense: float) -> dict[int, float]:
        if not meals_by_member:
            return {}
        share = round(total_expense / len(meals_by_member), 2)
        return {member_id: share for member_id in meals_by_member}
