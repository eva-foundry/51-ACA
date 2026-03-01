# Sprint 3 Workflow Enhancements

**Date**: 2026-02-28
**Status**: Ready for Implementation
**Target Sprint**: Sprint 3 (March 2026)
**Reference**: 38-ado-poc/sprint-execute.yml (555 lines, production-tested)

---

## Overview

Sprint 2 completed successfully with basic workflow automation. Sprint 3 enhancements bring the workflow to production-grade with full DPDCA integration, ADO sync, evidence tracking, and monitoring.

**Sprint 2 Baseline** (COMPLETE):
- ✅ Data model lifecycle integration (3 phases)
- ✅ AB# tags for ADO auto-linking
- ✅ Basic story execution (sequential)
- ✅ Progress comments to GitHub issues
- ✅ Graceful degradation if data model unavailable

**Sprint 3 Enhancements** (5 major improvements for 51-ACA):
1. ✨ **Veritas Evidence Receipts** - Full traceability chain
2. ✨ **ADO Bidirectional Sync** - Work item state + live progress
3. ✨ **Enhanced Error Handling** - Retry logic + failure recovery
4. ✨ **Parallel Story Execution** - Independent stories run concurrently
5. ✨ **Sprint Summary Dashboard** - Metrics + velocity visualization

**Note**: Heartbeat monitoring (originally Enhancement 3) has been moved to another EVA project for cross-cutting implementation. 51-ACA will consume it when available. See `docs/NEW-FEATURES-2026-02-28.md` for complete heartbeat specification.

---

## Enhancement 1: Veritas Evidence Receipts

### Current State
- Evidence receipts partially implemented (`.eva/evidence/*.json`)
- No Veritas audit after sprint completion
- MTI score not calculated
- No blocking on MTI regression

### Target State
```python
# After each story completes:
evidence = {
    "story_id": "ACA-NN-NNN",
    "phase": "A",  # DPDCA phase
    "timestamp": "2026-02-28T17:45:47Z",
    "artifacts": ["services/analysis/app/rules/devbox_autostop.py"],
    "test_result": "PASS",
    "lint_result": "PASS",
    "commit_sha": "4695206e...",
    "duration_ms": 45200,
    "tokens_used": 3210,
    "test_count_before": 24,
    "test_count_after": 27,
    "files_changed": 3
}
# Write to: .eva/evidence/<story-id>-receipt.json
# Commit to: sprint branch
```

**After sprint completes:**
```bash
# Run Veritas audit
node C:\AICOE\eva-foundry\48-eva-veritas\src\cli.js audit --repo .

# Check MTI score
if [ $MTI -lt 30 ]; then
    echo "[FAIL] MTI regression detected"
    post_wi_comment $FEATURE_ID "Sprint BLOCKED: MTI=$MTI (threshold 30)"
    exit 1
fi
```

### Implementation Steps

1. **Enhance `write_evidence()` in sprint_agent.py**
   - Add all required fields (duration_ms, tokens_used, test counts)
   - Calculate metrics from story execution timeline
   - Write structured JSON receipt

2. **Add Veritas audit step to workflow**
   - Install Node.js + Veritas CLI in workflow
   - Run audit after all stories complete
   - Parse MTI score from audit output
   - Block merge if MTI < 30

3. **Update commit format**
   - Include evidence receipt in commit (already done via `.eva/evidence/`)
   - Add `ACA-METRICS:` trailer to commit body with parseable metrics

### Files to Modify
- `.github/scripts/sprint_agent.py` - Enhance `write_evidence()` function
- `.github/workflows/sprint-agent.yml` - Add Veritas audit step
- `.github/workflows/sprint-agent.yml` - Add MTI gate check

---

## Enhancement 2: ADO Bidirectional Sync

### Current State
- Commits include AB# tags (one-way linking)
- No ADO work item state updates
- No live progress comments to ADO
- Manual PM oversight required

### Target State

