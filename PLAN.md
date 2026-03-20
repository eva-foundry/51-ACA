<!-- eva-primed-plan -->

## EVA Ecosystem Tools

- Data model: GET https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA
- 48-eva-veritas audit: run audit_repo MCP tool

---

---
project: 51-ACA
last_updated: 20260311
last_updated: 20260311
current_phase: 1 / 10
mti_target: 70
sprint: 48
mti_score: 99
---

# ACA - Azure Cost Advisor: Project Plan

## Program Scope

| Metric | Value |
|--------|-------|
| Total Epics | 19 |
| Total Stories (full backlog) | 623 |
| Phase 1 Stories (data model) | 281 |
| Total Function Points | 4,957 FP |
| Phases | 10 |
| Current Phase | 1 (MVP Foundation) |
| Data Model Source | [EVA Data Model API](https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io) |

Full story catalog: [`docs/WBS-FROM-DOCS-COMPLETE-20260311.md`](docs/WBS-FROM-DOCS-COMPLETE-20260311.md)

---

## Epic Breakdown

| ID | Epic | Stories | FP | Phase | Status |
|----|------|--------:|---:|-------|--------|
| E01 | Authentication & Authorization Framework | 25 | 193 | 1 | active |
| E02 | Data Collection Subsystem | 42 | 320 | 1 | active |
| E03 | Analysis Engine & Rules | 47 | 380 | 1 | active |
| E04 | Delivery & Script Generation | 32 | 240 | 1 | active |
| E05 | Frontend Application (Customer & Admin) | 39 | 285 | 1 | active |
| E06 | API Service (FastAPI Backend) | 47 | 333 | 1 | active |
| E07 | Billing & Payment Integration | 22 | 200 | 1 | active |
| E08 | Infrastructure & Deployment | 28 | 200 | 1 | active |
| E09 | Analytics & Telemetry | 12 | 90 | 1 | active |
| E10 | Phase 6 - Continuous Monitoring & Optimization | 28 | 250 | 3 | planned |
| E11 | Phase 7 - Enterprise Multi-Tenant Platform | 35 | 280 | 4 | planned |
| E12 | Phase 8 - Autonomous Optimization & Action Platform | 38 | 310 | 5 | planned |
| E13 | Phase 9 - Predictive & Strategic Optimization | 32 | 260 | 6 | planned |
| E14 | Phase 10 - Ecosystem & Intelligence Platform | 40 | 320 | 7 | planned |
| E15 | Testing & Quality Assurance | 24 | 180 | cross | active |
| E16 | Documentation | 16 | 100 | cross | active |
| E17 | DevOps & CI/CD | 18 | 150 | cross | active |
| E18 | Marketing & Go-To-Market | 15 | 113 | future | planned |
| E19 | Compliance & Governance | 17 | 133 | cross | active |
| **Total** | | **623** | **4,957** | | |

---

## Current Sprint (Sprint 48 - Governance Regeneration)

**Goal**: Complete governance regeneration from all 49 architecture docs; maintain MTI >= 70.

| Story ID | Story | Size | Phase Gate | Status | Evidence |
|----------|-------|-----:|------------|--------|----------|
| ACA-12-028 | Sync reconciled WBS to governance docs | L | P1-12 | done | [docs/WBS-RECONCILIATION-20260311.md](docs/WBS-RECONCILIATION-20260311.md) |
| ACA-19-006 | Standardize governance frontmatter | S | P1-12 | done | PLAN.md/STATUS.md/ACCEPTANCE.md updated |
| ACA-19-007 | Link status metrics to audit artifacts | M | P1-12 | done | [.eva/trust.json](.eva/trust.json) MTI=97 |
| ACA-19-008 | Run Veritas audit baseline | M | P1-12 | done | MTI 97 - deploy/merge/release |
| ACA-15-001 | Infrastructure provisioning: Bicep for Cosmos | M | P1-15 | done | [services/api/app/services/onboarding_runtime.py](services/api/app/services/onboarding_runtime.py) |
| ACA-15-002 | Cosmos DB schema implementation (9 containers) | M | P1-15 | done | [services/api/app/services/onboarding_runtime.py](services/api/app/services/onboarding_runtime.py) |
| ACA-15-003 | Gate state machine (7-gate workflow) | M | P1-15 | done | [services/api/app/services/onboarding_runtime.py](services/api/app/services/onboarding_runtime.py) |
| ACA-15-004 | FastAPI backend routes (POST /init, GET /{id}) | M | P1-15 | done | [services/api/app/routers/onboarding.py](services/api/app/routers/onboarding.py) |
| ACA-15-005 | Azure SDK wrappers + pagination + retry logic | M | P1-15 | done | [services/api/app/services/onboarding_runtime.py](services/api/app/services/onboarding_runtime.py) |
| ACA-15-006 | CLI command structure (init, resume, list...) | M | P1-15 | done | [tools/aca_onboarding_cli.py](tools/aca_onboarding_cli.py) |
| ACA-15-007 | Extraction pipeline (inventory + costs + advisor) | M | P1-15 | done | [services/api/app/services/onboarding_runtime.py](services/api/app/services/onboarding_runtime.py) |
| ACA-15-008 | Logging + recovery mechanism | M | P1-15 | done | [services/api/app/services/onboarding_runtime.py](services/api/app/services/onboarding_runtime.py) |
| ACA-15-009 | Analysis rules engine (18-azure-best integration) | M | P1-15 | done | [services/api/app/services/onboarding_runtime.py](services/api/app/services/onboarding_runtime.py) |
| ACA-15-010 | Evidence receipt generation (HMAC-SHA256) | M | P1-15 | done | [services/api/app/services/onboarding_runtime.py](services/api/app/services/onboarding_runtime.py) |
| ACA-15-011 | Integration tests (all gates, security, performance) | M | P1-15 | done | [services/api/tests/test_onboarding_routes.py](services/api/tests/test_onboarding_routes.py) |
| ACA-15-012 | React components (role assessment, preflight, progress) | M | P1-15 | done | [frontend/src/app/onboarding/OnboardingProgress.tsx](frontend/src/app/onboarding/OnboardingProgress.tsx) |

