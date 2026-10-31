import sqlite3

from app.models.meal import MealEntry


def _row_to_meal(row: sqlite3.Row) -> MealEntry:
    """Convert a SQLite row into a MealEntry dataclass."""
    return MealEntry(
        member_id=row["member_id"],
        meal_date=row["meal_date"],
        meal_count=row["meal_count"],
        id=row["id"],
    )


class MealRepository:
    """SQLite data access for the meals table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def set_meals(self, member_id: int, meal_date: str, meal_count: int) -> MealEntry:
        """Insert or overwrite the meal count for a member on a date."""
        self.conn.execute(
            """
            INSERT INTO meals (member_id, meal_date, meal_count)
            VALUES (?, ?, ?)
            ON CONFLICT(member_id, meal_date) DO UPDATE SET meal_count = excluded.meal_count
            """,
            (member_id, meal_date, meal_count),
        )
        self.conn.commit()
        return self.get(member_id, meal_date)

    def get(self, member_id: int, meal_date: str) -> MealEntry | None:
        """Return the meal entry for a member on a date, or None if not found."""
        row = self.conn.execute(
            "SELECT id, member_id, meal_date, meal_count FROM meals WHERE member_id = ? AND meal_date = ?",
            (member_id, meal_date),
        ).fetchone()
        return _row_to_meal(row) if row else None

    def list_for_month(self, month: str) -> list[MealEntry]:
        """Return all meal entries for a month ordered by meal_date, member_id."""
        rows = self.conn.execute(
            """
            SELECT id, member_id, meal_date, meal_count
            FROM meals
            WHERE substr(meal_date, 1, 7) = ?
            ORDER BY meal_date, member_id
            """,
            (month,),
        ).fetchall()
        return [_row_to_meal(row) for row in rows]

    def month_totals(self, month: str) -> dict[int, int]:
        """Return total meals per member id for the given month."""
        rows = self.conn.execute(
            """
            SELECT member_id, SUM(meal_count) AS total
            FROM meals
            WHERE substr(meal_date, 1, 7) = ?
            GROUP BY member_id
            """,
            (month,),
        ).fetchall()
        return {row["member_id"]: int(row["total"]) for row in rows}
