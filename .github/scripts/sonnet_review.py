#!/usr/bin/env python3
# EVA-STORY: ACA-14-008
# sonnet_review.py -- Cloud architecture review runner
# Calls Claude Sonnet 4.6 via GitHub Models API, posts findings as issue comment.
#
# Mode 1 -- load context:
#   python3 sonnet_review.py --load-context --out /tmp/review-context.txt
#
# Mode 2 -- run review:
#   python3 sonnet_review.py --review --issue 6 \
#       --context /tmp/review-context.txt --repo eva-foundry/51-ACA

import argparse
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent  # .github/scripts -> repo root
MODEL = "claude-sonnet-4-6"
GITHUB_MODELS_URL = "https://models.inference.ai.azure.com"
MAX_LINES_PER_FILE = 300

# Files loaded into context for the review agent
DIRECT_FILES = [
    "AGENTS.md",
    ".github/copilot-instructions.md",
    "PLAN.md",
    "STATUS.md",
    "ACCEPTANCE.md",
    "services/api/app/routers/admin.py",
    "services/api/app/routers/auth.py",
    "services/api/app/routers/checkout.py",
    "services/api/app/routers/findings.py",
    "services/api/app/routers/health.py",
    "services/api/app/routers/scans.py",
    "services/api/app/main.py",
    "services/api/app/settings.py",
    "services/api/requirements.txt",
    "services/collector/app/main.py",
    "services/analysis/app/main.py",
    "services/delivery/app/main.py",
    ".eva/trust.json",
    ".eva/veritas-plan.json",
]

GLOB_DIRS = [
    ("services/api/app/db", "*.py"),
    ("services/api/app/middleware", "*.py"),
    ("services/api/app/models", "*.py"),
    ("frontend/src/pages", "*.tsx"),
    ("frontend/src/hooks", "*.ts"),
    ("infra/phase1-marco", "*.bicep"),
]


def _read_truncated(path: Path, label: str) -> str:
    if not path.exists():
        return f"=== {label} ===\n[FILE NOT FOUND: {path}]\n\n"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if len(lines) > MAX_LINES_PER_FILE:
            kept = lines[:MAX_LINES_PER_FILE]
            kept.append(f"... [{len(lines) - MAX_LINES_PER_FILE} lines truncated]")
            content = "\n".join(kept)
        else:
            content = "\n".join(lines)
        return f"=== {label} ===\n{content}\n\n"
    except Exception as exc:
        return f"=== {label} ===\n[READ ERROR: {exc}]\n\n"


def load_context(out_path: str) -> None:
    """Assemble context from repo files and write to out_path."""
    chunks = []
    chunks.append("=== ACA REVIEW CONTEXT ===\n\n")

    # Direct files
    for rel in DIRECT_FILES:
        path = REPO_ROOT / rel
        chunks.append(_read_truncated(path, rel))

    # Glob directories
    for dir_rel, pattern in GLOB_DIRS:
        dir_path = REPO_ROOT / dir_rel
        if dir_path.exists():
            for fpath in sorted(dir_path.glob(pattern)):
                rel_label = str(fpath.relative_to(REPO_ROOT))
                chunks.append(_read_truncated(fpath, rel_label))
        else:
            chunks.append(f"=== {dir_rel}/{pattern} ===\n[DIR NOT FOUND]\n\n")

    # Inline endpoint table (known ground truth)
    chunks.append(_build_endpoint_table())

    context = "".join(chunks)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(context, encoding="utf-8")
    size_kb = len(context.encode()) // 1024
    print(f"[INFO] Context written to {out_path} ({size_kb} KB, {len(chunks)} sections)")


def _build_endpoint_table() -> str:
    """Embed the known data model endpoint table as context."""
    return textwrap.dedent("""
=== DATA MODEL ENDPOINT TABLE (ground truth from /model/endpoints) ===

IMPLEMENTED (14):
  GET  /health
  GET  /v1/admin/stats
  GET  /v1/checkout/entitlements
  GET  /v1/findings/{scan_id}
  GET  /v1/scans/
  GET  /v1/scans/{scan_id}
  POST /v1/auth/connect
  POST /v1/auth/disconnect
  POST /v1/auth/preflight
  POST /v1/checkout/tier2
  POST /v1/checkout/tier3
  POST /v1/checkout/webhook
  POST /v1/scans/
  DELETE /v1/admin/scans/{scan_id}

STUB (13 -- not yet implemented):
  GET  /v1/admin/customers
  GET  /v1/admin/kpis
  GET  /v1/admin/runs
  GET  /v1/billing/portal
  GET  /v1/collect/status
  GET  /v1/entitlements
  GET  /v1/reports/tier1
  POST /v1/admin/entitlements/grant
  POST /v1/admin/stripe/reconcile
  POST /v1/admin/subscriptions/{subscriptionId}/lock
  POST /v1/billing/checkout
  POST /v1/collect/start
  POST /v1/webhooks/stripe

""")


