import sqlite3


def test_app_has_open_database(app):
    assert isinstance(app.extensions["db"], sqlite3.Connection)


def test_app_creates_tables_on_startup(app):
    rows = app.extensions["db"].execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    assert {"members", "meals", "expenses", "payments"} <= {row["name"] for row in rows}
