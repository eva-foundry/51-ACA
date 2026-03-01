# EVA-STORY: ACA-03-014
import pytest
from unittest.mock import MagicMock
from services.analysis.app.rules.r04_compute_scheduling import evaluate_r04_compute_scheduling

def test_evaluate_r04_compute_scheduling():
    subscription_id = "test-subscription"
    client_tier = 1

    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {"serviceName": "Virtual Machines", "totalAnnualCost": 3000},
        {"serviceName": "App Service", "totalAnnualCost": 2500}
    ]

    # Patch the query_items function
    query_items_original = query_items
    globals()["query_items"] = mock_query_items

    try:
        findings = evaluate_r04_compute_scheduling(subscription_id, client_tier)

        assert len(findings) == 1
        assert findings[0]["id"] == f"r04-{subscription_id}"
        assert findings[0]["category"] == "compute-cost-optimization"
        assert findings[0]["title"] == "Annual schedulable compute cost exceeds $5,000"
        assert findings[0]["estimated_saving_low"] == 500
        assert findings[0]["estimated_saving_high"] == 1500
        assert findings[0]["effort_class"] == "medium"
        assert findings[0]["risk_class"] == "low"
    finally:
        # Restore the original query_items function
        globals()["query_items"] = query_items_original

@pytest.mark.parametrize("client_tier,expected_fields", [
    (1, {"id", "category", "title", "estimated_saving_low", "estimated_saving_high", "effort_class", "risk_class"}),
    (2, {"id", "category", "title", "estimated_saving_low", "estimated_saving_high", "effort_class", "risk_class", "narrative", "heuristic_source"}),
    (3, None)  # Full pass-through
])
def test_tier_gating(client_tier, expected_fields):
    subscription_id = "test-subscription"

    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {"serviceName": "Virtual Machines", "totalAnnualCost": 6000}
    ]

    # Patch the query_items function
    query_items_original = query_items
    globals()["query_items"] = mock_query_items

    try:
        findings = evaluate_r04_compute_scheduling(subscription_id, client_tier)

        if client_tier == 3:
            assert findings[0].keys() == {"id", "subscriptionId", "category", "title", "estimated_saving_low", "estimated_saving_high", "effort_class", "risk_class"}
        else:
            assert set(findings[0].keys()) == expected_fields
    finally:
        # Restore the original query_items function
        globals()["query_items"] = query_items_original