<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-13",
  "sprint_title": "analysis-rules-final",
  "target_branch": "sprint/13-analysis-rules-final",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-019",
      "title": "R-09 DNS sprawl: returns finding when annual DNS cost > $1,000",
      "wbs": "3.3.9",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Rule implementation follows established pattern from R-01 through R-08. Straightforward cost threshold check with standard finding schema. gpt-4o-mini sufficient for repetitive pattern work.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/app/rules/dns_sprawl.py (~80 lines)"
      ],
      "files_to_modify": [
        "services/analysis/app/rules/__init__.py (add R-09 to ALL_RULES list)"
      ],
      "acceptance": [
        "DNS cost fixture > $1,000 -> finding returned with category='network-optimization'",
        "DNS cost fixture < $1,000 -> no finding returned",
        "Finding schema includes: id, title, estimated_saving_low/high, effort_class, risk_class",
        "pytest: test_dns_sprawl_above_threshold() passes",
        "pytest: test_dns_sprawl_below_threshold() passes"
      ],
      "implementation_notes": "Query cost data for Microsoft.Network/dnsZones resources. Sum annual costs. If total > $1,000, return finding: effort_class=easy, risk_class=low. Recommended action: consolidate DNS zones, use private DNS for VNets. Use 18-azure-best/02-well-architected/cost-optimization.md for best practices."
    },
    {
      "id": "ACA-03-020",
      "title": "R-10 Savings plan: returns finding when annual total aggregate > $20,000",
      "wbs": "3.3.10",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Savings plan coverage calculation is straightforward arithmetic on aggregated cost data. Standard rule pattern, no complex logic required.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/app/rules/savings_plan_coverage.py (~90 lines)"
      ],
      "files_to_modify": [
        "services/analysis/app/rules/__init__.py (add R-10 to ALL_RULES list)"
      ],
      "acceptance": [
        "Total compute cost fixture > $20,000 -> finding returned with category='cost-optimization'",
        "Total compute cost fixture < $20,000 -> no finding returned",
        "Finding includes estimated_saving_low (15% of total) and estimated_saving_high (25% of total)",
        "pytest: test_savings_plan_above_threshold() passes",
        "pytest: test_savings_plan_below_threshold() passes"
      ],
      "implementation_notes": "Sum annual costs for compute categories: Virtual Machines, App Service, AKS, Functions, Container Apps. If total > $20,000, recommend 1-year savings plan. Savings estimate: 15-25% of total compute spend. Use Azure Advisor savings plan recommendations as reference (from advisor data)."
    },
    {
      "id": "ACA-03-021",
      "title": "R-11 APIM token budget: returns finding when APIM + OpenAI both present",
      "wbs": "3.3.11",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Co-existence check with simple token budget calculation. No ML or complex heuristics. gpt-4o-mini handles this easily.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/app/rules/apim_token_budget.py (~100 lines)"
      ],
      "files_to_modify": [
        "services/analysis/app/rules/__init__.py (add R-11 to ALL_RULES list)"
      ],
      "acceptance": [
        "Fixture with APIM + OpenAI resources -> finding returned with category='ai-governance'",
        "Fixture with APIM only -> no finding returned",
        "Fixture with OpenAI only -> no finding returned",
        "Finding narrative explains APIM token metering + budget alerts",
        "pytest: test_apim_openai_coexistence() passes",
        "pytest: test_apim_no_openai() passes"
      ],
      "implementation_notes": "Check inventory for both Microsoft.ApiManagement/service AND Microsoft.CognitiveServices/accounts (kind=OpenAI). If both exist, recommend APIM policy for token metering: rate-limit-by-key + quota-by-key. Reference 18-azure-best/04-ai-workloads/ai-security.md for AI governance patterns."
    },
    {
      "id": "ACA-03-022",
      "title": "R-12 Chargeback gap: returns finding when total period cost > $5,000",
      "wbs": "3.3.12",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Tag coverage analysis on cost data. Straightforward aggregation and threshold check. No complex logic required.",
      "epic": "Epic 3 -- Analysis Engine and Rules",
      "files_to_create": [
        "services/analysis/app/rules/chargeback_gap.py (~85 lines)"
      ],
      "files_to_modify": [
        "services/analysis/app/rules/__init__.py (add R-12 to ALL_RULES list)"
      ],
      "acceptance": [
        "Total cost > $5,000 with missing cost-center tag -> finding returned with category='governance'",
        "Total cost < $5,000 -> no finding returned",
        "Total cost > $5,000 with all resources tagged -> no finding returned",
        "Finding narrative lists top 5 untagged resources by cost",
        "pytest: test_chargeback_gap_untagged() passes",
        "pytest: test_chargeback_gap_all_tagged() passes"
      ],
      "implementation_notes": "Query cost data for resources without 'cost-center' or 'CostCenter' tag. Sum annual costs. If total > $5,000, return finding: effort_class=easy, risk_class=none. Recommended action: enforce mandatory tags via Azure Policy. Use 18-azure-best/12-security/azure-policy.md for tag enforcement patterns."
    }
  ]
}
-->

# Sprint 13: Analysis Rules Final -- 4 Rules (R-09 through R-12)

**Sprint ID**: SPRINT-13
**Epic**: Epic 3 -- Analysis Engine and Rules
**Target Branch**: sprint/13-analysis-rules-final
**Total FP**: 12 (4 stories x S=3 FP each)
**Sprint Goal**: Complete the final 4 analysis rules to reach 12/12 rule coverage for Phase 1

---

## Stories

### Story ACA-03-019: R-09 DNS Sprawl
- **WBS**: 3.3.9
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Detect DNS zone sprawl when annual cost exceeds $1,000
- **Files to Create**: services/analysis/app/rules/dns_sprawl.py
- **Acceptance**: Threshold tests pass, finding schema complete

### Story ACA-03-020: R-10 Savings Plan Coverage
- **WBS**: 3.3.10
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Recommend savings plan when compute spend exceeds $20,000
- **Files to Create**: services/analysis/app/rules/savings_plan_coverage.py
- **Acceptance**: 15-25% savings estimate, threshold tests pass

### Story ACA-03-021: R-11 APIM Token Budget
- **WBS**: 3.3.11
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Suggest APIM token metering when APIM + OpenAI co-exist
- **Files to Create**: services/analysis/app/rules/apim_token_budget.py
- **Acceptance**: Co-existence detection works, narrative includes policy snippet

### Story ACA-03-022: R-12 Chargeback Gap
- **WBS**: 3.3.12
- **Size**: S=3 FP
- **Model**: gpt-4o-mini
- **Description**: Flag missing cost-center tags when untagged spend > $5,000
- **Files to Create**: services/analysis/app/rules/chargeback_gap.py
- **Acceptance**: Tag coverage check works, top 5 untagged resources listed

---

## Success Criteria

- All 4 rule modules created with complete schema
- All rules registered in ALL_RULES list
- Unit tests for each rule (above/below threshold)
- Epic 3 progress: 8/12 rules → 12/12 rules (100%)
- Evidence receipts created for all 4 stories
- PLAN.md updated: 4 stories PLANNED → DONE

---

## Gradual Sprint Scaling Progress

| Sprint | Stories | FP | Observation |
|--------|---------|----|-|
| Sprint 11 | 3 | 14 | Workflow V2 Foundation (large) |
| Sprint 12 | 3 | 9 | Agent Context + Evidence Validation (medium) |
| **Sprint 13** | **4** | **12** | **+1 story, +33% FP (scaling up)** |

Next Sprint 14 target: 5 stories, ~15 FP (continue gradual increase)
