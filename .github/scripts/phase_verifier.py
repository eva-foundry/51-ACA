#!/usr/bin/env python3
# EVA-STORY: ACA-14-003
# phase_verifier.py -- Phase verification checkpoints for DPDCA workflow
#
# Per Opus recommendation (Risk #1, moved from Phase 4 to Phase 1):
# "Include phase verification checkpoints in Phase 1 because multi-agent handoffs
#  (Phase 3) are dangerous without per-phase assertion guards."
#
# 5 Checkpoint Functions (one per DPDCA phase):
#   D1 (Discover): Check evidence files exist
#   D2 (Discover-repo): Check test count > 0
#   P (Plan): Check PLAN.md updated with [x] marks
#   D3 (Do-execute): Check story selection manifest exists
#   A (Act): Check manifest JSON is valid
#
# Usage:
#   if not verify_d1_evidence(sprint_id, 6):
#       sys.exit(1)  # fail hard, no retry

import json
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def verify_d1_evidence(sprint_id: str, expected_count: int = 6, 
                      repo_root: Optional[str] = None) -> bool:
    """
    Verify Phase D1 (Discover) evidence: check evidence files exist.
    
    Args:
        sprint_id: "SPRINT-11" format
        expected_count: Expected minimum count of evidence receipts
        repo_root: Project root (defaults to current directory)
    
    Returns:
        True if verification passed, False otherwise
    """
    repo_root = Path(repo_root) if repo_root else Path.cwd()
    evidence_dir = repo_root / ".eva" / "evidence"
    
    if not evidence_dir.exists():
        print(f"[FAIL] D1 verification: evidence directory not found at {evidence_dir}")
        return False
    
    evidence_files = list(evidence_dir.glob("*.json"))
    if len(evidence_files) < expected_count:
        print(f"[FAIL] D1 verification: expected {expected_count} evidence files, found {len(evidence_files)}")
        return False
    
    print(f"[PASS] D1 verification: found {len(evidence_files)} evidence receipts")
    return True


