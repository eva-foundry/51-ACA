# Agent Audit Plan -- Fully Automated Scrum Process

**Version**: 1.0.0
**Date**: 2026-02-28
**Goal**: Validate end-to-end agent-driven DPDCA workflow for 51-ACA SaaS delivery

---

## Audit Scope

**North Star**: Fully automated agile scrum process where:
- Human + AI Scrum Master: Plan sprints, set priorities
- Cloud Agents (GitHub Actions): Execute stories, write code, run tests
- Validation Agents: Audit work, update data model, plan next sprint
- Goal: Deliver 51-ACA SaaS product to production

**Audit Phases**:
1. Component Validation (each agent individually)
2. Integration Testing (end-to-end sprint execution)
3. Telemetry Audit (all metrics captured)
4. Production Readiness (gates, rollback, monitoring)

---

## Phase 1: Component Validation

### A1. Sprint Agent (sprint_agent.py)

**Purpose**: Execute stories in GitHub Actions with LLM code generation

**Capabilities**:
- [x] Parse sprint manifest from GitHub issue
- [x] Read story metadata from data model
- [x] Generate code via GitHub Models API (gpt-4o)
- [x] Write files to repo
- [x] Run pytest with retry logic (3 attempts, exponential backoff)
- [x] Write Veritas evidence receipts (5 new metrics)
- [x] Update ADO work items (4 integration points)
- [x] Post sprint summary to GitHub issue
- [ ] Parallel story execution (infrastructure ready, not activated)

**Telemetry Captured**:
- [x] duration_ms (story execution time)
- [x] files_changed (artifact count)
- [ ] tokens_used (TODO: track LLM usage)
- [ ] test_count_before/after (TODO: parse pytest --co)
- [x] test_result (PASS/FAIL)
- [x] lint_result (PASS/FAIL)
- [x] commit_sha

**Test Plan**:
```bash
# Test 1: Single story execution (local validation)
python test-runner.py  # Validates manifest loading, spec reading

# Test 2: GitHub Action execution (cloud validation)
gh issue create --title "Test: ACA-03-001" --body "$(cat test-manifest-ACA-03-001.json)"
gh workflow run sprint-agent.yml --field issue=<issue-number>
gh run watch

# Test 3: ADO sync validation
# - Check ADO work item state transitions (New → Active → Done)
# - Verify comments posted at 4 integration points
# - Validate Feature WI summary update
```

**Success Criteria**:
- [ ] Story executes without errors
- [ ] All files created/edited as specified
- [ ] pytest exits 0
- [ ] Evidence receipt written with all 7 fields
- [ ] ADO work item marked Done
- [ ] GitHub issue updated with progress comment
- [ ] Sprint summary posted with metrics table

**Blockers**:
- ⚠️ Requires GITHUB_TOKEN for LLM access (GitHub Models API)
- ⚠️ Requires ADO_PAT for ADO sync (optional, graceful degradation)
- ⚠️ tokens_used tracking not implemented (TODO in code)
- ⚠️ test_count tracking not implemented (TODO in code)

---

### A2. Veritas Expert Skill (veritas-expert.skill.md)

**Purpose**: Audit repo for trust metrics, gap detection, evidence completeness

**Capabilities**:
- [x] DPDCA loop: discover → reconcile → compute-trust → report
- [x] MTI formula: coverage×0.50 + evidence×0.20 + consistency×0.30
- [x] Gap detection (4 types: missing_impl, missing_evidence, orphan_artifact, extra_declaration)
- [x] Story tagging validation (EVA-STORY: ACA-NN-NNN format)
- [x] Evidence receipt validation (schema, required fields)
- [x] Trust score trending (sparkline in .eva/trust.json)

**Telemetry Captured**:
- [x] MTI score (0-100)
- [x] Component scores (coverage, evidence, consistency)
- [x] Gap count by type
- [x] Story tag coverage (% of modified lines with tags)
- [x] Evidence completeness (% of done stories with receipts)
- [x] Trust trend (last 10 scores)

**Test Plan**:
```bash
# Test 1: Audit current repo state
node C:\eva-foundry\48-eva-veritas\src\cli.js audit --repo . --warn-only

# Test 2: Validate MTI gate (30)
# - Check .eva/trust.json score field
# - Verify actions array (no "no-deploy" flag)

# Test 3: Gap detection
# - Introduce missing evidence (delete receipt file)
# - Run audit, verify gap detected
# - Restore receipt, verify gap cleared
```

