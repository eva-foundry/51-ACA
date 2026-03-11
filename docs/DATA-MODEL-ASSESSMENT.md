# 51-ACA Data Model Assessment

**Date**: 2026-02-28  
**Purpose**: Assess whether data model can replace PLAN.md/STATUS.md as single source of truth  
**Status**: ✅ **PRIORITY 1 COMPLETE** -- 324 WBS objects + 4 sprint objects seeded  
**Completion report**: [docs/SEEDING-COMPLETE.md](SEEDING-COMPLETE.md)

---

## EXECUTIVE SUMMARY

**Can the data model replace PLAN.md/STATUS.md?** YES, with 4 enhancements.

**Current state (after Priority 1 seeding):** ✅ **UPDATED 2026-02-28**
- Data model has 31 layers, 4,060 total objects across EVA ecosystem
- 51-ACA now has **324 WBS objects** in data model (14 epics + 54 features + 256 stories)
- 51-ACA now has **4 sprint objects** in data model (sprint-backlog, sprint-01, sprint-02, sprint-03)
- **100% ADO sync** (all 256 stories have ADO ID mappings)
- 2 existing skills (veritas-expert, sprint-advance) are operational but incomplete

**Completed enhancements:**
1. ✅ **Seed 51-ACA WBS layer** (256 stories from PLAN.md -> data model) -- DONE
2. ✅ **Create sprint objects** (4 objects with ado_iteration_path: "51-aca\\Sprint N") -- DONE

**Remaining enhancements:**
3. ❌ **Create 3 new reporting skills** (sprint-report, gap-report, progress-report) -- TODO (6 hours)
4. ❌ **Enhance parser** (extract acceptance_criteria, related_stories, files_affected) -- TODO (2 hours)

**Benefit:** Single HTTP call answers questions that currently require reading 968-line PLAN.md + 150-line STATUS.md + running veritas audit. **Verified working** via 6 sample queries in verify-data-model.py.

---

## CURRENT STATE ANALYSIS

### What PLAN.md Contains (968 lines)

| Information Type | Example | In Data Model? | Queryable? |
|---|---|---|---|
| Epic hierarchy (14 epics) | Epic 1: Foundation, Epic 3: Analysis | ❌ NO | N/A |
| Feature breakdown (60+ features) | Feature 1.1: Local dev environment | ❌ NO | N/A |
| Story details (257 stories) | Story 1.1.1 [ACA-01-001]: docker-compose up | ❌ NO | N/A |
| Function points per story | ACA-01-001 FP: XS=1 | ❌ NO | N/A |
| Story status (DONE/ACTIVE/PLANNED) | Status: DONE (Sprint-02) | ❌ NO | N/A |
| Sprint assignments | Sprint: Sprint-02 | ❌ NO | N/A |
| Acceptance criteria | "All services start without error" | ❌ NO | N/A |
| Related dependencies | Related: Story 2.5.4 | ❌ NO | N/A |
| File references | Files: services/api/app/main.py | ❌ NO | N/A |
| Epic totals | Epic 13 total: 55 FP, 11 stories | ❌ NO | N/A |
| Decision records | DECISION LOCKED 2026-02-27 | ❌ NO | N/A |

**Key gap:** 100% of PLAN.md information lives ONLY in the markdown file. Zero WBS objects for 51-ACA in data model.

### What STATUS.md Contains (150 lines)

| Information Type | Example | In Data Model? | Queryable? |
|---|---|---|---|
| Session summaries | Session: 2026-02-28 Architecture docs | ❌ NO | N/A |
| Commit hashes | ad1463a, f2d1932, 36bc1da | ❌ NO | N/A |
| Test counts | 24/24 passing | ❌ NO | N/A |
| MTI scores | MTI: 100 (gated to 30) | ⚠️ PARTIAL | Via veritas audit only |
| Open blockers | "Open blockers: NONE" | ❌ NO | N/A |
| Active epic | Active Epic: Epic 3, 4, 5, 12 | ❌ NO | N/A |
| Next steps | "Begin Epic 3 analysis rules" | ❌ NO | N/A |
| User intent fulfilled | User: "do we have architecture plans?" | ❌ NO | N/A |

