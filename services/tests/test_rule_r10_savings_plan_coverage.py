# EVA-STORY: ACA-03-020
import pytest
from unittest.mock import MagicMock
from app.analysis.app.rules.r10_savings_plan_coverage import analyze_savings_plan_coverage

def test_analyze_savings_plan_coverage():
    subscription_id = "sub-123"
    tier = 2

    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {
            "id": "plan-001",
            "subscriptionId": subscription_id,
            "type": "savings_plan",
            "coverage": 75,
            "estimatedSavingLow": 100,
            "estimatedSavingHigh": 200,
            "narrative": "Coverage is below recommended levels."
        },
        {
            "id": "plan-002",
            "subscriptionId": subscription_id,
            "type": "savings_plan",
            "coverage": 85,
            "estimatedSavingLow": 50,
            "estimatedSavingHigh": 100,
            "narrative": "Coverage is adequate."
        }
    ]

    # Patch the query_items function
    from app.db.cosmos import query_items
    query_items = mock_query_items

    findings = analyze_savings_plan_coverage(subscription_id, tier)

    assert len(findings) == 1
    assert findings[0]["id"] == "plan-001"
    assert findings[0]["title"] == "Low Savings Plan Coverage"
    assert findings[0]["category"] == "Savings Plan"
    assert findings[0]["estimated_saving_low"] == 100
    assert findings[0]["estimated_saving_high"] == 200
    assert findings[0]["effort_class"] == "low"
    assert findings[0]["risk_class"] == "low"
    assert findings[0]["narrative"] == "Coverage is below recommended levels."
    assert "heuristic_source" not in findings[0]  # Tier 2 gating removes heuristic_source

    print("[PASS] test_analyze_savings_plan_coverage")