def run_review(issue: int, context_path: str, repo: str) -> None:
    """Call Sonnet 4.6 with issue body + context, post result as issue comment."""
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        print("[FAIL] GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    # Read issue body
    try:
        result = subprocess.run(
            ["gh", "issue", "view", str(issue), "--json", "body,title", "--repo", repo],
            capture_output=True, text=True, check=True
        )
        issue_data = json.loads(result.stdout)
        issue_body = issue_data.get("body", "")
        issue_title = issue_data.get("title", f"Issue #{issue}")
    except Exception as exc:
        print(f"[FAIL] Could not read issue: {exc}", file=sys.stderr)
        sys.exit(1)

    # Read context
    try:
        context_content = Path(context_path).read_text(encoding="utf-8")
    except Exception as exc:
        print(f"[FAIL] Could not read context file: {exc}", file=sys.stderr)
        sys.exit(1)

    # Truncate context if too large (keep first 80 KB)
    MAX_CONTEXT_BYTES = 80_000
    if len(context_content.encode()) > MAX_CONTEXT_BYTES:
        context_content = context_content.encode()[:MAX_CONTEXT_BYTES].decode("utf-8", errors="replace")
        context_content += "\n... [context truncated at 80 KB]"

    system_prompt = textwrap.dedent("""
        You are a senior software architect reviewing the 51-ACA (Azure Cost Advisor) project.
        You have access to the project context below.
        Respond with a structured architecture review using the exact format specified in the task.
        Be specific: reference actual file paths, endpoint IDs, and story IDs from the context.
        Use plain ASCII only. No Unicode. No emoji.
        Section headers: use === SECTION NAME === format.
        Keep the review actionable and grounded in the actual codebase state.
    """).strip()

    user_prompt = f"""TASK (from issue #{issue}: {issue_title}):

{issue_body}

---
PROJECT CONTEXT:

{context_content}
"""

    # Call GitHub Models API (Sonnet 4.6)
    try:
        from openai import OpenAI
    except ImportError:
        print("[FAIL] openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(
        base_url=GITHUB_MODELS_URL,
        api_key=github_token,
    )

    print(f"[INFO] Calling {MODEL} via GitHub Models API...")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=4096,
            temperature=0.2,
        )
        review_text = response.choices[0].message.content or "[WARN] Empty response"
    except Exception as exc:
        review_text = f"[FAIL] Model call failed: {exc}"
        print(f"[FAIL] {exc}", file=sys.stderr)

    # Write raw output to artifact
    output_path = "/tmp/review-output.txt"
    Path(output_path).write_text(review_text, encoding="utf-8")
    print(f"[INFO] Review written to {output_path} ({len(review_text)} chars)")

    # Format comment for GitHub issue
    comment = f"""### ACA Sprint 2 Architecture Review
**Model**: Claude Sonnet 4.6 via GitHub Models API
**Issue**: #{issue}
**Context size**: {len(context_content.encode()) // 1024} KB

---

{review_text}

---
*Posted by sonnet-review workflow -- READ ONLY -- no code changes made*
"""

    # Post as issue comment
    try:
        subprocess.run(
            ["gh", "issue", "comment", str(issue),
             "--repo", repo,
             "--body", comment],
            check=True
        )
        print(f"[PASS] Comment posted to issue #{issue}")
    except Exception as exc:
        print(f"[FAIL] Could not post comment: {exc}", file=sys.stderr)
        # Still exit 0 so the artifact is preserved
        print("[INFO] Review saved to artifact even though comment failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="ACA Sonnet architecture review runner")
    subparsers = parser.add_subparsers(dest="mode")

    # Load context mode
    ctx_parser = subparsers.add_parser("--load-context", help="Load repo context to file")
    ctx_parser.add_argument("--out", required=True, help="Output file path")

    # Review mode
    rev_parser = subparsers.add_parser("--review", help="Run review and post to issue")
    rev_parser.add_argument("--issue", required=True, type=int, help="Issue number")
    rev_parser.add_argument("--context", required=True, help="Context file path")
    rev_parser.add_argument("--repo", required=True, help="owner/repo")

    # Support both --load-context and --review as flags (not subcommands)
    # because the workflow calls them as flags
    args, remaining = parser.parse_known_args()

    # Re-parse as flat flags
    flat = argparse.ArgumentParser()
    flat.add_argument("--load-context", action="store_true")
    flat.add_argument("--out", default=None)
    flat.add_argument("--review", action="store_true")
    flat.add_argument("--issue", type=int, default=None)
    flat.add_argument("--context", default=None)
    flat.add_argument("--repo", default=None)
    opts = flat.parse_args()

    if opts.load_context:
        if not opts.out:
            print("[FAIL] --load-context requires --out", file=sys.stderr)
            sys.exit(1)
        load_context(opts.out)
    elif opts.review:
        if not opts.issue or not opts.context or not opts.repo:
            print("[FAIL] --review requires --issue, --context, --repo", file=sys.stderr)
            sys.exit(1)
        run_review(opts.issue, opts.context, opts.repo)
    else:
        flat.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
