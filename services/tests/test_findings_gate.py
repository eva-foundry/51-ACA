# EVA-STORY: ACA-03-033
import pytest
from services.api.app.services.findings_gate import gate_findings, TIER1_FIELDS, TIER2_FIELDS

FULL_FINDING = {
    "id": "f1",
    "category": "cost",
    "title": "Save on VM costs",
    "estimated_saving_low": 100,
    "estimated_saving_high": 200,
    "effort_class": "low",
    "risk_class": "low",
    "narrative": "Detailed narrative",
    "heuristic_source": "rule-123",
    "deliverable_template_id": "template-456",
    "evidence_refs": ["ref1", "ref2"]
}


def test_gate_findings_tier1():
    result = gate_findings([FULL_FINDING], "tier1")
    assert len(result) == 1
    assert set(result[0].keys()) == set(TIER1_FIELDS)
    assert "narrative" not in result[0]
    assert "deliverable_template_id" not in result[0]


def test_gate_findings_tier2():
    result = gate_findings([FULL_FINDING], "tier2")
    assert len(result) == 1
    assert "narrative" in result[0]
    assert "deliverable_template_id" not in result[0]


def test_gate_findings_tier3():
    result = gate_findings([FULL_FINDING], "tier3")
    assert len(result) == 1
    assert result[0] == FULL_FINDING