**Sprint Start**:
```python
# Query ADO for work items in sprint
for wi_id in sprint_work_items:
    wi_state = get_ado_wi_state(wi_id)
    if wi_state == "Done":
        print(f"[SKIP] WI {wi_id} already complete")
        continue
    
    # Mark WI as Active
    patch_ado_wi_state(wi_id, "Active")
    post_ado_wi_comment(wi_id, f"Started by sprint-agent | Run: {GH_RUN_URL}")
```

**Per Story**:
```python
# Before generation
post_ado_wi_comment(ado_id, f"{story_id} - Phase: Generate (DPDCA-D)")

# After commit
post_ado_wi_comment(ado_id, f"{story_id} - Committed {sha[:8]} | Tests: PASS | Lint: PASS")

# On completion
patch_ado_wi_state(ado_id, "Done")
post_ado_wi_comment(ado_id, f"{story_id} - COMPLETE | Duration: {duration_min} min")
```

**Sprint Complete**:
```python
# Post summary to Feature work item
summary = f"""
Sprint {sprint_id} Complete
- Stories: {done_count}/{total_count}
- Velocity: {velocity:.2f} stories/day
- Tests: {test_count} passing
- MTI: {mti_score}
- PR: {pr_url}
"""
post_ado_wi_comment(feature_id, summary)
```

### Implementation Steps

1. **Add ADO API client to sprint_agent.py**
   ```python
   import base64
   import requests
   
   ADO_ORG_URL = "https://dev.azure.com/marcopresta"
   ADO_PROJECT = "51-aca"
   ADO_PAT = os.getenv("ADO_PAT", "")
   ADO_AUTH = base64.b64encode(f":{ADO_PAT}".encode()).decode()
   
   def post_ado_wi_comment(wi_id: int, message: str):
       url = f"{ADO_ORG_URL}/{ADO_PROJECT}/_apis/wit/workitems/{wi_id}/comments?api-version=7.1"
       headers = {"Authorization": f"Basic {ADO_AUTH}", "Content-Type": "application/json"}
       payload = {"text": f"[{_now_iso()}] {message}"}
       response = requests.post(url, json=payload, headers=headers)
       response.raise_for_status()
   
   def patch_ado_wi_state(wi_id: int, state: str):
       url = f"{ADO_ORG_URL}/{ADO_PROJECT}/_apis/wit/workitems/{wi_id}?api-version=7.1"
       headers = {"Authorization": f"Basic {ADO_AUTH}", "Content-Type": "application/json-patch+json"}
       payload = [{"op": "replace", "path": "/fields/System.State", "value": state}]
       response = requests.patch(url, json=payload, headers=headers)
       response.raise_for_status()
   ```

2. **Integrate ADO calls into run_sprint() loop**
   - After sprint branch creation: Post to Feature WI
   - Before story generation: Mark WI Active + post comment
   - After story commit: Post progress comment with metrics
   - After story complete: Mark WI Done
   - After sprint complete: Post summary to Feature WI

3. **Add ADO_PAT secret to GitHub repository**
   - Generate PAT in Azure DevOps with Work Items Read/Write scope
   - Add to repository secrets: `ADO_PAT`
   - Reference in workflow: `${{ secrets.ADO_PAT }}`

### Files to Modify
- `.github/scripts/sprint_agent.py` - Add ADO API client functions
- `.github/scripts/sprint_agent.py` - Integrate ADO calls in `run_sprint()`
- `.github/workflows/sprint-agent.yml` - Pass ADO_PAT from secrets
- `README.md` - Document ADO_PAT setup requirement

---

## Enhancement 3: Enhanced Error Handling (formerly Enhancement 4)

### Current State
- Single exception handler per story
- No retry logic for transient failures
- Workflow exits on first error

### Target State

