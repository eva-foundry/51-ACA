# EVA-STORY: ACA-04-004
# EVA-STORY: ACA-04-001
# EVA-STORY: ACA-04-006
# EVA-STORY: ACA-04-008
# EVA-STORY: ACA-05-001
"""
Auth router -- ACA client sign-in and Azure subscription connection.
Onboarding modes: delegated (device code) and service principal.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.token_service import TokenService
from app.db.repos.clients_repo import ClientsRepo

router = APIRouter(tags=["auth"])


class ConnectRequest(BaseModel):
    subscription_id: str
    connection_mode: str  # "delegated" | "service_principal"
    # delegated: provide device-code flow (returns device_code + verification_uri)
    # service_principal: provide client_id + client_secret + tenant_id


class PreflightResponse(BaseModel):
    preflight_id: str
    subscription_id: str
    verdict: str  # PASS | PASS_WITH_WARNINGS | FAIL
    warnings: list[str] = []
    blockers: list[str] = []


@router.post("/connect", summary="Initiate Azure subscription connection")
async def connect_subscription(req: ConnectRequest):
    """
    Step 1: Client initiates connection to their Azure subscription.
    Delegated mode: returns device_code + verification_uri for device-code flow.
    SP mode: not yet implemented (Sprint-03).
    See 02-preflight.md for full spec.
    """
    if req.connection_mode == "service_principal":
        raise HTTPException(
            status_code=501,
            detail="[INFO] SP mode not yet implemented -- coming in Sprint-03",
        )

    svc = TokenService()
    repo = ClientsRepo()

    try:
        flow = svc.initiate_device_code(req.subscription_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    repo.upsert(
        subscription_id=req.subscription_id,
        auth_mode="delegated",
        status="pending",
    )

    return {**flow, "subscription_id": req.subscription_id}


@router.post("/preflight", response_model=PreflightResponse, summary="Validate Azure permissions")
async def preflight(subscription_id: str):
    """
    Step 2: Run pre-flight permission checks before collection.
    Probes: Reader, Cost Management Reader, Advisor, Policy, Network.
    Returns PASS/FAIL per capability. See 02-preflight.md for full spec.
    """
    # TODO: implement preflight probes from services/collector/app/preflight.py
    raise HTTPException(status_code=501, detail="[INFO] Not yet implemented -- see 02-preflight.md")


@router.post("/disconnect", summary="Revoke subscription connection")
async def disconnect(subscription_id: str):
    """Remove connection and delete refresh token from Key Vault."""
    # TODO: revoke token, delete KV secret, mark connection as disconnected in Cosmos
    raise HTTPException(status_code=501, detail="[INFO] Not yet implemented")
