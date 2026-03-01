# Sprint 2 Execution Plan - DPDCA Cycle
# Generated: 2026-02-28
# Project: 51-ACA (Azure Cost Advisor)

---

## DISCOVER - Current State Assessment

### ✅ LOCAL SQLite Database
- Path: C:\AICOE\eva-foundry\51-ACA\data-model\aca-model.db
- Sprint-02 linkage: 15 stories (ACA-03-001 through ACA-03-016, skipping done 006)
- ADO mapping: Work items 2978-2993
- Status: READY

### ✅ Cloud Cosmos Model
- Endpoint: https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io
- 51-ACA project record: ado_project = "51-aca" (corrected from "eva-poc")
- Status: READY

### ✅ ADO Sync Script
- File: update-ado-sprint2.ps1 (50 lines)
- Commands: 15 az board work-item update calls
- Iteration path: "51-aca\Sprint 2"
- Status: READY TO RUN

### ✅ GitHub Workflow
- File: .github/workflows/sprint-agent.yml (91 lines)
- Trigger: issue labeled "sprint-task" OR workflow_dispatch
- Model: gpt-4o via GitHub Models
- Script: .github/scripts/sprint_agent.py (649 lines)
- Status: READY

### ⚠️ ADO Work Items
- 15 work items exist (IDs 2978-2993)
- Iteration path: NOT YET SET
- Sprint 2 board: EMPTY (needs sync)
- Status: AWAITING SYNC

---

## PLAN - Execution Sequence

### Phase 1: ADO Synchronization (30 min)
**Goal**: Assign 15 work items to "51-aca\Sprint 2" iteration

1. Run update-ado-sprint2.ps1
   - Executes 15 az CLI commands
   - Sets iteration path for each work item
   - Expected: 15 successful updates

2. Verify ADO Sprint 2 board
   - Navigate to https://dev.azure.com/marcopresta/51-aca/_sprints
   - Confirm Sprint 2 shows 15 work items
   - Check work item states (should be "New")

3. Confirm sync
   - Query sample work items (2978, 2985, 2993)
   - Verify iteration path = "51-aca\Sprint 2"
   - Document any failures

### Phase 2: Sprint Execution Readiness (15 min)
**Goal**: Validate all systems ready for Sprint 2 execution

1. Test harness check
   - Run: pytest services/ -x -q --tb=short
   - Expected: All baseline tests pass
   - Record test count

2. Veritas baseline
   - Run: node veritas/cli.js audit --repo . --warn-only
   - Expected: MTI >= 30
   - Document gap count

3. Data model health
   - Query: http://localhost:8055/model/sprints/51-ACA-sprint-02
   - Verify sprint metadata is correct
   - Check story_count = 15

### Phase 3: Sprint Execution Trigger (Manual)
**Goal**: Launch Sprint 2 via GitHub workflow

Option A - Via GitHub Issue:
1. Create issue with sprint manifest
2. Add label "sprint-task"
3. Workflow auto-triggers

Option B - Via workflow_dispatch:
1. Navigate to Actions → Sprint Agent
2. Click "Run workflow"
3. Input issue_number (if using existing issue)

### Phase 4: Monitor Execution (Duration: varies)
**Goal**: Track sprint progress

1. Watch GitHub Actions run
   - URL: https://github.com/eva-foundry/51-ACA/actions
   - Monitor: sprint-agent workflow
   - Check: Progress comments on issue

2. Monitor artifacts
   - sprint-state.json (incremental state)
   - sprint-summary.md (final report)
   - .eva/evidence/ (story receipts)
   - lint-result.txt, test-collect.txt

3. Check ADO work item updates (manual)
   - States should transition: New → Active → Done
   - Comments should appear from Sprint Agent

---

## DO - Execution Checklist

### Task 1: Run ADO Sync [NEXT]
```powershell
cd C:\AICOE\eva-foundry\51-ACA
pwsh -NoProfile -File update-ado-sprint2.ps1 2>&1 | Tee-Object ado-sync-result.txt
Write-Host "[DONE] ADO sync complete - check ado-sync-result.txt"
```

### Task 2: Verify ADO Board [AFTER TASK 1]
- Open: https://dev.azure.com/marcopresta/51-aca/_sprints/taskboard/51-aca/51-aca/Sprint%202
- Expected: 15 work items visible in Sprint 2
- If empty: review ado-sync-result.txt for errors

