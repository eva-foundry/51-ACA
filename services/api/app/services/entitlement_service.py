"""
Entitlement service -- business logic layer over EntitlementsRepo.

Abstracts tier/payment-status persistence so routers and webhook
handlers call one method and don't touch Cosmos directly.
"""
from dataclasses import dataclass
from typing import Literal, Optional

from app.db.repos.entitlements_repo import EntitlementsRepo, PaymentStatus, Tier

PaymentStatus = Literal["none", "active", "past_due", "canceled"]  # re-export


@dataclass
class Entitlement:
    tier: int
    payment_status: str
    stripe_customer_id: str = ""
    stripe_subscription_id: str = ""
    expires_utc: str = ""

    @property
    def can_view_tier2(self) -> bool:
        return self.tier >= 2 and self.payment_status in ("active", "past_due")

    @property
    def can_generate_tier3(self) -> bool:
        return self.tier >= 3 and self.payment_status == "active"


class EntitlementService:
    def __init__(self) -> None:
        self._repo = EntitlementsRepo()

    def get(self, subscription_id: str) -> Entitlement:
        doc = self._repo.get(subscription_id)
        if not doc:
            return Entitlement(tier=1, payment_status="none")
        return Entitlement(
            tier=doc.get("tier", 1),
            payment_status=doc.get("paymentStatus", "none"),
            stripe_customer_id=doc.get("stripeCustomerId", ""),
            stripe_subscription_id=doc.get("stripeSubscriptionId", ""),
            expires_utc=doc.get("expiresUtc", ""),
        )

    def grant_tier2(
        self,
        subscription_id: str,
        *,
        payment_status: str = "active",
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None,
    ) -> None:
        existing = self.get(subscription_id)
        # never downgrade -- only upgrade tier
        new_tier: Tier = max(2, existing.tier)  # type: ignore[assignment]
        self._repo.upsert(
            subscription_id=subscription_id,
            tier=new_tier,
            payment_status=payment_status,  # type: ignore[arg-type]
            source="stripe",
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )

    def grant_tier3(
        self,
        subscription_id: str,
        *,
        payment_status: str = "active",
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None,
    ) -> None:
        self._repo.upsert(
            subscription_id=subscription_id,
            tier=3,
            payment_status=payment_status,  # type: ignore[arg-type]
            source="stripe",
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )

    def update_payment_status(
        self,
        subscription_id: str,
        payment_status: str,
        *,
        stripe_subscription_id: Optional[str] = None,
    ) -> None:
        """Called by recurring billing lifecycle webhooks (invoice.paid, etc.)"""
        existing = self.get(subscription_id)
        self._repo.upsert(
            subscription_id=subscription_id,
            tier=existing.tier,  # type: ignore[arg-type]
            payment_status=payment_status,  # type: ignore[arg-type]
            source="stripe_lifecycle",
            stripe_customer_id=existing.stripe_customer_id or None,
            stripe_subscription_id=(
                stripe_subscription_id or existing.stripe_subscription_id or None
            ),
        )

    def revoke(self, subscription_id: str) -> None:
        """Cancel entitlement -- called on subscription.deleted."""
        existing = self.get(subscription_id)
        self._repo.upsert(
            subscription_id=subscription_id,
            tier=1,
            payment_status="canceled",
            source="stripe_lifecycle",
            stripe_customer_id=existing.stripe_customer_id or None,
            stripe_subscription_id=existing.stripe_subscription_id or None,
        )
