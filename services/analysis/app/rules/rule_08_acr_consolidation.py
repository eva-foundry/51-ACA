"""Rule 08: Container Registry Consolidation -- Source: 14-az-finops #8"""
RULE_ID = "rule-08-acr-consolidation"

def rule_08_acr_consolidation(data: dict) -> dict | None:
    resources = data.get("resources", [])
    acrs = [r for r in resources if "containerregistry/registries" in r.get("type", "").lower()]
    if len(acrs) <= 2:
        return None
    return {
        "id": RULE_ID, "category": "service-consolidation",
        "title": f"Multiple container registries detected ({len(acrs)}); consolidation opportunity",
        "estimated_saving_low": round((len(acrs) - 1) * 1800), "estimated_saving_high": round((len(acrs) - 1) * 2400),
        "effort_class": "medium", "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": f"{len(acrs)} container registries found. Per-environment registries are a common cost driver; consolidating to a shared Standard-tier ACR eliminates per-registry standing charges.",
        "deliverable_template_id": "tmpl-acr-consolidation",
    }
