# EVA-STORY: ACA-04-004
# EVA-STORY: ACA-04-005
# EVA-STORY: ACA-04-009
# EVA-STORY: ACA-04-001
"""Sprint 17 auth endpoint tests"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_unauthenticated():
    """Story ACA-04-001: /health returns 200 without auth"""
    response = client.get("/v1/auth/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["store"] == "cosmos"
    assert data["version"] == "1.0.0"


def test_connect_with_valid_token():
    """Story ACA-04-004: POST /connect with delegated_token succeeds"""
    payload = {
        "delegated_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
        "desired_tier": "TIER2",
    }
    response = client.post("/v1/auth/connect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert data["subscriptionId"] == "00000000-0000-0000-0000-000000000001"
    assert data["tier"] == "TIER2"
    assert "connectedAt" in data


def test_connect_missing_token():
    """Story ACA-04-004: POST /connect without delegated_token returns 400"""
    payload = {"desired_tier": "TIER1"}
    response = client.post("/v1/auth/connect", json=payload)
    assert response.status_code == 422  # Missing required field


def test_disconnect_not_authenticated():
    """Story ACA-04-005: POST /disconnect without auth returns 401"""
    # No subscription context in request.state
    response = client.post("/v1/auth/disconnect")
    assert response.status_code == 401
    detail = response.json()["detail"]
    assert "authenticated" in detail.lower()


def test_preflight_not_authenticated():
    """Story ACA-04-009: POST /preflight without auth returns 401"""
    response = client.post("/v1/auth/preflight")
    assert response.status_code == 401
    detail = response.json()["detail"]
    assert "authenticated" in detail.lower()
