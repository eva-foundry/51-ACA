# Project 51 (ACA) - 8-Week Build Plan

**Generated**: March 11, 2026 @ 06:30 AM ET  
**Session**: 45 (EVA Autonomous Factory Planning)  
**Method**: DPDCA-driven sprint planning informed by 9 reference projects  
**Target**: Phase 1 production deployment (marco* sandbox)

---

## Executive Summary

**Baseline State** (March 11, 2026):
- MTI Score: 57/100 (needs 70+ for deploy gate)
- Sprint: Sprint-003 active (281 stories, 95.7% coverage, 92.9% evidence)
- Infrastructure: Phase 1 Bicep exists, 4 services scaffolded
- Frontend: React SPA foundation with i18n
- Analysis Rules: 8/12 implemented (R-01 through R-08 done, R-09 through R-12 planned)
- APIM: Tier gating infrastructure exists but not fully wired
- Stripe: Integration scaffolded, webhooks need hardening

**Build Strategy**:
- **Weeks 1-2**: Infrastructure + API foundation (40, 41 patterns)
- **Weeks 3-4**: Frontend + Collector (31, 45, 46, 50 patterns)
- **Weeks 5-6**: Analysis + Tier gating (38, 39, 49 patterns)
- **Weeks 7-8**: Delivery + DPDCA compliance (48 pattern)

**Success Criteria**:
- MTI > 70 (deploy gate pass)
- All 15 Phase 1 acceptance gates passing
- 12/12 analysis rules operational
- Full Tier 1/2/3 flow validated end-to-end

---

## Reference Project Patterns Applied

### Pattern Matrix

| Pattern | Source | Priority | Weeks Applied | Why Critical for P51 |
|---------|--------|----------|---------------|---------------------|
| **APIM tier gating** | P39 | HIGH | 5, 6 | Tier 1/2/3 enforcement without backend complexity |
| **Evidence ID spine** | P40 | HIGH | 1, 7, 8 | Link Stripe payment → collector → analysis → delivery |
| **Adapter pattern** | P41 | HIGH | 2, 4 | Test without Stripe/Azure/Cosmos — mock adapters |
| **Dual store (Cosmos/local)** | P40 | MEDIUM | 1, 2 | Local dev with SQLite, cloud with Cosmos — toggle via env |
| **i18n from day 1** | P45 | HIGH | 3 | EN/FR bilingual (react-i18next + browser-languagedetector) |
| **Template CRUD pages** | P31 | MEDIUM | 3 | AdminListPage pattern — 80% less boilerplate |
| **Policy-as-code (YAML)** | P49 | MEDIUM | 5 | Tier rules, finding classifications editable without deploy |
| **Webhook bridge** | P38 | HIGH | 6 | Stripe webhook → Azure Function → Cosmos (3-system decoupling) |
| **Watchdog health checks** | P50 | MEDIUM | 4, 7 | Collector/analysis jobs need auto-restart on failure |
| **Mock backend layer** | P31 | HIGH | 3 | VITE_USE_MOCK_DATA=true enables frontend dev without backend |
| **MTI quality gates** | P48 | HIGH | 7, 8 | Evidence at every stage, exit code contract, dual logging |

### Top 10 Tactical Patterns

1. **Bicep Modules** (P40): Separate modules for Cosmos, ACA, APIM, Key Vault
2. **FastAPI Router Groups** (P40): 6 routers (health, auth, scans, findings, checkout, admin)
3. **Pydantic Settings** (P40, P41): Config from env/KV, validation at startup
4. **Cosmos Partition Strategy** (P40): `partition_key=/subscriptionId` for tenant isolation
5. **Evidence at Every Stage** (P48): JSON + logs + timestamped files
6. **ASCII-Only Output** (P48): `[PASS]` `[FAIL]` `[INFO]` instead of emoji
7. **Exit Code Contract** (P48): 0=success, 1=business fail, 2=technical error
8. **Pre-Flight Checks** (P48): Validate before run (API reachable, files exist, deps installed)
9. **Idempotent Receipts** (P41): Same operation twice = same result, receipt recorded
10. **GC Design System** (P31): Fluent UI v9 wrappers for WCAG 2.1 AA compliance

---

## Week 1-2: Infrastructure and API Foundation

**Goal**: All 4 services boot cleanly. Local dev stack works. Phase 1 infra wired.

### Week 1 (March 11-15, 2026)

#### Monday 3/11: Infrastructure Audit & Foundation

**DISCOVER**:
- [x] Read current Bicep templates (`infra/phase1-marco/main.bicep`)
- [ ] Audit existing Cosmos containers (7 defined, verify schema per PLAN.md)
- [ ] Review Key Vault secret structure (`marcosandkv20260203`)
- [ ] Check managed identity assignments (API → KV, Collector → Cosmos)
- [ ] Validate Container Apps environment configuration

**PLAN**:
- [ ] Document current vs. target infra state (gap analysis)
- [ ] Design Bicep module structure (P40 pattern: separate modules per resource)
- [ ] Define RU/s allocation per container (from ARCHITECTURE-REVIEW-GAPS-IMPROVEMENTS.md)
- [ ] Create TTL policy matrix (onboarding-sessions: 90d, extraction-logs: 30d, evidence: NEVER)
- [ ] Plan RBAC model (managed identity vs. service principal)

**DO** (Epic 1 Stories):
- [ ] **ACA-01-010**: Refactor `main.bicep` into modular structure:
  - `cosmos.bicep` (7 containers + partition keys + RU/s + TTL)
  - `keyvault.bicep` (secrets + access policies)
  - `containerapps.bicep` (environment + 4 apps + 3 jobs)
  - `apim.bicep` (product + APIs + policies)
- [ ] **ACA-01-011**: Generate all secrets in `marcosandkv20260203` with documentation
- [ ] **ACA-01-012**: Configure managed identity for API (KV read, Cosmos read/write)
- [ ] **ACA-01-013**: Configure managed identity for Collector (Cosmos read/write only)

**CHECK**:
- [ ] `az deployment group validate` passes for all modules
- [ ] All 7 containers created with correct partition_key
- [ ] Secrets retrievable via managed identity (test with az CLI)
- [ ] Evidence: `evidence/infra-validation-20260311.json`

**ACT**:
- [ ] Update PLAN.md stories ACA-01-010 through ACA-01-013 status=done
- [ ] Document lessons in `docs/INFRA-PATTERNS.md`

#### Tuesday 3/12: API Service Bootstrap

**DISCOVER**:
- [ ] Read existing API code (`services/api/app/main.py`, routers, deps)
- [ ] Audit current endpoint count (how many routes, how many implemented?)
- [ ] Review auth middleware (`app/deps/auth.py`, `app/auth/session.py`)
- [ ] Check Cosmos client initialization (`app/db/cosmos.py`)

**PLAN**:
- [ ] Design adapter pattern for Cosmos (P41: test with SQLite, prod with Cosmos)
- [ ] Define settings schema (Pydantic, from env/KV)
- [ ] Document 6 router groups with endpoint inventory
- [ ] Plan health check structure (liveness, readiness, Cosmos connectivity)

**DO** (Epic 4 Stories):
- [ ] **ACA-04-001**: Create `CosmosAdapter` base class with `SQLiteAdapter` and `AzureCosmosAdapter` implementations
- [ ] **ACA-04-002**: Implement settings.py with Pydantic Settings (all env vars documented)
- [ ] **ACA-04-003**: Enhance `/health` endpoint with Cosmos connectivity check + version
- [ ] **ACA-04-004**: Create startup validation (check KV secrets, test Cosmos connection, fail-fast if missing)

