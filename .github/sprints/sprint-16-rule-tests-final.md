<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-16",
  "sprint_title": "rule-tests-final",
  "target_branch": "sprint/16-rule-tests-final",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-034",
      "title": "Unit test for R-12 chargeback_gap: fixture with total cost > $5,000 -> finding",
      "wbs": "3.4.12",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Final rule test, same pattern as previous test stories.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_chargeback_gap.py (~130 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_chargeback_untagged() passes (cost > $5k, missing tags)",
        "pytest: test_chargeback_below_threshold() passes (cost < $5k)",
        "pytest: test_chargeback_all_tagged() passes (all resources tagged)",
        "Coverage: chargeback_gap.py >= 95%",
        "Finding narrative lists top 5 untagged resources"
      ],
      "implementation_notes": "Test mandatory tag enforcement. Fixture: resources without cost-center tag, total cost > $5k. Implemented in Sprint 13."
    },
    {
      "id": "ACA-03-035",
      "title": "Negative tests batch 1: R-01 through R-06 below-threshold fixtures -> no findings",
      "wbs": "3.4.13a",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Negative test cases for first 6 rules. Straightforward assertion: no finding returned.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_negative_batch_1.py (~180 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_r01_devbox_below_threshold() passes (cost < $1k, no finding)",
        "pytest: test_r02_log_retention_below_threshold() passes (cost < $500, no finding)",
        "pytest: test_r03_defender_below_threshold() passes (cost < $2k, no finding)",
        "pytest: test_r04_compute_below_threshold() passes (cost < $5k, no finding)",
        "pytest: test_r05_anomaly_normal() passes (z-score < 3.0, no finding)",
        "pytest: test_r06_stale_below_count() passes (< 3 App Services, no finding)",
        "All 6 negative tests return empty finding list"
      ],
      "implementation_notes": "Consolidated negative test module for efficiency. Each test uses below-threshold fixture, asserts len(findings) == 0."
    },
    {
      "id": "ACA-03-036",
      "title": "Negative tests batch 2: R-07 through R-12 below-threshold fixtures -> no findings",
      "wbs": "3.4.13b",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Second batch of negative tests, same pattern as ACA-03-035.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_negative_batch_2.py (~180 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_r07_search_below_threshold() passes (cost < $2k, no finding)",
        "pytest: test_r08_acr_below_count() passes (< 3 registries, no finding)",
        "pytest: test_r09_dns_below_threshold() passes (cost < $1k, no finding)",
        "pytest: test_r10_savings_below_threshold() passes (compute < $20k, no finding)",
        "pytest: test_r11_apim_no_openai() passes (no co-existence, no finding)",
        "pytest: test_r12_chargeback_all_tagged() passes (all tagged, no finding)",
        "All 6 negative tests return empty finding list"
      ],
      "implementation_notes": "Consolidated negative test module for rules 7-12. Each test asserts no finding when below threshold or condition not met."
    },
    {
      "id": "ACA-03-037",
      "title": "Edge case tests: empty inventory, malformed cost data, missing fields",
      "wbs": "3.4.14",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "Edge case testing requires more complex reasoning about failure modes. gpt-4o recommended for robustness.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_edge_cases.py (~200 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_empty_inventory() passes (all 12 rules handle gracefully)",
        "pytest: test_malformed_cost_data() passes (missing cost field -> no crash)",
        "pytest: test_missing_subscription_id() passes (None subscription_id -> no crash)",
        "pytest: test_null_resource_type() passes (resource without type -> no crash)",
        "pytest: test_negative_cost() passes (negative cost value -> filtered)",
        "No exceptions raised, all rules return empty findings on edge cases",
        "Coverage: edge case branches >= 90%"
      ],
      "implementation_notes": "Test defensive programming. All 12 rules must handle: empty input, None values, malformed data, negative costs. Use pytest.mark.parametrize for efficiency."
    },
    {
      "id": "ACA-03-038",
      "title": "CI coverage gate: enforce 95% line coverage on all rule modules",
      "wbs": "3.4.15",
      "size": "M",
      "model": "gpt-4o-mini",
      "model_rationale": "CI configuration and coverage reporting. Straightforward workflow YAML changes.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [],
      "files_to_modify": [
        ".github/workflows/ci.yml (add pytest-cov step)",
        "services/analysis/pytest.ini or pyproject.toml (coverage config)"
      ],
      "acceptance": [
        "CI runs pytest --cov=services/analysis/app/rules --cov-report=term",
        "Coverage report shows >= 95% for services/analysis/app/rules/*.py",
        "CI fails if coverage drops below 95% (--cov-fail-under=95)",
        "Coverage badge in README.md (optional)",
        "Pull requests show coverage diff in CI output"
      ],
      "implementation_notes": "Add pytest-cov plugin. Configure coverage thresholds. Update CI workflow to run coverage check after tests. Block merge if coverage < 95%."
    },
    {
      "id": "ACA-03-039",
      "title": "Integration test: run all 12 rules against multi-rule fixture -> 12 findings",
      "wbs": "3.4.16",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "Integration testing requires understanding of cross-rule interactions and comprehensive fixture design.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/integration/test_all_rules.py (~250 lines)",
        "services/analysis/tests/fixtures/multi_rule_fixture.json (~500 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_all_rules_integration() passes (fixture triggers all 12 rules)",
        "Fixture includes: Dev Box ($1.5k), LA ($600), Defender P1, VMs ($6k), anomaly spike, 4 App Services, Search S2 ($2.5k), 4 ACRs, 15 DNS zones ($1.2k), compute ($25k), APIM+OpenAI, untagged resources ($6k)",
        "Engine returns exactly 12 findings (one per rule)",
        "All findings have complete schema (id, title, category, savings, effort, risk)",
        "Integration test runs in < 5 seconds (no Cosmos calls)"
      ],
      "implementation_notes": "Create comprehensive fixture JSON that triggers all 12 rules simultaneously. Test FindingsAssembler orchestration. Assert finding count, schema completeness, category coverage."
    },
    {
      "id": "ACA-03-040",
      "title": "Performance test: 1000-resource inventory -> analysis completes in < 10 seconds",
      "wbs": "3.4.17",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Performance test with simple timing assertion. Straightforward implementation.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/performance/test_scale.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_large_inventory_performance() passes (1000 resources, 365 days cost data)",
        "Analysis completes in < 10 seconds on CI runners (time.time() measurement)",
        "Memory usage < 500 MB (tracemalloc check)",
        "No N+1 query patterns (all data pre-loaded in fixtures)",
        "pytest --durations=10 shows no slow tests (> 5s)"
      ],
      "implementation_notes": "Generate 1000-resource fixture programmatically. Time the full rule engine run. Assert completion < 10s. Use pytest-benchmark for stable timing."
    }
  ]
}
-->

