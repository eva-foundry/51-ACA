# EVA-STORY: ACA-SCAN_ID-001
"""
Findings router -- retrieve scan findings with tier gating.

CRITICAL: gate_findings() must strip implementation details for Tier 1.
Never return narrative or deliverable_template_id to Tier 1 clients.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["findings"])

TIER1_FIELDS = {
    "id", "category", "title",
    "estimated_saving_low", "estimated_saving_high",
    "effort_class", "risk_class",
}

TIER2_FIELDS = TIER1_FIELDS | {"narrative", "heuristic_source"}
# Tier 3: all fields including deliverable_template_id


def gate_findings(findings: list[dict], tier: str) -> list[dict]:
    """
    Strip findings to tier-appropriate fields.
    NEVER expose narrative or deliverable_template_id to Tier 1.
    """
    if tier == "tier1":
        return [{k: v for k, v in f.items() if k in TIER1_FIELDS} for f in findings]
    if tier == "tier2":
        return [{k: v for k, v in f.items() if k in TIER2_FIELDS} for f in findings]
    return findings  # tier3: full object


@router.get("/{scan_id}", summary="Get findings for a completed scan")
async def get_findings(scan_id: str, subscription_id: str):
    """
    Returns findings for a completed scan, gated by client tier.
    Tier 1: title + savings range only.
    Tier 2: full narrative.
    Tier 3: full + deliverable_template_id.
    """
    # TODO: load scan from Cosmos, check scan.status == "complete"
    # TODO: load client tier from Cosmos clients container
    # TODO: load findings from Cosmos findings container (partition_key=subscription_id)
    # TODO: return gate_findings(findings, client_tier)
    raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found or not complete")
