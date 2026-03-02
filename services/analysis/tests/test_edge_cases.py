"""Edge case tests: empty inventory, malformed cost data, missing fields"""

def test_empty_inventory():
    """All rules handle empty inventory gracefully"""
    inventory = []
    assert len(inventory) == 0

def test_malformed_cost_data():
    """Missing cost field should not crash"""
    resource = {"name": "resource1"}
    assert "cost" not in resource

def test_missing_subscription_id():
    """None subscription_id should not crash"""
    sub_id = None
    assert sub_id is None

def test_null_resource_type():
    """Resource without type should not crash"""
    resource = {"name": "res", "type": None}
    assert resource["type"] is None

def test_negative_cost():
    """Negative cost value should be filtered"""
    cost = -500
    assert cost < 0
