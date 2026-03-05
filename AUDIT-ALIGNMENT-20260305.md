# 51-ACA Governance Alignment Audit
**Date**: 2026-03-05  
**Scope**: README, PLAN, STATUS ↔ Central Data Model (port 8010) ↔ Azure DevOps  
**Status**: FINDINGS DOCUMENTED

---

## Executive Summary

Three critical misalignments identified between 51-ACA governance files and the central data model:

1. **Project Not Registered** -- 51-ACA does not exist as a project record in the central 37-data-model
2. **Governance Documents Outdated** -- README/PLAN/STATUS reference deprecated local data model (port 8055)
3. **ADO Data Stale** -- ado-artifacts.json contains no work items; no sync with current sprint state

### Audit Findings

| Item | Source | Issue | Severity |
|------|--------|-------|----------|
| **Project Record** | Central Data Model | Not in `GET /model/projects/` list | 🔴 CRITICAL |
| **Data Model Endpoint** | README / PLAN / STATUS | Still reference old port 8055 | 🟠 HIGH |
| **ADO Artifacts** | ado-artifacts.json | Zero work items (stale) | 🟠 HIGH |
| **Version Dates** | README/PLAN/STATUS headers | Last updated 2026-03-02 (3 days old) | 🟠 MEDIUM |
| **Sprint State** | STATUS.md | Sprint-003 PENDING (never started) | 🟡 MEDIUM |

---

## Finding #1: Project Not Registered in Central Data Model

### Current State
```
Central data model (port 8010) has 50 registered projects
Project list includes: 01-documentation-generator, 02-poc-agent-skills, ..., 48-eva-veritas
Project NOT found: 51-ACA
```

### Expected State
```
51-ACA should have a project record with:
  id: "51-ACA"
  name: "ACA -- Azure Cost Advisor"
  phase: "Phase 1 -- Core Services Bootstrap"
  maturity: "active"
  story_count: 281
  mti_score: 99
  stack: "Python 3.12 / FastAPI / React 19 / Stripe / Cosmos"
```

### Root Cause
The project's local data model (port 8055) is independent. The seed-from-plan.py script populates the local SQLite 
but does not push to the central model store. Central model is not aware of 51-ACA existence.

### Impact
- Agents cannot validate cross-project dependencies via the central model
- 51-ACA not visible in workspace dashboards  
- Impact analysis (GET /model/impact/?...) cannot include 51-ACA  
- No unified project health scorecard

---

## Finding #2: Governance Documents Still Reference Port 8055

### Current State (README.md)
```markdown
| 37-data-model | Single source of truth for all project entities | GET http://localhost:8010/model/projects/51-ACA |

But then references local model setup:
  `$base = "http://localhost:8010"`  (correct in newer section)
  But earlier sections still reference legacy 8055 model server
```

### Expected State
All README, PLAN, STATUS should:
1. Acknowledge centralized data model on port 8010 as single source of truth
2. Document project-specific data model relationship (51-ACA is consumer, not owner)
3. Remove all references to deprecated local 8055 server
4. Update bootstrap instructions to point to project 37

### Completed
✅ copilot-instructions.md -- UPDATED 2026-03-05 (local session)
  
### TODO
- [ ] README.md -- update header block (Section "EVA Ecosystem Integration")
- [ ] PLAN.md -- update bootstrap reference (section "EVA Ecosystem Tools")
- [ ] STATUS.md -- if any 8055 references exist

---

## Finding #3: ADO Artifacts Stale (No Work Items)

### Current State
```
ado-artifacts.json exists but contains:
  - workItems: [] (empty)
  - iterations: [] (empty)
  - areas: [] (empty)
```

### Expected State
ADO should have:
```
Epic: 51-aca (1x)
Features: 15 (ACA-01 through ACA-15)
PBIs/Stories: 281+ mapped from PLAN.md
Sprints: Sprint-000 through Sprint-003 defined
```

### Root Cause
ADO artifacts were exported but never imported to dev.azure.com/marcopresta/51-aca project.
Script exists (ado-import.ps1) but has not been run against the ADO project.

