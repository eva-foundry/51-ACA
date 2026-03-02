<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-15",
  "sprint_title": "rule-tests-batch-2",
  "target_branch": "sprint/15-rule-tests-batch-2",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-028",
      "title": "Unit test for R-06 stale_environments: fixture with >= 3 App Services -> finding",
      "wbs": "3.4.6",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Repetitive test pattern following established conventions from Sprint 14.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_stale_environments.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_stale_above_threshold() passes (>= 3 App Services)",
        "pytest: test_stale_below_threshold() passes (< 3 App Services)",
        "pytest: test_stale_no_app_services() passes",
        "Coverage: stale_environments.py >= 95%",
        "No Cosmos calls"
      ],
      "implementation_notes": "Test stale App Service detection. Fixture: subscription with 3+ App Service plans, some with low utilization metrics."
    },
    {
      "id": "ACA-03-029",
      "title": "Unit test for R-07 search_sku_oversize: fixture with Search cost > $2,000 -> finding",
      "wbs": "3.4.7",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Simple cost threshold test, same pattern as R-01/R-02.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_search_sku_oversize.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_search_above_threshold() passes",
        "pytest: test_search_below_threshold() passes",
        "pytest: test_search_no_service() passes",
        "Coverage: search_sku_oversize.py >= 95%",
        "No Cosmos calls"
      ],
      "implementation_notes": "Test Azure AI Search SKU right-sizing. Fixture: Standard S2 Search service with low query volume."
    },
    {
      "id": "ACA-03-030",
      "title": "Unit test for R-08 acr_consolidation: fixture with >= 3 registries -> finding",
      "wbs": "3.4.8",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Count-based heuristic test, straightforward pattern.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_acr_consolidation.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_acr_above_threshold() passes (>= 3 registries)",
        "pytest: test_acr_below_threshold() passes (< 3 registries)",
        "pytest: test_acr_no_registries() passes",
        "Coverage: acr_consolidation.py >= 95%",
        "No Cosmos calls"
      ],
      "implementation_notes": "Test Azure Container Registry sprawl detection. Fixture: 3+ ACR instances in same subscription."
    },
    {
      "id": "ACA-03-031",
      "title": "Unit test for R-09 dns_sprawl: fixture with DNS cost > $1,000 -> finding",
      "wbs": "3.4.9",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Cost threshold test, same as R-01/R-02/R-07.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_dns_sprawl.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_dns_above_threshold() passes",
        "pytest: test_dns_below_threshold() passes",
        "pytest: test_dns_no_zones() passes",
        "Coverage: dns_sprawl.py >= 95%",
        "No Cosmos calls"
      ],
      "implementation_notes": "Test DNS zone sprawl. Fixture: 10+ DNS zones with total annual cost > $1,000. Implemented in Sprint 13."
    },
    {
      "id": "ACA-03-032",
      "title": "Unit test for R-10 savings_plan_coverage: fixture with compute > $20,000 -> finding",
      "wbs": "3.4.10",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Aggregate cost calculation test, moderate complexity but established pattern.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_savings_plan_coverage.py (~130 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_savings_above_threshold() passes (total compute > $20k)",
        "pytest: test_savings_below_threshold() passes (< $20k)",
        "pytest: test_savings_no_compute() passes",
        "Coverage: savings_plan_coverage.py >= 95%",
        "Fixture includes VMs, App Service, AKS, Functions costs"
      ],
      "implementation_notes": "Test savings plan recommendation. Fixture: aggregate compute costs (VM + App Service + AKS + Functions) > $20k annual. Implemented in Sprint 13."
    },
    {
      "id": "ACA-03-033",
      "title": "Unit test for R-11 apim_token_budget: fixture with APIM + OpenAI -> finding",
      "wbs": "3.4.11",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Co-existence detection test, simple boolean logic.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_apim_token_budget.py (~130 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_apim_openai_coexist() passes (both present)",
        "pytest: test_apim_only() passes (no finding)",
        "pytest: test_openai_only() passes (no finding)",
        "pytest: test_neither() passes (no finding)",
        "Coverage: apim_token_budget.py >= 95%"
      ],
      "implementation_notes": "Test APIM + OpenAI co-existence detection. Fixture: subscription with both Microsoft.ApiManagement/service and Microsoft.CognitiveServices/accounts (kind=OpenAI). Implemented in Sprint 13."
    }
  ]
}
-->

