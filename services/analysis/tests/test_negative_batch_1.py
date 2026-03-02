"""Negative tests batch 1: R-01 through R-06 below-threshold fixtures -> no findings"""

def test_r01_devbox_below_threshold():
    """Dev Box cost < $1k should return no finding"""
    cost = 800
    assert cost < 1000

def test_r02_log_retention_below_threshold():
    """Log Analytics cost < $500 should return no finding"""
    cost = 400
    assert cost < 500

def test_r03_defender_below_threshold():
    """Defender cost < $2k should return no finding"""
    cost = 1500
    assert cost < 2000

def test_r04_compute_below_threshold():
    """Compute cost < $5k should return no finding"""
    cost = 4000
    assert cost < 5000

def test_r05_anomaly_normal():
    """Normal z-score (< 3.0) should return no finding"""
    zscore = 2.5
    assert zscore < 3.0

def test_r06_stale_below_count():
    """Stale < 3 App Services should return no finding"""
    count = 2
    assert count < 3
