#!/usr/bin/env python3
# EVA-STORY: ACA-14-009
# EVA-STORY: ACA-12-022
# sprint_agent.py -- Full-sprint cloud execution runner
#
# Sprint 3 Enhancements (+180 lines):
#   - Veritas evidence receipts (duration_ms, tokens_used, test_count_before/after, files_changed)
#   - ADO bidirectional sync (4 integration points, Basic auth)
#   - Retry logic with exponential backoff (5s, 10s, 20s)  
#   - Enhanced sprint summary dashboard (metrics table, velocity trending)
#   - Parallel execution infrastructure (ThreadPoolExecutor)
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
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Any, Optional

# EVA-STORY: ACA-14-001 -- Import SprintContext for unified tracing
try:
    from sprint_context import SprintContext
except ImportError:
    SprintContext = None
    print("[WARN] SprintContext not available -- LM tracing disabled")

# EVA-STORY: ACA-14-002 -- Import state_lock for idempotency guard
try:
    from state_lock import acquire_lock, release_lock
except ImportError:
    acquire_lock = None
    release_lock = None
    print("[WARN] state_lock not available -- idempotency guard disabled")

# EVA-STORY: ACA-14-003 -- Import phase_verifier for checkpoint validation
try:
    from phase_verifier import verify_phase
except ImportError:
    verify_phase = None
    print("[WARN] phase_verifier not available -- phase checkpoints disabled")

try:
    import requests
except ImportError:
    requests = None
    print("[WARN] requests not available -- data model integration disabled")

REPO_ROOT = Path(__file__).parent.parent.parent
# EVA-STORY: ACA-14-008 -- GitHub Models endpoint (GITHUB_TOKEN in CI grants access to these models:
# gpt-4o, gpt-4o-mini, Meta-Llama-3.1-405B-Instruct, Mistral-large-2407)
# Claude models (claude-sonnet-*) are NOT available via GITHUB_TOKEN -- use gpt-4o
MODEL = "gpt-4o"
GITHUB_MODELS_URL = "https://models.inference.ai.azure.com"

# EVA-STORY: ACA-14-009 -- Azure OpenAI fallback (when GITHUB_TOKEN absent)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")


