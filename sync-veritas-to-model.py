#!/usr/bin/env python3
"""
Sync veritas audit results to data model.
"""
import json
import sys
import httpx
from pathlib import Path

# Veritas findings from audit
VERITAS_AUDIT = {
    "project_id": "51-ACA",
    "trust_score": 69,
    "consistency_score": 0.0,
    "stories_total": 268,
    "stories_with_artifacts": 268,
    "stories_with_evidence": 260,
    "gaps": 4,
    "orphan_tags": ["ACA-", "ACA-XX-XXX", "ACA-12-023", "ACA-NN-NNN"],
}

# Try ACA endpoint first (24x7), fallback to local
ENDPOINTS = [
    "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io",
    "http://localhost:8010",
]

def get_base():
    """Find a working model endpoint."""
    for base in ENDPOINTS:
        try:
            r = httpx.get(f"{base}/health", timeout=5)
            if r.status_code == 200:
                print(f"[OK] Using model at {base}")
                return base
        except:
            pass
    raise RuntimeError("No model endpoint available")

def main():
    base = get_base()
    
    # Query current project state
    print(f"[INFO] Querying current project state...")
    try:
        proj = httpx.get(f"{base}/model/projects/51-ACA", timeout=10).json()
        print(f"[OK] Found project: {proj.get('id')} | Maturity: {proj.get('maturity')}")
    except:
        print("[WARN] Project not found, will create")
        proj = {"id": "51-ACA", "label": "ACA -- Evidence-Driven Cloud Agent", "maturity": "active"}
    
    # Update metrics
    proj["metrics"] = {
        "veritas_trust_score": VERITAS_AUDIT["trust_score"],
        "veritas_consistency_score": VERITAS_AUDIT["consistency_score"],
        "stories_total": VERITAS_AUDIT["stories_total"],
        "stories_with_artifacts": VERITAS_AUDIT["stories_with_artifacts"],
        "stories_with_evidence": VERITAS_AUDIT["stories_with_evidence"],
        "orphan_story_count": VERITAS_AUDIT["gaps"],
    }
    
    if "row_version" not in proj:
        proj["row_version"] = 1
    
    # Strip audit columns
    for col in ["layer", "modified_by", "modified_at", "created_by", "created_at", "source_file"]:
        proj.pop(col, None)
    
    # PUT to model
    print(f"[INFO] Updating project metrics...")
    prev_rv = proj.get("row_version", 0)
    response = httpx.put(
        f"{base}/model/projects/51-ACA",
        json=proj,
        headers={"X-Actor": "agent:copilot", "Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"[OK] Project updated | row_version: {prev_rv} -> {result.get('row_version')}")
        print(f"[OK] Metrics synchronized:")
        print(f"     - Trust Score: {VERITAS_AUDIT['trust_score']}")
        print(f"     - Stories: {VERITAS_AUDIT['stories_total']} total, {VERITAS_AUDIT['stories_with_evidence']} with evidence")
        print(f"     - Orphan tags to fix: {VERITAS_AUDIT['gaps']}")
    else:
        print(f"[FAIL] PUT failed: {response.status_code} - {response.text}")
        sys.exit(1)
    
    # Query WBS to see if there are consistency issues
    print(f"\n[INFO] Checking WBS inconsistencies...")
    try:
        wbs = httpx.get(f"{base}/model/wbs?project=51-ACA", timeout=10).json()
        print(f"[INFO] WBS has {len(wbs)} items")
        
        # Look for orphan items
        orphan_count = 0
        for item in wbs:
            if item.get("id") in VERITAS_AUDIT["orphan_tags"]:
                print(f"[WARN] Orphan WBS item: {item.get('id')}")
                orphan_count += 1
        
        if orphan_count > 0:
            print(f"[WARN] Found {orphan_count} orphan WBS items - review PLAN.md")
    except Exception as e:
        print(f"[WARN] Could not query WBS: {e}")
    
    print(f"\n[OK] Sync complete!")
    print(f"[NEXT] Review PLAN.md for orphan story IDs (ACA-, ACA-XX-XXX, ACA-12-023, ACA-NN-NNN)")
    print(f"[NEXT] Run: pytest services/ -x -q to validate codebase")

if __name__ == "__main__":
    main()
