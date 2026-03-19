from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.db.cosmos import get_container
from app.settings import settings

class AdminCustomerRepo:
    def __init__(self):
        self.entitlements = get_container(settings.COSMOS_CONTAINER_ENTITLEMENTS)
        self.clients = get_container(settings.COSMOS_CONTAINER_CLIENTS)
        self.scans = get_container(settings.COSMOS_CONTAINER_SCANS)
        self.analyses = get_container(settings.COSMOS_CONTAINER_ANALYSES)
        self.deliverables = get_container(settings.COSMOS_CONTAINER_DELIVERABLES)

    async def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        # Search entitlement docs by subscriptionId prefix.
        q = "SELECT TOP @limit c.id, c.subscriptionId, c.tier, c.paymentStatus, c.updatedUtc FROM c WHERE STARTSWITH(c.subscriptionId, @q)"
        params = [{"name": "@limit", "value": limit}, {"name": "@q", "value": query}]
        items = list(self.entitlements.query_items(query=q, parameters=params, enable_cross_partition_query=True))

        results: List[Dict[str, Any]] = []
        for item in items:
            client_doc = self._safe_read_client(item.get("subscriptionId"))
            results.append({
                "subscriptionId": item.get("subscriptionId"),
                "tier": item.get("tier", 1),
                "paymentStatus": item.get("paymentStatus", "none"),
                "locked": bool((client_doc or {}).get("locked", False)),
                "lastSeenUtc": item.get("updatedUtc"),
            })
        return results

    def _safe_read_client(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.clients.read_item(item=f"client::{subscription_id}", partition_key=subscription_id)
        except Exception:
            return None

    def _safe_latest_time(self, container, subscription_id: str, field_name: str = "updatedUtc") -> Optional[str]:
        query = f"SELECT TOP 1 c.{field_name} FROM c WHERE c.subscriptionId = @sid ORDER BY c.{field_name} DESC"
        params = [{"name": "@sid", "value": subscription_id}]
        items = list(container.query_items(query=query, parameters=params, partition_key=subscription_id, enable_cross_partition_query=False))
        if not items:
            return None
        return items[0].get(field_name)

    async def get_customer(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        try:
            ent = self.entitlements.read_item(item=f"entitlement::{subscription_id}", partition_key=subscription_id)
        except Exception:
            return None

        client_doc = self._safe_read_client(subscription_id) or {}

        return {
            "subscriptionId": subscription_id,
            "tier": ent.get("tier", 1),
            "paymentStatus": ent.get("paymentStatus", "none"),
            "expiresUtc": ent.get("expiresUtc"),
            "locked": bool(client_doc.get("locked", False)),
            "stripeCustomerId": client_doc.get("stripeCustomerId"),
            "lastScanUtc": self._safe_latest_time(self.scans, subscription_id, "completedUtc"),
            "lastAnalysisUtc": self._safe_latest_time(self.analyses, subscription_id, "completedUtc"),
            "lastDeliveryUtc": self._safe_latest_time(self.deliverables, subscription_id, "createdUtc"),
        }

    async def set_locked(self, subscription_id: str, locked: bool, reason: str) -> Dict[str, Any]:
        try:
            doc = self.clients.read_item(item=f"client::{subscription_id}", partition_key=subscription_id)
        except Exception:
            doc = {"id": f"client::{subscription_id}", "subscriptionId": subscription_id}

        doc["locked"] = locked
        doc["lockReason"] = reason
        self.clients.upsert_item(doc)
        return doc