def generate_correlation_id(sprint_num: str) -> str:
    """Generate correlation ID in format ACA-S{NN}-{YYYYMMDD}-{uuid[:8]}."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    unique = str(uuid.uuid4())[:8]
    return f"ACA-S{sprint_num}-{timestamp}-{unique}"
STATE_FILE = REPO_ROOT / "sprint-state.json"
SUMMARY_FILE = REPO_ROOT / "sprint-summary.md"

# Data model integration (local dev: port 8055, cloud: ENV var)
DATA_MODEL_API = os.getenv("ACA_DATA_MODEL_URL", "http://localhost:8055")
DATA_MODEL_ACTOR = "sprint-agent"
DATA_MODEL_ENABLED = requests is not None

# ADO integration (Azure DevOps REST API)
ADO_ORG_URL = "https://dev.azure.com/marcopresta"
ADO_PROJECT = "eva-poc"
ADO_PAT = os.getenv("ADO_PAT", "")
ADO_ENABLED = ADO_PAT and requests is not None

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 5
MAX_PARALLEL_STORIES = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list, check: bool = False, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=capture, text=True, check=check)


# ---------------------------------------------------------------------------
# Data Model API Client
# ---------------------------------------------------------------------------

def _api_call(method: str, path: str, json_data: dict = None) -> dict:
    """
    Generic data model API call with error handling.
    Returns empty dict on failure (graceful degradation).
    """
    if not DATA_MODEL_ENABLED:
        return {}
    headers = {"X-Actor": DATA_MODEL_ACTOR}
    url = f"{DATA_MODEL_API}{path}"
    try:
        response = requests.request(method, url, json=json_data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json() if response.text else {}
    except Exception as exc:
        print(f"[WARN] Data model API call failed: {method} {path} -- {exc}")
        return {}


def start_sprint(sprint_id: str, manifest: dict) -> bool:
    """
    Update sprint status to in_progress at workflow start.
    Creates sprint record if missing.
    """
    if not DATA_MODEL_ENABLED:
        return False
    
    # Check if sprint exists
    existing = _api_call("GET", f"/model/sprints/{sprint_id}")
    
    sprint_obj = {
        "id": sprint_id,
        "project_id": "51-ACA",
        "sprint_number": int(manifest.get("sprint_id", "SPRINT-0").split("-")[-1]),
        "sprint_title": manifest.get("sprint_title", ""),
        "status": "in_progress",
        "start_timestamp": _now_iso(),
        "story_count": len(manifest.get("stories", [])),
        "completion_pct": 0.0,
        "velocity": 0.0,
        "actual_duration_hours": 0.0,
        "epic_id": manifest.get("epic", ""),
        "target_branch": manifest.get("target_branch", "main"),
        "issue_number": manifest.get("issue_number", 0),
        "is_active": True,
    }
    
    # Merge with existing if present (preserve row_version)
    if existing and existing.get("id"):
        sprint_obj.update({k: v for k, v in existing.items() 
                          if k not in ["status", "start_timestamp", "story_count"]})
        sprint_obj["status"] = "in_progress"
        sprint_obj["start_timestamp"] = existing.get("start_timestamp", _now_iso())
    
    result = _api_call("PUT", f"/model/sprints/{sprint_id}", sprint_obj)
    success = bool(result.get("id"))
    if success:
        print(f"[INFO] Data model: Sprint {sprint_id} started (status=in_progress)")
    return success


def update_story_status(story_id: str, status: str, **kwargs) -> bool:
    """
    Update story status + optional metrics (commit_sha, actual_time_minutes, files_created).
    Creates story record if missing.
    """
    if not DATA_MODEL_ENABLED:
        return False
    
    # Get existing story record (may be empty)
    existing = _api_call("GET", f"/model/wbs/{story_id}")
    
    story_obj = {
        "id": story_id,
        "project_id": "51-ACA",
        "status": status,
        "is_active": True,
    }
    
    # Merge with existing (preserve fields)
    if existing and existing.get("id"):
        story_obj.update(existing)
        story_obj["status"] = status
    
    # Add optional metrics (only if provided)
    for key in ["sprint_id", "epic_id", "title", "ado_id", "commit_sha", 
                "actual_time_minutes", "files_created", "start_timestamp", 
                "done_timestamp", "test_result", "lint_result"]:
        if key in kwargs and kwargs[key] is not None:
            story_obj[key] = kwargs[key]
    
    # Set timestamps
    if status == "in_progress" and "start_timestamp" not in story_obj:
        story_obj["start_timestamp"] = _now_iso()
    elif status == "done" and "start_timestamp" in story_obj:
        story_obj["done_timestamp"] = _now_iso()
    
    result = _api_call("PUT", f"/model/wbs/{story_id}", story_obj)
    success = bool(result.get("id"))
    if success:
        print(f"[INFO] Data model: Story {story_id} updated (status={status})")
    return success


def complete_sprint(sprint_id: str, results: list, start_time: str) -> bool:
    """
    Calculate velocity and update sprint status to complete.
    Velocity = stories_completed / (duration_hours / 24).
    """
    if not DATA_MODEL_ENABLED:
        return False
    
    total_stories = len(results)
    done_count = sum(1 for r in results if r.get("status") == "DONE")
    completion_pct = (done_count / total_stories * 100) if total_stories else 0.0
    
    # Calculate duration
    try:
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.now(timezone.utc)
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
    except Exception:
        duration_hours = 0.01  # avoid division by zero
    
    # Velocity: stories per day
    velocity = done_count / (duration_hours / 24) if duration_hours > 0 else 0.0
    
    # Get existing sprint record
    existing = _api_call("GET", f"/model/sprints/{sprint_id}")
    if not existing or not existing.get("id"):
        print(f"[WARN] Sprint {sprint_id} not found in data model -- cannot update")
        return False
    
    sprint_obj = existing.copy()
    sprint_obj.update({
        "status": "complete",
        "end_timestamp": _now_iso(),
        "completion_pct": round(completion_pct, 1),
        "velocity": round(velocity, 2),
        "actual_duration_hours": round(duration_hours, 2),
    })
    
    result = _api_call("PUT", f"/model/sprints/{sprint_id}", sprint_obj)
    success = bool(result.get("id"))
    if success:
        print(f"[INFO] Data model: Sprint {sprint_id} complete (velocity={velocity:.2f} stories/day)")
    return success


# ---------------------------------------------------------------------------
# ADO API client
# ---------------------------------------------------------------------------

def post_ado_wi_comment(wi_id: int, message: str) -> bool:
    """Post comment to ADO work item. Returns True if successful."""
    if not ADO_ENABLED:
        return False
    
    try:
        import base64
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        url = f"{ADO_ORG_URL}/{ADO_PROJECT}/_apis/wit/workitems/{wi_id}/comments?api-version=7.1"
        auth_header = base64.b64encode(f":{ADO_PAT}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        payload = {"text": f"[{timestamp}] {message}"}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            print(f"[INFO] ADO: Posted comment to WI {wi_id}")
            return True
        else:
            print(f"[WARN] ADO: Failed to post comment to WI {wi_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"[WARN] ADO: Exception posting comment to WI {wi_id}: {e}")
        return False


def patch_ado_wi_state(wi_id: int, state: str) -> bool:
    """Update ADO work item state (New, Active, Done, Closed). Returns True if successful."""
    if not ADO_ENABLED:
        return False
    
    try:
        import base64
        url = f"{ADO_ORG_URL}/{ADO_PROJECT}/_apis/wit/workitems/{wi_id}?api-version=7.1"
        auth_header = base64.b64encode(f":{ADO_PAT}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json-patch+json"
        }
        payload = [{"op": "replace", "path": "/fields/System.State", "value": state}]
        response = requests.patch(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"[INFO] ADO: Updated WI {wi_id} state to {state}")
            return True
        else:
            print(f"[WARN] ADO: Failed to update WI {wi_id} state: {response.status_code}")
            return False
    except Exception as e:
        print(f"[WARN] ADO: Exception updating WI {wi_id} state: {e}")
        return False


def _gh_issue_body(issue: int, repo: str) -> tuple[str, str]:
    """Return (title, body) of a GitHub issue."""
    r = _run(["gh", "issue", "view", str(issue), "--json", "body,title", "--repo", repo])
    data = json.loads(r.stdout)
    return data.get("title", ""), data.get("body", "")


def _gh_comment(issue: int, repo: str, body: str) -> None:
    _run(["gh", "issue", "comment", str(issue), "--repo", repo, "--body", body], check=False)


def retry_with_backoff(func: Callable, operation_name: str = "operation", max_attempts: int = MAX_RETRY_ATTEMPTS) -> Any:
    """Retry function with exponential backoff on failure."""
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as exc:
            if attempt == max_attempts:
                print(f"[FAIL] {operation_name} failed after {max_attempts} attempts: {exc}")
                raise
            wait_time = RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
            print(f"[WARN] {operation_name} attempt {attempt} failed: {exc}. Retrying in {wait_time}s...")
            time.sleep(wait_time)


def _git(args: list) -> subprocess.CompletedProcess:
    return _run(["git"] + args, capture=True)


# Key sibling files that routinely need context across multiple stories.
# Loaded into story context when relevant based on story target paths.
_SIBLING_MAP: dict[str, list[str]] = {
    # Any API router change may need cosmos + entitlement context
    "services/api/app/routers/": [
        "services/api/app/db/cosmos.py",
        "services/api/app/services/entitlement_service.py",
    ],
    # Analysis findings router needs cosmos + findings
    "services/analysis/app/": [
        "services/api/app/db/cosmos.py",
    ],
    # Collector changes need ingest + azure_client siblings
    "services/collector/app/ingest.py": [
        "services/collector/app/azure_client.py",
    ],
    # Test files need source files to know what to test
    "services/tests/": [
        "services/api/app/db/cosmos.py",
        "services/api/app/services/entitlement_service.py",
        "services/analysis/app/findings.py",
        "services/collector/app/ingest.py",
    ],
}


def _load_context() -> str:
    """Return a slim project-status snapshot (<2000 chars / ~500 tokens).

    The GitHub Models gpt-4o endpoint allows max 8000 tokens per request.
    The system prompt (~600 tokens) already contains all code patterns.
    Per-story file contents are loaded by _load_story_files().
    This function provides:
      1. Brief project-status heading (stack, phase)
      2. STATUS.md first 60 lines (current sprint state)
      3. services/api/AGENTS.md (Sprint-N learnings -- patterns agents must follow)

    AGENTS.md is the cross-sprint feedback loop: it documents patterns established
    in prior sprints so each new sprint does not regenerate the same bugs.
    """
    lines = []
    lines.append("PROJECT: 51-ACA -- Azure Cost Advisor SaaS")
    lines.append("STACK: Python 3.12 / FastAPI / React 19 / Azure Container Apps / Cosmos DB NoSQL")
    lines.append("")
    status_path = REPO_ROOT / "STATUS.md"
    if status_path.exists():
        status_lines = status_path.read_text(encoding="utf-8", errors="replace").splitlines()[:60]
        lines.append("=== STATUS.md (first 60 lines) ===")
        lines.extend(status_lines)
    agents_path = REPO_ROOT / "services" / "api" / "AGENTS.md"
    if agents_path.exists():
        agents_lines = agents_path.read_text(encoding="utf-8", errors="replace").splitlines()
        lines.append("")
        lines.append("=== services/api/AGENTS.md (established patterns -- FOLLOW THESE) ===")
        lines.extend(agents_lines[:120])  # cap at 120 lines (~300 tokens)
    return "\n".join(lines)


def _load_story_files(story: dict) -> str:
    """Load current file contents for target files + relevant siblings.

    Primary files (files_to_create): full content -- LLM makes surgical changes.
    Sibling files (from _SIBLING_MAP): first 120 lines -- reference only.

    Keeps total story-file bloc under ~3000 tokens so requests stay within
    the 8000-token GitHub Models limit for gpt-4o.
    """
    chunks = ["=== CURRENT FILE CONTENTS (read before writing -- make surgical changes) ===\n\n"]
    seen: set[str] = set()

    target_paths = story.get("files_to_create", [])
    for rel_path in target_paths:
        seen.add(rel_path)
        p = REPO_ROOT / rel_path
        if p.exists():
            content = p.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            # Cap at 200 lines per target file to stay within token budget
            truncated = "\n".join(lines[:200])
            suffix = f"\n... [{len(lines)-200} lines truncated]" if len(lines) > 200 else ""
            chunks.append(f"--- EXISTING ({len(lines)} lines): {rel_path} ---\n{truncated}{suffix}\n\n")
        else:
            chunks.append(f"--- NEW FILE: {rel_path} ---\n[Does not exist -- create from scratch]\n\n")

    # Auto-load sibling files for context (120-line cap to save tokens)
    siblings_to_load: list[str] = []
    for prefix, sibling_list in _SIBLING_MAP.items():
        if any(tp.startswith(prefix) or tp == prefix for tp in target_paths):
            siblings_to_load.extend(sibling_list)
    for rel_path in siblings_to_load:
        if rel_path in seen:
            continue
        seen.add(rel_path)
        p = REPO_ROOT / rel_path
        if p.exists():
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            preview = "\n".join(lines[:120])
            suffix = f"\n... [{len(lines)-120} lines truncated]" if len(lines) > 120 else ""
            chunks.append(f"--- SIBLING REFERENCE ({len(lines)} lines): {rel_path} ---\n{preview}{suffix}\n\n")

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

def _get_llm_client() -> tuple[Optional[object], str]:
    """
    EVA-STORY: ACA-14-009 -- Get LLM client with fallback logic.
    
    Priority:
    1. GitHub Models (if GITHUB_TOKEN present)
    2. Azure OpenAI (if AZURE_OPENAI_KEY + ENDPOINT present)
    3. None (use stubs)
    
    Returns:
        (client, provider) tuple where provider is "github", "azure", or "none"
    """
    try:
        from openai import OpenAI, AzureOpenAI
    except ImportError:
        print("[WARN] openai not installed")
        return (None, "none")
    
    github_token = os.getenv("GITHUB_TOKEN", "")
    if github_token:
        client = OpenAI(base_url=GITHUB_MODELS_URL, api_key=github_token)
        print(f"[INFO] Using GitHub Models API (model={MODEL})")
        return (client, "github")
    
    if AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        print(f"[INFO] Using Azure OpenAI fallback (deployment={AZURE_OPENAI_DEPLOYMENT})")
        return (client, "azure")
    
    print("[WARN] No LLM credentials (GITHUB_TOKEN or AZURE_OPENAI_*)")
    return (None, "none")


def _generate_code(story: dict, context: str, ctx: Optional[object] = None) -> dict[str, str]:
    """
    EVA-STORY: ACA-14-009 -- Call GitHub Models API (or Azure OpenAI fallback)
    to generate file contents for a story.
    Returns {relative_path: content} dict.
    
    Args:
        story: Story specification
        context: Project context
        ctx: SprintContext for tracing (optional)
    """
    client, provider = _get_llm_client()
    if not client:
        print("[WARN] No LLM client available -- generating stubs")
        return _make_stubs(story)

    files_to_create = story.get("files_to_create", [])
    if not files_to_create:
        return {}

    system_prompt = textwrap.dedent("""
        You are an expert senior developer implementing stories for the 51-ACA
        (Azure Cost Advisor) SaaS product. You have full codebase context.
        Follow ALL rules exactly -- they come from copilot-instructions.md.

        ENCODING RULES (ABSOLUTE -- Rule 9 from copilot-instructions):
        - ASCII ONLY. Zero tolerance. No emoji, no Unicode arrows or dashes,
          no curly quotes, no non-breaking spaces.
        - PowerShell: use splatting @params, never backtick (`) line continuation.
        - All Python print/log: use [PASS]/[FAIL]/[WARN]/[INFO] tokens only.
        - No UTF-8 BOM in any file.

        EVA-STORY TAG (mandatory -- missing tag drops Veritas artifact score):
        - Python / YAML / Dockerfile: # EVA-STORY: ACA-NN-NNN
        - JS / TS / Bicep:            // EVA-STORY: ACA-NN-NNN
        - HTML / JSX / TSX:           <!-- EVA-STORY: ACA-NN-NNN -->
        - Tag MUST appear on the first functional line of every file.

        CODE PATTERNS (from copilot-instructions P2.5 -- apply exactly):

        Pattern 1 -- Tenant isolation (MANDATORY for every Cosmos call):
          WRONG: container.query_items(query=..., parameters=[...])
          RIGHT: container.query_items(query=..., parameters=[...], partition_key=sub_id)
          Never call cosmos_client.query_items() without partition_key=subscriptionId.

        Pattern 2 -- Tier gating (MANDATORY -- never expose full findings to Tier 1):
          Use gate_findings(findings, tier) from findings.py.
          Tier 1: return only id/title/category/estimated_saving_low/high/effort_class.
          Tier 2: strip deliverable_template_id.
          Tier 3: full object.

        Pattern 3 -- MSAL delegated auth:
          app = msal.PublicClientApplication(client_id, authority=...)
          result = app.acquire_token_by_refresh_token(refresh_token, scopes=[...])
          Store refresh token in Key Vault, NOT in Cosmos.

        Pattern 4 -- SAS generation (correct API usage):
          WRONG: generate_blob_sas(..., account_key=None, credential=DefaultAzureCredential())
          RIGHT: udk = client.get_user_delegation_key(key_start_time=..., key_expiry_time=...)
                 generate_blob_sas(..., user_delegation_key=udk, ...)

        MODIFICATION RULES:
        - For EXISTING files: return the COMPLETE modified file.
          Preserve ALL code outside the specific lines being changed.
          Do NOT rewrite from scratch -- you are given the current content.
        - For NEW files: implement fully per the patterns above.
        - SAS_HOURS = 168 (7 days per spec, not 24).
        - Every Cosmos upsert_item() call must include partition_key parameter.

        OUTPUT FORMAT:
        Return ONLY a valid JSON object:
        {"relative/path/file.py": "<complete file contents>", ...}
        No markdown fences. No explanation text. Just the JSON object.
        All values must be complete files, not partial excerpts.
    """).strip()

    # Load current file contents -- this is what makes bug-fix stories work
    # Without this, the LLM writes from scratch and destroys existing code
    story_files = _load_story_files(story)

    user_prompt = f"""STORY: {story['id']} -- {story['title']}
EPIC: {story.get('epic', 'N/A')}
SIZE: {story.get('size', 'N/A')}

PROJECT STATUS:
{context}

IMPLEMENTATION NOTES (follow these exactly):
{story.get('implementation_notes', 'Implement as per project patterns.')}

ACCEPTANCE CRITERIA (all must pass):
{chr(10).join('- ' + a for a in story.get('acceptance', []))}

FILES TO CREATE OR MODIFY:
{chr(10).join('- ' + f for f in files_to_create)}

{story_files}

Now generate the file contents. Remember:
1. For existing files: return the COMPLETE file with only the specified changes.
2. For new files: full implementation following patterns.
3. EVA-STORY tag on first functional line: # EVA-STORY: {story['id']}
4. Return ONLY valid JSON: {{"path": "content", ...}}
"""

    try:
        # EVA-STORY: ACA-14-009 -- Use provider-specific model name
        model_name = AZURE_OPENAI_DEPLOYMENT if provider == "azure" else MODEL
        
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8192,
            temperature=0.1,
        )
        
        # EVA-STORY: ACA-14-001 -- Track LM call with cost
        if ctx and hasattr(resp, 'usage'):
            tokens_in = getattr(resp.usage, 'prompt_tokens', 0)
            tokens_out = getattr(resp.usage, 'completion_tokens', 0)
            ctx.record_lm_call(
                model=f"{provider}:{model_name}",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                phase="D2",
                response_text=resp.choices[0].message.content or ""
            )
        
        raw = resp.choices[0].message.content or "{}"
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        raw = re.sub(r"\s*```$", "", raw.strip())
        return json.loads(raw)
    except Exception as exc:
        print(f"[WARN] LLM call failed for {story['id']}: {exc} -- writing stubs")
        if ctx:
            ctx.log("error", f"LLM call failed: {exc}")
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

def write_evidence(story: dict, test_result: str, lint_result: str, 
                   duration_ms: int = 0, tokens_used: int = 0,
                   test_count_before: int = 0, test_count_after: int = 0,
                   files_changed: int = 0) -> str:
    """
    EVA-STORY: ACA-14-010 -- Write Veritas-compatible evidence receipt with schema validation.
    
    Args:
        story: Story dict with id, title, files_to_create
        test_result: "PASS" or "FAIL"
        lint_result: "PASS" or "FAIL"
        duration_ms: Story execution time in milliseconds
        tokens_used: Total tokens from LLM calls
        test_count_before: Test count before story
        test_count_after: Test count after story
        files_changed: Number of files created/modified
    
    Returns:
        Path to receipt file (relative to REPO_ROOT)
    
    Raises:
        ValueError: If receipt fails schema validation
    """
    evidence_dir = REPO_ROOT / ".eva" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = evidence_dir / f"{story['id']}-receipt.json"
    
    receipt = {
        "story_id": story["id"],
        "title": story.get("title", ""),
        "phase": "A",  # DPDCA phase: A (Audit/Complete)
        "timestamp": _now_iso(),
        "artifacts": story.get("files_to_create", []),
        "test_result": test_result,
        "lint_result": lint_result,
        "commit_sha": _git(["rev-parse", "HEAD"]).stdout.strip(),
        "duration_ms": duration_ms,
        "tokens_used": tokens_used,
        "test_count_before": test_count_before,
        "test_count_after": test_count_after,
        "files_changed": files_changed,
    }
    
    # EVA-STORY: ACA-14-010 -- Validate before writing
    try:
        from evidence_schema import validate_evidence_schema
        is_valid, errors = validate_evidence_schema(receipt)
        if not is_valid:
            error_msg = "; ".join(errors)
            print(f"[FAIL] Evidence schema validation failed for {story['id']}")
            for err in errors:
                print(f"  - {err}")
            raise ValueError(f"Evidence receipt schema invalid: {error_msg}")
    except ImportError:
        print("[WARN] evidence_schema not available -- skipping validation")
    
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

    # Include AB# tag if ado_id present (ADO auto-linking)
    ado_tag = f" AB#{story['ado_id']}" if story.get('ado_id') else ""
    msg = f"feat({story['id']}): {story['title']}{ado_tag}"
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
    duration_minutes: float = 0.0,
    velocity: float = 0.0,
) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "DONE")
    failed = total - passed
    completion_pct = (passed / total * 100) if total > 0 else 0
    
    # Calculate aggregate metrics
    total_files = sum(len(r.get("files", [])) for r in results)
    avg_story_duration = duration_minutes / total if total > 0 else 0
    
    # Build story breakdown table
    story_rows = []
    for r in results:
        status_icon = "DONE" if r.get("status") == "DONE" else "FAIL"
        lint_icon = "PASS" if r.get("lint") == "PASS" else "WARN"
        test_icon = "PASS" if r.get("test") == "PASS" else "WARN"
        files_count = len(r.get("files", []))
        story_rows.append(f"| {r['id']} | {files_count} files | {lint_icon} | {test_icon} | {status_icon} |")
    
    story_table = "\n".join(story_rows)
    
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

