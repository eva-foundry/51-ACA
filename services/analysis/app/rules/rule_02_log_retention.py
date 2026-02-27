"""
Rule 02: Log Analytics Retention Right-Size
Source: 14-az-finops saving-opportunities.md #2
Saving: CAD $1,000-$2,000/yr
Effort: trivial | Risk: none in dev
"""

RULE_ID = "rule-02-log-retention"


def rule_02_log_retention(data: dict) -> dict | None:
    """Detects Log Analytics workspaces likely at default 90-day retention in non-prod."""
    cost_rows = data.get("cost_rows", [])
    log_rows = [r for r in cost_rows
                if "log analytics" in str(r.get("MeterCategory", "")).lower()]
    if not log_rows:
        return None

    annual_cost = sum(float(r.get("Cost", 0)) for r in log_rows) / len(log_rows) * 365
    if annual_cost < 500:
        return None

    return {
        "id": RULE_ID,
        "category": "storage-retention",
        "title": "Log Analytics workspaces likely retaining more data than required for dev",
        "estimated_saving_low": round(annual_cost * 0.25),
        "estimated_saving_high": round(annual_cost * 0.50),
        "effort_class": "trivial",
        "risk_class": "none",
        "heuristic_source": RULE_ID,
        "narrative": (
            "Non-production Log Analytics workspaces typically default to 90-day retention. "
            "Reducing to 7-14 days eliminates redundant ingestion charges at no operational risk."
        ),
        "deliverable_template_id": "tmpl-log-retention",
    }
