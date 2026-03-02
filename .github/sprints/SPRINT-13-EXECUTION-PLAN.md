# SPRINT 13 REAL EXECUTION -- PLAN PHASE
## ACA-03: Analysis Engine and Rules (Final Batch)

**Date**: 2026-03-02  
**Objective**: Execute Sprint 13 with real LLM synthesis and collect authentic metrics  
**Acceptance Gate**: Evidence receipt must have:
- ✓ Real git commit SHA (40-char hex, not placeholder text)
- ✓ Natural variance in duration_ms (within 4000-15000 ms range based on pre-existing data)
- ✓ Actual artifacts in filesystem (rule files must exist)
- ✓ Real test count progression
- ✓ Non-zero tokens_used (evidence of LLM invocation)

---

## SPRINT 13 MANIFEST REVIEW

**Source**: `.github/sprints/sprint-13-analysis-rules-final.md`

**Stories**: 4 stories, 12 FP
- ACA-03-019: R-09 DNS sprawl rule (S=3)
- ACA-03-020: R-10 Savings plan rule (S=3)
- ACA-03-021: R-11 APIM token budget rule (S=3)
- ACA-03-022: R-12 Chargeback gap rule (S=3)

**DPDCA Breakdown**:

### **Discovery Phase (D1)**
- [ ] Read Sprint 13 manifest
- [ ] List required files: r09_dns_sprawl.py, r10_savings_plan.py, r11_apim_token.py, r12_chargeback.py
- [ ] Understand FINDING schema (id, category, title, estimated_saving_low, estimated_saving_high, effort_class, narrative, deliverable_template_id)

### **Planning Phase (P)**
- [ ] Design each rule as Python module
- [ ] Define unit tests: hardcoded fixtures (no Cosmos calls)
- [x] FP estimates: 3+3+3+3 = 12 FP

### **Implementation Phase (D2)**
- [ ] Generate r09_dns_sprawl.py (120 lines, ~5000-8000 ms)
- [ ] Generate r10_savings_plan.py (120 lines, ~5000-8000 ms)
- [ ] Generate r11_apim_token.py (110 lines, ~4500-7500 ms)
- [ ] Generate r12_chargeback.py (120 lines, ~5000-8000 ms)
- [ ] Create test fixtures for all 4 rules
- [ ] Add rules to ALL_RULES registry in engine

### **Check Phase (C)**
- [ ] pytest services/analysis/app/rules/test_r*.py → 95%+ coverage
- [ ] All rules return FINDING schema compliant objects
- [ ] Negative tests pass (cost < threshold → no finding)

### **Act Phase (A)**
- [ ] Commit: `feat(ACA-03-019-022): implement R-09 through R-12 analysis rules`
- [ ] Create evidence receipt with ACTUAL metrics:
  - duration_ms: measured wall-clock time
  - tokens_used: from LLM API responses
  - commit_sha: real git hash
  - test_count_after: actual pytest line count
- [ ] Seed evidence to data model
- [ ] Update PLAN.md story status → DONE

---

## EXECUTION PLAN

**Approach**: Use GitHub Models (primary) or Azure OpenAI (fallback)

**Environment**:
```
GITHUB_TOKEN: (configured, uses models.inference.ai.azure.com)
GITHUB_MODELS_URL: https://models.inference.ai.azure.com
AZURE_OPENAI_ENDPOINT: (fallback if GITHUB_TOKEN missing)
```

**Execution Method**:
```bash
cd 51-ACA
$env:PYTHONPATH = "."
C:\AICOE\.venv\Scripts\python.exe -m pytest services/analysis/app/rules/test_r*.py -v --tb=short
```

**Timing Instrumentation**:
```python
import time
start = time.time()
# ... execute sprint 13 code ...
duration_ms = int((time.time() - start) * 1000)
```

**Evidence Generation**:
Create receipt with:
- story_id: ACA-03-019 (primary story, includes all 4)
- phase: D (complete implementation)
- timestamp: ISO 8601 (actual execution time)
- duration_ms: measured in milliseconds
- tokens_used: from _get_llm_client() call count
- commit_sha: git rev-parse HEAD (actual commit)
- test_count_before: 0 (no tests yet)
- test_count_after: actual lines from pytest output

---

## SUCCESS CRITERIA

**Data Authenticity**:
- [ ] duration_ms between 4000-15000 ms (within observed variance range)
- [ ] tokens_used > 0 (must have invoked LLM)
- [ ] commit_sha matches `[0-9a-f]{40}` (real git hash)
- [ ] artifacts exist in filesystem
- [ ] test_count_after > test_count_before

**Code Quality**:
- [ ] All 4 rules implemented
- [ ] Test coverage >= 95% for each rule
- [ ] No lint errors (ruff check passes)
- [ ] No type errors (mypy passes)
- [ ] pytest exits 0

**Evidence Quality**:
- [ ] Receipt validates against evidence_schema.py
- [ ] Data model accepts receipt via POST /model/admin/seed-evidence
- [ ] Veritas audit continues to pass (no regression)

---

## RISK MITIGATION

**Risk 1: LLM unavailable**
- **Mitigation**: Azure OpenAI fallback configured, will activate automatically
- **Fallback Plan**: If both fail, use pre-written rule templates

**Risk 2: Execution takes longer than expected**
- **Mitigation**: Real execution may take 10-20 seconds per story (vs 1-2 sec simulation)
- **Acceptable**: Natural variance is expected, not a failure mode

**Risk 3: Evidence generation fails**
- **Mitigation**: evidence_schema.py validates on write, will catch errors immediately
- **Fallback**: Manual receipt creation if automation fails

---

## SCHEDULE

| Phase | Time | Activity |
|-------|------|----------|
| D1 | 5 min | Read manifest, understand requirements |
| P | 10 min | Plan implementation approach |
| D2 | 15-30 min | Generate 4 rule modules + tests (LLM synthesis) |
| C | 5 min | Run pytest, validate coverage |
| A | 5 min | Commit, create evidence receipt, seed to model |
| **Total** | **40-55 min** | Full DPDCA cycle |

**Expected completion**: ~12:00 PM ET (45 min from start)

---

## NEXT DECISION POINT

**After Sprint 13 completes**:
- If authentic metrics collected → proceed to Sprints 14-16 with confidence
- If issues arise → diagnose, adjust approach
- If successful → validate pattern holds for larger batches (14-16)

