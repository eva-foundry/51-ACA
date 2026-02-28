# ACA -- Critical Gaps and Decisions

**Version**: 1.2.0
**Date**: 2026-02-28
**For**: 2-person team (Marco + Copilot)
**Purpose**: Fix these BEFORE Phase 1 ships

---

## GUIDING PRINCIPLE: PRODUCT INDEPENDENCE

**Development (Phase 1)**: Share EVA project infrastructure (marco* resources, data model API, APIM)
**Production (Phase 2)**: Zero dependencies on EVA project infrastructure

Rationale: eva-poc and 51-aca are separate products for different audiences. Commercial SaaS
cannot depend on internal EVA tooling in production. Phase 1 reuse is acceptable for speed;
Phase 2 must be fully standalone.

---

## CRITICAL BLOCKERS (must fix for Phase 1 go-live)

### GB-01: Frontend Deployment Model Undecided → RESOLVED
**Impact**: Cannot deploy frontend to Production
**Location**: infrastructure-architecture.md line 118-120
**Decision**: marco-sandbox-backend App Service slot (Phase 1 acceptable per product independence principle)

**Phase 1 (Project Infrastructure)**:
- Reuse marco-sandbox-backend App Service slot (Linux container)
- Deploy frontend as Docker image to slot
- No custom domain (use *.azurewebsites.net)
- No CDN (direct access acceptable for proof-of-concept)

**Phase 2 (Product Independence)**:
- Migrate to dedicated Azure Static Web App
- Custom domain: app.aca.example.com
- Front Door CDN + WAF
- Zero dependency on marco* resources

**Story to add:**
```
Story 1.3.7 [ACA-01-022]  As an operator I deploy frontend to marco-sandbox-backend slot (Phase 1)
  Size: S
  Acceptance: PUBLIC_APP_URL resolves, CORS configured, MSAL redirectUri set
  Files: infra/phase1-marco/frontend-slot.bicep (new), .github/workflows/deploy-phase1.yml
  Note: Phase 2 migration to Static Web App tracked in Story 11.1.6
```

---

### GB-02: Analysis Job Never Auto-Triggers
**Impact**: Collection succeeds, but findings screen stays empty forever
**Location**: PLAN.md Story 2.5.4, scan_pipeline.py line 260-280
**Symptoms**: trigger_pipeline() only starts collector, not analysis

**Current flow**:
```
POST /v1/scans -> trigger_pipeline(collector) -> status=collecting
[collector finishes, writes status=collected]
[STOPS HERE -- analysis never runs]
```

**Required flow**:
```
POST /v1/scans -> trigger_pipeline(collector) -> status=collecting
[collector finishes, calls mark_collection_complete()]
mark_collection_complete() -> trigger_aca_job(aca-51-analysis) -> status=analysing
[analysis finishes] -> status=complete
```

**Story to add**:
```
Story 2.5.5 [ACA-02-018]  As the collector job I auto-trigger the analysis job on completion
  Size: M
  Acceptance: After mark_collection_complete(), analysis job starts within 30 seconds
  Files: services/collector/app/main.py (add trigger check)
        services/api/app/scan_pipeline.py (add trigger_analysis() helper)
        tools/trigger_aca_job.py (already exists, reuse)
  Related: Story 2.5.4 note (graceful degradation if ACA_ANALYSIS_JOB_NAME unset)
```

---

### GB-03: Resource Graph Pagination Not Implemented
**Impact**: Breaks on subscriptions with >1,000 resources (Azure limit per page)
**Location**: solution-architecture.md line 695, collector assumptions
**Symptoms**: Large subscriptions (e.g. enterprise prod) only see first 1,000 resources

**Current**: `resource_client.resources.list()` returns first page only
**Required**: Loop with `$skipToken` until no more pages

**Story to add**:
```
Story 2.2.8 [ACA-02-019]  As the system I paginate Resource Graph queries for large subscriptions
  Size: S
  Acceptance: Subscription with 5,000 resources collects all 5,000 (verified via count)
  Files: services/collector/app/azure_client.py (add pagination loop)
  Test: Mock response with $skipToken, assert loop continues
```

---

### GB-04: No Error Handling Strategy for Customer-Visible Failures
**Impact**: Users hit errors with no guidance (400/500 responses with stack traces)
**Location**: No doc, scattered across routers
**Symptoms**: Sentry/App Insights full of exceptions, support ticket volume high

**Current**: FastAPI default exception handler shows stack trace
**Required**: Structured error responses (RFC 7807 Problem Details)

**Example**:
```json
{
  "type": "/errors/insufficient-permissions",
  "title": "Azure RBAC permissions missing",
  "status": 403,
  "detail": "Cost Management Reader role not found on subscription 12345",
  "instance": "/v1/scans/abc-123",
  "help_url": "https://docs.aca.example.com/access-guide#cost-reader"
}
```

**Story to add**:
```
Story 4.6.1 [ACA-04-029]  As a client I receive structured error responses (RFC 7807)
  Size: M
  Acceptance: All 4xx/5xx responses include type, title, status, detail, help_url
  Files: services/api/app/main.py (add exception_handler)
        services/api/app/errors.py (new, define ACAException base class)
        docs/error-catalog.md (new, document all error types)
  Test: Unit test for each error type, assert JSON shape
```

