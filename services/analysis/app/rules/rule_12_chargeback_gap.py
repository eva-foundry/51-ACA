"""Rule 12: Shared Cost Chargeback Gap -- Source: 14-az-finops #12"""
# EVA-STORY: ACA-03-031
RULE_ID = "rule-12-chargeback-gap"
REQUIRED_TAGS = {"cost-center", "project", "owner"}
TAGGING_THRESHOLD = 0.80

def rule_12_chargeback_gap(data: dict) -> dict | None:
    cost_rows = data.get("cost_rows", [])
    if not cost_rows:
        return None
    total = sum(float(r.get("Cost", 0)) for r in cost_rows)
    if total < 5000:
        return None
    resources = data.get("resources", [])
    if resources:
        tagged = sum(
            1 for r in resources
            if any(t in str(r.get("tags", {})).lower() for t in REQUIRED_TAGS)
        )
        compliance = tagged / len(resources)
        if compliance >= TAGGING_THRESHOLD:
            return None
    return {
        "id": RULE_ID,
        "category": "cost-governance",
        "title": "Subscription lacks cost allocation tagging; chargeback visibility not possible",
        "estimated_saving_low": 0,
        "estimated_saving_high": 0,
        "effort_class": "strategic",
        "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": "Resources lack consistent cost-allocation tags, preventing per-team chargeback reporting. Implementing chargeback visibility typically drives 15-25% behavioural cost reduction within 2-3 billing cycles.",
        "deliverable_template_id": "tmpl-chargeback-policy",
    }
