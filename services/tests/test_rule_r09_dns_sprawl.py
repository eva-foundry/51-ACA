# EVA-STORY: ACA-03-019
import pytest
from services.analysis.app.rules.r09_dns_sprawl import analyze_dns_sprawl

def test_analyze_dns_sprawl():
    resources = [
        {
            "id": "dns-zone-1",
            "type": "Microsoft.Network/dnszones",
            "properties": {"numberOfRecordSets": 0},
        },
        {
            "id": "dns-zone-2",
            "type": "Microsoft.Network/dnszones",
            "properties": {"numberOfRecordSets": 10},
        },
        {
            "id": "vm-1",
            "type": "Microsoft.Compute/virtualMachines",
        },
    ]

    expected_findings = [
        {
            "id": "dns-zone-1",
            "title": "Unused DNS Zone",
            "category": "DNS Sprawl",
            "estimated_saving_low": 5,
            "estimated_saving_high": 20,
            "effort_class": "low",
            "risk_class": "low",
        }
    ]

    findings = analyze_dns_sprawl(resources)
    assert findings == expected_findings