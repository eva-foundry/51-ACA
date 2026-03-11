# 51-ACA Veritas Consistency Audit -- Issues Found

**Audit Date**: March 2, 2026, 14:44 UTC  
**Veritas Score**: 70/100 (was 100, regressed due to consistency=0)  
**Status**: ⚠️ CONSISTENCY BROKEN - Fixable within 15 minutes

---

## Findings Summary

**Coverage**: ✅ PASS (257 stories, 769 artifacts, 100% evidence)  
**Evidence**: ✅ PASS (all 14 epics documented)  
**Consistency**: ❌ FAIL (score=0) -- Story IDs in code don't match PLAN.md structure

---

## Root Cause: TWO Orphan Story ID Series

### Issue 1: ACA-13-002 through 008 (Infrastructure Cosmos Containers)

**Location**: `infra/phase1-marco/main.bicep` lines 2-8  
**Current IDs**: ACA-13-002, 003, 004, 005, 006, 007, 008  
**Problem**: 
- These IDs ARE in PLAN.md "Story ID Roster" (line 719-726)
- But they're NOT explicitly defined as story features in Epic 13 section
- veritas-plan.json doesn't know about them (PLAN.md only lists ACA-13-009 onwards in Epic 13)
- So veritas audit flags them as orphans

**Files Affected**:
```
infra/phase1-marco/main.bicep (lines 2-8)
PLAN.md (lines 719-726 list them but Epic 13 section doesn't)
```

**Story Details**:
- ACA-13-001: Cosmos DB aca-db + scans container
- ACA-13-002: inventories container
- ACA-13-003: cost-data container
- ACA-13-004: advisor container
- ACA-13-005: findings container
- ACA-13-006: APIM ACA product + subscription policy
- ACA-13-007: Key Vault secrets wiring
- ACA-13-008: Container App Job definitions

---

### Issue 2: ACA-INFRA-001 through 008 (WRONG ID FORMAT)

**Location**: `infra/phase2-private/main.tf` lines 1-6  
**Current IDs**: ACA-INFRA-001, 002, 003, 004, 005, 006, 007, 008  
**Problem**:
- Using wrong ID format (should be ACA-11-* for Epic 11: Phase 2 Infrastructure)
- veritas correctly flags these as orphans (not in any ACA-NN-NNN pattern)
- Corresponds to Epic 11 stories that should be: ACA-11-001 through 008

**Files Affected**:
```
infra/phase2-private/main.tf (lines 1-6)
```

**Story IDs Should Be**: ACA-11-001 through ACA-11-008  
**These Correspond to Epic 11**: Phase 2 Infrastructure (PLAN.md lines 630+)

---

## Fix Strategy (3 Steps)

### Step 1: Fix ACA-INFRA Tags → ACA-11 Format

**File**: `infra/phase2-private/main.tf`

Replace lines 1-8:
```
# EVA-STORY: ACA-INFRA-001    →  # EVA-STORY: ACA-11-001
# EVA-STORY: ACA-INFRA-002    →  # EVA-STORY: ACA-11-002
# EVA-STORY: ACA-INFRA-003    →  # EVA-STORY: ACA-11-003
# EVA-STORY: ACA-INFRA-004    →  # EVA-STORY: ACA-11-004
# EVA-STORY: ACA-INFRA-005    →  # EVA-STORY: ACA-11-005
# EVA-STORY: ACA-INFRA-006    →  # EVA-STORY: ACA-11-006
# EVA-STORY: ACA-INFRA-007    →  # EVA-STORY: ACA-11-007
# EVA-STORY: ACA-INFRA-008    →  # EVA-STORY: ACA-11-008
```

### Step 2: Legitimize ACA-13-001 through 008

**Option A - Recommended**: Move them to Epic 12 (Data Model Support)
- These are infrastructure/system stories, not "best practices rules"
- Epic 12 is "Data Model Support (runtime)" - better fit
- Rename to: ACA-12-009 through ACA-12-016
- Update PLAN.md Epic 12 Features section
- Update main.bicep comment tags

**Option B**: Create explicit Epic 13 Features for them
- Add Feature 13.0 "Core Infrastructure Containers" to PLAN.md
- Keep as ACA-13-001 through 008
- Document in PLAN.md Features section

**Recommended**: Option A (cleaner categorization)

### Step 3: Regenerate Veritas Plan

