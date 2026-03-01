# EVA-STORY: ACA-03-007
import pytest
from app.services.findings_gate import gate_findings

def test_tier1_strips_sensitive_fields():
    mock_findings = [
        {
            "id": "f1",
            "category": "compute",
            "title": "Optimize VM usage",
            "estimated_saving_low": 100,
            "estimated_saving_high": 200,
            "effort_class": "low",
            "risk_class": "low",
            "narrative": "Detailed analysis of VM usage",
            "deliverable_template_id": "template123",
            "evidence_refs": ["ref1", "ref2"]
        }
    ]

    result = gate_findings(mock_findings, tier="tier1")

    assert len(result) == 1
    assert "narrative" not in result[0]
    assert "deliverable_template_id" not in result[0]
    assert "evidence_refs" not in result[0]
    assert result[0]["id"] == "f1"
    assert result[0]["category"] == "compute"
    assert result[0]["title"] == "Optimize VM usage"
    assert result[0]["estimated_saving_low"] == 100
    assert result[0]["estimated_saving_high"] == 200
    assert result[0]["effort_class"] == "low"
    assert result[0]["risk_class"] == "low"
