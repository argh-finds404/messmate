import sqlite3

from app.models.expense import Expense


def _row_to_expense(row: sqlite3.Row) -> Expense:
    """Convert a SQLite row into an Expense dataclass."""
    return Expense(
        expense_date=row["expense_date"],
        description=row["description"],
        amount=float(row["amount"]),
        id=row["id"],
    )


class ExpenseRepository:
    """SQLite data access for the expenses table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, expense: Expense) -> Expense:
        """Insert a new expense and return it with its generated id."""
        cursor = self.conn.execute(
            "INSERT INTO expenses (expense_date, description, amount) VALUES (?, ?, ?)",
            (expense.expense_date, expense.description, expense.amount),
        )
        self.conn.commit()
        return Expense(
            expense_date=expense.expense_date,
            description=expense.description,
            amount=expense.amount,
            id=cursor.lastrowid,
        )

    def list_for_month(self, month: str) -> list[Expense]:
        """Return all expenses for a month ordered by expense_date, id."""
        rows = self.conn.execute(
            """
            SELECT id, expense_date, description, amount
            FROM expenses
            WHERE substr(expense_date, 1, 7) = ?
            ORDER BY expense_date, id
            """,
            (month,),
        ).fetchall()
        return [_row_to_expense(row) for row in rows]

    def total_for_month(self, month: str) -> float:
        """Return the total expense amount for a month, or 0.0 when empty."""
        row = self.conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM expenses
            WHERE substr(expense_date, 1, 7) = ?
            """,
            (month,),
        ).fetchone()
        return float(row["total"])