# Sprint 16: Rule Unit Tests Final -- 7 Stories (Test Coverage Complete)

**Sprint ID**: SPRINT-16
**Epic**: Epic 3 -- Analysis Engine and Rules
**Target Branch**: sprint/16-rule-tests-final
**Total FP**: 21 (4×S=12 FP + 3×M=9 FP)
**Sprint Goal**: Complete Epic 3 test coverage: negative tests, edge cases, integration, CI gate

---

## Stories

### Story ACA-03-034: Unit Test for R-12 Chargeback Gap
- **WBS**: 3.4.12
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test mandatory tag enforcement ($5,000 untagged threshold)
- **Files to Create**: services/analysis/tests/rules/test_chargeback_gap.py
- **Acceptance**: 3 test cases, top 5 untagged resources listed

### Story ACA-03-035: Negative Tests Batch 1 (R-01 to R-06)
- **WBS**: 3.4.13a
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Below-threshold fixtures return no findings
- **Files to Create**: services/analysis/tests/rules/test_negative_batch_1.py
- **Acceptance**: 6 negative test cases, all assert len(findings) == 0

### Story ACA-03-036: Negative Tests Batch 2 (R-07 to R-12)
- **WBS**: 3.4.13b
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Below-threshold fixtures return no findings
- **Files to Create**: services/analysis/tests/rules/test_negative_batch_2.py
- **Acceptance**: 6 negative test cases, all assert len(findings) == 0

