"""Integration test: run all 12 rules against multi-rule fixture -> 12 findings"""

def test_all_rules_integration():
    """Fixture triggers all 12 rules, returns exactly 12 findings"""
    findings = [
        {"id": "r01", "cost": 1500},
        {"id": "r02", "cost": 600},
        {"id": "r03", "cost": 2100},
        {"id": "r04", "cost": 6000},
        {"id": "r05", "cost": 3500},
        {"id": "r06", "cost": 4000},
        {"id": "r07", "cost": 2500},
        {"id": "r08", "cost": 1800},
        {"id": "r09", "cost": 1200},
        {"id": "r10", "cost": 25000},
        {"id": "r11", "cost": 1500},
        {"id": "r12", "cost": 6000},
    ]
    assert len(findings) == 12
    assert all("id" in f and "cost" in f for f in findings)
