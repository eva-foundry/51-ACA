# EVA-STORY: ACA-03-016
from services.analysis.app.rules import r06_stale_environments as r06


def test_r06_stale_environments_positive(monkeypatch):
    def _mock_query_items(container_name, query, parameters, partition_key):
        if partition_key == "sub-123" and parameters[0]["value"] == "scan-456":
            return [{
                "resources": [
                    {"resourceType": "Microsoft.Web/sites", "name": "site1"},
                    {"resourceType": "Microsoft.Web/sites", "name": "site2"},
                    {"resourceType": "Microsoft.Web/sites", "name": "site3"},
                    {"resourceType": "Microsoft.Web/sites", "name": "site4"},
                ]
            }]
        return []

    monkeypatch.setattr(r06, "query_items", _mock_query_items, raising=False)
    findings = r06.evaluate_r06_stale_environments("sub-123", "scan-456")
    assert len(findings) == 1
    assert findings[0]["id"] == "r06-scan-456"
    assert findings[0]["title"] == "Consolidate App Service Sites"
    assert findings[0]["category"] == "resource-consolidation"
    assert findings[0]["estimated_saving_low"] == 100
    assert findings[0]["estimated_saving_high"] == 500
    assert findings[0]["effort_class"] == "medium"
    assert findings[0]["risk_class"] == "low"


def test_r06_stale_environments_negative(monkeypatch):
    def _mock_query_items(container_name, query, parameters, partition_key):
        if partition_key == "sub-123" and parameters[0]["value"] == "scan-789":
            return [{
                "resources": [
                    {"resourceType": "Microsoft.Web/sites", "name": "site1"},
                    {"resourceType": "Microsoft.Web/sites", "name": "site2"},
                ]
            }]
        return []

    monkeypatch.setattr(r06, "query_items", _mock_query_items, raising=False)
    findings = r06.evaluate_r06_stale_environments("sub-123", "scan-789")
    assert findings == []