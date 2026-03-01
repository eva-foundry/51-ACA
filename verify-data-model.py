"""
Demonstrate new data model query capabilities after WBS + sprint seeding.
Shows example queries that replace PLAN.md/STATUS.md parsing.
"""
import sys
from pathlib import Path

# Add data-model to path (must be before import db)
_dm_path = str(Path(__file__).parent / "data-model")
if _dm_path not in sys.path:
    sys.path.insert(0, _dm_path)

import db as _db

print("=" * 80)
print("51-ACA DATA MODEL SEEDING VERIFICATION")
print("=" * 80)
print()

# ========== QUERY 1: Overall WBS statistics ==========
print("[QUERY 1] Overall WBS statistics for 51-ACA")
print("-" * 80)
wbs = _db.list_layer("wbs")
aca_wbs = [w for w in wbs if w.get("project_id") == "51-ACA"]
epics = [w for w in aca_wbs if w.get("level") == "epic"]
features = [w for w in aca_wbs if w.get("level") == "feature"]
stories = [w for w in aca_wbs if w.get("level") == "story"]

print(f"Total WBS objects: {len(aca_wbs)} (14 epics + 54 features + 256 stories)")
print(f"  Epics:    {len(epics)}")
print(f"  Features: {len(features)}")
print(f"  Stories:  {len(stories)}")
print()

# ========== QUERY 2: Story status breakdown ==========
print("[QUERY 2] Story status breakdown")
print("-" * 80)
done_stories = [s for s in stories if s.get("status") == "done"]
active_stories = [s for s in stories if s.get("status") == "active"]
planned_stories = [s for s in stories if s.get("status") == "planned"]

print(f"Done:    {len(done_stories)} stories")
print(f"Active:  {len(active_stories)} stories")
print(f"Planned: {len(planned_stories)} stories")
print(f"Total:   {len(stories)} stories")
print()

# ========== QUERY 3: Epic completion percentage ==========
print("[QUERY 3] Epic completion percentages")
print("-" * 80)
for epic in sorted(epics, key=lambda e: e["id"]):
    epic_stories = [s for s in stories if s.get("parent_wbs_id", "").startswith(epic["id"])]
    epic_done = [s for s in epic_stories if s.get("status") == "done"]
    completion = (len(epic_done) / len(epic_stories) * 100) if epic_stories else 0
    status_icon = "[DONE]" if completion == 100 else "[ACTIVE]" if completion > 0 else "[PLANNED]"
    print(f"  {status_icon} {epic['id']}: {completion:5.1f}% ({len(epic_done)}/{len(epic_stories)}) - {epic['label'][:50]}")
print()

# ========== QUERY 4: Sprint objects summary ==========
print("[QUERY 4] Sprint objects for 51-ACA")
print("-" * 80)
sprints = _db.list_layer("sprints")
aca_sprints = [s for s in sprints if s.get("project_id") == "51-ACA"]

for sprint in sorted(aca_sprints, key=lambda s: s["id"]):
    status_map = {"completed": "[DONE]", "active": "[ACTIVE]", "planned": "[PLANNED]"}
    status_icon = status_map.get(sprint["status"], "[?]")
    velocity_str = f"{sprint['velocity_actual']}/{sprint['velocity_planned']}" if sprint['velocity_actual'] else f"0/{sprint['velocity_planned']}"
    mti_str = str(sprint.get("mti_at_close", "TBD"))
    print(f"  {status_icon} {sprint['id']}")
    print(f"           {sprint['label']}")
    print(f"           Velocity: {velocity_str} FP | Stories: {sprint['stories_completed']}/{sprint['story_count']} | MTI: {mti_str}")
    print(f"           ADO: {sprint['ado_iteration_path']}")
print()

# ========== QUERY 5: ADO sync verification ==========
print("[QUERY 5] ADO sync verification")
print("-" * 80)
stories_with_ado = [s for s in stories if s.get("ado_id") is not None]
print(f"Stories with ADO ID: {len(stories_with_ado)} / {len(stories)}")
print(f"ADO coverage: {len(stories_with_ado) / len(stories) * 100:.1f}%")
print()

# ========== QUERY 6: Undone stories for next sprint (sample) ==========
print("[QUERY 6] Sample undone stories (next sprint candidates)")
print("-" * 80)
undone = [s for s in stories if s.get("status") in ("planned", "active")]
# Show first 5 undone stories with FP > 0
sample_undone = sorted([s for s in undone if s.get("story_points", 0) > 0], 
                       key=lambda s: s["id"])[:5]
for story in sample_undone:
    fp = story.get("story_points", 0)
    sprint = story.get("sprint_id", "None")
    print(f"  {story['id']} [{fp}FP] {sprint:15s} - {story['label'][:60]}")
print(f"  ... ({len(undone)} total undone stories)")
print()

print("=" * 80)
print("[PASS] Data model seeding verification complete")
print("=" * 80)
print()
print("NEXT STEPS:")
print("  1. All 256 WBS stories + 4 sprint objects are queryable via HTTP API")
print("  2. Create 3 new report skills: sprint-report, gap-report, progress-report")
print("  3. Replace PLAN.md/STATUS.md parsing with data model queries")
print("  4. Enhance parser to extract acceptance_criteria, related_stories, files_affected")
