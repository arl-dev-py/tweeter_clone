import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="function")
def client():
    return TestClient(app)
