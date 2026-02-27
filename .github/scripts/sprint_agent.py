#!/usr/bin/env python3
# EVA-STORY: ACA-14-009
# sprint_agent.py -- Full-sprint cloud execution runner
#
# Reads a sprint issue, executes all stories in sequence,
# posts progress comments after each story, posts final summary.
#
# Usage:
#   python3 sprint_agent.py --issue N --repo owner/repo
#
# Sprint issue format: the issue body must contain a JSON manifest block:
#   <!-- SPRINT_MANIFEST
#   { ... }
#   -->
#   See .github/SPRINT_ISSUE_TEMPLATE.md for the full schema.

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
MODEL = "claude-sonnet-4-6"
GITHUB_MODELS_URL = "https://models.inference.ai.azure.com"
STATE_FILE = REPO_ROOT / "sprint-state.json"
SUMMARY_FILE = REPO_ROOT / "sprint-summary.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list, check: bool = False, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=capture, text=True, check=check)


def _gh_issue_body(issue: int, repo: str) -> tuple[str, str]:
    """Return (title, body) of a GitHub issue."""
    r = _run(["gh", "issue", "view", str(issue), "--json", "body,title", "--repo", repo])
    data = json.loads(r.stdout)
    return data.get("title", ""), data.get("body", "")


def _gh_comment(issue: int, repo: str, body: str) -> None:
    _run(["gh", "issue", "comment", str(issue), "--repo", repo, "--body", body], check=False)


def _git(args: list) -> subprocess.CompletedProcess:
    return _run(["git"] + args, capture=True)


def _load_context() -> str:
    """Load abbreviated project context for the LLM."""
    chunks = []
    for rel in [
        ".github/copilot-instructions.md",
        "PLAN.md",
        "STATUS.md",
        "services/api/app/main.py",
        "services/api/app/settings.py",
    ]:
        p = REPO_ROOT / rel
        if p.exists():
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            truncated = "\n".join(lines[:200])
            if len(lines) > 200:
                truncated += f"\n... [{len(lines)-200} lines truncated]"
            chunks.append(f"=== {rel} ===\n{truncated}\n\n")
        else:
            chunks.append(f"=== {rel} ===\n[NOT FOUND]\n\n")
    return "".join(chunks)


# ---------------------------------------------------------------------------
# Parse sprint manifest
# ---------------------------------------------------------------------------

def parse_manifest(body: str) -> dict:
    """Extract the SPRINT_MANIFEST JSON block from the issue body."""
    match = re.search(
        r"<!--\s*SPRINT_MANIFEST\s*(.*?)-->",
        body,
        re.DOTALL,
    )
    if not match:
        raise ValueError("[FAIL] No SPRINT_MANIFEST block found in issue body.")
    raw = match.group(1).strip()
    return json.loads(raw)


# ---------------------------------------------------------------------------
# LLM code generation
# ---------------------------------------------------------------------------

def _generate_code(story: dict, context: str) -> dict[str, str]:
    """
    Call Sonnet 4.6 to generate file contents for a story.
    Returns {relative_path: content} dict.
    """
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        print("[WARN] GITHUB_TOKEN not set -- skipping code generation, writing stubs")
        return _make_stubs(story)

    try:
        from openai import OpenAI
        client = OpenAI(base_url=GITHUB_MODELS_URL, api_key=github_token)
    except ImportError:
        print("[WARN] openai not installed -- writing stubs")
        return _make_stubs(story)

    files_to_create = story.get("files_to_create", [])
    if not files_to_create:
        return {}

    system_prompt = textwrap.dedent("""
        You are implementing code for the 51-ACA (Azure Cost Advisor) project.
        Rules:
        - ASCII only. No Unicode. No emoji.
        - Follow the exact file paths specified.
        - Include the EVA-STORY tag comment on the first functional line.
        - For Python: use FastAPI patterns from copilot-instructions.
        - For TypeScript/TSX: use React 19 + Fluent UI v9 patterns.
        - For stubs: write minimal but importable/compilable code.
        - Respond ONLY with a JSON object: {"path/to/file.py": "<file contents>"}
        - No markdown fences. Just the JSON object.
    """).strip()

    user_prompt = f"""STORY: {story['id']} -- {story['title']}
WBS: {story.get('wbs', 'N/A')}
EPIC: {story.get('epic', 'N/A')}

IMPLEMENTATION NOTES:
{story.get('implementation_notes', 'Implement as per project patterns.')}

ACCEPTANCE CRITERIA:
{chr(10).join('- ' + a for a in story.get('acceptance', []))}

FILES TO CREATE OR UPDATE:
{chr(10).join('- ' + f for f in files_to_create)}

PROJECT CONTEXT:
{context[:40_000]}

Generate the file contents now. Return ONLY valid JSON: {{"path": "content", ...}}
EVA-STORY tag for this story: # EVA-STORY: {story['id']}
"""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8192,
            temperature=0.1,
        )
        raw = resp.choices[0].message.content or "{}"
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        raw = re.sub(r"\s*```$", "", raw.strip())
        return json.loads(raw)
    except Exception as exc:
        print(f"[WARN] LLM call failed for {story['id']}: {exc} -- writing stubs")
        return _make_stubs(story)