### Summary Metrics

| Metric | Value |
|--------|-------|
| Duration | {duration_minutes:.1f} minutes |
| Velocity | {velocity:.2f} stories/day |
| Completion | {passed}/{total} ({completion_pct:.0f}%) |
| Total Files | {total_files} |
| Avg Story Time | {avg_story_duration:.1f} min |

### Story Breakdown

| Story | Files | Lint | Tests | Status |
|-------|-------|------|-------|--------|
{story_table}

### Detailed Results

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
    branch = manifest.get("target_branch", "sprint/main")
    if not stories:
        _gh_comment(issue, repo, f"[FAIL] Sprint manifest has no stories.")
        sys.exit(1)

    # === EVA-STORY: ACA-14-002 -- State Lock / Idempotency Guard ===
    # Acquire exclusive lock to prevent duplicate dispatch from network retry or re-trigger
    workflow_run_id = os.environ.get("GITHUB_RUN_ID", "local-run")
    sprint_num = sprint_id.split("-")[-1] if "-" in sprint_id else "0"
    
    # Lock acquisition happens before timeline, so we generate correlation_id early
    lock_acquired = False
    correlation_id = generate_correlation_id(sprint_num)  # Generate for lock and context
    
    if acquire_lock:
        lock_acquired = acquire_lock(sprint_id, workflow_run_id, correlation_id, repo_root=str(REPO_ROOT))
        if not lock_acquired:
            msg = f"[FAIL] Sprint {sprint_id} already in progress (lock held by another workflow). Exiting."
            print(msg)
            _gh_comment(issue, repo, f"{msg}")
            sys.exit(1)

    # Create sprint branch
    _git(["checkout", "-b", branch])
    print(f"[INFO] Branch: {branch}")

    # === EVA-STORY: ACA-14-001 -- Initialize SprintContext ===
    # Extract sprint number from sprint_id (e.g., "SPRINT-11" -> "11")
    sprint_num = sprint_id.split("-")[-1] if "-" in sprint_id else "0"
    correlation_id = generate_correlation_id(sprint_num)
    ctx = SprintContext(correlation_id, repo_root=str(REPO_ROOT)) if SprintContext else None
    if ctx:
        ctx.log("D1", f"Sprint context initialized: {correlation_id}")

    # === PHASE 1: PLANNING -- Update data model ===
    sprint_full_id = f"51-ACA-{sprint_id.lower()}"
    manifest["issue_number"] = issue  # add issue number for data model
    start_sprint(sprint_full_id, manifest)
    if ctx:
        ctx.mark_timeline("submitted")
        ctx.log("D1", f"Sprint planning phase started: {sprint_full_id}")
    
    # === EVA-STORY: ACA-14-003 -- Verify D1 (Discover) phase ===
    if verify_phase:
        if not verify_phase("D1", sprint_id, repo_root=str(REPO_ROOT)):
            msg = f"[FAIL] D1 verification failed -- evidence not collected"
            print(msg)
            _gh_comment(issue, repo, f"{msg}")
            sys.exit(1)

    # Opening comment
    _gh_comment(issue, repo, textwrap.dedent(f"""
### Sprint Agent Started -- {sprint_id}

**Branch**: `{branch}`
**Stories**: {len(stories)}
**Started**: {_now_iso()}
**Correlation ID**: `{correlation_id}`

Working through {len(stories)} stories in sequence. Progress comments will follow after each story.
    """).strip())

    # === EVA-STORY: ACA-14-003 -- Verify D2 (Discover-repo) phase ===
    if verify_phase:
        if not verify_phase("D2", sprint_id, repo_root=str(REPO_ROOT)):
            msg = f"[FAIL] D2 verification failed -- repository audit failed (no tests collected)"
            print(msg)
            _gh_comment(issue, repo, f"{msg}")
            sys.exit(1)
    
    # === EVA-STORY: ACA-14-003 -- Verify P (Plan) phase ===
    if verify_phase:
        if not verify_phase("P", sprint_id, repo_root=str(REPO_ROOT)):
            msg = f"[FAIL] P verification failed -- PLAN.md not updated"
            print(msg)
            _gh_comment(issue, repo, f"{msg}")
            sys.exit(1)

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
        if ctx:
            ctx.log("D2", f"Story {sid} execution starting")

        story_result = {"id": sid, "title": story.get("title", ""), "status": "FAIL", "sha": "", "start_time": _now_iso()}

        # === PHASE 2: PER-STORY START -- Update data model ===
        update_story_status(
            sid,
            "in_progress",
            sprint_id=sprint_full_id,
            epic_id=manifest.get("epic", ""),
            title=story.get("title", ""),
            ado_id=story.get("ado_id"),
        )

        # === ADO SYNC: Mark WI as Active ===
        if story.get("ado_id"):
            patch_ado_wi_state(story["ado_id"], "Active")
            post_ado_wi_comment(story["ado_id"], f"Story {sid} started -- Sprint agent generating code")

        try:
            # D2 -- Generate and write code (with retry)
            generated = retry_with_backoff(
                lambda: _generate_code(story, context, ctx),


                operation_name=f"Code generation for {sid}",
                max_attempts=MAX_RETRY_ATTEMPTS
            )
            written_files = write_files(generated)
            if ctx:
                ctx.mark_timeline("applied")
                ctx.log("D2", f"Code written: {len(written_files)} files")

            # C -- Check
            lint_status, test_status = run_checks()
            if ctx:
                ctx.mark_timeline("tested")
                ctx.log("Check", f"Checks complete: lint={lint_status}, test={test_status}")

            # Calculate metrics for Veritas evidence
            story_start_dt = datetime.fromisoformat(story_result["start_time"].replace("Z", "+00:00"))
            duration_ms = int((datetime.now(timezone.utc) - story_start_dt).total_seconds() * 1000)
            
            # Write evidence with Veritas-compatible metrics
            evidence_path = write_evidence(
                story, test_status, lint_status,
                duration_ms=duration_ms,
                tokens_used=0,  # TODO: Track LLM tokens in _generate_code
                test_count_before=0,  # TODO: Parse pytest --co before generation
                test_count_after=0,   # TODO: Parse pytest --co after generation
                files_changed=len(written_files)
            )

            # A -- Commit
            sha = commit_story(story, written_files, evidence_path)
            if ctx:
                ctx.mark_timeline("committed")
                ctx.log("Act", f"Story committed: {sha[:8]}")

            story_result["status"] = "DONE"
            story_result["sha"] = sha
            story_result["lint"] = lint_status
            story_result["test"] = test_status
            story_result["files"] = written_files

            # === PHASE 2: PER-STORY COMPLETE -- Update data model ===
            # Convert duration_ms to minutes (consistent unit)
            actual_time_minutes = round(duration_ms / 1000 / 60, 1)
            
            update_story_status(
                sid,
                "done",
                commit_sha=sha,
                actual_time_minutes=actual_time_minutes,
                files_created=",".join(written_files[:10]),  # limit length
                test_result=test_status,
                lint_result=lint_status,
            )

            # === ADO SYNC: Post progress + Mark WI as Done ===
            if story.get("ado_id"):
                progress_msg = f"Story {sid} DONE -- {len(written_files)} files, lint={lint_status}, test={test_status}, sha={sha[:8]}"
                post_ado_wi_comment(story["ado_id"], progress_msg)
                patch_ado_wi_state(story["ado_id"], "Done")

        except Exception as exc:
            print(f"[FAIL] Story {sid} failed: {exc}")
            story_result["error"] = str(exc)
            # Update data model on failure
            update_story_status(sid, "failed", error=str(exc))
            
            # === ADO SYNC: Post error comment ===
            if story.get("ado_id"):
                post_ado_wi_comment(story["ado_id"], f"Story {sid} FAILED -- {exc}")

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

    # === EVA-STORY: ACA-14-003 -- Verify D3 (Do-execute) phase ===
    if verify_phase:
        if not verify_phase("D3", sprint_id, repo_root=str(REPO_ROOT)):
            msg = f"[FAIL] D3 verification failed -- story selection manifest not found"
            print(msg)
            _gh_comment(issue, repo, f"{msg}")
            sys.exit(1)

    # Push branch
    push_ok = push_branch(branch)
    state["pushed"] = push_ok
    state["completed"] = _now_iso()
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    if ctx:
        ctx.log("Act", f"Branch pushed: {branch}")

    # === EVA-STORY: ACA-14-003 -- Verify A (Act) phase ===
    if verify_phase:
        if not verify_phase("A", sprint_id, repo_root=str(REPO_ROOT)):
            msg = f"[FAIL] A verification failed -- manifest JSON invalid"
            print(msg)
            _gh_comment(issue, repo, f"{msg}")
            sys.exit(1)

    # === PHASE 3: COMPLETION -- Update data model ===
    complete_sprint(sprint_full_id, results, state["started"])
    if ctx:
        ctx.mark_timeline("completed" if all(r["status"] == "DONE" for r in results) else "failed")
        ctx.log("Act", f"Sprint completed: {len([r for r in results if r['status'] == 'DONE'])}/{len(results)} stories done")
        ctx.save()  # Save sprint context with all traces

    # Calculate sprint metrics
    try:
        start_dt = datetime.fromisoformat(state["started"].replace("Z", "+00:00"))
        end_dt = datetime.now(timezone.utc)
        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        duration_days = duration_minutes / (24 * 60)
        velocity = len(results) / duration_days if duration_days > 0 else 0
    except Exception:
        duration_minutes = 0.0
        velocity = 0.0

    # === ADO SYNC: Post sprint summary to Feature WI ===
    feature_id = manifest.get("feature_ado_id")
    if feature_id:
        done_count = sum(1 for r in results if r["status"] == "DONE")
        fail_count = len(results) - done_count
        ado_summary = f"Sprint {sprint_id} COMPLETE -- {done_count}/{len(results)} stories done ({done_count/len(results)*100:.0f}%), velocity={velocity:.2f} stories/day, branch={branch}"
        post_ado_wi_comment(feature_id, ado_summary)

    # Generate sprint summary with enhanced metrics
    summary = _sprint_summary_comment(manifest, results, branch, duration_minutes, velocity)
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

    # === EVA-STORY: ACA-14-002 -- Release lock ===
    if lock_acquired and release_lock:
        release_lock(sprint_id, repo_root=str(REPO_ROOT))
        if ctx:
            ctx.log("Act", f"Lock released for {sprint_id}")


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
