<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-04",
  "sprint_title": "analysis-foundation",
  "target_branch": "sprint/04-analysis-foundation",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-002",
      "title": "As the system I handle a rule failure in isolation (one rule crash does not",
      "wbs": "3.1.2",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Simple error handling pattern with try-catch and logging. No complex reasoning required.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/analysis/app/main.py (update run_analysis to wrap each rule in try-except)"
      ],
      "acceptance": [
        "If one rule raises an exception, the engine logs the error and continues",
        "The AnalysisRun record includes failed_rules array with rule IDs",
        "Other rules complete successfully and persist findings"
      ],
      "implementation_notes": "Wrap the rule execution loop in main.py with try-except for each rule. Log the exception with rule ID. Add failed_rules list to AnalysisRun schema. Continue to next rule on failure."
    },
    {
      "id": "ACA-03-003",
      "title": "As the system I persist each Finding to Cosmos with full schema:",
      "wbs": "3.1.3",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "Database schema mapping requires careful reasoning. Must handle all 11 fields correctly and partition by subscriptionId.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/analysis/app/findings.py (new module for Finding persistence)",
        "services/analysis/app/models.py (add Finding Pydantic model with all 11 fields)"
      ],
      "acceptance": [
        "Finding records persist to Cosmos findings container",
        "All 11 fields present: id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class, heuristic_source, narrative, deliverable_template_id, evidence_refs",
        "Partition key is subscriptionId",
        "Each finding has unique ID (format: {scanId}-{ruleId}-{counter})"
      ],
      "implementation_notes": "Create findings.py with persist_finding(cosmos_client, finding_dict) function. Import cosmos_client from services/api/app/db/cosmos.py pattern. Define Finding Pydantic model in models.py with all required fields. Use container.create_item() with partition_key=subscriptionId."
    },
    {
      "id": "ACA-03-011",
      "title": "R-01 Dev Box auto-stop: returns finding when annual Dev Box cost > $1,000",
      "wbs": "3.3.1",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "First real rule implementation with cost calculation logic and finding assembly. Requires understanding of Dev Box resource types and cost analysis patterns.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/analysis/app/rules/rule_01_dev_box_autostop.py (replace stub with full implementation)"
      ],
      "acceptance": [
        "Rule queries inventory for Microsoft.DevBox/devcenters and devboxes resources",
        "Calculates annual cost: sum of monthly costs * 12",
        "Returns finding when annual cost > $1,000",
        "Finding includes: category='compute-scheduling', title='Dev Box instances run nights and weekends', estimated_saving_low/high (30-50% of annual cost), effort_class='trivial', risk_class='none'",
        "narrative field explains auto-stop schedule recommendation",
        "deliverable_template_id='tmpl-dev-box-autostop'"
      ],
      "implementation_notes": "Update rule_01_dev_box_autostop.py to query inventory_data for DevBox resources. Calculate total annual cost. If > $1,000 threshold, construct Finding dict with all required fields. Use savings estimate: low=30% of cost, high=50% of cost. Return list with one finding (or empty list if below threshold). Reference docs/saving-opportunity-rules.md for full rule spec."
    }
  ]
}
-->

# SPRINT-04 -- analysis-foundation

Generated: 2026-03-01
Story IDs are canonical Veritas IDs from veritas-plan.json.
EVA-STORY tags in source files must use these exact IDs.

## Stories

| ID | Title | WBS | Size |
|----|-------|-----|------|
| ACA-03-002 | As the system I handle a rule failure in isolation (one | 3.1.2 | S |
| ACA-03-003 | As the system I persist each Finding to Cosmos with ful | 3.1.3 | M |
| ACA-03-011 | R-01 Dev Box auto-stop: returns finding when annual Dev | 3.3.1 | M |

## Execution Order

1. `ACA-03-002` -- As the system I handle a rule failure in isolation (one rule
2. `ACA-03-003` -- As the system I persist each Finding to Cosmos with full sch
3. `ACA-03-011` -- R-01 Dev Box auto-stop: returns finding when annual Dev Box 

## Notes

- All story IDs verified against .eva/veritas-plan.json
- Fill in TODO fields before creating the GitHub issue
- Create issue with: gh issue create --repo eva-foundry/51-ACA --title "[SPRINT-04] analysis-foundation" --body-file .github/sprints/sprint-04-analysis-foundation.md --label "sprint-task"
