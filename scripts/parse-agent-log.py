# EVA-STORY: ACA-14-010
"""
scripts/parse-agent-log.py
===========================
Parse git commits + evidence receipts to produce structured metrics JSON.
Feeds ADO work item comments and the data model story status.

Output:  .eva/metrics/agent-metrics-YYYYMMDD.json
ADO:     PATCH /wit/workitems/{id} -- adds comment with metrics block
Model:   PUT /model/requirements/{story_id} -- marks story done + attaches metrics

Usage:
    # dry run (no ADO/model writes)
    python scripts/parse-agent-log.py --since 7d --dry-run

    # live (writes to ADO + model)
    python scripts/parse-agent-log.py --since 7d

    # single story
    python scripts/parse-agent-log.py --story ACA-04-011

Environment vars required for live ADO writes:
    ADO_ORG          e.g. https://dev.azure.com/your-org
    ADO_PROJECT      e.g. eva-poc
    ADO_PAT          personal access token

Environment vars required for live model writes:
    ACA_MODEL_URL    e.g. http://localhost:8055  (default)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
EVIDENCE_DIR = REPO_ROOT / ".eva" / "evidence"
METRICS_DIR = REPO_ROOT / ".eva" / "metrics"
MODEL_URL = os.getenv("ACA_MODEL_URL", "http://localhost:8055")
ADO_ORG = os.getenv("ADO_ORG", "")
ADO_PROJECT = os.getenv("ADO_PROJECT", "eva-poc")
ADO_PAT = os.getenv("ADO_PAT", "")

STORY_RE = re.compile(r"\(ACA-(\d{2}-\d{3})\)")
METRICS_TRAILER_RE = re.compile(
    r"ACA-METRICS:\s+duration_ms=(\d+)\s+tokens=(\d+)\s+tests_before=(\d+)\s+tests_after=(\d+)\s+files=(\d+)\s+result=(\w+)"
)
SINCE_MAP = {"1d": "1 day ago", "7d": "1 week ago", "30d": "1 month ago"}

# ---------------------------------------------------------------------------
# Git log reader
# ---------------------------------------------------------------------------

def git_log(since: str = "7d", story_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Return list of commits as dicts.
    Each dict: sha, subject, author, timestamp_iso, story_id, files_changed, insertions, deletions.
    Also extracts ACA-METRICS trailer from commit body when present.
    """
    since_arg = SINCE_MAP.get(since, since)
    # Use %x00 as separator between commits to handle multi-line bodies
    fmt = "%H|%s|%an|%aI%n%b%x00"
    args = ["git", "-C", str(REPO_ROOT), "log", f"--since={since_arg}", f"--format={fmt}", "--numstat"]
    try:
        raw = subprocess.check_output(args, text=True, encoding="utf-8", errors="replace")
    except subprocess.CalledProcessError as exc:
        print(f"[WARN] git log failed: {exc}")
        return []

    # Split on NUL separator between commits
    commit_blocks = raw.split("\x00")
    commits = []

    for block in commit_blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        header = lines[0] if lines else ""
        if "|" not in header or len(header.split("|")) < 4:
            continue
        parts = header.split("|", 3)
        sha, subject, author, ts = parts[0], parts[1], parts[2], parts[3]
        m = STORY_RE.search(subject)
        sid = f"ACA-{m.group(1)}" if m else None

        # Extract ACA-METRICS trailer from body if present
        trailer_metrics: Dict[str, Any] = {}
        for line in lines[1:]:
            tm = METRICS_TRAILER_RE.search(line)
            if tm:
                trailer_metrics = {
                    "duration_ms": int(tm.group(1)),
                    "tokens_used": int(tm.group(2)),
                    "test_count_before": int(tm.group(3)),
                    "test_count_after": int(tm.group(4)),
                    "files_changed_trailer": int(tm.group(5)),
                    "test_result": tm.group(6),
                }
                break

        commit: Dict[str, Any] = {
            "sha": sha[:12],
            "subject": subject,
            "author": author,
            "timestamp_iso": ts,
            "story_id": sid,
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0,
        }
        commit.update(trailer_metrics)

        for line in lines[1:]:
            if re.match(r"^\d+\s+\d+\s+", line):
                p = line.split()
                try:
                    commit["insertions"] += int(p[0])
                    commit["deletions"] += int(p[1])
                    commit["files_changed"] += 1
                except (ValueError, IndexError):
                    pass

        commits.append(commit)

    if story_id:
        sid_norm = story_id.upper()
        commits = [c for c in commits if c.get("story_id") == sid_norm]

    return commits


