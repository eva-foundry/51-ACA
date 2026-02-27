"""
# EVA-STORY: ACA-14-005
gen-sprint-manifest.py -- generate a sprint manifest stub from Veritas story IDs
==================================================================================
Reads veritas-plan.json and PLAN.md to build a .github/sprints/sprint-NN-name.md
stub.  Story IDs are taken verbatim from veritas-plan.json -- never invented.

Usage:
  python scripts/gen-sprint-manifest.py --stories ACA-03-006,ACA-06-018,ACA-04-028
  python scripts/gen-sprint-manifest.py --sprint 02 --stories ACA-03-006,ACA-06-018
  python scripts/gen-sprint-manifest.py --list-done         # list done stories
  python scripts/gen-sprint-manifest.py --list-undone       # list undone stories (default filter)

The output file is a markdown doc containing a SPRINT_MANIFEST JSON block that the
sprint-agent.yml workflow parses.  Fill in the TODOs before creating the GitHub issue.

Encoding: ascii-only output -- no emoji, no unicode.
"""

import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT    = Path(__file__).parent.parent
PLAN_FILE    = REPO_ROOT / "PLAN.md"
VERITAS_FILE = REPO_ROOT / ".eva" / "veritas-plan.json"
SPRINTS_DIR  = REPO_ROOT / ".github" / "sprints"

# Default model per story size (kept in sync with CA.1)
MODEL_BY_SIZE = {
    "XS": "gpt-5-mini",
    "S":  "gpt-5",
    "M":  "claude-sonnet-4-6",
    "L":  "claude-sonnet-4-6",
    "XL": "claude-opus-4-6",
}

EPIC_LABEL = {
    "ACA-01": "Epic 01 -- Foundation",
    "ACA-02": "Epic 02 -- Data Collection",
    "ACA-03": "Epic 03 -- Analysis",
    "ACA-04": "Epic 04 -- API",
    "ACA-05": "Epic 05 -- Frontend",
    "ACA-06": "Epic 06 -- Billing",
    "ACA-07": "Epic 07 -- Delivery",
    "ACA-08": "Epic 08 -- Observability",
    "ACA-09": "Epic 09 -- i18n",
    "ACA-10": "Epic 10 -- Hardening",
    "ACA-11": "Epic 11 -- Phase 2 Infra",
    "ACA-12": "Epic 12 -- Data Model",
    "ACA-13": "Epic 13 -- Best Practices",
    "ACA-14": "Epic 14 -- DPDCA Agent",
}


def load_veritas() -> dict:
    if not VERITAS_FILE.exists():
        print(f"[FAIL] veritas-plan.json not found: {VERITAS_FILE}")
        print("[INFO] Run: python scripts/seed-from-plan.py --reseed-model")
        sys.exit(1)
    return json.loads(VERITAS_FILE.read_text(encoding="utf-8"))


def build_story_index(veritas: dict) -> dict[str, dict]:
    """Return dict: canonical_id -> story object (with wbs, title, feature_id, done)."""
    index: dict[str, dict] = {}
    for feat in veritas.get("features", []):
        for story in feat.get("stories", []):
            sid = story.get("id", "")
            if sid:
                index[sid] = story
    return index


def list_stories(veritas: dict, show_done: bool = False) -> None:
    index = build_story_index(veritas)
    header = "DONE stories:" if show_done else "Undone stories (ready for sprint):"
    print(header)
    print("-" * 60)
    for sid, story in sorted(index.items()):
        if story.get("done", False) == show_done:
            wbs = story.get("wbs", "")
            wbs_str = f" [wbs:{wbs}]" if wbs else ""
            print(f"  {sid}{wbs_str}  {story.get('title', '')[:70]}")
    print()


def make_story_stub(story: dict, size: str = "M") -> dict:
    """Build a single story entry for the SPRINT_MANIFEST."""
    sid = story.get("id", "UNKNOWN")
    epic_prefix = "-".join(sid.split("-")[:2])  # "ACA-03"
    wbs = story.get("wbs", "")
    model = MODEL_BY_SIZE.get(size.upper(), "claude-sonnet-4-6")
    epic_label = EPIC_LABEL.get(epic_prefix, f"Epic {epic_prefix}")

    return {
        "id": sid,
        "title": story.get("title", ""),
        "wbs": wbs,
        "size": size.upper(),
        "model": model,
        "model_rationale": "TODO: describe why this model was chosen",
        "epic": epic_label,
        "files_to_create": [
            "TODO: list files to create or update"
        ],
        "acceptance": [
            "TODO: add acceptance criteria"
        ],
        "implementation_notes": "TODO: add detailed implementation notes for the agent",
    }


