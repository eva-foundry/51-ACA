"""Unit tests for R-03: Defender plan mismatch"""
import pytest

def test_defender_above_threshold():
    """Should flag Defender cost > $2,000 with plan mismatch"""
    from rule_03_defender_mismatch import evaluate_defender
    
    fixture = {
        "resources": [{"type": "Defender", "plan": "P1", "resources": "Basic"}],
        "cost_data": [{"service": "Defender", "cost": 2500}],
    }
    result = evaluate_defender(fixture["resources"], fixture["cost_data"], [])
    assert result is not None
    assert result["id"] == "rule-03-defender-mismatch"

def test_defender_below_threshold():
    """Should not flag when Defender cost < $2,000"""
    from rule_03_defender_mismatch import evaluate_defender
    
    fixture = {
        "resources": [{"type": "Defender", "plan": "P1"}],
        "cost_data": [{"service": "Defender", "cost": 1000}],
    }
    result = evaluate_defender(fixture["resources"], fixture["cost_data"], [])
    assert result is None

def test_defender_no_plan():
    """Should handle missing Defender plan"""
    from rule_03_defender_mismatch import evaluate_defender
    
    result = evaluate_defender([], [], [])
    assert result is None
