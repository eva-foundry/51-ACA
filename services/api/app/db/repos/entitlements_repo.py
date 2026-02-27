"""
Entitlements repository.

Container : entitlements
Partition : /subscriptionId
ID scheme : "entitlement::{subscriptionId}"
"""
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

from app.db.cosmos import get_container
from app.settings import get_settings

PaymentStatus = Literal["none", "active", "past_due", "canceled"]
Tier = Literal[1, 2, 3]


class EntitlementsRepo:
    def __init__(self) -> None:
        s = get_settings()
        self.container = get_container(s.COSMOS_CONTAINER_ENTITLEMENTS)

    def _doc_id(self, subscription_id: str) -> str:
        return f"entitlement::{subscription_id}"

    def get(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.container.read_item(
                item=self._doc_id(subscription_id),
                partition_key=subscription_id,
            )
        except Exception:
            return None

    def upsert(
        self,
        *,
        subscription_id: str,
        tier: Tier,
        payment_status: PaymentStatus,
        source: str,
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None,
        expires_utc: Optional[str] = None,
        is_locked: bool = False,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        doc: Dict[str, Any] = {
            "id": self._doc_id(subscription_id),
            "subscriptionId": subscription_id,
            "tier": tier,
            "paymentStatus": payment_status,
            "source": source,
            "stripeCustomerId": stripe_customer_id or "",
            "stripeSubscriptionId": stripe_subscription_id or "",
            "expiresUtc": expires_utc or "",
            "isLocked": is_locked,
            "updatedUtc": now,
        }
        return self.container.upsert_item(doc)

    def set_locked(
        self,
        subscription_id: str,
        *,
        locked: bool,
        reason: str = "",
    ) -> Dict[str, Any]:
        """Set isLocked flag on the entitlement record. Creates a minimal record if absent."""
        now = datetime.now(timezone.utc).isoformat()
        existing = self.get(subscription_id)
        if existing:
            existing["isLocked"] = locked
            existing["lockReason"] = reason
            existing["updatedUtc"] = now
            return self.container.upsert_item(existing)
        # No entitlement yet -- create a locked placeholder at tier 1
        doc: Dict[str, Any] = {
            "id": self._doc_id(subscription_id),
            "subscriptionId": subscription_id,
            "tier": 1,
            "paymentStatus": "none",
            "source": "admin_lock",
            "stripeCustomerId": "",
            "stripeSubscriptionId": "",
            "expiresUtc": "",
            "isLocked": locked,
            "lockReason": reason,
            "updatedUtc": now,
        }
        return self.container.upsert_item(doc)
