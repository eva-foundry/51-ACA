"""Unit tests for Sprint 13 rules (R-09 through R-12)"""

import pytest
from unittest.mock import Mock


def test_r09_dns_sprawl_over_threshold():
    """R-09: Should detect DNS sprawl when cost > $1000"""
    from r09_dns_sprawl import evaluate_dns_sprawl
    
    cost_data = [
        {"MeterName": "DNS Zone", "MeterCost": 1500, "tags": {"env": "prod"}},
        {"MeterName": "Other", "MeterCost": 100},
    ]
    result = evaluate_dns_sprawl([], cost_data, [])
    
    assert result is not None
    assert result["id"] == "rule-09-dns-sprawl"
    assert result["category"] == "network"
    assert result["estimated_saving_low"] > 0


def test_r09_dns_sprawl_under_threshold():
    """R-09: Should not flag when DNS cost < $1000"""
    from r09_dns_sprawl import evaluate_dns_sprawl
    
    cost_data = [
        {"MeterName": "DNS Zone", "MeterCost": 500},
    ]
    result = evaluate_dns_sprawl([], cost_data, [])
    assert result is None


def test_r10_savings_plan_over_threshold():
    """R-10: Should recommend savings plan when compute > $20K"""
    from r10_savings_plan import evaluate_savings_plan
    
    cost_data = [
        {"MeterName": "Compute", "MeterCategory": "Virtual Machines", "MeterCost": 25000},
    ]
    result = evaluate_savings_plan([], cost_data, [])
    
    assert result is not None
    assert result["id"] == "rule-10-savings-plan"
    assert result["effort_class"] == "trivial"


def test_r10_savings_plan_under_threshold():
    """R-10: Should not flag when compute < $20K"""
    from r10_savings_plan import evaluate_savings_plan
    
    cost_data = [
        {"MeterName": "Compute", "MeterCategory": "Virtual Machines", "MeterCost": 10000},
    ]
    result = evaluate_savings_plan([], cost_data, [])
    assert result is None


def test_r11_apim_token_both_present():
    """R-11: Should flag when both APIM and OpenAI present"""
    from r11_apim_token import evaluate_apim_token
    
    inventory = [
        {"type": "API Management", "name": "my-apim"},
        {"type": "OpenAI", "name": "my-openai"},
    ]
    result = evaluate_apim_token(inventory, [], [])
    
    assert result is not None
    assert result["id"] == "rule-11-apim-token"
    assert result["category"] == "integration"


def test_r11_apim_token_only_apim():
    """R-11: Should not flag when only APIM present"""
    from r11_apim_token import evaluate_apim_token
    
    inventory = [{"type": "API Management", "name": "my-apim"}]
    result = evaluate_apim_token(inventory, [], [])
    assert result is None


def test_r12_chargeback_high_cost_untagged():
    """R-12: Should flag high cost with untagged resources"""
    from r12_chargeback import evaluate_chargeback
    
    cost_data = [
        {"MeterName": "VM1", "MeterCost": 6000, "tags": {}},
        {"MeterName": "VM2", "MeterCost": 500, "tags": {"env": "prod"}},
    ]
    result = evaluate_chargeback([], cost_data, [])
    
    assert result is not None
    assert result["id"] == "rule-12-chargeback"
    assert result["category"] == "governance"


def test_r12_chargeback_low_cost():
    """R-12: Should not flag when total cost < $5000"""
    from r12_chargeback import evaluate_chargeback
    
    cost_data = [
        {"MeterName": "VM1", "MeterCost": 3000, "tags": {}},
    ]
    result = evaluate_chargeback([], cost_data, [])
    assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