def verify_d2_repo_audit(sprint_id: str, repo_root: Optional[str] = None) -> bool:
    """
    Verify Phase D2 (Discover-repo) audit: check pytest test count > 0.
    
    Runs: pytest --collect-only -q
    
    Args:
        sprint_id: "SPRINT-11" format
        repo_root: Project root (defaults to current directory)
    
    Returns:
        True if test count > 0, False otherwise
    """
    repo_root = Path(repo_root) if repo_root else Path.cwd()
    
    try:
        result = subprocess.run(
            ["pytest", "--collect-only", "-q"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse pytest output: "12 tests collected" or similar
        match = re.search(r"(\d+)\s+test", result.stdout)
        if not match:
            print(f"[FAIL] D2 verification: could not parse pytest output")
            return False
        
        test_count = int(match.group(1))
        if test_count == 0:
            print(f"[FAIL] D2 verification: no tests collected")
            return False
        
        print(f"[PASS] D2 verification: {test_count} tests collected")
        return True
    
    except subprocess.TimeoutExpired:
        print(f"[FAIL] D2 verification: pytest timeout (>30s)")
        return False
    except Exception as exc:
        print(f"[FAIL] D2 verification: {exc}")
        return False


def verify_p_plan_update(sprint_id: str, expected_checked: int = 4, 
                        repo_root: Optional[str] = None) -> bool:
    """
    Verify Phase P (Plan) update: check PLAN.md has [x] marks for completed items.
    
    Args:
        sprint_id: "SPRINT-11" format
        expected_checked: Expected minimum count of [x] checkboxes
        repo_root: Project root (defaults to current directory)
    
    Returns:
        True if verification passed, False otherwise
    """
    repo_root = Path(repo_root) if repo_root else Path.cwd()
    plan_file = repo_root / "PLAN.md"
    
    if not plan_file.exists():
        print(f"[FAIL] P verification: PLAN.md not found at {plan_file}")
        return False
    
    content = plan_file.read_text(encoding="utf-8")
    checked_count = len(re.findall(r"\[x\]", content))
    
    if checked_count < expected_checked:
        print(f"[FAIL] P verification: expected {expected_checked} [x] marks, found {checked_count}")
        return False
    
    print(f"[PASS] P verification: found {checked_count} completed items in PLAN.md")
    return True


def verify_d3_story_selection(sprint_id: str, repo_root: Optional[str] = None) -> bool:
    """
    Verify Phase D3 (Do-execute) story selection: check manifest file exists.
    
    Args:
        sprint_id: "SPRINT-11" format
        repo_root: Project root (defaults to current directory)
    
    Returns:
        True if manifest file found, False otherwise
    """
    repo_root = Path(repo_root) if repo_root else Path.cwd()
    
    # Check for sprint manifest (could be in docs/ or .github/sprints/)
    manifest_locations = [
        repo_root / "docs" / f"{sprint_id}-MANIFEST.md",
        repo_root / ".github" / "sprints" / f"{sprint_id.lower()}-manifest.md",
    ]
    
    for manifest_path in manifest_locations:
        if manifest_path.exists():
            print(f"[PASS] D3 verification: manifest found at {manifest_path}")
            return True
    
    print(f"[FAIL] D3 verification: manifest not found in {[str(p) for p in manifest_locations]}")
    return False


def verify_a_manifest_creation(sprint_id: str, repo_root: Optional[str] = None) -> Tuple[bool, Optional[dict]]:
    """
    Verify Phase A (Act) manifest creation: check SPRINT_MANIFEST JSON is valid.
    
    Args:
        sprint_id: "SPRINT-11" format
        repo_root: Project root (defaults to current directory)
    
    Returns:
        Tuple of (success: bool, manifest_data: dict or None)
    """
    repo_root = Path(repo_root) if repo_root else Path.cwd()
    
    # Look for SPRINT_MANIFEST JSON in .eva/sprints/ or docs/
    manifest_locations = [
        repo_root / ".eva" / "sprints" / f"{sprint_id.lower()}-manifest.json",
        repo_root / "docs" / f"{sprint_id}-manifest.json",
    ]
    
    for manifest_path in manifest_locations:
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest_data = json.load(f)
                
                # Validate required fields
                required_fields = ["sprint_id", "stories", "lm_summary"]
                missing = [f for f in required_fields if f not in manifest_data]
                
                if missing:
                    print(f"[FAIL] A verification: manifest missing fields {missing}")
                    return False, None
                
                print(f"[PASS] A verification: manifest valid ({len(manifest_data.get('stories', []))} stories)")
                return True, manifest_data
            
            except json.JSONDecodeError as e:
                print(f"[FAIL] A verification: manifest JSON invalid: {e}")
                return False, None
            except Exception as exc:
                print(f"[FAIL] A verification: {exc}")
                return False, None
    
    print(f"[FAIL] A verification: manifest not found in {[str(p) for p in manifest_locations]}")
    return False, None


class PhaseVerificationError(Exception):
    """Raised when a phase verification checkpoint fails."""
    def __init__(self, phase: str, reason: str):
        self.phase = phase
        self.reason = reason
        super().__init__(f"Phase {phase} verification failed: {reason}")


def verify_phase(phase: str, sprint_id: str, skip_checkpoints: bool = False,
                repo_root: Optional[str] = None) -> bool:
    """
    Master verification function for a DPDCA phase.
    
    Args:
        phase: "D1", "D2", "P", "D3", "A"
        sprint_id: "SPRINT-11" format
        skip_checkpoints: If True, skip verification and return True
        repo_root: Project root
    
    Returns:
        True if verification passed or skipped, False if failed
    
    Raises:
        PhaseVerificationError on failure (unless skip_checkpoints=True)
    """
    if skip_checkpoints:
        print(f"[WARN] Phase {phase} verification skipped (--skip-checkpoint override)")
        return True
    
    try:
        if phase == "D1":
            return verify_d1_evidence(sprint_id, repo_root=repo_root)
        elif phase == "D2":
            return verify_d2_repo_audit(sprint_id, repo_root=repo_root)
        elif phase == "P":
            return verify_p_plan_update(sprint_id, repo_root=repo_root)
        elif phase == "D3":
            return verify_d3_story_selection(sprint_id, repo_root=repo_root)
        elif phase == "A":
            success, _ = verify_a_manifest_creation(sprint_id, repo_root=repo_root)
            return success
        else:
            print(f"[FAIL] Unknown phase: {phase}")
            return False
    
    except PhaseVerificationError as e:
        print(f"[FAIL] {e}")
        raise


if __name__ == "__main__":
    # Example usage
    print("Testing phase verification functions...")
    
    # These will fail on a fresh checkout (no evidence/PLAN marks yet)
    # but demonstrate the verification API
    
    result_d1 = verify_d1_evidence("SPRINT-11", expected_count=1)
    print(f"D1 result: {result_d1}\n")
    
    result_d3 = verify_d3_story_selection("SPRINT-11")
    print(f"D3 result: {result_d3}\n")
    
    print("[INFO] Phase verification functions operational")
