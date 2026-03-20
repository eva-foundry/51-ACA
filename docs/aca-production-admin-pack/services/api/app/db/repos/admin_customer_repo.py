from typing import Any, Dict, List, Optional
from app.db.cosmos import get_container
from app.settings import settings

class AdminCustomerRepo:
    def __init__(self):
        self.entitlements = get_container(getattr(settings, "COSMOS_CONTAINER_ENTITLEMENTS", "entitlements"))
        self.clients = get_container(getattr(settings, "COSMOS_CONTAINER_CLIENTS", "clients"))
        self.scans = get_container(getattr(settings, "COSMOS_CONTAINER_SCANS", "scans"))
        self.findings = get_container(getattr(settings, "COSMOS_CONTAINER_FINDINGS", "findings"))

    async def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        # Production TODO:
        # implement by ACA subscriptionId prefix and/or stripe customer mapping lookup
        return []

    async def get_customer(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        # Production TODO:
        return None