After fixing Option A:
```powershell
# Seed updated PLAN.md into veritas-plan.json
python .github/scripts/aca-seed-plan.py --reseed

# Re-run audit
node C:\eva-foundry\48-eva-veritas\src\cli.js audit --repo C:\eva-foundry\51-ACA

# Verify: consistency_score should be 1.0, MTI should jump back to 100
```

---

## Why Consistency Score = 0

Formula: `MTI = coverage*0.5 + evidence*0.2 + consistency*0.3`
- Coverage: 1.0 (257/257 stories have artifacts)
- Evidence: 1.0 (257/257 stories have evidence)
- Consistency: 0.0 (18 orphan story tags found in code, not in veritas-plan.json)

**Result**: MTI = 1.0*0.5 + 1.0*0.2 + 0.0*0.3 = **0.7 = 70%**

Once consistency=1.0, MTI = **100%**

---

## Data Model Consistency Check

The data model API's `/model/agent-summary` is currently returning empty (network issue on cosmos). After the fix:

```
POST /model/admin/commit should execute:
- Export all 257 stories from veritas-plan.json
- Update .eva/discovery.json
- Update .eva/reconciliation.json
- Verify no cross-reference violations
```

If data model has stories recorded but PLAN.md was out of sync, commit will catch it.

---

## Documentation Files That Reference Wrong IDs

These files need updates after the fix:

1. **AUTOMATION-INFRASTRUCTURE-INVENTORY.md** (I just created this)
   - Line references ACA-13-002 through 008
   - Will auto-correct once PLAN.md is fixed

2. **LOCAL-BASELINE-SPRINTS-13-18.md**
   - Template IDs: ACA-NN-NNN (placeholders, not errors)
   - No action needed

3. **ado-artifacts.json** / **ado-artifacts-full.json**
   - Generated from ADO import
   - Will auto-sync once Azure DevOps WBS is updated

---

## Implementation Order

1. **Fix infra/phase2-private/main.tf** (ACA-INFRA → ACA-11)
   - 2 minutes, 8 replacements
   - Low risk

2. **Choose Option A or B for ACA-13-001 through 008**
   - **Option A** (Recommended): Move to ACA-12-009 onwards
     - Update PLAN.md Epic 12 Features
     - Update main.bicep tags
     - 10 minutes, higher impact but cleaner
   
   - **Option B**: Explicit Epic 13 Features
     - Add Feature 13.0 to PLAN.md
     - 5 minutes, minimal changes

3. **Regenerate and Verify**
   - Reseed veritas-plan.json
   - Run audit
   - Verify MTI = 100
   - 3 minutes

**Total Time**: 15-20 minutes  
**Risk Level**: Low (all changes are documentation/config, no code behavior changes)

---

## Commit Message Template

```
fix(51-ACA): reconcile orphan story IDs with veritas-plan; restore MTI=100

- Fix ACA-INFRA-* tags in Phase 2 infra to correct format (ACA-11-*)
- Move Cosmos container stories to Epic 12 (Option A) [ACA-13-001..008 → ACA-12-009..016]
- Update PLAN.md Epic 12/13 features sections
- Reseed veritas-plan.json from corrected PLAN.md
- Verify consistency_score=1.0, MTI returns to 100

Closes: Veritas audit consistency=0 regression
EVA-STORY: ACA-14-001 (data model consistency)
```

---

## Before & After Comparison

### BEFORE (Current State)
```
Coverage:     1.0 ✅
Evidence:     1.0 ✅
Consistency:  0.0 ❌ (18 orphan story tags)
MTI Score:    70 ⚠️
Actions:      test, review, merge-with-approval
```

### AFTER (Expected state after fix)
```
Coverage:     1.0 ✅
Evidence:     1.0 ✅
Consistency:  1.0 ✅ (all code IDs match PLAN.md)
MTI Score:    100 ✅
Actions:      merge (no approval needed)
```

---

## Next Steps (When Ready)

1. Confirm Option A vs B choice
2. Apply fixes to:
   - `infra/phase2-private/main.tf` (ALL: fix ACA-INFRA tags)
   - `infra/phase1-marco/main.bicep` (Option A: rename tags)
   - `PLAN.md` (ALL: update Epic sections)
3. Regenerate veritas-plan.json
4. Run audit to verify
5. Commit + push
6. Verify data model sync

---

**Status**: Ready to fix. Awaiting confirmation on Option A vs B.

**User**: When you're ready, reply with:
- `"fix: option A"` to move containers to Epic 12
- `"fix: option B"` to keep in Epic 13 with Features
- Or I can implement both for you to choose

