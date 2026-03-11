"""
# EVA-STORY: ACA-03-021
Rule R-11: APIM Token Budget Enforcement
Source: 14-az-finops saving-opportunities.md #11
Risk: high (no dollar saving -- governance risk only)
Effort: medium
"""

RULE_ID = "r11-apim-token-budget"


def r11_apim_token_budget(data: dict) -> dict | None:
    """
    Detects subscriptions running both APIM and Azure OpenAI without token budget controls.
    Risk-only finding: no dollar saving, risk_class=high.
    """
    resources = data.get("resources", [])
    has_apim = any(
        "apimanagement/service" in str(r.get("type", r.get("resourceType", ""))).lower()
        for r in resources
    )
    has_openai = any(
        "cognitiveservices" in str(r.get("type", r.get("resourceType", ""))).lower()
        or "openai" in str(r.get("type", r.get("resourceType", ""))).lower()
        for r in resources
    )

    if not (has_apim and has_openai):
        return None

    return {
        "id": RULE_ID,
        "finding_type": "cost_risk",
        "category": "cost-governance",
        "title": "APIM + Azure OpenAI present without confirmed token budget policy",
        "estimated_saving_low": 0,
        "estimated_saving_high": 0,
        "effort_class": "medium",
        "risk_class": "high",
        "heuristic_source": RULE_ID,
        "narrative": (
            "APIM and OpenAI/AI services are both deployed in this subscription. "
            "Without per-application token budget policies enforced at the APIM gateway, "
            "a single runaway client can exhaust the entire token quota, creating unbounded "
            "cost exposure. Historical incidents from this pattern have exceeded $150K in "
            "a single billing period."
        ),
        "deliverable_template_id": "tmpl-apim-token-budget",
    }
