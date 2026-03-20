# 51-ACA Audit Action Plan
**Date**: March 13, 2026 @ 8:14 AM ET  
**Veritas MTI Score**: 98/100 (Coverage 100%, Consistency 100%, Field Population 84%)  
**Session Phase**: PLAN → DO (ready to execute)

---

## Executive Summary

Veritas audit identified:
- ✅ Zero gaps in story structure/evidence
- ✅ 100% coverage and consistency
- ⚠️  17 stories missing metadata (sprint, assignee, ado_id)
- ⚠️  04 documentation inconsistencies with cross-project ecosystem
- ⚠️  Paperless governance not fully documented

**Impact**: MTI score at 98 (excellent). Field population penalties from incomplete metadata = 2-point lift opportunity.

---

## PRIORITY 1: HIGH-IMPACT FIXES (Improves MTI to 99-100)

### 1.1 Fill Missing Story Metadata
**Effort**: 30 minutes | **Impact**: +1-2 MTI points | **Gate**: Required for Phase 1 closure

**Affected Stories** (17 total):
```
ACA-03-001, ACA-03-003, ACA-03-008, ACA-03-012, ACA-03-013, ACA-03-014, ACA-03-015, ACA-03-016
ACA-14-002, ACA-14-003  
+ 7 more (incomplete list in STATUS.md)
```

**Fields to Complete**:
- `sprint`: Assign to correct Sprint ID (e.g., "Sprint-48", "Sprint-47")
- `assignee`: Add GitHub username or email (e.g., "@marco", "marco@example.com")
- `ado_id`: Map to Azure DevOps work item ID (reference .eva/ado-id-map.json)

**Implementation**:
- [ ] Query `GET /model/wbs/?project_id=51-ACA&status=done` from data model API
- [ ] For each story with missing fields, perform PUT to update WBS record
- [ ] Validate row_version increment (confirms write succeeded)
- [ ] Run Veritas audit to confirm +2 MTI

**Evidence**: Create file `.eva/audit-fixes-metadata-fill-20260313.json` with all updates

---

### 1.2 Update Cross-Project Integration References
**Effort**: 45 minutes | **Impact**: Consistency, clarity | **Audience**: Project team

**Files to Update**:

#### A. `README.md` - Add FKTE Context Section
Insert after "Strategic Value" section (currently around line 35):
```markdown
## Cross-Project Integration

### FKTE Ecosystem
- **57-FKTE**: Architectural home for Fractal Knowledge Transformation Engine
  - Reference: [FKTE Technical Architecture](../57-FKTE/docs/FRACTAL-KNOWLEDGE-TRANSFORMATION-ENGINE.md)
  - 51-ACA is the proof-of-concept / reference implementation

- **58-CyberSec**: Second FKTE implementation (Security Factory)
  - Validates that FKTE pattern generalizes beyond FinOps
  - Uses same tier structure, skill system, and governance patterns

### Infrastructure Integration
- **60-IaC**: Infrastructure-as-Code automation
  - New layers added (L112-L120) bring total from 111 → 120 layers
  - 51-ACA onboarding (Epic 15) should reference L112 (resource_catalog)
  - 51-ACA cost rules should link to L117 (cost_tracking)

### Data Model Integration
- **37-Data-Model**: Central governance model and UI portal
  - View live 51-ACA data: [Model Portal](https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA)
  - Query 51-ACA WBS: `GET /model/wbs/?project_id=51-ACA`
  - Run Veritas audit: `audit_repo` MCP tool

### Autonomous UI Generation
- **30-UI-Bench**: Screen generation framework
  - 51-ACA dashboards can be auto-generated from data model definitions
  - Layer screens available at 37-data-model `/model` portal
```

