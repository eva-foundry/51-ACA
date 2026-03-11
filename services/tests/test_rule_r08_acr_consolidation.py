# EVA-STORY: ACA-03-018
from services.analysis.app.rules import r08_acr_consolidation as r08


def test_evaluate_acr_consolidation_positive(monkeypatch):
    subscription_id = "test-subscription"
    scan_id = "test-scan"

    def _mock_query_items(container_name, query, parameters, partition_key):
        return [
            {
                "resources": [
                    {"resourceType": "Microsoft.ContainerRegistry/registries"},
                    {"resourceType": "Microsoft.ContainerRegistry/registries"},
                    {"resourceType": "Microsoft.ContainerRegistry/registries"},
                ]
            }
        ]

    monkeypatch.setattr(r08, "query_items", _mock_query_items, raising=False)
    findings = r08.evaluate_acr_consolidation(subscription_id, scan_id)

    assert len(findings) == 1
    assert findings[0]["category"] == "container-consolidation"
    assert findings[0]["title"] == "Consider consolidating Azure Container Registries"
    assert findings[0]["estimated_saving_low"] == 100
    assert findings[0]["estimated_saving_high"] == 500
    assert findings[0]["effort_class"] == "medium"
    assert findings[0]["risk_class"] == "low"


def test_evaluate_acr_consolidation_negative(monkeypatch):
    subscription_id = "test-subscription"
    scan_id = "test-scan"

    def _mock_query_items(container_name, query, parameters, partition_key):
        return [
            {
                "resources": [
                    {"resourceType": "Microsoft.ContainerRegistry/registries"},
                    {"resourceType": "Microsoft.ContainerRegistry/registries"},
                ]
            }
        ]

    monkeypatch.setattr(r08, "query_items", _mock_query_items, raising=False)
    findings = r08.evaluate_acr_consolidation(subscription_id, scan_id)

    assert findings == []