---

### GB-05: Customer Onboarding Flow Missing
**Impact**: Users don't know how to start (no "Connect Subscription" CTA visible)
**Location**: Frontend pages not implemented (Epic 5 0% complete)
**Symptoms**: Good backend, no UI (users can't trigger scans)

**Current state**: LoginPage exists, ConnectSubscriptionPage is stub
**Required**: Full Tier 1 flow: Login -> Connect -> Status -> Findings -> Upgrade

**Epic 5 status**:
- 40 stories total
- 0 stories done
- Blocking all user testing

**Prioritized stories for Sprint 2**:
```
Story 5.1.2 [ACA-05-002]  useAuth.ts hook (MSAL + DEV bypass)            Size: S
Story 5.2.1 [ACA-05-006]  CustomerLayout.tsx (nav wrapper)              Size: XS
Story 5.3.1 [ACA-05-011]  router.tsx (createBrowserRouter pattern)     Size: S
Story 5.4.2 [ACA-05-017]  ConnectSubscriptionPage (Mode A form)        Size: M
Story 5.4.3 [ACA-05-018]  CollectionStatusPage (polling + progress)    Size: M
Story 5.4.4 [ACA-05-019]  FindingsTier1Page (gated report)             Size: L
Story 5.6.1 [ACA-05-026]  frontend/src/app/api/client.ts (http helper) Size: S
```

**Decision needed on**: MVP scope for Sprint 2 (skip Admin pages until Sprint 3?)

---

### GB-06: Data Model API Dependency (Phase 2 blocker, plan now)
**Impact**: Phase 2 cannot ship with dependency on shared EVA data model endpoint
**Location**: All services import from https://marco-eva-data-model...
**Symptoms**: Product independence principle violated

**Current state**:
- API: `$base = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"`
- Acceptable for Phase 1 (project infrastructure reuse)
- BLOCKER for Phase 2 (commercial product cannot depend on EVA internal API)

**Phase 2 options**:
- A) Deploy standalone data model server in aca-prod subscription (port 8010, Cosmos-backed)
- B) Embed db.py directly in API service (no external HTTP calls)
- C) Migrate to relational schema (Azure SQL, eliminate data model abstraction)

**Recommendation**: Option A (standalone server in Phase 2)
- Maintains data model benefits (audit, versioning, consistency)
- Clean separation: ACA owns its data model independently
- Deployment: Container App in aca-prod, aca-cosmos-prod backend

**Story to add:**
```
Story 11.1.6 [ACA-11-010]  As the system I use a standalone data model server (Phase 2)
  Size: M
  Acceptance: ACA data model runs at https://aca-dm-prod.canadacentral.azurecontainerapps.io
              All API/services point to aca-dm-prod (no marco-eva-data-model dependency)
  Files: infra/phase2-private/data-model.tf (new Container App)
        services/api/app/settings.py (ACA_DATA_MODEL_URL env var)
  Related: Product independence principle (no EVA dependency in production)
```

---