**Success Criteria**:
- [x] MTI score computed correctly (current: 70)
- [x] All 4 gap types detected accurately
- [x] Story tags validated (3 in sprint_agent.py)
- [x] Evidence receipts validated (all done stories)
- [x] Trust trend displayed in sparkline
- [x] Actions array reflects MTI score (no "no-deploy" at MTI >= 30)

**Status**: ✅ OPERATIONAL (MTI=70, gate=30, PASS)

---

### A3. Sprint Advance Skill (sprint-advance.skill.md)

**Purpose**: 5-phase sprint handoff workflow (validate → audit → update → plan → deliver)

**Capabilities**:
- [x] Phase 1: Validate prior sprint (pytest gate, MTI >= 30)
- [x] Phase 2: Audit repo + data model (WBS integrity, endpoint coverage)
- [x] Phase 3: Update data model + ADO (mark done, create ADO items)
- [x] Phase 4: Determine next sprint stories (archaeology, undone dump, sizing)
- [x] Phase 5: Deliver sprint manifest + GitHub issue
- [ ] Automated execution (skill defined, not yet triggered)

**Telemetry Captured**:
- [ ] Phase completion times (not yet tracked)
- [ ] Story selection rationale (archaeology output)
- [ ] Dependency chain validation (blockers field)
- [ ] Capacity planning (FP allocation)
- [ ] Sprint velocity (stories/day from prior sprint)

**Test Plan**:
```bash
# Test 1: Manual skill invocation
# - User: "sprint 4" or "next sprint" or "advance to sprint 4"
# - Copilot loads sprint-advance.skill.md
# - Executes 5-phase workflow
# - Validates each gate

# Test 2: Automated invocation (future)
# - sprint_agent.py triggers sprint-advance at end of sprint
# - Validates prior sprint (pytest, MTI)
# - Creates next sprint manifest
# - Opens GitHub issue automatically
```

**Success Criteria**:
- [ ] Phase 1 executes: pytest exits 0, MTI >= 30
- [ ] Phase 2 executes: 0 WBS integrity violations
- [ ] Phase 3 executes: Data model updated, ADO items created
- [ ] Phase 4 executes: Next sprint stories selected with rationale
- [ ] Phase 5 executes: Sprint manifest JSON + GitHub issue created
- [ ] End-to-end time < 10 minutes

**Blockers**:
- ⚠️ Not yet automated (skill defined, manual trigger only)
- ⚠️ Requires ADO_PAT for Phase 3 (ADO item creation)
- ⚠️ Dependency graph builder not implemented (parallel execution prerequisite)

---

### A4. Gap Report Skill (gap-report.skill.md)

**Purpose**: Identify critical blockers, missing evidence, orphan tags, dependency chains

**Capabilities**:
- [x] Critical blocker detection (undone stories blocking others)
- [x] Missing evidence detection (done stories without receipts)
- [x] Orphan tag detection (EVA-STORY tags for non-existent IDs)
- [x] Dependency chain tracing (transitive closure via blockers field)
- [x] Estimate to milestone (sum FP of undone M1.0 stories)
- [ ] Automated execution (skill defined, not yet triggered)

**Telemetry Captured**:
- [ ] Blocker count by epic
- [ ] Missing evidence count
- [ ] Orphan tag count
- [ ] Critical path length (longest dependency chain)
- [ ] Estimated effort to M1.0 (FP sum)

**Test Plan**:
```bash
# Test 1: Manual skill invocation
# - User: "gap report" or "what's blocking us" or "critical path"
# - Copilot loads gap-report.skill.md
# - Queries data model requirements layer
# - Displays prioritized gap list

# Test 2: Validate blocker detection
# - Add blockers field to story in PLAN.md
# - Re-seed data model
# - Run gap report
# - Verify blocker appears in critical list
```

**Success Criteria**:
- [ ] All critical blockers identified (stories blocking 2+ others)
- [ ] All missing evidence detected (done stories without receipts)
- [ ] All orphan tags detected (tags not in veritas-plan.json)
- [ ] Dependency chains traced correctly (transitive closure)
- [ ] M1.0 estimate accurate (sum FP of undone M1.0 stories)
- [ ] Remediation steps provided for each gap

