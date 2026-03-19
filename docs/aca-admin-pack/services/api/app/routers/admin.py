from typing import Literal
from fastapi import APIRouter, Query

router = APIRouter(prefix="/v1/admin", tags=["admin"])

@router.get("/kpis")
async def get_kpis():
    return {"revenueMtd": 0, "activeSubscriptions": 0, "scans24h": 0}

@router.get("/customers")
async def search_customers(query: str = Query(...)):
    return {"items": []}

@router.get("/customers/{subscriptionId}")
async def get_customer(subscriptionId: str):
    return {"subscriptionId": subscriptionId}

@router.post("/entitlements/grant")
async def grant_entitlement():
    return {"ok": True}

@router.post("/subscriptions/lock")
async def lock_subscription():
    return {"ok": True}

@router.post("/subscriptions/unlock")
async def unlock_subscription():
    return {"ok": True}

@router.post("/reconcile/stripe")
async def reconcile_stripe():
    return {"ok": True}

@router.get("/runs")
async def list_runs(type: Literal["scan","analysis","delivery"]):
    return {"items": []}

@router.get("/audit")
async def list_audit():
    return {"items": []}
