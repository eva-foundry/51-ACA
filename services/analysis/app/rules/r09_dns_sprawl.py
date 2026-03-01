# EVA-STORY: ACA-03-019
from typing import List, Dict

def analyze_dns_sprawl(resources: List[Dict]) -> List[Dict]:
    """
    Analyze DNS sprawl by identifying redundant or unused DNS zones.

    Args:
        resources (List[Dict]): List of DNS zone resources.

    Returns:
        List[Dict]: Findings indicating optimization opportunities.
    """
    findings = []

    for resource in resources:
        if resource.get("type") == "Microsoft.Network/dnszones":
            record_sets = resource.get("properties", {}).get("numberOfRecordSets", 0)
            if record_sets == 0:
                findings.append({
                    "id": resource["id"],
                    "title": "Unused DNS Zone",
                    "category": "DNS Sprawl",
                    "estimated_saving_low": 5,
                    "estimated_saving_high": 20,
                    "effort_class": "low",
                    "risk_class": "low",
                })

    return findings
