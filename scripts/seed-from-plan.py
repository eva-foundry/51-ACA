"""
seed-from-plan.py -- ACA artifact seeder
=========================================
Reads README.md, PLAN.md, STATUS.md, ACCEPTANCE.md and rebuilds:
  1. .eva/veritas-plan.json  -- complete story roster for Veritas MTI
  2. Data model (SQLite)     -- wipe + reseed all layers via data-model/db.py

Usage:
  python seed-from-plan.py                  # rebuild veritas-plan.json only
  python seed-from-plan.py --reseed-model   # rebuild veritas-plan.json + wipe/reseed model
  python seed-from-plan.py --wipe-only      # wipe model only (no plan parse)
  python seed-from-plan.py --dry-run        # print what would be written, no writes

Design principle:
  Parse PLAN.md as the single source of truth.
  Every Epic, Feature, and Story gets a canonical ACA-EE-NNN ID.
  veritas-plan.json is rebuilt from scratch every run.
  Data model is wiped and reseeded from the parsed plan + inline metadata.

EVA-STORY: ACA-14-005
"""

import re
import json
import sys
import os
import argparse
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT   = Path(__file__).parent.parent
PLAN_FILE   = REPO_ROOT / "PLAN.md"
STATUS_FILE = REPO_ROOT / "STATUS.md"
README_FILE = REPO_ROOT / "README.md"
ACCEPT_FILE = REPO_ROOT / "ACCEPTANCE.md"
EVA_DIR     = REPO_ROOT / ".eva"
PLAN_OUT    = EVA_DIR / "veritas-plan.json"

# -- local SQLite data model (data-model/db.py) -- no HTTP needed
_DB_DIR = Path(__file__).parent.parent / "data-model"
if str(_DB_DIR) not in sys.path:
    sys.path.insert(0, str(_DB_DIR))
try:
    import db as _db
    USE_SQLITE = True
except ImportError:
    USE_SQLITE = False
    print("[WARN] data-model/db.py not found -- model ops disabled")

# ---------------------------------------------------------------------------
# STEP 1 -- parse PLAN.md
# ---------------------------------------------------------------------------

EPIC_HEADER_RE   = re.compile(r"^=+\s*$", re.MULTILINE)
EPIC_TITLE_RE    = re.compile(r"EPIC\s+(\d+)\s+--\s+(.+?)(?:\s+\(|$)", re.IGNORECASE)
FEATURE_RE       = re.compile(r"^\s{0,4}Feature\s+(\d+)\.(\d+)\s+--\s+(.+)$")
STORY_OLD_RE     = re.compile(r"^\s{2,6}Story\s+(\d+)\.(\d+)\.(\d+)\s{2,}(.+)$")
STORY_NEW_RE     = re.compile(r"^\s{2,6}Story\s+(ACA-\d{2}-\d{3})\s{2,}(.+)$")
STATUS_LINE_RE   = re.compile(r"^\s+Status:\s+(.+)$", re.IGNORECASE)
EVA_TAG_LINE_RE  = re.compile(r"EVA-STORY\s+tag:\s+[/#/]+\s*EVA-STORY:\s+(ACA-\d{2}-\d{3})")
WBS_STATUS_RE    = re.compile(r"^(DONE|ACTIVE|PARTIAL|PLANNED|NEW|NOT STARTED|IN PROGRESS)\s+(\d+)\s+(.+?)\s{2,}", re.IGNORECASE)
FP_LINE_RE       = re.compile(r"FP:\s*(?:[XSML]{1,2}=)?(\d+)")
SPRINT_LINE_RE   = re.compile(r"Sprint:\s*(\S+)")
ROSTER_ID_RE     = re.compile(r"^\s+(ACA-\d{2}-\d{3})\s+", re.MULTILINE)
ACCEPT_GATE_RE   = re.compile(r"^\s{0,6}\[([\s xX])\]\s+(\S+):\s*(.+)$")


