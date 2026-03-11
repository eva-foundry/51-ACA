"""Unit tests for R-10: Savings plan coverage detection"""
# EVA-STORY: ACA-03-020
from services.analysis.app.rules.rule_10_savings_plan_coverage import rule_10_savings_plan_coverage


def test_savings_plan_above_threshold():
    """Should flag when annualised compute spend > $20,000"""
    data = {
        "cost_rows": [
            {"Cost": 100.0}
            for _ in range(30)
        ]
    }
    result = rule_10_savings_plan_coverage(data)
    assert result is not None
    assert result["id"] == "rule-10-savings-plan"
    assert result["effort_class"] == "involved"
    assert result["estimated_saving_low"] > 0
    assert result["estimated_saving_high"] > result["estimated_saving_low"]


def test_savings_plan_below_threshold():
    """Should not flag when annualised compute spend <= $20,000"""
    data = {
        "cost_rows": [
            {"Cost": 1.0}
            for _ in range(10)
        ]
    }
    result = rule_10_savings_plan_coverage(data)
    assert result is None


def test_savings_plan_empty():
    """Should return None when cost_rows is empty"""
    result = rule_10_savings_plan_coverage({"cost_rows": []})
    assert result is None


def test_savings_plan_saving_range():
    """Saving range should be 12-20% of total annualised spend"""
    data = {
        "cost_rows": [
            {"Cost": 100.0}
            for _ in range(30)
        ]
    }
    result = rule_10_savings_plan_coverage(data)
    assert result is not None
    annual = sum(100.0 for _ in range(30)) / 30 * 365
    assert result["estimated_saving_low"] == round(annual * 0.12)
    assert result["estimated_saving_high"] == round(annual * 0.20)

