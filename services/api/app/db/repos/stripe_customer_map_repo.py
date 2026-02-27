"""
# EVA-STORY: ACA-06-016
Stripe customer map repository.

Container : stripe_customer_map
Partition : /stripeCustomerId
ID scheme : "cust::{stripeCustomerId}"

Enables O(1) lookup of ACA subscriptionId from a Stripe customerId
(needed in webhook handlers where we only have the Stripe customer).
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.db.cosmos import get_container
from app.settings import get_settings


class StripeCustomerMapRepo:
    def __init__(self) -> None:
        s = get_settings()
        self.container = get_container(s.COSMOS_CONTAINER_STRIPE_CUSTOMER_MAP)

    def upsert_map(self, *, stripe_customer_id: str, subscription_id: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        doc: Dict[str, Any] = {
            "id": f"cust::{stripe_customer_id}",
            "stripeCustomerId": stripe_customer_id,
            "subscriptionId": subscription_id,
            "updatedUtc": now,
        }
        return self.container.upsert_item(doc)

    def get_subscription_id(self, stripe_customer_id: str) -> Optional[str]:
        doc_id = f"cust::{stripe_customer_id}"
        try:
            doc = self.container.read_item(
                item=doc_id,
                partition_key=stripe_customer_id,
            )
            return doc.get("subscriptionId")
        except Exception:
            return None
