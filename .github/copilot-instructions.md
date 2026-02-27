# GitHub Copilot Instructions -- 51-ACA

**Template Version**: 3.3.2
**Last Updated**: February 26, 2026 ET
**Project**: 51-ACA -- Azure Cost Advisor (commercial SaaS)
**Path**: `C:\AICOE\eva-foundry\51-ACA\`
**Stack**: Python 3.12 / FastAPI / React 19 / Fluent UI v9 / Azure Container Apps / Cosmos DB NoSQL / Azure OpenAI / Stripe

> This file is the Copilot operating manual for this repository.
> PART 1 is universal -- identical across all EVA Foundation projects.
> PART 2 is project-specific -- customise the placeholders before use.

---

## PART 1 -- UNIVERSAL RULES
> Applies to every EVA Foundation project. Do not modify.

---

### 1. Session Bootstrap (run in this order, every session)

Before answering any question or writing any code:

1. **Establish $base** (51-ACA local data model -- run the bootstrap block in Section 3.1 first):
   - Local ACA data model (port 8011): `http://localhost:8011`
   - Start if not running: `pwsh -File C:\AICOE\eva-foundry\51-ACA\data-model\start.ps1`
   - Reference: `C:\AICOE\eva-foundry\51-ACA\data-model\README.md`
   - `$base` must be set before any model query in this session.

2. **Read this project's governance docs** (in order):
   - `README.md` -- identity, stack, quick start
   - `PLAN.md` -- phases, current phase, next tasks
   - `STATUS.md` -- last session snapshot, open blockers
   - `ACCEPTANCE.md` -- DoD checklist, quality gates (if exists)
   - Latest `docs/YYYYMMDD-plan.md` and `docs/YYYYMMDD-findings.md` (if exists)

3. **Read the skills index** (if `.github/copilot-skills/` exists):
   - List files: `Get-ChildItem .github/copilot-skills/ -Filter "*.skill.md" | Select-Object Name`
   - Read `00-skill-index.skill.md` or the first skill matching the current task's trigger phrase
   - Each skill has a `triggers:` YAML block -- match it to the user's intent

4. **Query the data model** for this project's record:
   ```powershell
   Invoke-RestMethod "$base/model/projects/{PROJECT_FOLDER}" | Select-Object id, maturity, notes
   ```

5. **Produce a Session Brief** -- one paragraph: active phase, last test count, next task, open blockers.
   Do not skip this. Do not start implementing before the brief is written.

---

### 2. DPDCA Execution Loop

Every session runs this cycle. Do not skip steps.

```
Discover  --> synthesise current sprint from plan + findings docs
Plan      --> pick next unchecked task from yyyymmdd-plan.md checklist
Do        --> implement -- make the change, do not just describe it
Check     --> run the project test command (see PART 2); must exit 0
Act       --> update STATUS.md, PLAN.md, yyyymmdd-plan.md, findings doc
Loop      --> return to Discover if tasks remain
```

**Execution Rule**: Make the change. Do not propose, narrate, or ask for permission on a step you can determine yourself. If uncertain about scope, ask one clarifying question then proceed.

---

### 3. EVA Data Model API -- Mandatory Protocol

> **GOLDEN RULE**: The `model/*.json` files are an internal implementation detail of the API server.
> Agents must never read, grep, parse, or reference them directly -- not even to "check" something.
> The HTTP API is the only interface. One HTTP call beats ten file reads.
> The API self-documents: `GET /model/agent-guide` returns the complete operating protocol.

> **Full reference**: `C:\AICOE\eva-foundry\51-ACA\data-model\README.md`
> The model is the single source of truth. One HTTP call beats 10 file reads.
> Never grep source files for something the model already knows.

#### 3.1  Bootstrap

```powershell
# 51-ACA local data model (port 8011, MemoryStore -- no Cosmos required)
$base = "http://localhost:8011"
$h = Invoke-RestMethod "$base/health" -ErrorAction SilentlyContinue
# Start if not running
if (-not $h) {
    pwsh -File "C:\AICOE\eva-foundry\51-ACA\data-model\start.ps1"
    Start-Sleep 4
    $h = Invoke-RestMethod "$base/health" -ErrorAction SilentlyContinue
}
if (-not $h) { Write-Warning "[WARN] data-model not responding on port 8011 -- check start.ps1" }
# The API self-documents -- read the agent guide before doing anything
Invoke-RestMethod "$base/model/agent-guide"
# One-call state check -- all 27 layer counts + total objects
Invoke-RestMethod "$base/model/agent-summary"
```

