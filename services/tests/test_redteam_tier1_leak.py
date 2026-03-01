# EVA-STORY: ACA-03-010
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_tier1_findings_no_leak(client):
    """Ensure Tier 1 findings do not contain forbidden fields."""
    response = client.get("/v1/findings", headers={"Authorization": "Bearer fake-tier1-token"})
    assert response.status_code == 200, "[FAIL] API did not return 200 OK"

    findings = response.json()
    forbidden_fields = ["narrative", "deliverable_template_id", "evidence_refs"]

    for finding in findings:
        for field in forbidden_fields:
            assert field not in finding, f"[LEAK] Forbidden field '{field}' found in Tier 1 findings."

    print("[PASS] No forbidden fields found in Tier 1 findings.")

def test_tier1_findings_with_leak(client):
    """Simulate a leak scenario for Tier 1 findings."""
    response = client.get("/v1/findings", headers={"Authorization": "Bearer fake-tier1-token"})
    assert response.status_code == 200, "[FAIL] API did not return 200 OK"

    findings = response.json()
    forbidden_fields = ["narrative", "deliverable_template_id", "evidence_refs"]

    # Simulate a leak by adding forbidden fields
    findings[0]["narrative"] = "Leaked narrative"
    findings[0]["deliverable_template_id"] = "Leaked template ID"

    for finding in findings:
        for field in forbidden_fields:
            if field in finding:
                print(f"[LEAK] Forbidden field '{field}' found in Tier 1 findings.")
                assert False, f"[LEAK] Forbidden field '{field}' found in Tier 1 findings."

    print("[PASS] No forbidden fields found in Tier 1 findings.")
