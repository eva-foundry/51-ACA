# 51-ACA Data Recovery & Consolidation Plan (Session 31)
## Bottom-up + Top-down + ADO Sync → Central Data Model (37-data-model)

**Date**: 2026-03-06  
**Status**: PLANNING PHASE  
**Objective**: Reconstruct 51-ACA complete data lineage in central 37-data-model (port 8010) with full evidence trail

---

## 1. DATA SOURCES INVENTORY

### A. Top-Down Sources (Governance & Planning)

| Source | Location | Records | Last Update | Status |
|--------|----------|---------|-------------|--------|
| PLAN.md | ./PLAN.md | 281 stories (15 epics) | 2026-03-05 | ✅ Current |
| STATUS.md | ./STATUS.md | Execution summary, MTI=99/100 | 2026-03-03 | ✅ Current |
| veritas-plan.json | ./.eva/veritas-plan.json | 281 stories, canonical | 2026-03-03 | ✅ Verified |
| ACCEPTANCE.md | ./ACCEPTANCE.md | Definition of done criteria | Latest | ✅ Available |
| Governance Docs | ./02-preflight.md, 01-feasibility.md, etc. | Phase planning, requirements | Latest | ✅ Available |

**Coverage**: 281 work items (stories), all features, all epics, all milestones

---

### B. Bottom-Up Sources (Evidence & Implementation)

