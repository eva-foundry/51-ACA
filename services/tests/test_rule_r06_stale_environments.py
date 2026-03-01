# EVA-STORY: ACA-03-016
import pytest
from unittest.mock import MagicMock
from app.db.cosmos import query_items
from services.analysis.app.rules.r06_stale_environments import evaluate_r06_stale_environments

@pytest.fixture
def mock_query_items():
    def _mock_query_items(container_name, query, parameters, partition_key):
        if partition_key == "sub-123" and parameters[0]["value"] == "scan-456":
            return [{
                "resources": [
                    {"resourceType": "Microsoft.Web/sites", "name": "site1"},
                    {"resourceType": "Microsoft.Web/sites", "name": "site2"},
                    {"resourceType": "Microsoft.Web/sites", "name": "site3"},
                    {"resourceType": "Microsoft.Web/sites", "name": "site4"}
                ]
            }]
        return []
    return _mock_query_items

@pytest.fixture
def mock_query_items_negative():
    def _mock_query_items(container_name, query, parameters, partition_key):
        if partition_key == "sub-123" and parameters[0]["value"] == "scan-789":
            return [{
                "resources": [
                    {"resourceType": "Microsoft.Web/sites", "name": "site1"},
                    {"resourceType": "Microsoft.Web/sites", "name": "site2"}
                ]
            }]
        return []
    return _mock_query_items

@pytest.mark.parametrize("mock_query_items", [mock_query_items], indirect=True)
def test_r06_stale_environments_positive(mock_query_items, monkeypatch):
    monkeypatch.setattr("app.db.cosmos.query_items", mock_query_items)
    findings = evaluate_r06_stale_environments("sub-123", "scan-456")
    assert len(findings) == 1
    assert findings[0]["id"] == "r06-scan-456"
    assert findings[0]["title"] == "Consolidate App Service Sites"
    assert findings[0]["category"] == "resource-consolidation"
    assert findings[0]["estimated_saving_low"] == 100
    assert findings[0]["estimated_saving_high"] == 500
    assert findings[0]["effort_class"] == "medium"
    assert findings[0]["risk_class"] == "low"

@pytest.mark.parametrize("mock_query_items", [mock_query_items_negative], indirect=True)
def test_r06_stale_environments_negative(mock_query_items, monkeypatch):
    monkeypatch.setattr("app.db.cosmos.query_items", mock_query_items)
    findings = evaluate_r06_stale_environments("sub-123", "scan-789")
    assert len(findings) == 0