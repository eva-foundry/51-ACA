# Sprint 07 Manifest -- rules-and-redteam

**Sprint ID**: SPRINT-07  
**Title**: rules-and-redteam -- First 3 rule implementations + red-team validation gate  
**Target Branch**: sprint/07-rules-and-redteam  
**Epic**: ACA-03 (Analysis Engine + Rules)  
**Stories**: 4/4 (100% target)  
**Function Points**: 8 FP  
**Estimated Duration**: 25-30 seconds  
**Created**: 2026-03-01 15:30 UTC  

---

## Sprint Summary

**Objective**: Implement first 3 cost-saving detection rules (R-02, R-03, R-04) + red-team validation gate for Tier 1 security.

All rule implementations now execute via the ACA-03-001 rule orchestrator (Sprint 6). This sprint:
1. Validates Tier 1 gating never leaks sensitive fields (red-team gate)
2. Implements Log Retention (LA cost > $500) rule pattern
3. Implements Defender Mismatch (Defender cost > $2,000) rule pattern
4. Implements Compute Scheduling (schedulable compute > $5,000) rule pattern

Rules 2-4 establish the repeating pattern for remaining 8 rules (ACA-03-015 through ACA-03-031, planned for Sprints 8-9).

---

## Stories

### 1. ACA-03-010 [S=2 FP] -- Red-team gate for Tier 1 security

**Title**: As the red-team agent I can assert that Tier 1 tokens never leak narrative or deliverable_template_id fields  
**WBS**: 3.2.5  
**Model**: gpt-4o-mini (validation logic, easy pattern matching)  
**Rationale**: WARN=`Test validation gate - straightforward mocking`

**Acceptance Criteria**:
1. red-team-agent.yaml contains a "leak_test" stage that calls GET /v1/findings/:scanId with a Tier 1 token
2. Agent parses response and asserts presence of: category, title, estimated_saving_low, estimated_saving_high, effort_class
3. Agent asserts absence of: narrative, deliverable_template_id, evidence_refs (if present, gate fails with LEAK_DETECTED)
4. If ANY field is found that should not be present, exit code 1 and log [LEAK] message
5. Red-team gate is skipped by default (runs only when REDTEAM_ENABLED=true env var set)

**Files to Create/Modify**:
- `agents/red-team-agent.yaml` -- add leak_test stage
- `services/tests/test_redteam_tier1_leak.py` -- new unit test to verify gate logic

