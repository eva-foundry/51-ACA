"""Unit tests for R-02: Log retention policy"""
import pytest

def test_log_retention_above_threshold():
    """Should flag LA cost > $500 in non-prod"""
    from rule_02_log_retention import evaluate_log_retention
    
    fixture = {
        "resources": [{"type": "LogAnalytics", "environment": "staging"}],
        "cost_data": [{"service": "Log Analytics", "cost": 600}],
    }
    result = evaluate_log_retention(fixture["resources"], fixture["cost_data"], [])
    assert result is not None
    assert result["id"] == "rule-02-log-retention"

def test_log_retention_below_threshold():
    """Should not flag when LA cost < $500"""
    from rule_02_log_retention import evaluate_log_retention
    
    fixture = {
        "resources": [{"type": "LogAnalytics", "environment": "staging"}],
        "cost_data": [{"service": "Log Analytics", "cost": 300}],
    }
    result = evaluate_log_retention(fixture["resources"], fixture["cost_data"], [])
    assert result is None

def test_log_retention_no_la():
    """Should handle missing Log Analytics"""
    from rule_02_log_retention import evaluate_log_retention
    
    result = evaluate_log_retention([], [], [])
    assert result is None