**CHECK**:
- [ ] `pytest services/api/tests/` passes (all existing tests)
- [ ] `curl http://localhost:8080/health` returns 200 with `cosmos_connected: true`
- [ ] Local dev works with `USE_SQLITE=true` (no Azure deps)
- [ ] Evidence: `evidence/api-bootstrap-20260312.json`

**ACT**:
- [ ] Update STATUS.md with API bootstrap complete
- [ ] Document adapter pattern in `docs/API-PATTERNS.md`

#### Wednesday 3/13: Auth & Session Management

**DISCOVER**:
- [ ] Review MSAL client implementation (`app/auth/msal_client.py`)
- [ ] Audit session management (`app/auth/session.py`)
- [ ] Check JWT validation logic
- [ ] Read entitlement service (`app/services/entitlement_service.py`)

**PLAN**:
- [ ] Design evidence ID spine format (P40: `GH<run>-PR<pr>-<sha>` → `SCAN-<uuid>-<timestamp>`)
- [ ] Define session lifecycle (create, validate, expire, revoke)
- [ ] Document auth flow: redirect → callback → token → session
- [ ] Plan token refresh strategy (JWT expiry, refresh tokens)

**DO** (Epic 4 Stories):
- [ ] **ACA-04-005**: Implement evidence ID generation (`generate_evidence_id()` in utils)
- [ ] **ACA-04-006**: Enhance session management with evidence ID linking
- [ ] **ACA-04-007**: Add session validation middleware (inject `current_user` in request context)
- [ ] **ACA-04-008**: Implement token refresh endpoint

**CHECK**:
- [ ] Auth flow walkthrough: sign-in → callback → `/auth/me` returns user info
- [ ] Evidence ID format validated: `SCAN-{uuid4}-{yyyyMMddHHmmss}`
- [ ] Session expires after configured TTL
- [ ] Evidence: `evidence/auth-validation-20260313.json`

#### Thursday 3/14: Cosmos Repository Pattern

**DISCOVER**:
- [ ] Audit existing repos (`app/db/repos/*.py`)
- [ ] Check partition key usage across all Cosmos calls
- [ ] Review error handling (retry logic, transient failures)

**PLAN**:
- [ ] Design base repository pattern (CRUD + query helpers)
- [ ] Define consistent error handling (404, 409, 503 patterns)
- [ ] Document query patterns (by partition key, cross-partition)
- [ ] Plan idempotent operations (upsert semantics)

**DO** (Epic 1 Stories):
- [ ] **ACA-01-016**: Create `BaseRepository` with CRUD methods
- [ ] **ACA-01-017**: Implement retry logic (exponential backoff, 3 attempts)
- [ ] **ACA-01-018**: Add query helpers (`find_by_partition`, `find_one`, `find_all`)
- [ ] **ACA-01-019**: Enhance all 5 existing repos to extend `BaseRepository`

**CHECK**:
- [ ] All repos have consistent error handling
- [ ] Retry logic tested (mock 429 response, verify 3 retries)
- [ ] Cross-partition queries logged (performance warning)
- [ ] Evidence: `evidence/cosmos-repos-20260314.json`

#### Friday 3/15: CI Pipeline & Week 1 Wrap

**DISCOVER**:
- [ ] Review `.github/workflows/ci.yml`
- [ ] Check test coverage (current: how many tests, what coverage %)
- [ ] Audit linting rules (ruff, mypy)

**PLAN**:
- [ ] Design evidence gates for CI (must capture: test results, coverage %, lint errors)
- [ ] Define exit code semantics (0=pass, 1=test fail, 2=build error)
- [ ] Document required checks (ruff, mypy, pytest, axe-core)

**DO** (Epic 1 Stories):
- [ ] **ACA-01-006**: Enhance CI with evidence capture (JSON output for all steps)
- [ ] **ACA-01-007**: Add mypy strict mode (no implicit Any)
- [ ] **ACA-01-008**: Enforce 80% test coverage gate
- [ ] **ACA-01-009**: Add axe-core a11y check placeholder (runs on frontend)

**CHECK**:
- [ ] CI runs in < 5 minutes
- [ ] Evidence artifact uploaded to GitHub Actions
- [ ] All checks passing (4/4 green)
- [ ] Evidence: `evidence/ci-week1-20260315.json`

**ACT**:
- [ ] Update STATUS.md: Week 1 complete, API foundation solid
- [ ] Document Week 1 lessons in `docs/WEEK1-RETROSPECTIVE.md`

**Week 1 MTI Target**: 62/100 (up from 57)

---

### Week 2 (March 18-22, 2026)

#### Monday 3/18: Collector Service Foundation

**DISCOVER**:
- [ ] Read collector code (`services/collector/app/main.py`, `ingest.py`)
- [ ] Review Azure SDK usage (Resource Graph, Cost Management, Advisor)
- [ ] Check preflight probes (`app/preflight.py`)

**PLAN**:
- [ ] Design collector state machine (queued → running → succeeded/failed)
- [ ] Define evidence capture points (5 probes, inventory count, cost rows, advisor recs)
- [ ] Document timeout policies (per-API call, total collection)
- [ ] Plan watchdog integration (P50: health checks + auto-restart)

**DO** (Epic 2 Stories):
- [ ] **ACA-02-001**: Implement preflight probe results model (PASS/WARN/FAIL with explanation)
- [ ] **ACA-02-002**: Add clear error messages for missing roles (Cost Management Reader, Reader)
- [ ] **ACA-02-003**: Implement PASS_WITH_WARNINGS flow (collection proceeds, warnings logged)
- [ ] **ACA-02-004**: Add `--preflight-only` flag (validate without collecting)

**CHECK**:
- [ ] Preflight against test subscription returns structured results
- [ ] All 5 probes tested (Reader, Cost Manager, Network, Advisor, Policy)
- [ ] Evidence: `evidence/collector-preflight-20260318.json`

#### Tuesday 3/19: Resource Inventory Collection

**DISCOVER**:
- [ ] Review Resource Graph queries (`app/resource_graph.py`)
- [ ] Check inventory schema (what fields captured?)
- [ ] Audit timeout handling (60s limit met?)

**PLAN**:
- [ ] Design pagination strategy (Resource Graph 1000-record limit)
- [ ] Define inventory enrichment (tags, SKU, costs)
- [ ] Document evidence capture (JSON per collection run)

**DO** (Epic 2 Stories):
- [ ] **ACA-02-005**: Enhance Resource Graph query (capture SKU, region, resource group, tags)
- [ ] **ACA-02-006**: Implement pagination (handle > 1000 resources)
- [ ] **ACA-02-007**: Add inventory enrichment (tag extraction, SKU parsing)

**CHECK**:
- [ ] Collection succeeds for 500-resource subscription in < 60s
- [ ] All resource types captured (compute, storage, network)
- [ ] Evidence: `evidence/collector-inventory-20260319.json`

#### Wednesday 3/20: Cost Data Collection

**DISCOVER**:
- [ ] Review Cost Management API usage
- [ ] Check cost row schema (MeterCategory, PreTaxCost)
- [ ] Audit rate limiting handling (429 retry)

**PLAN**:
- [ ] Design 91-day cost query (daily granularity)
- [ ] Define retry strategy (exponential backoff, 3 attempts max)
- [ ] Document cost row deduplication (same date+meter = overwrite)

