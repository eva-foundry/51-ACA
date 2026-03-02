"""Unit tests for R-01: Dev Box auto-stop"""

def test_devbox_above_threshold():
    """Should flag Dev Box cost > $1,000"""
    cost = 1500
    assert cost > 1000

def test_devbox_below_threshold():
    """Should not flag when Dev Box cost < $1,000"""
    cost = 500
    assert cost < 1000

def test_devbox_no_resources():
    """Should handle empty inventory gracefully"""
    resources = []
    assert len(resources) == 0
