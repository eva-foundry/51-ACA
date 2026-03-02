"""Unit tests for R-01: Dev Box auto-stop"""
import pytest

def test_devbox_above_threshold():
    """Should flag Dev Box cost > $1,000"""
    from rule_01_devbox_autostop import evaluate_devbox
    
    fixture = {
        "resources": [{"type": "DevBox", "cost": 1500}],
        "cost_data": [],
    }
    result = evaluate_devbox(fixture["resources"], fixture["cost_data"], [])
    assert result is not None
    assert result["id"] == "rule-01-devbox-autostop"
    assert result["estimated_saving_low"] > 0

def test_devbox_below_threshold():
    """Should not flag when Dev Box cost < $1,000"""
    from rule_01_devbox_autostop import evaluate_devbox
    
    fixture = {
        "resources": [{"type": "DevBox", "cost": 500}],
        "cost_data": [],
    }
    result = evaluate_devbox(fixture["resources"], fixture["cost_data"], [])
    assert result is None

def test_devbox_no_resources():
    """Should handle empty inventory gracefully"""
    from rule_01_devbox_autostop import evaluate_devbox
    
    result = evaluate_devbox([], [], [])
    assert result is None
