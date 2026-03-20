from typing import Optional
from app.models.admin_dtos import AdminRunsResponse, AdminRunItem, RunType
from app.db.repos.admin_runs_repo import AdminRunsRepo

class AdminRunService:
    def __init__(self, repo: Optional[AdminRunsRepo] = None):
        self.repo = repo or AdminRunsRepo()

    async def list_runs(
        self,
        *,
        run_type: RunType,
        subscription_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> AdminRunsResponse:
        items = await self.repo.list_runs(
            run_type=run_type,
            subscription_id=subscription_id,
            status=status,
            limit=limit,
        )
        return AdminRunsResponse(items=[AdminRunItem(**i) for i in items])
