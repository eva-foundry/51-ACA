"""Unit tests for R-09: DNS zone sprawl detection"""
# EVA-STORY: ACA-03-019
from services.analysis.app.rules.rule_09_dns_sprawl import rule_09_dns_sprawl


def test_dns_above_threshold():
    """Should flag when annual DNS cost > $1,000"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Azure DNS", "Cost": 10.0, "ResourceId": f"zone-{i}"}
            for i in range(10)
        ]
    }
    result = rule_09_dns_sprawl(data)
    assert result is not None
    assert result["id"] == "rule-09-dns-sprawl"
    assert result["finding_type"] == "cost_optimization"
    assert result["effort_class"] == "easy"
    assert result["annual_dns_cost"] > 1000
    assert result["dns_zone_count"] >= 0
    assert result["estimated_saving_low"] > 0


def test_dns_below_threshold():
    """Should not flag when annual DNS cost <= $1,000"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Azure DNS", "Cost": 0.5}
            for _ in range(5)
        ]
    }
    result = rule_09_dns_sprawl(data)
    assert result is None


def test_dns_empty():
    """Should return None when no DNS cost rows"""
    result = rule_09_dns_sprawl({"cost_rows": []})
    assert result is None


def test_dns_no_dns_rows():
    """Should return None when no rows match DNS MeterCategory"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Virtual Machines", "Cost": 50.0}
        ]
    }
    result = rule_09_dns_sprawl(data)
    assert result is None


def test_dns_saving_range():
    """Saving range should be 26-44% of annual DNS cost"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Private DNS Zones", "Cost": 10.0}
            for _ in range(10)
        ]
    }
    result = rule_09_dns_sprawl(data)
    assert result is not None
    annual = result["annual_dns_cost"]
    assert result["estimated_saving_low"] == round(annual * 0.26)
    assert result["estimated_saving_high"] == round(annual * 0.44)

