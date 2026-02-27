"""
# EVA-STORY: ACA-12-001
reflect-ids.py -- reflect canonical Veritas story IDs back into PLAN.md
========================================================================
After seeding (seed-from-plan.py), this script annotates every Story WBS line
in PLAN.md with its canonical Veritas ID in square brackets:

  BEFORE:  Story 2.5.4  As the system, after mark_collection_complete...
  AFTER:   Story 2.5.4 [ACA-02-017]  As the system, after mark_collection_complete...

This makes PLAN.md the single human-readable reference for canonical IDs.
Agents and authors can read PLAN.md and find the correct EVA-STORY tag for any
story without consulting veritas-plan.json separately.

Idempotent: already-annotated lines are refreshed (not doubled or skipped).
Only rewrites old-format stories (N.M.K WBS numbers).
New-format stories (Story ACA-NN-NNN  title) are left unchanged.
STORY_NEW lines are counted to maintain correct sequential numbering.

Usage:
  python scripts/reflect-ids.py              # update PLAN.md in place, then re-seed
  python scripts/reflect-ids.py --dry-run    # print changes only, no write
  python scripts/reflect-ids.py --no-reseed  # update PLAN.md only, skip re-seed
"""

import re
import sys
import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PLAN_FILE = REPO_ROOT / "PLAN.md"
SCRIPTS_DIR = Path(__file__).parent
PYTHON_EXEC = sys.executable

# Matches old-format story with optional existing annotation:
#   "  Story 2.5.4  title..."
#   "  Story 2.5.4 [ACA-02-017]  title..."
# Groups: (1)indent, (2)epic_n, (3)feat_n, (4)story_n, (5)annotation|None, (6)rest_of_title
STORY_OLD_RE = re.compile(
    r"^(\s{2,6})Story\s+(\d+)\.(\d+)\.(\d+)"
    r"(?:\s+\[([A-Z]{2,5}-\d{2}-\d{3})\])?"
    r"(\s{2,}.+)$"
)

# Matches new-format story (already has canonical ID -- count it but do not rewrite):
#   "  Story ACA-02-017  title..."
STORY_NEW_RE = re.compile(r"^\s{2,6}Story\s+(ACA-\d{2}-\d{3})\s{2,}")


def reflect(plan_text: str, dry_run: bool = False) -> tuple[str, int]:
    """
    Annotate every old-format story line with its canonical ID.
    Returns (new_text, count_annotated).
    Uses a single sequential pass -- same counting logic as seed-from-plan.py.
    """
    story_counters: dict[int, int] = {}
    new_lines: list[str] = []
    changes = 0

    for line in plan_text.splitlines(keepends=True):
        # New-format story: count it to keep sequential numbering correct, no rewrite
        m_new = STORY_NEW_RE.match(line)
        if m_new:
            story_id = m_new.group(1)
            try:
                ep_n = int(story_id.split("-")[1])
            except (IndexError, ValueError):
                ep_n = 0
            story_counters[ep_n] = story_counters.get(ep_n, 0) + 1
            new_lines.append(line)
            continue

        # Old-format story: compute canonical ID and annotate
        m_old = STORY_OLD_RE.match(line)
        if m_old:
            indent = m_old.group(1)
            ep_n = int(m_old.group(2))
            feat_n = m_old.group(3)
            story_n = m_old.group(4)
            existing_annotation = m_old.group(5)  # may be None
            rest = m_old.group(6)  # "  title..."

            story_counters[ep_n] = story_counters.get(ep_n, 0) + 1
            canonical_id = f"ACA-{ep_n:02d}-{story_counters[ep_n]:03d}"

            new_line = f"{indent}Story {ep_n}.{feat_n}.{story_n} [{canonical_id}]{rest}\n"
            # keepends already adds \n from splitlines(keepends=True) -- but rest may
            # include trailing whitespace; strip the original newline and re-add cleanly
            rest_stripped = rest.rstrip("\r\n")
            new_line = f"{indent}Story {ep_n}.{feat_n}.{story_n} [{canonical_id}]{rest_stripped}\n"

            if existing_annotation and existing_annotation != canonical_id:
                print(f"[WARN] {existing_annotation} -> {canonical_id} (recount): wbs {ep_n}.{feat_n}.{story_n}")

            if dry_run:
                if not existing_annotation:
                    print(f"[DRY]  +[{canonical_id}]  wbs {ep_n}.{feat_n}.{story_n}")
                    changes += 1
                elif existing_annotation != canonical_id:
                    print(f"[DRY]  [{existing_annotation}] -> [{canonical_id}]  wbs {ep_n}.{feat_n}.{story_n}")
                    changes += 1
            else:
                if not existing_annotation or existing_annotation != canonical_id:
                    changes += 1
            new_lines.append(new_line)
            continue

        # All other lines -- pass through unchanged
        new_lines.append(line)

    return "".join(new_lines), changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Reflect Veritas IDs into PLAN.md")
    parser.add_argument("--dry-run", action="store_true", help="Print changes, do not write")
    parser.add_argument("--no-reseed", action="store_true", help="Skip re-seeding veritas after writing")
    args = parser.parse_args()

    if not PLAN_FILE.exists():
        print(f"[FAIL] PLAN.md not found: {PLAN_FILE}")
        sys.exit(1)

    plan_text = PLAN_FILE.read_text(encoding="utf-8")
    new_text, changes = reflect(plan_text, dry_run=args.dry_run)

    if args.dry_run:
        print(f"[INFO] Dry run complete -- {changes} stories would be annotated/updated")
        return

    if changes == 0:
        print("[PASS] PLAN.md already fully annotated -- no changes needed")
    else:
        PLAN_FILE.write_text(new_text, encoding="utf-8")
        print(f"[PASS] Annotated {changes} story lines in PLAN.md")

    if not args.no_reseed:
        seed_script = SCRIPTS_DIR / "seed-from-plan.py"
        if seed_script.exists():
            print("[INFO] Re-seeding veritas-plan.json...")
            result = subprocess.run(
                [PYTHON_EXEC, str(seed_script)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("[PASS] veritas-plan.json re-seeded")
                if result.stdout.strip():
                    print(result.stdout.strip())
            else:
                print("[WARN] seed-from-plan.py exited non-zero")
                print(result.stderr.strip())
        else:
            print("[WARN] seed-from-plan.py not found -- skipping re-seed")


if __name__ == "__main__":
    main()