**Key gap:** Session history, progress tracking, and active state are narrative-only. No structured queryable records.

### What Data Model Already Has (4,060 objects across EVA)

| Layer | Count | 51-ACA Objects | Queryable? | Example |
|---|---|---|---|---|
| **wbs** | 2,988 | **0** | ✅ YES | WBS-48-CONVERSATION-001 (48-eva-veritas stories) |
| **sprints** | 9 | **0** | ✅ YES | 37-data-model-sprint-8 (active sprint with velocity) |
| **milestones** | 4 | **0** | ✅ YES | (empty, schema exists) |
| **decisions** | 4 | **0** | ✅ YES | (empty, schema exists) |
| **risks** | 5 | **0** | ✅ YES | (empty, schema exists) |
| endpoints | 187 | 27 (51-ACA) | ✅ YES | GET /v1/scans -- status: stub/implemented |
| containers | 13 | 11 (51-ACA) | ✅ YES | scans, findings, cost-data |
| screens | 50 | 10 (51-ACA) | ✅ YES | FindingsTier1Page, AdminDashboardPage |
| hooks | 19 | 3 (51-ACA) | ✅ YES | useFindings, useScanStatus |
| agents | 12 | 4 (51-ACA) | ✅ YES | collection-agent, analysis-agent |
| infrastructure | 23 | 10 (51-ACA) | ✅ YES | marco-sandbox-cosmos, marcosandkv20260203 |

**Key finding:** Technical artifacts (endpoints, screens, containers) are fully modeled. Work breakdown (epics, features, stories) is NOT.

---

## WHAT QUERIES WOULD BE POSSIBLE (after enhancements)

### Query 1: All undone stories for Epic 3
**Current:** Search PLAN.md for "Epic 3", manually scan for `Status: DONE`, count undone.
**With data model:**
```powershell
$base = "http://localhost:8055"
Invoke-RestMethod "$base/model/wbs/" |
    Where-Object { $_.project_id -eq "51-ACA" -and $_.parent_wbs_id -like "ACA-03*" -and $_.status -ne "done" } |
    Select-Object id, label, story_points, sprint_id | Format-Table
```
**Output:** `ACA-03-001 | Analysis rule 01: Dev Box | 3 | Sprint-03`
**Note:** `project_id -eq "51-ACA"` filter is MANDATORY (data model contains objects from 37-data-model, 48-eva-veritas, etc.)

### Query 2: Sprint velocity report
**Current:** Manually count DONE stories in PLAN.md, multiply by FP.
**With data model:**
```powershell
$sprint = Invoke-RestMethod "$base/model/sprints/51-ACA-sprint-02"
"Sprint: $($sprint.label)  Velocity: $($sprint.velocity_actual) / $($sprint.velocity_planned)  Stories: $($sprint.stories_completed) / $($sprint.story_count)  MTI at close: $($sprint.mti_at_close)"
"ADO iteration: $($sprint.ado_iteration_path)"
```
**Output:** 
```
Sprint: Sprint 2 -- Core API  Velocity: 21/21  Stories: 5/5  MTI at close: 100
ADO iteration: 51-aca\Sprint 2
```
**Note:** Sprint objects are project-specific (51-ACA sprints separate from eva-poc sprints)

### Query 3: Critical path for Phase 1 go-live
**Current:** Read PLAN.md milestone map, trace dependencies in story "Related:" fields.
**With data model:**
```powershell
Invoke-RestMethod "$base/model/wbs/" |
    Where-Object { $_.project_id -eq "51-ACA" -and $_.milestone -eq $true -and $_.status -ne "done" } |
    Select-Object id, label, target_date, blocking_stories | Format-Table
```
**Output:** `M1.0 | Phase 1 go-live | 2026-03-15 | [ACA-02-018, ACA-03-020]`

