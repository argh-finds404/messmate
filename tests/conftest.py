import pytest
from app import create_app
from app.config import Config
from app.db import connect, init_schema


class TestConfig(Config):
    TESTING = True
    DATABASE = ":memory:"


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def conn():
    """A fresh in-memory database with all tables, closed after the test."""
    connection = connect(":memory:")
    init_schema(connection)
    yield connection
    connection.close()
