from fastapi.testclient import TestClient
from app.main import app

def test_create_tweet_invalid(client):
    resp = client.post("/api/v1/tweets/", headers={"Authorization": "Bearer test-api-key"}, json={"user_id": 1})
    assert resp.status_code == 422


