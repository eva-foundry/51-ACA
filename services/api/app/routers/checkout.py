# EVA-STORY: ACA-06-001
# EVA-STORY: ACA-07-001
# EVA-STORY: ACA-08-001
# EVA-STORY: ACA-09-001
"""
Checkout router -- Stripe Tier 2 / Tier 3 checkout, webhook, billing portal,
and entitlements query.

CRITICAL (webhook): read raw body BEFORE any JSON parsing to preserve Stripe
signature.  FastAPI's Request.body() buffers the bytes once; it is safe to
call it before any .json() call.
"""
import logging
from typing import Literal, Optional

import stripe
from fastapi import APIRouter, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.db.repos.clients_repo import ClientsRepo
from app.db.repos.payments_repo import PaymentsRepo
from app.db.repos.stripe_customer_map_repo import StripeCustomerMapRepo
from app.services.delivery_service import DeliveryService
from app.services.entitlement_service import EntitlementService
from app.services.stripe_service import StripeService
from app.settings import get_settings

log = logging.getLogger(__name__)
router = APIRouter(tags=["checkout"])

Tier2Mode = Literal["one_time", "subscription"]


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class CheckoutTier2Request(BaseModel):
    subscription_id: str = Field(..., min_length=1)
    analysis_id: str = Field(default="")
    mode: Tier2Mode = "one_time"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutTier3Request(BaseModel):
    subscription_id: str = Field(..., min_length=1)
    analysis_id: str = Field(..., min_length=1)
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    checkout_session_id: str
    redirect_url: str


class BillingPortalResponse(BaseModel):
    redirect_url: str


class EntitlementsResponse(BaseModel):
    subscription_id: str
    tier: int
    payment_status: str
    can_view_tier2: bool
    can_generate_tier3: bool
    expires_utc: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _svc() -> StripeService:
    return StripeService()


def _default_urls(settings, tier: str):
    base = settings.PUBLIC_APP_URL.rstrip("/")
    return (
        f"{base}/app/download?tier={tier}&session={{CHECKOUT_SESSION_ID}}",
        f"{base}/app/upgrade?cancelled=1",
    )


# ---------------------------------------------------------------------------
# POST /tier2
# ---------------------------------------------------------------------------

@router.post("/tier2", response_model=CheckoutResponse, summary="Create Tier 2 checkout session")
async def checkout_tier2(req: CheckoutTier2Request):
    """
    Create a Stripe checkout session for the Tier 2 Advisory Report.
    Returns a redirect_url for the client to navigate to Stripe.
    """
    s = get_settings()
    success_url, cancel_url = _default_urls(s, "tier2")
    try:
        session = _svc().create_checkout_session(
            tier="tier2",
            subscription_id=req.subscription_id,
            analysis_id=req.analysis_id,
            success_url=req.success_url or success_url,
            cancel_url=req.cancel_url or cancel_url,
            mode=req.mode,
        )
    except stripe.StripeError as exc:
        log.error("[FAIL] stripe checkout_tier2: %s", exc)
        raise HTTPException(status_code=502, detail=f"Stripe error: {exc.user_message or str(exc)}")
    return CheckoutResponse(
        checkout_session_id=session.id,
        redirect_url=session.url or "",
    )


# ---------------------------------------------------------------------------
# POST /tier3
# ---------------------------------------------------------------------------

@router.post("/tier3", response_model=CheckoutResponse, summary="Create Tier 3 checkout session")
async def checkout_tier3(req: CheckoutTier3Request):
    """
    Create a Stripe checkout session for the Tier 3 Deliverable Package.
    """
    s = get_settings()
    success_url, cancel_url = _default_urls(s, "tier3")
    try:
        session = _svc().create_checkout_session(
            tier="tier3",
            subscription_id=req.subscription_id,
            analysis_id=req.analysis_id,
            success_url=req.success_url or success_url,
            cancel_url=req.cancel_url or cancel_url,
        )
    except stripe.StripeError as exc:
        log.error("[FAIL] stripe checkout_tier3: %s", exc)
        raise HTTPException(status_code=502, detail=f"Stripe error: {exc.user_message or str(exc)}")
    return CheckoutResponse(
        checkout_session_id=session.id,
        redirect_url=session.url or "",
    )


# ---------------------------------------------------------------------------
# POST /webhook  (Stripe -> ACA)
# ---------------------------------------------------------------------------

