# EVA-STORY: ACA-03-009

import pytest
from app.services.findings_gate import gate_findings, TIER3_FIELDS

def test_tier3_gating():
    findings = [
        {
            "id": "f1",
            "category": "cost",
            "title": "Reduce VM size",
            "estimated_saving_low": 100,
            "estimated_saving_high": 200,
            "effort_class": "low",
            "risk_class": "low",
            "narrative": "Consider resizing VMs to save costs.",
            "evidence_refs": ["ref1", "ref2"],
            "deliverable_template_id": "template123"
        },
        {
            "id": "f2",
            "category": "security",
            "title": "Enable MFA",
            "estimated_saving_low": 0,
            "estimated_saving_high": 0,
            "effort_class": "medium",
            "risk_class": "high",
            "narrative": "Multi-factor authentication improves security.",
            "evidence_refs": ["ref3"],
            "deliverable_template_id": "template456"
        }
    ]

    result = gate_findings(findings, "tier3")

    assert len(result) == len(findings)
    for original, gated in zip(findings, result):
        assert gated == original  # Tier 3 should return full findings
        for field in TIER3_FIELDS:
            assert field in gated  # Ensure all fields are present

if __name__ == "__main__":
    pytest.main()