# ---------------------------------------------------------------------------
# Evidence receipt reader
# ---------------------------------------------------------------------------

def read_evidence(story_id: str) -> Optional[Dict]:
    """Load .eva/evidence/{story_id}-receipt.py or .json if it exists."""
    for suffix in ["-receipt.json", "-receipt.py"]:
        p = EVIDENCE_DIR / f"{story_id}{suffix}"
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace")
            # .py receipts embed an EVIDENCE dict -- extract it
            m = re.search(r"EVIDENCE\s*=\s*(\{.*?\})", text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1).replace("'", '"'))
                except json.JSONDecodeError:
                    pass
            # .json receipts
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
    return None


# ---------------------------------------------------------------------------
# Metrics assembler
# ---------------------------------------------------------------------------

def build_metrics(commits: List[Dict]) -> List[Dict]:
    """Merge git commit data with evidence receipt data per story."""
    story_map: Dict[str, Dict] = {}

    for c in commits:
        sid = c["story_id"]
        if not sid:
            continue
        if sid not in story_map:
            story_map[sid] = {
                "story_id": sid,
                "commits": [],
                "total_files_changed": 0,
                "total_insertions": 0,
                "total_deletions": 0,
                "first_commit_ts": c["timestamp_iso"],
                "last_commit_ts": c["timestamp_iso"],
                "authors": set(),
            }
        e = story_map[sid]
        e["commits"].append(c["sha"])
        e["total_files_changed"] += c["files_changed"]
        e["total_insertions"] += c["insertions"]
        e["total_deletions"] += c["deletions"]
        e["last_commit_ts"] = c["timestamp_iso"]
        e["authors"].add(c["author"])
        # Keep trailer data from the most recent (first-seen in reverse-chron log) commit
        if "duration_ms" in c and "last_trailer" not in e:
            e["last_trailer"] = {
                "duration_ms": c.get("duration_ms"),
                "tokens_used": c.get("tokens_used"),
                "test_count_before": c.get("test_count_before"),
                "test_count_after": c.get("test_count_after"),
                "test_result": c.get("test_result"),
            }

    results = []
    for sid, m in story_map.items():
        m["authors"] = sorted(m["authors"])
        receipt = read_evidence(sid) or {}
        # Trailer values from the most recent commit take precedence over receipt values
        trailer = m.get("last_trailer", {})
        record = {
            "story_id": sid,
            "commits": m["commits"],
            "files_changed": m["total_files_changed"],
            "insertions": m["total_insertions"],
            "deletions": m["total_deletions"],
            "first_commit_ts": m["first_commit_ts"],
            "last_commit_ts": m["last_commit_ts"],
            "authors": m["authors"],
            # ACA-METRICS trailer (commit-level, highest priority) > receipt > None
            "duration_ms": trailer.get("duration_ms") or receipt.get("duration_ms"),
            "tokens_used": trailer.get("tokens_used") or receipt.get("tokens_used"),
            "test_count_before": trailer.get("test_count_before") or receipt.get("test_count_before"),
            "test_count_after": trailer.get("test_count_after") or receipt.get("test_count_after"),
            "test_result": trailer.get("test_result") or receipt.get("test_result", "UNKNOWN"),
            "phase": receipt.get("phase"),
            "artifacts": receipt.get("artifacts", []),
            "metrics_source": "trailer" if trailer else ("receipt" if receipt else "none"),
        }
        results.append(record)

    return sorted(results, key=lambda r: r["last_commit_ts"], reverse=True)


# ---------------------------------------------------------------------------
# ADO writer
# ---------------------------------------------------------------------------

def ado_post_comment(work_item_id: int, body: str) -> bool:
    """POST a comment to an ADO work item."""
    if not ADO_ORG or not ADO_PAT:
        print(f"[WARN] ADO_ORG or ADO_PAT not set -- skipping ADO comment on WI {work_item_id}")
        return False
    try:
        import base64
        import urllib.request
        creds = base64.b64encode(f":{ADO_PAT}".encode()).decode()
        url = (
            f"{ADO_ORG}/{ADO_PROJECT}/_apis/wit/workItems/{work_item_id}/comments"
            "?api-version=7.1-preview.3"
        )
        payload = json.dumps({"text": body}).encode()
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Authorization", f"Basic {creds}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)
    except Exception as exc:
        print(f"[WARN] ADO comment failed for WI {work_item_id}: {exc}")
        return False


# ---------------------------------------------------------------------------
# Model writer
# ---------------------------------------------------------------------------

