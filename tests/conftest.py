"""
Pytest fixtures. Uses SQLite so tests run without PostgreSQL.
Set DATABASE_URL before app is loaded so the app uses SQLite in tests.
"""
import os
import pytest

# Use file-based SQLite for tests so one DB is shared (must be set before app.db is imported)
_tests_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tests_dir, 'test.db')}"

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    """Reset DB state before each test so tests are isolated."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    """HTTP client for the FastAPI app."""
    return TestClient(app)
