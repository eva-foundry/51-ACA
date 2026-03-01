# EVA-STORY: ACA-03-015
import pytest
from unittest.mock import MagicMock
from services.analysis.app.rules.r05_anomaly_detection import detect_anomalies

def test_detect_anomalies_outlier():
    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 200},
        {"category": "Compute", "cost": 1000},
        {"category": "Storage", "cost": 50},
        {"category": "Storage", "cost": 55},
        {"category": "Storage", "cost": 60},
    ]

    subscription_id = "sub-123"
    scan_id = "scan-456"

    findings = detect_anomalies(subscription_id, scan_id)

    assert len(findings) == 1
    assert findings[0]["category"] == "Compute"
    assert findings[0]["title"] == "Anomaly detected in Compute costs"

def test_detect_anomalies_no_outlier():
    mock_query_items = MagicMock()
    mock_query_items.return_value = [
        {"category": "Compute", "cost": 100},
        {"category": "Compute", "cost": 110},
        {"category": "Compute", "cost": 120},
        {"category": "Storage", "cost": 50},
        {"category": "Storage", "cost": 55},
        {"category": "Storage", "cost": 60},
    ]

    subscription_id = "sub-123"
    scan_id = "scan-456"

    findings = detect_anomalies(subscription_id, scan_id)

    assert len(findings) == 0