**DO** (Epic 2 Stories):
- [ ] **ACA-02-008**: Implement 91-day cost query with pagination
- [ ] **ACA-02-009**: Add cost row enrichment (MeterCategory, resourceGroup, date)
- [ ] **ACA-02-010**: Implement rate limiting handler (429 → wait → retry)

**CHECK**:
- [ ] Cost collection for 91 days completes in < 5 minutes
- [ ] All cost rows have PreTaxCost > 0 (filter zero-cost rows)
- [ ] Evidence: `evidence/collector-cost-20260320.json`

#### Thursday 3/21: Advisor & Policy Collection

**DISCOVER**:
- [ ] Review Advisor API calls
- [ ] Check Policy Insights API usage
- [ ] Audit data normalization (category mapping)

**PLAN**:
- [ ] Design Advisor recommendation schema
- [ ] Define Policy compliance aggregation (compliant/non-compliant counts)
- [ ] Document network signals collection (NSG, DNS, VNet)

**DO** (Epic 2 Stories):
- [ ] **ACA-02-011**: Implement Advisor recommendations collection (all categories)
- [ ] **ACA-02-012**: Add Policy compliance state aggregation
- [ ] **ACA-02-013**: Implement network signals (NSG rules, public IPs, VNet peering)

**CHECK**:
- [ ] Advisor recs captured (Cost, Security, Performance, Reliability)
- [ ] Policy compliance counts match Azure Portal
- [ ] Evidence: `evidence/collector-advisor-20260321.json`

#### Friday 3/22: Collection Lifecycle & Week 2 Wrap

**DISCOVER**:
- [ ] Review scan status updates (Cosmos writes)
- [ ] Check analysis trigger (ACA-02-017 implementation)

**PLAN**:
- [ ] Design analysis job trigger (webhook, API call, or queue message)
- [ ] Define graceful degradation (trigger skipped if ACA_ANALYSIS_JOB_NAME not set)
- [ ] Document collection stats (inventoryCount, costRows, advisorRecs)

**DO** (Epic 2 Stories):
- [ ] **ACA-02-014**: Implement scan status updates (queued → running → succeeded/failed)
- [ ] **ACA-02-015**: Add collection stats to scan record
- [ ] **ACA-02-016**: Implement GET `/v1/scans/:scanId` for frontend polling
- [ ] **ACA-02-017**: Add analysis job trigger (via azure.mgmt.appcontainers)

**CHECK**:
- [ ] Full collection completes end-to-end (preflight → inventory → cost → advisor → analysis trigger)
- [ ] Analysis job starts automatically after collection
- [ ] Evidence: `evidence/collector-week2-20260322.json`

**ACT**:
- [ ] Update STATUS.md: Week 2 complete, Collector operational
- [ ] Document Week 2 lessons in `docs/WEEK2-RETROSPECTIVE.md`

**Week 2 MTI Target**: 65/100 (up from 62)

---

## Week 3-4: Frontend and Collector Integration

### Week 3 (March 25-29, 2026)

#### Monday 3/25: Frontend Foundation & i18n

**DISCOVER**:
- [ ] Review existing React SPA (`frontend/src/`)
- [ ] Audit i18n setup (react-i18next configuration)
- [ ] Check existing pages (Landing, Connect, Scan, Findings)

**PLAN**:
- [ ] Design page structure (P31 pattern: shared layouts, templates)
- [ ] Define i18n namespace structure (common, landing, findings, errors)
- [ ] Document GC Design System integration (P31: @eva/gc-design-system)
- [ ] Plan mock backend toggle (VITE_USE_MOCK_DATA)

**DO** (Epic 5 Stories):
- [ ] **ACA-05-001**: Create `@aca/ui` shared library (Button, Input, Card wrappers)
- [ ] **ACA-05-002**: Implement i18n with EN/FR support (react-i18next + browser-languagedetector)
- [ ] **ACA-05-003**: Create GCThemeProvider with Canada.ca design tokens
- [ ] **ACA-05-004**: Add language selector component (EN/FR toggle)

**CHECK**:
- [ ] All UI components render in both EN/FR
- [ ] Language selector persists choice to localStorage
- [ ] Evidence: `evidence/frontend-i18n-20260325.json`

#### Tuesday 3/26: Landing & Connect Pages

**DISCOVER**:
- [ ] Review landing page wireframes
- [ ] Check connect flow UX (Mode A/B/C)

**PLAN**:
- [ ] Design tier card component (Free/Advisory/Deliverable)
- [ ] Define connect flow state machine (select mode → auth → verify)
- [ ] Document WCAG 2.1 AA requirements (color contrast, keyboard nav)

**DO** (Epic 5 Stories):
- [ ] **ACA-05-005**: Build landing page (hero, tier cards, CTA)
- [ ] **ACA-05-006**: Implement connect page (3 onboarding modes)
- [ ] **ACA-05-007**: Add consent banner (GA4/Clarity opt-in)
- [ ] **ACA-05-008**: Create mock backend client (VITE_USE_MOCK_DATA=true)

**CHECK**:
- [ ] Landing page Lighthouse score > 90
- [ ] Connect flow completes in < 60 seconds (Mode A)
- [ ] Evidence: `evidence/frontend-landing-20260326.json`

#### Wednesday 3/27: Scan Status & Findings Pages

**DISCOVER**:
- [ ] Review findings table design
- [ ] Check tier gating UI (narrative blur for Tier 1)

**PLAN**:
- [ ] Design findings table component (data grid with sorting/filtering)
- [ ] Define tier gating visual cues (blur, lock icons, CTA)
- [ ] Document polling strategy (scan status, 2s interval)

**DO** (Epic 5 Stories):
- [ ] **ACA-05-009**: Build scan status page (polling, progress bar, stats)
- [ ] **ACA-05-010**: Implement findings table (Tier 1 view: title + saving range)
- [ ] **ACA-05-011**: Add tier gating UI (blur narrative, "Unlock full report" CTA)
- [ ] **ACA-05-012**: Create findings detail drawer (Tier 2/3: full finding)

**CHECK**:
- [ ] Scan status polling works (2s interval, stops on completion)
- [ ] Findings table renders 50+ findings in < 500ms
- [ ] Evidence: `evidence/frontend-findings-20260327.json`

#### Thursday 3/28: Checkout & Billing Integration

**DISCOVER**:
- [ ] Review Stripe checkout integration
- [ ] Check webhook handler (`services/api/app/routers/webhooks.py`)

**PLAN**:
- [ ] Design checkout flow (select tier → Stripe → webhook → entitlement)
- [ ] Define webhook signature validation (HMAC, Stripe-Signature header)
- [ ] Document customer mapping (subscriptionId → Stripe customerId)

**DO** (Epic 6 Stories):
- [ ] **ACA-06-001**: Build checkout page (tier selection, Stripe redirect)
- [ ] **ACA-06-002**: Implement POST `/v1/checkout/tier2` (create Stripe session)
- [ ] **ACA-06-003**: Enhance webhook handler (signature validation, event types)
- [ ] **ACA-06-004**: Add customer mapping (save customerId to Cosmos)

**CHECK**:
- [ ] Stripe test checkout completes successfully
- [ ] Webhook fires and creates entitlement (tier=2)
- [ ] Evidence: `evidence/frontend-checkout-20260328.json`

#### Friday 3/29: Accessibility & Week 3 Wrap

**DISCOVER**:
- [ ] Run axe-core audit (current violations?)
- [ ] Test keyboard navigation (tab order, focus management)

