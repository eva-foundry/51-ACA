# Project 51 (ACA) -- 8-Week Build Plan v2.0

**Generated**: March 11, 2026 @ 08:45 AM ET  
**Revised by**: Opus 4.6 Critical Review (replaces v1.0)  
**Method**: Nested DPDCA at program / sprint / epic / story granularity  
**Target**: Phase 1 production deployment (marco* sandbox)  
**Sprint Alignment**: Sprint-004 through Sprint-011 (continues from Sprint-003)

---

## Changes from v1.0

| Issue | v1.0 | v2.0 (Corrected) |
|-------|------|-------------------|
| Cosmos containers | "7 containers" | **11 containers** (scans, inventories, cost-data, advisor, findings, clients, deliverables, entitlements, payments, stripe_customer_map, admin_audit_events) |
| Re-planned DONE work | Epics 1, 2, 6 re-scheduled | **Skipped** -- 259 FP of completed work not re-planned |
| Story IDs | Invented (ACA-01-006 etc.) | **Actual PLAN.md IDs** only |
| Missing Epics | 13, 14, 15 omitted | **Epics 13-14 scheduled**, Epic 15 deferred (Sprint-014+) |
| i18n locales | "EN/FR" (2) | **5 locales**: en, fr, pt-BR, es, de |
| Admin surface | Barely mentioned | **Full Spark admin**: 5 pages, 6 API endpoints, 3 roles |
| Frontend architecture | Generic pages | **Spark architecture**: 5 customer + 5 admin pages |
| Acceptance gates | "15 P1 gates" | **12 P1 gates** (P1-01 through P1-12) |
| Sprint numbering | "Week 1" (orphaned) | **Sprint-004 through Sprint-011** |
| SAS URL duration | 24h | **168h (7 days)** per spec fix ACA-07-021 |
| Total FP capacity | Not calculated | **~695 FP planned vs 640-800 capacity** |

---

## Program-Level DPDCA

### DISCOVER (Baseline State -- March 11, 2026)

| Metric | Value | Source |
|--------|-------|--------|
| MTI Score | 57/100 | .eva/trust.json |
| Total Stories | 281 | PLAN.md (15 epics) |
| Story Coverage | 95.7% (269/281) | .eva/reconciliation.json |
| Evidence Coverage | 92.9% (261/281) | .eva/reconciliation.json |
| Gaps | 23 (12 missing_impl + 11 orphan) | .eva/reconciliation.json |
| Active Sprint | Sprint-003 | STATUS.md |
| Completed Sprints | 000, 001, 002 | STATUS.md |
| Cosmos Containers | 11 | PLAN.md Epic 12, README.md |
| Analysis Rules | 8/12 done (R-01 to R-08) | PLAN.md Feature 3.3 |
| Epics DONE | 1 (Foundation), 2 (Collection), 6 (Billing) | PLAN.md WBS |
| Epics PARTIAL | 3, 4, 5, 8, 9, 14 | PLAN.md WBS |
| Epics NOT STARTED | 7, 10, 13 | PLAN.md WBS |
| Epics ONGOING | 12 | PLAN.md WBS |
| Epics DEFERRED | 11 (Phase 2 Infra), 15 (Onboarding) | PLAN.md milestones |

### PLAN (This Document)

**Scope**: Phase 1 go-live (Epics 3-5, 7-10, 12-14)  
**Out of scope**: Epic 11 (Phase 2 Infra, 100 FP -- deferred to Sprint-012+), Epic 15 (Onboarding, 72 FP -- deferred to Sprint-014+)

**FP Budget**:

| Epic | Title | Total FP | Already Done | Remaining FP | Weeks |
|------|-------|----------|--------------|-------------|-------|
| 3 | Analysis Engine | 155 | ~78 | ~77 | 1-2 |
| 4 | API and Auth | 125 | ~25 | ~100 | 1-2 |
| 5 | Frontend Spark | 175 | ~0 | ~175 | 3-4 |
| 7 | Delivery Packager | 80 | 0 | 80 | 5 |
| 8 | Observability | 55 | 0 | 55 | 5-6 |
| 9 | i18n and a11y | 85 | 0 | 85 | 4, 6 |
| 10 | Commercial Hardening | 90 | 0 | 90 | 7-8 |
| 12 | Data Model (ongoing) | 50 | ~20 | ~30 | 1-8 |
| 13 | Azure Best Practices | 55 | 0 | 55 | 7 |
| 14 | DPDCA Agent | 50 | ~47 | ~3 | 1 |
| **TOTAL** | | **920** | **~225** | **~695** | |

**Capacity**: 8 weeks x 80-100 FP/sprint = 640-800 FP. Budget fits.

### DO (Weeks 1-8 Execution -- detailed below)

### CHECK (Weekly MTI Audits)

| Sprint | Week | MTI Target | Gate Type | Action If Fail |
|--------|------|------------|-----------|----------------|
| S-004 | 1 | 62 | Advisory | Document gaps, continue |
| S-005 | 2 | 65 | Advisory | Document gaps, continue |
| S-006 | 3 | 68 | Advisory | Document gaps, continue |
| S-007 | 4 | 72 | **MANDATORY** | Fix gaps before Week 5 |
| S-008 | 5 | 75 | Advisory | Document gaps, continue |
| S-009 | 6 | 78 | Advisory | Document gaps, continue |
| S-010 | 7 | 82 | High Priority | Fix critical gaps |
| S-011 | 8 | 87 | **MANDATORY** | Must pass for go-live |

### ACT (Phase 1 Completion)

- Update STATUS.md: Phase 1 READY FOR DEPLOYMENT
- Generate deployment evidence pack (all Week 1-8 artifacts)
- Create go-live runbook
- Begin Phase 2 planning (Epic 11, Epic 15)

---

## Reference Project Patterns Applied

| Pattern | Source | Where Applied |
|---------|--------|---------------|
| **APIM tier gating** | P39 | Epic 4 (APIM policies), Epic 3 (tier filtering) |
| **Evidence ID spine** | P40 | Epic 7 (scan -> findings -> delivery linking) |
| **Adapter pattern** | P41 | Epic 4 (CosmosAdapter/SQLiteAdapter for testing) |
| **Dual store** | P40 | Epic 12 (Cosmos cloud / SQLite local toggle) |
| **i18n from day 1** | P45 | Epic 9 (react-i18next, 5 locales) |
| **Template CRUD pages** | P31 | Epic 5 (AdminListPage pattern) |
| **Policy-as-code** | P49 | Epic 3 (rule thresholds in YAML) |
| **Webhook bridge** | P38 | Epic 6 (Stripe -> Cosmos, already DONE) |
| **Watchdog health** | P50 | Epic 8 (collector/analysis auto-restart) |
| **Mock backend** | P31 | Epic 5 (VITE_USE_MOCK_DATA) |
| **MTI quality gates** | P48 | Weeks 4, 8 (mandatory gates) |

---

## Nested DPDCA Structure

```
Program DPDCA (8-week cycle)
  |
  +-- Sprint DPDCA (weekly cycle, Sprint-004 through Sprint-011)
       |
       +-- D: Monday AM -- read status, check dependencies, MTI delta
       +-- P: Monday AM -- define week goals, allocate stories to days
       +-- Do: Monday PM through Thursday
       |    |
       |    +-- Story DPDCA (per story, within each day)
       |         +-- D: Read story acceptance criteria + related code
       |         +-- P: Design implementation approach
       |         +-- Do: Write code + tests
       |         +-- C: Run tests, verify criteria met
       |         +-- A: Commit with EVA-STORY tag, update story status
       |
       +-- C: Friday -- veritas audit, MTI check, evidence review
       +-- A: Friday -- update STATUS.md, write retrospective
```