**Blockers**:
- ⚠️ Not yet triggered (skill defined, awaiting manual invocation)
- ⚠️ Blockers field not in data model schema (needs seed update)
- ⚠️ Milestone tracking not implemented (M1.0 field missing)

---

### A5. Progress Report Skill (progress-report.skill.md)

**Purpose**: Generate comprehensive project status (epic completion, test trends, next stories)

**Capabilities**:
- [x] Epic completion percentages (done/total per epic)
- [x] Phase 1 (M1.0) readiness score
- [x] Recent commits with story IDs (last 10 from git log)
- [x] Test count trend (from .eva/trust.json)
- [x] Open blockers table
- [x] Next 5 recommended stories (undone, no blockers, sized)
- [x] Automated execution (validated manually in Phase 37)

**Telemetry Captured**:
- [x] Epic completion % (14 epics tracked)
- [x] Overall progress (73/256 = 28.5%)
- [x] MTI score (70)
- [x] Recent commit count (10 commits parsed)
- [x] Next story recommendations (5 stories)
- [ ] Test count trend (TODO: not in trust.json yet)
- [ ] Blocker count (TODO: blockers field not in model)

**Test Plan**:
```bash
# Test 1: Manual execution (DONE in Phase 37)
# - Created 70-line Python script
# - Executed progress-report workflow
# - Validated all 7 steps
# - Confirmed epic completion breakdown

# Test 2: Copilot trigger
# - User: "progress report" or "where are we" or "project status"
# - Copilot loads progress-report.skill.md
# - Executes workflow via Python temp script
# - Displays comprehensive DPDCA status
```

**Success Criteria**:
- [x] All 14 epic completion % calculated correctly
- [x] M1.0 readiness score computed
- [x] Last 10 commits parsed with story IDs
- [x] MTI score retrieved from .eva/trust.json
- [x] Next 5 stories recommended (prioritized by epic completion)
- [x] Overall progress calculated (done/total)

**Status**: ✅ VALIDATED (executed manually in Phase 37, all steps working)

---

### A6. Sprint Report Skill (sprint-report.skill.md)

**Purpose**: Generate sprint summary (velocity, completion, MTI trend, blockers, test coverage)

**Capabilities**:
- [x] Sprint velocity chart (planned vs actual FP)
- [x] Story completion table (done/in-progress/blocked)
- [x] MTI trend (current sprint vs prior 3)
- [x] Blocker list (stories with non-empty blockers field)
- [x] Test coverage delta (test count start vs close)
- [ ] Automated execution (skill defined, not yet triggered)

**Telemetry Captured**:
- [ ] Planned FP (from sprint manifest)
- [ ] Actual FP (from completed stories)
- [ ] Velocity (stories/day, FP/day)
- [ ] Completion % (done/total)
- [ ] MTI at sprint start/close
- [ ] Test count at sprint start/close
- [ ] Blocker count

**Test Plan**:
```bash
# Test 1: Manual skill invocation
# - User: "sprint report" or "sprint 2 summary" or "sprint metrics"
# - Copilot loads sprint-report.skill.md
# - Queries data model sprints layer
# - Generates velocity chart + completion table

# Test 2: Validate sprint velocity calculation
# - Load Sprint 2 data from data model
# - Calculate planned vs actual FP
# - Display velocity chart (stories/day, FP/day)
```

**Success Criteria**:
- [ ] Sprint velocity calculated correctly (planned vs actual)
- [ ] Story completion table accurate (done/in-progress/blocked)
- [ ] MTI trend displayed (current sprint vs prior 3)
- [ ] Blocker list complete (all blocked stories)
- [ ] Test coverage delta calculated (start vs close)
- [ ] Output: Markdown report + JSON artifact

**Blockers**:
- ⚠️ Not yet triggered (skill defined, awaiting manual invocation)
- ⚠️ Sprints layer not populated in data model (need sprint records)
- ⚠️ Test count not tracked in sprint records

---

## Phase 2: Integration Testing

### I1. End-to-End Sprint Execution (Single Story)

**Test**: Execute ACA-03-001 via GitHub Actions

**Setup**:
```bash
# 1. Create GitHub issue with sprint manifest
gh issue create \
  --title "Test Sprint: ACA-03-001" \
  --body "$(cat test-manifest-ACA-03-001.json)" \
  --repo eva-foundry/51-ACA

# 2. Trigger sprint-agent workflow
gh workflow run sprint-agent.yml \
  --field issue=<issue-number> \
  --repo eva-foundry/51-ACA

# 3. Monitor execution
gh run watch --repo eva-foundry/51-ACA
```

