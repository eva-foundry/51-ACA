# EVA-STORY: ACA-03-008

import pytest
from unittest.mock import patch
from app.services.findings_gate import gate_findings, TIER2_FIELDS

def test_gate_findings_tier2():
    findings = [
        {
            "id": "f1",
            "category": "cost",
            "title": "Optimize VM",
            "estimated_saving_low": 100,
            "estimated_saving_high": 200,
            "effort_class": "low",
            "risk_class": "medium",
            "narrative": "Reduce VM size for cost savings.",
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
            "narrative": "Enable MFA for all users.",
            "evidence_refs": ["ref3"],
            "deliverable_template_id": "template456"
        }
    ]

    gated_findings = gate_findings(findings, "tier2")

    assert len(gated_findings) == 2
    for finding in gated_findings:
        assert all(key in TIER2_FIELDS for key in finding.keys())
        assert "deliverable_template_id" not in finding

if __name__ == "__main__":
    pytest.main(["-v", "--tb=short", "services/tests/test_findings_tier2_gating.py"])