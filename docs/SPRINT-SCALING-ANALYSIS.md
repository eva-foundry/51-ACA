# Sprint Scaling Analysis -- ACA DPDCA Agent Performance

**Version**: 1.0.0
**Updated**: 2026-03-01
**Project**: 51-ACA -- Azure Cost Advisor
**Path**: `C:\eva-foundry\51-ACA\`

---

## Executive Summary

Sprint 12 completed **3 stories with real code artifacts** (Azure OpenAI fallback + Evidence validation).
Sprint 13-16 manifests created to observe **gradual scaling** from **4 to 7 stories** per sprint.

⚠️ **IMPORTANT**: Sprint 12 timing data (2.2 hours) is **estimated**, not measured. Actual wall-clock execution time will be collected starting from Sprint 13 when the sprint_agent.py is actually executed.

### Key Findings (Subject to Revision on Real Data)

- **Sprint 12 Baseline**: ~2.2 hours estimate (code verified, timing unverified)
- **Scaling Strategy**: Add 1 story per sprint (Sprint 13-16)
- **Predicted Peak**: Sprint 16 at 7 stories, 21 FP, ~4.3 hours (estimates only)
- **Optimal Range**: 5-6 stories, 15-18 FP, 3-4 hours (based on heuristics, not measured data)

---

## Execution Time Data

### Sprint 12 (ESTIMATED - Not Measured)

**Stories**: 3 (ACA-14-008, ACA-14-009, ACA-14-010)
**Total FP**: 9
**Total Duration**: ~2.2 hours (130 minutes) **[ESTIMATED]**
**Real Status**: ✅ Code delivered, ❌ Timing unverified (sprint_agent.py not executed)

| Story | Description | Est. Duration | Reason | Files | Status |
|-------|-------------|---|-------------|-------|--------|
| ACA-14-008 | GitHub Models API | ~10 min | Verification only (already done Sprint 3) | 0 | ✅ Code verified |
| ACA-14-009 | Azure OpenAI fallback | ~70 min | 3-tier provider selection logic | 1 | ✅ Implemented, timing est. |
| ACA-14-010 | Evidence validation | ~60 min | Schema validator + integration | 2 | ✅ Implemented, timing est. |

**⚠️ Timing Clarification**:
- Duration figures (70 min, 60 min) are **estimates** based on code complexity, not wall-clock measurements
- Evidence receipts ACA-14-009 and ACA-14-010 contain `duration_ms` placeholder values
- No actual `time.time()` measurements were taken during implementation
- This was a **design session**, not an **execution session**

**What's Real (Verified)**:
- ✅ 8 files created/modified (2 new Python modules, 1 seed function, schema validator, etc.)
- ✅ ~400+ lines of production code written
- ✅ Sprint 12 stories marked DONE in PLAN.md
- ✅ All changes committed to GitHub (commit 6449ea2)
- ✅ Data model updated with evidence layer (31 receipts imported)

**What's Estimated (Not Yet Measured)**:
- ❌ Wall-clock execution time: Placeholder values in receipts
- ❌ LLM token usage: Extrapolated from code size, not from actual API responses
- ❌ Test coverage improvement: No actual pytest runs

**Real Data Collection Plan**:
When Sprint 13 executes, sprint_agent.py will:
1. Record actual `start_time` and `end_time` via `datetime.now()`
2. Measure actual token usage from Azure OpenAI API responses
3. Run pytest and record `test_count_before` / `test_count_after`
4. Write evidence receipt with **measured** values
5. Populate duration_ms with real wall-clock time (not estimates)

---

## Sprint Scaling Projections

⚠️ **DATA STATUS**: All Sprint 13-16 projections below are **ESTIMATES** based on heuristics, not measured data.
Once Sprint 13 executes and real timing data is collected, these projections will be **recalibrated with actual metrics**.

### Sprint 13: Analysis Rules Final (4 stories, 12 FP)

**Status**: Manifest created, awaiting execution
**Target**: Complete 12/12 rule coverage (R-09 through R-12)
**Estimated Duration**: ~2.7 hours (160 minutes) **[ESTIMATE]**

| Story | Rule | Estimated Time | Model | Size |
|-------|------|----------------|-------|------|
| ACA-03-019 | R-09 DNS Sprawl | 35 min est. | gpt-4o-mini | S=3 FP |
| ACA-03-020 | R-10 Savings Plan | 40 min est. | gpt-4o-mini | S=3 FP |
| ACA-03-021 | R-11 APIM Token Budget | 35 min est. | gpt-4o-mini | S=3 FP |
| ACA-03-022 | R-12 Chargeback Gap | 35 min est. | gpt-4o-mini | S=3 FP |

**Estimated Efficiency** (subject to revision):
- **Time per FP**: 13.5 minutes (assumes -10% from Sprint 12 baseline with pattern learning)
- **Time per story**: 40 minutes (assumes -9% improvement)
- **Tokens per FP**: ~1,500 (gpt-4o-mini cheaper than gpt-4o)

**CRITICAL TEST**: Sprint 13 execution will validate whether the -10% efficiency improvement assumption is realistic.

---

### Sprint 14: Rule Tests Batch 1 (5 stories, 15 FP)

**Status**: Manifest created
**Target**: Test coverage for R-01 through R-05
**Estimated Duration**: ~3.1 hours (185 minutes) **[ESTIMATE]**

**Scaling Impact**: +1 story (+25% FP), estimated +0.4 hours vs Sprint 13

**Estimated Efficiency** (subject to revision):
- **Time per FP**: 12.3 minutes (assumes -18% from Sprint 12, test pattern repetition benefit)
- **Time per story**: 37 minutes (assumes -16% improvement)

---

---

### Sprint 15: Rule Tests Batch 2 (6 stories, 18 FP)

**Status**: Manifest created
**Target**: Test coverage for R-06 through R-11
**Estimated Duration**: 3.7 hours (225 minutes)

**Scaling Impact**: +1 story (+20% FP), +0.6 hours (+19% time)

**Projected Efficiency:**
- **Time per FP**: 12.5 minutes (stable)
- **Time per story**: 37.5 minutes (stable)

---

### Sprint 16: Rule Tests Final (7 stories, 21 FP)

**Status**: Manifest created
**Target**: Negative tests, edge cases, integration, CI gate
**Estimated Duration**: 4.3 hours (260 minutes)

**Scaling Impact**: +1 story (+17% FP), +0.6 hours (+16% time)

**Projected Efficiency:**
- **Time per FP**: 12.4 minutes (stable)
- **Time per story**: 37 minutes (stable)

**Story Mix**:
- 4 simple (S=3 FP each): 35 min each = 140 min
- 3 medium (M=2-5 FP): 50-60 min each = 160 min

---

## Scaling Analysis

### Growth Rate (Sprint 12-16)

| Metric | Sprint 12 | Sprint 13 | Sprint 14 | Sprint 15 | Sprint 16 | Trend |
|--------|-----------|-----------|-----------|-----------|-----------|-------|
| Stories | 3 | 4 (+33%) | 5 (+25%) | 6 (+20%) | 7 (+17%) | Moderating |
| FP | 9 | 12 (+33%) | 15 (+25%) | 18 (+20%) | 21 (+17%) | Moderating |
| Hours | 2.2 | 2.7 (+23%) | 3.1 (+15%) | 3.7 (+19%) | 4.3 (+16%) | Sub-linear |
| Min/FP | 15 | 13.5 (-10%) | 12.3 (-9%) | 12.5 (+2%) | 12.4 (-1%) | Stabilizing |

**Key Observations**:
1. **FP growth moderating**: +33% → +25% → +20% → +17% (sustainable)
2. **Time scaling sub-linear**: Execution time grows slower than FP count (efficiency gains)
3. **Efficiency stabilizing**: Min/FP converges to ~12-13 minutes after pattern learning
4. **Story count peak**: 7 stories (Sprint 16) recommended as maximum for sustainable velocity

---

### Velocity Trajectory

```
FP Delivered per Sprint
25 |                                     * (Sprint 16: 21 FP)
20 |                              * (Sprint 15: 18 FP)
15 |                       * (Sprint 14: 15 FP)
10 |         * (Sprint 12: 9 FP)  * (Sprint 13: 12 FP)
 5 |
 0 +----+----+----+----+----+----+----+----+----+----+
   11   12   13   14   15   16   17   18   19   20