## Nested DPDCA Reconciliation (Docs 44-49)

Discover:
- Admin pack and production admin pack are available as concrete file artifacts under `docs/aca-admin-pack/` and `docs/aca-production-admin-pack/`.
- Doc 46 now points to `docs/aca-entra-cosmos-pack/` and provides concrete Entra JWT, dependency, RBAC, Cosmos, and admin repo wiring.
- Docs 47-49 refine onboarding, quotas, support, DR, and founder/GTM posture but do not justify duplicating already-seeded stories.

Plan:
- Map docs 44-49 to existing WBS stories first.
- Add only the true delta backlog items that were missing from the regenerated WBS.
- Promote doc 46 from passive evidence to explicit executable slices where the production wiring was underspecified.

Do:
- Added WBS deltas for `ACA-05-039`, `ACA-06-044`, `ACA-06-045`, `ACA-18-014`, `ACA-18-015`, `ACA-19-016`, and `ACA-19-017` in `docs/WBS-FROM-DOCS-COMPLETE-20260311.md`.
- Added doc 46 executable deltas for `ACA-01-024`, `ACA-01-025`, `ACA-06-046`, and `ACA-06-047` in `docs/WBS-FROM-DOCS-COMPLETE-20260311.md`.

Check:
- Docs 44-45 map primarily to existing admin stories in E05 and E06.
- Doc 46 now contributes explicit auth and data-layer slices in E01 and E06 covering JWT validation, actor extraction, bearer dependency wiring, and Cosmos-backed admin repositories.
- Docs 47-49 contribute operational and commercial deltas rather than a separate onboarding epic in the regenerated 19-epic model.

Act:
- Treat docs 44-49 as part of the canonical WBS input set going forward.
- Sync these deltas to the live data model on the next governed reseed/export cycle.

---

## Phase Roadmap

| Phase | Name | Duration | Epics | Status |
|-------|------|----------|-------|--------|
| 1 | MVP Foundation and Delivery | 12 weeks | E01-E09, E15-E17, E19 | **active** |
| 2 | Production Infrastructure Cutover | 8 weeks | E08 (Phase 2 infra), E19 | planned |
| 3 | Continuous Monitoring | 10 weeks | E10 | planned |
| 4 | Enterprise Multi-Tenant Platform | 12 weeks | E11 | planned |
| 5 | Autonomous Optimization | 12 weeks | E12 | planned |
| 6 | Predictive and Strategic Optimization | 10 weeks | E13 | planned |
| 7 | Ecosystem and Intelligence Platform | 12 weeks | E14 | planned |
| 8 | Compliance and Regional Expansion | 8 weeks | E19 (expansion) | planned |
| 9 | Marketplace and Partner Integration | 8 weeks | E18 | planned |
| 10 | Scale and Operational Excellence | ongoing | all | planned |

---

## Active Blockers

1. **Coverage uplift** - API coverage is 56.77% and must be raised to >=80% (policy gate currently set to 95%).
2. **Lint remediation** - `ruff check services/api` has unresolved legacy issues that must be fixed before strict lint gate closure.
3. **Manifest source-of-truth drift** - Sprint 49 stories `ACA-01-024`, `ACA-01-025`, `ACA-06-046`, and `ACA-06-047` are not yet present in `.eva/veritas-plan.json`, so `gen-sprint-manifest.py` aborts.

## Nested DPDCA Next Tasks (Sprint 49)

