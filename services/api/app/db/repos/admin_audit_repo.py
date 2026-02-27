"""
Admin audit events repository.

Container : admin_audit_events
Partition : /subscriptionId
ID scheme : "audit::{event_type}::{timestamp_ms}"

Append-only. Written by admin endpoints; never deleted.
"""
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.cosmos import get_container, query_items
from app.settings import get_settings


class AdminAuditRepo:
    def __init__(self) -> None:
        s = get_settings()
        self.container = get_container(s.COSMOS_CONTAINER_ADMIN_AUDIT)

    def write(
        self,
        *,
        event_type: str,
        subscription_id: str,
        actor: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        ts_ms = int(time.time() * 1000)
        doc: Dict[str, Any] = {
            "id": f"audit::{event_type}::{ts_ms}",
            "subscriptionId": subscription_id,
            "eventType": event_type,
            "actor": actor,
            "details": details or {},
            "createdUtc": now,
        }
        return self.container.upsert_item(doc)

    def list_for_subscription(
        self,
        subscription_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        return query_items(
            "admin_audit_events",
            "SELECT TOP @limit * FROM c WHERE c.subscriptionId = @sub ORDER BY c.createdUtc DESC",
            [{"name": "@sub", "value": subscription_id}, {"name": "@limit", "value": limit}],
            partition_key=subscription_id,
        )
