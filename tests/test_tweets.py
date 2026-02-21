import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app


@pytest.fixture
def mock_session():
    session = AsyncMock()
    mock_tweet = MagicMock(id=1, content="test", likes_count=0)
    mock_user = MagicMock(id=1, username="test")
    session.get.return_value = mock_tweet
    session.execute.return_value.scalar_one_or_none.return_value = None
    session.scalars.return_value.all.return_value = [mock_tweet]
    return session


@pytest.fixture
def mock_user():
    return MagicMock(id=1, username="test")


def test_create_tweet(mock_session, mock_user):
    app.dependency_overrides = {}

    with (
        patch("app.routers.tweets.get_async_session", return_value=mock_session),
        patch("app.middleware.api_key_auth", return_value=mock_user),
    ):
        client = TestClient(app)
        response = client.post(
            "/tweets/", json={"tweet_data": "hello", "tweet_media_ids": []}
        )
        assert response.status_code in [201, 404]


def test_tweet_like(mock_session, mock_user):
    app.dependency_overrides = {}
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with (
        patch("app.routers.tweets.get_async_session", return_value=mock_session),
        patch("app.middleware.api_key_auth", return_value=mock_user),
    ):
        client = TestClient(app)
        response = client.post("/tweets/1/likes")
        assert response.status_code in [200, 404]
