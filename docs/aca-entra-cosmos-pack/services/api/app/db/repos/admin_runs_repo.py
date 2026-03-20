from __future__ import annotations
from typing import Dict, List, Optional
from app.db.cosmos import get_container
from app.settings import settings

class AdminRunsRepo:
    def __init__(self):
        self.scans = get_container(settings.COSMOS_CONTAINER_SCANS)
        self.analyses = get_container(settings.COSMOS_CONTAINER_ANALYSES)
        self.deliverables = get_container(settings.COSMOS_CONTAINER_DELIVERABLES)

    def _container_for_type(self, run_type: str):
        if run_type == "scan":
            return self.scans, "scanId", "completedUtc"
        if run_type == "analysis":
            return self.analyses, "analysisId", "completedUtc"
        return self.deliverables, "deliverableId", "createdUtc"

    async def list_runs(
        self,
        *,
        run_type: str,
        subscription_id: Optional[str],
        status: Optional[str],
        limit: int,
    ) -> List[Dict]:
        container, id_field, finished_field = self._container_for_type(run_type)

        filters = []
        params = [{"name": "@limit", "value": limit}]
        if subscription_id:
            filters.append("c.subscriptionId = @sid")
            params.append({"name": "@sid", "value": subscription_id})
        if status:
            filters.append("c.status = @status")
            params.append({"name": "@status", "value": status})

        where_clause = (" WHERE " + " AND ".join(filters)) if filters else ""
        query = f"SELECT TOP @limit * FROM c{where_clause} ORDER BY c.startedUtc DESC"

        items = list(container.query_items(
            query=query,
            parameters=params,
            partition_key=subscription_id if subscription_id else None,
            enable_cross_partition_query=(subscription_id is None),
        ))

        normalized = []
        for c in items:
            normalized.append({
                "runId": c.get(id_field) or c.get("id"),
                "subscriptionId": c.get("subscriptionId"),
                "type": run_type,
                "status": c.get("status", ""),
                "startedUtc": c.get("startedUtc") or c.get("createdUtc") or "",
                "finishedUtc": c.get(finished_field),
                "durationSeconds": c.get("durationSeconds"),
                "correlationId": c.get("correlationId"),
            })
        return normalized
