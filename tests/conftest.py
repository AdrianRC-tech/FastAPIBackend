import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.user_service import user_service
from app.services.quota_service import quota_service


@pytest.fixture(autouse=True)
def reset_in_memory_state():
    """Reset global in-memory stores before each test."""
    user_service.users_db.clear()
    quota_service.request_log.clear()
    yield

@pytest.fixture
def client():
    """Provide FastAPI test client."""
    return TestClient(app)