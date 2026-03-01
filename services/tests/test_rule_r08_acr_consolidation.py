# EVA-STORY: ACA-03-018
import pytest
from unittest.mock import MagicMock
from app.db.cosmos import query_items
from services.analysis.app.rules.r08_acr_consolidation import evaluate_acr_consolidation

def test_evaluate_acr_consolidation_positive():
    subscription_id = "test-subscription"
    scan_id = "test-scan"

    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {
            "resources": [
                {"resourceType": "Microsoft.ContainerRegistry/registries"},
                {"resourceType": "Microsoft.ContainerRegistry/registries"},
                {"resourceType": "Microsoft.ContainerRegistry/registries"},
            ]
        }
    ]

    query_items.side_effect = mock_query_items

    findings = evaluate_acr_consolidation(subscription_id, scan_id)

    assert len(findings) == 1
    assert findings[0]["category"] == "container-consolidation"
    assert findings[0]["title"] == "Consider consolidating Azure Container Registries"
    assert findings[0]["estimated_saving_low"] == 100
    assert findings[0]["estimated_saving_high"] == 500
    assert findings[0]["effort_class"] == "medium"
    assert findings[0]["risk_class"] == "low"

def test_evaluate_acr_consolidation_negative():
    subscription_id = "test-subscription"
    scan_id = "test-scan"

    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {
            "resources": [
                {"resourceType": "Microsoft.ContainerRegistry/registries"},
                {"resourceType": "Microsoft.ContainerRegistry/registries"},
            ]
        }
    ]

    query_items.side_effect = mock_query_items

    findings = evaluate_acr_consolidation(subscription_id, scan_id)

    assert len(findings) == 0