from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.db.cosmos import get_container
from app.settings import settings

class AdminAuditRepo:
    def __init__(self):
        self.container = get_container(settings.COSMOS_CONTAINER_ADMIN_AUDIT)

    async def append(self, doc: Dict[str, Any]) -> None:
        self.container.create_item(doc)

    async def list(self, subscription_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
        if subscription_id:
            query = "SELECT TOP @limit * FROM c WHERE c.subscriptionId = @sid ORDER BY c.occurredUtc DESC"
            params = [{"name": "@limit", "value": limit}, {"name": "@sid", "value": subscription_id}]
            return list(self.container.query_items(query=query, parameters=params, partition_key=subscription_id, enable_cross_partition_query=False))
        query = "SELECT TOP @limit * FROM c ORDER BY c.occurredUtc DESC"
        params = [{"name": "@limit", "value": limit}]
        return list(self.container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
