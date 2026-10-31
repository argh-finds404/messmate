import sqlite3

import pytest

from app.db import connect, init_schema


def table_names(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row["name"] for row in rows}


def test_init_schema_creates_all_tables():
    conn = connect(":memory:")
    init_schema(conn)
    assert {"members", "meals", "expenses", "payments"} <= table_names(conn)


def test_init_schema_can_run_twice():
    conn = connect(":memory:")
    init_schema(conn)
    init_schema(conn)
    assert "members" in table_names(conn)


def test_rows_are_accessible_by_column_name():
    conn = connect(":memory:")
    init_schema(conn)
    conn.execute("INSERT INTO members (name, room, phone) VALUES ('Rafi', '101', '01711111111')")
    row = conn.execute("SELECT name FROM members").fetchone()
    assert row["name"] == "Rafi"


def test_foreign_keys_are_enforced():
    conn = connect(":memory:")
    init_schema(conn)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO meals (member_id, meal_date, meal_count) VALUES (999, '2026-10-01', 2)"
        )
