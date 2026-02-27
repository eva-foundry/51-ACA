"""
Delivery service -- triggers the Tier 3 delivery Container Apps Job.

Phase 1: stub that returns an opaque deliverable ID immediately.
Phase 2: enqueue a Container Apps Job run and poll for completion.
"""


class DeliveryService:
    async def trigger_delivery_job(
        self,
        *,
        subscription_id: str,
        analysis_id: str,
    ) -> str:
        """
        Kick off the delivery job for a Tier 3 purchase.

        Returns an opaque deliverableId that the client can poll via
        GET /v1/scans/{scan_id}/deliverable.

        Phase 1: returns a placeholder id synchronously.
        Phase 2: call Azure Container Apps Jobs API, return job run id.
        """
        # TODO (Phase 2): invoke Container Apps delivery job via ARM REST API
        # and persist the run id to Cosmos deliverables container.
        return f"deliv::{subscription_id[:8]}::{analysis_id[:8]}"