**Story-Level DPDCA Template** (applied to every story):

```
# Story ACA-XX-NNN: [Title]
# DISCOVER: Read acceptance criteria + review related code
# PLAN: Design approach (files to create/modify, test strategy)
# DO: Implement + test
# CHECK: pytest passes, acceptance criteria met, evidence captured
# ACT: Commit "feat(epicN): ACA-XX-NNN [title]", update PLAN.md status
```

---

## Week 1 / Sprint-004: Analysis Completion + API Auth Foundation

**Goal**: Finish remaining 4 analysis rules. Establish API auth layer.  
**Epic Focus**: Epic 3 (rules R-09 to R-12), Epic 4 (auth + core endpoints)  
**FP Target**: ~80

### Sprint-004 DISCOVER (Monday AM)

- [ ] Read analysis rule implementations (services/analysis/app/rules/)
- [ ] Audit which Epic 4 stories have code vs. stubs
- [ ] Verify collector data exists in Cosmos (prerequisite for new rules)
- [ ] Baseline MTI: 57

### Sprint-004 PLAN (Monday AM)

| Day | Stories | FP | Theme |
|-----|---------|-----|-------|
| Mon | ACA-03-019, ACA-03-020 | 10 | Rules R-09 (DNS sprawl), R-10 (Savings plan) |
| Tue | ACA-03-021, ACA-03-022 | 10 | Rules R-11 (APIM token budget), R-12 (Chargeback gap) |
| Wed | ACA-04-001, ACA-04-003, ACA-04-004 | 15 | Auth: multi-tenant sign-in, session, connect modes |
| Thu | ACA-04-005, ACA-04-007, ACA-04-009, ACA-04-010 | 20 | Auth: disconnect, LoginPage, preflight, disconnect API |
| Fri | Sprint-004 CHECK + ACT | 5 | Veritas audit, evidence, retrospective |

### Sprint-004 DO

#### Monday: Analysis Rules R-09, R-10

**Story ACA-03-019 -- R-09 DNS Sprawl Detection**
- D: Read services/analysis/app/rules/ for existing rule patterns
- P: Implement r09_dns_sprawl.py following R-01 through R-08 pattern
- Do: Rule returns finding when annual DNS cost > $1,000
- C: pytest services/analysis/tests/test_r09_dns_sprawl.py passes
- A: Commit with `# EVA-STORY: ACA-03-019`

**Story ACA-03-020 -- R-10 Savings Plan Coverage**
- D: Read 14-az-finops savings plan patterns
- P: Implement r10_savings_plan.py
- Do: Rule returns finding when annual total compute > $20,000
- C: pytest passes, finding includes evidence_refs
- A: Commit with `# EVA-STORY: ACA-03-020`

#### Tuesday: Analysis Rules R-11, R-12

**Story ACA-03-021 -- R-11 APIM Token Budget**
- D: Read APIM + OpenAI co-existence patterns
- P: Implement r11_apim_token_budget.py
- Do: Rule returns finding when APIM + OpenAI both present
- C: pytest passes, risk_class=high (no saving, risk-only)
- A: Commit with `# EVA-STORY: ACA-03-021`

**Story ACA-03-022 -- R-12 Chargeback Gap**
- D: Read chargeback tagging patterns from 14-az-finops
- P: Implement r12_chargeback_gap.py
- Do: Rule returns finding when total period cost > $5,000
- C: pytest passes, effort_class=strategic
- A: Commit with `# EVA-STORY: ACA-03-022`

#### Wednesday: Auth Foundation (Epic 4)

**Story ACA-04-001 -- Multi-Tenant Sign-In**
- D: Read services/api/app/auth/, check MSAL configuration
- P: Ensure authority=https://login.microsoftonline.com/common
- Do: Any Microsoft account (any tenant) can sign in
- C: Test with mock JWT from common tenant
- A: Commit with `# EVA-STORY: ACA-04-001`

**Story ACA-04-003 -- SubscriptionId from Session**
- D: Read session management code
- P: Extract subscriptionId from Cosmos clients container, not JWT
- Do: Implement session-based tier resolution
- C: Test tier lookup from Cosmos mock
- A: Commit with `# EVA-STORY: ACA-04-003`

**Story ACA-04-004 -- Connect Modes A/B/C**
- D: Read 01-feasibility.md, 02-preflight.md
- P: Implement POST /v1/auth/connect with mode parameter
- Do: Mode A (delegated, any-tenant), Mode B (SP), Mode C (Lighthouse)
- C: Test each mode with mock credentials
- A: Commit with `# EVA-STORY: ACA-04-004`

#### Thursday: Auth Completion + Preflight API

**Story ACA-04-005 -- Disconnect**
- D: Read existing disconnect stub
- P: POST /v1/auth/disconnect: invalidate tokens, remove from KV
- Do: Hard-delete all Cosmos documents for subscriptionId
- C: Verify clean disconnection
- A: Commit with `# EVA-STORY: ACA-04-005`

**Story ACA-04-007 -- Frontend LoginPage MSAL**
- D: Read frontend auth setup
- P: MSAL.js with authority=common
- Do: Sign-in CTA accepts any Microsoft account
- C: Dev bypass works with VITE_DEV_AUTH=true
- A: Commit with `# EVA-STORY: ACA-04-007`

**Story ACA-04-009 -- Preflight API**
- D: Read preflight probe logic from collector
- P: POST /v1/auth/preflight runs 5 probes
- Do: Returns structured PASS/WARN/FAIL per probe
- C: Test with mock Azure credentials
- A: Commit with `# EVA-STORY: ACA-04-009`

**Story ACA-04-010 -- Disconnect API**
- D: Verify ACA-04-005 implementation covers this endpoint
- P: Ensure POST /v1/auth/disconnect is registered in router
- Do: Wire to auth router
- C: Test endpoint returns 200 on valid session
- A: Commit with `# EVA-STORY: ACA-04-010`

#### Friday: Sprint-004 CHECK + ACT

### Sprint-004 CHECK

- [ ] Run: `node 48-eva-veritas/src/cli.js audit --repo 51-ACA`
- [ ] All 12 analysis rules run without error (R-01 through R-12 complete)
- [ ] Auth endpoints: /connect, /preflight, /disconnect all respond
- [ ] MSAL authority=common confirmed (not org-specific)
- [ ] Evidence: `evidence/sprint-004-check-{timestamp}.json`

### Sprint-004 ACT

- [ ] Update PLAN.md: mark ACA-03-019 through ACA-03-022, ACA-04-001 through ACA-04-010 done
- [ ] Update STATUS.md: Sprint-004 complete
- [ ] Write `docs/SPRINT-004-RETROSPECTIVE.md`
- [ ] MTI target: 62 (advisory gate)

---

## Week 2 / Sprint-005: API Completion + Admin API + Rule Unit Tests

**Goal**: All 25+ API endpoints live. Admin API operational. Rule test coverage 95%.  
**Epic Focus**: Epic 4 (APIM + admin), Epic 3 (unit tests), Epic 12 (ongoing)  
**FP Target**: ~95

### Sprint-005 DISCOVER (Monday AM)

- [ ] Review Sprint-004 retrospective
- [ ] Verify auth endpoints working (prerequisite for APIM)
- [ ] Read APIM policy XML templates (infra/phase1-marco/apim/)
- [ ] Audit admin router (services/api/app/routers/admin.py)
- [ ] Check rule test coverage (pytest --cov)

