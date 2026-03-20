from app.models.admin_dtos import AdminKpisResponse

class AdminKpiService:
    async def get_kpis(self) -> AdminKpisResponse:
        # Production TODO:
        # - Stripe revenue MTD
        # - active subscription count from entitlements
        # - 24h run counts from scans/analysis/delivery
        # - failure rate from run statuses
        return AdminKpisResponse(
            revenueMtd=0.0,
            activeSubscriptions=0,
            churnMtd=0,
            scans24h=0,
            analyses24h=0,
            deliveries24h=0,
            failureRate24h=0.0,
            webhookLagSecondsP95=0.0,
        )
