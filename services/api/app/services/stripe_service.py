"""
Stripe service -- thin wrapper around the stripe SDK.

Keeps all stripe API calls in one place so routers stay clean.
"""
from typing import Any, Dict, Literal, Optional

import stripe

from app.settings import get_settings

Tier2Mode = Literal["one_time", "subscription"]


class StripeService:
    def __init__(self) -> None:
        s = get_settings()
        stripe.api_key = s.STRIPE_SECRET_KEY
        self._settings = s

    # ------------------------------------------------------------------
    # Price helpers
    # ------------------------------------------------------------------
    def _price_tier2(self, mode: Tier2Mode) -> str:
        s = self._settings
        if mode == "subscription" and s.STRIPE_ENABLE_SUBSCRIPTIONS:
            return s.STRIPE_PRICE_TIER2_SUBSCRIPTION
        return s.STRIPE_PRICE_TIER2_ONETIME

    def _price_tier3(self) -> str:
        return self._settings.STRIPE_PRICE_TIER3_ONETIME

    # ------------------------------------------------------------------
    # Checkout sessions
    # ------------------------------------------------------------------
    def create_checkout_session(
        self,
        *,
        tier: Literal["tier2", "tier3"],
        subscription_id: str,
        analysis_id: str,
        success_url: str,
        cancel_url: str,
        mode: Tier2Mode = "one_time",
        customer_email: Optional[str] = None,
        existing_customer_id: Optional[str] = None,
    ) -> stripe.checkout.Session:
        billing_mode = "subscription" if (tier == "tier2" and mode == "subscription") else "payment"
        price_id = self._price_tier2(mode) if tier == "tier2" else self._price_tier3()

        params: Dict[str, Any] = {
            "mode": billing_mode,
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "aca_tier": tier,
                "aca_subscription_id": subscription_id,
                "aca_analysis_id": analysis_id,
                "aca_tier2_mode": mode if tier == "tier2" else "",
            },
        }
        if existing_customer_id:
            params["customer"] = existing_customer_id
        elif customer_email:
            params["customer_email"] = customer_email

        return stripe.checkout.Session.create(**params)

    # ------------------------------------------------------------------
    # Billing portal
    # ------------------------------------------------------------------
    def create_billing_portal_session(
        self,
        *,
        stripe_customer_id: str,
        return_url: str,
    ) -> stripe.billing_portal.Session:
        return stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=return_url,
        )

    # ------------------------------------------------------------------
    # Webhook verification
    # ------------------------------------------------------------------
    def verify_webhook(self, payload: bytes, sig_header: str) -> stripe.Event:
        s = self._settings
        return stripe.Webhook.construct_event(payload, sig_header, s.STRIPE_WEBHOOK_SECRET)
