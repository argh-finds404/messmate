from app.models.bill import BillLine
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.meal_repository import MealRepository
from app.repositories.member_repository import MemberRepository
from app.services.billing_strategies import BillingStrategy
from app.validation import check_month


class BillingService:
    """Generates monthly bill lines for active members using a BillingStrategy."""

    def __init__(
        self,
        member_repo: MemberRepository,
        meal_repo: MealRepository,
        expense_repo: ExpenseRepository,
    ) -> None:
        self.member_repo = member_repo
        self.meal_repo = meal_repo
        self.expense_repo = expense_repo

    def generate_bill(self, month: str, strategy: BillingStrategy) -> list[BillLine]:
        """Compute monthly bill lines for all active members using the given strategy."""
        check_month(month)
        members = self.member_repo.list_all(active_only=True)
        totals = self.meal_repo.month_totals(month)
        total_expense = self.expense_repo.total_for_month(month)
        meals_by_member = {m.id: totals.get(m.id, 0) for m in members}
        charges = strategy.calculate(meals_by_member, total_expense)
        return [
            BillLine(m.id, m.name, meals_by_member[m.id], charges[m.id])
            for m in members
        ]
