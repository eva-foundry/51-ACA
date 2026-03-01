# EVA-STORY: ACA-14-003
import os
import json
from typing import Any

def verify_d1_evidence(sprint_id: str, expected_count: int) -> bool:
    evidence_dir = f".eva/evidence/{sprint_id}"
    if not os.path.exists(evidence_dir):
        print("[FAIL] Evidence directory does not exist")
        return False

    evidence_files = [f for f in os.listdir(evidence_dir) if f.endswith("-receipt.json")]
    if len(evidence_files) != expected_count:
        print(f"[FAIL] Expected {expected_count} evidence files, found {len(evidence_files)}")
        return False

    print("[PASS] Evidence verification successful")
    return True

def verify_d2_repo_audit(ctx: Any) -> bool:
    pytest_output = ctx.get("pytest_output", "")
    if "test_count" not in pytest_output or pytest_output["test_count"] <= 0:
        print("[FAIL] No tests executed in pytest")
        return False

    print("[PASS] Repo audit verification successful")
    return True

def verify_p_plan_update(ctx: Any, sprint_id: str, expected_marks: int) -> bool:
    plan_file = f"docs/PLAN-{sprint_id}.md"
    if not os.path.exists(plan_file):
        print("[FAIL] Plan file does not exist")
        return False

    with open(plan_file, "r") as f:
        content = f.read()

    completed_marks = content.count("[x]")
    if completed_marks != expected_marks:
        print(f"[FAIL] Expected {expected_marks} completed marks, found {completed_marks}")
        return False

    print("[PASS] Plan update verification successful")
    return True

def verify_d3_story_selection(ctx: Any, sprint_id: str) -> bool:
    manifest_file = f"docs/{sprint_id}-MANIFEST.md"
    if not os.path.exists(manifest_file):
        print("[FAIL] Manifest file does not exist")
        return False

    print("[PASS] Story selection verification successful")
    return True

def verify_a_manifest_creation(ctx: Any, sprint_id: str) -> bool:
    manifest_file = f"docs/{sprint_id}-MANIFEST.md"
    if not os.path.exists(manifest_file):
        print("[FAIL] Manifest creation failed")
        return False

    print("[PASS] Manifest creation verification successful")
    return True