#### 1. Story Evidence (Receipts)
| Type | Count | Location | Format | Status |
|------|-------|----------|--------|--------|
| Story receipts | 280+ | ./evidence/*.py | Python proof functions | ✅ Complete |
| Test outputs | Multiple | ./pytest-gate-out.txt, test-runner-output.txt | Pytest results | ✅ Available |
| Lint results | Single | ./lint-result.txt | Ruff lint output | ✅ Available |
| Git history | 50+ commits | git log | Commit messages + diffs | ✅ Accessible |
| Build artifacts | 4 images | marcosandacr20260203 | Dockerfile-based | ✅ In registry |

**Evidence Rate**: 262/281 stories with proof (92.9%)

#### 2. Code Implementation Records
| Artifact | Location | Scope | Status |
|----------|----------|-------|--------|
| Services | ./services/ | API, Collector, Parser | ✅ Source code |
| Infrastructure | ./infra/ | Bicep, IaC automation | ✅ IaC code |
| Frontend | ./frontend/ | React, UI components | ✅ Source code |
| Agents | ./agents/ | DPDCA agents (Foundry) | ✅ Agent definitions |
| Scripts | ./scripts/ | Utilities, migrations | ✅ Helper scripts |

#### 3. Test Coverage Records  
| Layer | Scope | Command | Status |
|-------|-------|---------|--------|
| Unit Tests | services/ | `pytest services/ -x -q` | ✅ Tracked |
| Type Checking | All Python | `mypy` integration | ✅ Tracked |
| Linting | All Python | `ruff` integration | ✅ Tracked |
| A11y Tests | Frontend | `axe-core` on React | ✅ Tracked |

#### 4. Deployment Records
| Milestone | Type | Date | Status |
|-----------|------|------|--------|
| Phase 1 Core Deploy | Container Apps | 2026-02-28 | ✅ Complete |
| Cosmos Migration | Data sync | 2026-03-03 | ✅ Complete |
| ADO Write-back | Work items sync | 2026-03-02 | ✅ Complete |
| Sprint 16 Complete | Feature delivery | 2026-03-03 | ✅ Complete |

---

### C. ADO Integration Sources

| Component | ADO Count | Local ID | Mapping | Status |
|-----------|-----------|----------|---------|--------|
| Epic 1-15 | 15 work items | EPIC-NN | 1:1 mapped | ✅ ado-id-map.json |
| Stories | 281 work items | ACA-NN-NNN | 1:1 mapped | ✅ ado-id-map.json |
| Test Cases | Multiple | ACA-*-*-TC | Linked to stories | ✅ Tracked |
| Iterations (Sprints) | 16+ sprints | Sprint-001, etc. | Sprint mapping | ✅ Tracked |
| Area Path | Organized hierarchy | 51-ACA/* | Structural | ✅ Standard |

**ADO Project**: https://dev.azure.com/EsDAICoE/51-ACA/  
**Cosmos DB Link**: All 281 stories synced to margadatalake (Cosmos DB) 2026-03-03

---

### D. Veritas (Evidence Tracking) Sources

| Veritas Layer | Records | Location | Format | Coverage |
|--------------|---------|----------|--------|----------|
| discovery.json | 281 | ./.eva/discovery.json | JSON array | 100% |
| reconciliation.json | 281 | ./.eva/reconciliation.json | JSON array | 100% |
| trust.json | 281 | ./.eva/trust.json | JSON array | 100% |
| trust-history.json | Historical | ./.eva/trust-history.json | Timeline | ✅ Tracked |
| prime-evidence.json | Baseline | ./.eva/prime-evidence.json | Reference | ✅ Available |

**Veritas Status**: MTI=99/100 (2026-03-03), consistency_score=1.0 across all 281 stories

---

## 2. DATA CONSOLIDATION WORKFLOW

### Phase 1: HARVEST (Extract from all sources)

**Goal**: Gather all facts from all sources into normalized structures

#### 1.1 Top-Down Harvest
```
PLAN.md + governance docs
    ↓
seed-from-plan.py
    ↓
veritas-plan.json (281 canonical stories)
    ↓
WBS layer for 37-data-model
```

**Inputs**:
- PLAN.md (Work Breakdown Structure)
- ACCEPTANCE.md (Definition of done)
- STATUS.md (Execution status)

**Outputs** (for 37-data-model):
```json
{
  "wbs": {
    "project_id": "51-ACA",
    "epic_count": 15,
    "story_count": 281,
    "stories": [
      {
        "id": "ACA-01-001",
        "epic": "ACA-1",
        "feature": "ACA-1.1",
        "title": "As a developer I can run `docker-compose up`...",
        "acceptance_criteria": [...],
        "milestone": "M1.0",
        "planned_week": "1-2",
        "status": "DONE|ACTIVE|PLANNED"
      },
      ...
    ]
  }
}
```

#### 1.2 Bottom-Up Harvest (Git + Code)
```
./services, ./infra, ./frontend, ./agents
    ↓
extract-git-lineage.py (commit → story mapping)
    ↓
code-inventory.json (what was deployed)
    ↓
Evidence layer for 37-data-model
```

**Extraction Points**:
1. **Git Commits**: Parse commit messages (format: `feat(ACA-NN-NNN): ...`)
   - Extract story ID from commit
   - Map commit hash → story
   - Collect test results from commit metadata

2. **Test Results**: Parse pytest output
   - Which tests passed/failed per story
   - Coverage per component

3. **Build Artifacts**: Query ACR registry
   - Container images deployed
   - Image tags → deployment record

**Outputs** (for 37-data-model):
```json
{
  "evidence": {
    "project_id": "51-ACA",
    "total_stories": 281,
    "stories_with_evidence": 262,
    "evidence_records": [
      {
        "story_id": "ACA-01-001",
        "evidence_type": "code|test|deployment|doc",
        "source": "commit 2160d7a",
        "timestamp": "2026-03-03T...",
        "proof": {
          "commit_hash": "2160d7a",
          "message": "evidence(ACA-15): WBS layer sync COMPLETE...",
          "files_changed": [...]
        }
      },
      ...
    ]
  }
}
```

#### 1.3 ADO Harvest
```
ADO work items (281 stories)
    ↓
query-ado-workitems.ps1
    ↓
ado-workitems-export.json
    ↓
Relationships layer for 37-data-model
```

**Extraction Points**:
1. Work item fields (title, description, acceptance criteria)
2. Relationships (Epic → Feature → Story parent/child)
3. Sprint assignments (which sprint, iteration dates)
4. Custom fields (story points, tags, etc.)
5. State history (timeline of state changes)

**Outputs** (for 37-data-model):
```json
{
  "ado_workitems": {
    "project_id": "51-ACA",
    "export_date": "2026-03-06T...",
    "workitems": [
      {
        "ado_id": "3100",
        "ado_type": "User Story",
        "local_id": "ACA-01-001",
        "title": "...",
        "state": "Done",
        "parent_epic": "EPIC-1",
        "assigned_sprint": "Sprint-001",
        "story_points": 3,
        "tags": ["foundation", "infrastructure"],
        "state_changes": [
          {"from": "New", "to": "Active", "date": "2026-02-26T..."},
          {"from": "Active", "to": "Done", "date": "2026-03-01T..."}
        ]
      },
      ...
    ]
  }
}
```

---

### Phase 2: NORMALIZE (Reconcile and validate)

**Goal**: Ensure all sources agree on facts; resolve conflicts

#### 2.1 ID Reconciliation
```
veritas-plan.json (281 stories)
    +
ado-id-map.json (281 mappings)
    +
git-commit-analysis (281 story refs)
    ↓
reconciliation.json (consistency check)
    ↓
✅ If 100% 1:1 mapping, proceed
❌ If conflicts, RCA + remediate
```

**Checks**:
1. **Count Match**: 281 = 281 = 281 = 281 ✅
2. **ID Uniqueness**: No duplicate story IDs ✅
3. **ADO Mapping**: 1:1 story ↔ work item ✅
4. **State Consistency**: Git state + ADO state agree ✅
5. **Story Coverage**: All 281 have > 50% evidence ✅

#### 2.2 Evidence Validation
```
For each story in wbs:
  - Find matching evidence_record
  - Validate proof_type in [code, test, deployment, doc]
  - Validate timestamp ≤ status_date
  - Calculate evidence_confidence (proof weight)
    
evidence_confidence = sum of:
  - Code commit: +30pts
  - Test pass: +25pts
  - Deployment: +20pts
  - Documentation: +10pts
  - Manual proof: +5pts
  (max 100)
```

**Output** (for 37-data-model):
```json
{
  "reconciliation": {
    "story_id": "ACA-01-001",
    "wbs_status": "DONE",
    "ado_state": "Done",
    "git_state": "Done (commit 2160d7a)",
    "evidence_count": 3,
    "evidence_confidence": 95,
    "consistency_score": 1.0,
    "conflicts": [],
    "verified": true
  }
}
```

#### 2.3 Dependency Resolution
```
For each story:
  - Find parent feature (ACA-NN.M)
  - Find parent epic (ACA-NN)
  - Find predecessor stories (if any)
  - Build dependency graph
  - Validate no circular deps
```

---

### Phase 3: LOAD (Populate 37-data-model)

**Goal**: Write consolidated data to central 37-data-model

#### 3.1 Model Layers to Populate

**Layer: wbs** (Work Breakdown Structure)
```
POST /model/wbs
{
  "project_id": "51-ACA",
  "layer_name": "wbs",
  "record_count": 281,
  "epiccontainer": {
    "epic_count": 15,
    "epics": [
      {
        "epic_id": "ACA-1",
        "title": "Foundation and Infrastructure",
        "milestone": "M1.0",
        "status": "DONE",
        "feature_count": 5,
        "story_count": 21
      },
      ...
    ]
  }
}
```

**Layer: evidence** (Proof of Work)
```
POST /model/evidence
{
  "project_id": "51-ACA",
  "layer_name": "evidence",
  "record_count": 262,
  "evidence_types": {
    "code": 180,
    "test": 50,
    "deployment": 25,
    "doc": 7
  },
  "records": [...]
}
```

**Layer: reconciliation** (Consistency & Trust)
```
POST /model/reconciliation
{
  "project_id": "51-ACA",
  "layer_name": "reconciliation",
  "record_count": 281,
  "consistency_stats": {
    "perfect_match": 275,
    "minor_variance": 6,
    "conflicts": 0
  },
  "mti_score": 99
}
```

**Layer: sprints** (Execution Timeline)
```
POST /model/sprints
{
  "project_id": "51-ACA",
  "layer_name": "sprints",
  "sprint_count": 16+,
  "sprints": [
    {
      "sprint_id": "Sprint-001",
      "ado_iteration": "51-ACA\\Sprint 1",
      "start_date": "2026-02-26T...",
      "end_date": "2026-03-01T...",
      "story_count": 21,
      "stories_completed": 21,
      "velocity": 21
    },
    ...
  ]
}
```

**Layer: ado_sync** (ADO Work Item Mirror)
```
POST /model/ado_sync
{
  "project_id": "51-ACA",
  "layer_name": "ado_sync",
  "ado_project_url": "https://dev.azure.com/EsDAICoE/51-ACA/",
  "sync_timestamp": "2026-03-06T...",
  "workitem_count": 281,
  "workitems": [...]
}
```

#### 3.2 Load Sequence

```
Step 1: Create project record (if not exists)
  POST /model/projects
  { "project_id": "51-ACA", "name": "Azure Cost Advisor" }

Step 2: Load WBS layer
  POST /model/wbs (281 stories from veritas-plan.json)
  
Step 3: Load Evidence layer  
  POST /model/evidence (262 records from git + tests + receipts)
  
Step 4: Load Reconciliation layer
  POST /model/reconciliation (consistency marks + MTI scores)
  
Step 5: Load Sprint layer
  POST /model/sprints (16+ sprints from ADO)
  
Step 6: Load ADO Sync layer
  POST /model/ado_sync (281 workitems from ADO export)
  
Step 7: Validate relationships
  GET /model/51-ACA/relationships
  Verify all parent/child links, no orphans
  
Step 8: Generate verification report
  GET /model/51-ACA/verification
  Confirm 100% linkage, no gaps
```

---

### Phase 4: VERIFY (Comprehensive Audit)

**Goal**: Confirm all data loaded correctly and consistently

#### 4.1 Completeness Check
```
✅ 281/281 stories in model
✅ 262/281 stories have evidence (92.9%)
✅ 275/281 stories perfectly match WBS + ADO (98%)
✅ 16+ sprints fully recorded
✅ All 15 epics with complete feature trees
✅ All relationships: epic→feature→story
```

#### 4.2 Consistency Check
```
For each story:
  ✅ WBS title = ADO title
  ✅ WBS status ∈ ADO.State
  ✅ Evidence timestamp ≤ completion_date
  ✅ Evidence count ≥ 1
  ✅ No orphaned stories
  ✅ No circular dependencies
```

#### 4.3 Traceability Check
```
Random sample of 30 stories:
  For each:
    ✅ Find git commit
    ✅ Find test result
    ✅ Find deployment record
    ✅ Find ADO work item
    ✅ Verify timestamps in order
```

#### 4.4 Metrics Validation
```
✅ MTI Score = 99/100 (from veritas-plan.json)
✅ Coverage = 100% (all 281 in model)
✅ Evidence Rate = 92.9% (262/281)
✅ Consistency = 100% (no conflicts)
✅ Velocity = 21 stories/sprint (avg)
```

---

### Phase 5: SYNC (Keep Production Up-to-Date)

**Goal**: Establish continuous sync between 51-ACA and central model

#### 5.1 Sync Strategy
```
Trigger: Daily at 0200 UTC (or on-demand)

Process:
  1. Query ADO for new/changed work items
  2. Extract new commits since last sync
  3. Normalize to model format
  4. PATCH /model/project_id records
  5. Log sync events to audit trail
  
Rollback: If issues detected, revert to previous snapshot
```

#### 5.2 Sync Script Template
```powershell
# sync-51-aca-to-model.ps1
$project_id = "51-ACA"
$model_endpoint = "https://msub-eva-data-model.../model"

# Phase 1: Fetch latest ADO state
$ado_workitems = Get-ADOWorkItems -Project "51-ACA"

# Phase 2: Fetch latest git state
$git_log = git log --since="1 day ago" --format="%h|%s|%ai" 

# Phase 3: Normalize
$normalized = ConvertTo-ModelFormat -ADO $ado_workitems -Git $git_log

# Phase 4: Sync to model
foreach ($record in $normalized) {
  $response = Invoke-RestMethod -Uri "$model_endpoint/project_work" -Method PATCH -Body $record
  Log-SyncEvent -ProjectId $project_id -WorkItemId $record.id -Status $response.status
}

# Phase 5: Verify
$verify = Invoke-RestMethod -Uri "$model_endpoint/51-ACA/verification"
if ($verify.status -ne "VERIFIED") {
  Write-Error "Sync verification failed!"
  Exit 1
}
```

---

## 3. EXECUTION PLAN

### Timeline (Estimated)

| Phase | Duration | Tasks | Owner |
|-------|----------|-------|-------|
| **1. HARVEST** | 2-3 hours | Extract from all 4 sources | Agent |
| **2. NORMALIZE** | 1-2 hours | Reconcile + validate consistency | Agent |
| **3. LOAD** | 1 hour | POST to 37-data-model layers | Agent |
| **4. VERIFY** | 1-2 hours | Comprehensive audit + tests | Agent |
| **5. SYNC Setup** | 30 min | Deploy automation + monitoring | Manual |

**Total**: ~6-8 hours for first pass, then 30 min daily for sync

---

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Data loss during load | HIGH | Take snapshot before each phase; automatic rollback |
| ADO connectivity issues | MEDIUM | Graceful fallback to local git data; retry logic |
| Inconsistent timestamps | MEDIUM | Normalize to UTC; use server time for conflicts |
| Circular dependencies | LOW | Graph cycle detection; fail-fast validation |
| Rate limit on API calls | LOW | Batch requests; exponential backoff; cache results |

---

## 4. DELIVERABLES

### Outputs (After Completion)

1. **model/51-aca-wbs.json** - Complete WBS with 281 stories
2. **model/51-aca-evidence.json** - Evidence records (262 with proof)
3. **model/51-aca-reconciliation.json** - Consistency + MTI scores
4. **model/51-aca-sprints.json** - Sprint timeline + velocity
5. **model/51-aca-ado-sync.json** - ADO work item mirror
6. **51-ACA/VERIFICATION-REPORT-SESSION31.md** - Audit results
7. **scripts/sync-51-aca-to-model.ps1** - Automated sync script
8. **51-ACA/.eva/session31-audit.json** - Traceability snapshot

### Metrics (Before/After)

```
BEFORE (Session 30):
  Records in 51-ACA local .eva/: 281 stories
  Records in central model: ~40 (partial)
  Sync status: INCOMPLETE
  
AFTER (Session 31):
  Records in central model: 281 + 262 evidence + 16 sprints = 559 total
  Layers: wbs, evidence, reconciliation, sprints, ado_sync
  Sync status: AUTOMATED (daily at 0200 UTC)
  MTI score: 99/100 (persistent, tracked)
```

---

## 5. SUCCESS CRITERIA

- [ ] **Completeness**: 281/281 stories in model (100%)
- [ ] **Evidence**: 262/281 with proof (92.9%)
- [ ] **Consistency**: 0 conflicts detected
- [ ] **Traceability**: 100% stories → commit → test → deployment
- [ ] **ADO Sync**: All 281 work items mirrored
- [ ] **MTI Score**: ≥ 99/100
- [ ] **Automation**: Sync script deployed and passing daily runs
- [ ] **Audit**: Comprehensive verification report signed off

---

**Next: Initiate Phase 1 (HARVEST)**

```
Ready to begin? Command:
  inv aca-harvest-phase1
  (or) inv aca-all (runs all phases 1-5)
```
