---
project: 51-ACA
last_updated: 20260313
phase: Phase 1 - MVP Foundation
sprint: 48
audit_date: "2026-03-13T08:14:00-05:00"
mti_score: 98
mti_gate: 70
open_blockers: 4
---

# Project 51-ACA Status

## Latest Veritas Audit (March 13, 2026 @ 8:14 AM ET)

**Summary**:
```
Audit:       C:\eva-foundry\51-ACA
MTI Score:   98/100 (Coverage 100%, Consistency 100%, Field Pop 84%)
Total:       281 Phase 1 stories, 1064 artifacts
Evidence:    281/281 stories with evidence (100%)
Gaps:        0 detected
QA Issues:   17 stories missing sprint/assignee/ado_id metadata
```

**Quality Gate Status**:
- ? Coverage: 100% (all 281 stories have artifacts)
- ? Consistency: 100% (no WBS/plan conflicts)
- ? Evidence: 100% (all stories traced to commits/PRs)
- ??  Field Population: 84% (sprint=0%, assignee=0%, ado_id=24%)

**Cross-Project Context Validated**:
- ? 57-FKTE architectural alignment confirmed
- ? 60-IaC infrastructure layers (L112-L120) identified for future integration
- ? 58-CyberSec pattern validation underway
- ? 37-Data-Model UI generation complete
- ? Paperless governance ready for Friday sync ritual

**Recent Discovery**:
- 51-ACA is now recognized in workspace as FKTE reference implementation
- Cross-project dependency documentation updated in README
- API endpoint clarification added to copilot-instructions
- Action plan created for paperless DPDCA migration

---

## Sprint 48 Summary (Governance Regeneration + Epic 15 Closure)

Sprint 48 completed full WBS extraction from 43 architecture documents, closed Epic 15 implementation gaps ACA-15-001 through ACA-15-012, fixed a systemic Veritas consistency-scoring bug, and drove MTI from 66 to 99. A nested DPDCA reconciliation has now also onboarded docs 44-49 into the backlog model as mapped deltas instead of duplicate stories.

## Current Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Sprint | 48 (Governance Regeneration) | - | active |
| MTI Score | **99** | >= 70 | pass |
| MTI Coverage | 1.00 (100%) | >= 0.7 | pass |
| MTI Evidence | 1.00 (100%) | >= 0.7 | pass |
| MTI Consistency | 1.00 (100%) | >= 0.7 | pass |
| MTI Field Population | 0.88 (88%) | >= 0.5 | pass |
| Stories tracked (data model) | 281 / 281 artifacts | 281 | pass |
| Evidence-linked stories | 281 / 281 | 281 | pass |
| Full backlog scope | 623 stories, 19 epics + docs 44-49 deltas reconciled | - | documented |
| Open blockers | 2 | 0 | pending |
| Phase 1 gates | 12 / 12 pass | 12 | pass |
| Veritas actions | deploy, merge, release | deploy | pass |

## Recent Changes (Sprint 48)

1. WBS extraction from all 43 architecture documents completed: [`docs/WBS-FROM-DOCS-COMPLETE-20260311.md`](docs/WBS-FROM-DOCS-COMPLETE-20260311.md)
2. WBS reconciliation document finalized: [`docs/WBS-RECONCILIATION-20260311.md`](docs/WBS-RECONCILIATION-20260311.md)
3. Onboarding implementation slice added (ACA-15-001..012):
	- [`services/api/app/services/onboarding_runtime.py`](services/api/app/services/onboarding_runtime.py)
	- [`services/api/app/routers/onboarding.py`](services/api/app/routers/onboarding.py)
	- [`tools/aca_onboarding_cli.py`](tools/aca_onboarding_cli.py)
	- [`frontend/src/app/onboarding/OnboardingProgress.tsx`](frontend/src/app/onboarding/OnboardingProgress.tsx)
	- [`services/api/tests/test_onboarding_routes.py`](services/api/tests/test_onboarding_routes.py)
4. Veritas story-key consistency bug fixed: [`48-eva-veritas/src/lib/data-model-client.js`](../48-eva-veritas/src/lib/data-model-client.js) - `wbsToStatus()` now uses `original_story_id` for canonical lookup
5. Governance files regenerated from reconciled WBS baseline (PLAN, STATUS, ACCEPTANCE, README)
6. Nested DPDCA pass completed for docs 44-49: admin packs mapped to E05/E06, doc 46 promoted into explicit E01/E06 backlog slices for Entra JWT and Cosmos wiring, and founder/support deltas mapped to E18/E19

