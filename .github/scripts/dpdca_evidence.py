"""
DPDCA Evidence Step -- writes or updates the evidence receipt.
Called by dpdca-agent.yml D2 and C steps.
Usage:
  python3 dpdca_evidence.py write        -- create receipt
  python3 dpdca_evidence.py update       -- add lint/test results
EVA-STORY: ACA-14-005
"""
import os
import sys
import json
import datetime


def today_str():
    return datetime.date.today().strftime("%Y%m%d")


def receipt_path(story_id):
    return f".eva/evidence/{story_id}-{today_str()}.json"


def cmd_write():
    story_id = os.environ.get("STORY_ID", "UNKNOWN")
    os.makedirs(".eva/evidence", exist_ok=True)
    path = receipt_path(story_id)
    ev = {
        "story_id": story_id,
        "wbs_id": os.environ.get("WBS_ID", "UNKNOWN"),
        "epic": os.environ.get("EPIC", "UNKNOWN"),
        "issue_number": os.environ.get("ISSUE_NUM", "0"),
        "branch": os.environ.get("BRANCH_NAME", ""),
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "status": "agent-scaffolded",
        "agent": "dpdca-agent",
        "model": "gpt-4o-mini",
        "lint_result": "pending",
        "test_result": "pending",
    }
    with open(path, "w") as f:
        json.dump(ev, f, indent=2)
    print(f"[INFO] Evidence receipt written: {path}")

    # copy plan alongside receipt
    if os.path.exists("agent-plan.md"):
        import shutil
        shutil.copy("agent-plan.md", f".eva/evidence/{story_id}-plan.md")
        print(f"[INFO] Plan copied to .eva/evidence/{story_id}-plan.md")


def cmd_update():
    story_id = os.environ.get("STORY_ID", "UNKNOWN")
    path = receipt_path(story_id)
    lint_ok = "pass" if os.environ.get("LINT_STATUS", "1") == "0" else "warn"
    test_ok = "pass" if os.environ.get("TEST_STATUS", "1") == "0" else "warn"
    if os.path.exists(path):
        with open(path) as f:
            ev = json.load(f)
        ev["lint_result"] = lint_ok
        ev["test_result"] = test_ok
        with open(path, "w") as f:
            json.dump(ev, f, indent=2)
        print(f"[INFO] Evidence updated: lint={lint_ok} test={test_ok}")
    else:
        print(f"[WARN] Receipt not found at {path} -- skipping update")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "write"
    if cmd == "write":
        cmd_write()
    elif cmd == "update":
        cmd_update()
    else:
        print(f"[WARN] Unknown command: {cmd}")
        sys.exit(1)