**Retry Logic**:
```python
import time
from typing import Callable, Any

def retry_with_backoff(func: Callable, max_attempts: int = 3, backoff_seconds: int = 5) -> Any:
    """Retry function with exponential backoff."""
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as exc:
            if attempt == max_attempts:
                raise
            wait_time = backoff_seconds * (2 ** (attempt - 1))
            print(f"[WARN] Attempt {attempt} failed: {exc}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

# Usage:
def generate_code_with_retry():
    return retry_with_backoff(lambda: _generate_code(story, context), max_attempts=3)
```

**Failure Recovery**:
```python
# If LLM call fails:
try:
    generated = _generate_code(story, context)
except Exception as llm_error:
    # Fallback: Use template-based generation
    generated = _generate_from_template(story)
    post_ado_wi_comment(story["ado_id"], f"[WARN] LLM generation failed, used template fallback")

# If test fails:
if test_status != "PASS":
    # Auto-fix attempt
    print("[INFO] Tests failed, attempting auto-fix...")
    fix_result = _attempt_auto_fix(written_files, test_output)
    if fix_result:
        test_status = run_checks()[1]
```

### Implementation Steps

1. **Add retry_with_backoff utility**
2. **Wrap LLM calls with retry**
3. **Add template fallback for code generation**
4. **Add auto-fix attempt for test failures**

### Files to Modify
- `.github/scripts/sprint_agent.py` - Add retry utilities
- `.github/scripts/sprint_agent.py` - Wrap critical operations

---

## Enhancement 4: Parallel Story Execution (formerly Enhancement 5)

### Current State
- Sequential execution (one story at a time)
- No concurrency optimization
- Long sprint times for independent stories

### Target State

**Dependency Analysis**:
```python
def build_dependency_graph(stories: list) -> dict:
    """
    Parse story dependencies from 'depends_on' field.
    Returns: {story_id: [list of stories it depends on]}
    """
    graph = {}
    for story in stories:
        deps = story.get("depends_on", [])
        graph[story["id"]] = deps
    return graph

def get_execution_batches(stories: list) -> list[list]:
    """
    Group stories into batches that can execute in parallel.
    Returns: [[batch1_stories], [batch2_stories], ...]
    """
    graph = build_dependency_graph(stories)
    batches = []
    completed = set()
    
    while len(completed) < len(stories):
        batch = []
        for story in stories:
            if story["id"] in completed:
                continue
            deps = graph[story["id"]]
            if all(dep in completed for dep in deps):
                batch.append(story)
        
        if not batch:
            raise ValueError("Circular dependency detected!")
        
        batches.append(batch)
        completed.update(s["id"] for s in batch)
    
    return batches
```

**Parallel Execution**:
```python
import concurrent.futures

def execute_story_batch(stories: list) -> list:
    """Execute multiple stories in parallel."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(execute_single_story, s): s for s in stories}
        results = []
        for future in concurrent.futures.as_completed(futures):
            story = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"[FAIL] Story {story['id']} failed: {exc}")
                results.append({"id": story["id"], "status": "FAIL", "error": str(exc)})
        return results

# In run_sprint():
batches = get_execution_batches(stories)
all_results = []
for batch_num, batch in enumerate(batches, 1):
    print(f"[INFO] Executing batch {batch_num}/{len(batches)}: {len(batch)} stories")
    batch_results = execute_story_batch(batch)
    all_results.extend(batch_results)
```

### Implementation Steps

1. **Add dependency graph builder**
2. **Add batch scheduler**
3. **Add parallel executor with ThreadPoolExecutor**
4. **Update SPRINT_MANIFEST schema** - Add `depends_on` field

### Files to Modify
- `.github/scripts/sprint_agent.py` - Add parallel execution engine
- `.github/SPRINT_ISSUE_TEMPLATE.md` - Document `depends_on` field
- `docs/WORKFLOW-DATA-MODEL-INTEGRATION.md` - Update with parallel execution docs

---

## Enhancement 5: Sprint Summary Dashboard (formerly Enhancement 6)

### Current State
- Text-only summary in issue comment
- No visual metrics
- No velocity trending

### Target State

