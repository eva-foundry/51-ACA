from typing import Any, Dict, List, Optional
from app.db.cosmos import get_container
from app.settings import settings

class AdminAuditRepo:
    def __init__(self):
        self.container = get_container(getattr(settings, "COSMOS_CONTAINER_ADMIN_AUDIT", "admin_audit"))

    async def append(self, doc: Dict[str, Any]) -> None:
        self.container.create_item(doc)

    async def list(self, subscription_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
        # Production TODO:
        # query admin audit container by subscriptionId or global.
        return []
