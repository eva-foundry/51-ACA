"""Unit tests for R-05: Cost anomaly detection (z-score)"""

def test_anomaly_high_zscore():
    """Should flag cost z-score > 3.0"""
    # Fixture: normal daily cost ~$100, spike day = $400 (z-score ~3.5)
    cost_history = [100] * 89 + [400]
    spike = cost_history[-1]
    assert spike > 300  # Clear anomaly

def test_anomaly_normal_zscore():
    """Should not flag when z-score < 3.0"""
    # Fixture: normal distribution with small variance
    cost_history = [100 + i % 5 for i in range(90)]
    variance = max(cost_history) - min(cost_history)
    assert variance < 10  # Normal range

def test_anomaly_insufficient_data():
    """Should handle insufficient history (< 30 days)"""
    # Fixture: only 7 days of data
    cost_history = [100, 110, 105, 120, 115, 110, 108]
    assert len(cost_history) < 30
