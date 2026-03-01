# SPRINT-09: Analysis Rules Batch 3 (R-09 through R-12)

**Sprint ID**: SPRINT-09  
**Sprint Label**: analysis-rules-batch-3  
**Status**: PLANNED (2026-03-01 11:40 AM ET)  
**Stories**: 4  
**FP**: 8 (S + S + S + M)  
**Expected Duration**: 25-30 seconds  
**Target Branch**: sprint/09-analysis-rules-batch-3

## Stories

### 1. ACA-03-019: R-09 DNS Sprawl Rule
- **Size**: S (2 FP)
- **Description**: DNS cost optimization rule
- **Logic**: Returns finding when annual DNS cost > $1,000
- **Category**: network-cost-optimization
- **Threshold**: Annual DNS costs exceeding $1,000
- **Model**: gpt-4o-mini (rule pattern established)
- **Files to Create**:
  - `services/analysis/app/rules/r09_dns_sprawl.py`
  - `services/tests/test_rule_r09_dns_sprawl.py`
- **Acceptance Criteria**:
  - [x] Rule function accepts DNS cost data as parameter
  - [x] Returns finding when annual DNS cost > $1,000
  - [x] Returns empty list when cost <= $1,000
  - [x] Finding includes title, category, saving estimate
  - [x] Unit test with positive (> $1,000) and negative (<= $1,000) fixtures

### 2. ACA-03-020: R-10 Savings Plan Coverage Rule
- **Size**: S (2 FP)
- **Description**: Compute savings plan optimization
- **Logic**: Returns finding when annual total compute > $20,000 without savings plan
- **Category**: cost-optimization
- **Threshold**: Total compute > $20,000 without coverage
- **Model**: gpt-4o-mini
- **Files to Create**:
  - `services/analysis/app/rules/r10_savings_plan_coverage.py`
  - `services/tests/test_rule_r10_savings_plan_coverage.py`
- **Acceptance Criteria**:
  - [x] Rule aggregates VM + App Service + Container costs
  - [x] Checks if savings plan is present
  - [x] Returns finding if compute > $20,000 without plan
  - [x] Returns empty if plan present or cost lower
  - [x] Unit test with coverage and no-coverage scenarios

### 3. ACA-03-021: R-11 APIM Token Budget Rule
- **Size**: S (2 FP)
- **Description**: Azure API Management token usage optimization
- **Logic**: Returns finding when APIM + OpenAI both present (potential token wastage)
- **Category**: api-cost-optimization
- **Threshold**: APIM gateway + OpenAI service both active = risk signal
- **Model**: gpt-4o-mini
- **Files to Create**:
  - `services/analysis/app/rules/r11_apim_token_budget.py`
  - `services/tests/test_rule_r11_apim_token_budget.py`
- **Acceptance Criteria**:
  - [x] Rule detects when both APIM and OpenAI services exist
  - [x] Returns finding recommending token budgeting review
  - [x] Returns empty if only one service present
  - [x] Unit test with both services, single service scenarios

### 4. ACA-03-022: R-12 Chargeback Gap Rule
- **Size**: M (3 FP)
- **Description**: Cost allocation and chargeback analysis
- **Logic**: Returns finding when total period cost > $5,000 without proper cost allocation tags
- **Category**: cost-allocation
- **Threshold**: Total cost > $5,000 without allocation tags
- **Model**: gpt-4o-mini
- **Files to Create**:
  - `services/analysis/app/rules/r12_chargeback_gap.py`
  - `services/tests/test_rule_r12_chargeback_gap.py`
- **Acceptance Criteria**:
  - [x] Rule sums all resource costs across subscription
  - [x] Checks for cost allocation tags (costCenter, environment, owner, etc.)
  - [x] Returns finding if high cost + missing allocation
  - [x] Returns empty if allocation tags present or cost lower
  - [x] Unit test with tags and no-tags fixtures

## Implementation Notes

### Pattern Consistency
All 4 rules follow the established pattern from Sprints 7-8:
- **Import Strategy**: Simplified (no cosmos imports), take data as parameters
- **Return Type**: List[Dict] with finding objects or empty list
- **Fixture-based Testing**: Hardcoded JSON fixtures, no Cosmos calls
- **Coverage Target**: 95% line coverage per rule module
- **Test Structure**: 1 positive case + 1 negative case per rule

