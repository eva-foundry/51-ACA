# EVA-STORY: ACA-03-022
import pytest
from services.analysis.app.rules.r12_chargeback_gap import identify_chargeback_gap

def test_identify_chargeback_gap():
    # Test with high cost and no tags
    findings = identify_chargeback_gap(resource_cost=10000, allocation_tags={})
    assert len(findings) == 1
    assert findings[0]["id"] == "chargeback-allocation-gap"
    assert findings[0]["category"] == "cost-allocation"
    
    # Test with high cost and tags
    tags = {"cost_center": "engineering"}
    findings = identify_chargeback_gap(resource_cost=10000, allocation_tags=tags)
    assert len(findings) == 0
    
    # Test with low cost and no tags
    findings = identify_chargeback_gap(resource_cost=2000, allocation_tags={})
    assert len(findings) == 0
    
    # Test with none values
    findings = identify_chargeback_gap()
    assert len(findings) == 0
