# EVA-STORY: ACA-03-019
import pytest
from services.analysis.app.rules.r09_dns_sprawl import evaluate_dns_sprawl


def test_evaluate_dns_sprawl_finding_when_cost_exceeds_threshold():
    inventory = [{"type": "Microsoft.Network/dnsZones", "id": "zone-1"}]
    cost_data = [{"MeterName": "DNS Zone Operations", "MeterCost": "1200"}]
    advisor_data = []
    result = evaluate_dns_sprawl(inventory, cost_data, advisor_data)
    assert result is not None
    assert result["id"] == "rule-09-dns-sprawl"
    assert result["effort_class"] == "easy"
    assert result["estimated_saving_low"] == pytest.approx(1200 * 0.15)


def test_evaluate_dns_sprawl_no_finding_below_threshold():
    inventory = []
    cost_data = [{"MeterName": "DNS Zone Operations", "MeterCost": "800"}]
    advisor_data = []
    result = evaluate_dns_sprawl(inventory, cost_data, advisor_data)
    assert result is None


def test_evaluate_dns_sprawl_no_finding_empty_cost():
    inventory = []
    cost_data = []
    advisor_data = []
    result = evaluate_dns_sprawl(inventory, cost_data, advisor_data)
    assert result is None