# EVA-STORY: ACA-03-021
from typing import Optional, List, Dict

def r11_apim_token_budget(has_apim: bool = False, has_openai: bool = False) -> list[dict]:
    """
    Identify API Management with OpenAI token budget risk.

    Args:
        has_apim (bool): Whether APIM is present.
        has_openai (bool): Whether OpenAI service is present.

    Returns:
        list[dict]: Findings if both services present.
    """
    findings = []
    
    # Risk flag: APIM + OpenAI = potential token budget exhaustion
    if has_apim and has_openai:
        findings.append({
            "id": "apim-openai-token-risk",
            "title": "API Management with OpenAI Token Budget Risk",
            "category": "api-cost-optimization",
            "estimated_saving_low": 2000,
            "estimated_saving_high": 5000,
            "effort_class": "medium",
            "risk_class": "medium",
            "heuristic_source": "r11_apim_token_budget"
        })
    
    return findings