def generate_manifest(
    sprint_num: str,
    sprint_name: str,
    story_ids: list[str],
    story_index: dict[str, dict],
    sizes: dict[str, str],
) -> str:
    """Generate the sprint manifest markdown string."""
    stories = []
    missing = []
    for sid in story_ids:
        if sid not in story_index:
            missing.append(sid)
            print(f"[WARN] Story ID not found in veritas-plan.json: {sid}")
            print("[INFO] Run: python scripts/seed-from-plan.py --reseed-model")
            print("[INFO] Then: python scripts/reflect-ids.py")
        else:
            size = sizes.get(sid, "M")
            stories.append(make_story_stub(story_index[sid], size))

    if missing:
        print(f"[FAIL] {len(missing)} story IDs not found. Aborting.")
        sys.exit(1)

    # Determine primary epic (most common among stories)
    epic_counts: dict[str, int] = {}
    for sid in story_ids:
        ep = "-".join(sid.split("-")[:2])
        epic_counts[ep] = epic_counts.get(ep, 0) + 1
    primary_epic = max(epic_counts, key=lambda k: epic_counts[k]) if epic_counts else "ACA-00"

    target_branch = f"sprint/{sprint_num.zfill(2)}-{sprint_name.lower().replace(' ', '-')}"
    sprint_id = f"SPRINT-{sprint_num.zfill(2)}"

    manifest = {
        "sprint_id": sprint_id,
        "sprint_title": sprint_name,
        "target_branch": target_branch,
        "epic": primary_epic,
        "stories": stories,
    }

    manifest_json = json.dumps(manifest, indent=2, ensure_ascii=True)

    # Build the markdown document
    story_table_rows = "\n".join(
        f"| {s['id']} | {s['title'][:55]} | {s['wbs']} | {s['size']} |"
        for s in stories
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    doc = f"""<!-- SPRINT_MANIFEST
{manifest_json}
-->

# {sprint_id} -- {sprint_name}

Generated: {now}
Story IDs are canonical Veritas IDs from veritas-plan.json.
EVA-STORY tags in source files must use these exact IDs.

## Stories

| ID | Title | WBS | Size |
|----|-------|-----|------|
{story_table_rows}

## Execution Order

{chr(10).join(f"{i+1}. `{s['id']}` -- {s['title'][:60]}" for i, s in enumerate(stories))}

## Notes

- All story IDs verified against .eva/veritas-plan.json
- Fill in TODO fields before creating the GitHub issue
- Create issue with: gh issue create --repo eva-foundry/51-ACA --title "[{sprint_id}] {sprint_name}" --body-file .github/sprints/{sprint_id.lower()}-{sprint_name.lower().replace(' ', '-')}.md --label "sprint-task"
"""
    return doc


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sprint manifest from Veritas story IDs")
    parser.add_argument("--stories", type=str, help="Comma-separated canonical story IDs (e.g. ACA-03-006,ACA-06-018)")
    parser.add_argument("--sprint", type=str, default="00", help="Sprint number (e.g. 02)")
    parser.add_argument("--name", type=str, default="", help="Sprint name suffix (e.g. 'api fixes')")
    parser.add_argument("--sizes", type=str, default="", help="Per-story sizes: ACA-03-006=M,ACA-06-018=XS")
    parser.add_argument("--list-done", action="store_true", help="List done stories and exit")
    parser.add_argument("--list-undone", action="store_true", help="List undone stories and exit")
    parser.add_argument("--output", type=str, default="", help="Output file path (default: .github/sprints/sprint-NN-name.md)")
    args = parser.parse_args()

    veritas = load_veritas()
    story_index = build_story_index(veritas)

    if args.list_done:
        list_stories(veritas, show_done=True)
        return
    if args.list_undone:
        list_stories(veritas, show_done=False)
        return

    if not args.stories:
        print("[FAIL] --stories is required (or use --list-undone to browse)")
        print("Example: python scripts/gen-sprint-manifest.py --sprint 02 --stories ACA-03-006,ACA-06-018")
        sys.exit(1)

    story_ids = [s.strip() for s in args.stories.split(",") if s.strip()]

    # Parse per-story sizes: "ACA-03-006=M,ACA-06-018=XS"
    sizes: dict[str, str] = {}
    if args.sizes:
        for part in args.sizes.split(","):
            if "=" in part:
                sid, sz = part.strip().split("=", 1)
                sizes[sid.strip()] = sz.strip().upper()

    sprint_name = args.name or "stories"
    doc = generate_manifest(args.sprint, sprint_name, story_ids, story_index, sizes)

    if args.output:
        out_path = Path(args.output)
    else:
        SPRINTS_DIR.mkdir(parents=True, exist_ok=True)
        fname = f"sprint-{str(args.sprint).zfill(2)}-{sprint_name.lower().replace(' ', '-')}.md"
        out_path = SPRINTS_DIR / fname

    out_path.write_text(doc, encoding="utf-8", errors="replace")
    print(f"[PASS] Sprint manifest written: {out_path}")
    print("[INFO] Edit the TODO fields, then create the GitHub issue to trigger sprint-agent.yml")


if __name__ == "__main__":
    main()
