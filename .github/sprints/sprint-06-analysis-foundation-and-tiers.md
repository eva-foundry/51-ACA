<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-06",
  "sprint_title": "analysis-foundation-and-tiers",
  "target_branch": "sprint/06-analysis-foundation-and-tiers",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-001",
      "title": "As the system I load all 12 rules from ALL_RULES and run each in sequence",
      "wbs": "3.1.1",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "gpt-4o: cross-file reasoning to refactor run_analysis, orchestrate 12 rule modules, handle errors in isolation.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/analysis/app/main.py (update run_analysis to load ALL_RULES)",
        "services/tests/test_analysis_rule_loader.py (new)"
      ],
      "acceptance": [
        "# EVA-STORY: ACA-03-001 tag present in services/analysis/app/main.py",
        "ALL_RULES loaded from services/analysis/app/rules/ (12 rule modules)",
        "run_analysis iterates through ALL_RULES, calls each rule.execute(subscription_id)",
        "One rule failure does not stop other rules (error is logged, rule is skipped)",
        "pytest services/tests/test_analysis_rule_loader.py exits 0"
      ],
      "implementation_notes": "Refactor run_analysis in main.py to use a rule loader pattern. Create ALL_RULES array with imports from services/analysis/app/rules/ (12 modules: devbox_autostop, log_retention, defender_mismatch, etc.). Mock rule.execute() in tests to avoid Cosmos calls. Use @patch decorator pattern matching ACA-03-004/005/007 tests. Each rule returns list of findings; failures are caught in try/except and logged without stopping the loop. Tier gating (findings_gate.gate_findings) happens after all rules complete."
    },
    {
      "id": "ACA-03-008",
      "title": "As a Tier 2 client I receive the full finding including narrative and",
      "wbs": "3.2.3",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "gpt-4o-mini: simple field filtering pattern, builds directly on ACA-03-007 Tier 1 implementation.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/api/app/services/findings_gate.py (add TIER2_FIELDS constant)",
        "services/tests/test_findings_tier2_gating.py (new)"
      ],
      "acceptance": [
        "# EVA-STORY: ACA-03-008 tag present in findings_gate.py",
        "TIER2_FIELDS = [id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class, narrative, evidence_refs] (excludes deliverable_template_id)",
        "gate_findings(findings, 'tier2') returns only TIER2_FIELDS per finding",
        "Test verifies tier2 result excludes deliverable_template_id",
        "pytest services/tests/test_findings_tier2_gating.py exits 0"
      ],
      "implementation_notes": "Add TIER2_FIELDS constant to findings_gate.py alongside existing TIER1_FIELDS and new TIER3_FIELDS. Update gate_findings() conditional to handle 'tier2' case: {k: v for k, v in finding.items() if k in TIER2_FIELDS}. Tier 2 includes narrative (unlike Tier 1) and evidence_refs but excludes deliverable_template_id (unlike Tier 3). Test with @patch pattern and mock findings dict. No cross-service calls needed."
    },
    {
      "id": "ACA-03-009",
      "title": "As a Tier 3 client I receive the full finding including deliverable_template_id",
      "wbs": "3.2.4",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "gpt-4o-mini: simple full-passthrough case, builds on ACA-03-008 Tier 2 pattern.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/api/app/services/findings_gate.py (add TIER3_FIELDS constant)",
        "services/tests/test_findings_tier3_gating.py (new)"
      ],
      "acceptance": [
        "# EVA-STORY: ACA-03-009 tag present in findings_gate.py",
        "TIER3_FIELDS = [all keys from finding dict] (full object, no filtering)",
        "gate_findings(findings, 'tier3') returns complete findings unchanged",
        "Test verifies tier3 result includes deliverable_template_id",
        "pytest services/tests/test_findings_tier3_gating.py exits 0"
      ],
      "implementation_notes": "Add TIER3_FIELDS constant (or use 'all' conditional) to gate_findings(). For tier3: return findings iterable directly (no filtering). TIER3_FIELDS includes everything: id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class, narrative, evidence_refs, deliverable_template_id. Test with mock findings that include all fields, verify each field is present in result. Red-team gate (ACA-03-010) will verify Tier 1 never leaks sensitive fields via API integration test."
    }
  ]
}
-->

# SPRINT-06 -- analysis-foundation-and-tiers

Generated: 2026-03-01
Story IDs are canonical Veritas IDs from veritas-plan.json.
EVA-STORY tags in source files must use these exact IDs.

## Stories

| ID | Title | WBS | Size |
|----|-------|-----|------|
| ACA-03-001 | As the system I load all 12 rules from ALL_RULES and ru | 3.1.1 | M |
| ACA-03-008 | As a Tier 2 client I receive the full finding including | 3.2.3 | S |
| ACA-03-009 | As a Tier 3 client I receive the full finding including | 3.2.4 | S |

## Execution Order

1. `ACA-03-001` -- As the system I load all 12 rules from ALL_RULES and run eac
2. `ACA-03-008` -- As a Tier 2 client I receive the full finding including narr
3. `ACA-03-009` -- As a Tier 3 client I receive the full finding including deli

## Notes

- All story IDs verified against .eva/veritas-plan.json
- Fill in TODO fields before creating the GitHub issue
- Create issue with: gh issue create --repo eva-foundry/51-ACA --title "[SPRINT-06] analysis-foundation-and-tiers" --body-file .github/sprints/sprint-06-analysis-foundation-and-tiers.md --label "sprint-task"
