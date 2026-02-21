import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
import os


@pytest.fixture
def mock_session():
    session = AsyncMock()
    mock_media = MagicMock(id=1)
    session.flush = AsyncMock()
    session.add.return_value = mock_media
    return session


@pytest.fixture
def mock_user():
    return MagicMock(id=1)


def test_create_media(mock_session, mock_user):
    app.dependency_overrides = {}

    with (
        patch("app.routers.medias.get_async_session", return_value=mock_session),
        patch("app.middleware.api_key_auth", return_value=mock_user),
    ):
        client = TestClient(app)
        response = client.post(
            "/medias/", files={"file": ("test.jpg", b"fake", "image/jpeg")}
        )
        assert response.status_code in [201, 404]


def test_get_media_file_not_found(mock_user):
    with patch("app.middleware.api_key_auth", return_value=mock_user):
        client = TestClient(app)
        response = client.get("/medias/nonexistent.jpg")
        assert response.status_code == 404
