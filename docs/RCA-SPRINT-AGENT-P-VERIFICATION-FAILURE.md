# Root Cause Analysis: Sprint Agent P-Verification Failure

**Date**: 2026-03-11  
**Issue**: Sprint Agent workflow fails with "[FAIL] P verification: expected 4 [x] marks, found 1"  
**Run ID**: 22953448964 (and multiple prior runs)  
**Impact**: Cloud agent automation blocked - cannot execute GitHub issues  

---

## Executive Summary

The Sprint Agent workflow has a **fundamental design flaw** that prevents it from starting NEW sprints. Phase verifications (D1, D2, P) run BEFORE any work begins, but P verification expects PLAN.md to already have completion markers ([x]) for stories that haven't been worked yet.

**Root Cause**: Phase verification timing mismatch - checking for COMPLETION evidence at workflow START.

---

## Timeline of Events

| Time (UTC) | Event | Status |
|------------|-------|--------|
| 12:48:13 | Issue #39 created with correct SPRINT_MANIFEST | ✅ Success |
| 12:48:17 | Sprint Agent triggered (auto, label-based) | ⚠️ Started |
| 12:48:17 | Run 1 - NameError: 'branch' not defined | ❌ Failed |
| 12:51:13 | Fixed branch variable, run 2 | ⚠️ Started |
| 12:51:43 | TypeError: verify_phase() unexpected keyword 'expected_checked' | ❌ Failed |
| 12:53:43 | Fixed parameter, run 3 (manual dispatch) | ⚠️ Started |
| 12:54:13 | P verification failed: expected 4 [x] marks, found 1 | ❌ **ROOT CAUSE** |

---

## Detailed Analysis

### Workflow Execution Sequence

```
sprint_agent.py execution order:
├── 1. Parse SPRINT_MANIFEST from issue body
├── 2. Extract stories[] array (4 stories for Batch 1)
├── 3. Acquire lock (prevent duplicate runs)
├── 4. Create sprint branch: sprint/01-batch-1
├── 5. Initialize SprintContext
├── 6. start_sprint() - update data model
├── 7. Post opening comment to issue
├── 8. ❌ verify_phase("D1") - Check evidence files exist
├── 9. ❌ verify_phase("D2") - Check tests collected (pytest)
├── 10. ❌ verify_phase("P") - Check PLAN.md has [x] marks ← **FAILURE HERE**
├── 11. [NEVER REACHED] Load context
├── 12. [NEVER REACHED] Execute stories in loop
├── 13. [NEVER REACHED] Create PR
└── 14. [NEVER REACHED] Post completion comment
```

### The P-Verification Logic

**File**: `.github/scripts/phase_verifier.py` (lines 103-135)

```python
def verify_p_plan_update(sprint_id: str, expected_checked: int = 4, 
                        repo_root: Optional[str] = None) -> bool:
    """
    Verify Phase P (Plan) update: check PLAN.md has [x] marks for completed items.
    """
    repo_root = Path(repo_root) if repo_root else Path.cwd()
    plan_file = repo_root / "PLAN.md"
    
    if not plan_file.exists():
        print(f"[FAIL] P verification: PLAN.md not found")
        return False
    
    content = plan_file.read_text(encoding="utf-8")
    checked_count = len(re.findall(r"\[x\]", content))
    
    if checked_count < expected_checked:
        print(f"[FAIL] P verification: expected {expected_checked} [x] marks, found {checked_count}")
        return False  # ← This is where workflow dies
    
    print(f"[PASS] P verification: found {checked_count} completed items")
    return True
```

**Called from**: `sprint_agent.py` line 1019

```python
if verify_phase:
    if not verify_phase("P", sprint_id, repo_root=str(REPO_ROOT)):
        msg = f"[FAIL] P verification failed -- PLAN.md not updated"
        print(msg)
        _gh_comment(issue, repo, f"{msg}")
        sys.exit(1)  # ← Workflow exits here, never reaches story execution
```

