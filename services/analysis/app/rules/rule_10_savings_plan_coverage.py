"""Rule 10: Savings Plan Coverage Opportunity -- Source: 14-az-finops #10"""
RULE_ID = "rule-10-savings-plan"

def rule_10_savings_plan_coverage(data: dict) -> dict | None:
    cost_rows = data.get("cost_rows", [])
    if not cost_rows:
        return None
    total_annual = sum(float(r.get("Cost", 0)) for r in cost_rows) / len(cost_rows) * 365
    if total_annual < 20000:
        return None
    return {
        "id": RULE_ID, "category": "commitment-pricing",
        "title": "Annual compute spend may qualify for a Savings Plan or Reserved Instances",
        "estimated_saving_low": round(total_annual * 0.12), "estimated_saving_high": round(total_annual * 0.20),
        "effort_class": "involved", "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": "Subscription shows a spend level where 1-year Compute Savings Plans (typically 17%) or Reserved Instances for stable services can produce consistent annual savings without operational changes.",
        "deliverable_template_id": "tmpl-savings-plan",
    }