### Story ACA-03-037: Edge Case Tests
- **WBS**: 3.4.14
- **Size**: M=5 FP
- **Model**: gpt-4o
- **Description**: Test defensive programming (empty inventory, malformed data, None values)
- **Files to Create**: services/analysis/tests/rules/test_edge_cases.py
- **Acceptance**: 5+ edge case tests, no exceptions raised, 90% edge branch coverage

### Story ACA-03-038: CI Coverage Gate
- **WBS**: 3.4.15
- **Size**: M=2 FP
- **Model**: gpt-4o-mini
- **Description**: Enforce 95% line coverage on all rule modules in CI
- **Files to Modify**: .github/workflows/ci.yml, pytest.ini
- **Acceptance**: CI blocks merge if coverage < 95%, pytest-cov reports in pull requests

### Story ACA-03-039: Integration Test (All 12 Rules)
- **WBS**: 3.4.16
- **Size**: M=2 FP
- **Model**: gpt-4o
- **Description**: Multi-rule fixture triggers all 12 rules simultaneously
- **Files to Create**: test_all_rules.py, multi_rule_fixture.json
- **Acceptance**: Exactly 12 findings returned, complete schema validation, < 5s execution

### Story ACA-03-040: Performance Test (1000 Resources)
- **WBS**: 3.4.17
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test scalability with large inventory
- **Files to Create**: services/analysis/tests/performance/test_scale.py
- **Acceptance**: 1000-resource analysis completes in < 10s, memory < 500 MB

---

## Success Criteria

- **Epic 3 100% Complete**: All 12 rules implemented + full test coverage
- **Test Count**: 50+ test cases total (positive, negative, edge, integration, performance)
- **Coverage Target**: 95% line coverage across all 12 rule modules
- **CI Gate**: Pull requests blocked if coverage drops below 95%
- **Performance Validated**: 1000-resource analysis < 10s
- **Evidence Receipts**: Created for all 7 stories
- **PLAN.md Updated**: All Feature 3.4 stories PLANNED → DONE

---

## Sprint Scaling Progress (Full Trajectory)

| Sprint | Stories | FP | Execution Time (Est) | Story ΔP | FP ΔP | Observation |
|--------|---------|----|-|----------|--------|-------------|
| Sprint 11 | 3 | 14 | 8.5 hours | - | - | Workflow V2 (complex infra) |
| Sprint 12 | 3 | 9 | 2.2 hours | 0 | -36% | Agent Context (medium) |
| Sprint 13 | 4 | 12 | 2.7 hours (est) | +1 | +33% | Rule implementations |
| Sprint 14 | 5 | 15 | 3.1 hours (est) | +1 | +25% | Test batch 1 |
| Sprint 15 | 6 | 18 | 3.7 hours (est) | +1 | +20% | Test batch 2 |
| **Sprint 16** | **7** | **21** | **4.3 hours (est)** | **+1** | **+17%** | **Final tests + CI gate** |

**Estimated execution time calculation for Sprint 16:**
- 4 simple tests (S stories) × 35 min = 140 min
- 2 medium complexity (M stories) × 50 min = 100 min
- 1 complex integration (M story) × 60 min = 60 min
- Documentation + evidence receipts = 20 min
- **Total**: 320 min = 5.3 hours

**Scaling Analysis:**
- Gradual increase: +1 story per sprint (Sprint 11-16)
- FP growth moderating: +33% → +25% → +20% → +17% (sustainable)
- Execution time scales sub-linearly with FP (efficiency gains from patterns)
- Story count peak: 7 stories (Sprint 16) -- recommend max 7-8 per sprint

Next Sprint 17+ options:
- **Epic 4 (API)**: 21 stories, ~60 FP -- split into 3-4 sprints of 5-6 stories each
- **Epic 2 (Collector)**: 17 stories, ~45 FP -- split into 3 sprints of 5-6 stories each
