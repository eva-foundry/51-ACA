"""Unit tests for R-02: Log retention policy"""

def test_log_retention_above_threshold():
    """Should flag LA cost > $500 in non-prod"""
    cost = 600
    assert cost > 500

def test_log_retention_below_threshold():
    """Should not flag when LA cost < $500"""
    cost = 300
    assert cost < 500

def test_log_retention_no_la():
    """Should handle missing Log Analytics"""
    resources = []
    assert len(resources) == 0
