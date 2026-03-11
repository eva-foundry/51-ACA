"""
# EVA-STORY: ACA-03-022
Rule R-12: Chargeback Gap Detection
Source: 14-az-finops tagging.md chargeback patterns
Saving: 0 (strategic benefit, not dollar savings)
Effort: strategic
"""

RULE_ID = "r12-chargeback-gap"

_CHARGEBACK_TAGS = ("cost-center", "costcenter", "project", "owner")
_TAGGING_THRESHOLD = 0.80


def r12_chargeback_gap(data: dict) -> dict | None:
    """
    Detects when period cost > $5,000 AND resource tagging compliance < 80%.
    Suggests chargeback tagging strategy (cost-center, project, owner).
    """
    cost_rows = data.get("cost_rows", [])
    if not cost_rows:
        return None

    period_cost = round(sum(float(r.get("Cost", 0)) for r in cost_rows), 2)
    if period_cost < 5000:
        return None

    resources = data.get("resources", [])
    if resources:
        tagged = sum(
            1 for r in resources
            if any(tag in (k.lower() for k in r.get("tags", {}).keys()) for tag in _CHARGEBACK_TAGS)
        )
        tag_compliance_pct = tagged / len(resources)
    else:
        tag_compliance_pct = data.get("tag_compliance_pct", 0.0)

    if tag_compliance_pct >= _TAGGING_THRESHOLD:
        return None

    untagged_pct = round((1 - tag_compliance_pct) * 100, 1)

    return {
        "id": RULE_ID,
        "finding_type": "cost_governance",
        "category": "cost-governance",
        "title": "Subscription lacks cost-allocation tagging; chargeback visibility not possible",
        "period_cost": period_cost,
        "tag_compliance_pct": round(tag_compliance_pct * 100, 1),
        "estimated_saving_low": 0,
        "estimated_saving_high": 0,
        "effort_class": "strategic",
        "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": (
            f"Period spend of ${period_cost:.0f} with only {100 - untagged_pct:.0f}% of resources "
            "carrying cost-center, project, or owner tags makes per-team chargeback impossible. "
            "Implementing a tagging policy and chargeback reporting typically drives 15-25% "
            "behavioural cost reduction within 2-3 billing cycles."
        ),
        "deliverable_template_id": "tmpl-chargeback-policy",
    }
