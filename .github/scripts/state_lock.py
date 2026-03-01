# EVA-STORY: ACA-14-002
import os
import json
import time

LOCK_DIR = ".eva/locks"
LOCK_FILE_TEMPLATE = "{lock_id}.lock"

# Ensure lock directory exists
def _ensure_lock_dir():
    if not os.path.exists(LOCK_DIR):
        os.makedirs(LOCK_DIR)

# Acquire lock
def acquire_lock(lock_id: str, workflow_run_id: str, correlation_id: str) -> bool:
    """
    Acquires a lock for the given lock_id.
    Returns True if lock acquired successfully, False if lock already exists.
    """
    _ensure_lock_dir()
    lock_file_path = os.path.join(LOCK_DIR, LOCK_FILE_TEMPLATE.format(lock_id=lock_id))

    if os.path.exists(lock_file_path):
        return False

    lock_data = {
        "lock_id": lock_id,
        "workflow_run_id": workflow_run_id,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "correlation_id": correlation_id,
        "locked_by": os.getenv("USER", "unknown")
    }

    with open(lock_file_path, "w") as lock_file:
        json.dump(lock_data, lock_file)

    return True

# Release lock
def release_lock(lock_id: str) -> None:
    """
    Releases the lock for the given lock_id.
    """
    lock_file_path = os.path.join(LOCK_DIR, LOCK_FILE_TEMPLATE.format(lock_id=lock_id))

    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)

# Example usage (for testing purposes only)
if __name__ == "__main__":
    lock_id = "SPRINT-11"
    workflow_run_id = "12345"
    correlation_id = "ACA-S11-001"

    if acquire_lock(lock_id, workflow_run_id, correlation_id):
        print("[PASS] Lock acquired successfully.")
        try:
            # Simulate workflow execution
            print("[INFO] Executing workflow...")
        finally:
            release_lock(lock_id)
            print("[INFO] Lock released.")
    else:
        print("[FAIL] Lock acquisition failed. Lock already exists.")
        exit(1)