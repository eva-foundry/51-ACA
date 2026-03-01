<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-02",
  "sprint_title": "Analysis Rules",
  "target_branch": "main",
  "epic": "ACA-03",
  "stories": [
    {"id": "ACA-03-001", "title": "Load and run all 12 rules in sequence", "ado_id": 2978, "files_to_create": ["services/analysis/app/rules/__init__.py", "services/analysis/app/main.py"], "acceptance": ["ALL_RULES list defined", "Engine runs each rule"], "implementation_notes": "Create rule engine that loads all 12 rules and executes them in sequence"},
    {"id": "ACA-03-002", "title": "Rule 01 -- Dev Box autostop", "ado_id": 2979, "files_to_create": ["services/analysis/app/rules/devbox_autostop.py"], "acceptance": ["Returns finding when cost > $1000"], "implementation_notes": "Implement R-01 per PLAN.md 3.3.1"},
    {"id": "ACA-03-003", "title": "Rule 02 -- Log retention", "ado_id": 2980, "files_to_create": ["services/analysis/app/rules/log_retention.py"], "acceptance": ["Returns finding when cost > $500"], "implementation_notes": "Implement R-02 per PLAN.md 3.3.2"},
    {"id": "ACA-03-004", "title": "Rule 03 -- Defender mismatch", "ado_id": 2981, "files_to_create": ["services/analysis/app/rules/defender_mismatch.py"], "acceptance": ["Returns finding when cost > $2000"], "implementation_notes": "Implement R-03 per PLAN.md 3.3.3"},
    {"id": "ACA-03-005", "title": "Rule 04 -- Compute scheduling", "ado_id": 2982, "files_to_create": ["services/analysis/app/rules/compute_scheduling.py"], "acceptance": ["Returns finding when schedulable > $5000"], "implementation_notes": "Implement R-04 per PLAN.md 3.3.4"},
    {"id": "ACA-03-007", "title": "Rule 05 -- Anomaly detection", "ado_id": 2984, "files_to_create": ["services/analysis/app/rules/anomaly_detection.py"], "acceptance": ["Returns finding for z-score > 3.0"], "implementation_notes": "Implement R-05 per PLAN.md 3.3.5"},
    {"id": "ACA-03-008", "title": "Rule 06 -- Stale environments", "ado_id": 2985, "files_to_create": ["services/analysis/app/rules/stale_environments.py"], "acceptance": ["Returns finding when >= 3 App Services"], "implementation_notes": "Implement R-06 per PLAN.md 3.3.6"},
    {"id": "ACA-03-009", "title": "Rule 07 -- Search SKU oversize", "ado_id": 2986, "files_to_create": ["services/analysis/app/rules/search_sku_oversize.py"], "acceptance": ["Returns finding when cost > $2000"], "implementation_notes": "Implement R-07 per PLAN.md 3.3.7"},
    {"id": "ACA-03-010", "title": "Rule 08 -- ACR consolidation", "ado_id": 2987, "files_to_create": ["services/analysis/app/rules/acr_consolidation.py"], "acceptance": ["Returns finding when >= 3 registries"], "implementation_notes": "Implement R-08 per PLAN.md 3.3.8"},
    {"id": "ACA-03-011", "title": "Rule 09 -- DNS sprawl", "ado_id": 2988, "files_to_create": ["services/analysis/app/rules/dns_sprawl.py"], "acceptance": ["Returns finding when cost > $1000"], "implementation_notes": "Implement R-09 per PLAN.md 3.3.9"},
    {"id": "ACA-03-012", "title": "Rule 10 -- Savings plan coverage", "ado_id": 2989, "files_to_create": ["services/analysis/app/rules/savings_plan_coverage.py"], "acceptance": ["Returns finding when compute > $20000"], "implementation_notes": "Implement R-10 per PLAN.md 3.3.10"},
    {"id": "ACA-03-013", "title": "Rule 11 -- APIM token budget", "ado_id": 2990, "files_to_create": ["services/analysis/app/rules/apim_token_budget.py"], "acceptance": ["Returns finding when APIM + OpenAI exist"], "implementation_notes": "Implement R-11 per PLAN.md 3.3.11"},
    {"id": "ACA-03-014", "title": "Rule 12 -- Chargeback gap", "ado_id": 2991, "files_to_create": ["services/analysis/app/rules/chargeback_gap.py"], "acceptance": ["Returns finding when cost > $5000"], "implementation_notes": "Implement R-12 per PLAN.md 3.3.12"},
    {"id": "ACA-03-015", "title": "GB-02 -- Analysis auto-trigger", "ado_id": 2992, "files_to_create": ["services/analysis/app/trigger.py"], "acceptance": ["Auto-trigger on collector completion"], "implementation_notes": "Add auto-trigger logic from GB-02"},
    {"id": "ACA-03-016", "title": "GB-03 -- Resource Graph pagination", "ado_id": 2993, "files_to_create": ["services/collector/app/resource_graph.py"], "acceptance": ["Handles skipToken for large subscriptions"], "implementation_notes": "Add pagination support from GB-03"}
  ]
}
-->

## Sprint 2 -- Analysis Rules

**Goal**: Implement Epic 3 analysis rules (12 saving opportunity detectors) + GB-02/GB-03 infrastructure fixes

**Duration**: 2026-02-28 to 2026-03-10 (11 days)

**Stories**: 15

**ADO Iteration**: 51-aca\Sprint 2

---

### Work Items

1. **ACA-03-001** (WI 2978) - Load and run all 12 rules in sequence
2. **ACA-03-002** (WI 2979) - Rule 01: Dev Box autostop  
3. **ACA-03-003** (WI 2980) - Rule 02: Log retention
4. **ACA-03-004** (WI 2981) - Rule 03: Defender mismatch
5. **ACA-03-005** (WI 2982) - Rule 04: Compute scheduling
6. **ACA-03-007** (WI 2984) - Rule 05: Anomaly detection
7. **ACA-03-008** (WI 2985) - Rule 06: Stale environments
8. **ACA-03-009** (WI 2986) - Rule 07: Search SKU oversize
9. **ACA-03-010** (WI 2987) - Rule 08: ACR consolidation
10. **ACA-03-011** (WI 2988) - Rule 09: DNS sprawl
11. **ACA-03-012** (WI 2989) - Rule 10: Savings plan coverage
12. **ACA-03-013** (WI 2990) - Rule 11: APIM token budget
13. **ACA-03-014** (WI 2991) - Rule 12: Chargeback gap
14. **ACA-03-015** (WI 2992) - GB-02: Analysis auto-trigger
15. **ACA-03-016** (WI 2993) - GB-03: Resource Graph pagination

---

### Execution

Sprint Agent workflow auto-triggered. Monitor: https://github.com/eva-foundry/51-ACA/actions

**ADO Board**: https://dev.azure.com/marcopresta/51-aca/_sprints/taskboard/51-aca/51-aca/Sprint%202