### Query 4: All stories blocked by missing Key Vault secret
**Current:** Grep PLAN.md for "Key Vault", manually read each story.
**With data model:**
```powershell
Invoke-RestMethod "$base/model/wbs/" |
    Where-Object { $_.blockers -like "*Key Vault*" } |
    Select-Object id, label, blockers
```
**Output:** `ACA-04-009 | POST /v1/auth/preflight | ["ACA_CLIENT_ID not in Key Vault"]`

### Query 5: Generate sprint manifest (auto-select stories by size/priority)
**Current:** Manual process in sprint-advance.skill.md (Phase 4).
**With data model + new skill:**
```powershell
# Skill: sprint-planner (NEW)
# Trigger: "plan sprint 3" or "select next sprint stories"
node C:\eva-foundry\51-ACA\.github\scripts\plan-sprint.js \
    --project 51-ACA \
    --velocity 21 \
    --priority "GB-02,GB-03,Epic-3" \
    --output .eva/sprint-03-manifest.json
```
**Output:** Auto-selected 7 stories totaling 21 FP, respecting dependencies, blocked stories excluded.

---

## SKILLS ASSESSMENT

### Existing Skills (2)

**1. veritas-expert.skill.md** (302 lines)
- **Triggers**: veritas, mti, trust score, evidence, audit
- **Purpose**: Teaches DPDCA loop for 51-ACA
- **Strengths**: Complete veritas workflow, gap remediation table, evidence receipt format
- **Gaps**: 
  - Does not query data model (reads .eva/trust.json file only)
  - No integration with WBS layer (stories known only via veritas-plan.json)
  - No reporting beyond veritas CLI output

**2. sprint-advance.skill.md** (498 lines)
- **Triggers**: sprint 2, next sprint, advance sprint, close sprint
- **Purpose**: 5-phase sprint close + plan workflow
- **Strengths**: Complete sprint lifecycle, pytest + veritas gates, data model PUT patterns
- **Gaps**:
  - Phase 4 (select stories) is manual (dump undone stories, human picks)
  - No data model sprint object creation
  - No velocity tracking in data model
  - No automated sprint report generation

### Required New Skills (3)

**3. sprint-report.skill.md** (NEW)
- **Triggers**: sprint report, sprint summary, sprint velocity, burndown
- **Purpose**: Generate sprint summary from data model queries
- **Capabilities**:
  - Sprint velocity chart (planned vs actual FP)
  - Story completion table (done/in-progress/blocked)
  - MTI trend (current sprint vs prior 3 sprints)
  - Blocker list with affected stories
  - Test coverage delta (test count at sprint start vs close)
- **Data sources**: WBS layer (story status), sprints layer (velocity), veritas audit (MTI)
- **Output**: Markdown report + JSON artifact for ADO dashboard

**4. gap-report.skill.md** (NEW)
- **Triggers**: gap report, what's missing, blockers, critical path
- **Purpose**: Identify gaps blocking next sprint or milestone
- **Capabilities**:
  - Critical blockers list (stories blocking milestone with status != done)
  - Missing evidence list (stories marked done with no evidence receipt)
  - Orphan tags list (EVA-STORY tags not in veritas-plan.json)
  - Dependency chain (story -> blocking_stories -> transitive closure)
  - Estimate to milestone (sum FP of all undone stories on critical path)
- **Data sources**: WBS layer (blockers field), veritas audit (gaps)
- **Output**: Prioritized gap list with remediation steps

**5. progress-report.skill.md** (NEW)
- **Triggers**: progress report, project status, where are we, epic status
- **Purpose**: Replace STATUS.md as queryable progress snapshot
- **Capabilities**:
  - Epic completion percentages (done stories / total stories per epic)
  - Phase 1 readiness score (all M1.0 milestone stories done?)
  - Recent commits with story IDs (last 10 commits, parsed for ACA-NN-NNN)
  - Test count trend (last 5 values from session records)
  - Open blockers table (all stories with non-empty blockers field)
  - Next 5 recommended stories (undone, no blocking dependencies, sized)
- **Data sources**: WBS layer, git log, veritas reconciliation.json
- **Output**: Single-page HTML dashboard + JSON for API

