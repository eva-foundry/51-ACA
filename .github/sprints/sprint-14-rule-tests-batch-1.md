<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-14",
  "sprint_title": "rule-tests-batch-1",
  "target_branch": "sprint/14-rule-tests-batch-1",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-023",
      "title": "Unit test for R-01 devbox_autostop: fixture with Dev Box cost > $1,000 -> finding",
      "wbs": "3.4.1",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Test code generation with hardcoded fixtures. Repetitive pattern work following pytest conventions. gpt-4o-mini sufficient.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_devbox_autostop.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_devbox_above_threshold() passes (fixture cost > $1,000)",
        "pytest: test_devbox_below_threshold() passes (fixture cost < $1,000)",
        "pytest: test_devbox_no_resources() passes (empty inventory)",
        "Coverage: devbox_autostop.py >= 95% line coverage",
        "No Cosmos calls in test (hardcoded JSON fixtures only)"
      ],
      "implementation_notes": "Create pytest test module with 3 test cases. Use hardcoded fixtures (JSON dicts) for inventory/cost data. Assert finding schema fields. No actual Cosmos DB calls. Follow existing test patterns from Sprint 1-8."
    },
    {
      "id": "ACA-03-024",
      "title": "Unit test for R-02 log_retention: fixture with LA cost > $500 -> finding",
      "wbs": "3.4.2",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Repetitive test pattern, same as ACA-03-023. Simple fixture-based pytest.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_log_retention.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_log_retention_above_threshold() passes",
        "pytest: test_log_retention_below_threshold() passes",
        "pytest: test_log_retention_no_la() passes",
        "Coverage: log_retention.py >= 95%",
        "No Cosmos calls"
      ],
      "implementation_notes": "Test Log Analytics workspace cost > $500 in non-prod. Fixture includes subscription_id, workspace resource, cost data."
    },
    {
      "id": "ACA-03-025",
      "title": "Unit test for R-03 defender_mismatch: fixture with Defender cost > $2,000 -> finding",
      "wbs": "3.4.3",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Same repetitive pattern as previous test stories.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_defender_mismatch.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_defender_above_threshold() passes",
        "pytest: test_defender_below_threshold() passes",
        "pytest: test_defender_no_plan() passes",
        "Coverage: defender_mismatch.py >= 95%",
        "No Cosmos calls"
      ],
      "implementation_notes": "Test Defender SKU mismatch detection. Fixture: subscription with P1 plan but only basic resources."
    },
    {
      "id": "ACA-03-026",
      "title": "Unit test for R-04 compute_scheduling: fixture with schedulable > $5,000 -> finding",
      "wbs": "3.4.4",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Same pattern as previous 3 test stories.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_compute_scheduling.py (~120 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_scheduling_above_threshold() passes",
        "pytest: test_scheduling_below_threshold() passes",
        "pytest: test_scheduling_no_compute() passes",
        "Coverage: compute_scheduling.py >= 95%",
        "No Cosmos calls"
      ],
      "implementation_notes": "Test VM auto-shutdown detection. Fixture: non-prod subscription with VMs lacking auto-shutdown tag."
    },
    {
      "id": "ACA-03-027",
      "title": "Unit test for R-05 anomaly_detection: fixture with z-score > 3.0 -> finding",
      "wbs": "3.4.5",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Statistical test with z-score calculation. Still straightforward pytest pattern.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/tests/rules/test_anomaly_detection.py (~140 lines)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "pytest: test_anomaly_high_zscore() passes (z-score > 3.0)",
        "pytest: test_anomaly_normal_zscore() passes (z-score < 3.0)",
        "pytest: test_anomaly_insufficient_data() passes (< 30 days)",
        "Coverage: anomaly_detection.py >= 95%",
        "No Cosmos calls"
      ],
      "implementation_notes": "Test cost anomaly detection with statistical z-score. Fixture: 90-day cost history with one category showing spike (z > 3.0)."
    }
  ]
}
-->

# Sprint 14: Rule Unit Tests Batch 1 -- 5 Tests (R-01 through R-05)

**Sprint ID**: SPRINT-14
**Epic**: Epic 3 -- Analysis Engine and Rules
**Target Branch**: sprint/14-rule-tests-batch-1
**Total FP**: 15 (5 stories x S=3 FP each)
**Sprint Goal**: Establish 95% test coverage for first 5 analysis rules (R-01 through R-05)

---

## Stories

### Story ACA-03-023: Unit Test for R-01 Dev Box Auto-Stop
- **WBS**: 3.4.1
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test Dev Box cost threshold detection ($1,000 annual)
- **Files to Create**: services/analysis/tests/rules/test_devbox_autostop.py
- **Acceptance**: 3 test cases (above/below/no-resources), 95% coverage

### Story ACA-03-024: Unit Test for R-02 Log Retention
- **WBS**: 3.4.2
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test Log Analytics cost threshold ($500 non-prod)
- **Files to Create**: services/analysis/tests/rules/test_log_retention.py
- **Acceptance**: 3 test cases, 95% coverage

### Story ACA-03-025: Unit Test for R-03 Defender Mismatch
- **WBS**: 3.4.3
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test Defender SKU mismatch detection ($2,000 threshold)
- **Files to Create**: services/analysis/tests/rules/test_defender_mismatch.py
- **Acceptance**: 3 test cases, 95% coverage

### Story ACA-03-026: Unit Test for R-04 Compute Scheduling
- **WBS**: 3.4.4
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test VM auto-shutdown detection ($5,000 threshold)
- **Files to Create**: services/analysis/tests/rules/test_compute_scheduling.py
- **Acceptance**: 3 test cases, 95% coverage

### Story ACA-03-027: Unit Test for R-05 Anomaly Detection
- **WBS**: 3.4.5
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Test statistical anomaly detection (z-score > 3.0)
- **Files to Create**: services/analysis/tests/rules/test_anomaly_detection.py
- **Acceptance**: 3 test cases (high/normal/insufficient-data), 95% coverage

---

## Success Criteria

- All 5 test modules created with hardcoded JSON fixtures
- pytest suite: 15+ test cases added (3 per rule minimum)
- Coverage gate: each rule module >= 95% line coverage
- No Cosmos DB calls in any test (fixture-only testing)
- Evidence receipts created for all 5 stories
- PLAN.md updated: 5 stories PLANNED → DONE

---

## Sprint Scaling Progress

| Sprint | Stories | FP | Observation |
|--------|---------|----|-|
| Sprint 11 | 3 | 14 | Workflow V2 Foundation (complex) |
| Sprint 12 | 3 | 9 | Agent Context + Validation (medium) |
| Sprint 13 | 4 | 12 | Rule implementations R-09 to R-12 |
| **Sprint 14** | **5** | **15** | **+1 story, +25% FP (scaling up)** |

Next Sprint 15 target: 6 stories, ~18 FP (continue gradual increase)