### Task 3: Run Baseline Tests [AFTER TASK 2]
```powershell
cd C:\AICOE\eva-foundry\51-ACA
C:\AICOE\.venv\Scripts\python.exe -m pytest services/ -x -q --tb=short 2>&1 | 
    Tee-Object baseline-tests.txt
Write-Host "[DONE] Baseline tests complete"
```

### Task 4: Trigger Sprint 2 [AFTER TASK 3]
Choice: Create GitHub issue with sprint manifest OR run workflow_dispatch

---

## CHECK - Validation Gates

### Gate 1: ADO Sync Success
- [ ] All 15 commands executed without error
- [ ] ADO Sprint 2 board shows 15 work items
- [ ] Sample query confirms iteration path set
- [ ] No "failed" items in ado-sync-result.txt

### Gate 2: Test Baseline Pass
- [ ] pytest exits 0
- [ ] Test count >= last known baseline
- [ ] No new failures introduced
- [ ] baseline-tests.txt has [PASS] marker

### Gate 3: Data Model Consistency
- [ ] LOCAL db: 15 stories with sprint_id="Sprint-02"
- [ ] Cloud Cosmos: 51-ACA.ado_project = "51-aca"
- [ ] ADO: 15 work items in Sprint 2 iteration
- [ ] All three systems agree on story list

### Gate 4: Workflow Health
- [ ] sprint-agent.yml syntax is valid
- [ ] sprint_agent.py has no import errors
- [ ] GitHub Actions shows no prior failures
- [ ] GITHUB_TOKEN permissions are sufficient

---

## ACT - Close the Cycle

### Actions on Success
1. Update STATUS.md
   - Record Sprint 2 start date: 2026-02-28
   - Document test count baseline
   - Note MTI score
   - List 15 story IDs in sprint

2. Create sprint execution issue (if using Option A)
   - Template: .github/SPRINT_ISSUE_TEMPLATE.md
   - Body: Sprint manifest with all 15 stories
   - Label: "sprint-task"

3. Monitor and document
   - Watch GitHub Actions run
   - Collect artifacts after completion
   - Review sprint-summary.md
   - Extract lessons learned

### Actions on Failure
1. Identify failure point
   - ADO sync failed? Check az CLI authentication
   - Tests failed? Fix failing tests before sprint execution
   - Data model inconsistent? Reseed from PLAN.md
   - Workflow error? Review sprint_agent.py logs

2. Fix and retry
   - Address root cause
   - Re-run failed phase
   - Do NOT proceed to next phase until fixed

3. Document blockers
   - Add to STATUS.md under "Open Blockers"
   - Create issue in GitHub if blocker is complex
   - Escalate if blocker requires external dependency

---

## Success Criteria

Sprint 2 execution is READY when:
- ✅ LOCAL db has 15 stories with sprint_id="Sprint-02"
- ✅ Cloud Cosmos 51-ACA record has ado_project="51-aca"
- ✅ ADO Sprint 2 board shows 15 work items (IDs 2978-2993)
- ✅ Baseline tests pass (pytest exits 0)
- ✅ MTI >= 30 (gate threshold for Sprint 2)
- ✅ sprint-agent.yml workflow is healthy
- ✅ All DPDCA phases validated

Sprint 2 execution is COMPLETE when:
- ✅ All 15 stories executed (D→P→D→C→A)
- ✅ Evidence receipts generated (.eva/evidence/)
- ✅ Tests pass (pytest exits 0)
- ✅ ADO work items transitioned to Done
- ✅ PR created with sprint results
- ✅ sprint-summary.md uploaded to artifacts
- ✅ Lessons learned documented

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|---|---|---|
| ADO Sync | 30 min | az CLI working, network access |
| Readiness Check | 15 min | ADO sync complete |
| Sprint Execution | 4-8 hours | Readiness gates pass |
| Review & Document | 30 min | Execution complete |
| **TOTAL** | **5-9 hours** | Full cycle |

---

## Next Immediate Action

**STATUS**: Ready to execute Task 1 (ADO Sync)

**COMMAND**:
```powershell
cd C:\AICOE\eva-foundry\51-ACA
pwsh -NoProfile -File update-ado-sprint2.ps1
```

**EXPECTED RESULT**: 15 "Updated work item NNNN" messages

**ON SUCCESS**: Move to Task 2 (Verify ADO Board)

**ON FAILURE**: Review error messages, check az CLI authentication