def parse_done_roster(text: str) -> set[str]:
    """
    Extract confirmed shipped story IDs from the bounded 'Story ID Roster' section
    in PLAN.md.  Only reads from that section -- NOT from spec annotation lines
    like 'EVA-STORY tag: ...' which appear throughout the plan as guidance, not proof.
    """
    done_ids: set[str] = set()
    roster_start = re.search(r"Story ID Roster.*?confirmed", text, re.IGNORECASE)
    if not roster_start:
        return done_ids
    block = text[roster_start.start():]
    in_block = False
    blank_count = 0
    for line in block.splitlines():
        if "Story ID Roster" in line or "EVA-STORY tags confirmed" in line:
            in_block = True
            continue
        if not in_block:
            continue
        if re.match(r"^={5,}", line):
            break
        if line.strip() == "":
            blank_count += 1
            if blank_count >= 2:
                break
            continue
        blank_count = 0
        id_m = re.match(r"^\s+(ACA-\d{2}-\d{3})\s+", line)
        if id_m:
            done_ids.add(id_m.group(1))
    return done_ids


def parse_plan(text: str) -> dict:
    """
    Parse PLAN.md into a structured dict:
      { epic_id: { id, num, title, status, sprint, features: [ { id, title, stories: [...] } ] } }
    """
    # -- extract WBS overview for epic statuses --
    # scan every line in the full text; WBS table rows are space-aligned (no pipes)
    epic_status_map: dict[int, str] = {}
    for ln in text.splitlines():
        m = WBS_STATUS_RE.match(ln.strip())
        if m:
            status_str = m.group(1).strip().upper()
            try:
                epic_num = int(m.group(2))
                epic_status_map[epic_num] = status_str
            except ValueError:
                pass

    # -- extract confirmed done story IDs from roster section --
    # NOTE: roster IDs are from the old veritas feature scheme (ACA-01=STATS API).
    # Under the new PLAN.md epic scheme they don't align. Roster is stored separately
    # for reference only -- do NOT use it to set done=True on plan stories.
    roster_done = parse_done_roster(text)  # kept for logging/reference

    # -- split into epic blocks by the ==== separator lines --
    sections = re.split(r"={5,}", text)

    epics: dict[int, dict] = {}
    current_epic: dict | None = None
    current_feature: dict | None = None
    story_counters: dict[int, int] = {}  # epic_num -> sequential count

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Check if this section starts with an EPIC header
        em = EPIC_TITLE_RE.search(section)
        if em:
            epic_num = int(em.group(1))
            epic_title = em.group(2).strip()
            epic_id = f"ACA-{epic_num:02d}"
            current_epic = {
                "id": epic_id,
                "num": epic_num,
                "title": epic_title,
                "status": epic_status_map.get(epic_num, "UNKNOWN"),
                "features": [],
                "source": "plan-md",
            }
            epics[epic_num] = current_epic
            story_counters[epic_num] = 0
            current_feature = None
            # continue to parse lines in this section
            lines = section.splitlines()
        else:
            lines = section.splitlines()

        if current_epic is None:
            continue

        epic_num = current_epic["num"]
        pending_story: dict | None = None
        # Epics marked DONE in WBS overview propagate done=True to all their stories
        epic_is_done = epic_status_map.get(epic_num, "") in ("DONE",)

        for line in lines:
            # Feature header
            fm = FEATURE_RE.match(line)
            if fm:
                feat_epic_num = int(fm.group(1))
                feat_sub = int(fm.group(2))
                feat_title = fm.group(3).strip()
                if feat_epic_num != epic_num:
                    # cross-epic contamination in section -- find correct epic
                    if feat_epic_num not in epics:
                        epics[feat_epic_num] = {
                            "id": f"ACA-{feat_epic_num:02d}",
                            "num": feat_epic_num,
                            "title": f"Epic {feat_epic_num}",
                            "status": epic_status_map.get(feat_epic_num, "UNKNOWN"),
                            "features": [],
                            "source": "plan-md",
                        }
                        story_counters[feat_epic_num] = 0
                    current_epic = epics[feat_epic_num]
                    epic_num = feat_epic_num
                    epic_is_done = epic_status_map.get(epic_num, "") in ("DONE",)
                feat_id = f"{current_epic['id']}-F{feat_sub:02d}"
                current_feature = {
                    "id": feat_id,
                    "sub": feat_sub,
                    "title": feat_title,
                    "stories": [],
                }
                current_epic["features"].append(current_feature)
                pending_story = None
                continue

            # Story (old format: N.M.K)
            sm_old = STORY_OLD_RE.match(line)
            if sm_old:
                ep_n = int(sm_old.group(1))
                # story sequential within epic
                story_counters.setdefault(ep_n, 0)
                story_counters[ep_n] += 1
                story_id = f"ACA-{ep_n:02d}-{story_counters[ep_n]:03d}"
                raw_title = sm_old.group(4).strip()
                the_story = {
                    "id": story_id,
                    "wbs": f"{ep_n}.{sm_old.group(2)}.{sm_old.group(3)}",
                    "title": raw_title[:120],
                    "feature_id": current_epic["id"],
                    "done": epic_is_done,
                    "source": "plan-md",
                    "tasks": [],
                }
                if current_feature is not None:
                    current_feature["stories"].append(the_story)
                    the_story["feature_id"] = current_feature["id"]
                # Capture FP and sprint from subsequent lines
                fp_m = FP_LINE_RE.search(line)
                if fp_m:
                    the_story["fp"] = int(fp_m.group(1))
                sprint_m = SPRINT_LINE_RE.search(line)
                if sprint_m:
                    the_story["sprint"] = sprint_m.group(1)
                pending_story = the_story
                continue

            # Story (new format: ACA-NN-NNN)
            sm_new = STORY_NEW_RE.match(line)
            if sm_new:
                story_id = sm_new.group(1).strip()
                raw_title = sm_new.group(2).strip()
                # parse epic num from story ID
                ep_n_str = story_id.split("-")[1]
                ep_n = int(ep_n_str)
                the_story = {
                    "id": story_id,
                    "wbs": story_id,
                    "title": raw_title[:120],
                    "feature_id": current_epic["id"],
                    "done": epic_is_done,
                    "source": "plan-md",
                    "tasks": [],
                }
                if current_feature is not None:
                    current_feature["stories"].append(the_story)
                    the_story["feature_id"] = current_feature["id"]
                pending_story = the_story
                continue

            # Status: DONE / PLANNED / etc attached to the pending story
            slm = STATUS_LINE_RE.match(line)
            if slm and pending_story is not None:
                status_val = slm.group(1).strip().upper()
                if "DONE" in status_val:
                    pending_story["done"] = True
                elif "PLANNED" in status_val:
                    pending_story["done"] = False
                elif "IN PROGRESS" in status_val or "PROGRESS" in status_val:
                    pending_story["done"] = False
                    pending_story["in_progress"] = True
                continue

            # FP and sprint on continuation lines after a story
            if pending_story is not None:
                fp_m = FP_LINE_RE.search(line)
                if fp_m and "fp" not in pending_story:
                    pending_story["fp"] = int(fp_m.group(1))
                sprint_m = SPRINT_LINE_RE.search(line)
                if sprint_m and "sprint" not in pending_story:
                    pending_story["sprint"] = sprint_m.group(1)

    return epics


