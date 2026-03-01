#!/usr/bin/env python3
# EVA-STORY: ACA-14-002
# state_lock.py -- Idempotency guard: prevent duplicate sprint dispatch
#
# Per Opus recommendation (Risk #2, highest priority mitigation):
# "Add state lock mechanism (10 lines of code) that prevents the most dangerous
#  failure mode: duplicate sprint dispatch from network retry or user re-trigger."
#
# Lock file format (.eva/locks/{sprint_id}.lock):
# {
#   "sprint_id": "SPRINT-11",
#   "workflow_run_id": "12345",
#   "correlation_id": "ACA-S11-20260301-a1b2c3d4",
#   "started_at": "2026-03-01T22:38:44.937588+00:00Z",
#   "locked_by": "github-actions"
# }
#
# Usage:
#   if acquire_lock('SPRINT-11', run_id, correlation_id):
#       try:
#           # execute sprint
#       finally:
#           release_lock('SPRINT-11')
#   else:
#       print('[FAIL] Sprint already in progress (lock exists)')
#       sys.exit(1)

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def acquire_lock(sprint_id: str, workflow_run_id: str, correlation_id: str, 
                 repo_root: Optional[str] = None) -> bool:
    """
    Acquire an exclusive lock for a sprint (idempotency guard).
    
    Returns True if lock acquired, False if another process holds it.
    
    Args:
        sprint_id: "SPRINT-11" format
        workflow_run_id: GitHub Actions workflow run ID (or similar unique ID)
        correlation_id: Full correlation ID for tracing
        repo_root: Path to project root (defaults to current directory)
    
    Returns:
        True if lock acquired, False if already locked
    """
    locks_dir = Path(repo_root) if repo_root else Path.cwd()
    locks_dir = locks_dir / ".eva" / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    
    lock_file = locks_dir / f"{sprint_id}.lock"
    
    # Check if lock already exists
    if lock_file.exists():
        print(f"[WARN] Lock already held for {sprint_id}")
        return False
    
    # Create lock file atomically (exclusive creation, fail if exists)
    lock_data = {
        "sprint_id": sprint_id,
        "workflow_run_id": workflow_run_id,
        "correlation_id": correlation_id,
        "started_at": datetime.now(timezone.utc).isoformat() + "Z",
        "locked_by": os.environ.get("GITHUB_ACTOR", "local-user")
    }
    
    try:
        # O_EXCL ensures atomic creation -- fails if file exists
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        with os.fdopen(fd, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        print(f"[INFO] Lock acquired: {lock_file}")
        return True
    
    except FileExistsError:
        print(f"[WARN] Lock already held for {sprint_id} (concurrent execution detected)")
        return False
    except Exception as exc:
        print(f"[FAIL] Could not acquire lock: {exc}")
        return False


def release_lock(sprint_id: str, repo_root: Optional[str] = None) -> bool:
    """
    Release a lock and return True if successful, False if lock was not held.
    
    Args:
        sprint_id: "SPRINT-11" format
        repo_root: Path to project root (defaults to current directory)
    
    Returns:
        True if lock was released, False if lock didn't exist
    """
    locks_dir = Path(repo_root) if repo_root else Path.cwd()
    lock_file = locks_dir / ".eva" / "locks" / f"{sprint_id}.lock"
    
    if not lock_file.exists():
        print(f"[WARN] Lock not held for {sprint_id}")
        return False
    
    try:
        lock_file.unlink()
        print(f"[INFO] Lock released: {lock_file}")
        return True
    except Exception as exc:
        print(f"[FAIL] Could not release lock: {exc}")
        return False


def get_lock_status(sprint_id: str, repo_root: Optional[str] = None) -> Optional[dict]:
    """
    Get current lock status (None if not locked, dict if locked).
    
    Returns:
        Dict with lock metadata if locked, None if not locked
    """
    locks_dir = Path(repo_root) if repo_root else Path.cwd()
    lock_file = locks_dir / ".eva" / "locks" / f"{sprint_id}.lock"
    
    if not lock_file.exists():
        return None
    
    try:
        with open(lock_file) as f:
            return json.load(f)
    except Exception:
        return None


if __name__ == "__main__":
    # Example usage
    
    # Test acquire_lock
    acquired = acquire_lock("SPRINT-11", "12345", "ACA-S11-20260301-a1b2c3d4")
    print(f"[TEST] acquire_lock returned: {acquired}")
    
    # Check lock status
    status = get_lock_status("SPRINT-11")
    print(f"[TEST] Lock status: {json.dumps(status, indent=2)}")
    
    # Try to acquire again (should fail)
    acquired2 = acquire_lock("SPRINT-11", "67890", "ACA-S11-20260301-xyz")
    print(f"[TEST] Second acquire_lock returned (should be False): {acquired2}")
    
    # Release lock
    released = release_lock("SPRINT-11")
    print(f"[TEST] release_lock returned: {released}")
    
    # Check lock status again (should be None)
    status2 = get_lock_status("SPRINT-11")
    print(f"[TEST] Lock status after release (should be None): {status2}")
    
    # Cleanup
    import shutil
    if Path(".eva/locks").exists():
        shutil.rmtree(".eva/locks")
        print("[TEST] Cleaned up .eva/locks/")