**Structured Summary Output**:
```json
{
  "sprint_id": "51-ACA-sprint-02",
  "status": "complete",
  "duration_hours": 0.18,
  "velocity": 1.36,
  "stories": {
    "total": 15,
    "completed": 15,
    "failed": 0,
    "completion_pct": 100.0
  },
  "tests": {
    "before": 24,
    "after": 27,
    "added": 3
  },
  "metrics": {
    "avg_story_duration_min": 45.2,
    "total_files_created": 13,
    "total_commits": 15,
    "mti_score": 30
  },
  "pr_url": "https://github.com/eva-foundry/51-ACA/pull/42"
}
```

**Visual Dashboard** (GitHub issue comment with tables):
```markdown
## Sprint 2 Summary

| Metric | Value |
|--------|-------|
| Duration | 11 minutes |
| Velocity | 1.36 stories/day |
| Completion | 15/15 (100%) |
| Tests Added | +3 (24 → 27) |
| MTI Score | 30 ✅ |

### Story Breakdown

| Story | Duration | Tests | Status |
|-------|----------|-------|--------|
| ACA-03-001 | 45 min | ✅ PASS | ✅ DONE |
| ACA-03-002 | 38 min | ✅ PASS | ✅ DONE |
| ... | ... | ... | ... |

### Velocity Trend

Sprint 1: 0.92 stories/day
Sprint 2: 1.36 stories/day ↗️ **+48%**
```

### Implementation Steps

1. **Add summary generator function**
   - Collect all metrics from data model
   - Query historical sprints for velocity trend
   - Format as structured JSON + markdown tables

2. **Add summary posting**
   - Post to GitHub issue (already done)
   - Post to ADO Feature work item (new)
   - Write to `.eva/sprint-summary.json` artifact

3. **Optional: Web dashboard**
   - Static site generator from `.eva/sprint-*.json` files
   - Deploy to GitHub Pages
   - Charts: velocity trending, burndown, story duration distribution

### Files to Modify
- `.github/scripts/sprint_agent.py` - Add `generate_sprint_summary_dashboard()`
- `.github/workflows/sprint-agent.yml` - Upload summary as artifact

---

## Implementation Priority

**Note**: Heartbeat monitoring has been removed from 51-ACA scope. It will be implemented as a cross-cutting feature by another EVA project (38-ado-poc, 40-eva-control-plane, or new monitoring project). See `docs/NEW-FEATURES-2026-02-28.md` for complete specification.

### Phase 1: Critical (Sprint 3 Alpha)
1. ✅ Data model lifecycle integration (COMPLETE)
2. 🔄 Veritas evidence receipts (HIGH)
3. 🔄 ADO bidirectional sync (HIGH)

### Phase 2: Important (Sprint 3 Beta)
4. 🔄 Enhanced error handling (MEDIUM)
5. 🔄 Sprint summary dashboard (MEDIUM)

### Phase 3: Optimization (Sprint 4+)
6. 🔄 Parallel story execution (LOW - optimization, complex dependency management)

---

## Testing Plan

### Phase 1 Testing

**Test Sprint 3 Alpha** (Single story with full tracing):
- Story: ACA-04-009 (POST /v1/auth/preflight)
- Enable: Data model + Veritas + ADO sync
- Verify:
  - ✅ Data model updated (sprint + story records)
  - ✅ Evidence receipt written (`.eva/evidence/ACA-04-009-receipt.json`)
  - ✅ Veritas audit passes (MTI >= 30)
  - ✅ ADO work item state: New → Active → Done
  - ✅ ADO comments posted at each phase
  - ✅ Commit includes AB# tag

### Phase 2 Testing

**Test Sprint 3 Beta** (3 stories with error simulation):
- Stories: ACA-04-009, ACA-04-010, ACA-04-011
- Enable: All Phase 1 + error handling + dashboard
- Verify:
  - ✅ Retry logic works (simulate LLM timeout)
  - ✅ Template fallback works (simulate LLM error)
  - ✅ Sprint summary dashboard generates
  - ✅ Velocity trend displays correctly