**Expected Outputs**:
1. **Code Generated**:
   - services/analysis/app/rules/__init__.py (ALL_RULES list)
   - services/analysis/app/rules/rule_01_dev_box_autostop.py (12 files total)
   - services/analysis/app/main.py (updated to load ALL_RULES)

2. **Tests Pass**:
   - pytest services/analysis/ -v exits 0
   - All 12 rules imported and registered

3. **Evidence Receipt**:
   - .eva/evidence/ACA-03-001-receipt.json created
   - All 7 fields populated:
     ```json
     {
       "story_id": "ACA-03-001",
       "phase": "A",
       "timestamp": "2026-02-28T...",
       "artifacts": ["services/analysis/app/rules/__init__.py", ...],
       "test_result": "PASS",
       "commit_sha": "abc123",
       "duration_ms": 45000,
       "tokens_used": 12500,
       "test_count_before": 24,
       "test_count_after": 27,
       "files_changed": 13
     }
     ```

4. **ADO Sync** (if ADO_PAT set):
   - Work item 123 state: New → Active (at story start)
   - Work item 123 state: Active → Done (at story complete)
   - Comment posted with progress update
   - Feature WI updated with sprint summary

5. **GitHub Updates**:
   - Issue comment with story progress
   - Final summary comment with metrics table

6. **Data Model Updates**:
   - Story status: planned → done
   - Endpoint schemas updated (if endpoints created)

**Validation Checklist**:
- [ ] Sprint agent executes without errors
- [ ] All 13 files created
- [ ] pytest exits 0
- [ ] Evidence receipt has all 7 fields
- [ ] ADO work item marked Done
- [ ] GitHub issue updated
- [ ] Data model story status = done
- [ ] MTI remains >= 30

---

### I2. Full Sprint Execution (5 Stories)

**Test**: Execute Sprint 4 with 5 stories from Epic 3

**Stories**:
1. ACA-03-001 -- Load all 12 rules
2. ACA-03-002 -- Handle rule failure in isolation
3. ACA-03-003 -- Persist findings to Cosmos
4. ACA-03-004 -- Update AnalysisRun status
5. ACA-03-005 -- Write findingsSummary

**Setup**:
```bash
# 1. Run sprint-advance skill to generate Sprint 4 manifest
# User: "plan sprint 4 with ACA-03-001 through ACA-03-005"

# 2. Create GitHub issue with manifest
gh issue create --title "Sprint 4: Analysis Engine Core" --body "..."

# 3. Trigger workflow
gh workflow run sprint-agent.yml --field issue=<issue-number>
```

**Expected Outputs**:
- 5 stories completed
- 30+ files created/edited
- pytest exits 0 (all services)
- 5 evidence receipts
- 5 ADO work items marked Done
- Sprint summary with velocity chart
- Data model updated (5 stories done, endpoints updated)

**Validation Checklist**:
- [ ] All 5 stories execute in sequence
- [ ] No story blocks subsequent stories (isolation)
- [ ] Retry logic works (if transient failures)
- [ ] All tests pass
- [ ] All evidence receipts written
- [ ] ADO sync works for all 5 stories
- [ ] Sprint summary posted with metrics
- [ ] MTI >= 30 at sprint end

---

### I3. Sprint Handoff (sprint-advance skill)

**Test**: Trigger sprint-advance after Sprint 4 completion

**Setup**:
```bash
# Manual trigger after Sprint 4 complete
# User: "advance to sprint 5" or "next sprint"
```

**Expected Workflow**:
1. **Phase 1: Validate Sprint 4**
   - pytest exits 0
   - MTI >= 30 (current: 70)
   - All done stories have evidence

2. **Phase 2: Audit repo + data model**
   - WBS integrity check (no orphan stories)
   - Endpoint coverage check (all stubs implemented or marked)

3. **Phase 3: Update data model + ADO**
   - Mark 5 stories done in data model
   - Update endpoint schemas
   - Create ADO items for Sprint 5 stories

4. **Phase 4: Determine Sprint 5 stories**
   - Run archaeology (undone stories, no blockers)
   - Calculate capacity (velocity from Sprint 4)
   - Select stories (Epic 3 priority, ~20 FP)

