"""
Quick WBS verification script for 51-ACA data model seeding.
"""
import sys
from pathlib import Path

# Add data-model to path
sys.path.insert(0, str(Path(__file__).parent / "data-model"))
import db

# Query WBS layer
wbs = db.list_layer("wbs")
stories = [w for w in wbs if w.get("level") == "story" and w.get("project_id") == "51-ACA"]
epics = [w for w in wbs if w.get("level") == "epic" and w.get("project_id") == "51-ACA"]
features = [w for w in wbs if w.get("level") == "feature" and w.get("project_id") == "51-ACA"]

print(f"[INFO] Total WBS objects: {len(wbs)}")
print(f"[INFO] 51-ACA epic objects: {len(epics)}")
print(f"[INFO] 51-ACA feature objects: {len(features)}")
print(f"[INFO] 51-ACA story objects: {len(stories)}")
print()

# Verify expected counts
expected_stories = 257
if len(stories) == expected_stories:
    print(f"[PASS] Story count matches PLAN.md: {expected_stories}")
else:
    print(f"[WARN] Story count mismatch: got {len(stories)}, expected {expected_stories}")

# Check ADO mapping coverage
stories_with_ado = [s for s in stories if s.get("ado_id") is not None]
print(f"[INFO] Stories with ADO ID: {len(stories_with_ado)} / {len(stories)}")

# Sample stories
print()
print("[INFO] Sample WBS story objects:")
for i, story in enumerate(stories[:3]):
    print(f"  [{i+1}] {story['id']} - {story['label'][:60]}")
    print(f"      status={story['status']} FP={story['story_points']} sprint={story.get('sprint_id','None')} ADO={story.get('ado_id','None')}")