Discover:
1. ? Re-run project audit baseline (`veritas`, tests, coverage, lint) and record evidence snapshots.
   - Tests: 17 passed (100%)
   - Coverage: 59% (target: >=80%)
   - Lint: 150 issues, 84 fixable
   - Evidence: `evidence/sprint-49-discover-evidence-20260312.json`
2. ? Confirm canonical scope drift between local WBS (`623`) and cloud/data-model export baseline (`281`) remains unresolved.
   - Validation: Sprint 49 IDs (ACA-01-024/025, ACA-06-046/047) NOT in veritas-plan
   - Status: BLOCKER - Track A (governance sync) must run first

Plan:
1. Define sprint slice for doc 46 executable stories: `ACA-01-024`, `ACA-01-025`, `ACA-06-046`, `ACA-06-047`.
2. Split scope into two tracks:
	- Track A: Governance sync/export pipeline refresh.
	- Track B: Runtime implementation work in API/auth/admin repos.

Do:
1. Refresh model export and rebuild `veritas-plan.json` from the updated WBS baseline.
2. Use provisional manifest `/.github/sprints/sprint-49-entra-cosmos-wiring-provisional.md` for execution while Track A is in progress; replace it with a generated canonical manifest after ID sync.
3. Implement track B changes with story tags and evidence links.

Check:
1. `pytest services/api/tests -q --maxfail=1` exits 0.
2. `ruff check services/api` shows reduced blocking set (or zero if completed).
3. Coverage trend improves toward gate (`>=80%`) with updated report artifacts.
4. Veritas audit stays `>=70` with no new blocking traceability gaps.

Act:
1. Update `STATUS.md`, `ACCEPTANCE.md`, and WBS reconciliation notes with results.
2. Export updated governance state to cloud model in a governed sync cycle.
3. Close Sprint 49 with explicit residual risk list if any blockers remain.

### Immediate Implementation Slice (Doc 46)

Story pack for first executable unit:

1. `ACA-01-024` -- Entra JWT validation with discovery + JWKS cache
	- Target files: `services/api/app/auth/entra_jwt.py`, `services/api/app/settings.py`
2. `ACA-01-025` -- Claims to actor/role mapping
	- Target files: `services/api/app/auth/dependencies.py`, `services/api/app/auth/rbac.py`
3. `ACA-06-046` -- FastAPI bearer actor dependency wiring
	- Target files: `services/api/app/routers/admin.py`, `services/api/app/main.py`
4. `ACA-06-047` -- Cosmos-backed admin repositories (customers, runs, audit)
	- Target files: `services/api/app/db/cosmos.py`, `services/api/app/db/repos/admin_customer_repo.py`, `services/api/app/db/repos/admin_runs_repo.py`, `services/api/app/db/repos/admin_audit_repo.py`

Definition of done for this slice:

1. APIs compile and tests pass (`pytest services/api/tests -q --maxfail=1`).
2. Admin endpoints consume live repo/service results (no placeholder empty lists for the implemented paths).
3. Auth failures return structured 401/403 payloads and role checks enforce `ACA_Admin`, `ACA_Support`, `ACA_FinOps`.
4. All touched files include canonical `EVA-STORY` tags for the executing story IDs.

---

## Success Criteria

Phase 1 planning is considered done when all items below are true:

1. Governance files align with the reconciled WBS baseline and include required frontmatter.
2. Every active story in this sprint has explicit evidence tags.
3. Veritas audit runs successfully with parser-valid structure and no blocking traceability errors.
4. MTI remains at or above target (70) with no unapproved regression.

## WBS and Evidence References

1. `docs/WBS-FROM-DOCS-COMPLETE-20260311.md` [EVIDENCE: 49-doc extraction with docs 44-49 nested DPDCA deltas]
2. `docs/WBS-RECONCILIATION-20260311.md` [EVIDENCE: baseline + expansion reconciliation]
3. `README.md` [EVIDENCE: product scope and roadmap alignment]
4. `STATUS.md` [EVIDENCE: live sprint and test posture]
5. `ACCEPTANCE.md` [EVIDENCE: phase quality gates]
6. `docs/44-aca-admin-pack.md` [EVIDENCE: admin MVP scope]
7. `docs/45-aca-production-admin-pack.md` [EVIDENCE: production admin routes and API]
8. `docs/46-EntraJWT-Cosmos.md` [EVIDENCE: auth and Cosmos wiring pack pointer]
9. `docs/47-epic-15-gaps-closed.md` [EVIDENCE: onboarding, quotas, SLA, DR, support answers]
10. `docs/48-end-2-end-build.md` [EVIDENCE: end-to-end system context]
11. `docs/49-ACA-Founder-Launch-Kit.md` [EVIDENCE: GTM and founder operations]
12. `.github/sprints/sprint-49-entra-cosmos-wiring-provisional.md` [EVIDENCE: provisional Sprint 49 execution contract pending veritas-plan ID sync]
