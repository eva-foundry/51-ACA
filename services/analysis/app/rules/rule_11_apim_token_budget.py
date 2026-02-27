"""Rule 11: APIM Token Budget Enforcement -- Source: 14-az-finops #11"""
RULE_ID = "rule-11-apim-token-budget"

def rule_11_apim_token_budget(data: dict) -> dict | None:
    resources = data.get("resources", [])
    has_apim = any("apimanagement/service" in r.get("type", "").lower() for r in resources)
    has_openai = any("cognitiveservices" in r.get("type", "").lower() for r in resources)
    if not (has_apim and has_openai):
        return None
    return {
        "id": RULE_ID, "category": "cost-governance",
        "title": "APIM and OpenAI/AI services found -- per-app token budget enforcement not confirmed",
        "estimated_saving_low": 0, "estimated_saving_high": 0,
        "effort_class": "involved", "risk_class": "high",
        "heuristic_source": RULE_ID,
        "narrative": "A subscription running both APIM and Azure OpenAI without token budget policies is at high risk of uncapped AI spend. Historical incidents from this pattern have exceeded $150K in a single billing period.",
        "deliverable_template_id": "tmpl-apim-token-budget",
    }