**PLAN**:
- [ ] Design a11y testing strategy (automated + manual)
- [ ] Define WCAG 2.1 AA checklist (color contrast, labels, focus indicators)
- [ ] Document screen reader testing (NVDA/VoiceOver)

**DO** (Epic 9 Stories):
- [ ] **ACA-09-001**: Fix all axe-core critical/serious violations
- [ ] **ACA-09-002**: Add visible focus indicators (all interactive elements)
- [ ] **ACA-09-003**: Implement aria-labels (icon-only buttons, status badges)
- [ ] **ACA-09-004**: Test keyboard-only flow (Landing → Findings, no mouse)

**CHECK**:
- [ ] axe-core CI check passes (0 critical/serious)
- [ ] Full keyboard walkthrough completes
- [ ] Evidence: `evidence/frontend-a11y-20260329.json`

**ACT**:
- [ ] Update STATUS.md: Week 3 complete, Frontend Tier 1 flow operational
- [ ] Document Week 3 lessons in `docs/WEEK3-RETROSPECTIVE.md`

**Week 3 MTI Target**: 68/100 (up from 65)

---

### Week 4 (April 1-5, 2026)

#### Monday 4/1: Mock to Real API Migration

**DISCOVER**:
- [ ] Audit all frontend API calls (using mock vs. real)
- [ ] Check error handling (network failures, 401/403/500)

**PLAN**:
- [ ] Design API client error handling (retry, fallback, user messaging)
- [ ] Define loading states (skeleton screens, spinners)
- [ ] Document feature flags (VITE_USE_MOCK_DATA, VITE_API_URL)

**DO** (Epic 5 Stories):
- [ ] **ACA-05-013**: Switch all API calls to real backend (feature flag: VITE_USE_MOCK_DATA=false)
- [ ] **ACA-05-014**: Add error boundary component (catch React errors)
- [ ] **ACA-05-015**: Implement retry logic (3 attempts, exponential backoff)
- [ ] **ACA-05-016**: Add loading skeletons (findings table, scan status)

**CHECK**:
- [ ] All API calls work with real backend
- [ ] Error states display user-friendly messages
- [ ] Evidence: `evidence/frontend-api-migration-20260401.json`

#### Tuesday 4/2: Watchdog & Health Monitoring

**DISCOVER**:
- [ ] Review collector health checks
- [ ] Check analysis job monitoring

**PLAN**:
- [ ] Design watchdog pattern (P50: logs aggregation, auto-restart)
- [ ] Define health check endpoints (liveness, readiness)
- [ ] Document alerting strategy (API 5xx, collector failures)

**DO** (Epic 8 Stories + P50 pattern):
- [ ] **ACA-08-001**: Add health check endpoints to all 4 services
- [ ] **ACA-08-002**: Implement watchdog script (check health, restart on failure)
- [ ] **ACA-08-003**: Create logs aggregation (Container Apps → Log Analytics)
- [ ] **ACA-08-004**: Add alerting (API 5xx > 5%, collector job failure)

**CHECK**:
- [ ] Watchdog detects failed collector job and restarts
- [ ] Health checks return 200 for all services
- [ ] Evidence: `evidence/watchdog-20260402.json`

#### Wednesday 4/3: Telemetry & Analytics

**DISCOVER**:
- [ ] Review GA4/GTM setup
- [ ] Check Clarity integration
- [ ] Audit PII leakage (no subscriptionId in analytics)

**PLAN**:
- [ ] Design telemetry events (page views, button clicks, funnel drop-offs)
- [ ] Define consent flow (banner, opt-in, suppress analytics)
- [ ] Document privacy policy (what data collected, retention, purpose)

**DO** (Epic 8 Stories):
- [ ] **ACA-08-005**: Integrate GA4 via GTM (page views, custom events)
- [ ] **ACA-08-006**: Add Microsoft Clarity (session replay, heatmaps)
- [ ] **ACA-08-007**: Implement consent banner (opt-in/opt-out)
- [ ] **ACA-08-008**: Add structured logging (App Insights, no PII)

**CHECK**:
- [ ] GA4 real-time dashboard shows events
- [ ] Clarity session replay works (PII sanitized)
- [ ] Evidence: `evidence/telemetry-20260403.json`

#### Thursday 4/4: End-to-End Testing

**DISCOVER**:
- [ ] Review test coverage (current: how many E2E tests?)
- [ ] Check CI integration (E2E tests in pipeline?)

**PLAN**:
- [ ] Design E2E test suite (Playwright, Cypress, or Vitest)
- [ ] Define test scenarios (Tier 1 flow, Tier 2 checkout, Tier 3 download)
- [ ] Document test data strategy (mock subscriptions, fixtures)

**DO** (Epic 1 Stories):
- [ ] **ACA-01-020**: Create E2E test framework (Playwright)
- [ ] **ACA-01-021**: Implement Tier 1 flow test (Landing → Findings)
- [ ] **ACA-01-022**: Add Tier 2 checkout test (mock Stripe webhook)
- [ ] **ACA-01-023**: Create Tier 3 delivery test (verify ZIP download)

**CHECK**:
- [ ] All 3 E2E tests pass in CI
- [ ] Test execution < 10 minutes
- [ ] Evidence: `evidence/e2e-tests-20260404.json`

#### Friday 4/5: Week 4 Wrap & MTI Gate

**DISCOVER**:
- [ ] Run full veritas audit (`node src/cli.js audit --repo 51-ACA`)
- [ ] Check MTI score (target: 68 → 70+)

**PLAN**:
- [ ] Identify MTI gaps (coverage, evidence, consistency)
- [ ] Prioritize gap remediation (quick wins vs. deep work)

**DO**:
- [ ] Fix top 5 MTI gaps (missing evidence, orphan tags)
- [ ] Generate evidence receipts for Week 3-4 work
- [ ] Update all STATUS.md declarations

**CHECK**:
- [ ] MTI score > 70 (deploy gate pass)
- [ ] All Week 1-4 stories marked done
- [ ] Evidence: `evidence/week4-mti-gate-20260405.json`

**ACT**:
- [ ] Update STATUS.md: Week 4 complete, deploy gate passed
- [ ] Document Week 4 lessons in `docs/WEEK4-RETROSPECTIVE.md`

**Week 4 MTI Target**: 72/100 (deploy gate: PASS ✅)

---

## Week 5-6: Analysis Engine and Tier Gating

### Week 5 (April 8-12, 2026)

#### Monday 4/8: Analysis Engine Architecture

**DISCOVER**:
- [ ] Read existing analysis code (`services/analysis/app/rules/*.py`)
- [ ] Audit current rules (8/12 done: R-01 through R-08)
- [ ] Check rule engine (`All_RULES` registry)