### Sprint-005 PLAN (Monday AM)

| Day | Stories | FP | Theme |
|-----|---------|-----|-------|
| Mon | ACA-04-011..016 | 20 | Core API: collect, reports, billing, webhooks |
| Tue | ACA-04-017..021 | 15 | APIM policies: JWT, cache, tier, throttle |
| Wed | ACA-04-022..027 | 25 | Admin API: 6 endpoints |
| Thu | ACA-03-020..032 (unit tests, Feature 3.4) | 25 | Rule unit tests (12 positive + negative + assembler) |
| Fri | Sprint-005 CHECK + ACT, ACA-12-001..004 | 10 | Data model sync, evidence, retrospective |

### Sprint-005 DO

#### Monday: Core API Endpoints

**Stories ACA-04-011 through ACA-04-016** (Core API wiring)

- ACA-04-011: POST /v1/collect/start -- trigger collector job
  - D: Read collector trigger logic (ACA-02-017 implementation)
  - P: Route calls azure.mgmt.appcontainers to start collector job
  - Do: Implement with graceful degradation if ACA_ANALYSIS_JOB_NAME not set
  - C: Test trigger with mock Container Apps client
  - A: Commit with `# EVA-STORY: ACA-04-011`

- ACA-04-012: GET /v1/collect/status -- poll collection progress
  - D: Read scan status model (queued/running/succeeded/failed)
  - Do: Query Cosmos scans container by subscriptionId
  - C: Returns correct status fields (inventoryCount, costRows, etc.)

- ACA-04-013: GET /v1/reports/tier1 -- findings report (tier-gated)
  - D: Read tier gating logic (ACA-03-006 through ACA-03-009, all DONE)
  - Do: Wire to existing gate_findings() function
  - C: Tier 1 response excludes narrative + deliverable_template_id

- ACA-04-014: POST /v1/billing/checkout -- Stripe session
  - D: Read existing checkout router (Epic 6, DONE)
  - Do: Unify tier2/tier3 into single endpoint with tier in body
  - C: Returns valid Stripe checkout URL

- ACA-04-015: GET /v1/billing/portal -- Stripe billing portal
  - D: Read existing billing portal code
  - Do: Wire to Stripe customer portal API
  - C: Returns redirect URL for authenticated customer

- ACA-04-016: POST /v1/webhooks/stripe -- Stripe event handler
  - D: Read existing webhook handler (Epic 6, DONE)
  - Do: Verify single handler exists (fix ACA-06-021 duplicate if not done)
  - C: Signature validation works, idempotent processing

#### Tuesday: APIM Policies

**Stories ACA-04-017 through ACA-04-021** (APIM enforcement)

