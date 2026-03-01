"""
Create 4 sprint objects for 51-ACA project in data model.
Sprint objects enable velocity tracking and sprint-level reporting.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add data-model to path (must be before import db)
_dm_path = str(Path(__file__).parent.parent / "data-model")
if _dm_path not in sys.path:
    sys.path.insert(0, _dm_path)

try:
    import db as _db
    USE_SQLITE = True
except ImportError:
    USE_SQLITE = False
    print("[FAIL] data-model/db.py not found")
    sys.exit(1)

# Sprint definitions for 51-ACA
SPRINTS = [
    {
        "id": "51-ACA-sprint-backlog",
        "label": "Sprint Backlog -- Foundation",
        "project_id": "51-ACA",
        "start_date": "2026-02-01",
        "end_date": "2026-02-25",
        "status": "completed",
        "goal": "61 foundation stories shipped (Epic 1/2/6: docker setup, RBAC, Stripe)",
        "velocity_planned": 60,
        "velocity_actual": 61,
        "story_count": 61,
        "stories_completed": 61,
        "ado_iteration_path": "51-aca\\Sprint Backlog",
        "mti_at_close": 100,
        "notes": "Epic 1 DONE (21 stories), Epic 2 DONE (17 stories), Epic 6 DONE (18 stories), ACA-14 DONE (11 stories: parse-agent-log, commit/push validation)",
        "is_active": True,
        "source_file": "scripts/create-sprints.py"
    },
    {
        "id": "51-ACA-sprint-01",
        "label": "Sprint 1 -- Core API Stubs",
        "project_id": "51-ACA",
        "start_date": "2026-02-26",
        "end_date": "2026-02-27",
        "status": "completed",
        "goal": "5 API endpoint stubs + 24 passing tests (Epic 4: scans, auth, findings, checkout)",
        "velocity_planned": 5,
        "velocity_actual": 5,
        "story_count": 5,
        "stories_completed": 5,
        "ado_iteration_path": "51-aca\\Sprint 1",
        "mti_at_close": 100,
        "notes": "ACA-04-001 through ACA-04-005: POST /v1/scans, GET /v1/scans, POST /v1/auth/connect, GET /v1/findings, POST /v1/checkout/tier2",
        "is_active": True,
        "source_file": "scripts/create-sprints.py"
    },
    {
        "id": "51-ACA-sprint-02",
        "label": "Sprint 2 -- Analysis Rules",
        "project_id": "51-ACA",
        "start_date": "2026-02-28",
        "end_date": "2026-03-10",
        "status": "active",
        "goal": "Epic 3 rules (12 saving opportunity detectors) + GB-02/GB-03 fixes (auto-trigger, pagination)",
        "velocity_planned": 15,
        "velocity_actual": None,
        "story_count": 15,
        "stories_completed": 0,
        "ado_iteration_path": "51-aca\\Sprint 2",
        "mti_at_close": None,
        "notes": "Critical: GB-02 (analysis auto-trigger), GB-03 (Resource Graph pagination), 12 rules from ACA-03",
        "is_active": True,
        "source_file": "scripts/create-sprints.py"
    },
    {
        "id": "51-ACA-sprint-03",
        "label": "Sprint 3 -- Frontend MVP",
        "project_id": "51-ACA",
        "start_date": "2026-03-11",
        "end_date": "2026-03-24",
        "status": "planned",
        "goal": "Epic 5 customer flow (Login, Connect, Status, Findings, Upgrade screens)",
        "velocity_planned": 20,
        "velocity_actual": None,
        "story_count": 20,
        "stories_completed": 0,
        "ado_iteration_path": "51-aca\\Sprint 3",
        "mti_at_close": None,
        "notes": "Deliver customer-facing MVP: all screens + Tier 1 report with upgrade CTA",
        "is_active": True,
        "source_file": "scripts/create-sprints.py"
    }
]

print("[INFO] Creating 4 sprint objects for 51-ACA project...")

for sprint in SPRINTS:
    try:
        # Check if sprint already exists
        existing = _db.get_object("sprints", sprint["id"])
        if existing:
            print(f"  [SKIP] {sprint['id']} already exists")
            continue
    except Exception:
        pass  # Sprint doesn't exist, proceed with insert
    
    # Insert sprint
    _db.upsert_object("sprints", sprint, actor="agent:seed")
    print(f"  [PASS] Created {sprint['id']} - {sprint['label']}")

# Verify
sprints = _db.list_layer("sprints")
aca_sprints = [s for s in sprints if s.get("project_id") == "51-ACA"]
print()
print(f"[INFO] Total sprint objects in model: {len(sprints)}")
print(f"[INFO] 51-ACA sprint objects: {len(aca_sprints)}")

if len(aca_sprints) == 4:
    print("[PASS] All 4 sprint objects seeded successfully")
else:
    print(f"[WARN] Expected 4 sprint objects, got {len(aca_sprints)}")

# Show sprint summary
print()
print("[INFO] 51-ACA sprint summary:")
for sprint in sorted(aca_sprints, key=lambda s: s["id"]):
    status_icon = {"completed": "[DONE]", "active": "[ACTIVE]", "planned": "[PLANNED]"}.get(sprint["status"], "[?]")
    velocity_str = f"{sprint['velocity_actual']}/{sprint['velocity_planned']}" if sprint['velocity_actual'] else f"0/{sprint['velocity_planned']}"
    print(f"  {status_icon} {sprint['id']}: {sprint['label']}")
    print(f"         velocity={velocity_str} stories={sprint['stories_completed']}/{sprint['story_count']} MTI={sprint.get('mti_at_close','TBD')}")
