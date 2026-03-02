"""R-11: APIM + OpenAI token budget optimization"""

def evaluate_apim_token(inventory, cost_data, advisor_data):
    """Returns finding if both APIM and OpenAI present (opportunity for token management)"""
    has_apim = any("API Management" in res.get("type", "") for res in inventory)
    has_openai = any("OpenAI" in res.get("type", "") or "CognitiveServices" in res.get("type", "") for res in inventory)
    
    if has_apim and has_openai:
        return {
            "id": "rule-11-apim-token",
            "category": "integration",
            "title": "APIM token budget optimization",
            "estimated_saving_low": 500,
            "estimated_saving_high": 2000,
            "effort_class": "medium",
            "risk_class": "low",
            "heuristic_source": "rule-11",
            "narrative": "APIM + OpenAI present together; implement token budgeting policy",
        }
    return None