def build_veritas_plan(epics: dict) -> dict:
    """
    Convert parsed epics dict to veritas-plan.json schema.
    Features become the top-level entries (keyed by epic.id, not sub-feature).
    Stories roll up under their parent epic (flat, no sub-feature nesting -- Veritas v1 format).
    """
    features = []
    for epic_num in sorted(epics.keys()):
        ep = epics[epic_num]
        all_stories = []
        for feat in ep["features"]:
            for st in feat["stories"]:
                all_stories.append({
                    "id": st["id"],
                    "title": st["title"],
                    "feature_id": ep["id"],
                    "done": st.get("done", False),
                    "source": st.get("source", "plan-md"),
                    "tasks": [],
                })
        features.append({
            "id": ep["id"],
            "title": ep["title"],
            "source": "plan-md",
            "stories": all_stories,
        })
    return {
        "schema": "eva.veritas-plan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_from": ["PLAN.md", "README.md", "STATUS.md", "ACCEPTANCE.md"],
        "format_detected": "auto-seeded",
        "prefix": "ACA",
        "features": features,
    }


# ---------------------------------------------------------------------------
# STEP 2 -- parse STATUS.md for current sprint, mtI, decisions
# ---------------------------------------------------------------------------

def parse_status(text: str) -> dict:
    info = {"phase": "", "active_epic": "", "mti": 0, "decisions": []}
    for line in text.splitlines():
        if line.startswith("Phase:"):
            info["phase"] = line.split(":", 1)[1].strip()
        elif "Active Epic:" in line:
            info["active_epic"] = line.split(":", 1)[1].strip()
        elif "Veritas MTI:" in line:
            m = re.search(r"MTI:\s*(\d+)", line)
            if m:
                info["mti"] = int(m.group(1))
        elif re.match(r"^[A-Z]\d{1,2}\s+", line.strip()):
            info["decisions"].append(line.strip())
    return info


