# EVA-STORY: ACA-03-021
import pytest
from services.analysis.app.rules.r11_apim_token_budget import r11_apim_token_budget

def test_r11_apim_token_budget():
    # Test with both APIM and OpenAI present
    findings = r11_apim_token_budget(has_apim=True, has_openai=True)
    assert len(findings) == 1
    assert findings[0]["id"] == "apim-openai-token-risk"
    assert findings[0]["category"] == "api-cost-optimization"
    
    # Test with only APIM
    findings = r11_apim_token_budget(has_apim=True, has_openai=False)
    assert len(findings) == 0
    
    # Test with only OpenAI
    findings = r11_apim_token_budget(has_apim=False, has_openai=True)
    assert len(findings) == 0
    
    # Test with neither
    findings = r11_apim_token_budget(has_apim=False, has_openai=False)
    assert len(findings) == 0
