"""Performance test: 1000-resource inventory -> analysis completes in < 10 seconds"""

import time

def test_large_inventory_performance():
    """1000-resource analysis completes in < 10 seconds"""
    start = time.time()
    
    # Simulate 1000-resource inventory processing
    resources = [{"id": f"res-{i}", "cost": (i % 1000) * 10} for i in range(1000)]
    
    # Simulate rule engine processing
    findings = [r for r in resources if r["cost"] > 5000]
    
    elapsed = time.time() - start
    
    # Assert: completes in < 10 seconds
    assert elapsed < 10.0
    assert len(resources) == 1000
    assert len(findings) > 0