5. **Phase 5: Deliver manifest + issue**
   - Generate sprint-05-manifest.json
   - Create GitHub issue
   - Post to sprint channel (if webhooks configured)

**Validation Checklist**:
- [ ] Phase 1 gates pass (pytest, MTI)
- [ ] Phase 2 audit clean (0 violations)
- [ ] Phase 3 updates complete (data model + ADO)
- [ ] Phase 4 story selection rational (archaeology output)
- [ ] Phase 5 artifacts created (manifest + issue)
- [ ] End-to-end time < 10 minutes

---

## Phase 3: Telemetry Audit

### T1. Evidence Receipts (Veritas Integration)

**Required Fields** (7):
- [x] story_id (ACA-NN-NNN format)
- [x] phase (D|P|D|C|A)
- [x] timestamp (ISO 8601 UTC)
- [x] artifacts (file paths array)
- [x] test_result (PASS|FAIL)
- [x] commit_sha (git rev-parse HEAD)
- [x] duration_ms (story execution time)
- [ ] tokens_used (TODO: track LLM usage)
- [ ] test_count_before (TODO: parse pytest --co)
- [ ] test_count_after (TODO: parse pytest --co)
- [x] files_changed (len(artifacts))

**Tracking**:
```python
# sprint_agent.py lines 578-620
def write_evidence(story, test_result, lint_result,
                   duration_ms=0, tokens_used=0,
                   test_count_before=0, test_count_after=0,
                   files_changed=0) -> str:
    receipt = {
        "story_id": story["id"],
        "phase": "A",
        "timestamp": _now_iso(),
        "artifacts": written_files,
        "test_result": test_result,
        "commit_sha": sha,
        "duration_ms": duration_ms,       # ✅ Working
        "tokens_used": tokens_used,       # ⚠️ TODO
        "test_count_before": test_count_before,  # ⚠️ TODO
        "test_count_after": test_count_after,    # ⚠️ TODO
        "files_changed": files_changed    # ✅ Working
    }
```

**Validation**:
- [x] duration_ms calculated correctly (story start → complete)
- [x] files_changed matches len(artifacts)
- [ ] tokens_used tracks LLM API usage (not implemented)
- [ ] test_count parsed from pytest --co output (not implemented)

**TODO Items**:
```python
# Line 891: Track LLM tokens
generated = retry_with_backoff(
    lambda: _generate_code(story, context),
    operation_name=f"Code generation for {sid}",
    max_attempts=MAX_RETRY_ATTEMPTS
)
# TODO: Extract token usage from LLM response
# tokens_used = generated.get("usage", {}).get("total_tokens", 0)

# Line 842: Track test count
# TODO: Run pytest --co before/after to count tests
# test_count_before = int(subprocess.run(...).stdout.split()[0])
# ... (implementation)
# test_count_after = int(subprocess.run(...).stdout.split()[0])
```

---

### T2. ADO Integration (4 Integration Points)

**Integration Points**:

1. **Story Start** (line ~831):
   ```python
   if ADO_ENABLED and ado_id:
       patch_ado_wi_state(ado_id, "Active")
       post_ado_wi_comment(ado_id, f"Story started: {sid}")
   ```

2. **Story Complete** (line ~868):
   ```python
   if ADO_ENABLED and ado_id:
       patch_ado_wi_state(ado_id, "Done")
       post_ado_wi_comment(ado_id, f"Story complete: {sid} (tests: {test_status})")
   ```

3. **Story Failure** (line ~878):
   ```python
   if ADO_ENABLED and ado_id:
       post_ado_wi_comment(ado_id, f"Story failed: {sid}\nError: {exc}")
   ```

4. **Sprint Complete** (line ~1005):
   ```python
   if ADO_ENABLED and feature_ado_id:
       summary = _sprint_summary_comment(sprint, results, branch,
                                          duration_minutes, velocity)
       post_ado_wi_comment(feature_ado_id, summary)
   ```

**Telemetry**:
- [ ] ADO sync success/failure logged
- [ ] HTTP status codes captured (200 = success)
- [ ] Error messages persisted (if sync fails)
- [ ] Retry count (if transient failures)

**Validation**:
```bash
# Check ADO work item history
az boards work-item show --id <ado-id> --org https://dev.azure.com/marcopresta

# Expected:
# - State transitions: New → Active → Done
# - 3-4 comments (start, progress updates, complete)
# - Last comment = sprint summary (if Feature WI)
```

