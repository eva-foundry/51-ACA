# Sprint 49 Manifest (Provisional) -- Entra Auth + Cosmos Admin Wiring

**Sprint**: 49  
**Scope**: Doc 46 executable stories  
**Stories**: 4 (`ACA-01-024`, `ACA-01-025`, `ACA-06-046`, `ACA-06-047`)  
**Est. FP**: 26  
**Execution Model**: Nested DPDCA (Track A governance sync, Track B implementation)  
**Status**: Drafted manually because generator is blocked on source-of-truth drift

---

## Why Provisional

`gen-sprint-manifest.py` currently aborts because the Sprint 49 IDs are not yet present in `.eva/veritas-plan.json`.

Blocked IDs:

- `ACA-01-024`
- `ACA-01-025`
- `ACA-06-046`
- `ACA-06-047`

This manifest is a temporary execution contract to avoid idle time while Track A refreshes export/sync.

---

## Story 1: ACA-01-024 -- Entra JWT Validation (Discovery + JWKS)

**Acceptance**:

- [ ] Resolve OpenID metadata using tenant-specific authority with fallback to `common`
- [ ] Cache JWKS keys to reduce repeated remote lookups
- [ ] Validate `aud`, `iss`, `exp`, and `iat`
- [ ] Return structured 401 responses for malformed, expired, and unknown-key tokens
- [ ] Add/update tests for valid and invalid bearer tokens

**Target files**:

- `services/api/app/auth/entra_jwt.py`
- `services/api/app/settings.py`
- `services/api/tests/test_auth.py` (create or extend)

---

## Story 2: ACA-01-025 -- Claims to Actor/Role Mapping

**Acceptance**:

- [ ] Extract `oid/sub`, `name`, `tid`, and `roles/groups`
- [ ] Map roles/groups to `ACA_Admin`, `ACA_Support`, `ACA_FinOps`
- [ ] Produce a stable actor context object for downstream RBAC checks
- [ ] Ensure unauthorized role sets return 403 where applicable
- [ ] Add/update tests for role-mapping paths

**Target files**:

- `services/api/app/auth/dependencies.py`
- `services/api/app/auth/rbac.py`
- `services/api/tests/test_auth.py` (create or extend)

---

## Story 3: ACA-06-046 -- FastAPI Bearer Actor Dependency Wiring

**Acceptance**:

- [ ] Wire actor dependency into admin routes using bearer-token auth
- [ ] Return structured 401 on missing/malformed `Authorization` header
- [ ] Ensure admin endpoints consume actor context consistently
- [ ] Keep route behavior backward compatible for existing passing tests
- [ ] Add route-level tests for auth dependency enforcement

**Target files**:

- `services/api/app/routers/admin.py`
- `services/api/app/main.py`
- `services/api/tests/test_admin_routes.py` (create or extend)

---

## Story 4: ACA-06-047 -- Cosmos-Backed Admin Repositories

**Acceptance**:

- [ ] Implement partition-aware queries for customers, runs, and audit data
- [ ] Support customer search + detail retrieval, run listing, and audit listing
- [ ] Apply bounded limits and defensive defaults on list endpoints
- [ ] Replace placeholder/empty-list behavior for implemented paths
- [ ] Add/update repository tests and API wiring tests

**Target files**:

- `services/api/app/db/cosmos.py`
- `services/api/app/db/repos/admin_customer_repo.py`
- `services/api/app/db/repos/admin_runs_repo.py`
- `services/api/app/db/repos/admin_audit_repo.py`
- `services/api/tests/test_admin_repos.py` (create or extend)

---

## DPDCA Execution Notes

Discover:

- Baseline rerun complete (veritas/tests/lint/coverage).

Plan:

- Two-track plan active:
  - Track A: refresh governance export so story IDs exist in `.eva/veritas-plan.json`
  - Track B: implement runtime slice above with evidence and story tags

Do:

- Begin Track B in small commits while Track A sync is prepared.

Check:

- `pytest services/api/tests -q --maxfail=1`
- `ruff check services/api`
- Coverage trend improvement recorded in `evidence/api-coverage.xml`

Act:

- Replace this provisional file with generated canonical Sprint 49 manifest after Track A completes.
- Update `PLAN.md`, `STATUS.md`, and `ACCEPTANCE.md` with outcomes and residual risks.
