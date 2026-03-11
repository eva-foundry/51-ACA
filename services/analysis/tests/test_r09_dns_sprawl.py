"""Unit tests for R-09: DNS sprawl detection"""
# EVA-STORY: ACA-03-019
from services.analysis.app.rules.r09_dns_sprawl import r09_dns_sprawl


def test_dns_above_threshold_triggers_finding():
    """Should flag when annual DNS cost > $1,000"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Azure DNS", "Cost": "5.0", "ResourceId": "/dns/zone1"},
            {"MeterCategory": "Azure DNS", "Cost": "5.0", "ResourceId": "/dns/zone2"},
        ]
    }
    result = r09_dns_sprawl(data)
    assert result is not None
    assert result["id"] == "r09-dns-sprawl"
    assert result["finding_type"] == "cost_optimization"
    assert result["effort_class"] == "easy"
    assert result["estimated_saving_low"] > 0
    assert result["dns_zone_count"] >= 1
    assert result["annual_dns_cost"] > 1000


def test_dns_below_threshold_returns_none():
    """Should not flag when annual DNS cost < $1,000"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Azure DNS", "Cost": "0.50", "ResourceId": "/dns/zone1"},
        ]
    }
    result = r09_dns_sprawl(data)
    assert result is None


def test_dns_no_cost_rows_returns_none():
    """Should return None when no cost rows are present"""
    result = r09_dns_sprawl({"cost_rows": []})
    assert result is None


def test_dns_empty_data_returns_none():
    """Should handle completely empty data dict"""
    result = r09_dns_sprawl({})
    assert result is None


def test_dns_non_dns_rows_ignored():
    """Should not flag when only non-DNS cost rows exist"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Virtual Machines", "Cost": "100.0"},
        ]
    }
    result = r09_dns_sprawl(data)
    assert result is None


def test_dns_saving_is_30_percent():
    """Saving estimate should equal 30% of annual DNS cost"""
    data = {
        "cost_rows": [
            {"MeterCategory": "Azure DNS", "Cost": "10.0", "ResourceId": "/dns/zone1"},
        ]
    }
    result = r09_dns_sprawl(data)
    assert result is not None
    assert result["estimated_saving_low"] == result["estimated_saving_high"]
    expected_annual = round(10.0 / 1 * 365, 2)
    assert result["annual_dns_cost"] == expected_annual
    assert result["estimated_saving_low"] == round(expected_annual * 0.30)
