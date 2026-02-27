# EVA-STORY: ACA-04-013
"""
Findings router -- retrieve scan findings with tier gating.

CRITICAL: gate_findings() must strip implementation details for Tier 1.
Never return narrative or deliverable_template_id to Tier 1 clients.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.db.cosmos import get_item, query_items
from app.settings import get_settings
from app.services.findings_gate import gate_findings, TIER1_FIELDS, TIER2_FIELDS  # noqa: F401

router = APIRouter(tags=["findings"])

@router.get("/{scan_id}", summary="Get findings for a completed scan")
async def get_findings(scan_id: str, subscription_id: str):
    """
    Returns findings for a completed scan, gated by client tier.
    Tier 1: title + savings range only.
    Tier 2: full narrative.
    Tier 3: full + deliverable_template_id.
    """
    # Load scan from Cosmos
    scan = get_item("scans", scan_id, partition_key=subscription_id)
    if not scan or scan.get("status") != "complete":
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found or not complete")

    # Load client tier from Cosmos
    client = get_item("clients", subscription_id, partition_key=subscription_id)
    tier = client.get("tier", "tier1") if client else "tier1"

    # Load findings from Cosmos
    raw_findings = query_items(
        "findings",
        "SELECT * FROM c WHERE c.scanId = @s",
        [{"name": "@s", "value": scan_id}],
        partition_key=subscription_id,
    )

    # Return gated findings
    return gate_findings(raw_findings, tier)
