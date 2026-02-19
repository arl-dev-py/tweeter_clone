import pytest
from fastapi.testclient import TestClient

def test_api_key_required(client):
    resp = client.get("/api/v1/medias/")
    assert resp.status_code == 401

def test_api_key_valid(client):
    resp = client.get("/api/v1/medias/", headers={"Authorization": "Bearer test-api-key"})
    assert resp.status_code == 200

def test_create_media_invalid(client):
    resp = client.post("/api/v1/medias/", headers={"Authorization": "Bearer test-api-key"}, json={"tweet_id": 1})
    assert resp.status_code == 422
