# EVA-STORY: ACA-03-013
from services.analysis.app.rules import r03_defender_mismatch as r03


def test_defender_costs_above_threshold(monkeypatch):
    monkeypatch.setattr(r03, "persist_finding", lambda cosmos_client, finding: None, raising=False)
    findings = r03.evaluate_defender_costs(
        defender_cost_data=[
            {"serviceName": "Microsoft Defender for Cloud", "totalAnnualCost": 2500}
        ],
        subscription_id="sub-123",
        scan_id="scan-456",
    )

    assert len(findings) == 1
    assert findings[0]["category"] == "security-cost-optimization"
    assert findings[0]["title"] == "High Microsoft Defender for Cloud Costs"
    assert findings[0]["estimated_saving_high"] == 2500


def test_defender_costs_below_threshold(monkeypatch):
    monkeypatch.setattr(r03, "persist_finding", lambda cosmos_client, finding: None, raising=False)
    findings = r03.evaluate_defender_costs(
        defender_cost_data=[
            {"serviceName": "Microsoft Defender for Cloud", "totalAnnualCost": 1500}
        ],
        subscription_id="sub-123",
        scan_id="scan-456",
    )

    assert len(findings) == 0
