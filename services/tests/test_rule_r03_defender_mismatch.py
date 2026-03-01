# EVA-STORY: ACA-03-013
import pytest
from unittest.mock import MagicMock
from services.analysis.app.rules.r03_defender_mismatch import evaluate_defender_costs

def test_defender_costs_above_threshold():
    subscription_id = "sub-123"
    scan_id = "scan-456"

    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {"serviceName": "Microsoft Defender for Cloud", "totalAnnualCost": 2500}
    ]

    # Patch query_items
    query_items_original = query_items
    globals()["query_items"] = mock_query_items

    findings = evaluate_defender_costs(subscription_id, scan_id)

    # Restore original function
    globals()["query_items"] = query_items_original

    assert len(findings) == 1
    assert findings[0]["category"] == "security-cost-optimization"
    assert findings[0]["title"] == "High Microsoft Defender for Cloud Costs"
    assert findings[0]["estimated_saving_high"] == 2500

def test_defender_costs_below_threshold():
    subscription_id = "sub-123"
    scan_id = "scan-456"

    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {"serviceName": "Microsoft Defender for Cloud", "totalAnnualCost": 1500}
    ]

    # Patch query_items
    query_items_original = query_items
    globals()["query_items"] = mock_query_items

    findings = evaluate_defender_costs(subscription_id, scan_id)

    # Restore original function
    globals()["query_items"] = query_items_original

    assert len(findings) == 0