### Reusable Components
- **Finding Schema**: Standard fields used across all rules
  - id, subscriptionId, category, title, estimated_saving_low/high, effort_class, risk_class
- **Test Pattern**: Hardcoded fixtures matching R-02 through R-08 pattern
- **Tier Gating**: No gating applied in rules (gating happens in API layer)

### Epic 3 Completion
After Sprint 9: **All 12 analysis rules complete** (100% of analysis engine core)
- R-01 through R-04: Compute + scheduling cost optimization
- R-05 through R-08: Anomaly detection + resource consolidation
- R-09 through R-12: Network + planning + chargeback optimization

Next: **Pivot to Epic 4 (API implementation)** for Sprint 10+

## Success Criteria

- [x] All 4 stories implemented
- [x] All 8 files created (4 rules + 4 tests)
- [x] All tests passing (8+ new test functions)
- [x] Evidence receipts written (4 files)
- [x] PR created and reviewed
- [x] PR merged to main with squash strategy
- [x] Branch deleted after merge
- [x] STATUS.md updated with Sprint 9 completion

---

<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-09",
  "sprint_name": "Analysis Rules Batch 3",
  "stories": [
    {
      "id": "ACA-03-019",
      "title": "R-09 DNS Sprawl Cost Optimization",
      "size": 2,
      "model": "gpt-4o-mini",
      "ado_id": 3197,
      "files_to_create": [
        "services/analysis/app/rules/r09_dns_sprawl.py",
        "services/tests/test_rule_r09_dns_sprawl.py"
      ],
      "acceptance_criteria": [
        "Rule function accepts DNS cost data as parameter",
        "Returns finding when annual DNS cost > $1,000",
        "Returns empty list when cost <= $1,000",
        "Finding includes title, category, saving estimate",
        "Unit test with positive and negative fixtures"
      ],
      "implementation_notes": "Follow r02 pattern: simplified function signature, no cosmos imports"
    },
    {
      "id": "ACA-03-020",
      "title": "R-10 Savings Plan Coverage Analysis",
      "size": 2,
      "model": "gpt-4o-mini",
      "ado_id": 3198,
      "files_to_create": [
        "services/analysis/app/rules/r10_savings_plan_coverage.py",
        "services/tests/test_rule_r10_savings_plan_coverage.py"
      ],
      "acceptance_criteria": [
        "Rule aggregates VM + App Service + Container costs",
        "Checks if savings plan is present",
        "Returns finding if compute > $20,000 without plan",
        "Returns empty if plan present or cost lower",
        "Unit test with coverage and no-coverage scenarios"
      ],
      "implementation_notes": "Aggregation logic from r04; check for plan presence in data"
    },
    {
      "id": "ACA-03-021",
      "title": "R-11 APIM Token Budget Review",
      "size": 2,
      "model": "gpt-4o-mini",
      "ado_id": 3199,
      "files_to_create": [
        "services/analysis/app/rules/r11_apim_token_budget.py",
        "services/tests/test_rule_r11_apim_token_budget.py"
      ],
      "acceptance_criteria": [
        "Rule detects when both APIM and OpenAI services exist",
        "Returns finding recommending token budgeting review",
        "Returns empty if only one service present",
        "Unit test with both services, single service scenarios"
      ],
      "implementation_notes": "Service presence check, no cost thresholding"
    },
    {
      "id": "ACA-03-022",
      "title": "R-12 Chargeback Cost Allocation Gap",
      "size": 3,
      "model": "gpt-4o-mini",
      "ado_id": 3200,
      "files_to_create": [
        "services/analysis/app/rules/r12_chargeback_gap.py",
        "services/tests/test_rule_r12_chargeback_gap.py"
      ],
      "acceptance_criteria": [
        "Rule sums all resource costs across subscription",
        "Checks for cost allocation tags (costCenter, environment, owner, etc.)",
        "Returns finding if high cost + missing allocation",
        "Returns empty if allocation tags present or cost lower",
        "Unit test with tags and no-tags fixtures"
      ],
      "implementation_notes": "Aggregation + tag checking logic; cost > $5,000 threshold"
    }
  ]
}
-->
