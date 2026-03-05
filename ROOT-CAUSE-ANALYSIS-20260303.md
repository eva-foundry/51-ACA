# ROOT CAUSE ANALYSIS: 51-ACA Data Integrity Issues
**Analysis Date**: 2026-03-03 20:30 UTC  
**Severity**: 🔴 CRITICAL - Multiple Breaking Issues

---

## ROOT CAUSES IDENTIFIED

### RC-1: PLAN.md Has Non-Standard Story Numbering (CRITICAL)

**Problem**: ACA-13 and ACA-14 use non-sequential numbering schemes

**Evidence**:
- **ACA-13**: Starts at `ACA-13-009`, not `ACA-13-001`
  - Contains: ACA-13-009 through ACA-13-019 (11 stories)
  - Missing: ACA-13-001 through ACA-13-008
  - Why? Likely intentional (linking to 13 best-practice rules R-01 through R-11)

- **ACA-14**: Has DUPLICATE story IDs!
  ```
  Old format:  Story 14.5.1 [ACA-14-001] ... EVA-STORY: ACA-14-001
  New format:  Story ACA-14-001 ............. EVA-STORY: ACA-14-001
  Result: TWO different stories with SAME ID
  ```
  - Old WBS format (14.5.1, 14.5.2, 14.5.3...) re-tagged with [ACA-14-001], [ACA-14-002]
  - New canonical format (ACA-14-001, ACA-14-002, ACA-14-003...)
  - Both exist in the file!

**Impact**:
- ✶ Manual counting gives 259 stories (missing the duplicates/overlaps)
- ✶ seed-from-plan.py may deduplicate, giving 268 stories
- ✶ downstream systems inherit this confusion

---

### RC-2: seed-from-plan.py Deduplicates During Parsing (CRITICAL)

**Problem**: `seed-from-plan.py` uses regex patterns that may capture stories differently than manual count

**Evidence**:
```python
STORY_OLD_RE = r"^\s{2,6}Story\s+(\d+)\.(\d+)\.(\d+)(?:\s+\[[A-Z]{2,5}-\d{2}-\d{3}\])?\s{2,}(.+)$"  # OLD format (1.2.3)
STORY_NEW_RE = r"^\s{2,6}Story\s+(ACA-\d{2}-\d{3})\s{2,}(.+)$"                                        # NEW format (ACA-01-001)
```

**Result**:
- Parses ACA-13 as 11 stories (because it starts at -009)
- Parses ACA-14 as 17 stories (both old WBS AND new canonical formats)
- Produces veritas-plan.json with 268 stories

**Why This Matters**:
- PLAN.md is the "source of truth" but it's internally inconsistent
- seed-from-plan.py tries to normalize but creates a different count

---

### RC-3: discovery.json Doesn't Scan Code (HIGH)

**Problem**: discovery.json's "source" is ALL `"veritas-plan.json"`, not actual code artifacts

```json
  "features": [
    {
      "id": "ACA-01",
      "title": "FOUNDATION AND INFRASTRUCTURE",
      "source": "veritas-plan.json"  ← Reading from parsed plan, not code!
    }
  ]
```

**Root Cause**: 
- `discover.js` is just re-reading `veritas-plan.json` instead of scanning code for EVA-STORY tags
- This creates a circular dependency:
  ```
  PLAN.md → seed-from-plan.py → veritas-plan.json
       ↑                              ↓
       └──────── discover.js reads from ──────────
  ```

**Impact**:
- discovery.json is not truly "discovering" - it's just echoing veritas-plan
- Cannot catch discrepancies between planned vs actual code
- Template placeholders (ACA-, ACA-NN-NNN, etc) are never filtered

---

### RC-4: Template Placeholders Leaked Into Data (MEDIUM)

**Problem**: Found in discovery.json gaps:
```json
{
  "type": "orphan_story_tag",
  "story_id": "ACA-",
  "title": null
},
{
  "story_id": "ACA-NN-NNN",  ← Template example from documentation
  "title": null
},
{
  "story_id": "ACA-XX-XXX",  ← Template example from documentation
  "title": null
}
```

**Root Cause**:
- Some code has malformed tags: just `EVA-STORY: ACA-` without numbers
- Or copy-paste of template examples: `# EVA-STORY: ACA-NN-NNN` left in code
- discover.js's orphan detection found these but didn't filter them out

**Files with issues**:
- Likely in comments/docstrings showing examples
- Need to cleanup

---

### RC-5: ACA-03 Story Count Mismatch (HIGH)

**Problem**:
- PLAN.md grep shows: 36 stories
- veritas-plan.json claims: 33 stories  
- Difference: -3 stories

**Root Cause**:
- ACA-03 has subsections (Feature 3.1-3.4)
- Feature 3.4 is "Rule unit tests" with multiple test stories
- Some may be duplicates or named differently than standard format
- seed-from-plan.py's regex may not be capturing all of them

---

### RC-6: ACA-12 Exactly 50% Evidence (SUSPICIOUS)

**Problem**: Evidence metric suspiciously round
- ACA-12: 8/16 stories with evidence = 50.000% (TOO ROUND)

**Root Cause**:
- Could be real (exactly half the stories lack tests)
- Could be placeholder/default data
- gap_count shows 0 but gaps clearly exist
- Requires audit of actual story status

---

### RC-7: Consistency Score Hardcoded to Zero (CRITICAL)

**Problem**: All features show `consistency_score: 0`

**Root Cause**: From reconcile.js code:
```javascript
const consistency_score = checks === 0 ? 0 : Math.max(0, 1 - penalties / checks);
```

