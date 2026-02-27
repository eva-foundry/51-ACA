# EVA-STORY: ACA-SCANS-001
# EVA-STORY: ACA-SCAN_ID-002
# EVA-STORY: ACA-API-001
# EVA-STORY: ACA-API-002
"""
Scans router -- trigger and monitor collection + analysis jobs.
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel

from app.scan_pipeline import ScanPipeline, ScanStateError
from tools.observability import log_event, trace_operation

logger = logging.getLogger(__name__)
router = APIRouter(tags=["scans"])

_pipeline = ScanPipeline()
_executor = ThreadPoolExecutor(max_workers=4)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    subscription_id: str


class ScanStatus(BaseModel):
    scan_id: str
    subscription_id: str
    status: str  # queued | collecting | collected | analysing | complete | delivered | failed
    created_utc: str
    updated_utc: str
    error: str | None = None
    row_version: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_status(record) -> ScanStatus:
    d = record.as_dict()
    return ScanStatus(
        scan_id=record.scan_id,
        subscription_id=record.subscription_id,
        status=record.status,
        created_utc=d.get("created_utc", ""),
        updated_utc=d.get("updated_utc", ""),
        error=record.error,
        row_version=record.row_version,
    )


async def _run_sync(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, fn, *args)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/", response_model=ScanStatus, summary="Trigger a new scan")
async def trigger_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """
    Create a scan record (status=queued), then fire the collector job in the background.
    Returns scan_id immediately -- poll GET /v1/scans/{scan_id} for status.
    """
    with trace_operation("scans.trigger", {"subscription_id": req.subscription_id}):
        record = await _run_sync(_pipeline.create_scan, req.subscription_id)
        background_tasks.add_task(
            _pipeline.trigger_pipeline, record.scan_id, record.subscription_id
        )
        log_event("scan_triggered", {
            "scan_id": record.scan_id,
            "subscription_id": req.subscription_id,
        })
    return _to_status(record)


@router.get("/{scan_id}", response_model=ScanStatus, summary="Get scan status")
async def get_scan_status(scan_id: str, subscription_id: str = Query(...)):
    """
    Poll scan status. subscription_id required as query param (partition key).
    Recommended polling interval: every 15s.
    """
    record = await _run_sync(_pipeline.get_scan, scan_id, subscription_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id!r} not found")
    return _to_status(record)


@router.post("/{scan_id}/advance", summary="Advance scan state (job callback)")
async def advance_scan_state(
    scan_id: str,
    subscription_id: str = Query(...),
    new_status: str = Query(...),
    error: str | None = Query(default=None),
):
    """
    Internal: called by collector/analysis/delivery Container App Jobs to
    report state transitions. Returns 409 on invalid FSM transition.
    """
    try:
        record = await _run_sync(
            lambda: _pipeline.advance_scan(scan_id, subscription_id, new_status, error=error)
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ScanStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    log_event("scan_state_advanced", {
        "scan_id": scan_id,
        "new_status": new_status,
    })
    return _to_status(record)


@router.get("/", summary="List scans for a subscription")
async def list_scans(
    subscription_id: str = Query(...),
    limit: int = Query(default=10, ge=1, le=100),
):
    """List most recent scans for a subscription (descending by created_utc)."""
    records = await _run_sync(_pipeline.list_scans, subscription_id, limit)
    return [_to_status(r) for r in records]