### Phase 3 Testing

**Test Sprint 4** (5+ stories with parallelization):
- Stories: Multiple in (including parallel execution)
- Verify:
  - ✅ Parallel execution works (2+ stories concurrent)
  - ✅ Dependency graph built correctly
  - ✅ No deadlocks or race conditions
  - ✅ Per-story metrics aggregated correctly
  - ✅ Watchdog detects stall (simulate 30-min pause)

---

## Migration Path

### Backward Compatibility

All enhancements are **additive** — Sprint 2 workflows continue to work:
- Data model integration: Gracefully degrades if unavailable

**Note**: Heartbeat monitoring is not part of 51-ACA scope. It will be provided by another EVA project when available, with zero changes required to 51-ACA workflows.
- Veritas audit: Skips if Veritas CLI not installed
- Heartbeat: Skips if SPRINT_HEARTBEAT variable not created

### Incremental Rollout

1. **Deploy Phase 1** to Sprint 3 Alpha
2. **Run pilot sprint** with 1-2 stories
3. **Review metrics** (velocity, MTI, ADO sync success rate)
4. **Fix any issues** discovered
5. **Deploy Phase 2** to Sprint 3 Beta
6. **Run full Sprint 3** with Epic 4 stories
7. **Deploy Phase 3** to Sprint 4

---

## Documentation Updates

### Files to Update

1. **STATUS.md** - Mark Sprint 3 enhancements as ACTIVE
2. **PLAN.md** - Add Sprint 3 story checklist
3. **README.md** - Update workflow architecture diagram
4. **docs/WORKFLOW-DATA-MODEL-INTEGRATION.md** - Add Phase 2/3 sections
5. **.github/SPRINT_ISSUE_TEMPLATE.md** - Add `depends_on` field example
6. **.github/copilot-instructions.md** - Document ADO_PAT requirement

---

## Success Metrics

### Sprint 3 Alpha Goals

- ✅ 100% story completion rate (same as Sprint 2)
- ✅ MTI score >= 30 (maintain)
- ✅ ADO sync success rate >= 95%
- ✅ Evidence receipt coverage = 100%
- ✅ Velocity calculation accurate (within 10% margin)

### Sprint 3 Beta Goals

- ✅ Retry success rate >= 80% (transient failures recovered)
- ✅ Sprint summary dashboard generated
- ✅ Velocity trend displayed correctly

### Dependency graph handles complex interdependencies
- ✅ Zero deadlocks or race conditions in concurrent execution
- ✅ Historical velocity data enables sprint planning accuracy
- ✅ Parallel execution reduces sprint time by >= 30%
- ✅ Heartbeat stall detection < 5 minutes latency
- ✅ Watchdog alerts operational

---

## Cost Impact

### GitHub Actions Minutes

- Sprint 2 baseline: ~12 minutes for 15 stories = 0.8 min/story
- Sprint 3 Alpha (with ADO sync + Veritas): estimated +2 min overhead = ~14 minutes
- Sprint 3 Beta (with error handling): estimated +1 min = ~15 minutes
- Sprint 4 (with parallelization): estimated -30% time = ~10 minutes

### Azure Costs

- Data model server (ACA): $0.10/day (already running)
- Additional AI calls (retry logic): +10% tokens = $0.50/sprint
- Total incremental cost: **$0.50/sprint**

---

## References
 (cloud deployment at marco-eva-data-model ACA)
- **Azure DevOps REST API**: Work item comments + state updates
- **29-foundry patterns**: Parallel execution + error recovery
- **docs/NEW-FEATURES-2026-02-28.md**: Heartbeat monitoring specification (implemented by another project)

---

**Next Action**: Review this plan with PM → Approve Phase 1 → Begin implementation for Sprint 3 Alpha (ADO sync + Veritas evidence receipts)
---

**Next Action**: Review this plan with PM → Approve Phase 1 → Begin implementation for Sprint 3 Alpha.