- ACA-04-017: JWT validation on all /v1/* routes
  - D: Read APIM policy XML patterns
  - P: validate-jwt policy with JWKS from common endpoint
  - Do: Apply to all /v1/* operations
  - C: Invalid JWT returns 401

- ACA-04-018: Entitlement caching (60s TTL)
  - D: Read 19-apim-cache.md caching patterns
  - Do: Cache key = entitlements::{subscriptionId}
  - C: Second call within 60s served from cache

- ACA-04-019: Tier enforcement (403 TIER_REQUIRED)
  - D: Read tier gating requirements
  - Do: Check entitlement tier before forwarding to backend
  - C: Tier 1 calling Tier 2+ endpoint gets 403

- ACA-04-020: Subscription key throttling (100 req/min)
  - Do: rate-limit-by-subscription-key policy
  - C: 101st request within 1 minute returns 429

- ACA-04-021: X-Subscription-Id header forwarding
  - Do: set-header policy on inbound
  - C: Backend receives X-Subscription-Id header

#### Wednesday: Admin API (6 Endpoints)

**Stories ACA-04-022 through ACA-04-027** (Admin surface backend)

- ACA-04-022: GET /v1/admin/kpis
  - D: Read admin dashboard requirements (doc 21-managing-buz.md)
  - P: Aggregate from scans, clients, payments containers
  - Do: Return mrrCad, activeSubscriptions, scansLast24h, failureRate
  - C: Test with mock data, verify all fields present
  - A: Requires role: ACA_Admin | ACA_Support | ACA_FinOps

- ACA-04-023: GET /v1/admin/customers?query=
  - Do: Search by subscriptionId or stripeCustomerId
  - C: Returns AdminCustomerRow list with tier, paymentStatus, isLocked

- ACA-04-024: POST /v1/admin/entitlements/grant
  - Do: Write entitlement to Cosmos + admin_audit_events record
  - C: Requires ACA_Admin | ACA_Support role

- ACA-04-025: POST /v1/admin/subscriptions/:id/lock
  - Do: Mark subscription locked in clients container
  - C: Write admin_audit_events record

- ACA-04-026: POST /v1/admin/stripe/reconcile
  - Do: Enqueue reconcile job, return jobId
  - C: Requires ACA_Admin role (strictest)

- ACA-04-027: GET /v1/admin/runs?type=scan|analysis|delivery
  - Do: List job runs with filter by subscriptionId and type
  - C: Pagination works correctly

#### Thursday: Rule Unit Tests (Feature 3.4)

**Stories ACA-03-020..032** (14 unit test stories)

Apply DPDCA per test file:
- D: Read rule implementation module
- P: Design fixtures (positive: above threshold, negative: below threshold)
- Do: Write test file with 5+ test cases
- C: pytest --cov shows >= 95% for that rule module
- A: Commit "test(rules): ACA-03-0XX R-NN unit tests"

Tests to write (one file per rule):
1. test_r01_devbox_autostop.py (ACA-03-020)
2. test_r02_log_retention.py (ACA-03-021)
3. test_r03_defender_mismatch.py (ACA-03-022)
4. test_r04_compute_scheduling.py (ACA-03-023)
5. test_r05_anomaly_detection.py (ACA-03-024)
6. test_r06_stale_environments.py (ACA-03-025)
7. test_r07_search_sku_oversize.py (ACA-03-026)
8. test_r08_acr_consolidation.py (ACA-03-027)
9. test_r09_dns_sprawl.py (ACA-03-028)
10. test_r10_savings_plan.py (ACA-03-029)
11. test_r11_apim_token_budget.py (ACA-03-030)
12. test_r12_chargeback_gap.py (ACA-03-031)
13. Negative tests all rules (ACA-03-032)
14. FindingsAssembler test (ACA-03-033, DONE -- verify only)

Target: `pytest --cov=services/analysis/app/rules --cov-report=term` > 95%

#### Friday: Sprint-005 CHECK + ACT

### Sprint-005 CHECK

- [ ] All 25+ API endpoints respond (health, auth, collect, reports, billing, admin)
- [ ] APIM policies deployed and tested (JWT, cache, tier, throttle)
- [ ] Rule test coverage > 95%
- [ ] Admin endpoints require role (test with no-role token -> 403)
- [ ] Evidence: `evidence/sprint-005-check-{timestamp}.json`

### Sprint-005 ACT

- [ ] Update PLAN.md: all Epic 4 stories marked done
- [ ] Update STATUS.md: Sprint-005 complete
- [ ] Write `docs/SPRINT-005-RETROSPECTIVE.md`
- [ ] MTI target: 65 (advisory gate)

---

## Week 3 / Sprint-006: Frontend Spark Architecture -- Customer Side

**Goal**: Spark router, auth guards, layouts, all 5 customer pages functional.  
**Epic Focus**: Epic 5 (Features 5.1-5.4, 5.6-5.7)  
**FP Target**: ~90

### Sprint-006 DISCOVER (Monday AM)

- [ ] Read frontend/ directory structure
- [ ] Audit existing React components and pages
- [ ] Review docs 22-spark-frontend.md, 23-spark-prompt.md
- [ ] Check Fluent UI v9 version and setup
- [ ] Verify VITE_DEV_AUTH bypass works (from ACA-04-007)

### Sprint-006 PLAN (Monday AM)

| Day | Stories | FP | Theme |
|-----|---------|-----|-------|
| Mon | ACA-05-001..005, ACA-05-011..015 | 20 | Auth layer + Router (Features 5.1, 5.3) |
| Tue | ACA-05-006..010 | 15 | Layouts: CustomerLayout, AdminLayout, Nav (Feature 5.2) |
| Wed | ACA-05-016..020 | 25 | 5 Customer pages (Feature 5.4) |
| Thu | ACA-05-026..034 | 20 | API client layer + Shared components (Features 5.6, 5.7) |
| Fri | Sprint-006 CHECK + ACT | 10 | Verify Tier 1 flow end-to-end |

### Sprint-006 DO

#### Monday: Auth Layer + Router

**Feature 5.1 -- Auth Layer**

- ACA-05-001: roles.ts -- ACA_Admin, ACA_Support, ACA_FinOps constants
- ACA-05-002: useAuth.ts -- MSAL wrapper with DEV bypass mode (VITE_DEV_AUTH)
- ACA-05-003: RequireAuth.tsx -- redirect to / if not authenticated
- ACA-05-004: RequireRole.tsx -- redirect to /app/connect if missing role
- ACA-05-005: All admin routes require RequireAuth + RequireRole

**Feature 5.3 -- Router**

- ACA-05-011: router.tsx using createBrowserRouter (not BrowserRouter)
- ACA-05-012: Route / -> LoginPage (no auth)
- ACA-05-013: Routes /app/* -> RequireAuth -> CustomerLayout -> Outlet
- ACA-05-014: Routes /admin/* -> RequireAuth -> RequireRole -> AdminLayout -> Outlet
- ACA-05-015: All page components lazy-loaded with React.lazy

#### Tuesday: Layouts and Navigation

**Feature 5.2 -- Layout Layer**

- ACA-05-006: CustomerLayout.tsx -- top nav, LanguageSelector, user menu
- ACA-05-007: AdminLayout.tsx -- top nav + left sidebar
- ACA-05-008: NavCustomer.tsx -- /app/connect, /app/status, /app/findings
- ACA-05-009: NavAdmin.tsx -- /admin/dashboard, /admin/customers, /admin/billing, /admin/runs, /admin/controls
- ACA-05-010: AppShell.tsx -- FluentProvider + ConsentBanner + RouterProvider

#### Wednesday: Customer Pages

**Feature 5.4 -- Customer Pages (/app/*)**

- ACA-05-016: LoginPage (/) -- Entra ID login CTA + dev bypass
  - D: Read MSAL integration from useAuth.ts
  - Do: Login button, hero section, tier cards
  - C: Dev bypass works, production redirects to Microsoft login

- ACA-05-017: ConnectSubscriptionPage (/app/connect)
  - D: Read connect modes (A/B/C)
  - Do: Radio group for mode selection, calls POST /v1/auth/connect then POST /v1/collect/start
  - C: Stores subscriptionId in sessionStorage after connect

- ACA-05-018: CollectionStatusPage (/app/status/:subscriptionId)
  - D: Read collection status model
  - Do: Polls GET /v1/collect/status with backoff, shows progress bar
  - C: Links to findings page when collection complete

- ACA-05-019: FindingsTier1Page (/app/findings/:subscriptionId)
  - D: Read tier 1 response format (title + saving range only)
  - Do: Render findings with MoneyRangeBar + EffortBadge, blurred upgrade CTAs
  - C: No narrative or deliverable_template_id visible

- ACA-05-020: UpgradePage (/app/upgrade/:subscriptionId)
  - D: Read Stripe checkout flow
  - Do: Tier 2 vs Tier 3 cards, calls POST /v1/billing/checkout
  - C: Stripe redirect works in test mode

#### Thursday: API Client Layer + Shared Components

**Feature 5.6 -- API Client Layer**

- ACA-05-026: client.ts -- base http<T> function with credentials
- ACA-05-027: appApi.ts -- customer API calls (getTier1Report, startCollection, etc.)
- ACA-05-028: adminApi.ts -- admin API calls (kpis, searchCustomers, etc.)
- ACA-05-029: models.ts -- TypeScript DTOs (Tier1Report, Finding, AdminKpis, etc.)

**Feature 5.7 -- Shared Components**

- ACA-05-030: Loading.tsx -- Fluent Spinner with aria-label
- ACA-05-031: ErrorState.tsx -- Fluent MessageBar with retry
- ACA-05-032: DataTable.tsx -- accessible table (th scope=col)
- ACA-05-033: MoneyRangeBar.tsx -- low/high saving range visualization
- ACA-05-034: EffortBadge.tsx -- trivial/easy/medium/involved/strategic badges

#### Friday: Sprint-006 CHECK + ACT

### Sprint-006 CHECK

- [ ] Tier 1 flow: Login -> Connect -> Status -> Findings (end-to-end)
- [ ] VITE_DEV_AUTH bypass works (no Azure deps for frontend dev)
- [ ] Router: / (public), /app/* (auth required), /admin/* (role required)
- [ ] All shared components render correctly
- [ ] axe-core on all pages: 0 critical violations
- [ ] Evidence: `evidence/sprint-006-check-{timestamp}.json`

### Sprint-006 ACT

- [ ] Update PLAN.md: all Feature 5.1-5.4, 5.6-5.7 stories done
- [ ] Update STATUS.md: Sprint-006 complete
- [ ] Write `docs/SPRINT-006-RETROSPECTIVE.md`
- [ ] MTI target: 68 (advisory gate)

---

## Week 4 / Sprint-007: Frontend Admin + i18n Foundation + Consent

**Goal**: Admin pages functional. 5-locale i18n foundation. Consent + telemetry wired.  
**Epic Focus**: Epic 5 (Features 5.5, 5.8-5.9), Epic 9 (partial)  
**FP Target**: ~85

### Sprint-007 DISCOVER (Monday AM)

- [ ] Review Sprint-006 retrospective
- [ ] Verify customer pages working (prerequisite for admin)
- [ ] Read admin API endpoints (from Sprint-005)
- [ ] Audit i18n current state

### Sprint-007 PLAN (Monday AM)

| Day | Stories | FP | Theme |
|-----|---------|-----|-------|
| Mon | ACA-05-021..025 | 25 | 5 Admin pages (Feature 5.5) |
| Tue | ACA-05-035..038 | 15 | Consent banner + telemetry (Feature 5.8) |
| Wed | ACA-05-039..042 | 10 | Accessibility (Feature 5.9) |
| Thu | ACA-09-001..006 | 20 | i18n foundation: 5 locales, date/number formats (Feature 9.1 partial) |
| Fri | Sprint-007 CHECK + ACT | 15 | **MANDATORY MTI >= 72 gate** |

### Sprint-007 DO

#### Monday: Admin Pages

**Feature 5.5 -- Admin Pages (/admin/*)**

- ACA-05-021: AdminDashboardPage (/admin/dashboard)
  - Do: Call GET /v1/admin/kpis, display MRR, active subs, scans/day, failure rate
  - C: All KPI cards render with real data from admin API

- ACA-05-022: AdminCustomersPage (/admin/customers)
  - Do: Search input -> GET /v1/admin/customers?query=
  - C: Display tier, paymentStatus, isLocked, deep links

- ACA-05-023: AdminBillingPage (/admin/billing)
  - Do: Stripe portal link, webhook health, "Reconcile Stripe" with confirmation modal
  - C: Destructive actions require confirmation

- ACA-05-024: AdminRunsPage (/admin/runs)
  - Do: List runs from GET /v1/admin/runs, filter by type
  - C: Pagination and filtering work

- ACA-05-025: AdminControlsPage (/admin/controls)
  - Do: Grant tier form, lock/unlock, rate-limit override, feature flags, incident banner
  - C: All admin_audit_events written via backend

#### Tuesday: Consent and Telemetry

**Feature 5.8 -- Consent and Telemetry**

- ACA-05-035: ConsentBanner on first visit
- ACA-05-036: TelemetryProvider -- GTM + Clarity only when VITE_ENABLE_TELEMETRY=true AND consent granted
- ACA-05-037: All 16 AnalyticsEventName events fire at correct points
- ACA-05-038: Admin surface does NOT load telemetry

#### Wednesday: Accessibility

**Feature 5.9 -- Accessibility**

- ACA-05-039: Skip-to-content link on every page
- ACA-05-040: Full keyboard navigation in all pages
- ACA-05-041: All form fields have associated label elements
- ACA-05-042: Admin confirmation modals trap focus and close on Escape

#### Thursday: i18n Foundation (5 Locales)

**Feature 9.1 -- i18n (Partial -- foundation stories)**

- ACA-09-001: i18next configured with 5 locale namespaces
  - D: Read frontend/src/i18n/ structure
  - Do: Configure en, fr, pt-BR, es, de namespace files
  - C: All 5 locale directories exist with translation keys

- ACA-09-002: All user-visible strings extracted (no hardcoded EN text)
  - Do: Extract all strings to translation JSON files
  - C: No hardcoded English text in components

- ACA-09-003: Language selector visible in nav
  - Do: Locale names in their own language (English, Francais, Portugues (Brasil), Espanol, Deutsch)
  - C: Selector switches locale and re-renders

- ACA-09-004: Locale preference persisted in localStorage

- ACA-09-005: Dates use Intl.DateTimeFormat (locale-aware)

- ACA-09-006: Numbers/currency use Intl.NumberFormat (CAD, USD, BRL, EUR)

#### Friday: MANDATORY MTI Gate

### Sprint-007 CHECK (MANDATORY GATE -- MTI >= 72)

- [ ] Run veritas audit: MTI >= 72
- [ ] All 5 customer pages + 5 admin pages functional
- [ ] i18n: language selector switches between 5 locales
- [ ] Consent: accept/reject works, preference persisted
- [ ] Accessibility: axe-core 0 critical/serious
- [ ] Evidence: `evidence/sprint-007-mti-gate-{timestamp}.json`

**If MTI < 72**: Stop. Fix gaps. Do not proceed to Week 5.

### Sprint-007 ACT

- [ ] Update PLAN.md: all Epic 5 + partial Epic 9 stories done
- [ ] Update STATUS.md: Sprint-007 complete, MTI gate result
- [ ] Write `docs/SPRINT-007-RETROSPECTIVE.md`

---

## Week 5 / Sprint-008: Delivery Packager + Observability Start

**Goal**: Full delivery pipeline operational (IaC -> ZIP -> Blob -> SAS URL). Backend observability wired.  
**Epic Focus**: Epic 7 (complete), Epic 8 (partial)  
**FP Target**: ~95

### Sprint-008 DISCOVER (Monday AM)

- [ ] Review Sprint-007 retrospective and MTI gate result
- [ ] Read delivery service code (services/delivery/app/)
- [ ] Audit IaC templates (services/delivery/app/templates/)
- [ ] Read App Insights configuration

### Sprint-008 PLAN (Monday AM)

| Day | Stories | FP | Theme |
|-----|---------|-----|-------|
| Mon | ACA-07-001..004 | 25 | IaC template library (12 Jinja2 templates, Bicep) |
| Tue | ACA-07-005..007 | 20 | ZIP packaging + SHA-256 + Blob upload + SAS URL |
| Wed | ACA-07-008, ACA-07-009 | 15 | Deliverable record in Cosmos + delivery trigger |
| Thu | ACA-08-007..011 | 20 | Backend observability (App Insights, structured logs, metrics) |
| Fri | Sprint-008 CHECK + ACT | 15 | End-to-end delivery validation |

### Sprint-008 DO

#### Monday: IaC Template Library (Feature 7.1)

**Story ACA-07-001 -- 12 Jinja2 Template Folders**
- D: Read services/delivery/app/templates/ structure
- P: Create 12 folders (tmpl-devbox-autostop through tmpl-chargeback-policy)
- Do: Each folder has main.bicep and README.md (Bicep Phase 1 only; Terraform deferred to Epic 11)
- C: All 12 folders exist with parameterized templates
- A: Commit with `# EVA-STORY: ACA-07-001`

**Story ACA-07-002 -- Template Structure**
- Do: Each folder has main.bicep parameterized with scan_id, subscription_id, finding fields

**Story ACA-07-003 -- Template Parameterization**
- Do: Templates accept scan_id, subscription_id, and finding-specific fields

**Story ACA-07-004 -- Template Content from Patterns**
- Do: Content sourced from 12-IaCscript.md patterns

#### Tuesday: ZIP Packaging + Blob Storage

**Story ACA-07-005 -- Generate IaC Artifacts**
- D: Read generator.py
- Do: Generate all IaC artifacts for a scan's findings
- C: Correct template selected per finding type

**Story ACA-07-006 -- ZIP Assembly**
- Do: ZIP with findings.json manifest at root
- C: findings.json lists all findings + template mappings

**Story ACA-07-007 -- SHA-256 Signing + Blob Upload**
- Do: SHA-256 hash stored in deliverables container
- Do: Upload to Azure Blob Storage with **168h SAS URL** (7 days per ACA-07-021 fix)
- C: SAS URL valid for download, SHA-256 matches

#### Wednesday: Deliverable Record + Trigger

**Story ACA-07-008 -- SAS URL Endpoint**
- Do: GET /v1/download/:deliverableId returns 168h read-only SAS URL
- C: URL works for download within 7 days

**Story ACA-07-009 -- Deliverable Record**
- Do: Write to Cosmos deliverables container: sasUrl, sha256, artifactCount
- C: Record queryable by subscriptionId

#### Thursday: Backend Observability (Feature 8.2)

**Stories ACA-08-007 through ACA-08-011**

- ACA-08-007: App Insights connection string via KV reference in all Container Apps
- ACA-08-008: Structured JSON logging to Azure Monitor
- ACA-08-009: Custom metrics: scan duration, analysis duration, delivery duration
- ACA-08-010: API errors logged with error_category enum (no raw messages)
- ACA-08-011: Stripe webhook events logged (event type + hashed subscriptionId)

#### Friday: Sprint-008 CHECK + ACT

### Sprint-008 CHECK

- [ ] Delivery pipeline: findings -> IaC templates -> ZIP -> Blob -> SAS URL -> download
- [ ] SHA-256 of downloaded file matches Cosmos deliverable record
- [ ] SAS URL expires after 168h (7 days)
- [ ] App Insights receives structured logs from all 4 services
- [ ] Custom metrics visible in Azure Monitor
- [ ] Evidence: `evidence/sprint-008-check-{timestamp}.json`

### Sprint-008 ACT

- [ ] Update PLAN.md: all Epic 7 + partial Epic 8 stories done
- [ ] MTI target: 75 (advisory gate)

---

## Week 6 / Sprint-009: Observability Completion + i18n/a11y Finish

**Goal**: GA4 + Clarity + alerting live. All 5 locales translated. axe-core CI gate green.  
**Epic Focus**: Epic 8 (complete), Epic 9 (complete)  
**FP Target**: ~90

### Sprint-009 DISCOVER (Monday AM)

- [ ] Review Sprint-008 retrospective
- [ ] Verify App Insights collecting data (prerequisite for frontend telemetry)
- [ ] Read GTM/GA4/Clarity setup requirements
- [ ] Audit i18n translation completeness

### Sprint-009 PLAN (Monday AM)

| Day | Stories | FP | Theme |
|-----|---------|-----|-------|
| Mon | ACA-08-001..006 | 20 | Frontend telemetry: GTM, GA4, Clarity, consent |
| Tue | ACA-08-012..014 | 15 | Alerting: 5xx rate, collector failure, anomaly |
| Wed | ACA-09-007..009 | 20 | i18n translations: fr-CA, pt-BR, es, de + API i18n |
| Thu | ACA-09-010..018 | 25 | a11y: axe-core CI, aria-labels, focus, keyboard tests |
| Fri | Sprint-009 CHECK + ACT | 10 | All 5 locales verified, axe-core green |

### Sprint-009 DO

#### Monday: Frontend Telemetry (Feature 8.1)

- ACA-08-001: GTM container in index.html with consent gating
- ACA-08-002: GA4 tag fires after consent accepted
- ACA-08-003: Clarity tag fires after consent with form field masking ON
- ACA-08-004: All 16 AnalyticsEventName events fired at correct UI points
- ACA-08-005: Consent banner: accept/reject, rejected suppresses all tags
- ACA-08-006: Consent preference respected across page reloads (localStorage)

#### Tuesday: Alerting (Feature 8.3)

- ACA-08-012: Alert: API 5xx > 5% in 5 min -> email
- ACA-08-013: Alert: Collector job failure -> email + Cosmos audit record
- ACA-08-014: Alert: Anomaly rule fires -> owner notified

#### Wednesday: i18n Translations (Feature 9.1 Completion)

- ACA-09-007: fr (fr-CA) translations completed (required for Canadian market)
- ACA-09-008: pt-BR, es, de translations completed (machine translation; professional review Phase 2)
- ACA-09-009: API error messages with Accept-Language support for 5 locales

#### Thursday: Accessibility (Feature 9.2)

- ACA-09-010: axe-core CI check on every PR (0 critical/serious gate)
- ACA-09-011: All icon-only buttons have aria-label in all 5 locales
- ACA-09-012: All form fields have associated label elements
- ACA-09-013: Findings table has proper th scope=col headers
- ACA-09-014: PreFlight status uses both colour and icon/text
- ACA-09-015: Colour contrast >= 4.5:1 for all body text
- ACA-09-016: Focus ring visible and high-contrast on all focusable elements
- ACA-09-017: Skip-to-content link first focusable element
- ACA-09-018: Consent banner keyboard-accessible and screen-reader-labelled

#### Friday: Sprint-009 CHECK + ACT

### Sprint-009 CHECK

- [ ] GA4 real-time dashboard shows events
- [ ] Clarity session replay works (PII sanitized)
- [ ] All 5 locales render correctly (en, fr, pt-BR, es, de)
- [ ] Language selector persists choice across reloads
- [ ] axe-core CI gate passes (0 critical/serious)
- [ ] Keyboard-only walkthrough: Login -> Connect -> Findings completes
- [ ] Evidence: `evidence/sprint-009-check-{timestamp}.json`

### Sprint-009 ACT

- [ ] Update PLAN.md: all Epic 8 + Epic 9 stories done
- [ ] MTI target: 78 (advisory gate)

---

## Week 7 / Sprint-010: Azure Best Practices Catalog + Commercial Hardening Start

**Goal**: Epic 13 rules operational. Security + privacy compliance started.  
**Epic Focus**: Epic 13 (complete), Epic 10 (partial -- security)  
**FP Target**: ~90

### Sprint-010 DISCOVER (Monday AM)

- [ ] Read 18-azure-best library (32 modules)
- [ ] Audit existing rule patterns for integration approach
- [ ] Review security requirements from ACCEPTANCE.md
- [ ] Check current CSP header configuration

### Sprint-010 PLAN (Monday AM)

| Day | Stories | FP | Theme |
|-----|---------|-----|-------|
| Mon | ACA-13-009..012 | 28 | WAF assessment + FinOps rules |
| Tue | ACA-13-013..016 | 16 | Security rules + APIM health |
| Wed | ACA-13-017..019 | 11 | API design + IaC quality gate + tag enforcement |
| Thu | ACA-10-001..006 | 25 | Security: red-team, tenant isolation, webhook sig, CSP |
| Fri | Sprint-010 CHECK + ACT | 10 | MTI high-priority assessment |

### Sprint-010 DO

#### Monday: WAF + FinOps Assessment (Features 13.1, 13.2)

- ACA-13-009: GET /v1/assessment/waf -- scores subscription against 5 WAF pillars
  - Source: 18-azure-best/02-well-architected/waf-overview.md
  - C: Returns pillar_scores dict (reliability, security, cost, ops, performance), each 0-100

- ACA-13-010: WAF reliability pillar rules (APRL checklist)
  - Source: 18-azure-best/05-resiliency/aprl.md
  - C: Maps >= 5 APRL items to findings

- ACA-13-011: FinOps advisor rules R-13 to R-17
  - Source: 18-azure-best/08-finops/
  - C: 5 new rules pass unit tests

- ACA-13-012: Idle resource detection
  - Source: 18-azure-best/08-finops/cost-optimization.md
  - C: Detects VMs stopped but not deallocated; effort_class=trivial

#### Tuesday: Security + APIM Rules (Features 13.3, 13.4)

- ACA-13-013: RBAC hygiene check -- flags Contributor/Owner > 5 principals
- ACA-13-014: Key Vault access policy audit -- detects non-RBAC mode
- ACA-13-015: MCSB control compliance check via Defender score REST API
- ACA-13-016: APIM rate-limit policy health check -- detects APIs without rate-limit

#### Wednesday: IaC Quality + Epic 13 Completion (Feature 13.5)

- ACA-13-017: API design compliance check (versioning, idempotency, error codes)
- ACA-13-018: PSRule for Azure gate on all Bicep templates (CI gate, existing violations suppressed)
- ACA-13-019: Best-practice tag enforcement (cost-center, environment, owner mandatory)

#### Thursday: Commercial Hardening -- Security (Feature 10.1)

- ACA-10-001: Red-team agent: Tier 1 token against findings API, assert no narrative/deliverable_template_id
  - D: Read redteam-agent.yaml
  - Do: Automated red-team test in CI
  - C: Tier 1 never leaks Tier 2/3 data

- ACA-10-002: Tenant isolation: partition key enforcement in integration tests
  - Do: Attempt cross-tenant access, verify 403
  - C: No tenant A can access tenant B data

- ACA-10-003: Stripe webhook signature verified on every event (whsec_ secret)
- ACA-10-004: Admin endpoints protected by bearer token rotation schedule
- ACA-10-005: All Cosmos queries parameterized (no string concatenation)
- ACA-10-006: CSP header: scripts from GTM/Stripe/Clarity only, no inline

#### Friday: Sprint-010 CHECK + ACT

### Sprint-010 CHECK

- [ ] Epic 13: All 11 stories done, best practices assessment operational
- [ ] Red-team test passes (Tier 1 never leaks Tier 2/3 data)
- [ ] Tenant isolation verified (cross-tenant access blocked)
- [ ] CSP header enforced (no inline scripts)
- [ ] Evidence: `evidence/sprint-010-check-{timestamp}.json`

### Sprint-010 ACT

- [ ] MTI target: 82 (high-priority gate -- fix critical gaps if below)

---

## Week 8 / Sprint-011: Commercial Hardening Completion + Acceptance Gates + Go-Live

**Goal**: All 12 P1 acceptance gates pass. MTI >= 87. Phase 1 production-ready.  
**Epic Focus**: Epic 10 (complete privacy/support), Epic 12 (sync), P1 acceptance verification  
**FP Target**: ~80

### Sprint-011 DISCOVER (Monday AM)

- [ ] Review Sprint-010 retrospective and MTI result
- [ ] Audit privacy compliance requirements (PIPEDA, GDPR)
- [ ] Read ACCEPTANCE.md for all 12 P1 gates
- [ ] Check data model sync state

### Sprint-011 PLAN (Monday AM)

| Day | Stories | FP | Theme |
|-----|---------|-----|-------|
| Mon | ACA-10-007..012 | 20 | Privacy compliance: policy, terms, data retention, GDPR |
| Tue | ACA-10-013..015, ACA-12-001..008 | 20 | Support docs + Data model sync |
| Wed | P1-01..P1-06 verification | 15 | Acceptance: Infra, API, Collection, Analysis, Tier, Stripe |
| Thu | P1-07..P1-12 verification | 15 | Acceptance: Delivery, Frontend, APIM, a11y, i18n, CI |
| Fri | Go-live readiness | 10 | Final MTI push, deployment runbook, evidence pack |

### Sprint-011 DO

#### Monday: Privacy Compliance (Feature 10.2)

- ACA-10-007: Privacy policy at /privacy in all 5 locales
- ACA-10-008: Terms of service at /terms in all 5 locales
- ACA-10-009: Data retention: scans/inventories/cost-data TTL = 7,776,000s (90 days)
- ACA-10-010: DELETE /v1/auth/disconnect hard-deletes all Cosmos docs for subscriptionId
- ACA-10-011: GA4 data retention 14 months, IP anonymization enabled
- ACA-10-012: Clarity data retention respects GDPR right-to-be-forgotten

#### Tuesday: Support Docs + Data Model Sync

**Feature 10.3 -- Support**
- ACA-10-013: docs/client-access-guide.md at /docs/access-guide in 5 locales
- ACA-10-014: FAQ page (top 10 support questions from preflight failure analysis)
- ACA-10-015: Status page (uptime) linked from footer

**Epic 12 -- Data Model Sync** (ongoing, close out for Phase 1)
- ACA-12-001: All epics/features/stories seeded into data model stories layer
- ACA-12-002: Story status (not-started / in-progress / done) maintained
- ACA-12-003: Status updated at start/end of each work item
- ACA-12-004: Agent-summary reflects overall completion percentage
- ACA-12-005: Feature flags layer gates unreleased features
- ACA-12-006: Rules layer matches services/analysis/app/rules/ (now 12+ rules)
- ACA-12-007: Endpoints layer in sync with all shipped routes
- ACA-12-008: Containers layer reflects actual Cosmos schema (11 containers)

#### Wednesday: Acceptance Gates P1-01 through P1-06

**GATE P1-01 -- Infrastructure**
- [ ] P1-01a: main.bicep deploys to EsDAICoE-Sandbox
- [ ] P1-01b: All **11** Cosmos containers exist in aca-db
- [ ] P1-01c: All secrets in marcosandkv20260203
- [ ] P1-01d: API Container App has managed identity with KV read
- [ ] P1-01e: GitHub Actions OIDC federated credential configured
- [ ] P1-01f: deploy-phase1.yml deploys all 4 Container Apps

**GATE P1-02 -- API Startup**
- [ ] P1-02a: GET /health returns 200 with status ok
- [ ] P1-02b: All routers load without ImportError
- [ ] P1-02c: Cosmos connection validated on startup
- [ ] P1-02d: Settings load from KV references

**GATE P1-03 -- Data Collection**
- [ ] P1-03a: Preflight returns PASS or PASS_WITH_WARNINGS
- [ ] P1-03b: Full collection < 10 minutes
- [ ] P1-03c-e: inventories, cost-data, advisor containers have documents
- [ ] P1-03f: Scan status = succeeded

**GATE P1-04 -- Analysis Engine**
- [ ] P1-04a: All 12 rules run without unhandled exception
- [ ] P1-04b: >= 3 rules produce findings
- [ ] P1-04c: Correct partition_key on findings
- [ ] P1-04d: AnalysisRun status = succeeded
- [ ] P1-04e: findingsSummary.findingCount > 0

**GATE P1-05 -- Tier Gating (CRITICAL)**
- [PASS] P1-05a: gate_findings() exists
- [ ] P1-05b-c: Tier 1 excludes narrative + deliverable_template_id
- [ ] P1-05d: Tier 2 includes narrative
- [ ] P1-05e: Tier 3 includes deliverable_template_id
- [ ] P1-05f: Red-team assertion passes
- [ ] P1-05g: No cross-tenant data leak

**GATE P1-06 -- Stripe Integration**
- [ ] P1-06a: POST /v1/checkout/tier2 returns Stripe URL
- [ ] P1-06b: Completed checkout fires webhook
- [ ] P1-06c-d: Entitlement created with correct tier
- [ ] P1-06e: Tier 2 findings include narrative
- [ ] P1-06f: Subscription deleted -> downgrade to tier 1 (preserving Tier 3 per ACA-06-018)
- [ ] P1-06g: Webhook signature verification rejects invalid Stripe-Signature

#### Thursday: Acceptance Gates P1-07 through P1-12

**GATE P1-07 -- Delivery (Tier 3)**
- [ ] P1-07a: Tier 3 payment triggers delivery
- [ ] P1-07b: >= 1 IaC artifact generated
- [ ] P1-07c: ZIP uploaded to Blob
- [ ] P1-07d: 168h SAS URL works for download
- [ ] P1-07e: findings.json at ZIP root
- [ ] P1-07f: SHA-256 matches downloaded file

**GATE P1-08 -- Frontend (Tier 1 flow)**
- [ ] P1-08a: Landing page with tier cards and "Start Free Scan" CTA
- [ ] P1-08b: Sign-in via Entra ID
- [ ] P1-08c: Connect subscription (Mode A delegated)
- [ ] P1-08d: PreFlight shows probes with PASS/WARN/FAIL

**GATE P1-09 -- APIM**
- [ ] JWT validation on all /v1/* routes
- [ ] Tier enforcement (Tier 1 blocked from Tier 2+ endpoints)
- [ ] Entitlement caching (60s TTL)
- [ ] Throttling (100 req/min per subscription)

**GATE P1-10 -- Accessibility**
- [ ] axe-core CI gate green (0 critical/serious)
- [ ] Keyboard-only walkthrough passes (Login -> Connect -> Findings)
- [ ] All icon buttons have aria-labels in 5 locales

**GATE P1-11 -- i18n**
- [ ] Language selector switches between 5 locales
- [ ] All strings translated (no hardcoded EN)
- [ ] Dates and currency locale-aware (Intl.DateTimeFormat, Intl.NumberFormat)

**GATE P1-12 -- CI Pipeline**
- [ ] ruff lint passes (0 errors)
- [ ] mypy passes (no unresolved types)
- [ ] pytest passes (95%+ coverage across analysis rules)
- [ ] axe-core passes (0 critical/serious)

#### Friday: Go-Live Readiness

### Sprint-011 CHECK (MANDATORY GATE -- MTI >= 87)

- [ ] Run veritas audit: MTI >= 87
- [ ] All 12 P1 acceptance gates: ALL PASS
- [ ] Evidence pack: all 8 weeks of evidence receipts
- [ ] Deployment runbook created (step-by-step deploy, smoke test, monitor)
- [ ] Rollback plan documented (revert to previous Container Apps revision)
- [ ] All pre-flight stories resolved (ACA-06-021 duplicate webhook fixed)

**If MTI < 87**: Remediate. Do not deploy.

### Sprint-011 ACT

- [ ] Update STATUS.md: Phase 1 READY FOR DEPLOYMENT
- [ ] Create `docs/8-WEEK-BUILD-COMPLETE-{timestamp}.md`
- [ ] Generate deployment evidence pack
- [ ] Write `docs/SPRINT-011-RETROSPECTIVE.md`
- [ ] Begin Phase 2 planning (Epic 11 + Epic 15)

---

## Evidence Gates Summary

### Per-Sprint Evidence Requirements

| Sprint | Week | Evidence Files | Quality Gate |
|--------|------|----------------|--------------|
| S-004 | 1 | sprint-004-check.json | 12/12 rules complete, auth endpoints live |
| S-005 | 2 | sprint-005-check.json | 25+ API endpoints, APIM deployed, 95% rule coverage |
| S-006 | 3 | sprint-006-check.json | Spark frontend, Tier 1 flow end-to-end |
| S-007 | 4 | sprint-007-mti-gate.json | **MANDATORY: MTI >= 72**, admin + i18n + a11y |
| S-008 | 5 | sprint-008-check.json | Delivery pipeline operational, observability wired |
| S-009 | 6 | sprint-009-check.json | GA4 + Clarity live, 5 locales, axe-core green |
| S-010 | 7 | sprint-010-check.json | Best practices catalog, security hardening |
| S-011 | 8 | sprint-011-go-live.json | **MANDATORY: MTI >= 87**, 12 P1 gates ALL PASS |

### Mandatory Evidence per Story

Every story implementation must produce:
1. **Commit**: Message includes `# EVA-STORY: ACA-XX-NNN`
2. **Tests**: pytest passes for affected module
3. **Evidence JSON** (weekly batch): timestamp, stories completed, test results

---

## Risk Register

| Risk | Impact | Prob | Mitigation | Sprint |
|------|--------|------|------------|--------|
| MTI < 72 at Week 4 | HIGH | MED | Daily evidence capture, gap remediation priority | S-007 |
| Cross-tenant data leak | CRIT | LOW | Partition key enforcement + red-team (ACA-10-001/002) | S-010 |
| Stripe webhook replay | CRIT | LOW | HMAC validation + idempotency (already DONE in Epic 6) | -- |
| Frontend i18n quality | MED | MED | Machine translation Phase 1, professional review Phase 2 | S-009 |
| Analysis rule crash | MED | MED | Isolated error handling (ACA-03-002, DONE) | -- |
| Delivery generation timeout | MED | LOW | Async job + 3x retry | S-008 |
| MTI < 87 at Week 8 | HIGH | LOW | Week 7 high-priority gate catches early | S-011 |
| APIM tier bypass | CRIT | LOW | Red-team tests + APIM policy audit | S-010 |
| 5-locale translation gaps | MED | MED | Validate all keys present per locale in CI | S-009 |

---

## Success Metrics

### Week 8 Operational Targets

| Metric | Target | Baseline (3/11) | Delta |
|--------|--------|-----------------|-------|
| MTI Score | 87 | 57 | +30 |
| Test Coverage | 95% | ~70% | +25% |
| API Response p99 | < 500ms | N/A | Measure |
| Collection Time (500 resources) | < 10 min | N/A | Measure |
| Analysis Time (12 rules) | < 5 min | N/A | Measure |
| axe-core Violations | 0 critical/serious | Unknown | 0 |
| P1 Acceptance Gates | 12/12 PASS | 1/12 | +11 |
| Locales Functional | 5/5 | 0/5 | +5 |

### Business Targets (Post-Launch)

| Metric | Target | Method |
|--------|--------|--------|
| First external scan | Within 1 week | GA4 tracking |
| Tier 2 conversion | 5% of Tier 1 | Stripe + GA4 |
| Tier 3 conversion | 20% of Tier 2 | Stripe + GA4 |
| Avg findings/scan | 8-12 | Analysis summary |
| Avg saving/scan | CAD $30K-$80K | Findings aggregate |

---

## Deferred Work (Post-Phase 1)

### Epic 11 -- Phase 2 Infrastructure (Sprint-012+, 100 FP)
- ACA-11-001..009: Terraform provisioning, custom domain, Cosmos geo-replicas, DNS cutover
- Private subscription with OIDC GitHub Actions

### Epic 15 -- Onboarding System (Sprint-014+, 72 FP)
- ACA-15-000..012: 7-gate state machine, CLI, FastAPI backend, Azure SDK wrappers
- Evidence receipt generation (HMAC-SHA256), React UI integration

### Phase 2 Enhancements
- Terraform template generation (Tier 3 delivery addition)
- Professional translator review (5 locales)
- Intercom or equivalent support widget
- Advanced GA4 analytics (custom dimensions, cohort analysis)
- Multi-region Cosmos (canadacentral primary + 2 failover)

---

## Appendix A: DONE Epics (Not Re-Planned)

These epics are complete per PLAN.md WBS. Not scheduled in this plan.

| Epic | Title | Stories | FP | Status | Sprints |
|------|-------|---------|-----|--------|---------|
| 1 | Foundation and Infrastructure | 21 | 65 | DONE | S-000..002 |
| 2 | Data Collection Pipeline | 17 | 70 | DONE | S-000..002 |
| 6 | Monetization and Billing | 18 | 65 | DONE | S-000..002 |
| 14 | DPDCA Cloud Agent (most) | 13 | 50 | ~95% DONE | S-003..011 |
| Pre-flight | Critical bug fixes | 5 | 9 | DONE | Pre-flight |

Total DONE: ~74 stories, ~259 FP (not re-planned, saving ~3 weeks of capacity)

## Appendix B: Story ID Cross-Reference

All story IDs in this plan reference actual PLAN.md v0.7.0 entries.

| Plan Section | PLAN.md Stories | Count |
|-------------|-----------------|-------|
| Week 1 (S-004) | ACA-03-019..022, ACA-04-001..010 | ~14 |
| Week 2 (S-005) | ACA-04-011..027, ACA-03-020..033, ACA-12-001..004 | ~30 |
| Week 3 (S-006) | ACA-05-001..034 | ~34 |
| Week 4 (S-007) | ACA-05-021..042, ACA-09-001..006 | ~28 |
| Week 5 (S-008) | ACA-07-001..009, ACA-08-007..011 | ~14 |
| Week 6 (S-009) | ACA-08-001..006, ACA-08-012..014, ACA-09-007..018 | ~21 |
| Week 7 (S-010) | ACA-13-009..019, ACA-10-001..006 | ~17 |
| Week 8 (S-011) | ACA-10-007..015, ACA-12-001..008, P1-01..P1-12 | ~20 |

**Total stories scheduled**: ~178 (of 281 total; ~103 already DONE)

---

*Plan v2.0 -- Generated by Opus 4.6 critical review. Replaces v1.0. All story IDs verified against PLAN.md v0.7.0. v1.0 archived as 8-WEEK-BUILD-PLAN-20260311-v1.md.*