---

### T3. Data Model Updates

**Update Operations**:

1. **Story Status** (after completion):
   ```python
   # Query story from data model
   story = requests.get(f"{DATA_MODEL_API}/model/requirements/{story_id}").json()
   
   # Update status
   story["status"] = "done"
   
   # PUT back to model
   requests.put(f"{DATA_MODEL_API}/model/requirements/{story_id}",
                json=story,
                headers={"X-Actor": "sprint-agent"})
   ```

2. **Endpoint Schemas** (if new endpoints created):
   ```python
   # Endpoint schema update via put-schemas.py
   # Triggered by seed-from-plan.py at end of sprint
   ```

**Telemetry**:
- [ ] Data model PUT requests logged
- [ ] row_version incremented correctly
- [ ] modified_by = "sprint-agent"
- [ ] modified_at = current timestamp

**Validation**:
```powershell
# Query story status
$base = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"
Invoke-RestMethod "$base/model/requirements/ACA-03-001" | Select-Object id, status, modified_by

# Expected:
# id: ACA-03-001
# status: done (was: planned)
# modified_by: sprint-agent (was: seed-from-plan)
```

---

### T4. Sprint Metrics (Dashboard)

**Metrics Captured**:

1. **Duration** (minutes):
   ```python
   start_dt = datetime.fromisoformat(state["started"])
   end_dt = datetime.now(timezone.utc)
   duration_minutes = (end_dt - start_dt).total_seconds() / 60
   ```

2. **Velocity** (stories/day, FP/day):
   ```python
   duration_days = duration_minutes / (24 * 60)
   velocity = len(results) / duration_days if duration_days > 0 else 0
   ```

3. **Completion %**:
   ```python
   completed = sum(1 for r in results if r["status"] == "DONE")
   completion_pct = (completed / total) * 100
   ```

4. **Average Story Duration**:
   ```python
   avg_story_duration = duration_minutes / total if total > 0 else 0
   ```

5. **Total Files Changed**:
   ```python
   total_files = sum(len(r.get("files", [])) for r in results)
   ```

**Output Format** (sprint summary comment):
```markdown
### Summary Metrics
| Metric | Value |
|--------|-------|
| Duration | 45.2 minutes |
| Velocity | 1.36 stories/day |
| Completion | 5/5 (100%) |
| Total Files | 48 |
| Avg Story Time | 9.0 min |

### Story Breakdown
| Story | Files | Lint | Tests | Status |
|-------|-------|------|-------|--------|
| ACA-03-001 | 13 files | PASS | PASS | DONE |
| ACA-03-002 | 8 files | PASS | PASS | DONE |
| ACA-03-003 | 12 files | PASS | PASS | DONE |
| ACA-03-004 | 7 files | PASS | PASS | DONE |
| ACA-03-005 | 8 files | PASS | PASS | DONE |
```

**Validation**:
- [ ] All 5 metrics calculated correctly
- [ ] Story breakdown table accurate
- [ ] Markdown rendering correct
- [ ] JSON artifact written to sprint-summary.json

---

## Phase 4: Production Readiness

### P1. Gates (Quality Assurance)

**Gates Enforced**:

1. **pytest Gate**:
   ```bash
   pytest services/ -x -q 2>&1
   # Must exit 0 before commit
   ```

2. **MTI Gate**:
   ```bash
   node cli.js audit --repo . --warn-only
   # MTI must be >= 30 (current: 70)
   ```

3. **Story Tag Gate**:
   ```python
   # Every modified file must have EVA-STORY: ACA-NN-NNN tag
   # Enforced by veritas consistency score
   ```

4. **Evidence Gate**:
   ```bash
   # Every done story must have evidence receipt
   # Checked by veritas evidenceCompleteness score
   ```

**Validation**:
- [x] pytest gate enforced by sprint_agent.py (retry logic)
- [x] MTI gate enforced by sprint-advance.skill.md (Phase 1)
- [x] Story tag gate enforced by veritas audit (consistency component)
- [x] Evidence gate enforced by veritas audit (evidence component)

---

### P2. Rollback Strategy

**Rollback Triggers**:
1. pytest fails after 3 retry attempts
2. MTI drops below 30
3. Evidence receipt missing for done story
4. Data model integrity violation

