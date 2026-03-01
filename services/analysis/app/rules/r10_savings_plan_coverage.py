# EVA-STORY: ACA-03-020
from typing import Optional, List, Dict

def analyze_savings_plan_coverage(compute_cost_data: Optional[List[Dict]] = None, has_plan: bool = False) -> list[dict]:
    """
    Analyze savings plan coverage for compute resources.

    Args:
        compute_cost_data (Optional[List[Dict]]): Compute cost data resources.
        has_plan (bool): Whether subscription has savings plan.

    Returns:
        list[dict]: Findings.
    """
    if compute_cost_data is None:
        compute_cost_data = []
    
    findings = []
    
    # Calculate total compute cost
    total_compute = sum(item.get("cost", 0) for item in compute_cost_data if item.get("type") == "compute")
    
    # If compute cost exceeds threshold and no savings plan
    if total_compute > 20000 and not has_plan:
        findings.append({
            "id": "savings-plan-gap",
            "title": "Missing Savings Plan for High Compute Spend",
            "category": "cost-optimization",
            "estimated_saving_low": total_compute * 0.15,
            "estimated_saving_high": total_compute * 0.25,
            "effort_class": "easy",
            "risk_class": "low",
            "heuristic_source": "r10_savings_plan_coverage"
        })
    
    return findings
