# 51-ACA Workflow Data Quality Dashboard
**Analysis Date**: 2026-03-03 20:05 UTC  
**Scope**: Data flow integrity through 4 workflow layers

---

## QUICK FINDINGS

### Story Count Contradiction
```
SOURCE (PLAN.md):      259 stories ✓ Verified
CAPTURED (Reconcile):  268 stories → +9 (INFLATED)
INTEGRATED (ADO-map):  277 stories → +18 (SEVERELY INFLATED)
MISMATCH:              ±18 story variance (7% error rate)
```

### Data Flow Layer-by-Layer

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: SOURCE (PLAN.md)                                       │
├─────────────────────────────────────────────────────────────────┤
│ Input:   Human-authored epic/feature/story plan                │
│ Output:  259 story IDs [ACA-NN-NNN] tagged in markdown         │
│ Quality: ✅ Self-consistent, counts verified by regex (⬇️ PASS)  │
│                                                                  │
│ Per-Epic Breakdown:                                            │
│   ACA-01: 21 ✓    ACA-08: 14 ✓    ACA-15: 13 ✓               │
│   ACA-02: 17 ✓    ACA-09: 18 ✓                                │
│   ACA-03: 36 ✓    ACA-10: 15 ✓    ACA-13: 0 (not in plan)    │
│   ACA-04: 28 ✓    ACA-11:  9 ✓    ACA-14: 3 (only)           │
│   ACA-05: 42 ✓    ACA-12: 16 ✓                                │
│   ACA-06: 18 ✓    ACA-07:  9 ✓                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: DISCOVER (discovery.json)                             │
├─────────────────────────────────────────────────────────────────┤
│ Input:   PLAN.md + code artifacts with EVA-STORY tags         │
│ Output:  Feature list + gap detection                          │
│ Quality: ⚠️  Issues detected (⬇️ PROBLEMS)                      │
│                                                                  │
│ Issues:                                                         │
│  • All 14 features source="veritas-plan.json" (circular!)      │
│  • No independent code scanning evidence                        │
│  • Gap tags include templates: "ACA-", "ACA-NN-NNN", "ACA-XX" │
│  • Plans for ACA-13 & ACA-14 not explained                    │
│                                                                  │
│ Action: Verify if veritas actually scans code or just parses  │
│         PLAN.md                                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: RECONCILE (reconciliation.json)                       │
├─────────────────────────────────────────────────────────────────┤
│ Input:   PLAN.md + discovery.json                             │
│ Output:  Per-feature metrics (stories, artifacts, evidence)   │
│ Quality: 🔴 CRITICAL ISSUES (⬇️ MAJOR PROBLEMS)                │
│                                                                  │
│ ❌ Hallucinated Stories:                                        │
│    • ACA-13: PLAN has 0, Reconcile claims 11 (+11 phantom)   │
│    • ACA-14: PLAN has 3, Reconcile claims 17 (+14 phantom)   │
│                                                                  │
│ ❌ Missing Stories:                                             │
│    • ACA-03: PLAN has 36, Reconcile claims 33 (-3)           │
│    • ACA-15: PLAN has 13, Reconcile has 0 (-13)              │
│                                                                  │
│ ❌ Metrics Issues:                                              │
│    • consistency_score = 0 for ALL features (mathematically   │
│      impossible with 97% evidence; should be ~97%)             │
│    • gap_count = 0 for all (but gaps clearly exist)           │
│                                                                  │
│ 📊 Story Count: 268 vs PLAN 259 → +9 INFLATED                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: INTEGRATE (ado-id-map.json)                           │
├─────────────────────────────────────────────────────────────────┤
│ Input:   Reconciliation story list                             │
│ Output:  Story_ID → ADO_WorkItem_ID mapping                   │
│ Quality: 🔴 CRITICAL INCONSISTENCIES (⬇️ SEVERE PROBLEMS)      │
│                                                                  │
│ 📊 Story Count: 277 vs Reconcile 268 → +9 FURTHER INFLATED   │
│                  vs PLAN 259 → +18 vs source (7% error)       │
│                                                                  │
│ ❌ Missing from ADO:                                            │
│    • ACA-12: Has 16 in PLAN, only 10 in ADO (-6)             │
│    • ACA-03: Has 36 in PLAN, only 33 in ADO (-3)             │
│                                                                  │
│ ❌ Extra in ADO:                                                │
│    • ACA-07: Has 9 in PLAN, 10 in ADO (+1)                   │
│    • ACA-13: Has 0 in PLAN, 11 in ADO (+11)                  │
│    • ACA-14: Has 3 in PLAN, up to 14 in ADO (+11)            │
│    • ACA-15: Has 13 in PLAN, 21 in ADO (+8, with variants)  │
│                                                                  │
│ ❌ Non-Standard Entries:                                        │
│    • ACA-15-009a, ACA-15-012a (variant markers)              │
│    • Starting at ACA-13-009 (not -001)                        │
│                                                                  │
│ ⚠️  Gap: 6 stories from ACA-12 missing (ACA-12-009 to -016)   │
│    Are they in code but unmapped? Or phantom in Reconcile?    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 5: VISIBILITY (STATUS.md + trust.json)                   │
├─────────────────────────────────────────────────────────────────┤
│ Input:   ADO + Reconciliation metrics                          │
│ Output:  Executive metrics & dashboard data                    │
│ Quality: 🟡 UNRELIABLE (downstream of poisoned data)           │
│                                                                  │
│ Current Metrics:                                               │
│  • Stories: 268 claimed (should be 259 from PLAN)             │
│  • Evidence: 260/268 = 97% (inflated denominator)             │
│  • True evidence: 260/259 = 100.4% (impossible!)              │
│  • MTI: 69/100 (formula correct, inputs corrupted)            │
│                                                                  │
│ When Corrected (using PLAN as truth):                          │
│  • Stories: 259 (true count)                                   │
│  • Evidence: 260/259 would need recount from code             │
│  • Expected MTI: 70+ (if 260/259 or close to it)             │
│                                                                  │
│ ⚠️  All executive reports using these metrics are SUSPECT      │
└─────────────────────────────────────────────────────────────────┘
```

---

## HALLUCINATION EVIDENCE

### Template Placeholders Found in Data
```json
gap_tags in discovery.json:
  1. "ACA-"       ← Incomplete (missing epic-story)
  2. "ACA-NN-NNN" ← Template example (should not be real)
  3. "ACA-XX-XXX" ← Template example (should not be real)
  4. "ACA-12-023" ← Real orphan (ACA-12 only has 16, not 23)
