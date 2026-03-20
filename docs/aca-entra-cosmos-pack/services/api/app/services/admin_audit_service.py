from datetime import datetime, timezone
from typing import Dict, Optional
import uuid
from app.auth.rbac import Actor
from app.db.repos.admin_audit_repo import AdminAuditRepo

class AdminAuditService:
    def __init__(self, repo: Optional[AdminAuditRepo] = None):
        self.repo = repo or AdminAuditRepo()

    async def record(self, *, actor: Actor, action: str, subscription_id: Optional[str], payload: Dict) -> None:
        doc = {
            "id": f"audit::{uuid.uuid4()}",
            "subscriptionId": subscription_id or "global",
            "occurredUtc": datetime.now(timezone.utc).isoformat(),
            "actorId": actor.actor_id,
            "actorRoles": sorted(list(actor.roles)),
            "action": action,
            "payload": payload,
        }
        await self.repo.append(doc)