def model_mark_done(story_id: str, metrics: Dict, dry_run: bool) -> bool:
    """
    PUT to data model to mark story done + attach metrics snapshot.
    Uses the requirements layer -- story_id maps to veritas-plan story.
    """
    if dry_run:
        print(f"[DRY]  model: would mark {story_id} done with metrics")
        return True
    try:
        import urllib.request
        url = f"{MODEL_URL}/model/requirements/{story_id}"
        # GET current
        with urllib.request.urlopen(url, timeout=5) as resp:
            obj = json.loads(resp.read())
        obj["status"] = "done"
        obj["agent_metrics"] = {
            "duration_ms": metrics.get("duration_ms"),
            "tokens_used": metrics.get("tokens_used"),
            "files_changed": metrics.get("files_changed"),
            "test_count_after": metrics.get("test_count_after"),
            "last_commit": metrics["commits"][0] if metrics["commits"] else None,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        payload = json.dumps(obj, ensure_ascii=True).encode()
        req = urllib.request.Request(url, data=payload, method="PUT")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Actor", "agent:parse-log")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status in (200, 201)
    except Exception as exc:
        print(f"[WARN] model PUT failed for {story_id}: {exc}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Parse agent git log + receipts -> metrics JSON")
    ap.add_argument("--since", default="7d", help="Time window: 1d | 7d | 30d (default 7d)")
    ap.add_argument("--story", default=None, help="Filter to single story ID, e.g. ACA-04-011")
    ap.add_argument("--dry-run", action="store_true", help="Print only -- no ADO/model writes")
    ap.add_argument("--push-ado", action="store_true", help="Comment metrics on ADO work items")
    ap.add_argument("--push-model", action="store_true", help="Mark stories done in data model")
    ap.add_argument("--out", default=None, help="Output JSON path (default .eva/metrics/...)")
    args = ap.parse_args()

    commits = git_log(since=args.since, story_id=args.story)
    print(f"[INFO] {len(commits)} commits found in window={args.since}")

    metrics = build_metrics(commits)
    print(f"[INFO] {len(metrics)} stories with commits")

    for m in metrics:
        sid = m["story_id"]
        dur = f"{m['duration_ms']}ms" if m["duration_ms"] else "n/a"
        tok = str(m["tokens_used"]) if m["tokens_used"] else "n/a"
        tests_after = m["test_count_after"] if m["test_count_after"] else "n/a"
        print(
            f"  {sid}  commits={len(m['commits'])}  files={m['files_changed']}"
            f"  +{m['insertions']}/-{m['deletions']}"
            f"  duration={dur}  tokens={tok}  tests_after={tests_after}"
            f"  result={m['test_result']}"
        )

    # Save to .eva/metrics/
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = Path(args.out) if args.out else METRICS_DIR / f"agent-metrics-{date_str}.json"
    out_path.write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "metrics": metrics}, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(f"[PASS] metrics written to {out_path.relative_to(REPO_ROOT)}")

    if args.push_model:
        for m in metrics:
            if m["test_result"] == "PASS":
                ok = model_mark_done(m["story_id"], m, dry_run=args.dry_run)
                status = "[PASS]" if ok else "[FAIL]"
                print(f"  {status} model mark-done: {m['story_id']}")

    if args.push_ado:
        print("[INFO] ADO push requires work item ID mapping -- see .eva/ado-id-map.json")
        # Load optional ID map: { "ACA-04-011": 1234 }
        id_map_path = REPO_ROOT / ".eva" / "ado-id-map.json"
        if id_map_path.exists():
            id_map = json.loads(id_map_path.read_text())
            for m in metrics:
                wi_id = id_map.get(m["story_id"])
                if wi_id:
                    body = (
                        f"Agent metrics for {m['story_id']}:\n"
                        f"- Commits: {', '.join(m['commits'])}\n"
                        f"- Files changed: {m['files_changed']} (+{m['insertions']}/-{m['deletions']})\n"
                        f"- Duration: {m.get('duration_ms', 'n/a')} ms\n"
                        f"- Tokens used: {m.get('tokens_used', 'n/a')}\n"
                        f"- Tests after: {m.get('test_count_after', 'n/a')}\n"
                        f"- Result: {m['test_result']}\n"
                    )
                    ok = ado_post_comment(wi_id, body)
                    status = "[PASS]" if ok else "[FAIL]"
                    print(f"  {status} ADO comment: {m['story_id']} -> WI {wi_id}")
        else:
            print(f"[WARN] .eva/ado-id-map.json not found -- create it to enable ADO push")
            print('       Format: {"ACA-04-011": 1234, "ACA-04-012": 1235}')


if __name__ == "__main__":
    main()