# ---------------------------------------------------------------------------
# STEP 3 -- parse ACCEPTANCE.md for quality gates
# ---------------------------------------------------------------------------

def parse_acceptance(text: str) -> list[dict]:
    """
    Parse ACCEPTANCE.md GATE entries: [ ] P1-01a: description
    Returns list of {id, description, passed}
    """
    gates = []
    for line in text.splitlines():
        m = ACCEPT_GATE_RE.match(line)
        if m:
            marker = m.group(1).strip().upper()
            gates.append({
                "id": m.group(2).strip(),
                "description": m.group(3).strip(),
                "passed": marker in ("X",),
            })
    return gates


# ---------------------------------------------------------------------------
# STEP 4 -- data model: wipe + reseed
# ---------------------------------------------------------------------------

WIPEABLE_LAYERS = [
    "requirements", "endpoints", "containers", "screens", "agents",
    "services", "personas", "decisions", "schemas", "hooks",
    "components", "literals", "infrastructure", "feature_flags",
    "sprints", "milestones", "wbs",
]

# Canonical endpoint definitions (mirrors services/api routers)
ENDPOINT_DEFS = [
    # implemented
    {"id": "GET /health",                        "status": "implemented", "implemented_in": "services/api/app/routers/health.py",    "repo_line": 10, "auth": [],             "service": "aca-api"},
    {"id": "GET /v1/admin/stats",                "status": "implemented", "implemented_in": "services/api/app/routers/admin.py",     "repo_line": 12, "auth": ["ACA_Admin"],  "service": "aca-api"},
    {"id": "DELETE /v1/admin/scans/{scan_id}",   "status": "implemented", "implemented_in": "services/api/app/routers/admin.py",     "repo_line": 30, "auth": ["ACA_Admin"],  "service": "aca-api"},
    {"id": "GET /v1/scans/",                     "status": "implemented", "implemented_in": "services/api/app/routers/scans.py",     "repo_line": 15, "auth": ["user"],       "service": "aca-api"},
    {"id": "GET /v1/scans/{scan_id}",            "status": "implemented", "implemented_in": "services/api/app/routers/scans.py",     "repo_line": 25, "auth": ["user"],       "service": "aca-api"},
    {"id": "POST /v1/scans/",                    "status": "implemented", "implemented_in": "services/api/app/routers/scans.py",     "repo_line": 40, "auth": ["user"],       "service": "aca-api"},
    {"id": "POST /v1/auth/connect",              "status": "implemented", "implemented_in": "services/api/app/routers/auth.py",      "repo_line": 18, "auth": [],             "service": "aca-api"},
    {"id": "POST /v1/auth/preflight",            "status": "implemented", "implemented_in": "services/api/app/routers/auth.py",      "repo_line": 45, "auth": ["user"],       "service": "aca-api"},
    {"id": "POST /v1/auth/disconnect",           "status": "implemented", "implemented_in": "services/api/app/routers/auth.py",      "repo_line": 70, "auth": ["user"],       "service": "aca-api"},
    {"id": "POST /v1/checkout/tier2",            "status": "implemented", "implemented_in": "services/api/app/routers/checkout.py",  "repo_line": 20, "auth": ["user"],       "service": "aca-api"},
    {"id": "POST /v1/checkout/tier3",            "status": "implemented", "implemented_in": "services/api/app/routers/checkout.py",  "repo_line": 45, "auth": ["user"],       "service": "aca-api"},
    {"id": "POST /v1/checkout/webhook",          "status": "implemented", "implemented_in": "services/api/app/routers/checkout.py",  "repo_line": 70, "auth": [],             "service": "aca-api"},
    {"id": "GET /v1/checkout/entitlements",      "status": "implemented", "implemented_in": "services/api/app/routers/checkout.py",  "repo_line": 95, "auth": ["user"],       "service": "aca-api"},
    {"id": "GET /v1/findings/{scan_id}",         "status": "implemented", "implemented_in": "services/api/app/routers/findings.py",  "repo_line": 15, "auth": ["user"],       "service": "aca-api"},
    # stubs
    {"id": "GET /v1/admin/kpis",                 "status": "stub", "implemented_in": "services/api/app/routers/admin.py",     "repo_line": 55,  "auth": ["ACA_Admin", "ACA_Support", "ACA_FinOps"], "service": "aca-api"},
    {"id": "GET /v1/admin/customers",            "status": "stub", "implemented_in": "services/api/app/routers/admin.py",     "repo_line": 75,  "auth": ["ACA_Admin", "ACA_Support", "ACA_FinOps"], "service": "aca-api"},
    {"id": "GET /v1/admin/runs",                 "status": "stub", "implemented_in": "services/api/app/routers/admin.py",     "repo_line": 95,  "auth": ["ACA_Admin", "ACA_Support", "ACA_FinOps"], "service": "aca-api"},
    {"id": "POST /v1/admin/entitlements/grant",  "status": "stub", "implemented_in": "services/api/app/routers/admin.py",     "repo_line": 115, "auth": ["ACA_Admin", "ACA_Support"],               "service": "aca-api"},
    {"id": "POST /v1/admin/subscriptions/{subscriptionId}/lock", "status": "stub", "implemented_in": "services/api/app/routers/admin.py", "repo_line": 135, "auth": ["ACA_Admin", "ACA_Support"], "service": "aca-api"},
    {"id": "POST /v1/admin/stripe/reconcile",    "status": "stub", "implemented_in": "services/api/app/routers/admin.py",     "repo_line": 155, "auth": ["ACA_Admin"],                              "service": "aca-api"},
    {"id": "POST /v1/collect/start",             "status": "stub", "implemented_in": "services/api/app/routers/collector.py", "repo_line": 10,  "auth": ["user"], "service": "aca-api"},
    {"id": "GET /v1/collect/status",             "status": "stub", "implemented_in": "services/api/app/routers/collector.py", "repo_line": 30,  "auth": ["user"], "service": "aca-api"},
    {"id": "GET /v1/reports/tier1",              "status": "stub", "implemented_in": "services/api/app/routers/findings.py",  "repo_line": 40,  "auth": ["user"], "service": "aca-api"},
    {"id": "POST /v1/billing/checkout",          "status": "stub", "implemented_in": "services/api/app/routers/billing.py",   "repo_line": 10,  "auth": ["user"], "service": "aca-api"},
    {"id": "GET /v1/billing/portal",             "status": "stub", "implemented_in": "services/api/app/routers/billing.py",   "repo_line": 30,  "auth": ["user"], "service": "aca-api"},
    {"id": "POST /v1/webhooks/stripe",           "status": "stub", "implemented_in": "services/api/app/routers/webhooks.py",  "repo_line": 10,  "auth": [],       "service": "aca-api"},
    {"id": "GET /v1/entitlements",               "status": "stub", "implemented_in": "services/api/app/routers/entitlements.py", "repo_line": 10, "auth": ["user"], "service": "aca-api"},
]

