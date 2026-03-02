"""R-10: Savings plan coverage detection"""

def evaluate_savings_plan(inventory, cost_data, advisor_data):
    """Returns finding if annual compute cost > $20,000 without saving plans"""
    compute_cost = sum(
        float(row.get("MeterCost", 0))
        for row in cost_data
        if any(x in row.get("MeterCategory", "") for x in ["Compute", "Virtual"]) 
    )
    
    if compute_cost > 20000:
        return {
            "id": "rule-10-savings-plan",
            "category": "compute",
            "title": "Compute savings plan recommendation",
            "estimated_saving_low": compute_cost * 0.10,
            "estimated_saving_high": compute_cost * 0.30,
            "effort_class": "trivial",
            "risk_class": "none",
            "heuristic_source": "rule-10",
            "narrative": f"Annual compute cost of ${compute_cost:.0f} eligible for savings plans",
        }
    return None