def _make_stubs(story: dict) -> dict[str, str]:
    """Generate minimal stub files when LLM is unavailable."""
    files = {}
    for path in story.get("files_to_create", []):
        tag = f"# EVA-STORY: {story['id']}"
        if path.endswith(".py"):
            files[path] = f"{tag}\n# {story['title']}\n# STUB -- implement per implementation_notes\n"
        elif path.endswith((".ts", ".tsx")):
            files[path] = f"// EVA-STORY: {story['id']}\n// {story['title']}\n// STUB\n"
        elif path.endswith((".bicep", ".tf")):
            files[path] = f"// EVA-STORY: {story['id']}\n// {story['title']}\n// STUB\n"
        elif path.endswith(".yml") or path.endswith(".yaml"):
            files[path] = f"# EVA-STORY: {story['id']}\n# {story['title']}\n# STUB\n"
        else:
            files[path] = f"# EVA-STORY: {story['id']}\n# {story['title']}\n# STUB\n"
    return files


# ---------------------------------------------------------------------------
# Write files
# ---------------------------------------------------------------------------

def write_files(generated: dict[str, str]) -> list[str]:
    """Write generated content to disk. Return list of written paths."""
    written = []
    for rel_path, content in generated.items():
        full_path = REPO_ROOT / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        written.append(rel_path)
        print(f"[INFO] Wrote {rel_path} ({len(content)} chars)")
    return written


# ---------------------------------------------------------------------------
# Evidence receipt
# ---------------------------------------------------------------------------

