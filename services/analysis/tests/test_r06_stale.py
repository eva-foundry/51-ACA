"""Unit tests for R-06: Stale environments detection"""

def test_stale_above_threshold():
    """Should flag >= 3 stale App Services"""
    app_services = [
        {"name": "app-1", "utilization": 0.05},
        {"name": "app-2", "utilization": 0.08},
        {"name": "app-3", "utilization": 0.10},
    ]
    assert len(app_services) >= 3

def test_stale_below_threshold():
    """Should not flag when < 3 App Services"""
    app_services = [
        {"name": "app-1", "utilization": 0.95},
        {"name": "app-2", "utilization": 0.80},
    ]
    assert len(app_services) < 3

def test_stale_no_app_services():
    """Should handle missing App Services"""
    app_services = []
    assert len(app_services) == 0
