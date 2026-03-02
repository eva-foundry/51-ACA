"""Unit tests for R-04: Compute scheduling (auto-stop)"""
import pytest

def test_scheduling_above_threshold():
    """Should flag schedulable compute > $5,000"""
    from rule_04_compute_scheduling import evaluate_scheduling
    
    fixture = {
        "resources": [
            {"type": "VirtualMachine", "environment": "dev", "cost": 3000},
            {"type": "VirtualMachine", "environment": "test", "cost": 2500},
        ],
        "cost_data": [],
    }
    result = evaluate_scheduling(fixture["resources"], [], [])
    assert result is not None
    assert result["id"] == "rule-04-compute-scheduling"

def test_scheduling_below_threshold():
    """Should not flag when compute < $5,000"""
    from rule_04_compute_scheduling import evaluate_scheduling
    
    fixture = {
        "resources": [{"type": "VirtualMachine", "cost": 2000}],
    }
    result = evaluate_scheduling(fixture["resources"], [], [])
    assert result is None

def test_scheduling_no_compute():
    """Should handle missing compute resources"""
    from rule_04_compute_scheduling import evaluate_scheduling
    
    result = evaluate_scheduling([], [], [])
    assert result is None
