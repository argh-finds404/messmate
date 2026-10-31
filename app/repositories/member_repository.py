import sqlite3

from app.models.member import Member


def _row_to_member(row: sqlite3.Row) -> Member:
    """Convert a SQLite row into a Member dataclass."""
    return Member(
        name=row["name"],
        room=row["room"],
        phone=row["phone"],
        active=bool(row["active"]),
        id=row["id"],
    )


class MemberRepository:
    """SQLite data access for the members table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, member: Member) -> Member:
        """Insert a new member and return it with its generated id."""
        cursor = self.conn.execute(
            "INSERT INTO members (name, room, phone, active) VALUES (?, ?, ?, ?)",
            (member.name, member.room, member.phone, int(member.active)),
        )
        self.conn.commit()
        return Member(
            name=member.name,
            room=member.room,
            phone=member.phone,
            active=member.active,
            id=cursor.lastrowid,
        )

    def get(self, member_id: int) -> Member | None:
        """Return the member with the given id, or None if not found."""
        row = self.conn.execute(
            "SELECT id, name, room, phone, active FROM members WHERE id = ?",
            (member_id,),
        ).fetchone()
        return _row_to_member(row) if row else None

    def find_by_phone(self, phone: str) -> Member | None:
        """Return the member with the given phone number, or None if not found."""
        row = self.conn.execute(
            "SELECT id, name, room, phone, active FROM members WHERE phone = ?",
            (phone,),
        ).fetchone()
        return _row_to_member(row) if row else None

    def list_all(self, active_only: bool = False) -> list[Member]:
        """Return all members ordered by id, optionally filtered to active members."""
        if active_only:
            rows = self.conn.execute(
                "SELECT id, name, room, phone, active FROM members WHERE active = 1 ORDER BY id"
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT id, name, room, phone, active FROM members ORDER BY id"
            ).fetchall()
        return [_row_to_member(row) for row in rows]

    def set_active(self, member_id: int, active: bool) -> None:
        """Update the active status of a member."""
        self.conn.execute(
            "UPDATE members SET active = ? WHERE id = ?",
            (int(active), member_id),
        )
        self.conn.commit()
