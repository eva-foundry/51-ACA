<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-05",
  "sprint_title": "analysis-completion",
  "target_branch": "sprint/05-analysis-completion",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-004",
      "title": "As the system I update AnalysisRun status: queued -> running -> succeeded/failed",
      "wbs": "3.1.4",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "gpt-4o: Cosmos writes (status field updates) + cross-file reasoning between main.py and db/cosmos.py.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/analysis/app/main.py",
        "services/tests/test_analysis_status.py"
      ],
      "acceptance": [
        "services/analysis/app/main.py has EVA-STORY: ACA-03-004 tag",
        "AnalysisRun class has update_status(status: str) method",
        "update_status() calls upsert_item with partition_key=subscriptionId",
        "Status values: queued, running, succeeded, failed",
        "Test test_analysis_status_lifecycle in test_analysis_status.py passes",
        "pytest services/tests/test_analysis_status.py exits 0"
      ],
      "implementation_notes": "Extend AnalysisRun class in services/analysis/app/main.py to track status field (default: queued). Add update_status(status: str) method that updates self.status and calls upsert_item() immediately to persist. Status lifecycle: queued (init) -> running (before loop) -> succeeded/failed (after loop). Import upsert_item from app.db.cosmos. In tests, mock upsert_item and assert correct status transitions. Place EVA-STORY tag on functional line (class definition or import block), not in blank comment."
    },
    {
      "id": "ACA-03-005",
      "title": "As the system I write findingsSummary to the analysis run record",
      "wbs": "3.1.5",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "gpt-4o-mini: Single-file aggregation logic (count, sum), no auth or cross-service refs.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/analysis/app/main.py",
        "services/tests/test_findings_summary.py"
      ],
      "acceptance": [
        "services/analysis/app/main.py has EVA-STORY: ACA-03-005 tag",
        "AnalysisRun.persist() computes findingsSummary before upsert",
        "findingsSummary contains: findingCount, totalSavingLow, totalSavingHigh, categories[]",
        "categories is unique set of finding.category values",
        "Test test_findings_summary_aggregation in test_findings_summary.py passes",
        "pytest services/tests/test_findings_summary.py exits 0"
      ],
      "implementation_notes": "Extend AnalysisRun.persist() in services/analysis/app/main.py to compute summary dict before upsert. Compute: findingCount = len(self.findings), totalSavingLow = sum(f['estimated_saving_low']), totalSavingHigh = sum(f['estimated_saving_high']), categories = list(set(f['category'] for f in self.findings)). Add findingsSummary to the doc dict passed to upsert_item. In tests, create mock findings with category and saving fields, call persist(), assert summary fields present in upsert call."
    },
    {
      "id": "ACA-03-007",
      "title": "As a Tier 1 client I do not receive narrative or deliverable_template_id",
      "wbs": "3.2.2",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "gpt-4o: Security-critical (prevent data leak of premium fields) + cross-file validation (gate_findings already exists in findings_gate.py, must verify correct fields stripped).",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/api/app/services/findings_gate.py",
        "services/tests/test_tier1_gating.py"
      ],
      "acceptance": [
        "services/api/app/services/findings_gate.py has EVA-STORY: ACA-03-007 tag",
        "gate_findings(findings, tier='tier1') strips narrative and deliverable_template_id",
        "Tier 1 response includes ONLY: id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class",
        "narrative, deliverable_template_id, evidence_refs are NOT present in tier1 response",
        "Test test_tier1_strips_sensitive_fields in test_tier1_gating.py passes",
        "pytest services/tests/test_tier1_gating.py exits 0"
      ],
      "implementation_notes": "Update gate_findings function in services/api/app/services/findings_gate.py. For tier='tier1', return list comprehension that includes ONLY approved fields: id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class. Exclude narrative, deliverable_template_id, evidence_refs. gate_findings is already imported by findings router; verify existing test_findings_gate.py covers tier1 case. Create test_tier1_gating.py with mock finding containing ALL fields, call gate_findings, assert excluded fields are NOT in result. EVA-STORY tag on function def line."
    }
  ]
}
-->

# SPRINT-05 -- analysis-completion

Generated: 2026-03-01
Story IDs are canonical Veritas IDs from veritas-plan.json.
EVA-STORY tags in source files must use these exact IDs.

## Stories

| ID | Title | WBS | Size |
|----|-------|-----|------|
| ACA-03-004 | As the system I update AnalysisRun status: queued -> ru | 3.1.4 | M |
| ACA-03-005 | As the system I write findingsSummary to the analysis r | 3.1.5 | S |
| ACA-03-007 | As a Tier 1 client I do not receive narrative or delive | 3.2.2 | M |

## Execution Order

1. `ACA-03-004` -- As the system I update AnalysisRun status: queued -> running
2. `ACA-03-005` -- As the system I write findingsSummary to the analysis run re
3. `ACA-03-007` -- As a Tier 1 client I do not receive narrative or deliverable

## Notes

- All story IDs verified against .eva/veritas-plan.json
- Fill in TODO fields before creating the GitHub issue
- Create issue with: gh issue create --repo eva-foundry/51-ACA --title "[SPRINT-05] analysis-completion" --body-file .github/sprints/sprint-05-analysis-completion.md --label "sprint-task"