@router.post("/webhook", summary="Stripe webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(default="", alias="Stripe-Signature"),
):
    """
    Handles:
      - checkout.session.completed (one-time Tier 2 / Tier 3 purchase)
      - invoice.paid               (recurring Tier 2 subscription renewal)
      - customer.subscription.updated
      - customer.subscription.deleted
    """
    # MUST read raw body before any .json() call to preserve HMAC signature
    payload = await request.body()

    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    try:
        event = _svc().verify_webhook(payload, stripe_signature)
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")
    except Exception as exc:
        log.error("[FAIL] webhook verify: %s", exc)
        raise HTTPException(status_code=400, detail="Webhook verification failed")

    event_type: str = event.get("type", "")
    data_obj: dict = (event.get("data") or {}).get("object") or {}

    entitlements = EntitlementService()
    delivery = DeliveryService()
    payments_repo = PaymentsRepo()
    cust_map_repo = StripeCustomerMapRepo()
    clients_repo = ClientsRepo()

    # -----------------------------------------------------------------------
    # checkout.session.completed
    # -----------------------------------------------------------------------
    if event_type == "checkout.session.completed":
        session = data_obj
        meta = session.get("metadata") or {}
        tier = meta.get("aca_tier")
        subscription_id = meta.get("aca_subscription_id")
        analysis_id = meta.get("aca_analysis_id") or ""
        mode = meta.get("aca_tier2_mode") or "one_time"
        stripe_customer_id = session.get("customer") or ""
        stripe_subscription_id = session.get("subscription") or ""

        if not tier or not subscription_id:
            return {"received": True, "ignored": "missing_metadata"}

        # Persist customer mapping for future webhook lookups
        if stripe_customer_id:
            cust_map_repo.upsert_map(
                stripe_customer_id=stripe_customer_id,
                subscription_id=subscription_id,
            )
            clients_repo.set_stripe_customer_id(subscription_id, stripe_customer_id)

        # Record payment
        payments_repo.record(
            subscription_id=subscription_id,
            tier=3 if tier == "tier3" else 2,
            mode="subscription" if mode == "subscription" else "one_time",
            stripe_session_id=session.get("id", ""),
            stripe_customer_id=stripe_customer_id or None,
            stripe_subscription_id=stripe_subscription_id or None,
            amount_total=session.get("amount_total"),
            currency=session.get("currency", "cad"),
        )

        # Grant entitlement
        if tier == "tier2":
            entitlements.grant_tier2(
                subscription_id,
                stripe_customer_id=stripe_customer_id or None,
                stripe_subscription_id=stripe_subscription_id or None,
            )
        elif tier == "tier3":
            entitlements.grant_tier3(
                subscription_id,
                stripe_customer_id=stripe_customer_id or None,
                stripe_subscription_id=stripe_subscription_id or None,
            )
            # Fire the delivery job
            deliverable_id = await delivery.trigger_delivery_job(
                subscription_id=subscription_id,
                analysis_id=analysis_id,
            )
            log.info("[INFO] delivery job triggered: %s", deliverable_id)

        return {"received": True, "processed": event_type}

    # -----------------------------------------------------------------------
    # invoice.paid -- recurring Tier 2 subscription renewal
    # -----------------------------------------------------------------------
    if event_type == "invoice.paid":
        stripe_customer_id = data_obj.get("customer") or ""
        stripe_subscription_id = data_obj.get("subscription") or ""
        subscription_id = cust_map_repo.get_subscription_id(stripe_customer_id)
        if subscription_id:
            entitlements.update_payment_status(
                subscription_id,
                "active",
                stripe_subscription_id=stripe_subscription_id or None,
            )
        return {"received": True, "processed": event_type}

    # -----------------------------------------------------------------------
    # customer.subscription.updated (e.g. past_due)
    # -----------------------------------------------------------------------
    if event_type == "customer.subscription.updated":
        stripe_customer_id = data_obj.get("customer") or ""
        stripe_sub_id = data_obj.get("id") or ""
        raw_status = data_obj.get("status", "")
        # Map Stripe status -> ACA payment status
        status_map = {
            "active": "active",
            "past_due": "past_due",
            "unpaid": "past_due",
            "canceled": "canceled",
            "incomplete": "none",
            "incomplete_expired": "none",
            "trialing": "active",
        }
        payment_status = status_map.get(raw_status, "none")
        subscription_id = cust_map_repo.get_subscription_id(stripe_customer_id)
        if subscription_id:
            entitlements.update_payment_status(
                subscription_id,
                payment_status,
                stripe_subscription_id=stripe_sub_id or None,
            )
        return {"received": True, "processed": event_type}

    # -----------------------------------------------------------------------
    # customer.subscription.deleted -- revoke entitlement
    # -----------------------------------------------------------------------
    if event_type == "customer.subscription.deleted":
        stripe_customer_id = data_obj.get("customer") or ""
        subscription_id = cust_map_repo.get_subscription_id(stripe_customer_id)
        if subscription_id:
            entitlements.revoke(subscription_id)
        return {"received": True, "processed": event_type}

    # Unhandled event -- ack so Stripe doesn't retry
    return {"received": True, "ignored": event_type}