# Canonical Cosmos containers
CONTAINER_DEFS = [
    {"id": "scans",               "status": "active", "partition_key": "/subscriptionId", "description": "Scan lifecycle records"},
    {"id": "inventories",         "status": "active", "partition_key": "/subscriptionId", "description": "Azure resource inventory snapshots"},
    {"id": "cost-data",           "status": "active", "partition_key": "/subscriptionId", "description": "91-day daily cost rows"},
    {"id": "advisor",             "status": "active", "partition_key": "/subscriptionId", "description": "Azure Advisor recommendations"},
    {"id": "findings",            "status": "active", "partition_key": "/subscriptionId", "description": "Tiered analysis findings"},
    {"id": "clients",             "status": "active", "partition_key": "/subscriptionId", "description": "Client entitlement and tier records"},
    {"id": "entitlements",        "status": "active", "partition_key": "/subscriptionId", "description": "Stripe entitlement lifecycle"},
    {"id": "payments",            "status": "active", "partition_key": "/subscriptionId", "description": "Stripe webhook audit trail"},
    {"id": "deliverables",        "status": "active", "partition_key": "/subscriptionId", "description": "Tier 3 ZIP SAS URL records"},
    {"id": "admin_audit_events",  "status": "active", "partition_key": "/subscriptionId", "description": "Admin action audit log"},
    {"id": "stripe_customer_map", "status": "active", "partition_key": "/stripeCustomerId", "description": "stripeCustomerId -> subscriptionId map"},
]

