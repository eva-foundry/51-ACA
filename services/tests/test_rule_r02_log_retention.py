# EVA-STORY: ACA-03-012
import pytest
from services.analysis.app.rules.r02_log_retention import evaluate_log_retention_costs

def test_evaluate_log_retention_costs_positive():
    """Test case where annual cost exceeds $500."""
    log_analytics_data = [
        {"environment": "non-prod", "daily_cost": 2},
        {"environment": "non-prod", "daily_cost": 1.5},
        {"environment": "prod", "daily_cost": 5},
    ]

    findings = evaluate_log_retention_costs(log_analytics_data)

    assert len(findings) == 1
    assert findings[0]["id"] == "r02-log-retention"
    assert findings[0]["title"] == "Optimize Log Analytics Retention"
    assert findings[0]["category"] == "logging-optimization"
    assert findings[0]["estimated_saving_low"] == 500
    assert findings[0]["estimated_saving_high"] == pytest.approx(1277.5, rel=0.01)
    assert findings[0]["effort_class"] == "medium"
    assert findings[0]["risk_class"] == "low"

def test_evaluate_log_retention_costs_negative():
    """Test case where annual cost does not exceed $500."""
    log_analytics_data = [
        {"environment": "non-prod", "daily_cost": 1},
        {"environment": "non-prod", "daily_cost": 0.5},
        {"environment": "prod", "daily_cost": 5},
    ]

    findings = evaluate_log_retention_costs(log_analytics_data)

    assert len(findings) == 0
