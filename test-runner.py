#!/usr/bin/env python3
"""
Test runner for single story execution (ACA-03-001).
Bypasses GitHub issue requirement for quick DPDCA validation.
"""
import os
import sys
import json
from pathlib import Path

# Set up paths
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT / ".github" / "scripts"))

# Mock environment for test mode
os.environ["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN", "test-token")
os.environ["ACA_DATA_MODEL_URL"] = os.getenv("ACA_DATA_MODEL_URL", "http://localhost:8055")

# Load test manifest
manifest_path = REPO_ROOT / "test-manifest-ACA-03-001.json"
with open(manifest_path) as f:
    manifest = json.load(f)

print(f"[INFO] Test mode: executing single story {manifest['stories'][0]['id']}")
print(f"[INFO] Story: {manifest['stories'][0]['title']}")
print(f"[INFO] Files to create: {len(manifest['stories'][0]['files_to_create'])}")
print(f"[INFO] Files to edit: {len(manifest['stories'][0]['files_to_edit'])}")
print()

# Import sprint agent functions
try:
    import sprint_agent
    
    # Story data
    story = manifest["stories"][0]
    
    # Execute story implementation (simplified workflow)
    print(f"[1/5] Preparing story context...")
    context = {
        "repo_root": str(REPO_ROOT),
        "story_id": story["id"],
        "title": story["title"],
        "files_to_create": story["files_to_create"],
        "files_to_edit": story.get("files_to_edit", []),
        "spec_references": story.get("spec_references", []),
        "acceptance_criteria": story.get("acceptance_criteria", [])
    }
    
    print(f"[2/5] Reading spec references...")
    spec_content = []
    for spec_file in context["spec_references"]:
        spec_path = REPO_ROOT / spec_file
        if spec_path.exists():
            with open(spec_path) as f:
                spec_content.append(f.read())
            print(f"  - Loaded {spec_file} ({len(spec_content[-1])} chars)")
        else:
            print(f"  - [WARN] Spec file not found: {spec_file}")
    
    print(f"[3/5] Analyzing existing code...")
    existing_files = []
    for edit_file in context["files_to_edit"]:
        edit_path = REPO_ROOT / edit_file
        if edit_path.exists():
            with open(edit_path) as f:
                existing_files.append({"path": edit_file, "content": f.read()})
            print(f"  - Loaded {edit_file} ({len(existing_files[-1]['content'])} chars)")
    
    print(f"[4/5] Generating implementation plan...")
    print(f"  - {story['id']}: {story['title']}")
    print(f"  - Epic: {story.get('epic', 'N/A')}, Feature: {story.get('feature', 'N/A')}")
    print(f"  - FP: {story.get('fp', 'N/A')}")
    print()
    
    print(f"[5/5] MANUAL EXECUTION REQUIRED")
    print()
    print(f"The sprint agent is designed to run as a GitHub Action with LLM access.")
    print(f"For local testing, you need to:")
    print()
    print(f"Option A -- Manual Implementation:")
    print(f"  1. Read spec: docs/saving-opportunity-rules.md")
    print(f"  2. Create {len(story['files_to_create'])} rule files in services/analysis/app/rules/")
    print(f"  3. Update services/analysis/app/main.py to load ALL_RULES")
    print(f"  4. Run: pytest services/analysis/ -v")
    print(f"  5. Verify: All 12 rules are imported and registered")
    print()
    print(f"Option B -- GitHub Action:")
    print(f"  1. Create GitHub issue with sprint manifest")
    print(f"  2. Trigger sprint-agent workflow")
    print(f"  3. Monitor workflow logs")
    print()
    print(f"Option C -- LLM-Assisted (GitHub Copilot):")
    print(f"  1. Open docs/saving-opportunity-rules.md")
    print(f"  2. Ask Copilot to implement ACA-03-001")
    print(f"  3. Run pytest to validate")
    print()
    
    # Write evidence receipt stub
    evidence_dir = REPO_ROOT / ".eva" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence = {
        "story_id": story["id"],
        "phase": "P",  # Planning phase (not executed)
        "timestamp": sprint_agent._now_iso(),
        "artifacts": [],
        "test_result": "SKIPPED",
        "commit_sha": None,
        "duration_ms": 0,
        "tokens_used": 0,
        "test_count_before": 0,
        "test_count_after": 0,
        "files_changed": 0,
        "notes": "Test runner executed in planning mode -- no implementation attempted"
    }
    
    evidence_file = evidence_dir / f"{story['id']}-receipt.json"
    with open(evidence_file, "w") as f:
        json.dump(evidence, f, indent=2)
    
    print(f"[INFO] Evidence receipt stub written: {evidence_file}")
    print(f"[PASS] Test runner complete -- manual implementation required")
    
except ImportError as exc:
    print(f"[FAIL] Could not import sprint_agent: {exc}")
    sys.exit(1)
except Exception as exc:
    print(f"[FAIL] Test runner error: {exc}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
