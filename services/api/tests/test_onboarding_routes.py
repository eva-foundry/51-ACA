# EVA-STORY: ACA-15-001
# EVA-STORY: ACA-15-002
# EVA-STORY: ACA-15-003
# EVA-STORY: ACA-15-004
# EVA-STORY: ACA-15-005
# EVA-STORY: ACA-15-006
# EVA-STORY: ACA-15-007
# EVA-STORY: ACA-15-008
# EVA-STORY: ACA-15-009
# EVA-STORY: ACA-15-010
# EVA-STORY: ACA-15-011
# EVA-STORY: ACA-15-012
"""Integration-oriented onboarding tests covering API and core runtime helpers."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import onboarding
from app.services.onboarding_runtime import categorize_findings, sign_evidence_receipt


app = FastAPI()
app.include_router(onboarding.router, prefix="/v1/onboarding")
client = TestClient(app)


def test_init_get_and_decision_flow() -> None:
    init_resp = client.post("/v1/onboarding/init", json={"subscription_id": "sub-123", "tenant_id": "tenant-abc"})
    assert init_resp.status_code == 200
    data = init_resp.json()
    assert data["subscription_id"] == "sub-123"
    assert data["state"] == "initialized"

    session_id = data["session_id"]

    get_resp = client.get(f"/v1/onboarding/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["session_id"] == session_id

    decision_resp = client.post(
        f"/v1/onboarding/{session_id}/decision",
        json={"gate": "gate_3_extract", "decision": "approve"},
    )
    assert decision_resp.status_code == 200
    updated = decision_resp.json()
    assert updated["state"] == "approved"
    assert len(updated["decisions"]) == 1


def test_analysis_categorization_and_signature() -> None:
    findings = [{"rule_id": "R-01", "estimated_savings": 12000, "automatable": True, "safe_default": True}]
    categorized = categorize_findings(findings)
    assert categorized[0]["severity"] == "critical"
    assert categorized[0]["effort"] == "quick-fix"
    assert categorized[0]["risk"] == "low"

    receipt = sign_evidence_receipt({"story": "ACA-15-010", "status": "completed"}, "secret-key")
    assert receipt["algorithm"] == "HMAC-SHA256"
    assert len(receipt["signature"]) == 64
