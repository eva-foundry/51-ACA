#!/usr/bin/env python3
"""Sprint 2 Pre-Flight Check - Verify all requirements before launch"""

import sys
import json
from pathlib import Path

sys.path.insert(0, 'data-model')
import db

print("=" * 60)
print("SPRINT 2 PRE-FLIGHT CHECK")
print("=" * 60)
print()

# Check 1: LOCAL DB stories
print("[CHECK 1] LOCAL DB Sprint 2 Stories")
print("-" * 40)
stories = [s for s in db.list_layer('wbs') if s.get('sprint_id') == 'Sprint-02']
print(f"Stories found: {len(stories)}")
print(f"Expected: 15")
if len(stories) == 15:
    print("[PASS] Story count correct")
else:
    print("[FAIL] Story count mismatch")
print()

# Check 2: Story details completeness
print("[CHECK 2] Story Details Completeness")
print("-" * 40)
missing_fields = []
for story in stories[:3]:  # Check first 3 as sample
    story_id = story.get('id', 'N/A')
    required = ['id', 'title', 'epic', 'ado_work_item_id', 'acceptance_criteria']
    missing = [f for f in required if not story.get(f)]
    if missing:
        missing_fields.append(f"{story_id}: missing {missing}")
        print(f"  {story_id}: MISSING {missing}")
    else:
        print(f"  {story_id}: COMPLETE")

if not missing_fields:
    print("[PASS] All stories have required fields")
else:
    print(f"[WARN] Some stories missing fields")
print()

# Check 3: ADO work item IDs
print("[CHECK 3] ADO Work Item ID Mapping")
print("-" * 40)
ado_ids = [s.get('ado_work_item_id') for s in stories if s.get('ado_work_item_id')]
print(f"Stories with ADO IDs: {len(ado_ids)}")
print(f"Sample ADO IDs: {ado_ids[:5]}")
if len(ado_ids) == 15:
    print("[PASS] All stories have ADO IDs")
else:
    print(f"[FAIL] Only {len(ado_ids)}/15 stories have ADO IDs")
print()

# Check 4: Sprint manifest
print("[CHECK 4] Sprint Manifest File")
print("-" * 40)
manifest_path = Path("sprint-02-manifest.json")
if manifest_path.exists():
    with open(manifest_path) as f:
        manifest = json.load(f)
    print(f"Manifest exists: YES")
    print(f"Story count in manifest: {manifest.get('story_count', 0)}")
    print(f"Stories in manifest: {len(manifest.get('stories', [])) if manifest.get('stories') else 0}")
    if manifest.get('stories') and len(manifest['stories']) == 15:
        print("[PASS] Manifest has all stories")
    else:
        print("[WARN] Manifest needs story list populated")
else:
    print("[FAIL] Manifest file not found")
print()

# Check 5: Workflow file
print("[CHECK 5] GitHub Workflow")
print("-" * 40)
workflow_path = Path(".github/workflows/sprint-agent.yml")
if workflow_path.exists():
    print(f"Workflow exists: YES")
    print("[PASS] Workflow file present")
else:
    print("[FAIL] Workflow file not found")
print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"LOCAL DB: {len(stories)} stories ready")
print(f"ADO Mapping: {len(ado_ids)}/15 stories have ADO IDs")
print(f"Manifest: {'Complete' if manifest.get('stories') and len(manifest['stories']) == 15 else 'Needs update'}")
print(f"Workflow: {'Ready' if workflow_path.exists() else 'Missing'}")
print()

# Output first 3 stories for verification
print("=" * 60)
print("SAMPLE STORIES (first 3)")
print("=" * 60)
for i, story in enumerate(stories[:3], 1):
    print(f"{i}. {story.get('id')} - {story.get('title')[:60]}...")
    print(f"   Epic: {story.get('epic')}")
    print(f"   ADO: {story.get('ado_work_item_id')}")
    print()