---

## DATA MODEL ENHANCEMENTS REQUIRED

### Enhancement 1: Extend WBS schema (4 new fields)

**Current WBS schema** (from other projects like 48-eva-veritas):
```json
{
  "id": "ACA-01-001",
  "label": "docker-compose up",
  "level": "story",
  "status": "planned",
  "project_id": "51-ACA",
  "parent_wbs_id": "F-ACA-01-001",
  "sprint_id": "Sprint-02",
  "story_points": 1,
  "ado_id": 2681,
  "owner": "marco.presta",
  "notes": "...",
  "is_active": true
}
```

**Required additions:**
```json
{
  ... existing fields ...
  "acceptance_criteria": "All services start without error",
  "related_stories": ["ACA-01-002", "ACA-01-003"],
  "blockers": [],
  "files_affected": ["services/api/app/main.py", "docker-compose.yml"]
}
```

**Rationale:**
- `acceptance_criteria`: Testable DoD for story (currently only in PLAN.md)
- `related_stories`: Dependencies + related work (enables critical path queries)
- `blockers`: Active blockers (e.g. "ACA_CLIENT_ID not in Key Vault", enables blocker reports)
- `files_affected`: Source files implementing story (complements EVA-STORY tags, enables impact analysis)

**Migration:** Seed script reads PLAN.md, extracts these 4 fields, writes to WBS layer.

### Enhancement 2: Create blockers layer (NEW L31)

**Schema:**
```json
{
  "id": "51-ACA-blocker-001",
  "label": "ACA_CLIENT_ID not provisioned in Key Vault",
  "project_id": "51-ACA",
  "severity": "critical",
  "affected_stories": ["ACA-04-009", "ACA-04-010"],
  "status": "open",
  "opened_date": "2026-02-28",
  "resolved_date": null,
  "resolution": null,
  "owner": "marco.presta",
  "notes": "Blocks all auth stories requiring Entra app registration"
}
```

**Purpose:** Queryable blocker registry with status tracking. Links blockers to affected stories.

**Queries enabled:**
- All open critical blockers
- Stories blocked by X
- Blocker resolution timeline

### Enhancement 3: Seed 51-ACA WBS objects (257 stories)

**Process:**
1. Extend `scripts/seed-from-plan.py` to write WBS layer (currently writes only veritas-plan.json)
2. Parse PLAN.md epic/feature/story hierarchy
3. For each story, extract:
   - id (ACA-NN-NNN)
   - label (story title)
   - status (DONE/ACTIVE/PLANNED from PLAN.md or "planned" default)
   - story_points (parsed from "FP: XS=1" or size map)
   - sprint_id (parsed from "Sprint: Sprint-02" or "Sprint-Backlog" default)
   - acceptance_criteria (lines after "Acceptance:")
   - related_stories (lines after "Related:")
   - files_affected (lines after "Files:")
   - parent_wbs_id (parent feature ID)
4. PUT to data model WBS layer
5. Verify: `GET /model/wbs/ | Where-Object {$_.project_id -eq "51-ACA"} | Measure-Object` returns 257

**One-time cost:** 1 hour to extend seed script + test.

### Enhancement 4: Create sprint objects for 51-ACA

**Objects to create:**
- `51-ACA-sprint-backlog` (status: completed, 61 done stories)
- `51-ACA-sprint-01` (status: completed, Epic 1/2/6 done)
- `51-ACA-sprint-02` (status: completed, 5 API stubs)
- `51-ACA-sprint-03` (status: planned, Epic 3 rules + GB-02/GB-03 fixes)

**Schema** (already exists, just needs objects):
```json
{
  "id": "51-ACA-sprint-02",
  "label": "Sprint 2 -- Core API",
  "project_id": "51-ACA",
  "start_date": "2026-02-26",
  "end_date": "2026-02-27",
  "status": "completed",
  "goal": "5 API endpoint stubs implemented + 24 tests passing",
  "velocity_planned": 21,
  "velocity_actual": 21,
  "story_count": 5,
  "stories_completed": 5,
  "ado_iteration_path": "51-aca\\Sprint 2",
  "mti_at_close": 100,
  "notes": "ACA-04-xxx stubs + timing middleware + parse-agent-log"
}
```

