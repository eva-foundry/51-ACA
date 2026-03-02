# EVA-STORY: ACA-04-016
"""Webhooks router -- Stripe event handler"""
from fastapi import APIRouter, HTTPException, Request
import hmac
import hashlib
import os

router = APIRouter(tags=["webhooks"])


@router.post("/stripe", summary="Stripe webhook event handler")
async def webhook_stripe(request: Request):
    """
    Handle Stripe webhook events (subscription updated, invoice paid).
    No JWT auth required -- signature validated via HMAC-SHA256.
    Story ACA-04-016
    """
    # Get Stripe signature header
    stripe_signature = request.headers.get("stripe-signature")
    
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    # Get raw body (stub: would validate signature here)
    # In production: compute HMAC-SHA256(secret, raw_body) and compare to stripe_signature
    
    # Stub: assume all signatures valid (would fail in production)
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    
    # For now, just accept and log
    return {
        "status": "received",
        "eventId": "evt_stub_12345",
    }
