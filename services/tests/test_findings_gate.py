# EVA-STORY: ACA-03-033
import pytest
from services.analysis.app.findings import gate_findings, TIER1_FIELDS, TIER2_FIELDS

def test_gate_findings_tier1():
    full_finding = {
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
    tier1_result = gate_findings(full_finding, "tier1")
    assert set(tier1_result.keys()) == set(TIER1_FIELDS)
    assert "narrative" not in tier1_result
    assert "deliverable_template_id" not in tier1_result

def test_gate_findings_tier2():
    full_finding = {
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
    tier2_result = gate_findings(full_finding, "tier2")
    assert "narrative" in tier2_result
    assert "deliverable_template_id" not in tier2_result

def test_gate_findings_tier3():
    full_finding = {
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
    tier3_result = gate_findings(full_finding, "tier3")
    assert tier3_result == full_finding
