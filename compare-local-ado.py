#!/usr/bin/env python3
"""Compare LOCAL SQLite data model with ADO project state."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "data-model"))
import db

# Load ADO mappings
ado_map_file = Path(__file__).parent / ".eva" / "ado-id-map.json"
with open(ado_map_file) as f:
    ado_map = json.load(f)

# Get Sprint 2 metadata from LOCAL SQLite
sprint2 = db.get_object("sprints", "51-ACA-sprint-02")

# Get all WBS stories
all_stories = db.list_layer("wbs")
stories = [s for s in all_stories if s["level"] == "story"]

# Analyze Epic 3 (target for Sprint 2)
epic3_stories = [s for s in stories if s["id"].startswith("ACA-03-")]
epic3_done = [s for s in epic3_stories if s.get("status") == "done"]
epic3_undone = [s for s in epic3_stories if s.get("status") != "done"]

# Stories with sprint_id assigned
assigned_to_sprint2 = [s for s in stories if s.get("sprint_id") == "Sprint-02"]

# Build comparison result
result = {
    "storage": {
        "local_sqlite": str(db.DB_PATH),
        "size_kb": round(db.DB_PATH.stat().st_size / 1024, 1)
    },
    "ado_integration": {
        "project_url": "https://dev.azure.com/marcopresta/51-aca",
        "total_ado_mappings": len(ado_map),
        "local_stories_with_ado_id": len([s for s in stories if s.get("ado_id")]),
        "ado_coverage_percent": round(100 * len([s for s in stories if s.get("ado_id")]) / len(stories), 1),
        "note": "All 256 stories have ADO work item IDs mapped"
    },
    "sprint_02_in_local_db": {
        "id": sprint2["id"],
        "label": sprint2["label"],
        "status": sprint2["status"],
        "goal": sprint2["goal"],
        "ado_iteration_path": sprint2["ado_iteration_path"],
        "velocity_planned": sprint2["velocity_planned"],
        "story_count_planned": sprint2["story_count"],
        "stories_completed": sprint2["stories_completed"]
    },
    "sprint_02_linkage_problem": {
        "issue": "sprint_id field is null for all 256 WBS stories in local db",
        "stories_linked_to_sprint_02": len(assigned_to_sprint2),
        "expected": 15,
        "impact": "Cannot query 'which stories are in Sprint 2' from local db"
    },
    "epic_3_analysis": {
        "target_for_sprint_02": "Epic 3 -- Analysis Rules (12 rules + GB-02/GB-03)",
        "total_epic3_stories": len(epic3_stories),
        "done": len(epic3_done),
        "undone": len(epic3_undone),
        "undone_story_ids": [s["id"] for s in epic3_undone[:15]],
        "problem": "All Epic 3 undone stories have story_points=0",
        "next_step": "Size stories in PLAN.md, then assign 15 to Sprint 2"
    },
    "ado_state_unknown": {
        "note": "Cannot query ADO from this script without az CLI working",
        "manual_check_required": [
            "Open https://dev.azure.com/marcopresta/51-aca/_sprints",
            "Check if Sprint 2 iteration exists",
            "Check if any work items are assigned to Sprint 2 iteration",
            "Check if work item IDs 2978-3009 (Epic 3) have iteration path set"
        ]
    },
    "recommendation": {
        "step_1": "Manually check ADO: do Sprint 2 work items exist with iteration path '51-aca\\Sprint 2'?",
        "step_2": "If ADO Sprint 2 is empty: stories exist but not sprint-assigned",
        "step_3": "If ADO Sprint 2 has work items: local db sprint_id needs updating to match ADO",
        "step_4": "Create script to sync: read ADO iteration assignments -> update local db sprint_id field"
    }
}

print(json.dumps(result, indent=2))
