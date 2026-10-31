from app.errors import ValidationError
from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.validation import check_date, check_month


class ExpenseService:
    """Business logic and validation for recording and querying bazar expenses."""

    def __init__(self, expense_repo: ExpenseRepository) -> None:
        self.expense_repo = expense_repo

    def add_expense(self, expense_date: str, description: str, amount: float) -> Expense:
        """Validate inputs and record a new bazar expense."""
        check_date(expense_date)
        description = description.strip()
        if not description:
            raise ValidationError("Description is required")
        if type(amount) not in (int, float) or amount <= 0:
            raise ValidationError("Amount must be a number greater than 0")
        return self.expense_repo.add(Expense(expense_date, description, round(amount, 2)))

    def list_for_month(self, month: str) -> list[Expense]:
        """Validate the month format and return all expenses for that month."""
        check_month(month)
        return self.expense_repo.list_for_month(month)

    def total_for_month(self, month: str) -> float:
        """Validate the month format and return total expenses for that month."""
        check_month(month)
        return self.expense_repo.total_for_month(month)
