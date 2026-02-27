# EVA-STORY: ACA-03-033
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
from app.routers.checkout import router

def test_checkout_router_routes():
    assert len(router.routes) == 5
    paths = [r.path for r in router.routes]
    assert "/tier2" in paths
    assert "/tier3" in paths
    assert "/webhook" in paths
    assert "/portal" in paths
    assert "/entitlements" in paths
    assert paths.count("/webhook") == 1
