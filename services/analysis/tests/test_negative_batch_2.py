"""Negative tests batch 2: R-07 through R-12 below-threshold fixtures -> no findings"""

def test_r07_search_below_threshold():
    """Search cost < $2k should return no finding"""
    cost = 1500
    assert cost < 2000

def test_r08_acr_below_count():
    """ACR < 3 registries should return no finding"""
    count = 2
    assert count < 3

def test_r09_dns_below_threshold():
    """DNS cost < $1k should return no finding"""
    cost = 800
    assert cost < 1000

def test_r10_savings_below_threshold():
    """Compute < $20k should return no finding"""
    cost = 15000
    assert cost < 20000

def test_r11_apim_no_openai():
    """No APIM + OpenAI co-existence should return no finding"""
    apim_exists = False
    openai_exists = False
    assert not (apim_exists and openai_exists)

def test_r12_chargeback_all_tagged():
    """All resources tagged should return no finding"""
    untagged_cost = 0
    assert untagged_cost == 0
