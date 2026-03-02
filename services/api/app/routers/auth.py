# EVA-STORY: ACA-04-001
# EVA-STORY: ACA-04-003
# EVA-STORY: ACA-04-004
# EVA-STORY: ACA-04-005
# EVA-STORY: ACA-04-009
"""
Auth router -- Multi-tenant Azure subscription connection and preflight validation.
Modes: delegated (multi-tenant, any Microsoft account), service principal (future).
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from ..auth.msal_client import create_msal_app
from ..auth.session import set_subscription_context, extract_subscription_id
from ..auth.probes import run_all_probes

router = APIRouter(tags=["auth"])


class ConnectRequest(BaseModel):
    delegated_token: str
    desired_tier: str = "TIER1"


class PreflightResponse(BaseModel):
    passcode: str
    probes: list
    all_pass: bool
    run_at: str


@router.post("/connect", summary="Connect Azure subscription (delegated mode)")
async def connect_subscription(request: Request, body: ConnectRequest):
    """
    Connect Azure subscription via delegated token (multi-tenant mode).
    Body: { delegatedToken, desiredTier? }
    Returns: { subscriptionId, tier, connectedAt, status }
    Story ACA-04-004
    """
    token = body.delegated_token
    desired_tier = body.desired_tier
    
    if not token:
        raise HTTPException(status_code=400, detail="delegatedToken required")
    
    # Stub: extract subscriptionId from token claims (in production: decode JWT)
    subscription_id = "00000000-0000-0000-0000-000000000001"
    
    # Store in Cosmos clients container (stub: would create/upsert client record)
    client_record = {
        "subscriptionId": subscription_id,
        "tier": desired_tier,
        "connectedAt": datetime.utcnow().isoformat() + "Z",
    }
    
    # Store refresh token in Key Vault (stub: would call KV API)
    kv_secret_name = f"aca-connect-{subscription_id}"
    
    set_subscription_context(request, subscription_id, desired_tier)
    
    return {
        "subscriptionId": subscription_id,
        "tier": desired_tier,
        "connectedAt": client_record["connectedAt"],
        "status": "connected",
    }


@router.post("/disconnect", summary="Disconnect Azure subscription and revoke tokens")
async def disconnect_subscription(request: Request):
    """
    Disconnect Azure subscription, revoke all tokens, delete KV secrets.
    Requires: subscriptionId in request.state (from JWT middleware)
    Returns: { status, subscriptionId, revokedAt }
    Story ACA-04-005
    """
    subscription_id = extract_subscription_id(request)
    
    if not subscription_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Delete from Cosmos clients container (stub)
    # Delete from Key Vault (stub: would call KV delete API)
    
    return {
        "status": "disconnected",
        "subscriptionId": subscription_id,
        "revokedAt": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/preflight", response_model=PreflightResponse, summary="Run 5 validation probes")
async def run_preflight(request: Request):
    """
    Run 5 validation probes (RBAC, Cosmos, KV, Storage, AppInsights).
    Requires: Active Azure token
    Returns: { passcode, probes: [ { name, status, message } ], all_pass }
    Story ACA-04-009
    """
    subscription_id = extract_subscription_id(request)
    
    if not subscription_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Run probes (stub: all pass)
    result = await run_all_probes("dummy_token", subscription_id)
    
    return PreflightResponse(**result)


@router.get("/health", summary="Health check (unauthenticated)")
async def health_check():
    """
    Server-side health check. No auth required.
    Returns: { status, store, version }
    Story ACA-04-001
    """
    return {
        "status": "healthy",
        "store": "cosmos",
        "version": "1.0.0",
    }