### Impact
- No ADO integration for sprints, work assignment, burndown tracking
- GitHub commits cannot auto-link to ADO work items
- CI/CD cannot gate deployments on ADO release readiness
- No unified ADO ↔ GitHub sync

---

## Alignment Roadmap

### Phase 1: Register Project in Central Model (IMMEDIATE)

**Action 1.1** -- Create project record in central model
```powershell
$base = "http://localhost:8010"
$ep = @{
  "id" = "51-ACA"
  "name" = "ACA -- Azure Cost Advisor"
  "folder" = "51-ACA"
  "phase" = "Phase 1 -- Core Services Bootstrap"
  "maturity" = "active"
  "mti_score" = 99
  "story_count" = 281
  "stack" = "Python 3.12 / FastAPI / React 19 / Stripe / Cosmos"
  "owner" = "Marco Presta"
  "notes" = "Commercial SaaS. Phase 1 multi-agent orchestration pipeline complete."
}
$body = $ep | ConvertTo-Json -Depth 10
Invoke-RestMethod "$base/model/projects/51-ACA" `
  -Method PUT `
  -ContentType "application/json" `
  -Body $body `
  -Headers @{"X-Actor" = "agent:copilot"}
```

**Action 1.2** -- Verify project now discoverable
```powershell
Invoke-RestMethod "$base/model/projects/51-ACA"
# Should return 200 OK with project record
```

### Phase 2: Update Governance Documents (THIS SESSION)

**Action 2.1** -- Update README.md
- [ ] Remove deprecated port 8055 references in "EVA Ecosystem Integration" section
- [ ] Clarify that central 37-data-model on port 8010 is source of truth for project metadata
- [ ] Add note: "Local data models (51-ACA/data-model) are DEPRECATED as of 2026-03-05"

**Action 2.2** -- Update PLAN.md
- [ ] Update "EVA Ecosystem Tools" section to point to port 8010 exclusively
- [ ] Remove any local 8055 bootstrap instructions

**Action 2.3** -- Update STATUS.md
- [ ] If any port 8055 references exist, update to 8010
- [ ] Update version timestamp to reflect today's alignment fix

### Phase 3: Sync ADO (H-2 HOURS)

**Action 3.1** -- Run ADO import
```powershell
$env:ADO_PAT = "<pat>"
.\ado-import.ps1
# Creates 1 epic, 15 features, 281 stories in dev.azure.com/marcopresta/51-aca
```

**Action 3.2** -- Verify ADO sync
```powershell
.\check-ado-sprint2.ps1
# Should show: ado_project=51-aca, features=15, stories=281, sprints=active
```

**Action 3.3** -- Commit alignment proof
```powershell
git add AUDIT-ALIGNMENT-20260305.md
git commit -m "docs: governance alignment audit -- port 8010, project registered"
```

---

## Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Project registered | `GET http://localhost:8010/model/projects/51-ACA` returns 200 |
| Docs updated | README/PLAN/STATUS have no 8055 references |
| ADO synced | ado-artifacts.json has >280 work items |
| Version current | README/PLAN/STATUS headers show 2026-03-05 |
| Commit proof | AUDIT-ALIGNMENT-20260305.md in tree with alignment markers |

---

## Related Files

- `.github/copilot-instructions.md` -- ✅ UPDATED (removed 8055 bootstrap)
- `README.md` -- TODO
- `PLAN.md` -- TODO
- `STATUS.md` -- TODO (if needed)
- `ado-artifacts.json` -- TODO (re-export from ADO after sync)
- `ado-import.ps1` -- READY (no changes needed)

---

## References

- **Project 37 API Docs**: `http://localhost:8010/model/agent-guide`
- **ADO Integration**: `C:\AICOE\eva-foundry\38-ado-poc\scripts\ado-import-project.ps1`
- **Governance Template**: `C:\AICOE\eva-foundry\07-foundation-layer\.github\copilot-skills\`

---

**Next Session**: Complete Actions 2.1-2.3, execute Phase 3 ADO sync, update this audit with CURRENT timestamps.
