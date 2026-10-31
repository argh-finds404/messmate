from dataclasses import dataclass


@dataclass
class Expense:
    """Represents a bazar expense entry."""

    expense_date: str
    description: str
    amount: float
    id: int | None = None
