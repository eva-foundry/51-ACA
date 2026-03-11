"""Unit tests for R-12: Chargeback gap detection"""
# EVA-STORY: ACA-03-022
from services.analysis.app.rules.rule_12_chargeback_gap import rule_12_chargeback_gap


def test_chargeback_high_cost_low_tagging():
    """Should flag when period cost > $5,000 and tagging compliance < 80%"""
    data = {
        "cost_rows": [{"Cost": 1000.0} for _ in range(6)],
        "resources": [
            {"tags": {"cost-center": "eng"}},
            {"tags": {}},
            {"tags": {}},
            {"tags": {}},
            {"tags": {}},
        ],
    }
    result = rule_12_chargeback_gap(data)
    assert result is not None
    assert result["id"] == "rule-12-chargeback-gap"
    assert result["effort_class"] == "strategic"
    assert result["estimated_saving_low"] == 0
    assert result["estimated_saving_high"] == 0


def test_chargeback_below_cost_threshold():
    """Should not flag when period cost <= $5,000"""
    data = {
        "cost_rows": [{"Cost": 100.0} for _ in range(3)],
        "resources": [{"tags": {}} for _ in range(5)],
    }
    result = rule_12_chargeback_gap(data)
    assert result is None


def test_chargeback_all_tagged():
    """Should not flag when tagging compliance >= 80%"""
    data = {
        "cost_rows": [{"Cost": 1000.0} for _ in range(6)],
        "resources": [
            {"tags": {"cost-center": "eng", "owner": "alice"}},
            {"tags": {"cost-center": "eng", "project": "proj-a"}},
            {"tags": {"cost-center": "ops", "owner": "bob"}},
            {"tags": {"cost-center": "ops", "project": "proj-b"}},
            {"tags": {"owner": "carol", "project": "proj-c"}},
        ],
    }
    result = rule_12_chargeback_gap(data)
    assert result is None


def test_chargeback_empty_cost_rows():
    """Should return None when cost_rows is empty"""
    result = rule_12_chargeback_gap({"cost_rows": []})
    assert result is None


def test_chargeback_no_resources_key():
    """Should flag when cost > $5,000 and no resources provided (skips tagging check)"""
    data = {
        "cost_rows": [{"Cost": 1000.0} for _ in range(6)],
    }
    result = rule_12_chargeback_gap(data)
    assert result is not None
    assert result["id"] == "rule-12-chargeback-gap"