#### B. `PLAN.md` - Add Paperless Governance Section
Insert before MILESTONES section (around line 600):
```markdown
## Paperless Governance & Data Model Sync

**Source of Truth**: Central EVA data model (Project 37)
- **Project Record**: https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA
- **WBS Query**: GET `/model/wbs/?project_id=51-ACA`
- **Evidence Query**: GET `/model/evidence/?project_id=51-ACA`

**Synchronization Protocol**:
Every Friday end-of-sprint, run:
```
cd C:\eva-foundry\48-eva-veritas
node src/cli.js audit --repo "C:/eva-foundry/51-ACA" --threshold 70
node src/cli.js sync --repo "C:/eva-foundry/51-ACA" --source api
```

**Skills Registered** (workspace integration):
- `@audit_repo` — Run full governance audit
- `@sync_repo` — Full paperless DPDCA (audit + write-back + export)
- `@get_trust_score` — Quick MTI check
- `@export_to_model` — Extract WBS/evidence/decisions to data model API
- `@sprint-advance` — Run sprint-start verification gates
```

#### C. `STATUS.md` - Add Latest Audit Results
Insert after "Veritas Audit Output" section:
```markdown
## Latest Audit (March 13, 2026 @ 8:14 AM ET)

```
Audit:   C:\eva-foundry\51-ACA
MTI:     98/100 (Coverage 100%, Consistency 100%, Field Pop 84%)
Summary: 281 stories, 100% artifact/evidence coverage
Gaps:    0
Actions: Fill metadata (sprint/assignee/ado_id) for 17 done stories → +2 MTI
```

### Evidence Files
- `.eva/discovery.json` — WBS discovery output
- `.eva/reconciliation.json` — Artifact mapping
- `.eva/trust.json` — MTI calculation details
- `.eva/audit-fixes-metadata-fill-20260313.json` — Metadata fill proof
```

#### D. `.github/copilot-instructions.md` - Fix API Endpoint References
**Issue**: References both localhost:8010 and cloud API without clarity

**Fixes**:
1. Line 17: Change "Central EVA data model on port 8010" to:
   > **Central EVA data model**: Project 37 hosted at:
   > - Local dev: `http://localhost:8010` (for local testing)
   > - Cloud production: `https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io` (primary)
   > - CI/Cloud agents: via APIM gateway

2. Line 20-21: Add note:
   > **Data Migration**: 51-ACA migrated from local SQLite to Cosmos (March 5, 2026). All queries now go to cloud API endpoints.

3. Add new section before "3.1 Bootstrap":
   ```markdown
   #### 3.0.1 Endpoint Decision Matrix
   
   | Scenario | Endpoint | Why |
   |----------|----------|-----|
   | Local development | `http://localhost:8010` | Instant feedback, offline capable |
   | CI/CD pipelines | Cloud APIM + bearer token | Uniform across all environments |
   | Cloud agents (51-ACA) | Cloud APIM + RBAC | Production audit trail |
   | This session | Cloud APIM (BOOTSTRAP above) | Workspace-wide standard |
   ```

---

## PRIORITY 2: MEDIUM-IMPACT FIXES (Improves Clarity & Consistency)

### 2.1 Create Skill Index Documentation
**Effort**: 20 minutes | **Impact**: Discoverability

**Create file**: `51-ACA/.github/copilot-skills/00-SKILL-INDEX.md`

```markdown
# 51-ACA Skills Index

Workspace-registered skills available for 51-ACA project work.

## Quick Reference

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `@sprint-advance` | "start sprint", "verify sprint", "pre-flight" | Pre-sprint verification gates (PLAN/manifests/readiness) |
| `@progress-report` | "progress", "velocity", "status", "metrics" | Sprint progress report (burndown, velocity, blockers) |
| `@gap-report` | "gaps", "missing", "discrepancies", "audit" | Find gaps between actual vs planned work |
| `@sprint-report` | "sprint close", "sprint summary", "retrospective" | Sprint closure report (evidence, learnings, next sprint) |
| `@veritas-expert` | "audit", "trust score", "verify", "governance" | Run Veritas audit and MTI analysis on 51-ACA |

## Detailed Skills

### @sprint-advance
**File**: `sprint-advance.skill.md`
**When**: Run before Sprint starts
**What it does**:
- Verify PLAN.md manifest consistency
- Check all required Sprint files exist
- Validate story counts vs backlog
- Run pre-flight Veritas check
- Gate: MTI must be >= 70 to proceed

