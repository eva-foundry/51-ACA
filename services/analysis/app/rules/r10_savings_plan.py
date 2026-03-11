"""
# EVA-STORY: ACA-03-020
Rule R-10: Savings Plan Coverage
Source: 14-az-finops saving-opportunities.md #10
Saving: 15-30% of annual compute spend
Effort: involved | Risk: low
"""

RULE_ID = "r10-savings-plan"

_COMPUTE_CATEGORIES = (
    "virtual machines",
    "compute",
    "app service",
    "azure kubernetes",
    "functions",
    "container apps",
    "container instances",
)


def r10_savings_plan(data: dict) -> dict | None:
    """
    Detects when annual compute spend exceeds $20,000, indicating Savings Plan opportunity.
    Covers: VM, AKS, App Service, Functions, Container Apps.
    """
    cost_rows = data.get("cost_rows", [])
    compute_rows = [
        r for r in cost_rows
        if any(cat in str(r.get("MeterCategory", "")).lower() for cat in _COMPUTE_CATEGORIES)
        or any(cat in str(r.get("ServiceName", "")).lower() for cat in _COMPUTE_CATEGORIES)
    ]
    if not compute_rows:
        return None

    annual_compute_cost = round(
        sum(float(r.get("Cost", 0)) for r in compute_rows) / max(len(compute_rows), 1) * 365, 2
    )

    if annual_compute_cost < 20000:
        return None

    return {
        "id": RULE_ID,
        "finding_type": "cost_optimization",
        "category": "commitment-pricing",
        "title": "Annual compute spend qualifies for a 1-year or 3-year Savings Plan",
        "annual_compute_cost": annual_compute_cost,
        "estimated_saving_low": round(annual_compute_cost * 0.15),
        "estimated_saving_high": round(annual_compute_cost * 0.30),
        "effort_class": "involved",
        "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": (
            f"Annual compute spend of ${annual_compute_cost:.0f} exceeds the $20,000 threshold "
            "where a 1-year Compute Savings Plan (typically 17%) or Reserved Instances for "
            "stable workloads produce consistent savings without operational changes. "
            "Requires procurement approval and 12-36 month commitment."
        ),
        "deliverable_template_id": "tmpl-savings-plan",
    }
