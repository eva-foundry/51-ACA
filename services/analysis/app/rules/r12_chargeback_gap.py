# EVA-STORY: ACA-03-022
from typing import Optional, Dict

def identify_chargeback_gap(resource_cost: float = 0, allocation_tags: Optional[Dict] = None) -> list[dict]:
    """
    Identify cost allocation gaps for chargeback.

    Args:
        resource_cost (float): Total resource cost.
        allocation_tags (Optional[Dict]): Allocation tags dictionary.

    Returns:
        list[dict]: Findings if chargeback gap detected.
    """
    if allocation_tags is None:
        allocation_tags = {}
    
    findings = []
    
    # Detect chargeback gap: cost > $5000 without proper allocation tags
    if resource_cost > 5000 and not allocation_tags.get("cost_center"):
        findings.append({
            "id": "chargeback-allocation-gap",
            "title": "Missing Cost Center Allocation Tags",
            "category": "cost-allocation",
            "estimated_saving_low": resource_cost * 0.05,
            "estimated_saving_high": resource_cost * 0.1,
            "effort_class": "easy",
            "risk_class": "low",
            "heuristic_source": "r12_chargeback_gap"
        })
    
    return findings