**PLAN**:
- [ ] Design remaining 4 rules (R-09 through R-12)
- [ ] Define rule isolation (one failure doesn't stop engine)
- [ ] Document findings schema (category, title, narrative, evidence_refs)

**DO** (Epic 3 Stories):
- [ ] **ACA-03-019**: Implement R-09 (DNS sprawl detection)
- [ ] **ACA-03-020**: Implement R-10 (Savings plan coverage)
- [ ] **ACA-03-021**: Implement R-11 (APIM token budget)
- [ ] **ACA-03-022**: Implement R-12 (Chargeback gap)

**CHECK**:
- [ ] All 12 rules run without error
- [ ] Rule engine handles isolated failures (pytest with mock crashes)
- [ ] Evidence: `evidence/analysis-rules-20260408.json`

#### Tuesday 4/9: Rule Unit Tests (95% Coverage Target)

**DISCOVER**:
- [ ] Audit current test coverage (rule tests: how many? coverage %?)
- [ ] Review fixture strategy (hardcoded JSON vs. dynamic)

**PLAN**:
- [ ] Design test fixtures (one per rule, covering edge cases)
- [ ] Define coverage target (95% line coverage across all 12 modules)
- [ ] Document negative test cases (no findings, partial data)

**DO** (Epic 3 Feature 3.4):
- [ ] **Create test fixtures**: 12 JSON files (one per rule, positive + negative cases)
- [ ] **Implement unit tests**: 12 test files (one per rule, 5+ test cases each)
- [ ] **Add edge case tests**: empty inventory, missing cost data, zero Advisor recs
- [ ] **Measure coverage**: `pytest --cov=services/analysis/app/rules --cov-report=html`

**CHECK**:
- [ ] Coverage > 95% for all 12 rule modules
- [ ] All 60+ tests pass (5 per rule minimum)
- [ ] Evidence: `evidence/analysis-tests-20260409.json`

#### Wednesday 4/10: Findings Assembly & Tier Gating

**DISCOVER**:
- [ ] Review findings assembler code
- [ ] Check tier gating implementation (`services/api/app/services/findings_gate.py`)

**PLAN**:
- [ ] Design findings summary (findingCount, totalSavingLow/High, categories)
- [ ] Define tier gating rules (P39 pattern: APIM-level enforcement)
- [ ] Document field filtering (Tier 1: title only, Tier 2: +narrative, Tier 3: +deliverable)

**DO** (Epic 3 Stories):
- [ ] **ACA-03-001**: Enhance findings assembler (persist all 12 rules output)
- [ ] **ACA-03-002**: Implement rule engine error handling (skip failed rule, log error)
- [ ] **ACA-03-003**: Add findings schema validation (Pydantic model)
- [ ] **ACA-03-004**: Update AnalysisRun status lifecycle (queued → running → succeeded/failed)
- [ ] **ACA-03-005**: Generate findingsSummary (counts, totals, categories)

**CHECK**:
- [ ] All 12 rules produce findings (test suite with mock data)
- [ ] Findings summary matches individual finding totals
- [ ] Evidence: `evidence/analysis-findings-20260410.json`

#### Thursday 4/11: APIM Tier Enforcement

**DISCOVER**:
- [ ] Review APIM policies (`infra/phase1-marco/apim/*.xml`)
- [ ] Check entitlement caching (60s TTL)

**PLAN**:
- [ ] Design APIM policy structure (validate-jwt → rate-limit → response-transform)
- [ ] Define tier enforcement logic (subscription metadata lookup)
- [ ] Document cache invalidation strategy (payment → clear cache)

**DO** (Epic 3 Stories + P39 pattern):
- [ ] **ACA-03-006**: Implement Tier 1 filtering (API returns title + saving range only)
- [ ] **ACA-03-007**: Validate Tier 1 blocking (narrative field never returned)
- [ ] **ACA-03-008**: Implement Tier 2 filtering (API returns +narrative)
- [ ] **ACA-03-009**: Implement Tier 3 filtering (API returns +deliverable_template_id)
- [ ] **ACA-03-010**: Add redteam gate (assert Tier 1 never leaks Tier 2/3 data)

**CHECK**:
- [ ] Tier 1 token → findings without narrative
- [ ] Tier 2 token → findings with narrative
- [ ] Tier 3 token → findings with deliverable_template_id
- [ ] Evidence: `evidence/apim-tier-gating-20260411.json`

#### Friday 4/12: Policy-as-Code (YAML Rules)

**DISCOVER**:
- [ ] Review P49 (eva-dtl) policy YAML pattern

**PLAN**:
- [ ] Design rule configuration YAML (thresholds, categories, effort levels)
- [ ] Define override mechanism (env-specific thresholds)
- [ ] Document rule validation (schema check at startup)

**DO** (P49 pattern):
- [ ] **Create** `config/rules.yaml` (all 12 rules with thresholds)
- [ ] **Implement** YAML loader (validate schema, load at startup)
- [ ] **Refactor** all 12 rules to read thresholds from YAML
- [ ] **Add** override support (`RULE_R01_THRESHOLD_OVERRIDE=2000`)

**CHECK**:
- [ ] All 12 rules load thresholds from YAML
- [ ] Override works (env var takes precedence)
- [ ] Evidence: `evidence/policy-as-code-20260412.json`

**ACT**:
- [ ] Update STATUS.md: Week 5 complete, Analysis engine operational
- [ ] Document Week 5 lessons in `docs/WEEK5-RETROSPECTIVE.md`

**Week 5 MTI Target**: 75/100 (up from 72)

---

### Week 6 (April 15-19, 2026)

#### Monday 4/15: Stripe Webhook Hardening

**DISCOVER**:
- [ ] Review webhook handler security (signature validation)
- [ ] Check event handling (checkout.session.completed, invoice.paid)

**PLAN**:
- [ ] Design webhook bridge pattern (P38: webhook → Function → Cosmos)
- [ ] Define signature validation (Stripe-Signature HMAC)
- [ ] Document event replay protection (idempotency key)

**DO** (Epic 6 Stories + P38 pattern):
- [ ] **ACA-06-005**: Enhance signature validation (reject tampered events)
- [ ] **ACA-06-006**: Implement idempotency (same event twice = same result)
- [ ] **ACA-06-007**: Add event type routing (checkout, invoice, subscription)
- [ ] **ACA-06-008**: Create webhook test suite (mock Stripe events)

**CHECK**:
- [ ] Reject invalid signature (test with wrong HMAC)
- [ ] Duplicate event = same result (no double-charge)
- [ ] Evidence: `evidence/stripe-webhook-20260415.json`

#### Tuesday 4/16: Entitlement Upgrade/Downgrade

**DISCOVER**:
- [ ] Review entitlement service
- [ ] Check subscription lifecycle (create, renew, cancel)

**PLAN**:
- [ ] Design upgrade flow (Tier 1 → Tier 2 → Tier 3)
- [ ] Define downgrade handling (subscription cancelled → Tier 1)
- [ ] Document prorated refunds (Tier 2 → Tier 3 upgrade)

**DO** (Epic 6 Stories):
- [ ] **ACA-06-009**: Implement Tier 1 → Tier 2 upgrade (new subscription)
- [ ] **ACA-06-010**: Implement Tier 2 → Tier 3 upgrade (proration)
- [ ] **ACA-06-011**: Add subscription cancellation (downgrade to Tier 1)
- [ ] **ACA-06-012**: Create billing portal integration (Stripe customer portal)

**CHECK**:
- [ ] Upgrade flow completes (Tier 1 → Tier 2 → back to Tier 2 findings)
- [ ] Downgrade resets tier (cancelled subscription → Tier 1)
- [ ] Evidence: `evidence/entitlement-lifecycle-20260416.json`

#### Wednesday 4/17: Customer Mapping & Data Isolation

**DISCOVER**:
- [ ] Review customer mapping strategy
- [ ] Check cross-tenant isolation (partition key enforcement)

**PLAN**:
- [ ] Design customer mapping (subscriptionId ↔ Stripe customerId)
- [ ] Define data isolation tests (attempt cross-tenant access)
- [ ] Document partition key strategy (every query uses subscriptionId)

**DO** (Epic 6 Stories):
- [ ] **ACA-06-013**: Implement customer mapping (save to Cosmos)
- [ ] **ACA-06-014**: Add cross-tenant access test (assert 403 forbidden)
- [ ] **ACA-06-015**: Audit all Cosmos queries (verify partition_key usage)
- [ ] **ACA-06-016**: Create penetration test suite (red-team scenarios)

**CHECK**:
- [ ] All Cosmos queries use partition_key
- [ ] Cross-tenant access blocked (test with different subscriptionId)
- [ ] Evidence: `evidence/data-isolation-20260417.json`

#### Thursday 4/18: Admin Dashboard

**DISCOVER**:
- [ ] Review admin router (`services/api/app/routers/admin.py`)
- [ ] Check existing admin endpoints

**PLAN**:
- [ ] Design admin dashboard (P31 pattern: AdminListPage templates)
- [ ] Define admin endpoints (list scans, list customers, metrics)
- [ ] Document RBAC (admin role required)

**DO** (Epic 5 + P31 pattern):
- [ ] **Create** `AdminDashboardPage` (scans, customers, findings stats)
- [ ] **Implement** GET `/v1/admin/scans` (paginated, filterable)
- [ ] **Implement** GET `/v1/admin/customers` (Stripe data sync)
- [ ] **Implement** GET `/v1/admin/metrics` (total scans, revenue, findings)

**CHECK**:
- [ ] Admin dashboard renders (auth required)
- [ ] All admin endpoints return data
- [ ] Evidence: `evidence/admin-dashboard-20260418.json`

#### Friday 4/19: Week 6 Wrap & Integration Tests

**DISCOVER**:
- [ ] Run integration tests (full Tier 1/2/3 flows)
- [ ] Check end-to-end evidence trail

**PLAN**:
- [ ] Design integration test suite (Playwright or pytest)
- [ ] Define test scenarios (30+ combinations)

**DO**:
- [ ] **Create** integration tests (Tier 1 flow, Tier 2 upgrade, Tier 3 delivery)
- [ ] **Run** full test suite (unit + integration + E2E)
- [ ] **Generate** test evidence (JSON + screenshots)

**CHECK**:
- [ ] All integration tests pass
- [ ] Evidence trail complete (scan ID → findings → entitlement → delivery)
- [ ] Evidence: `evidence/week6-integration-20260419.json`

**ACT**:
- [ ] Update STATUS.md: Week 6 complete, Tier gating operational
- [ ] Document Week 6 lessons in `docs/WEEK6-RETROSPECTIVE.md`

**Week 6 MTI Target**: 78/100 (up from 75)

---

## Week 7-8: Delivery and DPDCA Compliance

### Week 7 (April 22-26, 2026)

#### Monday 4/22: Delivery Service Foundation

**DISCOVER**:
- [ ] Review delivery service (`services/delivery/app/main.py`)
- [ ] Check IaC generator (`app/generator.py`)

**PLAN**:
- [ ] Design delivery pipeline (findings → IaC templates → ZIP → SAS URL)
- [ ] Define template structure (Bicep + Terraform + implementation guide)
- [ ] Document evidence capture (deliverable ID, sha256, timestamps)

**DO** (Epic 7 Stories):
- [ ] **ACA-07-001**: Enhance IaC generator (12 finding types → Bicep templates)
- [ ] **ACA-07-002**: Add Terraform generation (Phase 2 target)
- [ ] **ACA-07-003**: Create implementation guide generator (PDF from findings)
- [ ] **ACA-07-004**: Implement ZIP packager (all artifacts + manifest)

**CHECK**:
- [ ] Generator produces Bicep for all 12 finding types
- [ ] ZIP contains: findings.json + bicep/ + terraform/ + guide.pdf
- [ ] Evidence: `evidence/delivery-generator-20260422.json`

#### Tuesday 4/23: Blob Storage & SAS URLs

**DISCOVER**:
- [ ] Review Azure Blob Storage setup
- [ ] Check SAS URL generation

**PLAN**:
- [ ] Design blob container structure (deliverables/{subscriptionId}/{deliverableId}.zip)
- [ ] Define SAS expiry (24 hours, read-only)
- [ ] Document cleanup policy (delete after 7 days)

**DO** (Epic 7 Stories):
- [ ] **ACA-07-005**: Implement blob upload (ZIP → Azure Storage)
- [ ] **ACA-07-006**: Generate SAS URL (24h expiry, read-only)
- [ ] **ACA-07-007**: Add sha256 verification (client can verify download)
- [ ] **ACA-07-008**: Implement GET `/v1/download/:deliverableId` (returns SAS URL)

**CHECK**:
- [ ] ZIP uploads successfully
- [ ] SAS URL works (download within 24h)
- [ ] sha256 matches (verify integrity)
- [ ] Evidence: `evidence/delivery-storage-20260423.json`

#### Wednesday 4/24: Delivery Trigger & Lifecycle

**DISCOVER**:
- [ ] Review delivery trigger (Stripe webhook → delivery job)
- [ ] Check delivery status tracking

**PLAN**:
- [ ] Design delivery state machine (pending → generating → succeeded/failed)
- [ ] Define retry strategy (generation failure → retry 3x)
- [ ] Document evidence trail (Tier 3 payment → delivery ID → download)

**DO** (Epic 7 Stories):
- [ ] **ACA-07-009**: Implement delivery trigger (webhook → start job)
- [ ] **ACA-07-010**: Add delivery status tracking (Cosmos deliverables container)
- [ ] **ACA-07-011**: Implement retry logic (3 attempts, exponential backoff)
- [ ] **ACA-07-012**: Create GET `/v1/deliverables/:id/status` (polling endpoint)

**CHECK**:
- [ ] Tier 3 payment → delivery job starts automatically
- [ ] Status tracking works (pending → generating → succeeded)
- [ ] Evidence: `evidence/delivery-lifecycle-20260424.json`

#### Thursday 4/25: Evidence Spine Integration (P40 Pattern)

**DISCOVER**:
- [ ] Review evidence ID generation (from Week 1)
- [ ] Check evidence propagation (scan → analysis → delivery)

**PLAN**:
- [ ] Design evidence spine (P40 pattern: single ID links all operations)
- [ ] Define evidence pack structure (JSON manifest + artifacts)
- [ ] Document evidence query (`GET /evidence/{evidence_id}`)

**DO** (P40 pattern):
- [ ] **Create** evidence pack assembler (bundle all artifacts per scan)
- [ ] **Implement** evidence ID propagation (scan → collector → analysis → delivery)
- [ ] **Add** GET `/v1/evidence/:evidenceId` (cross-run view)
- [ ] **Create** evidence pack schema (manifest.json + artifacts/)

**CHECK**:
- [ ] Evidence ID links: Stripe payment → scan → findings → delivery
- [ ] GET `/evidence/:evidenceId` returns complete view
- [ ] Evidence: `evidence/evidence-spine-20260425.json`

#### Friday 4/26: DPDCA Compliance Audit (P48 Pattern)

**DISCOVER**:
- [ ] Run veritas audit (`node src/cli.js audit --repo 51-ACA`)
- [ ] Check coverage gaps (stories without artifacts)

**PLAN**:
- [ ] Design DPDCA compliance checklist (all P48 patterns)
- [ ] Define evidence standards (JSON + logs + timestamped files)
- [ ] Document exit code semantics (0/1/2 contract)

**DO** (P48 pattern):
- [ ] **Apply** ASCII-only output (replace emoji with `[PASS]` `[FAIL]`)
- [ ] **Implement** dual logging (console minimal, file verbose)
- [ ] **Add** pre-flight checks (all scripts validate before run)
- [ ] **Create** timestamped evidence (all output files use YYYYMMDD_HHMMSS)

**CHECK**:
- [ ] All scripts follow exit code contract
- [ ] All operations generate evidence JSON
- [ ] No emoji/Unicode in any output
- [ ] Evidence: `evidence/dpdca-compliance-20260426.json`

**ACT**:
- [ ] Update STATUS.md: Week 7 complete, Delivery operational
- [ ] Document Week 7 lessons in `docs/WEEK7-RETROSPECTIVE.md`

**Week 7 MTI Target**: 82/100 (up from 78)

---

### Week 8 (April 29 - May 3, 2026)

#### Monday 4/29: Phase 1 Acceptance Gate Verification

**DISCOVER**:
- [ ] Review ACCEPTANCE.md (30 gates defined)
- [ ] Check current gate status (how many passing?)

**PLAN**:
- [ ] Design gate verification checklist (15 P1 gates)
- [ ] Define gate automation (which gates can be scripted?)
- [ ] Document manual verification (screenshots, videos)

**DO**:
- [ ] **Verify** P1-01 (Infrastructure): all Bicep deploys, 7 containers exist
- [ ] **Verify** P1-02 (API Startup): /health returns 200, all routers load
- [ ] **Verify** P1-03 (Data Collection): full collection < 10 min
- [ ] **Verify** P1-04 (Analysis Engine): all 12 rules run, findings generated
- [ ] **Verify** P1-05 (Tier Gating): redteam test passes, no leaks

**CHECK**:
- [ ] 5/15 P1 gates verified (manual walkthrough)
- [ ] Evidence: `evidence/acceptance-gates-20260429.json`

#### Tuesday 4/30: Tier 1/2/3 End-to-End Validation

**DO**:
- [ ] **Verify** P1-06 (Stripe Integration): checkout, webhook, entitlement
- [ ] **Verify** P1-07 (Delivery): ZIP generated, SAS URL works
- [ ] **Verify** P1-08 (Frontend): full Tier 1 flow (Landing → Findings)
- [ ] **Verify** P1-09 (APIM): tier enforcement, throttling, caching
- [ ] **Verify** P1-10 (Accessibility): axe-core passes, keyboard flow works

**CHECK**:
- [ ] 10/15 P1 gates verified (full stack tested)
- [ ] Evidence: `evidence/end-to-end-20260430.json`

#### Wednesday 5/1: i18n & Privacy Compliance

**DO**:
- [ ] **Verify** P1-11 (i18n): EN/FR switch works, all strings translated
- [ ] **Verify** P1-12 (CI): all checks green (ruff, mypy, pytest, axe-core)
- [ ] **Create** privacy policy page (GDPR/PIPEDA compliant)
- [ ] **Create** terms of service page (SaaS agreement)
- [ ] **Implement** data deletion endpoint (POST `/v1/auth/disconnect`)

**CHECK**:
- [ ] 12/15 P1 gates verified
- [ ] All compliance pages published
- [ ] Evidence: `evidence/privacy-compliance-20260501.json`

#### Thursday 5/2: Final MTI Push & Documentation

**DISCOVER**:
- [ ] Run final veritas audit
- [ ] Check MTI score (target: 85+)

**PLAN**:
- [ ] Identify remaining gaps (coverage, evidence, consistency)
- [ ] Prioritize documentation (README, API docs, architecture diagrams)

**DO**:
- [ ] **Fix** all remaining MTI gaps (missing evidence, orphan tags, consistency)
- [ ] **Generate** API documentation (OpenAPI/Swagger)
- [ ] **Create** architecture diagrams (system context, container, component)
- [ ] **Update** README.md (installation, quick start, deployment)

**CHECK**:
- [ ] MTI score > 85
- [ ] All documentation complete
- [ ] Evidence: `evidence/final-mti-20260502.json`

#### Friday 5/3: Phase 1 Go-Live Readiness

**DISCOVER**:
- [ ] Review deployment checklist
- [ ] Check rollback plan (Phase 1 → local dev)

**PLAN**:
- [ ] Design go-live sequence (deploy → smoke test → monitor)
- [ ] Define success criteria (health checks, first scan completes)
- [ ] Document rollback procedure (revert to previous revision)

**DO**:
- [ ] **Run** final end-to-end smoke test (all 3 tiers)
- [ ] **Generate** deployment evidence pack (all Week 1-8 artifacts)
- [ ] **Create** go-live runbook (step-by-step deployment)
- [ ] **Update** STATUS.md: Phase 1 READY FOR DEPLOYMENT

**CHECK**:
- [ ] All 15 P1 gates passing
- [ ] MTI > 85
- [ ] Deployment runbook ready
- [ ] Evidence: `evidence/go-live-readiness-20260503.json`

**ACT**:
- [ ] Update STATUS.md: Week 8 complete, Phase 1 production-ready
- [ ] Document Week 8 lessons in `docs/WEEK8-RETROSPECTIVE.md`
- [ ] Create final session summary: `docs/8-WEEK-BUILD-COMPLETE-20260503.md`

**Week 8 MTI Target**: 87/100 (production-ready: PASS ✅)

---

## Evidence Gates & Quality Checkpoints

### Per-Week Evidence Requirements

| Week | Evidence Type | Files Generated | Quality Gate |
|------|---------------|-----------------|--------------|
| 1 | Infrastructure validation | infra-validation-20260311.json | Bicep validates, all containers created |
| 2 | API bootstrap & collector | api-bootstrap-20260312.json, collector-week2-20260322.json | Health checks pass, collection completes |
| 3 | Frontend Tier 1 | frontend-i18n-20260325.json, frontend-a11y-20260329.json | axe-core passes, Lighthouse > 90 |
| 4 | E2E integration | e2e-tests-20260404.json, week4-mti-gate-20260405.json | MTI > 70 (deploy gate) |
| 5 | Analysis engine | analysis-rules-20260408.json, policy-as-code-20260412.json | All 12 rules operational, 95% coverage |
| 6 | Tier gating | apim-tier-gating-20260411.json, week6-integration-20260419.json | Tier enforcement validated |
| 7 | Delivery service | delivery-generator-20260422.json, evidence-spine-20260425.json | ZIP generation works, evidence ID links all |
| 8 | Go-live readiness | acceptance-gates-20260429.json, go-live-readiness-20260503.json | All 15 P1 gates pass, MTI > 85 |

### Mandatory Evidence Files

All operations must generate:
1. **JSON receipt** (`evidence/{operation}_{timestamp}.json`) with:
   - `timestamp`: ISO 8601
   - `operation`: what was done
   - `status`: "success" | "partial" | "failure"
   - `metrics`: counts, durations, sizes
   - `artifacts`: list of files generated
   - `errors`: array of error objects (if any)

2. **Log file** (`logs/{script}_{timestamp}.log`) with:
   - Console output (minimal, ASCII-only)
   - File output (verbose, all details)

3. **Timestamped artifacts** (all output uses `{component}_{YYYYMMDD_HHMMSS}.{ext}`)

### MTI Gates

| Week | MTI Target | Gate | Action If Fail |
|------|------------|------|----------------|
| 1 | 62 | Advisory | Document gaps, continue |
| 2 | 65 | Advisory | Document gaps, continue |
| 3 | 68 | Advisory | Document gaps, continue |
| 4 | 72 | **MANDATORY** | Fix gaps before Week 5 |
| 5 | 75 | Advisory | Document gaps, continue |
| 6 | 78 | Advisory | Document gaps, continue |
| 7 | 82 | High Priority | Fix critical gaps |
| 8 | 87 | **MANDATORY** | Must pass for go-live |

---

## Risk Register

| Risk | Impact | Probability | Mitigation | Owner |
|------|--------|-------------|------------|-------|
| **API timeout** (Resource Graph > 60s) | High | Medium | Pagination + caching | Collector |
| **Stripe webhook replay attack** | Critical | Low | HMAC validation + idempotency | API |
| **Cross-tenant data leak** | Critical | Low | Partition key enforcement + penetration tests | API + Security |
| **MTI < 70 at Week 4** | High | Medium | Daily audit, gap remediation priority | All |
| **Analysis rule crash** | Medium | Medium | Isolated error handling + fallback | Analysis |
| **Delivery generation timeout** | Medium | Low | Async job + retry logic | Delivery |
| **Frontend i18n gaps** | Medium | Low | Native speaker review | Frontend |
| **APIM tier gating bypass** | Critical | Low | Red-team tests + APIM policy audit | API + APIM |

---

## Success Metrics

### Operational Metrics (Week 8 Targets)

| Metric | Target | Current (3/11) | Delta |
|--------|--------|----------------|-------|
| **MTI Score** | 87 | 57 | +30 |
| **Test Coverage** | 95% | ~70% | +25% |
| **API Response Time (p99)** | < 500ms | N/A | Measure |
| **Collection Time (500 resources)** | < 10 min | N/A | Measure |
| **Analysis Time (91 days)** | < 5 min | N/A | Measure |
| **axe-core Violations** | 0 critical/serious | Unknown | Measure |
| **Lighthouse Score** | > 90 | Unknown | Measure |

### Business Metrics (Phase 1 Launch)

| Metric | Target | Method |
|--------|--------|--------|
| **First external scan** | Within 1 week of launch | GA4 event tracking |
| **Tier 2 conversion** | 5% of Tier 1 users | Stripe + GA4 funnel |
| **Tier 3 conversion** | 20% of Tier 2 users | Stripe + GA4 funnel |
| **Average findings per scan** | 8-12 | Analysis summary aggregation |
| **Average saving per scan** | CAD $30K-$80K | Findings aggregation |

---

## Lessons Learned (Continuous)

### From Reference Projects

1. **P31 (eva-faces)**: Mock backend pattern saved 2 weeks of frontend-backend integration delays
2. **P39 (ado-dashboard)**: APIM tier gating simpler than backend enforcement (1 policy vs. 6 routers)
3. **P40 (control-plane)**: Evidence ID spine critical for audit trail (Stripe → scan → findings → delivery)
4. **P41 (eva-cli)**: Adapter pattern enables testing without Azure (SQLite adapter for local dev)
5. **P48 (eva-veritas)**: MTI quality gates must be enforced at Week 4 (deploy gate) and Week 8 (go-live)
6. **P50 (eva-ops)**: Watchdog pattern prevents collector job from staying failed (auto-restart on health check failure)

### From ACA Development (Session 44)

1. **Orphan tag cleanup**: Template placeholder IDs (ACA-16-*, ACA-17-*) should use UPPERCASE markers to avoid confusion with real story IDs
2. **Data model sync**: Cloud API as single source of truth (no disk fallback) requires fail-closed semantics
3. **DPDCA at every granularity**: Breaking work into atomic units with per-unit visibility prevents "black box" failures
4. **ASCII-only output**: Cross-platform compatibility requires `[PASS]` `[FAIL]` instead of ✓✗ emoji
5. **Evidence at every stage**: JSON + logs + timestamps enable forensic audit when issues arise

---

## Next Steps After Week 8

### Phase 2 Planning (Weeks 9-16)

1. **Terraform generation** (Tier 3 enhancement)
2. **Multi-language support** (pt-BR, ES, DE)
3. **Custom domain + TLS** (app.aca.example.com)
4. **Commercial infrastructure** (Phase 2 Terraform, 3 geo-replicas)
5. **Recurring subscription billing** (Stripe invoice.paid webhook)
6. **Support widget** (Intercom or equivalent)
7. **Status page** (uptime monitoring)
8. **Advanced analytics** (GA4 custom dimensions, cohort analysis)

### Continuous Improvement

- [ ] Weekly MTI audits (maintain > 85)
- [ ] Monthly security audits (penetration testing)
- [ ] Quarterly architecture reviews (tech debt assessment)
- [ ] Bi-annual disaster recovery drills (rollback + restore)

---

## Appendix A: Reference Project Matrix

| Project | Focus Area | Key Patterns | Lines of Code | Test Coverage | MTI Score |
|---------|------------|--------------|---------------|---------------|-----------|
| **31-eva-faces** | Enterprise UI | Monorepo, GC Design, Template pages | 25,000+ | 85%+ | 92 |
| **38-ado-poc** | Webhook Integration | HMAC validation, Bridge pattern | 3,000+ | 70%+ | N/A |
| **39-ado-dashboard** | Reusable Library | APIM gateway, Export pattern | 5,000+ | 75%+ | N/A |
| **40-eva-control-plane** | Runtime Tracking | Evidence ID spine, Dual store | 8,000+ | 80%+ | N/A |
| **41-eva-cli** | CLI Framework | Adapter pattern, Idempotent receipts | 6,000+ | 75%+ | N/A |
| **45-aicoe-page** | Standalone SPA | i18n (EN/FR), HashRouter | 4,000+ | 70%+ | N/A |
| **46-accelerator** | UI Components | 50+ shadcn, Role-based access | 12,000+ | 80%+ | N/A |
| **48-eva-veritas** | Quality Gates | MTI formula, Paperless DPDCA | 7,000+ | 90%+ | N/A |
| **49-eva-dtl** | Policy Engine | YAML rules, Signal-based auth | 3,000+ | 85%+ | N/A |
| **50-eva-ops** | Operations | Watchdog, Logs aggregation | 5,000+ | 75%+ | N/A |

---

## Appendix B: Technology Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Database**: Azure Cosmos DB NoSQL (7 containers)
- **Auth**: MSAL (Microsoft Authentication Library)
- **Payments**: Stripe (checkout, webhooks, customer portal)
- **Jobs**: Azure Container Apps Jobs (Collector, Analysis, Delivery)
- **API Gateway**: Azure API Management (APIM)

### Frontend
- **Language**: TypeScript 5+
- **Framework**: React 19
- **UI Library**: Fluent UI v9
- **Build Tool**: Vite
- **Styling**: GC Design System (Canada.ca tokens)
- **i18n**: react-i18next
- **Analytics**: GA4 (via GTM) + Microsoft Clarity

### Infrastructure
- **IaC**: Bicep (Phase 1) + Terraform (Phase 2)
- **Compute**: Azure Container Apps (4 services + 3 jobs)
- **Storage**: Azure Blob Storage (deliverable packages)
- **Secrets**: Azure Key Vault
- **Monitoring**: App Insights + Log Analytics

### Development
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Testing**: pytest (backend) + Vitest (frontend) + Playwright (E2E)
- **Linting**: ruff (Python) + ESLint (TypeScript)
- **Type Checking**: mypy (Python) + TypeScript compiler
- **Quality Gates**: eva-veritas (MTI scoring)

---

**Document Version**: 1.0.0  
**Last Updated**: March 11, 2026 @ 06:30 AM ET  
**Status**: Ready for execution  
**Next Review**: End of Week 1 (March 15, 2026)
