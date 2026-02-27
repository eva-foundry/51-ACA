"""
Rule 04: Night and Weekend Compute Scheduling
Source: 14-az-finops saving-opportunities.md #4
Saving: CAD $33,764-$48,088/yr (highest ROI)
Effort: easy | Risk: none
"""

RULE_ID = "rule-04-compute-scheduling"

SCHEDULABLE_CATEGORIES = {
    "azure app service", "azure container apps", "virtual machines",
    "microsoft dev box",
}


def rule_04_compute_scheduling(data: dict) -> dict | None:
    """
    Detects compute spend on schedulable services.
    Estimates saving by applying 33% (nights) and 47% (nights+weekends) factors.
    """
    cost_rows = data.get("cost_rows", [])
    compute_rows = [r for r in cost_rows
                    if str(r.get("MeterCategory", "")).lower() in SCHEDULABLE_CATEGORIES]
    if not compute_rows:
        return None

    annual_cost = sum(float(r.get("Cost", 0)) for r in compute_rows) / len(compute_rows) * 365
    if annual_cost < 5000:
        return None

    return {
        "id": RULE_ID,
        "category": "compute-scheduling",
        "title": "Schedulable compute services likely running 24x7 without auto-shutdown",
        "estimated_saving_low": round(annual_cost * 0.33),
        "estimated_saving_high": round(annual_cost * 0.47),
        "effort_class": "easy",
        "risk_class": "none",
        "heuristic_source": RULE_ID,
        "narrative": (
            "App Service, Container Apps, VMs, and Dev Box account for significant spend. "
            "Automated scheduled shutdown during non-business hours typically eliminates "
            "33-47% of these costs with no impact on developer productivity."
        ),
        "deliverable_template_id": "tmpl-compute-schedule",
    }