**Example**:
```
User: "Verify Sprint-49 is ready to start"
Agent: Runs sprint-advance, checks manifests, confirms readiness
```

### @progress-report
**File**: `progress-report.skill.md`
**When**: During sprint, daily or on-demand
**What it does**:
- Calculate current velocity from closed stories
- Plot burndown from PLAN vs actual
- Identify blockers in STATUS.md
- Show trend (last 5 sprints)

**Example**:
```
User: "What's our velocity this sprint?"
Agent: Queries .eva/ evidence, calculates FP/day, shows trend
```

### @gap-report
**File**: `gap-report.skill.md`
**When**: After audit/sync, or on-demand quality check
**What it does**:
- Compare PLAN.md planned stories vs WBS in data model
- Flag stories in WBS not in PLAN.md
- Flag stories in PLAN.md not in WBS
- List missing artifacts/evidence per story

**Example**:
```
User: "Are we missing any stories from the plan?"
Agent: Runs gap-report, shows discrepancies
```

### @sprint-report  
**File**: `sprint-report.skill.md`
**When**: End of sprint, before merge
**What it does**:
- Summarize sprint outcomes (FP completed, MTI final)
- Link evidence files (commits, PRs, artifacts)
- Document learnings and risks for next sprint
- Generate markdown for CHANGELOG.md entry

**Example**:
```
User: "Close Sprint-48, I want a report"
Agent: Generates sprint-report with all metrics and evidence
```

### @veritas-expert
**File**: `veritas-expert.skill.md`
**When**: Quality gates, trust score checks, governance audits
**What it does**:
- Run full Veritas audit (discovery + reconciliation + trust)
- Check MTI against gate (70)
- Identify discrepancies and field population issues
- Recommend fixes with evidence

**Example**:
```
User: "Run a full audit on 51-ACA"
Agent: Calls Veritas, parses results, identifies gaps, recommends fixes
```
```

---

### 2.2 Create Paperless DPDCA Guide
**Effort**: 25 minutes | **Impact**: Process clarity for team

**Create file**: `51-ACA/docs/PAPERLESS-DPDCA-GUIDE.md`

```markdown
# Paperless DPDCA Guide for 51-ACA

This guide explains how 51-ACA operates as a "paperless" project using the central
EVA data model as the single source of truth.

## What is Paperless Governance?

Traditional projects store work items in local files (PLAN.md, STATUS.md). 51-ACA
instead:
- Stores all work items in central data model API (Project 37 Cosmos DB)
- Uses local README/PLAN/STATUS as human-readable **references** (not masters)
- Syncs local ↔ API weekly via `sync_repo` MCP tool
- Veritas audit is the authoritative quality check

## Weekly Sync Ritual (Every Friday 5 PM ET)

### Step 1: Pre-Sync Verification
```powershell
cd C:\eva-foundry\51-ACA
# Quick health check
node ..\48-eva-veritas\src\cli.js audit --repo . --threshold 70
# Expected: MTI >= 70, Coverage 100%, Consistency 100%
```

### Step 2: Sync to Data Model
```powershell
# Full paperless DPDCA: discover + audit + write-back + export
node ..\48-eva-veritas\src\cli.js sync --repo . --source auto
# This:
# - Queries WBS from data model (L25-26-27)
# - Compares to local PLAN.md
# - Updates local .eva/ evidence files
# - Writes results back to project_work layer (L46)
```

### Step 3: Review Results
Check `.eva/` directory:
- `discovery.json` — WBS discovered from plan
- `reconciliation.json` — Comparison: planned vs actual
- `trust.json` — Final MTI score + field population audit
- Evidence files — Links to commits, PRs, artifacts

### Step 4: Commit & Close Sprint
```powershell
git add -A
git commit -m "chore(sprint-48): paperless sync complete, MTI=$score"
git push
```

## Live Data Model Browser

View 51-ACA data in real-time at:
https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA

