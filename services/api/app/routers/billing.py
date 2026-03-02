# EVA-STORY: ACA-04-014
# EVA-STORY: ACA-04-015
"""Billing router -- Stripe checkout and portal management"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from ..auth.session import extract_subscription_id

router = APIRouter(tags=["billing"])


class CheckoutRequest(BaseModel):
    desired_tier: str


@router.post("/checkout", summary="Create Stripe checkout session")
async def billing_checkout(request: Request, body: CheckoutRequest):
    """
    Create Stripe checkout for tier upgrade.
    Story ACA-04-014
    """
    # Stub: use mock subscription_id if not provided
    subscription_id = extract_subscription_id(request) or "00000000-0000-0000-0000-000000000001"
    
    if body.desired_tier not in ["TIER2", "TIER3"]:
        raise HTTPException(status_code=400, detail="Invalid tier: must be TIER2 or TIER3")
    
    # Stub: return hardcoded Stripe test session
    session_id = "cs_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
    
    return {
        "sessionId": session_id,
        "checkoutUrl": f"https://checkout.stripe.com/pay/{session_id}",
        "expiresAt": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
    }


@router.get("/portal", summary="Stripe billing portal redirect URL")
async def billing_portal(request: Request):
    """
    Redirect to Stripe customer billing portal.
    Story ACA-04-015
    """
    # Stub: use mock subscription_id if not provided
    subscription_id = extract_subscription_id(request) or "00000000-0000-0000-0000-000000000001"
    
    # Stub: return hardcoded Stripe test portal URL
    portal_url = "https://billing.stripe.com/session/test_Y1NhZWEzZWFjODJfUno3q1VlPZY0UXkPxfG7"
    
    return {
        "portalUrl": portal_url,
        "expiresAt": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
    }
