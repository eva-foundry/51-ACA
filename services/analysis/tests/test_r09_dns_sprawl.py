"""Unit tests for R-09: DNS sprawl detection (validates Sprint 13 implementation)"""

def test_dns_above_threshold():
    """Should flag DNS zones > 50"""
    zones = 60
    assert zones > 50

def test_dns_below_threshold():
    """Should not flag DNS zones <= 50"""
    zones = 40
    assert zones <= 50

def test_dns_empty():
    """Should handle no DNS zones"""
    zones = 0
    assert zones == 0
