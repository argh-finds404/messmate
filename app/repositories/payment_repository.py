import sqlite3

from app.models.payment import Payment


def _row_to_payment(row: sqlite3.Row) -> Payment:
    """Convert a SQLite row into a Payment dataclass."""
    return Payment(
        member_id=row["member_id"],
        month=row["month"],
        amount=float(row["amount"]),
        reference=row["reference"],
        id=row["id"],
    )


class PaymentRepository:
    """SQLite data access for the payments table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, payment: Payment) -> Payment:
        """Insert a new payment and return it with its generated id."""
        cursor = self.conn.execute(
            "INSERT INTO payments (member_id, month, amount, reference) VALUES (?, ?, ?, ?)",
            (payment.member_id, payment.month, payment.amount, payment.reference),
        )
        self.conn.commit()
        return Payment(
            member_id=payment.member_id,
            month=payment.month,
            amount=payment.amount,
            reference=payment.reference,
            id=cursor.lastrowid,
        )

    def total_paid(self, member_id: int, month: str) -> float:
        """Return the total amount paid by a member for a month, or 0.0 when empty."""
        row = self.conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE member_id = ? AND month = ?
            """,
            (member_id, month),
        ).fetchone()
        return float(row["total"])

    def list_for_month(self, month: str) -> list[Payment]:
        """Return all payments for a month ordered by id."""
        rows = self.conn.execute(
            """
            SELECT id, member_id, month, amount, reference
            FROM payments
            WHERE month = ?
            ORDER BY id
            """,
            (month,),
        ).fetchall()
        return [_row_to_payment(row) for row in rows]