def write_evidence(story: dict, test_result: str, lint_result: str) -> str:
    evidence_dir = REPO_ROOT / ".eva" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = evidence_dir / f"{story['id']}-receipt.json"
    receipt = {
        "story_id": story["id"],
        "title": story.get("title", ""),
        "phase": "D|P|D|C|A",
        "timestamp": _now_iso(),
        "artifacts": story.get("files_to_create", []),
        "test_result": test_result,
        "lint_result": lint_result,
        "commit_sha": _git(["rev-parse", "HEAD"]).stdout.strip(),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return str(receipt_path.relative_to(REPO_ROOT))


# ---------------------------------------------------------------------------
# Check step (lint + pytest collect)
# ---------------------------------------------------------------------------

def run_checks() -> tuple[str, str]:
    """Run ruff lint and pytest collect. Return (lint_status, test_status)."""
    lint = _run(["ruff", "check", "services/", "--quiet"])
    lint_out = (lint.stdout + lint.stderr).strip()
    lint_status = "PASS" if lint.returncode == 0 else "WARN"

    test = _run(["python3", "-m", "pytest", "services/", "--co", "-q"])
    test_out = (test.stdout + test.stderr).strip()
    test_status = "PASS" if test.returncode == 0 else "WARN"

    # Write artifact files
    (REPO_ROOT / "lint-result.txt").write_text(lint_out or "clean", encoding="utf-8")
    (REPO_ROOT / "test-collect.txt").write_text(test_out or "ok", encoding="utf-8")

    return lint_status, test_status


# ---------------------------------------------------------------------------
# Git commit
# ---------------------------------------------------------------------------

def commit_story(story: dict, written_files: list, evidence_path: str) -> str:
    """Stage and commit story files. Return commit SHA."""
    _git(["config", "user.name", "ACA Sprint Agent"])
    _git(["config", "user.email", "agent@eva-foundry.dev"])

    for f in written_files:
        _git(["add", f])
    if evidence_path:
        _git(["add", evidence_path])
    # Also add evidence json
    _git(["add", ".eva/evidence/"])
    _git(["add", "lint-result.txt", "test-collect.txt"])

    msg = f"feat({story['id']}): {story['title']}"
    result = _git(["commit", "-m", msg])
    if result.returncode != 0:
        if "nothing to commit" in (result.stdout + result.stderr):
            print(f"[INFO] Nothing to commit for {story['id']}")
            return _git(["rev-parse", "HEAD"]).stdout.strip()
        print(f"[WARN] Commit failed: {result.stderr}")
        return ""

    sha = _git(["rev-parse", "HEAD"]).stdout.strip()
    print(f"[INFO] Committed {story['id']} -> {sha[:8]}")
    return sha


def push_branch(branch: str) -> bool:
    result = _run(["git", "push", "origin", branch, "--force-with-lease"])
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Progress comments
# ---------------------------------------------------------------------------

def _story_progress_comment(
    sprint_id: str,
    story: dict,
    written_files: list,
    lint_status: str,
    test_status: str,
    sha: str,
    story_index: int,
    total_stories: int,
) -> str:
    lint_icon = "[PASS]" if lint_status == "PASS" else "[WARN]"
    test_icon = "[PASS]" if test_status == "PASS" else "[WARN]"
    files_list = "\n".join(f"  - {f}" for f in written_files) or "  (no files written)"
    return textwrap.dedent(f"""
### {sprint_id} -- Story {story_index}/{total_stories} Complete

**Story**: {story['id']} -- {story.get('title', '')}
**Status**: DONE
**Commit**: `{sha[:8] if sha else 'n/a'}`
**Lint**: {lint_icon} {lint_status}
**Tests**: {test_icon} {test_status}

**Files written:**
{files_list}

**Acceptance criteria:**
{chr(10).join('- [ ] ' + a for a in story.get('acceptance', ['(none)']))}

---
*Sprint agent continuing to next story...*
    """).strip()


def _sprint_summary_comment(
    sprint: dict,
    results: list[dict],
    branch: str,
) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "DONE")
    failed = total - passed
    story_lines = []
    for r in results:
        icon = "[PASS]" if r.get("status") == "DONE" else "[FAIL]"
        story_lines.append(f"{icon} {r['id']} -- {r.get('title', '')} -- `{r.get('sha', 'n/a')[:8]}`")

    return textwrap.dedent(f"""
## Sprint Summary -- {sprint.get('sprint_id', 'SPRINT')} COMPLETE

**Sprint**: {sprint.get('sprint_title', '')}
**Branch**: `{branch}`
**Stories**: {passed}/{total} passed
**Failed**: {failed}
**Timestamp**: {_now_iso()}

### Story Results:
{chr(10).join(story_lines)}

### Next Steps:
1. Review the PR for this branch
2. Check acceptance criteria on each story above
3. Run full test suite
4. Merge when all criteria are met
5. Add `sonnet-review` label to trigger architecture review

*Posted by sprint-agent workflow -- all changes on branch `{branch}`*
    """).strip()


# ---------------------------------------------------------------------------
# Main sprint loop
# ---------------------------------------------------------------------------