**One-time cost:** 30 min to manually create 4 sprint objects.

---

## RECOMMENDATION

**Priority 1 (Immediate -- enables report skills):** ✅ **COMPLETE (2026-02-28)**
1. ✅ Enhancement 1: Extend WBS schema (4 fields) -- 30 min → DONE (4 fields added: acceptance_criteria, related_stories, blockers, files_affected)
2. ✅ Enhancement 3: Seed 51-ACA WBS objects -- 1 hour → DONE (324 WBS objects: 14 epics + 54 features + 256 stories)
3. ✅ Enhancement 4: Create sprint objects -- 30 min → DONE (4 sprint objects with ado_iteration_path: "51-aca\\Sprint N")

**Seeding verification:**
- Total WBS objects: 324 (all with project_id="51-ACA")
- Story-level objects: 256 (matches PLAN.md)
- ADO sync: 100% (all 256 stories have ADO ID mappings)
- Sprint objects: 4 (sprint-backlog, sprint-01, sprint-02, sprint-03)
- Completion report: [docs/SEEDING-COMPLETE.md](SEEDING-COMPLETE.md)

**Priority 2 (Short-term -- enables automation):**
4. ❌ Create sprint-report.skill.md -- 2 hours
5. ❌ Create gap-report.skill.md -- 2 hours
6. ❌ Create progress-report.skill.md -- 2 hours

**Priority 3 (Medium-term -- full automation):**
7. ❌ Enhancement 2: Create blockers layer -- 1 hour
8. ❌ Integrate skills with sprint-advance workflow -- 1 hour

**Total effort:** Priority 1 DONE (~2 hours actual). Priority 2+3 remaining: ~8 hours.

**Benefit:** PLAN.md becomes a seeding source (edit once, publish to data model). STATUS.md becomes generated artifact (query data model + veritas + git log, write report). Single source of truth shifts from markdown to queryable API.

---

## CRITICAL: ADO PROJECT SEPARATION

**ADO organizational structure:**
- `dev.azure.com/marcopresta/51-aca` -- Independent project, 51-ACA only (257 PBIs)
- `dev.azure.com/marcopresta/eva-poc` -- All other EVA projects (29-foundry, 37-data-model, 48-eva-veritas, etc.)

**Implication for data model:**
- 51-ACA sprint objects MUST use `ado_iteration_path: "51-aca\\Sprint N"` (NOT eva-poc)
- WBS objects for 51-ACA MUST have `project_id: "51-ACA"` (strict isolation)
- Data model supports multi-project, but 51-ACA is managed **independently** from EVA
- Sprint velocity, MTI tracking, and reports are per-project (no cross-project aggregation)

**Current data model state confirms isolation:** ✅ **VERIFIED (2026-02-28)**
```powershell
# 51-ACA sprint objects now seeded with correct ADO iteration paths
GET /model/sprints/ | Where-Object {$_.project_id -eq "51-ACA"} returns 4 objects:
  - 51-ACA-sprint-backlog (ado_iteration_path: 51-aca\Sprint Backlog)
  - 51-ACA-sprint-01 (ado_iteration_path: 51-aca\Sprint 1)
  - 51-ACA-sprint-02 (ado_iteration_path: 51-aca\Sprint 2)
  - 51-ACA-sprint-03 (ado_iteration_path: 51-aca\Sprint 3)

# All 256 stories have project_id="51-ACA" (isolated from eva-poc)
GET /model/wbs/ | Where-Object {$_.project_id -eq "51-ACA"} returns 324 objects
```

**Required sprint objects for 51-ACA:** ✅ **SEEDED**
```json
{
  "id": "51-ACA-sprint-02",
  "label": "Sprint 2 -- Core API",
  "project_id": "51-ACA",
  "ado_iteration_path": "51-aca\\Sprint 2",   // <-- CRITICAL: separate ADO project
  "status": "completed",
  "mti_at_close": 100
}
```

