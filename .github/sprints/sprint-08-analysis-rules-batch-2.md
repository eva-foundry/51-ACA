<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-08",
  "sprint_title": "analysis-rules-batch-2",
  "target_branch": "sprint/08-analysis-rules-batch-2",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-015",
      "title": "As the system I implement R-05 rule: returns finding for each category with z-score > 3.0",
      "wbs": "3.3.5",
      "size": "M",
      "model": "gpt-4o-mini",
      "model_rationale": "Statistical anomaly detection - z-score calculation + category filtering, moderate complexity",
      "files_to_create": ["services/analysis/app/rules/r05_anomaly_detection.py", "services/tests/test_rule_r05_anomaly_detection.py"],
      "acceptance": [
        "Rule module exists at services/analysis/app/rules/r05_anomaly_detection.py",
        "Calculates z-scores for each cost category (Compute, Storage, Database, etc)",
        "Returns Finding for each category where z-score >= 3.0 (> 3 std deviations from historical mean)",
        "Unit test: fixture with outlier cost in one category -> returns 1 finding",
        "Negative test: all categories normal (z < 3) -> returns 0 findings"
      ],
      "implementation_notes": "Use numpy or scipy for z-score calculation. Group costs by category, calculate mean/stdev over 91-day window, identify outliers. Return one finding per outlier category."
    },
    {
      "id": "ACA-03-016",
      "title": "As the system I implement R-06 rule: returns finding when >= 3 App Service sites exist",
      "wbs": "3.3.6",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Simple inventory-based rule - count App Service instances, compare threshold",
      "files_to_create": ["services/analysis/app/rules/r06_stale_environments.py", "services/tests/test_rule_r06_stale_environments.py"],
      "acceptance": [
        "Rule module exists at services/analysis/app/rules/r06_stale_environments.py",
        "Counts App Service sites in inventory (by filtering resource type = 'Microsoft.Web/sites')",
        "Returns Finding if count >= 3 with category=resource-consolidation",
        "Unit test: fixture with 4 App Service sites -> returns 1 finding",
        "Negative test: fixture with 2 App Service sites -> returns 0 findings"
      ],
      "implementation_notes": "Filter inventory by resourceType == 'Microsoft.Web/sites', count occurrences, threshold=3. No cost aggregation needed."
    },
    {
      "id": "ACA-03-017",
      "title": "As the system I implement R-07 rule: returns finding when annual Search cost > $2,000",
      "wbs": "3.3.7",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Cost threshold rule - filter Azure AI Search costs, annualize, compare $2K threshold",
      "files_to_create": ["services/analysis/app/rules/r07_search_sku_oversize.py", "services/tests/test_rule_r07_search_sku_oversize.py"],
      "acceptance": [
        "Rule module exists at services/analysis/app/rules/r07_search_sku_oversize.py",
        "Filters cost data by service='Azure AI Search' or similar meter category",
        "Annualizes 91-day cost data and checks if annual total > $2,000",
        "Returns Finding with category=search-optimization if threshold exceeded",
        "Unit test: fixture with annual Search cost > $2K -> returns 1 finding",
        "Negative test: annual Search cost < $2K -> returns 0 findings"
      ],
      "implementation_notes": "Same cost filtering pattern as R-02/R-03. Service filter: 'Azure AI Search' or MeterCategory contains 'Search'. Threshold: $2,000/year."
    },
    {
      "id": "ACA-03-018",
      "title": "As the system I implement R-08 rule: returns finding when >= 3 registries exist",
      "wbs": "3.3.8",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Inventory-based rule - count container registries, same pattern as R-06",
      "files_to_create": ["services/analysis/app/rules/r08_acr_consolidation.py", "services/tests/test_rule_r08_acr_consolidation.py"],
      "acceptance": [
        "Rule module exists at services/analysis/app/rules/r08_acr_consolidation.py",
        "Counts Azure Container Registries in inventory (by filtering resource type = 'Microsoft.ContainerRegistry/registries')",
        "Returns Finding if count >= 3 with category=container-consolidation",
        "Unit test: fixture with 3+ ACRs -> returns 1 finding",
        "Negative test: fixture with 2 ACRs -> returns 0 findings"
      ],
      "implementation_notes": "Filter inventory by resourceType == 'Microsoft.ContainerRegistry/registries', count occurrences, threshold=3. Same pattern as R-06."
    }
  ]
}
-->

## Sprint 08: Analysis Rules Batch 2

**Epic**: ACA-03 Analysis Engine
**Branch**: sprint/08-analysis-rules-batch-2
**Stories**: 4 (8 FP expected)
**Expected Duration**: 25-30 seconds (same as Sprint 7)

### Objectives

Implement 4 additional analysis rules:
- R-05: Anomaly detection (statistical z-score analysis)
- R-06: Stale environments (App Service consolidation)
- R-07: Search SKU oversize (AI Search cost threshold)
- R-08: ACR consolidation (Container Registry consolidation)

All rules follow the established pattern:
- Filter inventory or cost data
- Apply threshold or statistical logic
- Return Finding if condition met
- Include unit tests (fixture: positive + negative)

### Patterns to Reuse

**Cost threshold rules**: R-07 follows R-02/R-03 cost filtering pattern
**Inventory rules**: R-06 and R-08 follow simple resource type counting pattern
**Statistical rule**: R-05 introduces z-score calculation (new complexity)

### Success Criteria

After merge to main:
- All 4 rule modules import cleanly
- All tests pass (expected: 37/37 = 29 baseline + 8 new from this sprint + previous sprint new)
- No regressions
- <1 minute execution time
- Branch deleted after merge

### Next Steps After Merge

Sprint 9: Rules R-09, R-10, R-11, R-12 (final batch) + API integration preparation
