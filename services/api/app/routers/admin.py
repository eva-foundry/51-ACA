# EVA-STORY: ACA-STATS-001
"""
Admin router -- internal ops. Not exposed publicly via APIM.

Endpoints (all require Bearer token; roles enforced by APIM or calling layer):
  GET  /kpis                         -- AdminKpis DTO
  GET  /customers                    -- search by query param
  POST /entitlements/grant           -- grant tier override, writes audit event
  POST /subscriptions/{id}/lock      -- lock subscription, writes audit event
  POST /stripe/reconcile             -- enqueue reconcile job, writes audit event
  GET  /runs                         -- run history with type + subscriptionId filters

Legacy (kept for backward compat):
  GET  /stats
  DELETE /scans/{scan_id}
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.db.cosmos import upsert_item, query_items, get_container

router = APIRouter(tags=["admin"])
security = HTTPBearer()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AdminKpis(BaseModel):
    mrrCad: float
    activeSubscriptions: int
    scansLast24h: int
    failureRatePctLast24h: float


class AdminCustomerRow(BaseModel):
    subscriptionId: str
    tier: int
    paymentStatus: str
    isLocked: bool
    lastActivityUtc: Optional[str] = None


class AdminCustomerSearchResponse(BaseModel):
    items: list[AdminCustomerRow]
    total: int


class AdminGrantEntitlementRequest(BaseModel):
    subscriptionId: str
    tier: int
    durationDays: int
    reason: str


class AdminLockRequest(BaseModel):
    reason: str


class AdminJobAccepted(BaseModel):
    jobId: str
    status: str = "queued"


class AdminRunRecord(BaseModel):
    runId: str
    subscriptionId: str
    type: str
    status: str
    durationMs: Optional[int] = None
    correlationId: Optional[str] = None


class AdminRunsResponse(BaseModel):
    items: list[AdminRunRecord]
    total: int


# ---------------------------------------------------------------------------
# Audit helper
# ---------------------------------------------------------------------------

def _write_audit(action: str, payload: dict, actor: str = "admin") -> None:
    """Write an admin_audit_events record. Non-blocking best-effort."""
    try:
        event_id = f"aae::{uuid.uuid4()}"
        subscription_id = payload.get("subscriptionId", "system")
        upsert_item(
            "admin_audit_events",
            {
                "id": event_id,
                "subscriptionId": subscription_id,
                "action": action,
                "actor": actor,
                "payload": payload,
                "timestampUtc": datetime.now(timezone.utc).isoformat(),
            },
        )
    except Exception:  # noqa: BLE001
        pass  # Audit write failure must never block the primary operation


# ---------------------------------------------------------------------------
# New admin endpoints
# ---------------------------------------------------------------------------

@router.get("/kpis", response_model=AdminKpis, summary="KPI overview")
async def get_kpis(creds: HTTPAuthorizationCredentials = Depends(security)):
    """Return aggregate KPIs. Reads entitlements + scans containers."""
    # TODO: implement real aggregation queries against Cosmos
    return AdminKpis(
        mrrCad=0.0,
        activeSubscriptions=0,
        scansLast24h=0,
        failureRatePctLast24h=0.0,
    )


@router.get("/customers", response_model=AdminCustomerSearchResponse, summary="Search customers")
async def search_customers(
    query: str = Query(default="", description="Filter by subscriptionId, UPN, or tier"),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """Search across entitlements container. Cross-partition (admin-only)."""
    # TODO: implement cross-partition query against entitlements container
    return AdminCustomerSearchResponse(items=[], total=0)


@router.post(
    "/entitlements/grant",
    status_code=202,
    summary="Grant entitlement override",
)
async def grant_entitlement(
    req: AdminGrantEntitlementRequest,
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Override entitlement for a subscription (support + admin use).
    Writes an ENTITLEMENT_GRANTED audit event.
    """
    # TODO: upsert entitlement doc in entitlements container
    _write_audit(
        action="ENTITLEMENT_GRANTED",
        payload=req.model_dump(),
    )
    return {"subscriptionId": req.subscriptionId, "tier": req.tier, "status": "granted"}


@router.post(
    "/subscriptions/{subscription_id}/lock",
    status_code=200,
    summary="Lock a subscription",
)
async def lock_subscription(
    subscription_id: str,
    req: AdminLockRequest,
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Set isLocked=true on the entitlement record.
    Writes a SUBSCRIPTION_LOCKED audit event.
    """
    # TODO: update entitlement record isLocked field
    _write_audit(
        action="SUBSCRIPTION_LOCKED",
        payload={"subscriptionId": subscription_id, "reason": req.reason},
    )
    return {"subscriptionId": subscription_id, "isLocked": True}


@router.post(
    "/stripe/reconcile",
    response_model=AdminJobAccepted,
    status_code=202,
    summary="Enqueue Stripe reconciliation job",
)
async def reconcile_stripe(creds: HTTPAuthorizationCredentials = Depends(security)):
    """
    Enqueues an async Stripe sync job. Admin-only.
    Writes a STRIPE_RECONCILE audit event.
    """
    job_id = str(uuid.uuid4())
    _write_audit(
        action="STRIPE_RECONCILE",
        payload={"jobId": job_id},
    )
    # TODO: enqueue job via Azure Storage Queue or Container Apps Job trigger
    return AdminJobAccepted(jobId=job_id)


@router.get("/runs", response_model=AdminRunsResponse, summary="Run history")
async def get_runs(
    type: Optional[str] = Query(default=None, description="Filter by run type: scan|analysis|delivery"),
    subscriptionId: Optional[str] = Query(default=None, description="Filter by subscription ID"),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Return run records from the scans container filtered by type and/or subscriptionId.
    Cross-partition when subscriptionId is not provided (admin-only).
    """
    # TODO: implement run history query
    return AdminRunsResponse(items=[], total=0)


# ---------------------------------------------------------------------------
# Legacy endpoints (kept for backward compat)
# ---------------------------------------------------------------------------

@router.get("/stats", summary="ACA stats: scans, clients, revenue (legacy)")
async def stats(creds: HTTPAuthorizationCredentials = Depends(security)):
    # TODO: aggregate from Cosmos
    return {"scans_total": 0, "clients_total": 0, "deliverables_generated": 0}


@router.delete("/scans/{scan_id}", summary="Delete scan and its data (legacy)")
async def delete_scan(
    scan_id: str,
    subscription_id: str,
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    # TODO: delete scan + related data from Cosmos (partition_key=subscription_id)
    return {"deleted": scan_id}
