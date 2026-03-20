from typing import List, Optional
from app.models.admin_dtos import AdminRunsResponse, AdminRunItem, RunType

class AdminRunService:
    async def list_runs(
        self,
        *,
        run_type: RunType,
        subscription_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> AdminRunsResponse:
        # Production TODO: unify scan / analysis / delivery records into one response.
        return AdminRunsResponse(items=[])
