# EVA-STORY: ACA-04-013
"""Reports router -- return tier-gated findings"""
from fastapi import APIRouter, HTTPException, Request
from ..auth.session import extract_subscription_id

router = APIRouter(tags=["reports"])


@router.get("/tier1", summary="Tier 1 findings report")
async def reports_tier1(request: Request, scan_id: str):
    """
    Return tier-gated findings (title, category, savings only).
    Story ACA-04-013
    """
    # Stub: use mock subscription_id if not provided
    subscription_id = extract_subscription_id(request) or "00000000-0000-0000-0000-000000000001"
    
    if not scan_id:
        raise HTTPException(status_code=400, detail="scanId required")
    
    # Stub: return 3 hardcoded findings (tier-gated)
    findings = [
        {
            "id": "finding-001",
            "title": "Dev Box instances run nights and weekends",
            "category": "compute-scheduling",
            "estimatedSavingLow": 5548,
            "estimatedSavingHigh": 7902,
            "effortClass": "trivial",
        },
        {
            "id": "finding-002",
            "title": "Storage account access tiers suboptimal",
            "category": "storage-access-tiers",
            "estimatedSavingLow": 1200,
            "estimatedSavingHigh": 2800,
            "effortClass": "easy",
        },
        {
            "id": "finding-003",
            "title": "Azure Disk redundancy overprovisioned",
            "category": "storage-redundancy",
            "estimatedSavingLow": 1000,
            "estimatedSavingHigh": 2000,
            "effortClass": "medium",
        },
    ]
    
    return {
        "scanId": scan_id,
        "tier": "TIER1",
        "findings": findings,
        "totalFindings": len(findings),
        "totalSavingRange": {
            "low": sum(f["estimatedSavingLow"] for f in findings),
            "high": sum(f["estimatedSavingHigh"] for f in findings),
        },
    }
