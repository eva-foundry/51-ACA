"""Rule 12: Shared Cost Chargeback Gap -- Source: 14-az-finops #12"""
RULE_ID = "rule-12-chargeback-gap"

def rule_12_chargeback_gap(data: dict) -> dict | None:
    cost_rows = data.get("cost_rows", [])
    if not cost_rows:
        return None
    total = sum(float(r.get("Cost", 0)) for r in cost_rows)
    if total < 5000:
        return None
    return {
        "id": RULE_ID, "category": "cost-governance",
        "title": "Subscription lacks cost allocation tagging; chargeback visibility not possible",
        "estimated_saving_low": round(total * 0.15), "estimated_saving_high": round(total * 0.25),
        "effort_class": "strategic", "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": "Resources lack consistent cost-allocation tags, preventing per-team chargeback reporting. Implementing chargeback visibility typically drives 15-25% behavioural cost reduction within 2-3 billing cycles.",
        "deliverable_template_id": "tmpl-chargeback-policy",
    }
