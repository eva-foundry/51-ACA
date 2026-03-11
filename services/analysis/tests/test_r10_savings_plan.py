"""Unit tests for R-10: Savings plan coverage detection"""
# EVA-STORY: ACA-03-020
from services.analysis.app.rules.r10_savings_plan import r10_savings_plan


def test_savings_plan_above_threshold_triggers_finding():
    """Should flag when annual compute cost > $20,000"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Virtual Machines", "Cost": "100.0"},
            {"MeterCategory": "Virtual Machines", "Cost": "100.0"},
        ]
    }
    result = r10_savings_plan(data)
    assert result is not None
    assert result["id"] == "r10-savings-plan"
    assert result["finding_type"] == "cost_optimization"
    assert result["effort_class"] == "involved"
    assert result["estimated_saving_low"] > 0
    assert result["estimated_saving_high"] > result["estimated_saving_low"]
    assert result["annual_compute_cost"] > 20000


def test_savings_plan_below_threshold_returns_none():
    """Should not flag when annual compute cost < $20,000"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Virtual Machines", "Cost": "1.0"},
        ]
    }
    result = r10_savings_plan(data)
    assert result is None


def test_savings_plan_no_compute_rows_returns_none():
    """Should return None when no compute cost rows exist"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Azure DNS", "Cost": "500.0"},
        ]
    }
    result = r10_savings_plan(data)
    assert result is None


def test_savings_plan_empty_data_returns_none():
    """Should handle completely empty data"""
    result = r10_savings_plan({})
    assert result is None


def test_savings_plan_saving_range_15_to_30_percent():
    """Saving estimate should be 15-30% of annual compute cost"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Virtual Machines", "Cost": "100.0"},
        ]
    }
    result = r10_savings_plan(data)
    assert result is not None
    annual = result["annual_compute_cost"]
    assert result["estimated_saving_low"] == round(annual * 0.15)
    assert result["estimated_saving_high"] == round(annual * 0.30)


def test_savings_plan_aks_detected():
    """Should flag Azure Kubernetes Service compute category"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Azure Kubernetes", "Cost": "100.0"},
        ]
    }
    result = r10_savings_plan(data)
    assert result is not None
