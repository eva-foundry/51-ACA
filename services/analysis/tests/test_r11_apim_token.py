"""Unit tests for R-11: APIM token budget risk detection"""
# EVA-STORY: ACA-03-021
from services.analysis.app.rules.r11_apim_token_budget import r11_apim_token_budget


def test_apim_and_openai_triggers_finding():
    """Should flag when both APIM and OpenAI are present"""
    data = {
        "resources": [
            {"type": "Microsoft.ApiManagement/service", "name": "my-apim"},
            {"type": "Microsoft.CognitiveServices/accounts", "name": "my-openai"},
        ]
    }
    result = r11_apim_token_budget(data)
    assert result is not None
    assert result["id"] == "r11-apim-token-budget"
    assert result["risk_class"] == "high"
    assert result["estimated_saving_low"] == 0
    assert result["estimated_saving_high"] == 0
    assert result["effort_class"] == "medium"


def test_apim_only_returns_none():
    """Should not flag when only APIM is present (no OpenAI)"""
    data = {
        "resources": [
            {"type": "Microsoft.ApiManagement/service", "name": "my-apim"},
        ]
    }
    result = r11_apim_token_budget(data)
    assert result is None


def test_openai_only_returns_none():
    """Should not flag when only OpenAI is present (no APIM)"""
    data = {
        "resources": [
            {"type": "Microsoft.CognitiveServices/accounts", "name": "my-openai"},
        ]
    }
    result = r11_apim_token_budget(data)
    assert result is None


def test_no_resources_returns_none():
    """Should return None when no resources present"""
    result = r11_apim_token_budget({"resources": []})
    assert result is None


def test_empty_data_returns_none():
    """Should handle completely empty data dict"""
    result = r11_apim_token_budget({})
    assert result is None


def test_finding_type_is_cost_risk():
    """Finding type should be cost_risk (governance risk, not a saving)"""
    data = {
        "resources": [
            {"type": "Microsoft.ApiManagement/service", "name": "apim"},
            {"type": "Microsoft.CognitiveServices/openAI", "name": "oai"},
        ]
    }
    result = r11_apim_token_budget(data)
    assert result is not None
    assert result["finding_type"] == "cost_risk"
