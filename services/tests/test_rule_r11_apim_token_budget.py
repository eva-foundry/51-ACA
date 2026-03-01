# EVA-STORY: ACA-03-021
import pytest
from unittest.mock import MagicMock
from services.analysis.app.rules.r11_apim_token_budget import r11_apim_token_budget

def test_r11_apim_token_budget():
    subscription_id = "test-subscription-id"

    # Mock the query_items function
    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {
            "id": "1",
            "title": "High Token Budget",
            "category": "API Management",
            "estimated_saving_low": 5000,
            "estimated_saving_high": 10000,
            "effort_class": "medium",
            "subscriptionId": subscription_id
        },
        {
            "id": "2",
            "title": "Excessive Token Budget",
            "category": "API Management",
            "estimated_saving_low": 8000,
            "estimated_saving_high": 15000,
            "effort_class": "high",
            "subscriptionId": subscription_id
        }
    ]

    # Patch the query_items function
    from services.api.app.db.cosmos import query_items
    query_items = mock_query_items

    findings = r11_apim_token_budget(subscription_id)

    assert len(findings) == 2
    assert findings[0]["title"] == "High Token Budget"
    assert findings[1]["title"] == "Excessive Token Budget"
    assert findings[0]["subscriptionId"] == subscription_id
    assert findings[1]["subscriptionId"] == subscription_id