Execution Time per Sprint
5h |                                     * (Sprint 16: 4.3h)
4h |                              * (Sprint 15: 3.7h)
3h |                       * (Sprint 14: 3.1h)
   |              * (Sprint 13: 2.7h)
2h |    * (Sprint 12: 2.2h)
1h |
0h +----+----+----+----+----+----+----+----+----+----+
   11   12   13   14   15   16   17   18   19   20
```

---

## Token Usage Analysis

### Sprint 12 Token Breakdown

| Story | Model | Tokens (Input + Output) | Cost (GitHub Models) |
|-------|-------|-------------------------|----------------------|
| ACA-14-009 | gpt-4o via GitHub | ~8,450 | $0.00 (free tier) |
| ACA-14-010 | gpt-4o via GitHub | ~7,200 | $0.00 (free tier) |
| **Total** | - | **15,650** | **$0.00** |

**With Azure OpenAI Fallback** (if GitHub Models unavailable):
- gpt-4o pricing: $2.50/1M input + $10.00/1M output
- Estimated cost per Sprint 12: ~$0.15 (15k tokens × avg $10/1M)
- Annual cost at 2 sprints/month: ~$3.60/year (negligible)

### Projected Sprint 13-16 Token Usage

| Sprint | Stories | FP | Estimated Tokens | Cost (Azure OpenAI) |
|--------|---------|----|-----------------|-|
| Sprint 13 | 4 | 12 | ~18,000 | $0.18 |
| Sprint 14 | 5 | 15 | ~22,500 | $0.22 |
| Sprint 15 | 6 | 18 | ~27,000 | $0.27 |
| Sprint 16 | 7 | 21 | ~31,500 | $0.31 |

**Total Sprint 12-16**: ~115,000 tokens, ~$1.15 (Azure OpenAI), $0.00 (GitHub Models)

---

## Optimal Sprint Size Recommendation

### Constraints

1. **Weekly sprint cadence**: 5 business days = 40 hours team capacity
2. **Agent execution time**: 3-4 hours optimal (leaves buffer for reviews, fixes)
3. **Story complexity mix**: 70% simple (S), 20% medium (M), 10% large (L)
4. **Human review overhead**: ~1 hour per sprint (plan review + PR approval)

### Recommended Target

**5-6 stories, 15-18 FP, 3-4 hours execution time**

**Rationale**:
- **Sprint 14-15 range** shows best balance: high throughput, stable efficiency, manageable review load
- **Sub-4-hour execution** leaves buffer for:
  - PR review and feedback: ~1 hour
  - Bug fixes and rework: ~1-2 hours
  - Sprint planning and retro: ~0.5 hours
- **18 FP per week** = **936 FP per year** (52 weeks) = **~94 person-weeks** (10 FP/week baseline)

### Anti-Patterns to Avoid

1. **Too small** (< 3 stories): Under-utilizes agent, high overhead per story
2. **Too large** (> 8 stories): Review bottleneck, increased failure risk, diminishing returns
3. **Variable size**: Makes velocity prediction difficult, disrupts flow

---

## Next Steps

### Immediate (Sprint 13 Execution)

1. **Trigger Sprint 13** via GitHub Issue with manifest body
2. **Monitor execution time**:
   - Target: < 3 hours (160 minutes)
   - Track: duration_ms in evidence receipts
   - Compare: actual vs projected 2.7 hours
3. **Collect metrics**:
   - Tokens used per story
   - Files changed per story
   - Test count added (if any)

### Short-term (Sprint 14-16 Execution)

1. **Execute Sprint 14-16** in sequence
2. **Validate scaling hypothesis**:
   - Does efficiency stabilize at ~12 min/FP?
   - Does 7-story sprint stay under 5 hours?
   - Does token usage scale linearly with FP?
3. **Adjust sprint size** based on data:
   - If Sprint 16 > 5 hours: cap at 6 stories
   - If Sprint 15 < 3 hours: try 7-story sprint sooner

### Long-term (Epic 4 & Beyond)

1. **Apply learned velocity** to Epic 4 (API) and Epic 2 (Collector)
2. **Target cadence**: 2 sprints per week × 15 FP = 30 FP per week
3. **Annual throughput**: 30 FP/week × 48 weeks = 1,440 FP/year
4. **Phase 1 completion**: ~200 FP remaining ÷ 30 FP/week = 7 weeks (mid-April 2026)

---

## Risk Factors

### Execution Time Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GitHub Models rate limit | Medium | High | Azure OpenAI fallback (ACA-14-009) |
| Complex story blocks sprint | Low | High | Break down L stories into M+S stories |
| Test failures cascade | Medium | Medium | Phase verification checkpoints (ACA-14-013) |
| Token quota exhaustion | Low | Medium | Monitor usage, switch to gpt-4o-mini for simple stories |

### Scaling Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Efficiency degrades > 6 stories | Medium | Medium | Cap at 6 stories/sprint until proven stable |
| Review bottleneck | High | High | Automate PR checks, reduce required approvals |
| Story dependencies block parallelism | Medium | High | Dependency audit pre-sprint (48-veritas) |

---

## Appendix: Evidence Receipt Schema

All receipts follow [ACA-14-010 schema](C:\eva-foundry\51-ACA\.github\scripts\evidence_schema.py):

```python
REQUIRED_FIELDS = [
    "story_id",          # ACA-NN-NNN format
    "phase",             # D, P, D|P|D|C|A, A, C
    "timestamp",         # ISO 8601
    "test_result",       # PASS, FAIL, WARN, SKIP
    "duration_ms",       # int >= 0 (wall-clock execution time)
    "tokens_used",       # int >= 0 (sum of prompt + completion tokens)
    "test_count_before", # int >= 0 (pytest count before this story)
    "test_count_after",  # int >= 0 (pytest count after this story)
    "files_changed",     # int >= 0 (source files created or modified)
]
```

**Validation**: Enforced by `write_evidence()` in sprint_agent.py (raises ValueError on fail).

---

## References

- **Sprint 12 Completion**: [STATUS.md v1.33.0](C:\eva-foundry\51-ACA\STATUS.md)
- **Sprint 13-16 Manifests**: [.github/sprints/](C:\eva-foundry\51-ACA\.github\sprints)
- **Evidence Layer**: [ACA-12-022 implementation](C:\eva-foundry\51-ACA\data-model\db.py#L209-L263)
- **Veritas MTI Baseline**: [48-eva-veritas](C:\eva-foundry\48-eva-veritas) (MTI >= 30 for Sprint 2, >= 70 for Sprint 3+)
- **18-Azure-Best Practices**: [18-azure-best/](C:\eva-foundry\18-azure-best) (referenced in rule implementations)
