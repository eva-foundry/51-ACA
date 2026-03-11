"""Unit tests for R-11: APIM token budget enforcement"""
# EVA-STORY: ACA-03-021
from services.analysis.app.rules.rule_11_apim_token_budget import rule_11_apim_token_budget


def test_apim_and_openai_both_present():
    """Should flag when APIM and OpenAI/AI services both exist"""
    data = {
        "resources": [
            {"type": "Microsoft.ApiManagement/service"},
            {"type": "Microsoft.CognitiveServices/openAI"},
        ]
    }
    result = rule_11_apim_token_budget(data)
    assert result is not None
    assert result["id"] == "rule-11-apim-token-budget"
    assert result["risk_class"] == "high"
    assert result["effort_class"] == "medium"
    assert result["estimated_saving_low"] == 0
    assert result["estimated_saving_high"] == 0


def test_apim_without_openai():
    """Should not flag when APIM exists but no OpenAI"""
    data = {
        "resources": [
            {"type": "Microsoft.ApiManagement/service"},
            {"type": "Microsoft.Storage/storageAccounts"},
        ]
    }
    result = rule_11_apim_token_budget(data)
    assert result is None


def test_openai_without_apim():
    """Should not flag when OpenAI exists but no APIM"""
    data = {
        "resources": [
            {"type": "Microsoft.CognitiveServices/openAI"},
            {"type": "Microsoft.Storage/storageAccounts"},
        ]
    }
    result = rule_11_apim_token_budget(data)
    assert result is None


def test_apim_no_resources():
    """Should return None when resources list is empty"""
    result = rule_11_apim_token_budget({"resources": []})
    assert result is None


def test_apim_risk_only_no_saving():
    """Confirmed: risk-only finding with zero saving estimate"""
    data = {
        "resources": [
            {"type": "Microsoft.ApiManagement/service"},
            {"type": "Microsoft.CognitiveServices/accounts", "kind": "OpenAI"},
        ]
    }
    result = rule_11_apim_token_budget(data)
    assert result is not None
    assert result["estimated_saving_low"] == 0
    assert result["estimated_saving_high"] == 0

