"""R-12: Chargeback gap (unattributed costs)"""

def evaluate_chargeback(inventory, cost_data, advisor_data):
    """Returns finding if total cost > $5,000 with incomplete resource tagging"""
    total_cost = sum(float(row.get("MeterCost", 0)) for row in cost_data)
    untagged = sum(
        float(row.get("MeterCost", 0))
        for row in cost_data
        if not row.get("tags", {})
    )
    
    if total_cost > 5000:
        chargeback_gap = untagged / total_cost if total_cost > 0 else 0
        return {
            "id": "rule-12-chargeback",
            "category": "governance",
            "title": "Complete resource tagging for chargeback",
            "estimated_saving_low": 1000,
            "estimated_saving_high": 5000,
            "effort_class": "medium",
            "risk_class": "none",
            "heuristic_source": "rule-12",
            "narrative": f"${untagged:.0f} ({chargeback_gap*100:.0f}%) of spend is untagged",
        }
    return None