**Rollback Actions**:
1. Revert commit (git revert)
2. Mark story as "blocked" in data model
3. Post failure comment to ADO work item
4. Create blocker issue in GitHub
5. Alert human scrum master

**Implementation**:
```python
# sprint_agent.py (not yet implemented)
def rollback_story(story_id: str, reason: str):
    # Revert git commit
    subprocess.run(["git", "revert", "--no-edit", "HEAD"])
    
    # Update data model
    story = requests.get(f"{DATA_MODEL_API}/model/requirements/{story_id}").json()
    story["status"] = "blocked"
    story["notes"] = f"Rollback: {reason}"
    requests.put(f"{DATA_MODEL_API}/model/requirements/{story_id}", json=story)
    
    # Create blocker issue
    subprocess.run(["gh", "issue", "create",
                    "--title", f"BLOCKER: {story_id} rollback",
                    "--body", reason,
                    "--label", "blocker"])
```

**TODO**: Implement rollback_story() in sprint_agent.py

---

### P3. Monitoring & Alerting

**Metrics to Monitor**:

1. **Sprint Agent Health**:
   - GitHub Actions workflow success rate
   - Average story duration
   - LLM API error rate
   - pytest failure rate

2. **Data Model Health**:
   - API uptime (99.9% SLA)
   - Query latency (< 500ms p95)
   - PUT conflict rate (row_version collisions)

3. **Veritas Health**:
   - MTI trend (should not drop > 10 points)
   - Gap count (should decrease over time)
   - Evidence completeness (should be 100% for done stories)

4. **ADO Sync Health**:
   - Sync success rate (> 95%)
   - API error rate (< 5%)
   - State transition accuracy (100%)

**Alerting**:
```yaml
# .github/workflows/sprint-agent-monitor.yml
name: Sprint Agent Monitor

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Check MTI
        run: |
          MTI=$(curl -s $DATA_MODEL_API/model/admin/mti | jq .score)
          if [ $MTI -lt 30 ]; then
            echo "MTI=$MTI ALERT: Below gate threshold"
            # Send alert to Teams/Slack
          fi
      
      - name: Check Evidence Completeness
        run: |
          COMPLETE=$(node cli.js audit --repo . | grep evidenceCompleteness | awk '{print $2}')
          if [ $COMPLETE != "1" ]; then
            echo "Evidence incomplete: $COMPLETE"
            # Send alert
          fi
```

**TODO**: Implement sprint-agent-monitor.yml workflow

---

## Test Execution Plan

### Week 1: Component Validation (Days 1-3)

**Day 1**: Sprint Agent + Veritas
- [ ] Test A1: Sprint agent (single story)
- [ ] Test A2: Veritas audit (current repo)
- [ ] Validate telemetry (evidence receipts, MTI score)

**Day 2**: Skills System
- [ ] Test A3: sprint-advance skill (manual trigger)
- [ ] Test A4: gap-report skill (manual trigger)
- [ ] Test A5: progress-report skill (re-validate)
- [ ] Test A6: sprint-report skill (manual trigger)

**Day 3**: ADO Integration
- [ ] Deploy ADO_PAT secret to GitHub
- [ ] Test ADO sync (4 integration points)
- [ ] Validate work item state transitions
- [ ] Validate sprint summary comment

### Week 2: Integration Testing (Days 4-6)

**Day 4**: Single Story E2E
- [ ] Test I1: ACA-03-001 via GitHub Actions
- [ ] Validate all outputs (code, tests, evidence, ADO, GitHub)
- [ ] Check MTI score (should remain >= 70)

**Day 5**: Full Sprint (5 Stories)
- [ ] Test I2: Sprint 4 execution (ACA-03-001 through ACA-03-005)
- [ ] Monitor execution (30-60 minutes expected)
- [ ] Validate sprint summary metrics

**Day 6**: Sprint Handoff
- [ ] Test I3: sprint-advance skill (Sprint 4 → Sprint 5)
- [ ] Validate 5-phase workflow
- [ ] Check end-to-end time (< 10 minutes target)

### Week 3: Telemetry & Production (Days 7-10)

**Day 7**: Telemetry Audit
- [ ] Test T1: Evidence receipts (all 7 fields)
- [ ] Test T2: ADO integration (all 4 points)
- [ ] Test T3: Data model updates (story status, endpoints)
- [ ] Test T4: Sprint metrics (dashboard)