```

**Where did these come from?**
- Likely copy-pasted from documentation or code comments
- Suggests veritas is not properly filtering template strings
- Data quality issue: Junk data in gap detection

### Phantom Epics
```
ACA-13 Analysis:
  PLAN.md: Does not exist (0 stories) ✓ Verified
  Discovery: Not mentioned
  Reconciliation: Claims 11 stories (!)
  ADO map: Has 11 entries (ACA-13-009 through ACA-13-019)
  → VERDICT: Phantom epic, likely seeded by error
  
ACA-14 Analysis:
  PLAN.md: 3 stories (ACA-14-001, 002, 003) ✓ Verified
  Reconciliation: Claims 17 stories
  ADO map: Has 10-14 stories
  → VERDICT: Reconcile added 14 phantom stories
```

---

## ROUND NUMBER ANOMALIES

| Metric | Value | Suspicion | Explanation |
|--------|-------|-----------|------------|
| ACA-12 evidence | 8/16 = 50% | 🔴 HIGH | Perfect 50% too round |
| Stories per epic | 21,17,36,28,42,18,9,14,18,15,9,16,0,3,13 | 🟡 MED | Most divisible by 3-7 |
| Consistency score | 0, 0, 0, ... (ALL) | 🔴 CRITICAL | Uniform = broken metric |
| MTI values | 70,70,70...60,70 | 🟡 MED | 13 identical, 1 exception |
| gap_count | 0, 0, 0, ... (ALL) | 🔴 CRITICAL | All zero but gaps exist |
| Trust score drop | 100→70 exact | 🟡 MED | Large, round number (-30) |

---

## COUNTING VERIFICATION MATRIX

| Epic | PLAN | Discovery | Reconcile | ADO-Map | Status | Notes |
|------|------|-----------|-----------|---------|--------|-------|
| 01 | 21 | ? | 21 | 21 | ✅ | Consistent |
| 02 | 17 | ? | 17 | 17 | ✅ | Consistent |
| 03 | 36 | ? | 33 | 33 | 🔴 | -3 from PLAN |
| 04 | 28 | ? | 28 | 28 | ✅ | Consistent |
| 05 | 42 | ? | 42 | 42 | ✅ | Consistent |
| 06 | 18 | ? | 18 | 18 | ✅ | Consistent |
| 07 | 9 | ? | 9 | **10** | 🔴 | +1 in ADO |
| 08 | 14 | ? | 14 | 14 | ✅ | Consistent |
| 09 | 18 | ? | 18 | 18 | ✅ | Consistent |
| 10 | 15 | ? | 15 | 15 | ✅ | Consistent |
| 11 | 9 | ? | 9 | 9 | ✅ | Consistent |
| 12 | 16 | ? | 16 | **10** | 🔴 | -6 in ADO |
| 13 | **0** | ? | **11** | **11** | 🔴 | Phantom +11 |
| 14 | **3** | ? | **17** | **10-14** | 🔴 | Phantom +14 |
| 15 | **13** | ? | **0** | **21** | 🔴 | Missing -13 from Reconcile |
| **TOTAL** | **259** | **?** | **268** | **277** | 🔴 | ±18 variance |

---

## DRIFT ANALYSIS: Why Did Trust Score Drop 30 Points?

```
Trust Score History:
  2026-02-27 17:33:13 → 100 ← Bootstrap (Coverage only?)
  2026-02-27 18:41:51 → 100 ← Stable
  2026-02-27 18:42:09 → 100 ← Stable (3 minutes later)
  
  2026-03-01 13:12:35 → 70  ← MAJOR DROP (-30 points)
                             Changed likely: Formula update
                             Consistency scoring activated
                             
  2026-03-01 14:26:04 → 70  ← Stabilized here
  2026-03-01 14:59:52 → 70
  2026-03-02 14:44:19 → 70
  2026-03-02 14:49:42 → 69  ← Minor adjustment (-1)
  2026-03-02 14:50:21 → 69
  2026-03-02 17:04:02 → 69  ← Current
