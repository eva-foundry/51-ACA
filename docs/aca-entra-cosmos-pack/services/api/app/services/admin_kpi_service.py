from datetime import datetime, timedelta, timezone

from app.models.admin_dtos import AdminKpisResponse
from app.db.cosmos import get_container
from app.settings import settings

class AdminKpiService:
    async def get_kpis(self) -> AdminKpisResponse:
        entitlements = get_container(settings.COSMOS_CONTAINER_ENTITLEMENTS)
        scans = get_container(settings.COSMOS_CONTAINER_SCANS)
        analyses = get_container(settings.COSMOS_CONTAINER_ANALYSES)
        deliverables = get_container(settings.COSMOS_CONTAINER_DELIVERABLES)

        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(hours=24)).isoformat()

        def count_query(container, query, params=None):
            items = list(container.query_items(query=query, parameters=params or [], enable_cross_partition_query=True))
            if not items:
                return 0
            return items[0].get("count", 0)

        active_subs = count_query(entitlements, "SELECT VALUE COUNT(1) FROM c WHERE c.paymentStatus = 'active'")
        scans24 = count_query(scans, "SELECT VALUE COUNT(1) FROM c WHERE c.startedUtc >= @cutoff", [{"name": "@cutoff", "value": cutoff}])
        analyses24 = count_query(analyses, "SELECT VALUE COUNT(1) FROM c WHERE c.startedUtc >= @cutoff", [{"name": "@cutoff", "value": cutoff}])
        deliveries24 = count_query(deliverables, "SELECT VALUE COUNT(1) FROM c WHERE c.createdUtc >= @cutoff", [{"name": "@cutoff", "value": cutoff}])

        return AdminKpisResponse(
            revenueMtd=0.0,              # TODO: derive from Stripe/reporting source
            activeSubscriptions=active_subs,
            churnMtd=0,                 # TODO
            scans24h=scans24,
            analyses24h=analyses24,
            deliveries24h=deliveries24,
            failureRate24h=0.0,         # TODO
            webhookLagSecondsP95=0.0,   # TODO
        )