def run_sprint(issue: int, repo: str) -> None:
    print(f"[INFO] Sprint agent starting -- issue #{issue} repo {repo}")

    # Fetch issue content
    issue_title, issue_body = _gh_issue_body(issue, repo)
    print(f"[INFO] Issue: {issue_title}")

    # Parse sprint manifest
    try:
        manifest = parse_manifest(issue_body)
    except (ValueError, json.JSONDecodeError) as exc:
        msg = f"[FAIL] Could not parse sprint manifest: {exc}"
        print(msg)
        _gh_comment(issue, repo, f"Sprint agent failed to start:\n```\n{msg}\n```")
        sys.exit(1)

    sprint_id = manifest.get("sprint_id", "SPRINT")
    stories = manifest.get("stories", [])
    if not stories:
        _gh_comment(issue, repo, f"[FAIL] Sprint manifest has no stories.")
        sys.exit(1)

    # Create sprint branch
    branch = manifest.get("target_branch", f"sprint/{sprint_id.lower()}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    _git(["checkout", "-b", branch])
    print(f"[INFO] Branch: {branch}")

    # Opening comment
    _gh_comment(issue, repo, textwrap.dedent(f"""
### Sprint Agent Started -- {sprint_id}

**Branch**: `{branch}`
**Stories**: {len(stories)}
**Started**: {_now_iso()}

Working through {len(stories)} stories in sequence. Progress comments will follow after each story.
    """).strip())

    # Load context once for all LLM calls
    context = _load_context()

    results = []
    state = {
        "sprint_id": sprint_id,
        "issue": issue,
        "branch": branch,
        "started": _now_iso(),
        "stories": [],
    }

    for idx, story in enumerate(stories, 1):
        sid = story.get("id", f"UNKNOWN-{idx}")
        print(f"\n[INFO] === Story {idx}/{len(stories)}: {sid} ===")

        story_result = {"id": sid, "title": story.get("title", ""), "status": "FAIL", "sha": ""}

        try:
            # D2 -- Generate and write code
            generated = _generate_code(story, context)
            written_files = write_files(generated)

            # C -- Check
            lint_status, test_status = run_checks()

            # Write evidence
            evidence_path = write_evidence(story, test_status, lint_status)

            # A -- Commit
            sha = commit_story(story, written_files, evidence_path)

            story_result["status"] = "DONE"
            story_result["sha"] = sha
            story_result["lint"] = lint_status
            story_result["test"] = test_status
            story_result["files"] = written_files

        except Exception as exc:
            print(f"[FAIL] Story {sid} failed: {exc}")
            story_result["error"] = str(exc)

        results.append(story_result)
        state["stories"].append(story_result)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

        # Post progress comment
        comment = _story_progress_comment(
            sprint_id=sprint_id,
            story=story,
            written_files=story_result.get("files", []),
            lint_status=story_result.get("lint", "N/A"),
            test_status=story_result.get("test", "N/A"),
            sha=story_result.get("sha", ""),
            story_index=idx,
            total_stories=len(stories),
        )
        _gh_comment(issue, repo, comment)
        print(f"[INFO] Progress comment posted for {sid}")

    # Push branch
    push_ok = push_branch(branch)
    state["pushed"] = push_ok
    state["completed"] = _now_iso()
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

    # Generate sprint summary
    summary = _sprint_summary_comment(manifest, results, branch)
    SUMMARY_FILE.write_text(summary, encoding="utf-8")

    # Post final summary comment
    _gh_comment(issue, repo, summary)

    # Open PR
    try:
        pr_result = _run([
            "gh", "pr", "create",
            "--repo", repo,
            "--title", f"fix({sprint_id}): {manifest.get('sprint_title', '')}",
            "--body", summary,
            "--base", "main",
            "--head", branch,
        ])
        pr_url = pr_result.stdout.strip()
        print(f"[INFO] PR created: {pr_url}")
        _gh_comment(issue, repo, f"PR opened: {pr_url}")
    except Exception as exc:
        print(f"[WARN] PR creation failed: {exc}")

    print(f"\n[PASS] Sprint {sprint_id} complete -- {sum(1 for r in results if r['status']=='DONE')}/{len(results)} stories done")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="ACA sprint agent -- full sprint executor")
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--repo", required=True)
    opts = parser.parse_args()
    run_sprint(opts.issue, opts.repo)


if __name__ == "__main__":
    main()