**Azure APIM (CI / cloud agents):**
```powershell
$base = "https://marco-sandbox-apim.azure-api.net/data-model"
$hdrs = @{"Ocp-Apim-Subscription-Key" = $env:EVA_APIM_KEY}
Invoke-RestMethod "$base/model/agent-summary" -Headers $hdrs
```

#### 3.2  Query Decision Table

| You want to know... | One-turn API call | FORBIDDEN (costs 10 turns) |
|---|---|---|
| Browse all layers + objects visually | portal-face `/model` (requires `view:model` permission) | grep model/*.json |
| Report: overview / endpoint matrix / edge types | portal-face `/model/report` | build ad-hoc queries |
| All layer counts | `GET /model/agent-summary` | query each layer separately |
| Object by ID | `GET /model/{layer}/{id}` | grep, file_search |
| All objects in a layer | `GET /model/{layer}/` | read source files |
| All ready-to-call endpoints | `GET /model/endpoints/filter?status=implemented` | grep router files |
| All unimplemented stubs | `GET /model/endpoints/filter?status=stub` | grep router files |
| Filter ANY other layer | `GET /model/{layer}/` + `Where-Object` client-side | no server filter on non-endpoint layers |
| What a screen calls | `GET /model/screens/{id}` -> `.api_calls` | read screen source |
| Auth / feature flag for endpoint | `GET /model/endpoints/{id}` -> `.auth`, `.auth_mode`, `.feature_flag` | grep auth middleware |
| Where is the route handler | `GET /model/endpoints/{id}` -> `.implemented_in`, `.repo_line` | file_search |
| Cosmos container schema | `GET /model/containers/{id}` -> `.fields`, `.partition_key` | read Cosmos config |
| What breaks if container changes | `GET /model/impact/?container=X` | trace imports manually |
| Relationship graph | `GET /model/graph/?node_id=X&depth=2` | read config files |
| Services list | `GET /model/services/` -> `obj_id, status, is_active, notes` | services uses obj_id not id; no type/port |
| Is the process alive? | `GET /health` -> `.status`, `.store`, `.version` | check process list |
| Is Cosmos reachable? | `GET /health` -> `.store` == "cosmos" means Cosmos-backed | ping Cosmos directly |
| Browse all layers + objects visually | portal-face `/model` (requires `view:model` permission) | grep model/*.json |
| Report: overview stats / endpoint matrix / edge types | portal-face `/model/report` | build ad-hoc PowerShell queries |

#### 3.3  PUT Rules -- Read Before Every Write

**Rule 1 -- Capture `row_version` BEFORE mutating (not in USER-GUIDE)**
Store it before any field changes so the confirm assert can check `previous + 1`.
```powershell
$ep      = Invoke-RestMethod "$base/model/endpoints/GET /v1/tags"
$prev_rv = $ep.row_version   # capture BEFORE mutation
$ep.status         = "implemented"
```

**Rule 2 -- Strip audit columns, keep domain fields**
Exclude: `obj_id`, `layer`, `modified_by`, `modified_at`, `created_by`, `created_at`, `row_version`, `source_file`.
`is_active` is a domain field -- keep it.
```powershell
function Strip-Audit ($obj) {
    $obj | Select-Object * -ExcludeProperty `
        obj_id, layer, modified_by, modified_at, created_by, created_at, row_version, source_file
}
```

**Rule 3 -- Assign ConvertTo-Json before piping; use -Depth 10 for nested schemas**
`-Depth 5` silently truncates `request_schema` / `response_schema` objects. Always use `-Depth 10`.
```powershell
$body = Strip-Audit $ep | ConvertTo-Json -Depth 10
Invoke-RestMethod "$base/model/endpoints/GET /v1/tags" `
    -Method PUT -ContentType "application/json" -Body $body `
    -Headers @{"X-Actor"="agent:copilot"}
```

**Rule 4 -- PATCH is not supported** -- always PUT the full object (422 otherwise).

**Rule 5 -- Endpoint id = exact string "METHOD /path"** -- never construct; copy verbatim:
```powershell
Invoke-RestMethod "$base/model/endpoints/" |
    Where-Object { $_.path -like '*translations*' } | Select-Object id, path
```

**Rule 6 -- Never PUT inside a `pwsh -Command` inline string** -- JSON escaping is mangled by shell quoting.
Write a `.ps1` script file and run it with `pwsh -File`. This is the single most common cause of failed model
writes. If a PUT fails on the first attempt, the first diagnosis is: is the body in an inline string?

WRONG (JSON escaping breaks silently):
```
pwsh -NoLogo -NonInteractive -Command "& { $body=... | ConvertTo-Json; Invoke-RestMethod ... -Body $body }"
```

RIGHT -- write a temp script, run it with -File:
```powershell
$script = @'
$base = "http://localhost:8011"
$obj  = Invoke-RestMethod "$base/model/{layer}/{id}"
$obj.status = "implemented"
$body = $obj | Select-Object * -ExcludeProperty layer,modified_by,modified_at,created_by,created_at,row_version,source_file | ConvertTo-Json -Depth 10
Invoke-RestMethod "$base/model/{layer}/{id}" -Method PUT -ContentType "application/json" -Body $body -Headers @{"X-Actor"="agent:copilot"}
'@
$script | Set-Content "$env:TEMP\put-model.ps1" -Encoding UTF8
pwsh -NoProfile -File "$env:TEMP\put-model.ps1"
```

**Rule 7 -- `get_terminal_output` only accepts IDs from `run_in_terminal(isBackground=true)`**
Never pass `"1"`, `"last"`, `"pwsh"`, or any terminal name/label as the ID.
The only valid ID is the opaque string returned by `run_in_terminal` when `isBackground=true`.
For a foreground terminal the output is returned inline -- no follow-up call needed.

```powershell
# WRONG
get_terminal_output(id="1")
get_terminal_output(id="pwsh")

# CORRECT -- capture the id from a background run, then use it:
# result = run_in_terminal(command="...", isBackground=true)
# get_terminal_output(id=result.id)
```

**Rule 8 -- Never call `create_file` on a path that already exists**
`create_file` on an existing file returns a hard error and makes no change.
Before any `create_file`, use `Test-Path` to check, then use `replace_string_in_file` or
`multi_replace_string_in_file` for edits to existing files.

```powershell
# Pre-flight check
if (Test-Path "C:\AICOE\path\to\file.ps1") {
    # use replace_string_in_file -- do NOT call create_file
} else {
    # safe to call create_file
}
```

#### 3.4  Write Cycle -- Every Model Change

**Preferred -- 3-step (admin/commit = export + assemble + validate in one call):**
```powershell
# Step 1 -- PUT
Invoke-RestMethod "$base/model/endpoints/GET /v1/tags" `
    -Method PUT -ContentType "application/json" -Body $body `
    -Headers @{"X-Actor"="agent:copilot"}

# Step 2 -- Canonical confirm: assert all three
$w = Invoke-RestMethod "$base/model/endpoints/GET /v1/tags"
$w.row_version   # must equal $prev_rv + 1
$w.modified_by   # must equal "agent:copilot"
$w.status        # must equal the value you PUT

# Step 3 -- Close the cycle
$c = Invoke-RestMethod "$base/model/admin/commit" `
    -Method POST -Headers @{"Authorization"="Bearer dev-admin"}
$c.status          # "PASS" = done; "FAIL" = fix violations before merging
$c.violation_count # 0 = clean
# ACA note: commit returns status=FAIL with assemble.stderr="Script not found" -- EXPECTED on ACA.
# PASS conditions on ACA: violation_count=0 AND exported_total matches agent-summary.total AND export_errors.Count=0.
```

**Manual fallback (if admin/commit unavailable):**
```
POST /model/admin/export  ->  scripts/assemble-model.ps1  ->  scripts/validate-model.ps1
[FAIL] lines block; [WARN] repo_line lines (38+) are pre-existing noise -- ignore
```

**Validate only (distinguishes new violations from pre-existing noise):**
```powershell
$v = Invoke-RestMethod "$base/model/admin/validate" `
       -Headers @{"Authorization"="Bearer dev-admin"}
$v.count       # 0 = clean; >0 = new violations to fix NOW
$v.violations  # the cross-reference FAILs -- fix these before commit
```

#### 3.5  Fix a Validation FAIL

```
Pattern: "screen 'X' api_calls references unknown endpoint 'Y'"
Root cause: api_calls used a wrong or constructed id.
```
```powershell
# Find the exact id  (never construct)
Invoke-RestMethod "$base/model/endpoints/" |
    Where-Object { $_.path -like '*conversation*' } | Select-Object id, path
# Fetch screen, replace bad id, PUT + Strip-Audit + ConvertTo-Json -Depth 10 + commit
```

#### 3.6  What to Update for Each Source Change

| Source change | Model layers to update |
|---|---|
| New FastAPI endpoint | `endpoints` + `schemas` |
| Stub -> implemented | `endpoints` -- set `status`, `implemented_in`, `repo_line` |
| New Cosmos container/field | `containers` |
| New React screen | `screens` + `literals` |
| New i18n key | `literals` |
| New hook / component | `hooks` / `components` |
| New persona / feature flag | `personas` + `feature_flags` |
| New Azure resource | `infrastructure` |
| New agent | `agents` |

> **Same-PR rule**: every source change that affects a model object must update the model
> in the same commit. Never defer. A stale model is worse than no model.

---

### 4. Encoding and Output Safety

**Windows Enterprise Encoding (cp1252) -- ABSOLUTE RULE**

```python
# [FORBIDDEN] -- causes UnicodeEncodeError in enterprise Windows
print("success")   # with any emoji or unicode

# [REQUIRED] -- ASCII only
print("[PASS] Done")   print("[FAIL] Failed")   print("[INFO] Wait...")
```

- All Python scripts: `PYTHONIOENCODING=utf-8` in any .bat wrapper
- All PowerShell output: `[PASS]` / `[FAIL]` / `[WARN]` / `[INFO]` -- never emoji
- Machine-readable outputs (JSON, YAML, evidence files): ASCII-only always
- Markdown docs (README, STATUS, PLAN, ACCEPTANCE, copilot-instructions): ASCII-only -- no emoji anywhere

---

### 5. Context Health Protocol

Maintain a mental count of Do steps (file edits, terminal commands, test runs) this session.

| Milestone | Action |
|---|---|
| Step 5  | Context health check -- answer 4 questions from memory, verify against state files |
| Step 10 | Health check + re-read SESSION-STATE.md or STATUS.md |
| Step 15 | Health check + re-read + state summary aloud |
| Every 5 after | Repeat step-10 pattern |

**4 health questions:**
1. What is the active task and its one-line description?
2. What was the last recorded test count?
3. What file am I currently editing or about to edit?
4. Have I run any terminal command I cannot account for?

**Drift signals** -- trigger immediate check:
- About to search for a file already read this session
- About to run the full test suite without isolating the failing test first
- Proposing an approach that contradicts a decision in PLAN.md
- Uncertainty about which task or sprint is active

**Recovery**: re-read STATUS.md from disk -> run baseline tests -> resume from last verified state.

---

### 6. Python Environment

```
venv exec: C:\AICOE\.venv\Scripts\python.exe
activate:  C:\AICOE\.venv\Scripts\Activate.ps1
```

Never use bare `python` or `python3`. Always use the full venv path.

---

### 7. Azure Account Pattern

- **Personal / Dev**: `EsDAICoESub` (`d2d4e571-e0f2-4f6c-901a-f88f7669bcba`) -- sandbox (Phase 1 marco* resources)
- **Professional**: `marco.presta@hrsdc-rhdcc.gc.ca` -- Government of Canada / production resources
  - Dev subscription:  `d2d4e571-e0f2-4f6c-901a-f88f7669bcba` (EsDAICoESub -- used for Phase 1)
  - Prod subscription: TBD (Phase 2 -- private ACA subscription, not yet provisioned)

If `az` fails with "subscription doesn't exist":
```powershell
az account show --query user.name
az logout; az login --use-device-code
az account set --subscription d2d4e571-e0f2-4f6c-901a-f88f7669bcba
```

---



## PART 2 -- 51-ACA PROJECT SPECIFIC

> ACA is a commercial SaaS product. Every code change is a potential revenue impact.
> Tier 1 report must never expose implementation details. Tenant isolation is non-negotiable.

---

### P2.1 Architecture Overview

**Three services + one API + one frontend:**

```
frontend/          React 19 + Fluent UI v9 (Tier 1/2/3 UI, checkout, download)
services/api/      FastAPI -- orchestration hub, auth, tier gating, APIM-facing
services/collector/  Python worker -- Azure SDK inventory + cost + advisor + network pull
services/analysis/   Python worker -- 12 rules + 29-foundry agents -> findings JSON
services/delivery/   Python worker -- IaC generator + zip packager (Tier 3)
agents/            29-foundry agent definitions (collection, analysis, generation, redteam)
infra/
  phase1-marco/    Bicep -- reuse existing marco* sandbox resources
  phase2-private/  Terraform -- clean private ACA subscription
.github/workflows/ CI (lint+test), deploy-phase1, deploy-phase2, collector-schedule
```

**Data flow:**
```
Client browser
  -> frontend React
  -> services/api (APIM + Entra auth)
  -> collector job (Azure SDK -> Cosmos)
  -> analysis job (Cosmos -> findings JSON -> Cosmos)
  -> frontend shows Tier 1 report
  -> Stripe checkout -> tier upgrade in Cosmos
  -> delivery job (findings + inventory -> zip -> Storage SAS URL)
```

**Tenant isolation**: Cosmos partition key = `subscriptionId`. API middleware enforces
partition filter on every DB call. No cross-tenant query is possible at the code level.

---

### P2.2 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Fluent UI v9 (from 31-eva-faces patterns) |
| API | FastAPI 0.115+, Python 3.12 |
| Auth | MSAL Python (delegated + SP modes), Entra OIDC for ACA users |
| Database | Cosmos DB NoSQL (marco-sandbox-cosmos Phase 1 / aca-cosmos Phase 2) |
| AI / LLM | Azure OpenAI GPT-4o via marco-sandbox-openai-v2 (Phase 1) |
| Agent framework | 29-foundry (collection, analysis, generation, redteam agents) |
| Payment | Stripe (Tier 2 / Tier 3 checkout, webhook unlock) |
| Infra Phase 1 | Bicep -- reuse marco* resources, no new Azure spend |
| Infra Phase 2 | Terraform modules from 18-azure-best/04-terraform-modules |
| Delivery | Azure Blob Storage (SAS URLs, 7-day expiry); zip with SHA-256 manifest |
| Observability | Application Insights (marco-sandbox-appinsights Phase 1) |
| CI/CD | GitHub Actions (OIDC federation to Azure, GHCR images) |

---

### P2.3 Project Structure

```
51-ACA/
  .github/
    copilot-instructions.md       <- this file
    workflows/
      ci.yml                      <- lint + test on every PR
      deploy-phase1.yml           <- push to marco* resources
      deploy-phase2.yml           <- push to private ACA subscription
      collector-schedule.yml      <- nightly collection cron
  services/
    api/
      app/
        main.py                   <- FastAPI app factory
        routers/                  <- auth, scans, findings, checkout, admin
        middleware/               <- tenant isolation, tier gating
        models/                   <- Pydantic schemas
        db/                       <- Cosmos client + partition helpers
        settings.py               <- pydantic-settings
      Dockerfile
      requirements.txt
    collector/
      app/
        main.py                   <- entry point (runs as Container App Job)
        azure_client.py           <- ARM / Resource Graph / Cost Mgmt / Advisor
        preflight.py              <- RBAC + capability probes
        ingest.py                 <- normalize and write to Cosmos
      requirements.txt
    analysis/
      app/
        main.py                   <- entry point (Container App Job)
        rules/                    <- 12 rule modules (one file per rule)
        agents/                   <- analysis-agent + redteam-agent (29-foundry)
        findings.py               <- assemble findings JSON, tier gating
      requirements.txt
    delivery/
      app/
        main.py                   <- entry point (Container App Job)
        templates/                <- IaC template library (12 categories)
        generator.py              <- parametrize templates from inventory
        packager.py               <- assemble + sign zip, upload to blob
      requirements.txt
  frontend/
    src/
      pages/                      <- Login, ConnectSubscription, Status, Findings, Download
      components/                 <- OpportunityCard, SavingsBar, TierGate, CheckoutCTA
      hooks/                      <- useFindings, useScanStatus, useCheckout
      api/                        <- ACA API client (typed)
    package.json
    vite.config.ts
  agents/
    collection-agent.yaml         <- 29-foundry agent spec
    analysis-agent.yaml
    generation-agent.yaml
    redteam-agent.yaml
  infra/
    phase1-marco/
      main.bicep                  <- Cosmos containers + KV secrets wiring
      cosmos-containers.bicep
    phase2-private/
      main.tf                     <- full private subscription provisioning
      variables.tf
      modules/                    <- reuses 18-azure-best/04-terraform-modules
  docs/
    api-spec.md                   <- from 05-technical.md
    onboarding-spec.md            <- from 02-preflight.md
    saving-opportunity-rules.md   <- 12 rules reference
    iac-template-library.md       <- Tier 3 template catalogue
  .env.example
  .gitignore
  docker-compose.yml              <- local dev (API + frontend + Cosmos emulator)
  pyproject.toml                  <- shared Python tooling config
  README.md / PLAN.md / STATUS.md / ACCEPTANCE.md
```

---

### P2.4 Development Workflows

**Local dev setup:**
```powershell
# 1. Clone
git clone https://github.com/eva-foundry/51-ACA.git
cd 51-ACA

# 2. Python venv (shared across services for local dev)
C:\AICOE\.venv\Scripts\Activate.ps1
pip install -r services/api/requirements.txt
pip install -r services/collector/requirements.txt
pip install -r services/analysis/requirements.txt
pip install -r services/delivery/requirements.txt

# 3. Frontend
cd frontend && npm install && cd ..

# 4. Environment
copy .env.example .env   # fill in ACA_COSMOS_URL, ACA_OPENAI_KEY, etc.

# 5. Run (local docker-compose)
docker compose up
# OR run API only:
C:\AICOE\.venv\Scripts\python.exe -m uvicorn services.api.app.main:app --reload --port 8080
```

**Quick commands:**
```powershell
# Run all tests
C:\AICOE\.venv\Scripts\python.exe -m pytest services/ -v

# Lint
C:\AICOE\.venv\Scripts\python.exe -m ruff check services/

# Type check
C:\AICOE\.venv\Scripts\python.exe -m mypy services/

# Frontend
cd frontend && npm run dev      # dev server
cd frontend && npm run build    # production build
cd frontend && npm test         # vitest
```

**Test command for DPDCA Check step:**
```powershell
C:\AICOE\.venv\Scripts\python.exe -m pytest services/ -x -q 2>&1
```
Must exit 0 before any commit.

---

### P2.5 Critical Code Patterns

#### Pattern 1: Tenant Isolation Middleware

Every Cosmos query MUST include the partition key. The API middleware extracts
`subscriptionId` from the auth token or request body and injects it into every
DB operation. Never call `cosmos_client.query_items()` without a `partition_key` argument.

```python
# services/api/app/middleware/tenant.py
def get_subscription_id(request: Request) -> str:
    sub_id = request.state.subscription_id  # set by auth middleware
    if not sub_id:
        raise HTTPException(status_code=403, detail="No subscription context")
    return sub_id

# services/api/app/db/cosmos.py
def query_findings(sub_id: str) -> list:
    # CORRECT -- always partition-scoped
    return list(container.query_items(
        query="SELECT * FROM c WHERE c.subscriptionId = @sub",
        parameters=[{"name": "@sub", "value": sub_id}],
        partition_key=sub_id,   # MANDATORY
    ))
```

#### Pattern 2: Tier Gating on Findings

The analysis engine produces full findings. The API layer strips fields based on tier.
Never return full findings to Tier 1 clients.

```python
# services/api/app/routers/findings.py
def gate_findings(findings: list, tier: str) -> list:
    if tier == "tier1":
        return [{"id": f["id"], "title": f["title"],
                 "category": f["category"],
                 "estimated_saving_low": f["estimated_saving_low"],
                 "estimated_saving_high": f["estimated_saving_high"],
                 "effort_class": f["effort_class"]} for f in findings]
    if tier == "tier2":
        return [{k: v for k, v in f.items() if k != "deliverable_template_id"}
                for f in findings]
    return findings  # tier3: full object
```

#### Pattern 3: Collector MSAL Delegated Auth

```python
# services/collector/app/azure_client.py
import msal, os

def get_arm_token(client_id: str, tenant_id: str, refresh_token: str) -> str:
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )
    result = app.acquire_token_by_refresh_token(
        refresh_token,
        scopes=["https://management.azure.com/.default"],
    )
    if "access_token" not in result:
        raise RuntimeError(f"[FAIL] Token refresh: {result.get('error_description')}")
    return result["access_token"]
```

#### Pattern 4: Rule Output Schema

Every analysis rule must return a dict conforming to this shape.
Do not invent new fields -- extend via `extra` only if approved.

```python
FINDING = {
    "id": "rule-01-dev-box-autostop",       # kebab-case, stable
    "category": "compute-scheduling",
    "title": "Dev Box instances run nights and weekends",  # plain English, no how-to
    "estimated_saving_low":  5548,           # CAD/yr
    "estimated_saving_high": 7902,
    "effort_class": "trivial",               # trivial|easy|medium|involved|strategic
    "risk_class": "none",                    # none|low|medium|high
    "heuristic_source": "rule-01",
    "narrative": "...",                      # Tier 2+ only
    "deliverable_template_id": "tmpl-dev-box-autostop",  # Tier 3 only
}
```

---

### P2.6 Phase 1 Infrastructure (marco* resources)

Phase 1 reuses existing resources. No new Azure spend.

| Resource | Purpose in ACA | Notes |
|---|---|---|
| marco-sandbox-cosmos | ACA database | Create new DB: aca-db, containers: scans/inventories/cost-data/advisor/findings |
| marco-sandbox-apim | API gateway | Add ACA product + subscription key policy |
| marco-sandbox-openai-v2 | Analysis LLM | Use existing deployment |
| marco-sandbox-foundry | Agent orchestration | Use existing Foundry project |
| marcosandacr20260203 | Container images | ACA images pushed here |
| marcosandkv20260203 | Secrets | Add: ACA-CLIENT-ID, ACA-OPENAI-KEY, ACA-COSMOS-CONN |
| marco-sandbox-appinsights | Observability | Use existing App Insights |
| marcosandboxfinopshub | Cost export landing | Already configured for 91-day exports |
| marco-sandbox-finops-adf | Cost ingestion | ADF pipeline already working |
| marco-sandbox-search | Azure AI Search (Free) | Full-text + semantic search (Phase 2 candidate) |
| marco-sandbox-aisvc | Azure AI Services | CognitiveServices -- NLP / content moderation |
| marco-sandbox-docint | Form Recognizer | Document Intelligence for IaC parsing (Tier 3) |
| marco-sandbox-backend | App Service (linux/container) | Pre-existing backend slot; candidate for ACA API |
| marco-sandbox-enrichment | App Service (linux) | Pre-existing enrichment slot; candidate for collector |

**Phase 1 deploy:**
```powershell
# Deploy collector + analysis + delivery as Container App Jobs
# Deploy API as Container App
# All in existing EsDAICoE-Sandbox resource group
az deployment group create \
  --resource-group EsDAICoE-Sandbox \
  --template-file infra/phase1-marco/main.bicep \
  --parameters @infra/phase1-marco/params.json
```

---

### P2.7 Tier and Data Model Notes

- Do not register ACA services in the EVA data model API until Phase 1 is go-live.
- When ready: `POST /model/services/` with service record for `aca-api`, `aca-collector`,
  `aca-analysis`, `aca-delivery`.
- Register endpoints in the model as each route is implemented.

---

### P2.8 Troubleshooting

**Cosmos 403 on query**: Check that `partition_key=subscriptionId` is present. Never query
without partition key.

**MSAL token refresh fails**: Refresh token may be expired (default 90 days). Prompt client
to reconnect via `/v1/auth/reconnect`. Store new refresh token in Key Vault.

**Collector times out on large subscription**: Enable Resource Graph pagination
(`$skipToken`). Cost Management: use `ADF pipeline` mode via `marcosandboxfinopshub`
instead of direct API. See `02-preflight.md` for probe checks.

**Tier 1 report shows implementation detail**: BUG -- check `gate_findings()` in
`services/api/app/routers/findings.py`. Tier 1 must strip `narrative` and
`deliverable_template_id`.

**Stripe webhook returns 400**: Check `STRIPE_WEBHOOK_SECRET` in Key Vault. Webhook
signature validation fails if the raw request body is consumed before verification.
Use `await request.body()` before any JSON parsing.

---

### P2.9 Roles, Secrets, and Infra Identity

**ACA Application Roles (Entra ID groups -- define before Phase 1 go-live)**

| Role | Permissions | Cosmos Access |
|---|---|---|
| ACA_Admin | Full admin: tenant management, lock, reconcile, tier overrides | Read + write all containers |
| ACA_Support | Read customers + scan runs; no destructive actions | Read scans, inventories, findings |
| ACA_FinOps | Billing reconcile + Stripe webhook management only | Read cost-data, advisor |

**Secrets in `marcosandkv20260203` (RBAC-enabled, EsDAICoE-Sandbox, canadacentral)**

| Secret Name | Purpose | Status |
|---|---|---|
| ADO-PAT | Azure DevOps PAT for ado-import scripts (len=84, rotates 90d) | Present |
| ACA-CLIENT-ID | MSAL app client ID for delegated auth | Add before Phase 1 deploy |
| ACA-OPENAI-KEY | OpenAI key for marco-sandbox-openai-v2 | Add before Phase 1 deploy |
| ACA-COSMOS-CONN | Cosmos DB connection string for aca-db | Add before Phase 1 deploy |
| STRIPE-SECRET-KEY | Stripe secret key for checkout | Add before Tier 2 launch |
| STRIPE-WEBHOOK-SECRET | Stripe webhook signing secret | Add before Tier 2 launch |

**Key Vault access (RBAC mode):**
```powershell
# Read a secret
az keyvault secret show --vault-name marcosandkv20260203 --name ADO-PAT --query value -o tsv

# Set a secret
az keyvault secret set --vault-name marcosandkv20260203 --name ACA-CLIENT-ID --value "<value>"
```

**Subscription and RG reference:**
```
Subscription : d2d4e571-e0f2-4f6c-901a-f88f7669bcba (EsDAICoESub)
Resource Group: EsDAICoE-Sandbox
Region        : canadacentral (primary), canadaeast (OpenAI + Foundry)
All marco* resources live in EsDAICoE-Sandbox unless noted.
```

**Complete marco* resource inventory (from MARCO-INVENTORY-20260213):**

| Resource Name | Type | Region |
|---|---|---|
| marcosandkv20260203 | Key Vault | canadacentral |
| marcosandacr20260203 | Container Registry (Basic) | canadacentral |
| marcosand20260203 | Storage Account | canadacentral |
| marcosandboxfinopshub | Storage Account (FinOps hub) | canadacentral |
| marco-sandbox-cosmos | Cosmos DB (NoSQL) | canadacentral |
| marco-sandbox-apim | API Management | canadacentral |
| marco-sandbox-appinsights | Application Insights | canadacentral |
| marco-sandbox-func | Function App (Linux) + App Insights | canadacentral |
| marco-sandbox-search | AI Search | canadacentral |
| marco-sandbox-finops-adf | Data Factory | canadacentral |
| marco-sandbox-backend | App Service (linux/container) | canadacentral |
| marco-sandbox-enrichment | App Service (linux) | canadacentral |
| marco-sandbox-aisvc | Azure AI Services (CognitiveServices) | canadacentral |
| marco-sandbox-openai | Azure OpenAI (S0) | canadaeast |
| marco-sandbox-openai-v2 | Azure OpenAI (S0) | canadaeast |
| marco-sandbox-foundry | Azure AI Services (AIServices) + project | canadaeast |
| marco-sandbox-docint | Form Recognizer | canadacentral |

---

**For comprehensive specs see:**
- `01-feasibility.md` -- auth pattern decision
- `02-preflight.md` -- onboarding + permission validation spec
- `05-technical.md` -- full API spec + FastAPI skeleton
- `08-payment.md` -- Stripe backend stubs
- `12-IaCscript.md` -- IaC template library
- `docs/saving-opportunity-rules.md` -- 12 rule reference