# Canonical screens (Spark pages)
SCREEN_DEFS = [
    {"id": "LoginPage",               "route": "/",                               "service": "aca-frontend", "api_calls": [], "auth_required": False},
    {"id": "ConnectSubscriptionPage", "route": "/app/connect",                    "service": "aca-frontend", "api_calls": ["POST /v1/auth/connect", "POST /v1/auth/preflight"], "auth_required": True},
    {"id": "CollectionStatusPage",    "route": "/app/status/:subscriptionId",     "service": "aca-frontend", "api_calls": ["POST /v1/collect/start", "GET /v1/collect/status"], "auth_required": True},
    {"id": "FindingsTier1Page",       "route": "/app/findings/:subscriptionId",   "service": "aca-frontend", "api_calls": ["GET /v1/reports/tier1"], "auth_required": True},
    {"id": "UpgradePage",             "route": "/app/upgrade/:subscriptionId",    "service": "aca-frontend", "api_calls": ["POST /v1/billing/checkout"], "auth_required": True},
    {"id": "AdminDashboardPage",      "route": "/admin/dashboard",                "service": "aca-frontend", "api_calls": ["GET /v1/admin/kpis"], "auth_required": True},
    {"id": "AdminCustomersPage",      "route": "/admin/customers",                "service": "aca-frontend", "api_calls": ["GET /v1/admin/customers"], "auth_required": True},
    {"id": "AdminBillingPage",        "route": "/admin/billing",                  "service": "aca-frontend", "api_calls": ["POST /v1/admin/stripe/reconcile", "GET /v1/billing/portal"], "auth_required": True},
    {"id": "AdminRunsPage",           "route": "/admin/runs",                     "service": "aca-frontend", "api_calls": ["GET /v1/admin/runs"], "auth_required": True},
    {"id": "AdminControlsPage",       "route": "/admin/controls",                 "service": "aca-frontend", "api_calls": ["POST /v1/admin/entitlements/grant", "POST /v1/admin/subscriptions/{subscriptionId}/lock"], "auth_required": True},
]

# Canonical services
SERVICE_DEFS = [
    {"id": "aca-api",       "label": "ACA API",       "type": "fastapi",  "port": 8080, "status": "active", "is_active": True, "notes": "FastAPI orchestration hub"},
    {"id": "aca-frontend",  "label": "ACA Frontend",  "type": "vite",     "port": 5173, "status": "active", "is_active": True, "notes": "React 19 + Fluent UI v9"},
    {"id": "aca-collector", "label": "ACA Collector", "type": "job",      "port": 0,    "status": "stub",   "is_active": True, "notes": "Azure SDK inventory job"},
    {"id": "aca-analysis",  "label": "ACA Analysis",  "type": "job",      "port": 0,    "status": "stub",   "is_active": True, "notes": "12-rule analysis + tier gating"},
    {"id": "aca-delivery",  "label": "ACA Delivery",  "type": "job",      "port": 0,    "status": "stub",   "is_active": True, "notes": "Jinja2 IaC generator + ZIP packager"},
]

# Canonical agents
AGENT_DEFS = [
    {"id": "collection-agent",    "label": "Collection Agent",    "framework": "29-foundry", "status": "stub",   "is_active": True, "notes": "Azure resource inventory orchestration"},
    {"id": "analysis-agent",      "label": "Analysis Agent",      "framework": "29-foundry", "status": "stub",   "is_active": True, "notes": "12 rules + findings assembly"},
    {"id": "generation-agent",    "label": "Generation Agent",    "framework": "29-foundry", "status": "stub",   "is_active": True, "notes": "IaC template renderer"},
    {"id": "redteam-agent",       "label": "Red Team Agent",      "framework": "29-foundry", "status": "stub",   "is_active": True, "notes": "Tier 1 token leak assertion"},
]

