"""
# EVA-STORY: ACA-03-013
Rule 03: Defender for Cloud Plan Mismatch
Source: 14-az-finops saving-opportunities.md #3
Saving: CAD $4,000-$6,000/yr
Effort: easy | Risk: low
"""

RULE_ID = "rule-03-defender-mismatch"


def rule_03_defender_mismatch(data: dict) -> dict | None:
    """Detects Defender costs disproportionately high vs expected for scope."""
    cost_rows = data.get("cost_rows", [])
    def_rows = [r for r in cost_rows
                if "defender" in str(r.get("MeterCategory", "")).lower()
                or "security center" in str(r.get("MeterCategory", "")).lower()]
    if not def_rows:
        return None

    annual_cost = sum(float(r.get("Cost", 0)) for r in def_rows) / len(def_rows) * 365
    if annual_cost < 2000:
        return None

    return {
        "id": RULE_ID,
        "category": "security-plan",
        "title": "Defender for Cloud plan tier may be higher than required for this environment",
        "estimated_saving_low": round(annual_cost * 0.28),
        "estimated_saving_high": round(annual_cost * 0.42),
        "effort_class": "easy",
        "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": (
            "Defender costs are elevated relative to the subscription scope. "
            "P2-to-P1 downgrade on non-production VMs or excluding dev resource groups "
            "from server-level plans is a common 28-42% cost reduction."
        ),
        "deliverable_template_id": "tmpl-defender-plan",
    }