- If `checks === 0`: score = 0 (no STATUS entries checked)
- If no `declared_status` in discovery.json: no checks → score = 0
- discovery.json likely has empty `declared_status` object

**Why discovered_status is empty**:
- discover.js extracts from CODE (looking for EVA-STORY tags)
- But it doesn't read STATUS.md to get declared progress
- So `declared_status` stays empty
- Result: consistency_score always 0

---

### RC-8: ADO Map Has Extra Stories (HIGH)

**Problem**: ado-id-map.json has 277 vs reconciliation's 268 vs PLAN's 259

**Root Cause**:
- Some sto stories are duplicated or have variants (ACA-15-009a, ACA-15-012a)
- These are NOT in the canonical PLAN mapping
- Likely added manually for tracking sub-tasks

---

## REMEDIATION PLAN

### Phase 1: CLEAN DATA (NOW)

**1.1 Fix PLAN.md Story Numbering**
- [ ] Normalize ACA-13: Add fictional ACA-13-001 through ACA-13-008 stubs OR
  - [ ] Document why it starts at ACA-13-009
  - [ ] Update comments to clarify intentional numbering
- [ ] Consolidate ACA-14 duplicates:
  - [ ] Remove old WBS format (Story 14.5.1, 14.5.2, etc.)
  - [ ] Keep only canonical ACA-14-001 through ACA-14-017 format
- [ ] Verify ACA-03: Confirm we have exactly 36 stories (not 33)
- [ ] Verify ACA-15: Confirm 13 stories (not missing in reconciliation)

**1.2 Remove Template Placeholders**
- [ ] Search code for `EVA-STORY: ACA-` (incomplete)
- [ ] Search code for `EVA-STORY: ACA-NN-NNN` (template)
- [ ] Search code for `EVA-STORY: ACA-XX-XXX` (template)
- [ ] Fix or delete any malformed tags

**1.3 Rebuild Generation Files**
- [ ] Run seed-from-plan.py to regenerate veritas-plan.json
- [ ] Run discover.js to regenerate discovery.json (should now have proper counts)
- [ ] Run reconcile.js to regenerate reconciliation.json
- [ ] Verify consistency_score is no longer all zeros

### Phase 2: FIX ROOT CAUSES (THIS SPRINT)

**2.1 Enhance discover.js**
- [ ] Make it actually scan code for EVA-STORY tags (not just read veritas-plan)
- [ ] Detect orphan tags (template placeholders)
- [ ] Detect missing tags (stories with code but no EVA-STORY marker)
- [ ] Extract declared_status from STATUS.md to feed into reconciliation

**2.2 Fix reconcile.js**
- [ ] Ensure consistency_score is calculated properly
- [ ] Use declared_status from STATUS.md for consistency metric
- [ ] Add validation: story_count must match within 5% tolerance

**2.3 Add Data Quality Gates**
- [ ] Before writing reconciliation.json:
  - [ ] Check story count delta (error if >5%)
  - [ ] Check for orphan tags (error if found)
  - [ ] Check for zero consistency_score (warning if all zeros)
  - [ ] Mark as "untrustworthy" if failures detected

### Phase 3: REBUILD DATA (NEXT)

After fixes deployed:
- [ ] Regenerate all .eva/*.json files
- [ ] Verify counts match
- [ ] Verify no template placeholders
- [ ] Trust score should stabilize

---

## IMPLEMENTATION STEPS

### Step 1: Fix PLAN.md (Current)

I will:
1. Count ACA-03 stories manually (PLAN says 36, need to verify)
2. Count ACA-14 stories (remove duplicates, keep canonical IDs only)
3. Document why ACA-13 starts at -009 (intentional)
4. Search for and fix template placeholder tags in code

### Step 2: Rebuild .eva Files (Current)

I will:
1. Run seed-from-plan.py --dry-run to see predicted output
2. Run seed-from-plan.py to regenerate veritas-plan.json
3. Run discover.js to regenerate discovery.json
4. Run reconcile.js to regenerate reconciliation.json
5. Run compute-trust.js to generate fresh trust.json

### Step 3: Verify Fixes

I will:
1. Check story counts:
   - PLAN.md: X stories confirmed
   - veritas-plan.json: X stories (should match)  
   - discovery.json: X stories (should match)
   - reconciliation.json: X stories (should match)
   - ado-id-map.json: Cleaned of duplicates
2. Check consistency_score: Should NO LONGER all be 0
3. Check trust.json: Should be > 70 and stable
4. Verify no template placeholders in data

---

## Expected Outcomes

### Before Fix
```
PLAN.md           259 stories (with double-counting issues)
veritas-plan.json 268 stories (seed-from-plan.py normalized)
discovery.json    268 stories (echo of veritas-plan)
reconciliation.json 268 stories
ado-id-map.json   277 stories (includes variants)
consistency_score ALL 0.0
trust.json score  69/100
```

### After Fix
```
PLAN.md           270 stories (consistent, properly deduplicated)
veritas-plan.json 270 stories (matches PLAN.md)
discovery.json    270 stories (from actual code scan)
reconciliation.json 270 stories
ado-id-map.json   270 stories (cleaned, 1:1 mapping)
consistency_score 0.95+ (from STATUS.md alignment)
trust.json score  85+/100 (coverage 100%, evidence ~97%, consistency ~95%)
```

---

**STATUS**: Ready for implementation  
**COMMITS NEEDED**: 1-2 (fix PLAN.md naming, regenerate files)  
**RISK**: Low (PLAN.md is source of truth, regeneration is deterministic)
