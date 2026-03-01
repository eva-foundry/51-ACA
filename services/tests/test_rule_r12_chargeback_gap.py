# EVA-STORY: ACA-03-022
import pytest
from unittest.mock import MagicMock
from app.db.cosmos import query_items
from services.analysis.app.rules.r12_chargeback_gap import identify_chargeback_gap

def test_identify_chargeback_gap():
    subscription_id = "test-subscription"
    threshold = 5000.0

    mock_findings = [
        {
            "id": "finding-1",
            "category": "Compute",
            "title": "Chargeback Gap Detected",
            "estimated_saving_low": 1000.0,
            "estimated_saving_high": 2000.0,
            "effort_class": "low",
            "risk_class": "medium",
        },
        {
            "id": "finding-2",
            "category": "Storage",
            "title": "Chargeback Gap Detected",
            "estimated_saving_low": 3000.0,
            "estimated_saving_high": 4000.0,
            "effort_class": "medium",
            "risk_class": "high",
        },
    ]

    mock_query_items = MagicMock(return_value=mock_findings)

    # Patch the query_items function
    query_items_original = query_items
    try:
        globals()["query_items"] = mock_query_items

        findings = identify_chargeback_gap(subscription_id, threshold)

        assert len(findings) == 2
        assert findings[0]["id"] == "finding-1"
        assert findings[1]["id"] == "finding-2"
        mock_query_items.assert_called_once_with(
            container_name="cost-data",
            query=(
                "SELECT c.id, c.category, c.title, c.estimated_saving_low, "
                "c.estimated_saving_high, c.effort_class, c.risk_class "
                "FROM c WHERE c.subscriptionId = @sub AND c.totalCost > @threshold"
            ),
            parameters=[
                {"name": "@sub", "value": subscription_id},
                {"name": "@threshold", "value": threshold},
            ],
            partition_key=subscription_id,
        )
    finally:
        globals()["query_items"] = query_items_original
