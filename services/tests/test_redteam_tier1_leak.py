# EVA-STORY: ACA-03-010
from app.services.findings_gate import gate_findings, TIER1_FIELDS


def _sample_findings():
    return [
        {
            "id": "f-1",
            "category": "compute",
            "title": "High VM spend",
            "estimated_saving_low": 100,
            "estimated_saving_high": 250,
            "effort_class": "easy",
            "risk_class": "low",
            "narrative": "Detailed implementation narrative",
            "deliverable_template_id": "tmpl-123",
            "evidence_refs": ["ev-1"],
            "heuristic_source": "rule-04",
        }
    ]


def test_tier1_findings_no_leak():
    """Tier 1 must strip narrative/template/evidence fields."""
    findings = gate_findings(_sample_findings(), "tier1")
    assert len(findings) == 1
    assert set(findings[0].keys()) == set(TIER1_FIELDS)
    assert "narrative" not in findings[0]
    assert "deliverable_template_id" not in findings[0]
    assert "evidence_refs" not in findings[0]


def test_tier1_findings_with_leak_fixture_still_filtered():
    """Even if source findings contain forbidden fields, tier1 output must not."""
    raw = _sample_findings()
    raw[0]["narrative"] = "Leaked narrative"
    raw[0]["deliverable_template_id"] = "Leaked template ID"
    raw[0]["evidence_refs"] = ["leaked-evidence"]

    findings = gate_findings(raw, "tier1")
    assert "narrative" not in findings[0]
    assert "deliverable_template_id" not in findings[0]
    assert "evidence_refs" not in findings[0]