**Product independence reinforced:**
- Phase 1: Data model API shared (marco-eva-data-model endpoint, but 51-ACA objects isolated)
- Phase 2: Standalone data model server (aca-dm-prod, completely independent ADO + data model)

This organizational separation means:
1. `.eva/ado-id-map.json` maps to `51-aca` ADO project (256 PBIs, NOT eva-poc)
2. Veritas audit runs only on 51-ACA repo (no cross-repo dependencies)
3. Sprint reports query ONLY `project_id: "51-ACA"` objects
4. Epic completion % calculated ONLY from 51-ACA WBS objects

**Example workflow after enhancements:**
```powershell
# Instead of reading PLAN.md + STATUS.md
copilot: "generate sprint 3 report"
# Skill queries data model, generates:
# - Sprint velocity chart
# - Epic completion table
# - Blocker list
# - Next 5 recommended stories
# - MTI trend
# Output: docs/sprint-03-report.md (auto-generated, never hand-edited)
```

---

## EXISTING SKILLS THAT BENEFIT

**veritas-expert.skill.md** enhancements after WBS seeding:
- Section 11 "TARGET MTI PLAN" becomes live query: `GET /model/wbs/ + filter by status`
- Section 12 "KNOWN CURRENT STATE" becomes obsolete (replaced by progress-report skill)
- Evidence receipt creation can auto-populate story title from data model instead of manual copy from veritas-plan.json

**sprint-advance.skill.md** enhancements after sprint objects:
- Phase 2.3 "undone story dump" becomes: `GET /model/wbs/ | Where-Object {$_.status -ne "done"}`
- Phase 3.1 "mark done in PLAN.md" becomes: `PUT /model/wbs/{id}` with `status=done`
- Phase 4 "select stories" becomes: invoke sprint-planner skill (auto-selects by FP/priority/dependencies)
- Phase 5 "deliver manifest" reads from data model instead of parsing veritas-plan.json

---

## CONCLUSION

**Yes, the data model can replace PLAN.md/STATUS.md** with 10 hours of work:
- Seed 257 WBS objects (current gap)
- Add 4 fields to WBS schema (acceptance, related, blockers, files)
- Create 4 sprint objects (Sprint-Backlog through Sprint-03)
- Write 3 new skills (sprint-report, gap-report, progress-report)

**Key architectural shift:**
- **Before:** PLAN.md = source of truth (968 lines, manually edited), STATUS.md = narrative snapshot (150 lines, manually updated)
- **After:** Data model = source of truth (257 WBS objects + 4 sprints, HTTP queryable), PLAN.md = seeding source (auto-generated on reseed), STATUS.md = generated report (auto-updated from queries)

**Product independence alignment:**
- **Data model API shared (Phase 1):** `marco-eva-data-model` endpoint shared across EVA projects, BUT 51-ACA objects strictly isolated via `project_id: "51-ACA"` filter on all queries
- **ADO projects separate:** `dev.azure.com/marcopresta/51-aca` (51-ACA only, 257 PBIs) vs `eva-poc` (all other EVA projects)
- **Standalone migration (Phase 2):** `aca-dm-prod` Container App + `aca-cosmos-prod` backend = zero dependency on EVA infrastructure

**Data isolation guarantees:**
- Every WBS query includes `Where-Object {$_.project_id -eq "51-ACA"}` filter
- Sprint objects use `ado_iteration_path: "51-aca\\Sprint N"` (NOT eva-poc)
- Veritas audit runs only on 51-ACA repo (no cross-project gaps)
- Epic completion % calculated only from 51-ACA stories

**Immediate next step (if approved):**
1. Confirm WBS schema extensions with Marco
2. Extend `scripts/seed-from-plan.py` to write WBS layer with project_id isolation
3. Run seed, verify 257 objects with `project_id: "51-ACA"` in data model
4. Create 4 sprint objects with correct ADO iteration paths (51-aca\Sprint N)
5. Create first report skill (sprint-report) as proof-of-concept with project filtering