Useful queries:
- `GET /model/wbs/?project_id=51-ACA&status=in-progress` — Current sprint work
- `GET /model/evidence/?project_id=51-ACA&$orderby=created%20desc&$limit=10` — Latest evidence
- `GET /model/projects/51-ACA` — Project metadata & phase info

## API-First Decision Making

**Before** asking "Is story X done?":
❌ DON'T: Read PLAN.md locally
✅ DO: Query `GET /model/wbs/ACA-15-001` from API

**Before** "What's the current MTI score?":
❌ DON'T: Read STATUS.md
✅ DO: Run `@veritas-expert` skill (which queries API)

**API is the source of truth. Local files are documentation.**

## Troubleshooting Sync Failures

### Issue: `sync_repo` returns "API unreachable"

**Check**:
1. Is Project 37 running? `curl http://localhost:8010/health` (local) or check cloud
2. Is network connectivity OK? Can you reach `https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/health`?
3. Is your auth token valid? Check `.eva/bootstrap-session-*.json` for fresh credentials

**Recovery**:
- Local-only mode: `sync_repo --allow-degraded` (prints warning, not compliant for prod)
- Cloud mode: Verify cloud API health and retry

### Issue: Metadata fields (sprint, assignee) are empty

**Reason**: These are populated during active sprint work, not during initial sync.

**Fix**:
- During sprint planning: Fill in sprint ID and assignee for each WBS record
- Use PUT `/model/wbs/{id}` to update individual records
- Veritas audit will flag any still-empty fields

## See Also

- [Veritas Audit Output](../.eva/trust.json)
- [Sprint Manifests](.github/sprints/)
- [Evidence Directory](.eva/)
```

---

## PRIORITY 3: LOW-IMPACT ENHANCEMENTS (Nice-to-Have)

### 3.1 Add Example Data Model Queries to README
**Effort**: 15 minutes | **Impact**: Developer convenience

Insert into README "Getting Started" section:
```markdown
### Live Project Status via Data Model API

```powershell
# View current 51-ACA project metadata
curl https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA | jq '.[] | {id, phase, wbs_id, maturity}'

# List all in-progress stories
curl https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/wbs/?project_id=51-ACA&status=in-progress | jq '.[] | {id, label, status}'

# Get latest 10 evidence records
curl https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/evidence/?project_id=51-ACA&$limit=10 | jq '.[-10:] | .[] | {id, type, created_at}'
```
```

### 3.2 Add Veritas Score Badge to README
**Effort**: 5 minutes | **Impact**: Status visibility

Add to README top:
```markdown
| Metric | Value | Status |
|--------|-------|--------|
| **Veritas MTI** | 98/100 | ✅ Pass (gate: 70) |
| **Coverage** | 100% | ✅ Complete |
| **Consistency** | 100% | ✅ Perfect |
| **Field Population** | 84% | ⚠️ Fixable |
```

---

## Execution Order (DO Phase)

**Recommended sequence**:
1. **Priority 1.1** (30 min) — Fill metadata → MTI +2
2. **Priority 1.2** (45 min) — Update docs → consistency
3. **Priority 2.1** (20 min) — Skill index → discoverability
4. **Priority 2.2** (25 min) — Paperless guide → clarity
5. **Priority 3.1 & 3.2** (20 min) — Enhancements
6. **CHECK**: Run Veritas audit → confirm MTI 100
7. **ACT**: Commit evidence

**Total**: ~2.5 hours for full execution

---

## Success Criteria (CHECK Phase)

All fixes applied:
- [ ] 17 stories have sprint/assignee/ado_id filled
- [ ] README has FKTE/cross-project sections
- [ ] PLAN.md has paperless governance notes
- [ ] STATUS.md has March 13 audit results
- [ ] Copilot instructions fixed
- [ ] Skill index created
- [ ] Paperless guide created
- [ ] Veritas audit run → MTI target 100 ✅
- [ ] No regressions vs baseline

**Gate**: MTI >= 98, Coverage 100%, Consistency 100%