```

**Timeline Analysis**:
- **Feb 27**: Initial calculation (before Reconciliation had errors?)
  - Coverage = 1.0, consistency_score = (not computed)
  - Reported as 100: Likely dividing by denominator of 1.0?
  
- **Mar 01 morning**: Reconciliation ran, data inflated
  - Added phantom stories
  - consistency_score still broken (0)
  - New formula: (1.0 * 0.50) + (0.97 * 0.20) + (0 * 0.30) = 0.694 → 69-70
  
- **Mar 02**: Additional data quality checks ran
  - Score refined from 70 → 69 (minor variations)
  - Data now considered "stable" despite inconsistencies

---

## REMEDIATION ROADMAP

### Phase 1: QUARANTINE (Immediate)
```
⏸️  Pause any executive reporting using these metrics
📝 Mark metrics as "Under Review - Do Not Use"
🚨 Alert scrum master: Data integrity issue detected
```

### Phase 2: VALIDATE (This Sprint)
```
1️⃣  Manually verify ACA-13 & ACA-14 existence
    - Do these epics exist in actual code/plan?
    - If no: Mark as erroneous
    
2️⃣  Recount all stories from PLAN.md
    - Use PLAN as source of truth
    - Verify each [ACA-NN-NNN] against actual content
    
3️⃣  Audit code artifacts
    - Scan for actual EVA-STORY tags
    - Does project really have 260 stories with evidence?
    - Or is reconciliation lying?
    
4️⃣  Check reconciliation.json generator
    - Who/what creates this file?
    - Is it regenerated or static?
    - Verify the logic
```

### Phase 3: REBUILD (Next Sprint)
```
1️⃣  Regenerate reconciliation.json from clean PLAN.md
    
2️⃣  Rescan code for actual EVA-STORY tags
    - Count real artifacts
    
3️⃣  Rebuild ado-id-map.json
    - Remove phantom stories
    - Add missing stories
    - Normalize variants
    
4️⃣  Recalculate trust.json
    - Fix consistency_score (should not be 0!)
    - Recompute MTI with clean data
```

### Phase 4: MONITOR (Ongoing)
```
1️⃣  Add data quality gates
    - Flag story count drift > 5%
    - Require manual review if drift > 10%
    
2️⃣  Version control reconciliation
    - Audit trail of changes
    - Know WHO changed what WHEN
    
3️⃣  Weekly data quality report
    - Check for new anomalies
    - Verify consistency_score is reasonable
```

---

## EVIDENCE SUMMARY

**Data Quality Scorecard**:

| Layer | Quality | Issues | Confidence |
|-------|---------|--------|-----------|
| PLAN.md (Source) | ✅ Good | None detected | 95% |
| Discovery | ⚠️ Fair | Circular refs, templates | 60% |
| Reconciliation | 🔴 Poor | +9 phantom, broken metrics | 30% |
| ADO Map | 🔴 Poor | +18 vs source, variants | 25% |
| Visibility | 🔴 Poor | Downstream of bad data | 20% |
| **Overall** | **🔴 POOR** | **±18 story variance** | **25%** |

---

**CRITICAL ATTESTATION**:

> "51-ACA's workflow has good intentions but poor execution. The source (PLAN.md) is solid. The automated sync layers (veritas → reconciliation → ADO) are BROKEN. Do not use current metrics for executive reporting until data is cleaned. Estimated effort to fix: 8-16 story points. Impact if not fixed: All metrics untrustworthy."

---

**Report**: [DATA-QUALITY-FORENSICS-20260303.md](DATA-QUALITY-FORENSICS-20260303.md)  
**Generated**: 2026-03-03 20:05 UTC