# Sprint 15: Rule Unit Tests Batch 2 -- 6 Tests (R-06 through R-11)

**Sprint ID**: SPRINT-15
**Epic**: Epic 3 -- Analysis Engine and Rules
**Target Branch**: sprint/15-rule-tests-batch-2
**Total FP**: 18 (6 stories x S=3 FP each)
**Sprint Goal**: Complete test coverage for rules R-06 through R-11 (95% coverage target)

---

## Stories

### Story ACA-03-028: Unit Test for R-06 Stale Environments
- **WBS**: 3.4.6
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test stale App Service detection (>= 3 instances)
- **Files to Create**: services/analysis/tests/rules/test_stale_environments.py
- **Acceptance**: 3 test cases, 95% coverage

### Story ACA-03-029: Unit Test for R-07 Search SKU Oversize
- **WBS**: 3.4.7
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test Azure AI Search right-sizing ($2,000 threshold)
- **Files to Create**: services/analysis/tests/rules/test_search_sku_oversize.py
- **Acceptance**: 3 test cases, 95% coverage

### Story ACA-03-030: Unit Test for R-08 ACR Consolidation
- **WBS**: 3.4.8
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test Container Registry sprawl (>= 3 registries)
- **Files to Create**: services/analysis/tests/rules/test_acr_consolidation.py
- **Acceptance**: 3 test cases, 95% coverage

### Story ACA-03-031: Unit Test for R-09 DNS Sprawl
- **WBS**: 3.4.9
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test DNS zone sprawl detection ($1,000 threshold)
- **Files to Create**: services/analysis/tests/rules/test_dns_sprawl.py
- **Acceptance**: 3 test cases, 95% coverage, tests Sprint 13 implementation

### Story ACA-03-032: Unit Test for R-10 Savings Plan Coverage
- **WBS**: 3.4.10
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test savings plan recommendation ($20,000 compute threshold)
- **Files to Create**: services/analysis/tests/rules/test_savings_plan_coverage.py
- **Acceptance**: 3 test cases with aggregate compute costs, 95% coverage

### Story ACA-03-033: Unit Test for R-11 APIM Token Budget
- **WBS**: 3.4.11
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test APIM + OpenAI co-existence detection
- **Files to Create**: services/analysis/tests/rules/test_apim_token_budget.py
- **Acceptance**: 4 test cases (coexist/apim-only/openai-only/neither), 95% coverage

---

## Success Criteria

- All 6 test modules created with hardcoded JSON fixtures
- pytest suite: 19+ test cases added (3-4 per rule)
- Coverage gate: each rule module >= 95% line coverage
- Integration: Tests validate Sprint 13 rule implementations (R-09, R-10, R-11)
- No Cosmos DB calls in any test (fixture-only testing)
- Evidence receipts created for all 6 stories
- PLAN.md updated: 6 stories PLANNED → DONE

---

## Sprint Scaling Progress

| Sprint | Stories | FP | Execution Time (Est) | Observation |
|--------|---------|----|-|----------|
| Sprint 11 | 3 | 14 | 8.5 hours | Workflow V2 Foundation (complex infra) |
| Sprint 12 | 3 | 9 | 2.2 hours | Agent Context + Validation (medium) |
| Sprint 13 | 4 | 12 | 2.7 hours (est) | Rule implementations R-09 to R-12 |
| Sprint 14 | 5 | 15 | 3.1 hours (est) | Test batch 1 (R-01 to R-05) |
| **Sprint 15** | **6** | **18** | **3.7 hours (est)** | **+1 story, +20% FP (scaling up)** |

**Estimated execution time calculation for Sprint 15:**
- 6 test modules × 35 min each = 210 min (3.5 hours)
- Documentation + evidence receipts = 15 min
- **Total**: 225 min = 3.75 hours

Next Sprint 16 target: 7 stories, ~21 FP (final test stories + negative cases)
