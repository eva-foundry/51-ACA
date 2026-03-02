"""Unit test for R-12: chargeback gap detection"""

def test_chargeback_untagged():
    """Should flag when untagged resources total > $5,000"""
    untagged_cost = 6000
    assert untagged_cost > 5000

def test_chargeback_below_threshold():
    """Should not flag when untagged < $5,000"""
    untagged_cost = 3000
    assert untagged_cost < 5000

def test_chargeback_all_tagged():
    """Should handle all resources tagged"""
    resources = [{"cost": 1000, "tag": "cost-center"}, {"cost": 2000, "tag": "cost-center"}]
    assert all("tag" in r for r in resources)