# Canonical personas
PERSONA_DEFS = [
    {"id": "tier1-user",   "label": "Tier 1 User (Free)",          "tier": "tier1", "features": ["findings_summary"]},
    {"id": "tier2-user",   "label": "Tier 2 User (Paid Monthly)",  "tier": "tier2", "features": ["findings_summary", "narrative", "evidence"]},
    {"id": "tier3-user",   "label": "Tier 3 User (One-time)",      "tier": "tier3", "features": ["findings_summary", "narrative", "evidence", "iac_deliverable"]},
    {"id": "aca-admin",    "label": "ACA Admin",                   "tier": "admin", "features": ["admin_dashboard", "customer_mgmt", "billing_mgmt", "controls"]},
]


def model_wipe(dry_run: bool = False) -> int:
    """
    Hard-wipe all wipeable layers from the SQLite data model.
    Returns total count of deleted objects.
    """
    if not USE_SQLITE:
        print("[WARN] SQLite db not available -- skipping wipe")
        return 0
    wiped = 0
    for layer in WIPEABLE_LAYERS:
        if dry_run:
            items = _db.list_layer(layer)
            print(f"  [DRY] WIPE {layer} ({len(items)} objects)")
            wiped += len(items)
        else:
            n = _db.wipe_layer(layer)
            print(f"  [INFO] Wiped {layer}: {n} objects")
            wiped += n
    return wiped


def model_upsert(layer: str, obj: dict, dry_run: bool = False) -> bool:
    """
    Write one object to the SQLite data model.  Fully idempotent.
    """
    if not USE_SQLITE:
        return False
    obj_id = obj.get("id", "")
    if not obj_id:
        return False
    if dry_run:
        print(f"  [DRY] UPSERT {layer}/{obj_id}")
        return True
    try:
        _db.upsert_object(layer, obj, actor="agent:seed")
        return True
    except Exception as e:
        print(f"  [WARN] UPSERT {layer}/{obj_id} -- {e}")
        return False


def model_post(layer: str, obj: dict, dry_run: bool = False) -> bool:
    return model_upsert(layer, obj, dry_run)