## Veritas Audit Output (Sprint 48 Final)

```
Command: node src/cli.js audit --repo C:/eva-foundry/51-ACA --threshold 70
MTI Score: 97
Coverage:    1.00
Evidence:    0.93
Consistency: 1.00
Field Pop:   0.88
Formula:     4-component-field-population
Actions:     deploy, merge, release
Sparkline:   57 -> 66 -> 66 -> 66 -> 57 -> 57 -> 57 -> 66 -> 67 -> 97
```
```
Command: node src/cli.js audit --repo C:/eva-foundry/51-ACA --threshold 70
MTI Score: 99
Coverage:    1.00
Evidence:    1.00
Consistency: 1.00
Field Pop:   0.88
Formula:     4-component-field-population
Actions:     deploy, merge, release
Sparkline:   57 -> 66 -> 66 -> 66 -> 57 -> 57 -> 57 -> 66 -> 67 -> 97 -> 99
Sparkline delta: +2 (nested DPDCA remaining-item closure)
Gaps: 0
WBS-F12 evidence: 16/16
WBS-F15 evidence: 17/17
```

Primary evidence artifacts:
- [`.eva/trust.json`](.eva/trust.json)
- [`.eva/reconciliation.json`](.eva/reconciliation.json)
- [`.eva/discovery.json`](.eva/discovery.json)

## Test Results

Sprint 48 ran full API test suite and coverage measurement in the project venv after dependency remediation.

| Metric | Current | Target | Evidence |
|--------|--------:|-------:|----------|
| Onboarding integration tests | 2 pass | > 0 | [services/api/tests/test_onboarding_routes.py](services/api/tests/test_onboarding_routes.py) |
| Full API suite | 17 pass | > 0 | [evidence/pytest-baseline-20260312.log](evidence/pytest-baseline-20260312.log) |
| API coverage | 59% | >= 80% | [evidence/coverage-baseline-20260312.xml](evidence/coverage-baseline-20260312.xml) |
| Lint | 150 issues (84 fixable) | 0 violations | [evidence/ruff-baseline-20260312.txt](evidence/ruff-baseline-20260312.txt) |

## Active Blockers

1. **Coverage gap** - API coverage is 59%, below the >=80% sprint target.
2. **Lint debt** - `ruff check services/api` reports 150 issues (84 fixable).
3. **Manifest source-of-truth drift** - Sprint 49 IDs (`ACA-01-024`, `ACA-01-025`, `ACA-06-046`, `ACA-06-047`) **NOT in `.eva/veritas-plan.json`**. Track A (governance sync/export) must run first to populate these IDs. Provisional manifest ready at `.github/sprints/sprint-49-entra-cosmos-wiring-provisional.md` for execution while Track A is in progress.

## Evidence Checklist

- [x] WBS extraction complete (43 docs ? comprehensive backlog)
- [x] Reconciliation complete (data model 281 stories cross-referenced)
- [x] All 12 Phase 1 gates pass
- [x] MTI >= 70 (current: 97)
- [x] Epic 15 implementation gaps closed (ACA-15-001..012)
- [x] Veritas consistency bug fixed and verified
- [x] Governance docs regenerated from WBS baseline
- [x] Full test suite executed post-merge (API: 17 passed)
- [ ] Coverage >= 80% reported (current 56.77%)
- [x] WBS metadata fields normalized (script result: updated=0 skipped=281 failed=0)
- [ ] Data model updated for latest governance sync
- [x] PLAN.md reflects actual work in this session

## Next Session Focus

1. ? Sprint 49 Discover phase complete (baseline evidence captured: [sprint-49-discover-evidence-20260312.json](evidence/sprint-49-discover-evidence-20260312.json))
2. Execute Track A governance sync: refresh model export and rebuild `veritas-plan.json` to include Sprint 49 IDs.
3. Regenerate canonical Sprint 49 manifest (replace provisional file).
4. Execute Track B implementation for doc 46 stories: `ACA-01-024`, `ACA-01-025`, `ACA-06-046`, `ACA-06-047` with evidence linkage.
4. Replace provisional Sprint 49 manifest with generated canonical manifest after Track A ID sync, then finalize acceptance/file TODOs for issue creation.
5. Close Check/Act with updated `PLAN.md`, `STATUS.md`, and `ACCEPTANCE.md` plus cloud sync evidence.


---

## 2026-03-15 -- Re-primed by agent:copilot

<!-- eva-primed-status -->

Data model: GET https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA
48-eva-veritas: run audit_repo MCP tool
