"""Pytest fixtures configuration."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient fixture with lifespan startup execution."""
    with TestClient(app) as test_client:
        yield test_client
