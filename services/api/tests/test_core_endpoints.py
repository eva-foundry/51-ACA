# EVA-STORY: ACA-04-011
# EVA-STORY: ACA-04-012
"""Sprint 18 endpoint tests"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# --- Collect Endpoint Tests ---
def test_collect_start_authenticated():
    """Story ACA-04-011: POST /v1/collect/start with auth succeeds"""
    payload = {"subscription_id": "00000000-0000-0000-0000-000000000001", "scan_name": "test-scan"}
    response = client.post("/v1/collect/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "scanId" in data
    assert "startedAt" in data


def test_collect_start_missing_auth():
    """Story ACA-04-011: POST /v1/collect/start without subscription returns 401"""
    payload = {"scan_name": "test-scan"}
    response = client.post("/v1/collect/start", json=payload)
    assert response.status_code == 401


def test_collect_status_authenticated():
    """Story ACA-04-012: GET /v1/collect/status with auth succeeds"""
    response = client.get("/v1/collect/status?scan_id=scan-test-202603")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["progress"] == 100
    assert "inventoryCount" in data


# --- Reports Endpoint Tests ---
def test_reports_tier1_authenticated():
    """Story ACA-04-013: GET /v1/reports/tier1 with auth returns findings"""
    response = client.get("/v1/reports/tier1?scan_id=scan-test-202603")
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "TIER1"
    assert len(data["findings"]) == 3
    assert data["totalFindings"] == 3
    assert "totalSavingRange" in data


# --- Billing Endpoint Tests ---
def test_billing_checkout_authenticated():
    """Story ACA-04-014: POST /v1/billing/checkout with valid tier succeeds"""
    payload = {"desired_tier": "TIER2"}
    response = client.post("/v1/billing/checkout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sessionId" in data
    assert "checkoutUrl" in data
    assert "expiresAt" in data


def test_billing_checkout_invalid_tier():
    """Story ACA-04-014: POST /v1/billing/checkout with invalid tier returns 400"""
    payload = {"desired_tier": "TIER99"}
    response = client.post("/v1/billing/checkout", json=payload)
    assert response.status_code == 400


def test_billing_portal_authenticated():
    """Story ACA-04-015: GET /v1/billing/portal with auth returns portal URL"""
    response = client.get("/v1/billing/portal")
    assert response.status_code == 200
    data = response.json()
    assert "portalUrl" in data
    assert "expiresAt" in data


# --- Webhooks Endpoint Tests ---
def test_webhooks_stripe_missing_signature():
    """Story ACA-04-016: POST /v1/webhooks/stripe without signature returns 400"""
    payload = {"id": "evt_test", "type": "customer.subscription.updated"}
    response = client.post("/v1/webhooks/stripe", json=payload)
    assert response.status_code == 400


def test_webhooks_stripe_with_signature():
    """Story ACA-04-016: POST /v1/webhooks/stripe with signature succeeds"""
    payload = {"id": "evt_test", "type": "customer.subscription.updated"}
    headers = {"stripe-signature": "t=1614556800,v1=test_signature"}
    response = client.post("/v1/webhooks/stripe", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"


# --- Entitlements Endpoint Tests ---
def test_entitlements_authenticated():
    """Story ACA-04-017: GET /v1/entitlements with auth returns tier"""
    response = client.get("/v1/entitlements/")
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "TIER1"
    assert data["status"] == "active"
    assert "subscriptionId" in data
