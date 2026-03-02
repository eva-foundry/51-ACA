# EVA-STORY: ACA-04-011
# EVA-STORY: ACA-04-012
"""Collect router -- trigger and poll Azure resource collection"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from ..auth.session import extract_subscription_id

router = APIRouter(tags=["collect"])


class CollectStartRequest(BaseModel):
    subscription_id: str = None
    scan_name: str = "default-scan"
    description: str = ""


@router.post("/start", summary="Trigger collection run")
async def collect_start(request: Request, body: CollectStartRequest):
    """
    Trigger Azure resource inventory collection.
    Story ACA-04-011
    """
    subscription_id = body.subscription_id or extract_subscription_id(request)
    
    if not subscription_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    scan_id = f"scan-{subscription_id[:8]}-{datetime.utcnow().strftime('%Y%m%d-%H%M')}"
    
    return {
        "scanId": scan_id,
        "status": "running",
        "startedAt": datetime.utcnow().isoformat() + "Z",
        "estimatedCompletionAt": (datetime.utcnow() + timedelta(minutes=12)).isoformat() + "Z",
        "subscriptionId": subscription_id,
    }


@router.get("/status", summary="Poll collection progress")
async def collect_status(request: Request, scan_id: str):
    """
    Poll scan progress (inventory collection + analysis).
    Story ACA-04-012
    """
    # Stub: use mock subscription_id if not provided
    subscription_id = extract_subscription_id(request) or "00000000-0000-0000-0000-000000000001"
    
    if not scan_id:
        raise HTTPException(status_code=400, detail="scanId required")
    
    # Stub: return completed status
    return {
        "scanId": scan_id,
        "status": "completed",
        "progress": 100,
        "startedAt": datetime.utcnow().isoformat() + "Z",
        "completedAt": datetime.utcnow().isoformat() + "Z",
        "inventoryCount": 487,
        "analysisCount": 12,
    }
