from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_actor
from app.auth.rbac import Actor, require_admin, require_support_or_admin, require_finops_or_admin
from app.models.admin_dtos import (
    AdminKpisResponse, CustomerSearchResponse, CustomerDetailResponse, CustomerEntitlement,
    GrantEntitlementRequest, LockSubscriptionRequest, UnlockSubscriptionRequest,
    ReconcileStripeRequest, ReconcileStripeResponse, AdminRunsResponse, AdminAuditResponse
)
from app.services.admin_kpi_service import AdminKpiService
from app.services.admin_audit_service import AdminAuditService
from app.services.admin_run_service import AdminRunService
from app.services.entitlement_service import EntitlementService

router = APIRouter(prefix="/v1/admin", tags=["admin"])

@router.get("/kpis", response_model=AdminKpisResponse)
async def get_kpis(actor: Actor = Depends(get_actor)):
    require_finops_or_admin(actor)
    return await AdminKpiService().get_kpis()

@router.get("/customers", response_model=CustomerSearchResponse)
async def search_customers(query: str = Query(..., min_length=1), actor: Actor = Depends(get_actor)):
    require_support_or_admin(actor)
    # Production TODO: use AdminCustomerRepo search
    return CustomerSearchResponse(items=[])

@router.get("/customers/{subscriptionId}", response_model=CustomerDetailResponse)
async def get_customer(subscriptionId: str, actor: Actor = Depends(get_actor)):
    require_support_or_admin(actor)
    ent = await EntitlementService().get_entitlement(subscriptionId)
    return CustomerDetailResponse(
        entitlement=CustomerEntitlement(
            subscriptionId=subscriptionId,
            tier=ent.tier,
            paymentStatus=ent.payment_status,
            expiresUtc=getattr(ent, "expires_utc", None),
            locked=False,
        )
    )

@router.post("/entitlements/grant", response_model=CustomerEntitlement)
async def grant_entitlement(req: GrantEntitlementRequest, actor: Actor = Depends(get_actor)):
    require_support_or_admin(actor)
    svc = EntitlementService()
    if req.tier == 2:
        await svc.grant_tier2(req.subscriptionId, payment_status="active", source="admin_override")
    else:
        await svc.grant_tier3(req.subscriptionId, payment_status="active", source="admin_override")
    await AdminAuditService().record(actor=actor, action="entitlement.grant", subscription_id=req.subscriptionId, payload=req.model_dump())
    ent = await svc.get_entitlement(req.subscriptionId)
    return CustomerEntitlement(
        subscriptionId=req.subscriptionId,
        tier=ent.tier,
        paymentStatus=ent.payment_status,
        expiresUtc=getattr(ent, "expires_utc", None),
        locked=False,
    )

@router.post("/subscriptions/lock")
async def lock_subscription(req: LockSubscriptionRequest, actor: Actor = Depends(get_actor)):
    require_support_or_admin(actor)
    # Production TODO: persist lock flag in clients/subscriptions container.
    await AdminAuditService().record(actor=actor, action="subscription.lock", subscription_id=req.subscriptionId, payload=req.model_dump())
    return {"ok": True}

@router.post("/subscriptions/unlock")
async def unlock_subscription(req: UnlockSubscriptionRequest, actor: Actor = Depends(get_actor)):
    require_support_or_admin(actor)
    # Production TODO: persist lock flag in clients/subscriptions container.
    await AdminAuditService().record(actor=actor, action="subscription.unlock", subscription_id=req.subscriptionId, payload=req.model_dump())
    return {"ok": True}

@router.post("/reconcile/stripe", response_model=ReconcileStripeResponse)
async def reconcile_stripe(req: Optional[ReconcileStripeRequest] = None, actor: Actor = Depends(get_actor)):
    require_admin(actor)
    sid = req.subscriptionId if req else None
    # Production TODO: load Stripe customer/subscription state and repair entitlements.
    await AdminAuditService().record(actor=actor, action="stripe.reconcile", subscription_id=sid, payload={"subscriptionId": sid})
    return ReconcileStripeResponse(reconciled=0, updated=0, warnings=[])

@router.get("/runs", response_model=AdminRunsResponse)
async def list_runs(
    type: Literal["scan", "analysis", "delivery"] = Query(...),
    subscriptionId: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    actor: Actor = Depends(get_actor),
):
    require_support_or_admin(actor)
    return await AdminRunService().list_runs(
        run_type=type,
        subscription_id=subscriptionId,
        status=status,
        limit=limit,
    )

@router.get("/audit", response_model=AdminAuditResponse)
async def list_audit(
    subscriptionId: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    actor: Actor = Depends(get_actor),
):
    require_admin(actor)
    # Production TODO: list from AdminAuditRepo
    return AdminAuditResponse(items=[])
