# EVA-STORY: ACA-03-015
from services.analysis.app.rules import r05_anomaly_detection as r05


def test_detect_anomalies_outlier(monkeypatch):
    sample = [
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 1000},
        {"category": "Storage", "cost": 50},
        {"category": "Storage", "cost": 52},
        {"category": "Storage", "cost": 54},
    ]
    persisted = []

    monkeypatch.setattr(
        r05,
        "query_items",
        lambda container_name, query, parameters, partition_key: sample,
        raising=False,
    )
    monkeypatch.setattr(
        r05,
        "persist_finding",
        lambda cosmos_client, finding_dict: persisted.append(finding_dict),
        raising=False,
    )

    findings = r05.detect_anomalies("sub-123", "scan-456")

    assert len(findings) == 1
    assert findings[0]["category"] == "Compute"
    assert findings[0]["title"] == "Anomaly detected in Compute costs"
    assert len(persisted) == 1


def test_detect_anomalies_no_outlier(monkeypatch):
    sample = [
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 105},
        {"category": "Compute", "cost": 110},
        {"category": "Storage", "cost": 50},
        {"category": "Storage", "cost": 55},
        {"category": "Storage", "cost": 60},
    ]

    monkeypatch.setattr(
        r05,
        "query_items",
        lambda container_name, query, parameters, partition_key: sample,
        raising=False,
    )
    monkeypatch.setattr(r05, "persist_finding", lambda *args, **kwargs: None, raising=False)

    findings = r05.detect_anomalies("sub-123", "scan-456")

    assert findings == []