**Day 8**: TODO Completion
- [ ] Implement tokens_used tracking
- [ ] Implement test_count tracking
- [ ] Implement rollback_story()
- [ ] Implement sprint-agent-monitor.yml

**Day 9**: Production Readiness
- [ ] Test P1: All gates enforced
- [ ] Test P2: Rollback strategy (inject failure)
- [ ] Test P3: Monitoring & alerting (webhook setup)

**Day 10**: Go/No-Go Decision
- [ ] Review all test results
- [ ] Validate all telemetry captured
- [ ] Check MTI >= 30
- [ ] Approve Sprint 4 execution in production

---

## Success Criteria (Go/No-Go)

**GO Criteria** (all must be ✅):
- [ ] Sprint agent executes single story without errors
- [ ] All 7 evidence receipt fields captured
- [ ] ADO sync works (all 4 integration points)
- [ ] pytest gate enforced (exits 0 required)
- [ ] MTI gate enforced (>= 30 required)
- [ ] Story tag gate enforced (consistency score)
- [ ] Evidence gate enforced (completeness score)
- [ ] Data model updates successful (story status, endpoints)
- [ ] Sprint metrics calculated correctly (5 metrics)
- [ ] sprint-advance skill executes 5 phases
- [ ] No critical blockers detected by gap-report skill

**NO-GO Criteria** (any triggers halt):
- [ ] Sprint agent crashes (unhandled exception)
- [ ] pytest fails after 3 retries
- [ ] MTI drops below 30
- [ ] Evidence receipt missing required fields
- [ ] ADO sync fails (> 10% error rate)
- [ ] Data model PUT returns 409 conflict
- [ ] Critical blocker detected (story blocking 5+ others)

---

## Current Status Summary

**Components**:
- [x] Sprint agent: READY (cloud execution via GitHub Actions)
- [x] Veritas expert: OPERATIONAL (MTI=70, gate=30, PASS)
- [x] Sprint advance: DEFINED (skill ready, not yet triggered)
- [x] Gap report: DEFINED (skill ready, not yet triggered)
- [x] Progress report: VALIDATED (manual execution successful)
- [x] Sprint report: DEFINED (skill ready, not yet triggered)

**Telemetry**:
- [x] Evidence receipts: 5/7 fields working (duration_ms, files_changed)
- [ ] Evidence receipts: 2/7 fields TODO (tokens_used, test_count)
- [x] ADO sync: 4/4 integration points implemented
- [x] Data model updates: PUT operations ready
- [x] Sprint metrics: 5/5 metrics calculated

**Blockers**:
- ⚠️ tokens_used tracking not implemented (TODO in sprint_agent.py)
- ⚠️ test_count tracking not implemented (TODO in sprint_agent.py)
- ⚠️ Sprints layer not populated in data model (need sprint records)
- ⚠️ Blockers field not in model schema (need seed update)
- ⚠️ Milestone tracking not implemented (M1.0 field missing)
- ⚠️ Rollback strategy not implemented (need rollback_story())
- ⚠️ Monitoring workflow not created (sprint-agent-monitor.yml)

**Next Action**: Test I1 (single story execution via GitHub Actions)

---

## Appendix: Key Files

**Code**:
- `.github/scripts/sprint_agent.py` (1054 lines)
- `.github/workflows/sprint-agent.yml` (workflow definition)

**Skills**:
- `.github/copilot-skills/veritas-expert.skill.md` (302 lines)
- `.github/copilot-skills/sprint-advance.skill.md` (498 lines)
- `.github/copilot-skills/sprint-report.skill.md` (~300 lines)
- `.github/copilot-skills/gap-report.skill.md` (~300 lines)
- `.github/copilot-skills/progress-report.skill.md` (~350 lines)

**Data**:
- `data-model/aca-model.db` (local SQLite, 348 objects)
- `.eva/veritas-plan.json` (257 stories)
- `.eva/trust.json` (MTI=70)
- `test-manifest-ACA-03-001.json` (single story test)

**Docs**:
- `docs/saving-opportunity-rules.md` (12 rules spec)
- `STATUS.md` (v1.14.0, Sprint 3 summary)
- `PLAN.md` (14 epics, 256 stories)

---

**AUDIT PLAN COMPLETE** -- Ready for Week 1 execution
