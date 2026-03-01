#!/usr/bin/env python3
"""Get Sprint 2 info from LOCAL SQLite database."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "data-model"))
import db

# Get Sprint 2 metadata
sprint = db.get_object("sprints", "51-ACA-sprint-02")

# Get all WBS stories
all_stories = db.list_layer("wbs")

# Find Epic 3 undone stories (ACA-03-NNN)
epic3_undone = [
    s for s in all_stories 
    if s["level"] == "story" 
    and s["id"].startswith("ACA-03-") 
    and s.get("status") != "done"
    and s.get("story_points", 0) > 0
]

# Build result
result = {
    "storage_info": {
        "database": "LOCAL SQLite (NOT Cosmos)",
        "path": str(db.DB_PATH),
        "size_kb": round(db.DB_PATH.stat().st_size / 1024, 1)
    },
    "sprint_02_metadata": {
        "id": sprint["id"],
        "label": sprint["label"],
        "status": sprint["status"],
        "goal": sprint["goal"],
        "start_date": sprint["start_date"],
        "end_date": sprint["end_date"],
        "velocity_planned": sprint["velocity_planned"],
        "story_count": sprint["story_count"],
        "stories_completed": sprint["stories_completed"],
        "ado_iteration_path": sprint["ado_iteration_path"]
    },
    "critical_issue": "sprint_id field is null for all 256 WBS stories",
    "epic_3_analysis_rules": {
        "total_stories": len([s for s in all_stories if s["level"] == "story" and s["id"].startswith("ACA-03-")]),
        "done": len([s for s in all_stories if s["level"] == "story" and s["id"].startswith("ACA-03-") and s.get("status") == "done"]),
        "undone_with_fp": len(epic3_undone),
        "candidate_stories_for_sprint_02": [
            {
                "id": s["id"],
                "label": s["label"][:70],
                "fp": s.get("story_points"),
                "status": s.get("status"),
                "parent": s.get("parent_wbs_id")
            }
            for s in sorted(epic3_undone, key=lambda x: -x.get("story_points", 0))[:12]
        ]
    }
}

print(json.dumps(result, indent=2))