def model_reseed(epics: dict, dry_run: bool = False) -> dict:
    """
    Seed all model layers from parsed plan data + canonical definitions.
    Returns counts per layer.
    """
    counts = {}

    # -- services --
    n = 0
    for svc in SERVICE_DEFS:
        if model_post("services", svc, dry_run):
            n += 1
    counts["services"] = n

    # -- containers --
    n = 0
    for c in CONTAINER_DEFS:
        if model_post("containers", c, dry_run):
            n += 1
    counts["containers"] = n

    # -- endpoints --
    n = 0
    for ep in ENDPOINT_DEFS:
        if model_post("endpoints", ep, dry_run):
            n += 1
    counts["endpoints"] = n

    # -- screens --
    n = 0
    for sc in SCREEN_DEFS:
        if model_post("screens", sc, dry_run):
            n += 1
    counts["screens"] = n

    # -- agents --
    n = 0
    for ag in AGENT_DEFS:
        if model_post("agents", ag, dry_run):
            n += 1
    counts["agents"] = n

    # -- personas --
    n = 0
    for p in PERSONA_DEFS:
        if model_post("personas", p, dry_run):
            n += 1
    counts["personas"] = n

    # -- requirements: seed every story as a requirement object --
    n = 0
    for epic_num in sorted(epics.keys()):
        ep = epics[epic_num]
        # post epic-level req
        req_epic = {
            "id": ep["id"],
            "type": "epic",
            "title": ep["title"],
            "status": ep["status"].lower(),
            "sprint": None,
            "is_active": True,
        }
        if model_post("requirements", req_epic, dry_run):
            n += 1
        for feat in ep["features"]:
            for st in feat["stories"]:
                req = {
                    "id": st["id"],
                    "type": "story",
                    "title": st["title"],
                    "status": "done" if st.get("done") else "planned",
                    "sprint": None,
                    "feature_id": ep["id"],
                    "wbs": st.get("wbs", st["id"]),
                    "is_active": True,
                }
                if model_post("requirements", req, dry_run):
                    n += 1
    counts["requirements"] = n

    return counts


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ACA plan seeder")
    parser.add_argument("--reseed-model",  action="store_true", help="Wipe + reseed data model")
    parser.add_argument("--wipe-only",     action="store_true", help="Wipe model only")
    parser.add_argument("--dry-run",       action="store_true", help="Print actions, no writes")
    args = parser.parse_args()

    print(f"[INFO] ACA seed-from-plan -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[INFO] Repo: {REPO_ROOT}")

    # -- read governance docs --
    plan_text   = PLAN_FILE.read_text(encoding="utf-8")
    status_text = STATUS_FILE.read_text(encoding="utf-8") if STATUS_FILE.exists() else ""
    accept_text = ACCEPT_FILE.read_text(encoding="utf-8") if ACCEPT_FILE.exists() else ""
    readme_text = README_FILE.read_text(encoding="utf-8") if README_FILE.exists() else ""

    print(f"[INFO] PLAN.md        {len(plan_text):,} chars")
    print(f"[INFO] STATUS.md      {len(status_text):,} chars")
    print(f"[INFO] ACCEPTANCE.md  {len(accept_text):,} chars")
    print(f"[INFO] README.md      {len(readme_text):,} chars")

    # -- parse --
    epics    = parse_plan(plan_text)
    status_i = parse_status(status_text)
    gates    = parse_acceptance(accept_text)

    total_features = sum(len(ep["features"]) for ep in epics.values())
    total_stories  = sum(
        len(feat["stories"])
        for ep in epics.values()
        for feat in ep["features"]
    )
    done_stories = sum(
        1
        for ep in epics.values()
        for feat in ep["features"]
        for st in feat["stories"]
        if st.get("done")
    )
    planned_stories = total_stories - done_stories
    gates_passed = sum(1 for g in gates if g["passed"])

    print(f"[INFO] Parsed: {len(epics)} epics, {total_features} features, {total_stories} stories")
    print(f"[INFO]   done={done_stories}  planned={planned_stories}")
    print(f"[INFO]   shipped roster (old scheme, reference only): {len(status_i.get('roster', []))} IDs")
    print(f"[INFO] Acceptance gates: {len(gates)} total, {gates_passed} passed")
    print(f"[INFO] Status: phase={status_i['phase']} MTI={status_i['mti']}")
    print()
    print("[INFO] Epic breakdown:")
    for en in sorted(epics.keys()):
        ep = epics[en]
        ep_stories = sum(len(f["stories"]) for f in ep["features"])
        ep_done    = sum(1 for f in ep["features"] for s in f["stories"] if s.get("done"))
        print(f"  {ep['id']}  {ep['status']:12s}  stories={ep_stories:3d}  done={ep_done}  -- {ep['title']}")

    # -- wipe model if requested --
    if args.wipe_only or args.reseed_model:
        if not USE_SQLITE:
            print("[FAIL] data-model/db.py not found -- cannot wipe/reseed model")
            sys.exit(1)
        db_path = _db.DB_PATH
        print(f"[INFO] Wiping data model (SQLite: {db_path}) ...")
        n = model_wipe(dry_run=args.dry_run)
        print(f"[INFO] Wiped {n} objects")
        if args.wipe_only:
            print("[PASS] Wipe complete")
            return

    # -- build + write veritas-plan.json --
    plan_doc = build_veritas_plan(epics)
    if not args.dry_run:
        EVA_DIR.mkdir(exist_ok=True)
        PLAN_OUT.write_text(json.dumps(plan_doc, indent=2), encoding="utf-8")
        plan_story_count = sum(len(f["stories"]) for f in plan_doc["features"])
        print(f"[PASS] veritas-plan.json written: {len(plan_doc['features'])} features, {plan_story_count} stories")
    else:
        plan_story_count = sum(len(f["stories"]) for f in plan_doc["features"])
        print(f"[DRY]  veritas-plan.json would have: {len(plan_doc['features'])} features, {plan_story_count} stories")

    # -- reseed model --
    if args.reseed_model:
        print("[INFO] Reseeding data model (SQLite) ...")
        counts = model_reseed(epics, dry_run=args.dry_run)
        for layer, cnt in sorted(counts.items()):
            print(f"  [INFO] {layer}: {cnt} objects seeded")
        total = sum(counts.values())
        if not args.dry_run and USE_SQLITE:
            live_total = _db.total_active()
            print(f"[PASS] Model seeded: {total} objects written | DB active total: {live_total}")
        else:
            print(f"[PASS] Model seeded: {total} total objects")

    print("[PASS] seed-from-plan complete")


if __name__ == "__main__":
    main()
