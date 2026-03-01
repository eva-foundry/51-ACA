# EVA-STORY: ACA-03-017
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from services.analysis.app.rules.r07_search_sku_oversize import analyze_search_costs

def test_analyze_search_costs_exceeds_threshold():
    scan_id = "test-scan-id"
    subscription_id = "test-sub-id"

    mock_cost_data = [
        {
            "rows": [
                {"serviceName": "Azure AI Search", "meterCategory": "Search", "cost": 1000},
                {"serviceName": "Azure AI Search", "meterCategory": "Search", "cost": 1200},
            ]
        }
    ]

    with patch("app.db.cosmos.query_items", return_value=mock_cost_data):
        with patch("app.findings.persist_finding") as mock_persist:
            analyze_search_costs(scan_id, subscription_id)

            mock_persist.assert_called_once()
            finding = mock_persist.call_args[0][1]

            assert finding["category"] == "search-optimization"
            assert finding["title"] == "High Azure AI Search Costs"
            assert finding["estimated_saving_low"] == 500
            assert finding["estimated_saving_high"] == 1500

def test_analyze_search_costs_below_threshold():
    scan_id = "test-scan-id"
    subscription_id = "test-sub-id"

    mock_cost_data = [
        {
            "rows": [
                {"serviceName": "Azure AI Search", "meterCategory": "Search", "cost": 500},
                {"serviceName": "Azure AI Search", "meterCategory": "Search", "cost": 400},
            ]
        }
    ]

    with patch("app.db.cosmos.query_items", return_value=mock_cost_data):
        with patch("app.findings.persist_finding") as mock_persist:
            analyze_search_costs(scan_id, subscription_id)

            mock_persist.assert_not_called()
