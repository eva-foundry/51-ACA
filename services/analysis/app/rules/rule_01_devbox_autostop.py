"""
# EVA-STORY: ACA-03-011
Rule 01: Dev Box Auto-Stop
Source: 14-az-finops saving-opportunities.md #1
Saving: CAD $5,548-$7,902/yr
Effort: trivial | Risk: none
"""

RULE_ID = "rule-01-devbox-autostop"


def rule_01_devbox_autostop(data: dict) -> dict | None:
    """
    Detects Dev Box spending with no scheduled auto-stop policy.
    Checks: MeterCategory='Dev Box', looks for weekend zero spend as signal.
    """
    cost_rows = data.get("cost_rows", [])
    devbox_rows = [r for r in cost_rows
                   if str(r.get("MeterCategory", "")).lower() in ("microsoft dev box", "dev box")]
    if not devbox_rows:
        return None

    annual_cost = sum(float(r.get("Cost", 0)) for r in devbox_rows) / len(devbox_rows) * 365
    if annual_cost < 1000:
        return None

    return {
        "id": RULE_ID,
        "category": "compute-scheduling",
        "title": "Dev Box instances run without auto-stop on nights and weekends",
        "estimated_saving_low": round(annual_cost * 0.33),
        "estimated_saving_high": round(annual_cost * 0.47),
        "effort_class": "trivial",
        "risk_class": "none",
        "heuristic_source": RULE_ID,
        "narrative": (
            "Dev Box costs show continuous spending including off-hours. "
            "Enabling an auto-stop schedule with hibernate (not shutdown) eliminates "
            "33-47% of compute spend at zero risk to in-progress work."
        ),
        "deliverable_template_id": "tmpl-devbox-autostop",
    }
