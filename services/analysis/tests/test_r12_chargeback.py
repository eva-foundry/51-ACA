"""Unit test for R-12: chargeback gap detection"""
# EVA-STORY: ACA-03-022
from services.analysis.app.rules.r12_chargeback_gap import r12_chargeback_gap


def test_high_cost_low_tagging_triggers_finding():
    """Should flag when period cost > $5,000 AND tagging compliance < 80%"""
    data = {
        "cost_rows": [
            {"Cost": "6000.0"},
        ],
        "resources": [
            {"name": "vm1", "tags": {}},
            {"name": "vm2", "tags": {}},
            {"name": "vm3", "tags": {"cost-center": "eng"}},
        ],
    }
    result = r12_chargeback_gap(data)
    assert result is not None
    assert result["id"] == "r12-chargeback-gap"
    assert result["finding_type"] == "cost_governance"
    assert result["effort_class"] == "strategic"
    assert result["estimated_saving_low"] == 0
    assert result["estimated_saving_high"] == 0
    assert result["period_cost"] == 6000.0
    assert result["tag_compliance_pct"] < 80


def test_below_cost_threshold_returns_none():
    """Should not flag when period cost < $5,000"""
    data = {
        "cost_rows": [{"Cost": "3000.0"}],
        "resources": [{"name": "vm1", "tags": {}}],
    }
    result = r12_chargeback_gap(data)
    assert result is None


def test_high_tagging_compliance_returns_none():
    """Should not flag when tagging compliance >= 80%"""
    data = {
        "cost_rows": [{"Cost": "7000.0"}],
        "resources": [
            {"name": "vm1", "tags": {"cost-center": "eng"}},
            {"name": "vm2", "tags": {"cost-center": "eng"}},
            {"name": "vm3", "tags": {"cost-center": "ops"}},
            {"name": "vm4", "tags": {"cost-center": "ops"}},
            {"name": "vm5", "tags": {}},
        ],
    }
    result = r12_chargeback_gap(data)
    assert result is None


def test_empty_cost_rows_returns_none():
    """Should return None when no cost rows present"""
    result = r12_chargeback_gap({"cost_rows": []})
    assert result is None


def test_empty_data_returns_none():
    """Should handle completely empty data dict"""
    result = r12_chargeback_gap({})
    assert result is None


def test_tag_compliance_via_pct_field():
    """Should use tag_compliance_pct field when no resources list provided"""
    data = {
        "cost_rows": [{"Cost": "6000.0"}],
        "tag_compliance_pct": 0.50,
    }
    result = r12_chargeback_gap(data)
    assert result is not None
    assert result["tag_compliance_pct"] == 50.0