### The Flaw

**Design Intent** (from phase_verifier.py docstring):
> "Include phase verification checkpoints... because multi-agent handoffs (Phase 3) are dangerous without per-phase assertion guards."

This was designed for **RESUMING** sprints where:
1. Sprint ran partially before
2. PLAN.md already has entries
3. Verifications ensure previous phases completed before advancing

**Actual Usage** (Issue #39):
1. **BRAND NEW** sprint/batch (never run before)
2. PLAN.md has 1 old [x] mark from previous unrelated work
3. Expects 4 [x] marks for 4 new stories that **don't exist in PLAN.md yet**

**Result**: Verification treats a new sprint start as a resume, expecting work that hasn't begun.

---

## Evidence

### Run 3 Logs (22953448964)

```
[INFO] Sprint agent starting -- issue #39 repo eva-foundry/51-ACA
[INFO] Issue: [SPRINT-004-BATCH-1] Analysis Rules Completion (R-09 to R-12)
[INFO] Branch: sprint/01-batch-1
[PASS] D1 verification: found 121 evidence files  ← D1 passes (old evidence)
[PASS] D2 verification: 121 tests collected       ← D2 passes (existing tests)
[FAIL] P verification: expected 4 [x] marks, found 1  ← P fails (no new work entries)
[FAIL] P verification failed -- PLAN.md not updated
```

### PLAN.md State

**Actual Content**: Has 1 [x] mark from old completed work  
**Expected by Verification**: 4 [x] marks for new stories (ACA-03-019 through ACA-03-022)  
**Reality**: These stories aren't even in PLAN.md yet - they're in the GitHub issue manifest

### SPRINT_MANIFEST (Issue #39 Body)

```json
{
  "sprint_id": "SPRINT-001-BATCH-1",
  "sprint_title": "[SPRINT-004-BATCH-1] Analysis Rules Completion (R-09 to R-12)",
  "target_branch": "sprint/01-batch-1",
  "epic": "ACA-03",
  "stories": [
    {"id": "ACA-03-019", "title": "R-09 DNS Sprawl Detection", ...},
    {"id": "ACA-03-020", "title": "R-10 Savings Plan Coverage", ...},
    {"id": "ACA-03-021", "title": "R-11 APIM Token Budget", ...},
    {"id": "ACA-03-022", "title": "R-12 Chargeback Gap", ...}
  ]
}
```

These stories exist in the manifest but NOT in PLAN.md, so P verification can't find them.

---

## Why This Wasn't Caught Earlier

### Historical Context

**Sprint Agent Usage Pattern** (Sprints 1-13):
1. Stories were MANUALLY added to PLAN.md first
2. Then GitHub issue created referencing existing PLAN.md entries
3. Sprint agent resumed/continued work already tracked in PLAN.md

**New Cloud Agent Pattern** (Issue #39):
1. Stories defined ONLY in issue SPRINT_MANIFEST
2. PLAN.md doesn't have these stories yet
3. Sprint agent expected to create/update PLAN.md during execution
4. But verification runs BEFORE execution, expects entries already exist

**Result**: Old pattern worked (verification found existing entries), new pattern fails (verification expects entries that don't exist yet).

---

## Root Cause Summary

### Primary Root Cause

**Timing Mismatch**: Phase P verification executes at workflow START (before any work) but checks for COMPLETION markers that can only exist after work is done.

### Contributing Factors

1. **Verification Purpose Mismatch**
   - Designed for: Resume protection (don't skip phases)
   - Used for: New sprint validation (no prior state)

2. **Missing State Detection**
   - No differentiation between "new sprint" vs "resume sprint"
   - Same verification logic for both scenarios

3. **Hardcoded Expectations**
   - `expected_checked=4` default doesn't adapt to sprint state
   - No way to signal "this is a new sprint, skip completion checks"

4. **Verification Placement**
   - D1, D2, P all run BEFORE story execution loop
   - Appropriate for D1/D2 (check prerequisites)
   - Inappropriate for P (checks completion of work not yet started)

---

## Impact Assessment

### Immediate Impact

- ❌ **Cloud agent automation blocked** - cannot execute batches via GitHub issues
- ❌ **8-week build plan stalled** - 62% automation (425 FP) unreachable
- ❌ **Manual workaround required** - defeats automation purpose

### Workflow Consequences

**What Works**:
- ✅ Issue creation (create-cloud-agent-issues-8week.ps1)
- ✅ SPRINT_MANIFEST parsing
- ✅ Branch creation
- ✅ Lock acquisition (idempotency)
- ✅ D1/D2 phase verification (evidence, tests)

**What's Blocked**:
- ❌ P phase verification (completion markers before work)
- ❌ Story execution loop (never reached)
- ❌ Code generation (never reached)
- ❌ PR creation (never reached)
- ❌ Evidence recording (never reached)

---

## Solution Options

### Option 1: Skip P Verification for New Sprints (Recommended)

**Implementation**:
```python
# sprint_agent.py line 1015
# Detect if this is a new sprint (no prior state)
state_file = REPO_ROOT / ".eva" / "sprint-state.json"
is_new_sprint = not state_file.exists() or state_file.stat().st_size == 0

if verify_phase and not is_new_sprint:  # Only verify on resume
    if not verify_phase("P", sprint_id, repo_root=str(REPO_ROOT)):
        msg = f"[FAIL] P verification failed -- PLAN.md not updated"
        print(msg)
        _gh_comment(issue, repo, f"{msg}")
        sys.exit(1)
```

**Pros**:
- Minimal code change
- Preserves verification for resume scenarios
- Clear semantic: verify COMPLETION only when resuming

**Cons**:
- Need reliable "new vs resume" detection
- State file might not exist on first run

---

### Option 2: Remove P Verification from Sprint Start

**Implementation**:
```python
# sprint_agent.py line 1015-1021
# REMOVE this block entirely - P verification doesn't make sense at start
```

**Pros**:
- Simplest fix
- P verification at start provides no value (work hasn't begun)
- Aligns with DPDCA: verify AFTER phases, not BEFORE

**Cons**:
- Lose safety check for resume scenarios
- If sprint agent crashes mid-execution, no guard on restart

---

### Option 3: Move P Verification to AFTER Story Execution

**Implementation**:
```python
# sprint_agent.py - move verification to after story loop (line ~1150)
for idx, story in enumerate(stories, 1):
    # ... execute story ...
    results.append(story_result)
    
    # Verify P phase after EACH story
    if verify_phase:
        if not verify_phase("P", sprint_id, repo_root=str(REPO_ROOT)):
            print("[WARN] P verification failed after story execution")
            # Don't exit - continue with remaining stories
```

**Pros**:
- Verification happens when it makes sense (after work completes)
- Incremental validation (per-story, not per-sprint)

**Cons**:
- More complex logic
- Verification must adapt to "how many stories completed so far"
- Requires passing expected_checked dynamically

---

### Option 4: Use skip_checkpoints Flag

**Implementation**:
```python
# sprint_agent.py line 1015
# Add skip_checkpoints parameter to verify_phase
if verify_phase:
    # For new sprints, skip P verification (no prior state to check)
    skip_p = True  # Could make this conditional based on detection
    if not verify_phase("P", sprint_id, skip_checkpoints=skip_p, repo_root=str(REPO_ROOT)):
        msg = f"[FAIL] P verification failed -- PLAN.md not updated"
        print(msg)
        _gh_comment(issue, repo, f"{msg}")
        sys.exit(1)
```

**Pros**:
- Uses existing skip mechanism
- Explicit control over verification behavior

**Cons**:
- Still need to determine when to skip
- Defeats purpose of verification if always skipped

---

## Recommended Solution

### **Hybrid Approach**: Option 1 + Option 3

**Phase 1 (Immediate Fix)**:
Skip P verification at sprint start for NEW sprints only.

**Phase 2 (Proper Fix)**:
Move P verification to AFTER story execution, with adaptive expected_checked.

### Implementation Plan

**Step 1**: Detect sprint state
```python
def is_new_sprint(sprint_id: str, repo_root: Path) -> bool:
    """Check if this sprint has never run before."""
    state_file = repo_root / ".eva" / "sprint-state.json"
    if not state_file.exists():
        return True
    
    try:
        state = json.loads(state_file.read_text())
        return state.get("sprint_id") != sprint_id
    except:
        return True  # Treat errors as new sprint
```

**Step 2**: Conditional verification at start
```python
# Only verify P for RESUME scenarios
if verify_phase and not is_new_sprint(sprint_id, REPO_ROOT):
    if not verify_phase("P", sprint_id, repo_root=str(REPO_ROOT)):
        sys.exit(1)
else:
    print(f"[INFO] Skipping P verification (new sprint: {sprint_id})")
```

**Step 3**: Add verification after story execution
```python
for idx, story in enumerate(stories, 1):
    # ... execute story ...
    
    # Incremental P verification: expect 'idx' completed stories
    if verify_phase:
        verify_p_plan_update(sprint_id, expected_checked=idx, repo_root=str(REPO_ROOT))
        # Don't fail-hard here - continue even if verification fails
```

---

## Validation Plan

### Test Case 1: New Sprint Start
- **Scenario**: Issue #39 (current)
- **Expected**: P verification skipped, stories execute
- **Validation**: PR created with 4 analysis rules

### Test Case 2: Sprint Resume
- **Scenario**: Manually stop workflow, restart same issue
- **Expected**: P verification runs, checks prior work
- **Validation**: Workflow doesn't repeat completed stories

### Test Case 3: Incremental Verification
- **Scenario**: Story 1 completes, verify P expects 1 [x] mark
- **Expected**: Verification passes after each story
- **Validation**: Workflow continues through all 4 stories

---

## Lessons Learned

1. **Verification Timing Matters**: Check prerequisites BEFORE work, check results AFTER work
2. **State Detection Required**: Differentiate "new" vs "resume" to apply appropriate logic
3. **Default Parameters Dangerous**: `expected_checked=4` hardcoded, doesn't adapt to reality
4. **Test New Patterns**: Old workflow pattern (manual PLAN.md) worked, new pattern (issue-only) broke
5. **Fail-Hard Trade-offs**: `sys.exit(1)` prevents bad state but also prevents progress

---

## Action Items

- [ ] **Immediate**: Implement Option 1 (skip P for new sprints)
- [ ] **Short-term**: Test with Issue #39 re-run
- [ ] **Medium-term**: Implement Option 3 (move P verification after execution)
- [ ] **Long-term**: Review all phase verifications for similar timing issues
- [ ] **Documentation**: Update sprint agent docs with "new vs resume" behavior
- [ ] **Monitoring**: Add telemetry for verification pass/fail rates

---

## Appendix: Related Issues

### Data Model API Timeout (Secondary Issue)

**Log Entry**:
```
[WARN] Data model API call failed: GET /model/sprints/51-ACA-sprint-001-batch-1
HTTPSConnectionPool(...marco-eva-data-model...): Read timed out (read timeout=10)
```

**Analysis**: 
- Wrong endpoint (marco-eva-data-model vs msub-eva-data-model)
- Not blocking (graceful degradation)
- Separate fix needed in workflow environment variables

**Not Root Cause**: Sprint fails even if data model succeeds (P verification blocks execution)

---

**Analyzed By**: GitHub Copilot (Agent Mode)  
**Session**: 2026-03-11 Cloud Agent Automation  
**Status**: Root cause identified, solution designed, ready for implementation
