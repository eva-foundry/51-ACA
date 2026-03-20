# Sprint 49 Implementation Slice (Track B - Doc 46 Stories)

**Status**: READY FOR EXECUTION (pending Track A completion)  
**Activation**: After veritas-plan contains ACA-01-024/025, ACA-06-046/047  
**Priority**: HIGH - Unblocks auth/admin wiring for MVP

---

## Story 1: ACA-01-024 -- Entra JWT Validation

**FP**: 8  
**Target files**:
- `services/api/app/auth/entra_jwt.py` (NEW)
- `services/api/app/settings.py` (MODIFY - add discovery endpoint config)
- `services/api/tests/test_auth.py` (CREATE or MODIFY)

**What to implement**:
1. OpenID discovery endpoint resolution (tenant-specific + common fallback)
2. JWKS key caching (5 min TTL)
3. Token validation: aud, iss, exp, iat
4. Structured 401 responses for auth failures

**Entry point**: `from app.auth.entra_jwt import validate_token`

**Test coverage**:
- Valid token → returns claims
- Expired token → returns 401 with details
- Unknown key → returns 401 with details
- Invalid signature → returns 401
- Missing required claims → returns 401

---

## Story 2: ACA-01-025 -- Claims to Actor Mapping

**FP**: 5  
**Target files**:
- `services/api/app/auth/dependencies.py` (CREATE or MODIFY)
- `services/api/app/auth/rbac.py` (CREATE or MODIFY)
- `services/api/tests/test_auth.py` (ADD test cases)

**What to implement**:
1. Extract oid/sub, name, tid, roles/groups from token claims
2. Map to internal roles: ACA_Admin, ACA_Support, ACA_FinOps
3. Build stable actor context object
4. Return 403 for unauthorized role sets on restricted endpoints

**Entry point**: `from app.auth.dependencies import get_current_actor`

**Test coverage**:
- Admin role extraction → ACA_Admin
- Support role extraction → ACA_Support
- FinOps role extraction → ACA_FinOps
- Unknown role → raises 403
- Missing roles → raises 403

---

## Story 3: ACA-06-046 -- FastAPI Bearer Actor Dependency

**FP**: 5  
**Target files**:
- `services/api/app/routers/admin.py` (MODIFY - wire dependency)
- `services/api/app/main.py` (MODIFY - add dependency to routes)
- `services/api/tests/test_admin_routes.py` (CREATE or MODIFY)

**What to implement**:
1. FastAPI dependency injection for bearer token auth
2. Extract Authorization header, validate bearer scheme
3. Call `validate_token` from Story 1
4. Build actor context from Story 2
5. Return 401 for missing/malformed headers
6. Attach actor to request scope for downstream use

**Entry point**: Routes decorated `@app.get("/v1/admin/something", dependencies=[Depends(validate_bearer_auth)])`

**Test coverage**:
- Missing Authorization header → 401
- Malformed bearer token → 401
- Valid token → actor available in dependency
- Role check enforces ACA_Admin/Support → 403 if unauthorized

---

## Story 4: ACA-06-047 -- Cosmos Admin Repositories

**FP**: 8  
**Target files**:
- `services/api/app/db/cosmos.py` (MODIFY - add admin queries)
- `services/api/app/db/repos/admin_customer_repo.py` (CREATE)
- `services/api/app/db/repos/admin_runs_repo.py` (CREATE)
- `services/api/app/db/repos/admin_audit_repo.py` (CREATE)
- `services/api/tests/test_admin_repos.py` (CREATE)

**What to implement**:
1. Query existing data: entitlements, clients, scans, analyses, deliverables, audit
2. Support customer search (by subscriptionId), detail retrieval, run listing, audit listing
3. Partition-aware queries (subscriptionId partition key)
4. Bounded limits (default 100 items per list, configurable)
5. Replace hardcoded empty lists with real Cosmos queries

**Entry point**: `from app.db.repos.admin_customer_repo import AdminCustomerRepository`

**Test coverage**:
- Get customer by subscriptionId → returns entitlements, stripeCustomerId, tier, locked status
- List customers with pagination → returns bounded list
- List runs for subscription → returns scan/analysis/delivery records
- List audit events with filters → returns admin action records
- Partition key enforcement → no cross-subscription data leaks

---

## File Dependency Graph (Execution Order)

```
1. ACA-01-024 (Entra JWT validation)
   ↓ deps: settings.py
   
2. ACA-01-025 (Claims mapping)
   ↓ deps: ACA-01-024 (validate_token)
   
3. ACA-06-046 (FastAPI dependency)
   ↓ deps: ACA-01-025 (get_current_actor)
   
4. ACA-06-047 (Admin repositories)
   ↓ deps: ACA-06-046 (actor context available in routes)
```

**Recommendation**: Parallel implementation possible after ACA-01-024 (JWT validation is foundation):
- Developer 1: ACA-01-024 + ACA-01-025 (auth stack)
- Developer 2: ACA-06-046 (dependency wiring) - can start once Story 2 AC are met
- Developer 3: ACA-06-047 (repositories) - can start once Cosmos structure understood

---

## Definition of Done (All 4 Stories)

1. **Code compiles**
   - `python -m py_compile services/api/app/auth/*.py`
   - `python -m py_compile services/api/app/db/repos/*.py`

2. **Tests pass**
   - `pytest services/api/tests/test_auth.py -v`
   - `pytest services/api/tests/test_admin_repos.py -v`
   - `pytest services/api/tests/test_admin_routes.py -v`
   - All existing tests still pass: `pytest services/api/tests -q`

3. **Acceptance criteria met**
   - Each story AC checklist signed off per story acceptance doc in PLAN

4. **Evidence captured**
   - `# EVA-STORY: ACA-01-024` (or 025, 046, 047) commit tags on all commits
   - Story completion evidence files in `evidence/story-receipts/`
   - Coverage not regressed (maintain or improve from baseline 59%)

5. **No empty implementations**
   - Admin repos return real Cosmos data, not placeholder empty lists
   - JWT validation actually validates (not bypass)
   - Role mapping enforces actual role logic (not always grant access)

---

## Integration Points

### With existing API structure:
- Routes in `app/routers/admin.py` already stubbed
- Tests in `services/api/tests/` already structured
- Cosmos connection already established in `app/db/cosmos.py`
- Settings already configured (just need OpenID discovery endpoint)

### With existing project standards:
- All code must pass `ruff check` (84 fixable violations, use `--fix` where possible)
- Tests must run via `pytest` with coverage tracking
- Commit format: `[ACA-NN-NNN] Short description`
- Story tag in code: `# EVA-STORY: ACA-NN-NNN`

---

## Blockers & Dependencies

### On Track A (Governance):
- ⏳ WAITING: veritas-plan must contain ACA-01-024/025, ACA-06-046/047
- ⏳ WAITING: Sprint 49 canonical manifest regenerated (replace provisional)

### On Track B (Implementation):
- All 4 stories can start in parallel once Track A unblocks
- No blocking inter-story dependencies (dependency injection works once Auth stack ready)

---

## Success Metrics

- All 17 existing tests still passing: ✅
- 4 new stories implemented with tests: ✅
- Coverage does not regress: ✅
- Admin endpoints return real data (not stubs): ✅
- Auth enforcement active and auditable: ✅

---

## Next Document

See [51-ACA/.github/sprints/sprint-49-entra-cosmos-wiring-provisional.md](51-ACA/.github/sprints/sprint-49-entra-cosmos-wiring-provisional.md) for detailed acceptance criteria per story.