**Implementation Notes** (technical guidance for gpt-4o-mini):
- Use simple field list comparison: expected_fields = {category, title, ...}; actual_fields = set(response.keys())
- Use MSAL mock for Tier 1 token generation (no real auth needed in test)
- Mock GET /v1/findings/:scanId response with hard-coded findings JSON
- Assertion: `assert not any(field in actual for field in ["narrative", "deliverable_template_id"])`
- Keep gate in separate file so CI can skip it (don't add to default pytest gate)

**Dependencies**: ACA-03-007 (Tier 1 gating implementation, Sprint 5)

---

### 2. ACA-03-012 [S=2 FP] -- R-02 Log retention rule

**Title**: As the system I implement R-02 rule: returns finding when annual LA cost > $500 in non-prod environments  
**WBS**: 3.3.2  
**Model**: gpt-4o-mini (rule implementation, pattern from ACA-03-011)  
**Rationale**: WARN=`Simple rule pattern - filter LA costs, aggregate by env, compare threshold`

**Acceptance Criteria**:
1. Rule module exists at `services/analysis/app/rules/r02_log_retention.py`
2. Rule accepts finding_base and cost_data (from Cosmos), returns list of Finding dicts
3. Rule logic: sum daily LA costs by environment, exclude "prod" tag, check if annual total > $500
4. If found: returns Finding with category ="logging-optimization", title="LA cost > $500 in non-prod", heuristic_source="rule-02"
5. If not found or < $500: returns empty list
6. Unit test: hardcoded LA cost fixture with 90+ days -> annual projection > $500 -> returns 1 finding
7. Negative test: annual < $500 -> returns 0 findings

**Files to Create/Modify**:
- `services/analysis/app/rules/r02_log_retention.py` -- new (40-50 lines)
- `services/tests/test_rule_r02_log_retention.py` -- new unit test
- `services/analysis/app/rules/__init__.py` -- add r02_log_retention import to ALL_RULES

**Implementation Notes** (technical guidance for gpt-4o-mini):
- Copy pattern from `services/analysis/app/rules/r01_devbox_autostop.py` (ACA-03-011 implementation)
- Filter: `[x for x in cost_data if x["service"] == "LogAnalytics" and "prod" not in x.get("tags", [])]`
- Calculation: `annual_cost = sum(daily_costs) * (365 / days_collected)`
- Return Finding name dict (not Finding class instance - JSON-serializable)
-  Set `estimated_saving=annual_cost` (the $500+ amount found)
- No DB calls - all data in function parameters

**Dependencies**: ACA-03-001 (rule orchestrator, Sprint 6), ACA-03-011 (R-01 pattern, Sprint 4)

---

### 3. ACA-03-013 [S=2 FP] -- R-03 Defender mismatch rule

**Title**: As the system I implement R-03 rule: returns finding when annual Defender cost > $2,000 (mismatch detection)  
**WBS**: 3.3.3  
**Model**: gpt-4o-mini (rule implementation, same pattern as R-02)  
**Rationale**: WARN=`Pattern rule - Defender cost aggregation, same filter/threshold approach`

**Acceptance Criteria**:
1. Rule module exists at `services/analysis/app/rules/r03_defender_mismatch.py`
2. Rule logic: aggregate Defender costs (Microsoft Defender for Cloud), compare annual total > $2,000
3. Heuristic: high Defender cost suggests over-provisioning or pricing misconfiguration
4. If found: returns Finding with category="security-cost-optimization", title="Defender cost > $2,000 annually"
5. If not found or < $2,000: returns empty list
6. Unit test: Defender cost fixture > $2,000 annual -> returns 1 finding
7. Negative test: annual < $2,000 -> returns 0 findings

**Files to Create/Modify**:
- `services/analysis/app/rules/r03_defender_mismatch.py` -- new (40-50 lines, same cost aggregation pattern as R-02)
- `services/tests/test_rule_r03_defender_mismatch.py` -- new unit test
- `services/analysis/app/rules/__init__.py` -- add r03_defender_mismatch import

**Implementation Notes** (technical guidance for gpt-4o-mini):
- Reuse same pattern as R-02
- Filter: `[x for x in cost_data if x["service"] == "Microsoft Defender for Cloud"]`
- Threshold: $2,000/year
- Same annualization formula

**Dependencies**: ACA-03-001, ACA-03-011, ACA-03-012 (build on R-02 pattern)

---

### 4. ACA-03-014 [S=2 FP] -- R-04 Compute scheduling rule

**Title**: As the system I implement R-04 rule: returns finding when annual schedulable compute > $5,000  
**WBS**: 3.3.4  
**Model**: gpt-4o-mini (rule implementation, cost aggregation pattern)  
**Rationale**: WARN=`Compute aggregation - VM + App Service + Container costs, threshold $5K`

**Acceptance Criteria**:
1. Rule module exists at `services/analysis/app/rules/r04_compute_scheduling.py`
2. Compute types: Virtual Machines (VM), App Service, Container Instances, Dedicated Hosts
3. Filter: exclude "prod" or "critical" tags (schedulable compute is non-critical only)
4. Rule logic: sum annual costs of all schedulable compute, compare > $5,000
5. If found: returns Finding with category="compute-cost-optimization", title="Schedulable compute > $5,000 annually"
6. Suggestion: turn off workloads after hours, use reserved instances, or scale down
7. If not found or < $5,000: returns empty list
8. Unit test: compute cost fixture with 3 VMs + 2 App Services > $5K annually -> returns 1 finding
9. Negative test: total < $5K -> returns 0 findings

**Files to Create/Modify**:
- `services/analysis/app/rules/r04_compute_scheduling.py` -- new (50-60 lines, multi-service aggregation)
- `services/tests/test_rule_r04_compute_scheduling.py` -- new unit test with multi-service fixture
- `services/analysis/app/rules/__init__.py` -- add r04_compute_scheduling import

**Implementation Notes** (technical guidance for gpt-4o-mini):
- Filter: `[x for x in cost_data if x["service"] in ["Virtual Machines", "App Service", "Container Instances", "Dedicated Hosts"] and "prod" not in x.get("tags", [])]`
- Aggregation: `sum(all matching costs)`, annualize
- Threshold: $5,000/year
- Note: first multi-service rule (previous 3 were single-service) - good pattern test

**Dependencies**: ACA-03-001, ACA-03-012, ACA-03-013

---

## Execution Plan

### Phase 1 -- Implement all 4 stories in parallel (agents auto-coordinate)
- ACA-03-010: ~3-4 minutes (YAML + test stub)
- ACA-03-012: ~4-5 minutes (rule impl + test)
- ACA-03-013: ~3-4 minutes (pattern repeat)
- ACA-03-014: ~5-6 minutes (multi-service aggregation)

**Parallel execution**: ~6-7 minutes total (agent creates 4 branches, 4 commits)

### Phase 2 -- Merge to sprint branch
- Squash 4 commits into 1 sprint commit
- All 4 stories in 1 PR

### Phase 3 -- Tests (CI)
- Run full pytest suite: expect 33 tests (29 existing + 4 new)
  - `test_rule_r02_log_retention.py`: 3 tests (positive, negative, boundary)
  - `test_rule_r03_defender_mismatch.py`: 3 tests
  - `test_rule_r04_compute_scheduling.py`: 3 tests
  - `test_redteam_tier1_leak.py`: 2 tests (leak detected, no leak)

### Phase 4 -- Merge to main
- Merge PR with squash strategy
- Expected test count after merge: 33/33 passing

### Phase 5 -- Ready for Sprint 8
- Remaining 8 rules (R-05 through R-12) follow same pattern
- Sprint 8: ACA-03-015, 016, 017, 018 (4 rules, 8 FP, ~25-30s)
- Sprint 9: ACA-03-019, 020, 021, 022, 023, 024, 025, 026 (8 tests, 16 FP)
- Sprint 10: ACA-03-027, 028, 029, 030, 031, 032, 033 (7 stories, rule tests complete + integration tests)

---

## TODO Fields (Agent Guidance)

**TODO: ACA-03-010**
```
gpt-4o-mini: Create red-team-agent YAML stage with leak detection.
Mock Tier 1 token, call GET /v1/findings, parse JSON fields.
Assert narrative + deliverable_template_id NOT in response.
Tests: leak_detected=true, leak_detected=false cases.
```

**TODO: ACA-03-012**
```
gpt-4o-mini: Rule R-02 -- filter LA costs by service name and non-prod tag.
Aggregate daily costs into annual projection.
Threshold $500. Return finding if exceeded, empty list if not.
Fixture: 100 days of LA costs, 90-day average $18/day -> $6,570/year.
Pattern reuse: matching logic from R-01 (ACA-03-011).
```

**TODO: ACA-03-013**
```
gpt-4o-mini: Rule R-03 -- filter Defender costs by service name.
Aggregate annual cost. Threshold $2,000.
Same annualization logic as R-02.
Fixture: 90 days of Defender costs, $55/day average -> $6,708/year.
```

**TODO: ACA-03-014**
```
gpt-4o-mini: Rule R-04 -- aggregate multiple compute services (VM, App Service, Containers).
Filter non-prod. Threshold $5K/year.
Multi-service fixture: 2 VMs @ $500/mo, 3 App Services @ $300/mo -> $33,600/year.
Most complex rule so far -- multi-service filtering is new pattern.
```

---

## Verification Checklist

After workflow completes:
- [ ] PR #25 (predicted) created by sprint-agent
- [ ] 4 story commits visible in PR
- [ ] All 33 tests passing (29 + 4 new)
- [ ] Red-team gate skipped in default gate (only runs with REDTEAM_ENABLED=true)
- [ ] 4 new rule files in `services/analysis/app/rules/`
- [ ] 4 new test files in `services/tests/`
- [ ] ALL_RULES constant now includes r02, r03, r04 (6 rules total: r01 via Sprint 4 + r02-04 via Sprint 7)
- [ ] No regressions: all 29 prior tests still passing
- [ ] Lint clean (ruff check passes)
- [ ] Type check clean (mypy passes)

---

## Branch + PR Details

**PR Title**: `fix(SPRINT-07): rules-and-redteam`  
**Branch**: `sprint/07-rules-and-redteam`  
**Base**: `main`  
**Label**: `sprint-task` (auto-triggers sprint-agent.yml)  

---

**Generated by sprint-advance skill**  
**Manifest Version**: 1.0  
**Schema**: SPRINT_MANIFEST_v1  
