"""
Payments repository.

Container : payments
Partition : /subscriptionId
ID scheme : "payment::{stripeSessionId}"
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from app.db.cosmos import get_container
from app.settings import get_settings

PaymentMode = Literal["one_time", "subscription"]
Tier = Literal[1, 2, 3]


class PaymentsRepo:
    def __init__(self) -> None:
        s = get_settings()
        self.container = get_container(s.COSMOS_CONTAINER_PAYMENTS)

    def record(
        self,
        *,
        subscription_id: str,
        tier: Tier,
        mode: PaymentMode,
        stripe_session_id: str,
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None,
        amount_total: Optional[int] = None,
        currency: str = "cad",
        status: str = "completed",
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        doc: Dict[str, Any] = {
            "id": f"payment::{stripe_session_id}",
            "subscriptionId": subscription_id,
            "tier": tier,
            "mode": mode,
            "stripeSessionId": stripe_session_id,
            "stripeCustomerId": stripe_customer_id or "",
            "stripeSubscriptionId": stripe_subscription_id or "",
            "amountTotal": amount_total,
            "currency": currency,
            "status": status,
            "createdUtc": now,
        }
        return self.container.upsert_item(doc)

    def list_for_subscription(self, subscription_id: str) -> List[Dict[str, Any]]:
        from app.db.cosmos import query_items
        return query_items(
            "payments",
            "SELECT * FROM c WHERE c.subscriptionId = @sub ORDER BY c.createdUtc DESC",
            [{"name": "@sub", "value": subscription_id}],
            partition_key=subscription_id,
        )
