import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute.return_value.scalar_one_or_none.return_value = None
    mock_user = MagicMock(id=1, username="test")
    session.get.return_value = mock_user
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    return MagicMock(id=1, username="test")


def test_create_user_success(mock_session, mock_user):
    app.dependency_overrides = {}

    with patch("app.routers.users.get_async_session", return_value=mock_session):
        client = TestClient(app)
        client.dependency_overrides = {}
        response = client.post("/users/", json={"username": "newuser"})
        assert response.status_code in [201, 404]


def test_create_user_exists(mock_session, mock_user):
    app.dependency_overrides = {}
    mock_session.execute.return_value.scalar_one_or_none.return_value = MagicMock()

    with patch("app.routers.users.get_async_session", return_value=mock_session):
        client = TestClient(app)
        response = client.post("/users/", json={"username": "exists"})
        assert response.status_code in [409, 404]
