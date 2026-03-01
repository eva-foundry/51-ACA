# EVA-STORY: ACA-03-020
import pytest
from services.analysis.app.rules.r10_savings_plan_coverage import analyze_savings_plan_coverage

def test_analyze_savings_plan_coverage():
    # Test with high compute cost but no savings plan
    compute_cost_data = [
        {"type": "compute", "cost": 25000},
        {"type": "storage", "cost": 1000},
    ]
    
    findings = analyze_savings_plan_coverage(compute_cost_data, has_plan=False)
    assert len(findings) == 1
    assert findings[0]["id"] == "savings-plan-gap"
    assert findings[0]["category"] == "cost-optimization"
    
    # Test with plan present
    findings = analyze_savings_plan_coverage(compute_cost_data, has_plan=True)
    assert len(findings) == 0
    
    # Test with low compute cost
    low_compute_data = [
        {"type": "compute", "cost": 5000},
        {"type": "storage", "cost": 1000},
    ]
    findings = analyze_savings_plan_coverage(low_compute_data, has_plan=False)
    assert len(findings) == 0