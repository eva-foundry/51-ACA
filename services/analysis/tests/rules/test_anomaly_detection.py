"""Unit tests for R-05: Cost anomaly detection (z-score)"""
import pytest

def test_anomaly_high_zscore():
    """Should flag cost z-score > 3.0"""
    from rule_05_anomaly_detection import evaluate_anomaly
    
    # Fixture: normal daily cost ~$100, spike day = $400 (z-score ~3.5)
    fixture = {
        "cost_history": [100] * 89 + [400],  # 90 days, last day spike
        "category": "Compute",
    }
    result = evaluate_anomaly(fixture["cost_history"], fixture["category"], [])
    assert result is not None
    assert result["id"] == "rule-05-anomaly-detection"

def test_anomaly_normal_zscore():
    """Should not flag when z-score < 3.0"""
    from rule_05_anomaly_detection import evaluate_anomaly
    
    # Fixture: normal distribution with small variance
    fixture = {
        "cost_history": [100 + i % 5 for i in range(90)],  # small variance
        "category": "Network",
    }
    result = evaluate_anomaly(fixture["cost_history"], fixture["category"], [])
    assert result is None

def test_anomaly_insufficient_data():
    """Should handle insufficient history (< 30 days)"""
    from rule_05_anomaly_detection import evaluate_anomaly
    
    # Fixture: only 7 days of data
    fixture = {
        "cost_history": [100, 110, 105, 120, 115, 110, 108],
        "category": "Storage",
    }
    result = evaluate_anomaly(fixture["cost_history"], fixture["category"], [])
    assert result is None
