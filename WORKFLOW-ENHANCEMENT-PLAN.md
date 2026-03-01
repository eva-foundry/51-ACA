---
# 51-ACA Data Model + Workflow Status
# Generated: 2026-02-28

## Data Model State

### LOCAL SQLite (51-ACA standalone)
- Path: C:\AICOE\eva-foundry\51-ACA\data-model\aca-model.db
- Size: 316 KB
- Objects: 324 WBS stories + 4 sprint metadata records
- Server: FastAPI port 8055 (http://localhost:8055)
- Scope: 51-ACA project ONLY

### Cloud Cosmos (EVA-wide, 37-data-model)
- Endpoint: https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io
- Store: Azure Cosmos DB (marco-eva-cosmos, canadacentral)
- Objects: 4060 total (53 projects, 2988 WBS across all EVA projects)
- **51-ACA record**: NOW FIXED - ado_project = "51-aca" (was "eva-poc")

### ADO Integration
- Project: https://dev.azure.com/marcopresta/51-aca
- Work Items: 256 created (IDs 2940-3196)
- Mapping: 100% coverage via .eva/ado-id-map.json
- Sprint 2 Assignment:
  - LOCAL db: 15 stories linked to Sprint-02 [COMPLETE]
  - ADO: 15 work items (IDs 2978-2993) need iteration path assignment [TODO]

---

## Sprint 2 Configuration

Sprint ID (local): Sprint-02
Sprint Label: Sprint 2 -- Analysis Rules
Status: active
Goal: Epic 3 rules (12 saving opportunity detectors) + GB-02/GB-03 fixes
Start: 2026-02-28
End: 2026-03-10
Velocity: 15 FP planned
ADO Iteration: "51-aca\Sprint 2"

Stories in Sprint 2 (LOCAL db):
- ACA-03-001 (ADO 2978)
- ACA-03-002 (ADO 2979)
- ACA-03-003 (ADO 2980)
- ACA-03-004 (ADO 2981)
- ACA-03-005 (ADO 2982)
- ACA-03-007 (ADO 2984)
- ACA-03-008 (ADO 2985)
- ACA-03-009 (ADO 2986)
- ACA-03-010 (ADO 2987)
- ACA-03-011 (ADO 2988)
- ACA-03-012 (ADO 2989)
- ACA-03-013 (ADO 2990)
- ACA-03-014 (ADO 2991)
- ACA-03-015 (ADO 2992)
- ACA-03-016 (ADO 2993)

---

## GitHub Automation (CURRENT STATE)

### Workflow: .github/workflows/sprint-agent.yml
- Triggers: issue labeled "sprint-task" OR workflow_dispatch
- Model: gpt-4o via GitHub Models API
- Script: .github/scripts/sprint_agent.py (649 lines)
- Process: Parse issue manifest → execute stories D→P→D→C→A → post progress
- Artifacts: sprint-state.json, summary, evidence, test results

### Skill: .github/copilot-skills/sprint-advance.skill.md
- 498 lines
- 5 phases: Discover → Plan → Do → Check → Act
- Phase 5 automation: Create GitHub issue with sprint manifest → auto-trigger workflow → cloud execution

**LIMITATION**: Current workflow is basic single-file script. No integration with:
- LOCAL 51-ACA data model
- ADO work item state sync
- Evidence receipts (Veritas integration)
- Multi-story parallel execution
- Heartbeat/watchdog monitoring

---

## Enhancement Targets (Main Track)

### Target 1: Align 51-ACA workflow with 38-ado-poc sprint-execute pattern
**Reference**: 38-ado-poc/.github/workflows/sprint-execute.yml (550 lines)

Current 51-ACA:
- Single sprint_agent.py script (649 lines)
- No ADO sync
- No evidence artifacts
- No heartbeat monitoring

Target 38-ado-poc pattern:
- Full DPDCA loop with phase transitions
- ADO WI state sync (New → Active → Done)
- Evidence upload to artifacts
- 15-min heartbeat updates
- Parallel story execution support
- PR auto-creation with AB#N tags

**Action**: Refactor .github/workflows/sprint-agent.yml to match sprint-execute.yml structure

### Target 2: Integrate LOCAL data model into workflow
- Read sprint metadata from LOCAL db (port 8055)
- Update story status after each phase
- Write evidence receipts to .eva/evidence/
- Close the write-verify cycle with commit

**Action**: Add db.py integration to sprint_agent.py

### Target 3: Add Veritas integration
- Write evidence receipts after each story
- Calculate MTI score after sprint
- Block merge if MTI < 30

**Action**: Add veritas audit step to workflow

### Target 4: Add ADO bidirectional sync
- On sprint start: read ADO WI states → set LOCAL db status
- During execution: update ADO WI comments with phase progress
- On story done: mark ADO WI as Done
- On sprint complete: post summary comment to ADO Feature

**Action**: Add ADO REST API calls to workflow

### Target 5: Multi-story parallel execution
- Parse sprint manifest → group by dependency
- Execute independent stories in parallel
- Aggregate evidence + test results
- Report per-story + sprint-level metrics

**Action**: Refactor sprint_agent.py to support parallel execution

---

## Immediate Action Items

1. Fix: Run update-ado-sprint2.ps1 to complete Sprint 2 ADO assignment
2. Enhance: Upgrade sprint-agent.yml to match 38-ado-poc/sprint-execute.yml pattern  
3. Integrate: Connect workflow to LOCAL data model (port 8055)
4. Add: Veritas evidence receipt generation
5. Add: ADO bidirectional sync (WI state + comments)
6. Test: Execute Sprint 2 with enhanced workflow

---

## References

- 38-ado-poc sprint execution: .github/workflows/sprint-execute.yml (550 lines)
- 29-foundry GitHub plane skills: copilot-skills/github-plane/01-sprint-execute.skill.md
- LOCAL db API: http://localhost:8055/model/agent-guide
- Cloud Cosmos API: https://marco-eva-data-model.../model/agent-guide
- Veritas CLI: C:\AICOE\eva-foundry\48-eva-veritas\src\cli.js
- ADO REST API: https://dev.azure.com/marcopresta/_apis/
