# EVA-STORY: ACA-03-017
from services.analysis.app.rules import r07_search_sku_oversize as r07


def test_analyze_search_costs_exceeds_threshold(monkeypatch):
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
    persisted = []

    monkeypatch.setattr(
        r07,
        "query_items",
        lambda container_name, query, parameters, partition_key: mock_cost_data,
        raising=False,
    )
    monkeypatch.setattr(
        r07,
        "persist_finding",
        lambda cosmos_client, finding: persisted.append(finding),
        raising=False,
    )

    r07.analyze_search_costs(scan_id, subscription_id)

    assert len(persisted) == 1
    finding = persisted[0]
    assert finding["category"] == "search-optimization"
    assert finding["title"] == "High Azure AI Search Costs"
    assert finding["estimated_saving_low"] == 500
    assert finding["estimated_saving_high"] == 1500


def test_analyze_search_costs_below_threshold(monkeypatch):
    scan_id = "test-scan-id"
    subscription_id = "test-sub-id"

    mock_cost_data = [
        {
            "rows": [
                {"serviceName": "Azure AI Search", "meterCategory": "Search", "cost": 200},
                {"serviceName": "Azure AI Search", "meterCategory": "Search", "cost": 200},
            ]
        }
    ]
    persisted = []

    monkeypatch.setattr(
        r07,
        "query_items",
        lambda container_name, query, parameters, partition_key: mock_cost_data,
        raising=False,
    )
    monkeypatch.setattr(
        r07,
        "persist_finding",
        lambda cosmos_client, finding: persisted.append(finding),
        raising=False,
    )

    r07.analyze_search_costs(scan_id, subscription_id)
    assert persisted == []
