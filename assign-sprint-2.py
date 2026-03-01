#!/usr/bin/env python3
"""
Assign 15 Epic 3 stories to Sprint 2 in BOTH local db and ADO.
This is the initial sprint population - both systems are currently empty.
"""
import json
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "data-model"))
import db

# Target: first 15 Epic 3 stories for Sprint 2
SPRINT_2_STORIES = [
    "ACA-03-001", "ACA-03-002", "ACA-03-003", "ACA-03-004", "ACA-03-005",
    "ACA-03-007", "ACA-03-008", "ACA-03-009", "ACA-03-010", "ACA-03-011",
    "ACA-03-012", "ACA-03-013", "ACA-03-014", "ACA-03-015", "ACA-03-016"
]

SPRINT_ID = "Sprint-02"
ADO_ITERATION_PATH = "51-aca\\Sprint 2"
ADO_ORG = "https://dev.azure.com/marcopresta"
ADO_PROJECT = "51-aca"

def update_local_db():
    """Update sprint_id field in local SQLite for 15 stories."""
    print("[INFO] Updating local SQLite database...")
    
    # Load ADO mappings
    ado_map_file = Path(__file__).parent / ".eva" / "ado-id-map.json"
    with open(ado_map_file) as f:
        ado_map = json.load(f)
    
    updated = []
    for story_id in SPRINT_2_STORIES:
        story = db.get_object("wbs", story_id)
        if not story:
            print(f"[WARN] Story {story_id} not found in db")
            continue
        
        # Update sprint_id field
        story["sprint_id"] = SPRINT_ID
        
        # Strip audit fields before PUT
        story_clean = {k: v for k, v in story.items() 
                      if k not in ["layer", "modified_by", "modified_at", "created_by", "created_at", "row_version", "source_file"]}
        
        db.upsert_object("wbs", story_clean, actor="agent:sprint-assign")
        
        ado_work_item_id = ado_map.get(story_id)
        updated.append({
            "story_id": story_id,
            "label": story.get("label", "")[:50],
            "sprint_id": SPRINT_ID,
            "ado_work_item_id": ado_work_item_id
        })
        print(f"[PASS] {story_id} -> sprint_id={SPRINT_ID} (ADO ID: {ado_work_item_id})")
    
    return updated

def generate_ado_commands(updated_stories):
    """Generate az boards CLI commands to update ADO work items."""
    print("\n[INFO] Generating ADO update commands...")
    
    commands = []
    for s in updated_stories:
        if not s["ado_work_item_id"]:
            continue
        
        cmd = (
            f'az boards work-item update '
            f'--id {s["ado_work_item_id"]} '
            f'--org {ADO_ORG} '
            f'--iteration "{ADO_ITERATION_PATH}"'
        )
        commands.append({
            "story_id": s["story_id"],
            "ado_id": s["ado_work_item_id"],
            "command": cmd
        })
    
    return commands

def main():
    print("=" * 80)
    print("SPRINT 2 ASSIGNMENT SCRIPT")
    print("=" * 80)
    print(f"Target: {len(SPRINT_2_STORIES)} Epic 3 stories")
    print(f"Sprint ID (local): {SPRINT_ID}")
    print(f"Iteration Path (ADO): {ADO_ITERATION_PATH}")
    print()
    
    # Step 1: Update local SQLite db
    updated = update_local_db()
    
    # Step 2: Verify local updates
    print(f"\n[PASS] Updated {len(updated)} stories in local db")
    
    # Step 3: Generate ADO commands
    ado_commands = generate_ado_commands(updated)
    
    # Write commands to file for manual execution
    ado_script_file = Path(__file__).parent / "update-ado-sprint2.ps1"
    with open(ado_script_file, "w", encoding="utf-8") as f:
        f.write("# Sprint 2 ADO Work Item Updates\n")
        f.write("# Run this script to assign 15 Epic 3 work items to Sprint 2\n\n")
        for cmd_info in ado_commands:
            f.write(f"# {cmd_info['story_id']} (ADO ID: {cmd_info['ado_id']})\n")
            f.write(f"{cmd_info['command']}\n\n")
        f.write('Write-Host "[PASS] All 15 work items assigned to Sprint 2"\n')
    
    print(f"\n[INFO] ADO commands written to: {ado_script_file}")
    print("[INFO] Run that script to update ADO work items")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Local DB: {len(updated)} stories updated with sprint_id={SPRINT_ID}")
    print(f"ADO: {len(ado_commands)} commands generated")
    print(f"\nNext step: Run {ado_script_file.name} to sync ADO")
    print("=" * 80)

if __name__ == "__main__":
    main()
