# EVA-STORY: ACA-04-006
# EVA-STORY: ACA-04-004
# EVA-STORY: ACA-04-001
# EVA-STORY: ACA-05-001
"""
Auth router -- ACA client sign-in and Azure subscription connection.
Onboarding modes: delegated (device code) and service principal.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.token_service import TokenService

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
    Returns a device-code URL for delegated mode, or validates SP credentials.
    See 02-preflight.md for full spec.
    """
    if req.connection_mode == "delegated":
        token_service = TokenService()
        flow = token_service.initiate_device_code(req.subscription_id)
        return flow
    raise HTTPException(status_code=501, detail="[INFO] Service principal mode not yet implemented")


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