# ---------------------------------------------------------------------------
# GET /portal  (redirect client to Stripe billing portal)
# ---------------------------------------------------------------------------

@router.get("/portal", response_model=BillingPortalResponse, summary="Billing portal redirect")
async def billing_portal(subscription_id: str = Query(...)):
    """
    Look up the Stripe customer ID for this subscription, then create a
    Stripe billing portal session and return the redirect URL.

    SECURITY: in production this endpoint must be protected by auth middleware
    so that only the authenticated owner of subscription_id can call it.
    """
    s = get_settings()
    clients_repo = ClientsRepo()
    client = clients_repo.get(subscription_id)
    if not client or not client.get("stripeCustomerId"):
        raise HTTPException(status_code=404, detail="No Stripe customer found for this subscription")

    stripe_customer_id = client["stripeCustomerId"]
    return_url = f"{s.PUBLIC_APP_URL.rstrip('/')}/app/billing"

    try:
        portal = _svc().create_billing_portal_session(
            stripe_customer_id=stripe_customer_id,
            return_url=return_url,
        )
    except stripe.StripeError as exc:
        log.error("[FAIL] billing portal: %s", exc)
        raise HTTPException(status_code=502, detail=f"Stripe error: {exc.user_message or str(exc)}")

    return BillingPortalResponse(redirect_url=portal.url)


# ---------------------------------------------------------------------------
# GET /entitlements
# ---------------------------------------------------------------------------

@router.get("/entitlements", response_model=EntitlementsResponse, summary="Get client entitlements")
async def get_entitlements(subscription_id: str = Query(...)):
    """Return current tier and access flags for a subscription."""
    ent = EntitlementService().get(subscription_id)
    return EntitlementsResponse(
        subscription_id=subscription_id,
        tier=ent.tier,
        payment_status=ent.payment_status,
        can_view_tier2=ent.can_view_tier2,
        can_generate_tier3=ent.can_generate_tier3,
        expires_utc=ent.expires_utc,
    )

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(tags=["checkout"])


class CheckoutRequest(BaseModel):
    subscription_id: str
    scan_id: str | None = None
    success_url: str
    cancel_url: str


@router.post("/tier2", summary="Create Tier 2 checkout session")
async def checkout_tier2(req: CheckoutRequest):
    """
    Create a Stripe checkout session for Tier 2 Advisory Report.
    Returns checkout_url for client redirect.
    See 08-payment.md for full implementation.
    """
    # TODO: create Stripe checkout session, store pending checkout in Cosmos
    raise HTTPException(status_code=501, detail="[INFO] Not yet implemented -- see 08-payment.md")


@router.post("/tier3", summary="Create Tier 3 deliverable checkout session")
async def checkout_tier3(req: CheckoutRequest):
    """
    Create a Stripe checkout session for Tier 3 Deliverable Package.
    Returns checkout_url for client redirect.
    """
    # TODO: create Stripe checkout session
    raise HTTPException(status_code=501, detail="[INFO] Not yet implemented -- see 08-payment.md")


@router.post("/webhook", summary="Stripe webhook handler", include_in_schema=False)
async def stripe_webhook(request: Request):
    """
    Stripe webhook: verify signature, handle checkout.session.completed.
    On Tier 2 payment: upgrade client tier in Cosmos.
    On Tier 3 payment: trigger delivery job, return SAS download URL.
    CRITICAL: read raw body BEFORE json() to preserve Stripe signature.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    # TODO: stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    # TODO: handle checkout.session.completed event
    return {"status": "received"}


@router.get("/entitlements", summary="Get client tier entitlements")
async def get_entitlements(subscription_id: str):
    """Return current tier and available actions for a subscription."""
    # TODO: read client record from Cosmos
    return {"subscription_id": subscription_id, "tier": "tier1", "deliverables": []}
