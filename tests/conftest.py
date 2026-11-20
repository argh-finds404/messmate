import pytest
from app import create_app
from app.config import Config
from app.db import connect, init_schema


class TestConfig(Config):
    TESTING = True
    DATABASE = ":memory:"


@pytest.fixture
def app():
    """Create a test Flask app backed by an in-memory database and close it afterwards."""
    flask_app = create_app(TestConfig)
    yield flask_app
    flask_app.extensions["db"].close()


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