### GB-07: 29-Foundry Agent Dependency (Phase 2 blocker, plan now)
**Impact**: Phase 2 cannot ship with dependency on shared EVA 29-foundry service
**Location**: services/analysis/app/main.py line 9 + 52, agents/*.yaml files
**Symptoms**: Product independence principle violated

**Current state**:
- Analysis service uses: `sys.path.insert(0, "../29-foundry")` imports
- Agent definitions: agents/collection-agent.yaml, analysis-agent.yaml, generation-agent.yaml, redteam-agent.yaml
- Shared code: tools/search.py, tools/rag.py, agents/orchestrator.py from C:\AICOE\eva-foundry\29-foundry
- Acceptable for Phase 1 (project infrastructure reuse)
- BLOCKER for Phase 2 (commercial product cannot depend on EVA internal service)

**Phase 2 options**:
- A) Bundle 29-foundry code into ACA analysis service (copy required modules, no external dependency)
- B) Deploy ACA-owned 29-foundry fork (separate repo, no EVA shared service)
- C) Replace with direct Azure OpenAI SDK calls (eliminate agent framework, simpler but less flexible)

**Recommendation**: Option A (bundle agent code into analysis service)
- Self-contained deployment (no external service dependency)
- Agent definitions stay in ACA repo (agents/*.yaml already there)
- Copy only required modules: tools/search.py, tools/rag.py, agents/orchestrator.py (lightweight)
- Phase 2 migration: Replace `sys.path.insert` with bundled package import

**Story to add:**
```
Story 3.2.9 [ACA-03-020]  As the analysis service I bundle 29-foundry agent code (Phase 2)
  Size: M
  Acceptance: services/analysis/app/foundry/ contains search.py, rag.py, orchestrator.py
              No sys.path.insert to external 29-foundry path
              All agent workflows run without EVA dependency
  Files: services/analysis/app/foundry/ (new package, copy from 29-foundry)
        services/analysis/app/main.py (update imports)
        services/analysis/requirements.txt (add agent dependencies)
  Related: Product independence principle (no EVA dependency in production)
```

**Build-time dependencies (Acceptable):**
- **48-eva-veritas**: CI/CD gate only (MTI >= 30 for Sprint 2, restore to 70 at Sprint 3)
  - Used in: .github/workflows/ci.yml for trust scoring
  - NOT a production runtime dependency
  - Acceptable: CI tools can remain shared EVA infrastructure per product independence principle

---

## HIGH PRIORITY (Phase 1 quality issues)

### GP-01: No Rate Limiting on Collection
**Impact**: Single malicious customer can exhaust Azure ARM API quota (12,000 req/hour)
**Fix**: Add retry-after backoff in collector, APIM throttling policy
**Story**: ACA-02-020 (add to Epic 2)

---

### GP-02: No Monitoring/Alerting Thresholds Defined
**Imp0 | Product independence principle | Share infra forever / Phase 1 share Phase 2 standalone | **Phase 1 share, Phase 2 standalone** | 2026-02-28 | Commercial product cannot depend on EVA internal tooling |
| D-01 | Frontend deployment Phase 1? | Static Web App / App Service slot | **App Service slot (marco-sandbox-backend)** | 2026-02-28 | Phase 1 project infra reuse OK; Phase 2 migrates to Static Web |
| D-02 | MVP scope Sprint 2? | Full Epic 5 / Customer flow only | **Customer flow only** | 2026-02-28 | Admin pages defer to Sprint 3 |
| D-03 | Error response format? | Plain text / RFC 7807 Problem Details | **RFC 7807** | 2026-02-28 | Structured + help URLs |
| D-04 | Rate limiting Phase 1? | None / APIM 10 req/sec / Collector backoff | **APIM + backoff** | 2026-02-28 | Defense in depth |
| D-05 | Data model Phase 2? | Standalone server / Embed db.py / Migrate to SQL | **Standalone server** | 2026-02-28 | Maintains benefits, product independence| D-06 | 29-foundry Phase 2? | Bundle agent code / Deploy ACA fork / Replace with direct SDK | **Bundle agent code** | 2026-02-28 | Self-contained, no external dependency |---

### GP-03: Data Retention Beyond TTLs Not Specified
**Impact**: Cosmos grows unbounded, monthly cost escalates
**Fix**: Define purge policy (e.g. completed scans older than 90 days)
**Story**: ACA-10-016 (add to Epic 10)

---

## PHASE 2 (can defer, but decide now to avoid rework)

### PD-01: Cosmos Reserved Instance Decision
**Impact**: Phase 2 overspends by 30% (~$255 CAD/month waste)
**Fix**: After 3 months Phase 1 usage data, commit to 1-year RI
**Story**: Already captured in infrastructure-architecture.md line 519 (TBD note)

---

### PD-02: Cost Tracking Per Tenant
**Impact**: Cannot identify high-cost customers or optimize pricing
**Fix**: Emit custom metrics per subscriptionId (RU consumption, job duration)
**Story**: ACA-08-019 (add to Epic 8)

---

## DECISIONS LOG

| ID | Question | Options | Decision | Date | Reason |
|---|---|---|---|---|---|
| D-01 | Frontend deployment Phase 1? | Static Web App / App Service slot | **TBD** | 2026-02-28 | Choose based on CDN requirement |
| D-02 | MVP scope Sprint 2? | Full Epic 5 / Customer flow only | **Customer flow only** | 2026-02-28 | Admin pages defer to Sprint 3 |
| D-03 | Error response format? | Plain text / RFC 7807 Problem Details | **RFC 7807** | 2026-02-28 | Structured + help URLs |
| D-04 | Rate limiting Phase 1? | None / APIM 10 req/sec / Collector backoff | **APIM + backoff** | 2026-02-28 | Defense in depth |

---

## ACTION ITEMS (next 48 hours)
~~Decide D-01 (frontend deployment)~~ ✅ RESOLVED (App Service slot Phase 1)
2. Review Epic 5 Sprint 2 scope (7 stories above) -- confirm priority order
3. Approve GB-04 error catalog structure before implementation

**For Copilot:**
1. Add 10 new stories to PLAN.md (GB-01 through GB-07 conversions)
2. Implement GB-02 (analysis auto-trigger) -- HIGHEST IMPACT
3. Implement GB-03 (Resource Graph pagination) -- QUICK WIN
4. Create infra/phase1-marco/frontend-slot.bicep (GB-01 resolution)sions)
2. Implement GB-02 (analysis auto-trigger) -- HIGHEST IMPACT
3. Implement GB-03 (Resource Graph pagination) -- QUICK WIN

---

## RELATED DOCS

- [PLAN.md](../PLAN.md) -- full WBS with 257 stories
- [application-architecture.md](./architecture/application-architecture.md) -- technical patterns
- [infrastructure-architecture.md](./architecture/infrastructure-architecture.md) -- Phase 1/2 topology
- [STATUS.md](../STATUS.md) -- current sprint state
