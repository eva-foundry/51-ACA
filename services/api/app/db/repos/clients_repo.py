"""
# EVA-STORY: ACA-04-003
Clients repository.

Container : clients
Partition : /subscriptionId
ID scheme : "client::{subscriptionId}"

Stores per-tenant ACA client record: auth mode, tier, status, dates.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.db.cosmos import get_container
from app.settings import get_settings


class ClientsRepo:
    def __init__(self) -> None:
        s = get_settings()
        self.container = get_container(s.COSMOS_CONTAINER_CLIENTS)

    def _doc_id(self, subscription_id: str) -> str:
        return f"client::{subscription_id}"

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
        auth_mode: str,
        tier: int = 1,
        status: str = "active",
        stripe_customer_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        existing = self.get(subscription_id) or {}
        doc: Dict[str, Any] = {
            **existing,
            "id": self._doc_id(subscription_id),
            "subscriptionId": subscription_id,
            "authMode": auth_mode,
            "tier": tier,
            "status": status,
            "stripeCustomerId": stripe_customer_id or existing.get("stripeCustomerId", ""),
            "updatedUtc": now,
        }
        if "createdUtc" not in doc:
            doc["createdUtc"] = now
        if extra:
            doc.update(extra)
        return self.container.upsert_item(doc)

    def set_stripe_customer_id(self, subscription_id: str, stripe_customer_id: str) -> None:
        """Patch stripeCustomerId onto existing client record."""
        client = self.get(subscription_id)
        if not client:
            return
        client["stripeCustomerId"] = stripe_customer_id
        client["updatedUtc"] = datetime.now(timezone.utc).isoformat()
        self.container.upsert_item(client)
