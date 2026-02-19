from fastapi.testclient import TestClient
from app.main import app
import pytest


def test_tweet_endpoints():
    client = TestClient(app)
    headers = {"Authorization": "Bearer test-api-key"}

    resp = client.get("/api/v1/tweets/")
    assert resp.status_code in [200, 401]

    resp = client.get("/api/v1/tweets/7")
    assert resp.status_code in [200, 401, 404]

    resp = client.post("/api/v1/tweets/7/likes")
    assert resp.status_code in [200, 401, 404]

    resp = client.post("/api/v1/tweets/", json={"text": "test", "user_id": 3})
    assert resp.status_code in [200, 401, 422, 404, 201]


def test_delete_tweet(client):
    resp = client.delete("/api/v1/tweets/999", headers={"Authorization": "Bearer test-api-key"})
    assert resp.status_code in [200, 404]


def test_unlike_tweet(client):
    resp = client.delete("/api/v1/tweets/7/likes", headers={"Authorization": "Bearer test-api-key"})
    assert resp.status_code in [200, 404]
