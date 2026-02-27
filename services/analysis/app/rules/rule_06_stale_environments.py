"""Rule 06: Stale Environment Detection -- Source: 14-az-finops #6"""
RULE_ID = "rule-06-stale-environments"

def rule_06_stale_environments(data: dict) -> dict | None:
    resources = data.get("resources", [])
    app_services = [r for r in resources if "microsoft.web/sites" in r.get("type", "").lower()]
    if len(app_services) < 3:
        return None
    return {
        "id": RULE_ID, "category": "idle-resources",
        "title": f"Multiple App Service instances detected ({len(app_services)}); some may be idle",
        "estimated_saving_low": round(len(app_services) * 0.3 * 3000),
        "estimated_saving_high": round(len(app_services) * 0.5 * 5000),
        "effort_class": "easy", "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": "Multiple App Service instances exist. Usage analysis typically reveals 30-50% are idle with zero active sessions, presenting an immediate decommission opportunity.",
        "deliverable_template_id": "tmpl-stale-envs",
    }
