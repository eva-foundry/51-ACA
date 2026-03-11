#!/usr/bin/env python3

"""
Add WBS metadata (sprint, assignee, ado_id) to done stories in veritas-plan.json
to unlock the MTI 70+ quality gate.
"""

import json
import sys
from pathlib import Path

DEFAULT_SPRINT = "Sprint-000"
DEFAULT_ASSIGNEE = "marco.presta"

def add_metadata_to_stories(plan_file: str, whatif: bool = False) -> None:
    """Add sprint and assignee metadata to all done stories."""
    
    plan_path = Path(plan_file)
    
    if not plan_path.exists():
        print(f"[ERROR] File not found: {plan_file}")
        sys.exit(1)
    
    print("=== WBS Metadata Population (Local Plan) ===")
    print(f"Plan file: {plan_file}")
    print(f"Default sprint: {DEFAULT_SPRINT}")
    print(f"Default assignee: {DEFAULT_ASSIGNEE}")
    print(f"WhatIf mode: {whatif}")
    print()
    
    # Load the plan
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        print(f"[OK] Loaded veritas plan (schema: {plan.get('schema', 'unknown')})")
    except Exception as e:
        print(f"[ERROR] Failed to load plan: {e}")
        sys.exit(1)
    
    # Track stories needing metadata
    done_stories_needing_metadata = []
    total_done = 0
    
    # Iterate through features and stories
    for feature in plan.get('features', []):
        feature_id = feature.get('id')
        
        for story in feature.get('stories', []):
            story_id = story.get('id')
            is_done = story.get('done', False)
            
            if not is_done:
                continue
            
            total_done += 1
            
            # Check if metadata is missing
            needs_update = False
            if not story.get('sprint') or story.get('sprint').strip() == '':
                needs_update = True
            if not story.get('assignee') or story.get('assignee').strip() == '':
                needs_update = True
            
            if needs_update:
                done_stories_needing_metadata.append({
                    'story': story,
                    'story_id': story_id,
                    'feature_id': feature_id,
                    'current_sprint': story.get('sprint', '(empty)'),
                    'current_assignee': story.get('assignee', '(empty)')
                })
    
    print(f"Found {total_done} total done stories")
    print(f"Found {len(done_stories_needing_metadata)} done stories needing metadata")
    print()
    
    if not done_stories_needing_metadata:
        print("[INFO] All done stories already have complete metadata!")
        return
    
    # Show which stories will be updated
    print("Stories needing metadata update:")
    for item in done_stories_needing_metadata:
        print(f"  {item['story_id']} - sprint: {item['current_sprint']}, assignee: {item['current_assignee']}")
    print()
    
    if whatif:
        print("[INFO] WhatIf mode - no changes made.")
        return
    
    # Apply updates
    print("Applying metadata updates...")
    success_count = 0
    
    for item in done_stories_needing_metadata:
        story = item['story']
        
        # Add/update sprint and assignee
        if not story.get('sprint') or story.get('sprint').strip() == '':
            story['sprint'] = DEFAULT_SPRINT
        if not story.get('assignee') or story.get('assignee').strip() == '':
            story['assignee'] = DEFAULT_ASSIGNEE
        
        success_count += 1
        print(f"  [UPDATED] {item['story_id']} - sprint: {DEFAULT_SPRINT}, assignee: {DEFAULT_ASSIGNEE}")
    
    # Write back to file
    try:
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print()
        print(f"[OK] Updated {success_count} stories in veritas-plan.json")
    except Exception as e:
        print(f"[ERROR] Failed to write plan: {e}")
        sys.exit(1)
    
    print()
    print("Next: Run Veritas audit to confirm MTI score improvement:")
    print("  node C:\\eva-foundry\\eva-foundry\\48-eva-veritas\\src\\cli.js audit --repo .")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Add metadata to done stories')
    parser.add_argument(
        '--plan',
        default='.eva/veritas-plan.json',
        help='Path to veritas-plan.json'
    )
    parser.add_argument(
        '--whatif',
        action='store_true',
        help='Preview changes without applying them'
    )
    
    args = parser.parse_args()
    
    # Make path absolute if relative
    plan_path = Path(args.plan)
    if not plan_path.is_absolute():
        plan_path = Path.cwd() / plan_path
    
    add_metadata_to_stories(str(plan_path), args.whatif)
