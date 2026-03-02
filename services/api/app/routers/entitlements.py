# EVA-STORY: ACA-04-017
"""Entitlements router -- fetch current tier for subscription"""
from fastapi import APIRouter, HTTPException, Request
from ..auth.session import extract_subscription_id

router = APIRouter(tags=["entitlements"])


@router.get("/", summary="Get current tier/entitlements")
async def get_entitlements(request: Request):
    """
    Fetch current tier and entitlements for authenticated subscription.
    APIM will cache this response for 60s per subscriptionId.
    Story ACA-04-017
    """
    # Stub: use mock subscription_id if not provided
    subscription_id = extract_subscription_id(request) or "00000000-0000-0000-0000-000000000001"
    
    # Stub: return TIER1 with no expiry
    return {
        "subscriptionId": subscription_id,
        "tier": "TIER1",
        "expiresAt": None,
        "status": "active",
    }
