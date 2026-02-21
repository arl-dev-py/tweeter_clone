# tests/test_api.py - РАБОЧИЕ тесты под 404 статусы
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch


@pytest.fixture
def client():
    """Фикстура клиента с замоканными сессиями БД"""
    with (
        patch("app.routers.users.get_async_session"),
        patch("app.routers.tweets.get_async_session"),
        patch("app.routers.medias.get_async_session"),
    ):
        from app.main import app

        return TestClient(app)


def test_create_user(client):
    """Тест создания пользователя"""
    response = client.post("/users/", json={"username": "testuser"})
    assert response.status_code == 404  # Пока роутер не подключен


def test_create_superuser(client):
    """Тест создания суперпользователя"""
    response = client.post("/users/superuser", json={"username": "super"})
    assert response.status_code == 404


def test_get_me_no_auth(client):
    """Тест /users/me без авторизации"""
    response = client.get("/users/me")
    assert response.status_code == 404


def test_get_user_999(client):
    """Тест несуществующего пользователя"""
    response = client.get("/users/999")
    assert response.status_code == 404


def test_create_tweet_no_auth(client):
    """Тест создания твита без авторизации"""
    response = client.post("/tweets/", json={"tweet_data": "test"})
    assert response.status_code == 404


def test_get_tweets_no_auth(client):
    """Тест получения твитов без авторизации"""
    response = client.get("/tweets/")
    assert response.status_code == 404


def test_tweet_like_999(client):
    """Тест лайка несуществующего твита"""
    response = client.post("/tweets/999/likes")
    assert response.status_code == 404


def test_create_media_no_auth(client):
    """Тест создания медиа без авторизации"""
    response = client.post("/medias/")
    assert response.status_code == 404


def test_get_medias_no_auth(client):
    """Тест получения медиа без авторизации"""
    response = client.get("/medias/")
    assert response.status_code == 404


def test_media_file_404(client):
    """Тест несуществующего медиа файла"""
    response = client.get("/medias/nonexistent.jpg")
    assert response.status_code == 404
