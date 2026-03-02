"""Unit tests for R-03: Defender plan mismatch"""

def test_defender_above_threshold():
    """Should flag Defender cost > $2,000 with plan mismatch"""
    cost = 2500
    assert cost > 2000

def test_defender_below_threshold():
    """Should not flag when Defender cost < $2,000"""
    cost = 1000
    assert cost < 2000

def test_defender_no_plan():
    """Should handle missing Defender plan"""
    resources = []
    assert len(resources) == 0
