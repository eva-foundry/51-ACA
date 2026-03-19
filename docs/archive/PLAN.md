<!-- eva-primed-plan -->

## EVA Ecosystem Tools

- Data model (central, port 8010): GET https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA
- 29-foundry agents: C:\eva-foundry\eva-foundation\29-foundry\agents\
- 48-eva-veritas audit: run audit_repo MCP tool

---

ACA -- Azure Cost Advisor -- PLAN
=================================

Version: 0.7.0
Updated: 2026-03-06T19:38:00-05:00 (2:38 PM ET - Sprint-003 Baseline Locked, Agent Execution Ready)
Phase: Phase 1 active (multi-agent orchestration pipeline complete)

This plan is the Work Breakdown Structure (WBS) for ACA.
Each Epic maps to one or more data-model layers.
Features map to WBS nodes whose leaf records are user stories in the data-model WBS layer.
All milestone dates are relative to 2026-02-26 (project bootstrap complete).

**SPRINT-003 BASELINE LOCKED**: 281 stories planned, 23 gaps (12 ACA-15 not-started, 11 orphan doc refs).
Data model synced to cloud. Cloud model row_version: 2. Ready for agent orchestration. March 6, 2:38 PM ET.
NOTE 2026-03-11: Cloud drift was later confirmed between legacy `/model/stories` consumers and the
live WBS-backed hierarchy. Feature 12.4 governs the safe cleanup and ground-up restore. Recompute
story counts after README + PLAN scope refresh and the controlled rebuild.

=============================================================================
WBS OVERVIEW
=============================================================================

STATUS  Epic  Title                                         Milestone  Weeks
------  ----  ----                                         ---------  -----
DONE    1     Foundation and Infrastructure                 M1.0       1-2
DONE    2     Data Collection Pipeline                      M1.1       2-3
ACTIVE  3     Analysis Engine + Rules                       M1.2       2-3
ACTIVE  4     API and Auth Layer                            M1.3       2-3
ACTIVE  5     Frontend Core                                 M1.4       3-4
DONE    6     Monetization and Billing (Stripe)             M1.5       3-4
ACTIVE  7     Delivery Packager (Tier 3)                    M1.6       4
ACTIVE  8     Observability and Telemetry                   M2.0       4
ACTIVE  9     i18n and a11y                                 M2.1       4-5
PLANNED 10    Commercial Hardening                          M2.2       5-6
PLANNED 11    Phase 2 Infrastructure                        M3.0       7-9
ACTIVE  12    Data Model Support (app runtime)              ongoing    -
NEW     13    Azure Best Practices Service Catalog          M2.3       4-5
NEW     14    DPDCA Cloud Agent (GitHub Actions)            M2.4       3-5
NEW     15    Onboarding System (Client Onboarding SaaS)    M4.0       6-10

=============================================================================
EPIC 1 -- FOUNDATION AND INFRASTRUCTURE (M1.0)
=============================================================================

Goal: All four services boot cleanly. Local dev stack works. Phase 1 infra wired.

Feature 1.1 -- Local dev environment
  Story 1.1.1 [ACA-01-001]  As a developer I can run `docker-compose up` and all services start
  Story 1.1.2 [ACA-01-002]  As a developer I can run `pytest services/ -x -q` and all tests pass
  Story 1.1.3 [ACA-01-003]  As a developer I can hit http://localhost:8080/health and get status=ok
  Story 1.1.4 [ACA-01-004]  As a developer I can query the central data model (port 8010, managed by project 37)
  Story 1.1.5 [ACA-01-005]  As a developer I can use the .env.example as a complete checklist

Feature 1.2 -- CI pipeline
  Story 1.2.1 [ACA-01-006]  As a developer, every PR triggers ruff lint. Zero lint errors = green.
  Story 1.2.2 [ACA-01-007]  As a developer, every PR triggers mypy type check. No unresolved types.
  Story 1.2.3 [ACA-01-008]  As a developer, every PR triggers pytest. No test failures = merge allowed.
  Story 1.2.4 [ACA-01-009]  As a developer, main branch push triggers axe-core a11y check on frontend.

Feature 1.3 -- Phase 1 marco* infra wiring
  Story 1.3.1 [ACA-01-010]  As an operator I can run infra/phase1-marco/main.bicep and get 7 Cosmos containers
  Story 1.3.2 [ACA-01-011]  As an operator all secrets are in marcosandkv20260203 (no .env in production)
  Story 1.3.3 [ACA-01-012]  As an operator the API Container App has managed identity approved on KV
  Story 1.3.4 [ACA-01-013]  As an operator the collector job has managed identity with Cosmos read/write
  Story 1.3.5 [ACA-01-014]  As an operator OIDC is configured on the GitHub Actions workflow for EsDAICoE-Sandbox
  Story 1.3.6 [ACA-01-015]  As an operator infra/phase1-marco/bootstrap.sh exists and provisions all
               marco* ACA resources in sequence (Cosmos containers, KV secrets, ACA env,
               Container App + 3 jobs, APIM product) using az CLI with DO_* toggle flags
               (DO_CONTAINERAPPS, DO_APIM) for partial re-runs

Feature 1.4 -- Container build + push
  Story 1.4.1 [ACA-01-016]  As a developer all 4 Dockerfiles build without error on ubuntu-latest
  Story 1.4.2 [ACA-01-017]  As an operator deploy-phase1.yml pushes 4 images to marcosandacr20260203
  Story 1.4.3 [ACA-01-018]  As an operator collector-schedule.yml triggers nightly at 02:00 UTC

Feature 1.5 -- Phase 1 deployment URLs
  Story 1.5.1 [ACA-01-019]  As an operator PUBLIC_APP_URL and PUBLIC_API_URL are read from env vars;
               no URLs are hardcoded in source. Phase 1 = Azure free hostnames
               (*.{region}.azurecontainerapps.io). No custom domain required.
  Story 1.5.2 [ACA-01-020]  As a developer .env.example documents the Azure free hostname pattern
               with a placeholder comment and instructions to update on first deploy.
  Story 1.5.3 [ACA-01-021]  As an operator ACA_ALLOWED_ORIGINS is seeded from the Phase 1 free hostname
               on container startup via environment variable injection from KV.

Goal: Collector job runs against a real Azure subscription and saves data to Cosmos.

Feature 2.1 -- Pre-flight validation
  Story 2.1.1 [ACA-02-001]  As a client using Mode A (delegated) I see a PASS/FAIL/WARN status
               for each of the 5 capability probes before collection starts
  Story 2.1.2 [ACA-02-002]  As a client with missing Cost Management Reader role I see a clear
               error message naming the missing role and linking to the access guide
  Story 2.1.3 [ACA-02-003]  As a client with PASS_WITH_WARNINGS I can still proceed with collection
               and the warnings are recorded in the scan record
  Story 2.1.4 [ACA-02-004]  As an operator I can pass --preflight-only to the collector to validate
               without collecting

Feature 2.2 -- Resource inventory
  Story 2.2.1 [ACA-02-005]  As the system I collect all Azure resources via Resource Graph in < 60s
               for a subscription with up to 500 resources
  Story 2.2.2 [ACA-02-006]  As the system I save inventory to Cosmos with partition_key=subscriptionId
  Story 2.2.3 [ACA-02-007]  As the system I capture: resource type, name, SKU, region, resource group, tags

Feature 2.3 -- Cost data
  Story 2.3.1 [ACA-02-008]  As the system I collect 91 days of daily cost rows via Cost Management Query API
  Story 2.3.2 [ACA-02-009]  As the system I capture: date, MeterCategory, MeterName, resourceGroup,
               resourceId (hashed), PreTaxCost in subscription currency
  Story 2.3.3 [ACA-02-010]  As the system I handle rate limiting (429) with exponential backoff + retry

Feature 2.4 -- Advisor, Policy, Network
  Story 2.4.1 [ACA-02-011]  As the system I collect all Advisor recommendations across all categories
  Story 2.4.2 [ACA-02-012]  As the system I collect Policy compliance state (compliant / non-compliant counts)
  Story 2.4.3 [ACA-02-013]  As the system I collect network signals: NSG rule counts, private DNS zones,
               public IP count, VNet peering map

Feature 2.5 -- Collection lifecycle
  Story 2.5.1 [ACA-02-014]  As the system I update scan status in Cosmos: queued -> running -> succeeded/failed
  Story 2.5.2 [ACA-02-015]  As the system I write stats to the scan record (inventoryCount, costRows, advisorRecs)
  Story 2.5.3 [ACA-02-016]  As the API I expose GET /v1/scans/:scanId so the frontend can poll status
  Story 2.5.4 [ACA-02-017]  As the system, after mark_collection_complete sets status=collected, the analysis
               Container App Job is triggered automatically (via azure.mgmt.appcontainers or
               az CLI fallback). If ACA_ANALYSIS_JOB_NAME is not set, the trigger is skipped
               with a warning and collection still succeeds (graceful degradation for CI).
               Without this trigger no findings are ever produced -- scans stay at status=collected.

=============================================================================
EPIC 3 -- ANALYSIS ENGINE AND RULES (M1.2)
=============================================================================

Goal: Analysis engine runs all 12 rules and persists tiered findings to Cosmos.

Feature 3.1 -- Rule engine
  Story 3.1.1 [ACA-03-001]  As the system I load all 12 rules from ALL_RULES and run each in sequence
    Status: DONE (Sprint-06, merged PR #24)
  Story 3.1.2 [ACA-03-002]  As the system I handle a rule failure in isolation (one rule crash does not
               stop the engine; the error is logged and that rule is skipped)
    Status: DONE (Sprint-04, merged PR #19)
  Story 3.1.3 [ACA-03-003]  As the system I persist each Finding to Cosmos with full schema:
               id, category, title, estimated_saving_low, estimated_saving_high,
               effort_class, risk_class, heuristic_source, narrative,
               deliverable_template_id, evidence_refs
    Status: DONE (Sprint-04, merged PR #19)
  Story 3.1.4 [ACA-03-004]  As the system I update AnalysisRun status: queued -> running -> succeeded/failed
    Status: DONE (Sprint-05, merged PR #22)
  Story 3.1.5 [ACA-03-005]  As the system I write findingsSummary to the analysis run record
               (findingCount, totalSavingLow, totalSavingHigh, categories[])
    Status: DONE (Sprint-05, merged PR #22)

Feature 3.2 -- Tier gating
  Story 3.2.1 [ACA-03-006]  As a Tier 1 client calling GET /v1/findings/:scanId I receive findings
               with category, title, estimated_saving_low, estimated_saving_high only
    Status: DONE (Sprint-01, merged PR #11)
  Story 3.2.2 [ACA-03-007]  As a Tier 1 client I do not receive narrative or deliverable_template_id
               even if they are stored in Cosmos
    Status: DONE (Sprint-05, merged PR #22)
  Story 3.2.3 [ACA-03-008]  As a Tier 2 client I receive the full finding including narrative and
               evidence_refs but not deliverable_template_id
    Status: DONE (Sprint-06, merged PR #24)
  Story 3.2.4 [ACA-03-009]  As a Tier 3 client I receive the full finding including deliverable_template_id
    Status: DONE (Sprint-06, merged PR #24)
  Story 3.2.5 [ACA-03-010]  As the red-team agent I can assert that Tier 1 tokens never leak
               narrative or deliverable_template_id fields (redteam-agent.yaml gate)
    Status: DONE (Sprint-07, merged PR #29)

Feature 3.3 -- Individual rules (one story per rule)
  Story 3.3.1 [ACA-03-011]  R-01 Dev Box auto-stop: returns finding when annual Dev Box cost > $1,000
    Status: DONE (Sprint-04, merged PR #19)
  Story 3.3.2 [ACA-03-012]  R-02 Log retention: returns finding when annual LA cost > $500 in non-prod
    Status: DONE (Sprint-07, merged PR #29)
  Story 3.3.3 [ACA-03-013]  R-03 Defender mismatch: returns finding when annual Defender cost > $2,000
    Status: DONE (Sprint-07, merged PR #29)
  Story 3.3.4 [ACA-03-014]  R-04 Compute scheduling: returns finding when annual schedulable compute > $5,000
    Status: DONE (Sprint-07, merged PR #29)
  Story 3.3.5 [ACA-03-015]  R-05 Anomaly detection: returns finding for each category with z-score > 3.0
    Status: DONE (Sprint-08, merged PR #31)
  Story 3.3.6 [ACA-03-016]  R-06 Stale environments: returns finding when >= 3 App Service sites exist
    Status: DONE (Sprint-08, merged PR #31)
  Story 3.3.7 [ACA-03-017]  R-07 Search SKU oversize: returns finding when annual Search cost > $2,000
    Status: DONE (Sprint-08, merged PR #31)
  Story 3.3.8 [ACA-03-018]  R-08 ACR consolidation: returns finding when >= 3 registries exist
    Status: DONE (Sprint-08, merged PR #31)
  Story 3.3.9 [ACA-03-019]  R-09 DNS sprawl: returns finding when annual DNS cost > $1,000
    Status: DONE (Sprint-004-Batch-1, merged PR #43, Issue #39 closed)
  Story 3.3.10 [ACA-03-020] R-10 Savings plan: returns finding when annual total compute > $20,000
    Status: DONE (Sprint-004-Batch-1, merged PR #43, Issue #39 closed)
  Story 3.3.11 [ACA-03-021] R-11 APIM token budget: returns finding when APIM + OpenAI both present
    Status: DONE (Sprint-004-Batch-1, merged PR #43, Issue #39 closed)
  Story 3.3.12 [ACA-03-022] R-12 Chargeback gap: returns finding when total period cost > $5,000
    Status: DONE (Sprint-004-Batch-1, merged PR #43, Issue #39 closed)

Feature 3.4 -- Rule unit tests (DECISION LOCKED 2026-02-27: 95% coverage, hardcoded fixtures)
  One test file per rule. Tests use hardcoded JSON fixtures (no Cosmos calls).
  Target: 95% line coverage across all 12 rule modules. CI blocks on regression.

  Story 3.4.1 [ACA-03-020]   Unit test for R-01 devbox_autostop: fixture with Dev Box cost > $1,000 -> finding
    Status: DONE (test_r01_devbox.py, 3 tests passing)
  Story 3.4.2 [ACA-03-021]   Unit test for R-02 log_retention: fixture with LA cost > $500 -> finding
    Status: DONE (test_r02_log_retention.py, 3 tests passing)
  Story 3.4.3 [ACA-03-022]   Unit test for R-03 defender_mismatch: fixture with Defender cost > $2,000 -> finding
    Status: DONE (test_r03_defender.py, 3 tests passing)
  Story 3.4.4 [ACA-03-023]   Unit test for R-04 compute_scheduling: fixture with schedulable > $5,000 -> finding
    Status: DONE (test_r04_compute.py, 3 tests passing)
  Story 3.4.5 [ACA-03-024]   Unit test for R-05 anomaly_detection: fixture with z-score > 3.0 -> finding
    Status: DONE (test_r05_anomaly.py, 3 tests passing)
  Story 3.4.6 [ACA-03-025]   Unit test for R-06 stale_environments: fixture with >= 3 App Services -> finding
    Status: DONE (test_r06_stale.py, 3 tests passing)
  Story 3.4.7 [ACA-03-026]   Unit test for R-07 search_sku_oversize: fixture with Search cost > $2,000 -> finding
    Status: DONE (test_r07_search.py, 3 tests passing)
  Story 3.4.8 [ACA-03-027]   Unit test for R-08 acr_consolidation: fixture with >= 3 registries -> finding
    Status: DONE (test_r08_acr.py, 3 tests passing)
  Story 3.4.9 [ACA-03-028]   Unit test for R-09 dns_sprawl: fixture with DNS cost > $1,000 -> finding
    Status: DONE (Sprint-004-Batch-1, 5 tests in test_r09_dns_sprawl.py, merged PR #43)
  Story 3.4.10 [ACA-03-029]  Unit test for R-10 savings_plan_coverage: fixture with compute > $20,000 -> finding
    Status: DONE (Sprint-004-Batch-1, 4 tests in test_r10_savings_plan.py, merged PR #43)
  Story 3.4.11 [ACA-03-030]  Unit test for R-11 apim_token_budget: fixture with APIM + OpenAI -> finding
    Status: DONE (Sprint-004-Batch-1, 5 tests in test_r11_apim_token.py, merged PR #43)
  Story 3.4.12 [ACA-03-031]  Unit test for R-12 chargeback_gap: fixture with total cost > $5,000 -> finding
    Status: DONE (Sprint-004-Batch-1, 5 tests in test_r12_chargeback.py, merged PR #43)
  Story 3.4.13 [ACA-03-032]  Negative tests for each rule: below-threshold fixture -> no finding returned
    Status: DONE (test_negative_batch_1.py + test_negative_batch_2.py, 12 tests, all 12 rules covered)
  Story 3.4.14 [ACA-03-033]  FindingsAssembler unit test: mock rule list -> correct Cosmos upsert payload
    Status: DONE (Sprint-01, merged PR #11)
=============================================================================

Goal: All 25+ API endpoints implemented, JWT-validated, APIM-proxied.

Feature 4.1 -- Authentication (DECISION LOCKED 2026-02-27)
  ACA is standalone private-sector SaaS. NOT tied to EsDAICoE organization.
  Multi-tenant: authority=https://login.microsoftonline.com/common
  Any client with a Microsoft account (any tenant) can sign in.
  What matters: delegated token has Reader + Cost Management Reader on CLIENT's subscription.
  ACA app registration must be multi-tenant in Azure portal.

  Story 4.1.1 [ACA-04-001]  As a client I can sign in via Microsoft Identity (any Microsoft tenant);
               I do not need to be in any specific organization to use ACA
  Story 4.1.2 [ACA-04-002]  As the API I validate the JWT on every authenticated endpoint using
               JWKS from https://login.microsoftonline.com/common/discovery/keys
    Status: DONE (Sprint-02)
  Story 4.1.3 [ACA-04-003]  As the API I extract subscriptionId from the session (stored after connect);
               tier is read from the Cosmos clients container (not from JWT claims)
  Story 4.1.4 [ACA-04-004]  As a client I can connect my Azure subscription (POST /v1/auth/connect)
               in Mode A (delegated, any-tenant), Mode B (service principal provided
               by client), or Mode C (Azure Lighthouse delegation)
  Story 4.1.5 [ACA-04-005]  As a client I can disconnect (POST /v1/auth/disconnect) and all access
               tokens are invalidated and removed from Key Vault
  Story 4.1.6 [ACA-04-006]  As a developer auth.py is reworked: MSAL authority=common, no EsDAICoE
               org dependency, all 3 endpoints (connect/preflight/disconnect) implemented
               beyond 501 stubs. Refresh token stored per-scan in KV, not per-user.
    Status: DONE (Sprint-02)
  Story 4.1.7 [ACA-04-007]  As the frontend LoginPage, sign-in CTA calls MSAL.js with
               authority=common so any Microsoft account (personal or work) is accepted

Feature 4.2 -- Core API endpoints (Spark paths from docs 22-23)
  Story 4.2.1 [ACA-04-008]  POST /v1/auth/connect         -- Connect Azure subscription
    Status: DONE (Sprint-02)
  Story 4.2.2 [ACA-04-009]  POST /v1/auth/preflight       -- Run pre-flight probes
  Story 4.2.3 [ACA-04-010]  POST /v1/auth/disconnect      -- Disconnect subscription
  Story 4.2.4 [ACA-04-011]  POST /v1/collect/start        -- Trigger collector job (was /v1/scans)
  Story 4.2.5 [ACA-04-012]  GET  /v1/collect/status       -- Poll collection progress (was /v1/scans/:scanId)
  Story 4.2.6 [ACA-04-013]  GET  /v1/reports/tier1        -- Tier 1 findings report (was /v1/findings/:scanId)
  Story 4.2.7 [ACA-04-014]  POST /v1/billing/checkout     -- Stripe checkout (tier2 or tier3 in body)
  Story 4.2.8 [ACA-04-015]  GET  /v1/billing/portal       -- Stripe billing portal redirect URL
  Story 4.2.9 [ACA-04-016]  POST /v1/webhooks/stripe      -- Stripe event handler
  Story 4.2.10 GET  /v1/entitlements         -- Current tier for subscriptionId
  Story 4.2.11 GET  /health                  -- Health check (unauthenticated)

Feature 4.3 -- APIM policies
  Story 4.3.1 [ACA-04-017]  As the gateway I validate JWT signature on all /v1/* routes
  Story 4.3.2 [ACA-04-018]  As the gateway I cache /v1/entitlements response for 60s per subscriptionId
               using cache key entitlements::{subscriptionId} (from doc 19)
  Story 4.3.3 [ACA-04-019]  As the gateway I return 403 with TIER_REQUIRED error when a Tier 1
               client calls a Tier 2+ endpoint
  Story 4.3.4 [ACA-04-020]  As the gateway I enforce subscription key throttling (100 req/min default)
  Story 4.3.5 [ACA-04-021]  As the gateway I forward X-Subscription-Id header to the API on all calls

Feature 4.4 -- Admin API endpoints (NEW from docs 21/23)
  Story 4.4.1 [ACA-04-022]  GET  /v1/admin/kpis
               Returns { utc, mrrCad, activeSubscriptions, scansLast24h,
               analysesLast24h, deliveriesLast24h, failureRatePctLast24h }
               Requires role: ACA_Admin | ACA_Support | ACA_FinOps
  Story 4.4.2 [ACA-04-023]  GET  /v1/admin/customers?query=
               Searches by subscriptionId, stripeCustomerId; returns list of
               AdminCustomerRow (subscriptionId, stripeCustomerId, tier,
               paymentStatus, lastActivityUtc, isLocked)
               Requires role: ACA_Admin | ACA_Support | ACA_FinOps
  Story 4.4.3 [ACA-04-024]  POST /v1/admin/entitlements/grant
               Body: { subscriptionId, tier, days, reason }
               Writes entitlement to Cosmos + writes admin_audit_events record
               Requires role: ACA_Admin | ACA_Support
  Story 4.4.4 [ACA-04-025]  POST /v1/admin/subscriptions/:subscriptionId/lock
               Body: { reason }
               Marks subscription locked in clients container
               Writes admin_audit_events record
               Requires role: ACA_Admin | ACA_Support
  Story 4.4.5 [ACA-04-026]  POST /v1/admin/stripe/reconcile
               Enqueues reconcile job: fetches all active Stripe subscriptions
               and repairs missing entitlements in Cosmos
               Returns { jobId, acceptedUtc }
               Requires role: ACA_Admin
  Story 4.4.6 [ACA-04-027]  GET  /v1/admin/runs?type=scan|analysis|delivery
               Lists job run records (scan/analysis/delivery) from Cosmos
               Supports filter by subscriptionId and type
               Requires role: ACA_Admin | ACA_Support | ACA_FinOps

Feature 4.5 -- Data layer correctness
  Story 4.5.1 [ACA-04-028]  services/api/app/db/cosmos.py upsert_item() must accept partition_key as a
               required third parameter and pass it explicitly to container.upsert_item().
               Without this, the Cosmos SDK infers partition_key from the item dict which
               is unreliable and silently fails tenant isolation on malformed documents.
               All callers of upsert_item() must be updated to pass partition_key=subscription_id.
    Status: DONE (Sprint-01, merged PR #11)

=============================================================================
EPIC 5 -- FRONTEND SPARK ARCHITECTURE (M1.4)
=============================================================================

Goal: Spark /app/* + /admin/* routing live. RequireAuth + RequireRole guards.
      All 5 customer pages + 5 admin pages functional. Tier 1 flow end-to-end.

Feature 5.1 -- Auth layer (NEW from docs 22-23)
  Story 5.1.1 [ACA-05-001]  roles.ts defines ACA_Admin, ACA_Support, ACA_FinOps role constants
  Story 5.1.2 [ACA-05-002]  useAuth.ts wraps MSAL PublicClientApplication; exposes user, roles,
               isAuthenticated, login(), logout()
               DEV bypass mode: when VITE_DEV_AUTH=true, simulates signed-in user
               with configurable roles + subscriptionId (no MSAL call needed)
  Story 5.1.3 [ACA-05-003]  RequireAuth.tsx: if !isAuthenticated redirect to /
  Story 5.1.4 [ACA-05-004]  RequireRole.tsx: if user lacks anyOf roles, redirect to /app/connect
               Destructive action gating: confirmation modal before grant/lock/reconcile
  Story 5.1.5 [ACA-05-005]  All admin routes require RequireAuth + RequireRole (ACA_Admin|Support|FinOps)

Feature 5.2 -- Layout layer (NEW from docs 22-23)
  Story 5.2.1 [ACA-05-006]  CustomerLayout.tsx: top nav with logo, LanguageSelector, user menu
               Wraps all /app/* routes via Outlet
  Story 5.2.2 [ACA-05-007]  AdminLayout.tsx: top nav + left sidebar with admin nav items
               Wraps all /admin/* routes via Outlet
  Story 5.2.3 [ACA-05-008]  NavCustomer.tsx: links to /app/connect, /app/status, /app/findings
  Story 5.2.4 [ACA-05-009]  NavAdmin.tsx: links to /admin/dashboard, /admin/customers,
               /admin/billing, /admin/runs, /admin/controls
  Story 5.2.5 [ACA-05-010]  AppShell.tsx: root component with FluentProvider + ConsentBanner +
               RouterProvider (replaces App.tsx BrowserRouter pattern)

Feature 5.3 -- Router (Spark createBrowserRouter pattern)
  Story 5.3.1 [ACA-05-011]  router.tsx uses createBrowserRouter (not BrowserRouter + <Routes>)
  Story 5.3.2 [ACA-05-012]  Route / -> LoginPage (no auth required)
  Story 5.3.3 [ACA-05-013]  Routes /app/* -> RequireAuth -> CustomerLayout -> Outlet
  Story 5.3.4 [ACA-05-014]  Routes /admin/* -> RequireAuth -> RequireRole -> AdminLayout -> Outlet
  Story 5.3.5 [ACA-05-015]  Code-split: all page components lazy-loaded with React.lazy

Feature 5.4 -- Customer pages (/app/*)
  Story 5.4.1 [ACA-05-016]  LoginPage (/) -- Entra ID login CTA + dev bypass link
  Story 5.4.2 [ACA-05-017]  ConnectSubscriptionPage (/app/connect) -- Mode A/B/C radio group;
               calls POST /v1/auth/connect then POST /v1/collect/start;
               stores subscriptionId in sessionStorage after connect
  Story 5.4.3 [ACA-05-018]  CollectionStatusPage (/app/status/:subscriptionId) -- polls
               GET /v1/collect/status with backoff; shows named steps + progress bar;
               links to /app/findings/:subscriptionId when collection complete
  Story 5.4.4 [ACA-05-019]  FindingsTier1Page (/app/findings/:subscriptionId) -- renders Tier 1
               report from GET /v1/reports/tier1; shows MoneyRangeBar + EffortBadge
               per finding; blurred upgrade CTA rows for Tier 2+ findings
  Story 5.4.5 [ACA-05-020]  UpgradePage (/app/upgrade/:subscriptionId) -- Tier 2 vs Tier 3 cards;
               calls POST /v1/billing/checkout with tier in body;
               handles redirectUrl from Stripe response

Feature 5.5 -- Admin pages (/admin/*) (NEW from docs 21/22/23)
  Story 5.5.1 [ACA-05-021]  AdminDashboardPage (/admin/dashboard) -- calls GET /v1/admin/kpis;
               displays MRR (CAD), active subscriptions, scans/day, failure rate %
  Story 5.5.2 [ACA-05-022]  AdminCustomersPage (/admin/customers) -- search input calls
               GET /v1/admin/customers?query=; displays tier, paymentStatus,
               isLocked, lastActivityUtc; deep links to customer runs
  Story 5.5.3 [ACA-05-023]  AdminBillingPage (/admin/billing) -- Stripe billing portal link;
               webhook health indicator; "Reconcile Stripe" button calls
               POST /v1/admin/stripe/reconcile with confirmation modal
  Story 5.5.4 [ACA-05-024]  AdminRunsPage (/admin/runs) -- lists runs from GET /v1/admin/runs;
               supports filter by subscriptionId and type (scan|analysis|delivery)
  Story 5.5.5 [ACA-05-025]  AdminControlsPage (/admin/controls) -- grant tier form (subscriptionId,
               tier, days, reason); lock/unlock subscription form; rate-limit override;
               feature flag toggles; incident banner text input;
               all destructive actions write admin_audit_events via backend

Feature 5.6 -- API client layer (NEW from doc 22)
  Story 5.6.1 [ACA-05-026]  frontend/src/app/api/client.ts -- base http<T> function; includes
               credentials; throws on non-ok; Content-Type application/json
  Story 5.6.2 [ACA-05-027]  frontend/src/app/api/appApi.ts -- customer API calls:
               getTier1Report, startCollection, getStatus, getEntitlement,
               startCheckout, getBillingPortalUrl
  Story 5.6.3 [ACA-05-028]  frontend/src/app/api/adminApi.ts -- admin API calls:
               kpis, searchCustomers, grantEntitlement, lockSubscription,
               reconcileStripe, getRuns
  Story 5.6.4 [ACA-05-029]  frontend/src/app/types/models.ts -- TypeScript DTOs:
               Tier1Report, Finding, AdminKpis, AdminCustomerRow, Entitlement,
               CollectionStatus, AdminCustomerSearchResponse

Feature 5.7 -- Shared components (NEW from doc 22)
  Story 5.7.1 [ACA-05-030]  Loading.tsx -- full-page or inline Fluent Spinner with aria-label
  Story 5.7.2 [ACA-05-031]  ErrorState.tsx -- Fluent MessageBar (error) with retry callback
  Story 5.7.3 [ACA-05-032]  DataTable.tsx -- accessible Fluent Table wrapper (th scope=col)
  Story 5.7.4 [ACA-05-033]  MoneyRangeBar.tsx -- visual low/high saving range bar with currency label
  Story 5.7.5 [ACA-05-034]  EffortBadge.tsx -- colour-coded badge: trivial/easy/medium/involved/strategic

Feature 5.8 -- Consent and telemetry integration
  Story 5.8.1 [ACA-05-035]  As a user I see a consent banner on first visit (ConsentBanner reused)
  Story 5.8.2 [ACA-05-036]  TelemetryProvider.tsx wraps CustomerLayout; loads GTM + Clarity scripts
               only when VITE_ENABLE_TELEMETRY=true AND consent granted
  Story 5.8.3 [ACA-05-037]  All 16 AnalyticsEventName events fire at correct points in customer flow
  Story 5.8.4 [ACA-05-038]  Admin surface does NOT load telemetry (no GA4 in admin pages)

Feature 5.9 -- Accessibility
  Story 5.9.1 [ACA-05-039]  Skip-to-content link is first focusable element on every page
  Story 5.9.2 [ACA-05-040]  Full keyboard navigation in all customer and admin pages
  Story 5.9.3 [ACA-05-041]  All form fields have associated label elements
  Story 5.9.4 [ACA-05-042]  Admin confirmation modals trap focus and close on Escape

=============================================================================
EPIC 6 -- MONETIZATION AND BILLING (M1.5)
=============================================================================

Goal: Stripe checkout, webhook, entitlements, recurring billing lifecycle all work.

Feature 6.1 -- Stripe checkout (DECISIONS LOCKED 2026-02-27)
  Prices are env-var driven (STRIPE_PRICE_* settings). NOT hardcoded.
  Billing is monthly subscription for Tier 2. Tier 3 is one-time.
  Promotion codes are supported (full fee waiver for trials/partnerships).

  Story 6.1.1 [ACA-06-001]  POST /v1/checkout/tier2 returns a Stripe checkout session URL
  Story 6.1.2 [ACA-06-002]  POST /v1/checkout/tier3 returns a Stripe checkout session URL
  Story 6.1.3 [ACA-06-003]  mode=subscription creates a Stripe subscription (Tier 2 monthly)
  Story 6.1.4 [ACA-06-004]  mode=one_time creates a one-time session (Tier 2 one-time, Tier 3)
  Story 6.1.5 [ACA-06-005]  Checkout metadata contains subscriptionId and analysisId
  Story 6.1.6 [ACA-06-006]  As a client with a coupon code I can enter it at Stripe checkout
               and receive a partial or full fee waiver
               (allow_promotion_codes=True when STRIPE_COUPON_ENABLED=true)
  Story 6.1.7 [ACA-06-007]  settings.py has STRIPE_COUPON_ENABLED: bool = True field
               stripe_service.py passes allow_promotion_codes=setting to checkout session
  Story 6.1.8 [ACA-06-008]  As an admin I can create Stripe promotion codes for trial clients
               without any code changes (pure Stripe dashboard action)

Feature 6.2 -- Webhook lifecycle
  Story 6.2.1 [ACA-06-009]  checkout.session.completed -> write entitlement to Cosmos, trigger delivery
               if Tier 3
  Story 6.2.2 [ACA-06-010]  invoice.paid -> renew Tier 2 subscription entitlement for next period
  Story 6.2.3 [ACA-06-011]  customer.subscription.updated -> update Tier in Cosmos clients container
  Story 6.2.4 [ACA-06-012]  customer.subscription.deleted -> downgrade to Tier 1 in Cosmos unless Tier 3 permanent
  Story 6.2.5 [ACA-06-013]  All webhook events written to payments container for audit trail

Feature 6.3 -- Entitlement service
  Story 6.3.1 [ACA-06-014]  GET /v1/entitlements?subscriptionId=X returns { tier, validUntil, features[] }
  Story 6.3.2 [ACA-06-015]  Tier gate evaluates entitlement from Cosmos (with APIM 60s cache)
  Story 6.3.3 [ACA-06-016]  StripeCustomerMapRepo resolves stripeCustomerId -> subscriptionId for webhooks
  Story 6.3.4 [ACA-06-017]  Billing portal endpoint derives stripeCustomerId from Cosmos clients container
               (never from browser input -- security requirement)
  Story 6.3.5 [ACA-06-018]  As a Tier 3 customer, when my Tier 2 subscription is canceled (subscription.deleted)
               my Tier 3 one-time purchase access is preserved. revoke() must not unconditionally
               set tier=1. Correct logic: if existing.tier >= 3, new_tier = 3 else new_tier = 1.
               payment_status is always set to canceled regardless. A customer who paid $1,499
               one-time for Tier 3 must not lose access due to a Tier 2 subscription lifecycle event.

=============================================================================
EPIC 7 -- DELIVERY PACKAGER (M1.6)
=============================================================================

Goal: Tier 3 deliverable ZIP generated, uploaded, SAS URL delivered.

Feature 7.1 -- IaC template library (DECISION LOCKED 2026-02-27: Bicep only)
  Templates are Bicep only. Terraform is NOT included in delivery templates
  to keep Phase 1 simple. Generator skips missing main.tf gracefully (TemplateNotFound pass).

  Story 7.1.1 [ACA-07-001]  12 Jinja2 template folders exist in services/delivery/app/templates/
               (one per deliverable_template_id from analysis rules)
               Folders: tmpl-devbox-autostop, tmpl-log-retention, tmpl-defender-plan,
               tmpl-compute-schedule, tmpl-anomaly-alert, tmpl-stale-envs,
               tmpl-search-sku, tmpl-acr-consolidation, tmpl-dns-consolidation,
               tmpl-savings-plan, tmpl-apim-token-budget, tmpl-chargeback-policy
  Story 7.1.2 [ACA-07-002]  Each folder has main.bicep and README.md (Bicep Phase 1 only;
               main.tf is deferred to Phase 2 / Epic 11)
  Story 7.1.3 [ACA-07-003]  Templates are parameterized with scan_id, subscription_id, and finding fields
  Story 7.1.4 [ACA-07-004]  Template content sourced from 12-IaCscript.md patterns

Feature 7.2 -- Package and deliver
  Story 7.2.1 [ACA-07-005]  Delivery service generates all IaC artifacts for a scan's findings
  Story 7.2.2 [ACA-07-006]  ZIP is assembled with findings.json manifest at root
  Story 7.2.3 [ACA-07-007]  ZIP is signed with SHA-256 and the hash stored in the deliverables container
  Story 7.2.4 [ACA-07-008]  ZIP is uploaded to Azure Blob Storage with 24h SAS URL
  Story 7.2.5 [ACA-07-009]  Deliverable record is written to Cosmos with sasUrl, sha256, artifactCount

=============================================================================
EPIC 8 -- OBSERVABILITY AND TELEMETRY (M2.0)
=============================================================================

Goal: GA4, Clarity, App Insights all wired. Zero PII in any telemetry event.

Feature 8.1 -- Frontend telemetry
  Story 8.1.1 [ACA-08-001]  GTM container is loaded in index.html with consent gating
  Story 8.1.2 [ACA-08-002]  GA4 tag fires after consent accepted
  Story 8.1.3 [ACA-08-003]  Clarity tag fires after consent accepted with form field masking ON
  Story 8.1.4 [ACA-08-004]  All 16 AnalyticsEventName events are fired at correct points in the UI
  Story 8.1.5 [ACA-08-005]  Consent banner allows accept/reject: rejected state suppresses all tags
  Story 8.1.6 [ACA-08-006]  Consent preference is respected across page reloads (localStorage)

Feature 8.2 -- Backend observability
  Story 8.2.1 [ACA-08-007]  App Insights connection string is set in all Container Apps via KV reference
  Story 8.2.2 [ACA-08-008]  All service logs are structured JSON and appear in Azure Monitor
  Story 8.2.3 [ACA-08-009]  Scan duration, analysis duration, delivery duration are emitted as custom metrics
  Story 8.2.4 [ACA-08-010]  All API errors (4xx, 5xx) are logged with error_category enum (no raw messages)
  Story 8.2.5 [ACA-08-011]  Stripe webhook events are logged with event type + subscriptionId (hashed)

Feature 8.3 -- Alerting
  Story 8.3.1 [ACA-08-012]  Alert: API service 5xx rate > 5% in 5 minutes -> PagerDuty / email
  Story 8.3.2 [ACA-08-013]  Alert: Collector job failure -> email + Cosmos audit record
  Story 8.3.3 [ACA-08-014]  Alert: Anomaly detection rule fires -> owner notified (Story R-05 output)

=============================================================================
EPIC 9 -- i18n AND a11y (M2.1)
=============================================================================

Goal: All 5 locales live. WCAG 2.1 AA passing in axe-core CI gate.

Feature 9.1 -- i18n
  Story 9.1.1 [ACA-09-001]  i18next is configured with 5 locale namespaces in frontend/src/i18n/
  Story 9.1.2 [ACA-09-002]  All user-visible strings are extracted to translation files (no hardcoded EN text)
  Story 9.1.3 [ACA-09-003]  Language selector is visible in the nav with locale names in their own language:
               English, Francais, Portugues (Brasil), Espanol, Deutsch
  Story 9.1.4 [ACA-09-004]  Locale preference is persisted in localStorage
  Story 9.1.5 [ACA-09-005]  Date formats use Intl.DateTimeFormat -- locale-aware, no hardcoded format
  Story 9.1.6 [ACA-09-006]  Number/currency formats use Intl.NumberFormat with locale and currency options:
               CAD, USD, BRL, EUR supported on findings page saving estimates
  Story 9.1.7 [ACA-09-007]  fr (fr-CA) translations are completed before Phase 1 go-live
               (required for Canadian market)
  Story 9.1.8 [ACA-09-008]  pt-BR, es, and de translations are completed before Phase 1 go-live
               as best-effort machine translation (DECISION LOCKED 2026-02-27:
               all 5 locales ship in Phase 1; professional review is Phase 2 hardening)
  Story 9.1.9 [ACA-09-009]  API error messages returned with Accept-Language header support for the
               5 supported locales (error codes + localized message)
  Story 9.1.10 Stripe checkout locale is set from user preference

Feature 9.2 -- a11y (DECISION LOCKED 2026-02-27: Playwright headless CI)
  Story 9.2.1 [ACA-09-010]  axe-core CI check runs on every PR -- zero critical or serious violations gate
  Story 9.2.2 [ACA-09-011]  All icon-only buttons have aria-label in all 5 locales
  Story 9.2.3 [ACA-09-012]  All form fields have associated <label> elements (no placeholder-as-label)
  Story 9.2.4 [ACA-09-013]  Findings table has proper <th scope="col"> headers
  Story 9.2.5 [ACA-09-014]  PreFlight status indicators use both colour and icon/text (not colour-only)
  Story 9.2.6 [ACA-09-015]  Colour contrast ratio >= 4.5:1 for all body text (verified in Figma + axe)
  Story 9.2.7 [ACA-09-016]  Focus ring is visible and high-contrast on all focusable elements
  Story 9.2.8 [ACA-09-017]  Skip-to-content link is the first focusable element on every page
  Story 9.2.9 [ACA-09-018]  Consent banner is keyboard-accessible and screen-reader-labelled
  Story 9.2.10 Keyboard-only walkthrough of the full Tier 1 flow passes before M1.4 sign-off
  Story 9.2.11 Playwright headless tests cover the Tier 1 customer flow with axe-core
               assertions. Target: 95% end-to-end coverage. CI gate blocks on failure.
               All 5 locales exercised in Playwright suite. Runs on ubuntu-latest headless.

=============================================================================
EPIC 10 -- COMMERCIAL HARDENING (M2.2)
=============================================================================

Goal: Security review passed, privacy compliance ready, support tooling live.

Feature 10.1 -- Security
  Story 10.1.1 [ACA-10-001]  Red-team agent runs Tier 1 token against findings API and asserts
                no narrative or deliverable_template_id in response
  Story 10.1.2 [ACA-10-002]  All endpoints validated: no tenant A can access tenant B data
                (partition key enforcement verified in integration tests)
  Story 10.1.3 [ACA-10-003]  Stripe webhook signature verified on every event (whsec_ secret)
  Story 10.1.4 [ACA-10-004]  Admin endpoints protected by bearer token rotation schedule
  Story 10.1.5 [ACA-10-005]  All Cosmos queries parameterized (no string concatenation in queries)
  Story 10.1.6 [ACA-10-006]  CSP header enforced: scripts from GTM/Stripe/Clarity only, no inline

Feature 10.2 -- Privacy compliance
  Story 10.2.1 [ACA-10-007]  Privacy policy published at /privacy in all 5 locales
  Story 10.2.2 [ACA-10-008]  Terms of service published at /terms in all 5 locales
  Story 10.2.3 [ACA-10-009]  Data retention policy: collected Azure data purged after 90 days
                (Cosmos container TTL = 7,776,000 seconds on scans, inventories, cost-data)
  Story 10.2.4 [ACA-10-010]  Client can request data deletion via DELETE /v1/auth/disconnect which
                hard-deletes all Cosmos documents for that subscriptionId
  Story 10.2.5 [ACA-10-011]  GA4 data retention set to 14 months. IP anonymization enabled.
  Story 10.2.6 [ACA-10-012]  Clarity data retention respects GDPR right-to-be-forgotten via Clarity API

Feature 10.3 -- Support and docs
  Story 10.3.1 [ACA-10-013]  docs/client-access-guide.md published at /docs/access-guide in all 5 locales
  Story 10.3.2 [ACA-10-014]  FAQ page covers top 10 support questions (from preflight failure analysis)
  Story 10.3.3 [ACA-10-015]  Status page (uptime) linked from footer

=============================================================================
EPIC 11 -- PHASE 2 INFRASTRUCTURE (M3.0)
=============================================================================

Goal: Private subscription provisioned, CI pointing to Phase 2, domain live.

Feature 11.1 -- Terraform provisioning
  Story 11.1.1 [ACA-11-001]  `terraform apply` on infra/phase2-private completes without error
  Story 11.1.2 [ACA-11-002]  ACA-specific APIM instance is deployed with Tier enforcement policies
  Story 11.1.3 [ACA-11-003]  GitHub Actions deploy-phase2.yml is wired to private subscription via OIDC
  Story 11.1.4 [ACA-11-004]  Custom domain (app.aca.example.com / api.aca.example.com) configured with
                managed TLS via Azure Container Apps ingress
  Story 11.1.5 [ACA-11-005]  Phase 2 Cosmos has 3 geo-replicas (canadacentral primary + failover)

Feature 11.2 -- Cutover
  Story 11.2.1 [ACA-11-006]  DNS TTL lowered 48h before cutover
  Story 11.2.2 [ACA-11-007]  Phase 1 marco* infra remains live as rollback for 30 days post-cutover
  Story 11.2.3 [ACA-11-008]  Phase 2 smoke test: full Tier 1 -> Tier 3 flow on Phase 2 infra
  Story 11.2.4 [ACA-11-009]  APIM configuration exported and version-controlled

=============================================================================
EPIC 12 -- DATA MODEL SUPPORT (ONGOING)
=============================================================================

Goal: EVA data model used as source of truth for build process and as app runtime API.

Feature 12.1 -- Build-time use
  Story 12.1.1 [ACA-12-001]  All epics, features, and stories from this PLAN are seeded into
                the data-model WBS layer with epic, feature, and user_story node types preserved
  Story 12.1.2 [ACA-12-002]  Each story has status: not-started / in-progress / done
  Story 12.1.3 [ACA-12-003]  Story status is updated by the agent at start and end of each work item
  Story 12.1.4 [ACA-12-004]  data-model agent-summary reflects current overall completion percentage

Feature 12.2 -- Runtime use
  Story 12.2.1 [ACA-12-005]  API service reads feature_flags layer to gate unreleased features
  Story 12.2.2 [ACA-12-006]  Analysis service reads the rules layer to discover enabled/disabled rules
               (data-model rules layer matches services/analysis/app/rules/ files)
  Story 12.2.3 [ACA-12-007]  Endpoints layer is kept in sync with every shipped route (PUT on ship)
  Story 12.2.4 [ACA-12-008]  Containers layer reflects the actual Cosmos schema (fields, partition keys)

Feature 12.3 -- Phase 1 Core Infrastructure & Containers
  Story 12.3.1 [ACA-12-009]  Cosmos DB aca-db + scans container with 256-partition key on subscriptionId
                (Phase 1 marco* sandbox, infra/phase1-marco/main.bicep)
  Story 12.3.2 [ACA-12-010]  inventories container for Azure resource snapshots (partition key: subscriptionId)
  Story 12.3.3 [ACA-12-011]  cost-data container for monthly cost export and FinOps hub landing zone
  Story 12.3.4 [ACA-12-012]  advisor container for Azure Advisor recommendations + scores
  Story 12.3.5 [ACA-12-013]  findings container for analysis rule output (indexed on risk_class, effort_class)
  Story 12.3.6 [ACA-12-014]  APIM ACA product + subscription key policy for tier-gated rate limiting
  Story 12.3.7 [ACA-12-015]  Key Vault secrets wiring (ACA-CLIENT-ID, ACA-OPENAI-KEY, ACA-COSMOS-CONN)
  Story 12.3.8 [ACA-12-016]  Container App Job definitions for collector, analysis, delivery workers

Feature 12.4 -- Data Model Safe Cleanup and Ground-Up Restore
  Execution order: snapshot -> scoped cleanup -> re-prime -> README/PLAN refresh -> WBS rebuild -> Veritas audit
  Gate: do not execute cleanup until the README scope refresh is merged and the snapshot evidence pack exists
  Story 12.4.1 [ACA-12-029]  Snapshot the live `projects/51-ACA`, WBS, evidence, and related governance rows
                before any delete so the restore can prove exactly what was removed and why
  Story 12.4.2 [ACA-12-030]  Execute a scoped cleanup that deletes only 51-ACA WBS and evidence records,
                preserves the canonical project identity row, and records API correlation IDs for every delete
  Story 12.4.3 [ACA-12-031]  Re-prime 51-ACA through Project 07 after cleanup and verify governance
                scaffolding, project registration, and PROJECT-ORGANIZATION continuity remain intact
  Story 12.4.4 [ACA-12-032]  Regenerate the project hierarchy from README + PLAN top-down into the
                data-model WBS layer, preserving epic -> feature -> user_story relationships
  Story 12.4.5 [ACA-12-033]  Run a bottom-up reconciliation that flags missing user_story leaves,
                duplicate IDs, orphan evidence, and legacy `/model/stories` dependencies as explicit gaps
  Story 12.4.6 [ACA-12-034]  Publish a restore evidence pack plus Veritas audit results and do not
                re-open cloud sprint execution until the rebuilt WBS counts and trust score are accepted

=============================================================================
MILESTONES
=============================================================================

Milestone  Target      Epic(s)   Deliverable
---------  ----------  --------  -------------------------------------------
M1.0       +2 weeks    1         Local dev works. Phase 1 Bicep deployed.
M1.1       +3 weeks    2         Collector runs against EsDAICoE-Sandbox.
M1.2       +3 weeks    3         12 rules produce findings. Tier gate passes.
M1.3       +3 weeks    4         All 15 API endpoints live behind APIM.
M1.4       +4 weeks    5         All 9 frontend pages. Tier 1 flow end-to-end.
M1.5       +4 weeks    6         Stripe checkout + webhook + entitlements live.
M1.6       +5 weeks    7         Tier 3 zip delivered via SAS URL.
M2.0       +5 weeks    8         GA4 + Clarity + App Insights all live.
M2.1       +6 weeks    9         EN + FR live. axe-core CI gate green.
M2.2       +7 weeks    10        Red-team passes. Privacy docs published.
M3.0       +10 weeks   11        Phase 2 infra live. Custom domain active.

=============================================================================
RISKS
=============================================================================

R1  APIM policy for Tier gating conflicts with EVA POC APIM policies (Phase 1 reuse)
    Mitigation: test on a cloned policy in a dev product. Isolate by API path prefix.

R2  Stripe account not yet created for production environment
    Mitigation: create Stripe account in test mode now. Go live with real keys at M1.5.

R3  Azure Conditional Access in client tenant blocks Mode A delegated consent
    Mitigation: document Mode B (SP) clearly. Build Mode B UI in M1.3 scope.

R4  Google Tag Manager consent mode 2.0 requirements for EU clients (GDPR)
    Mitigation: implement TCF-compatible consent mode banner at M2.0.

R5  i18n content quality for pt-BR and es may require professional translator review
    Mitigation: use machine translation for M2.1 sprint. Flag for professional review M2.2.

R6  PIPEDA and LGPD compliance review may require legal opinion
    Mitigation: engage AICOE legal by M2.2. Privacy policy drafted by M2.1.

=============================================================================
DEPENDENCIES
=============================================================================

D1  14-az-finops -- saving-opportunities.md (seeded all 12 rules)
D2  18-azure-best -- 11-module playbook (infra patterns, APIM, Terraform)
D3  Azure AI Foundry Agent SDK -- AI agent framework for analysis agents (collection, analysis, generation, redteam)
D4  Fluent UI v9 -- Microsoft component library for React 19 frontend (npm package, no EVA dependency)
D5  REMOVED -- 51-ACA has its own standalone data model (data-model/); no dependency on any shared EVA model
D6  48-eva-veritas -- traceability (audit_repo gates trust score)
D7  Stripe account (marco production) -- needed before M1.5
D8  Google Analytics 4 property ID (existing marco account) -- needed at M2.0
D9  Microsoft Clarity project ID (existing marco account) -- needed at M2.0
D10 Private Azure subscription for Phase 2 -- needed before M3.0
D11 18-azure-best library (32 modules) -- consumed by Epic 13 analysis rules
D12 GitHub Models API token (GITHUB_TOKEN) -- consumed by Epic 14 DPDCA agent

=============================================================================
FUNCTION POINT INDEX AND VELOCITY TRACKING
=============================================================================

Sizing scale (IFPUG simplified):
  XS = 1 FP  (config only, flag, env var)
  S  = 3 FP  (single route, simple model)
  M  = 5 FP  (feature + unit tests)
  L  = 9 FP  (cross-service integration)
  XL = 20 FP (major integration: multi-service + UI + tests)

Story ID format: ACA-EE-NNN  (EE = epic number, NNN = sequential within epic)
EVA-STORY tag:   # EVA-STORY: ACA-EE-NNN  (Python) or // EVA-STORY: ACA-EE-NNN (JS/Bicep)

Epic Function Point Totals (estimated):
| Epic | Title                            | Stories | Est FP | Sprint | Status      |
|------|----------------------------------|---------|--------|--------|-------------|
|  1   | Foundation and Infrastructure    |  20     |  65    |  1-2   | DONE        |
|  2   | Data Collection Pipeline         |  12     |  70    |  2     | DONE        |
|  3   | Analysis Engine + Rules          |  30     | 155    |  2-3   | PARTIAL     |
|  4   | API and Auth Layer               |  25     | 125    |  3     | IN PROGRESS |
|  5   | Frontend Core                    |  40     | 175    |  3-4   | IN PROGRESS |
|  6   | Billing (Stripe)                 |  13     |  65    |  2-3   | DONE        |
|  7   | Delivery Packager                |  10     |  80    |  4     | NOT STARTED |
|  8   | Observability and Telemetry      |  13     |  55    |  4-5   | PARTIAL     |
|  9   | i18n and a11y                    |  21     |  85    |  4-5   | IN PROGRESS |
| 10   | Commercial Hardening             |  15     |  90    |  5-6   | NOT STARTED |
| 11   | Phase 2 Infrastructure           |   9     | 100    |  7-9   | NOT STARTED |
| 12   | Data Model Support               |  22     |  75    |  ongo  | ONGOING     |
| 13   | Azure Best Practices Catalog     |  12     |  55    |  4-5   | PLANNED     |
| 14   | DPDCA Cloud Agent                |  10     |  65    |  3-5   | IN PROGRESS |
| 15   | Onboarding System (Client SaaS)  |  22     |  72    | 14-17  | PLANNED     |
| TOTAL|                                  | ~282    | ~1382  |        |             |

Sprint Velocity:
| Sprint | Dates              | Scope                                     | FP Completed | Notes            |
|--------|--------------------|-------------------------------------------|--------------|------------------|
|   0    | Feb 19-26, 2026    | Bootstrap, repo, data model, infra Bicep  |    ~120      | CLOSED           |
|   1    | Feb 26-Mar 5, 2026 | API core, auth, collector, analysis rules |    ~95       | IN PROGRESS      |
|   2    | Mar 5-12, 2026     | Frontend, Tier gates, delivery stub       |    TBD       | PLANNED          |
|   3    | Mar 12-19, 2026    | i18n, a11y, observability, hardening      |    TBD       | PLANNED          |
|   4    | Mar 19-26, 2026    | Azure best-practices catalog, DPDCA       |    TBD       | PLANNED          |
|   5    | Mar 26-Apr 2, 2026 | Phase 2 infra, commercial hardening       |    TBD       | PLANNED          |
Projected velocity: 80-100 FP per sprint (2 engineers)

Story ID Roster (all 22 shipped stories, EVA-STORY tags confirmed):
  ACA-01-001  GET /stats admin dashboard (admin.py)
  ACA-02-001  DELETE /scans/{scan_id} purge endpoint (scans.py)
  ACA-03-001  POST /connect subscription onboarding (auth.py)
  ACA-04-001  POST /preflight RBAC probe (auth.py)
  ACA-05-001  POST /disconnect tenant offboarding (auth.py)
  ACA-06-001  POST /checkout/tier2 Stripe session (checkout.py)
  ACA-07-001  POST /checkout/tier3 Stripe session (checkout.py)
  ACA-08-001  POST /checkout/webhook Stripe event handler (checkout.py)
  ACA-09-001  GET /checkout/entitlements tier query (checkout.py)
  ACA-10-001  GET /{scan_id}/findings tier-gated (findings.py)
  ACA-10-002  GET /{scan_id}/inventory tenant-scoped (scans.py)
  ACA-11-001  GET /health readiness probe (health.py)
  ACA-12-001  FastAPI app factory + CORS middleware (main.py)
  ACA-12-002  Settings and env config (main.py)
  ACA-12-009  Cosmos DB aca-db + scans container (main.bicep)
  ACA-12-010  inventories container (main.bicep)
  ACA-12-011  cost-data container (main.bicep)
  ACA-12-012  advisor container (main.bicep)
  ACA-12-013  findings container (main.bicep)
  ACA-12-014  APIM ACA product + subscription policy (main.bicep)
  ACA-12-015  Key Vault secrets wiring (main.bicep)
  ACA-12-016  Container App Job definitions (main.bicep)

=============================================================================
EPIC 13 -- AZURE BEST PRACTICES SERVICE CATALOG
=============================================================================

Milestone: M2.3
Sprint: 4-5
Status: PLANNED
WBS: 13.x.x
Description: ACA consumes the 18-azure-best 32-module library to expose a governed
  set of best-practice assessments as API-gated service endpoints. Each rule maps to
  one or more entries in the 18-azure-best library. Engineers must read
  C:\eva-foundry\18-azure-best before implementing rules.

Related dependencies: D11 (18-azure-best library)

Feature 13.1 -- WAF Assessment Endpoint
  Story ACA-13-009  GET /v1/assessment/waf scores subscription against 5 WAF pillars
    Source: 18-azure-best/02-well-architected/waf-overview.md
    FP: M=5  Sprint: 4
    EVA-STORY tag: # EVA-STORY: ACA-13-009
    Acceptance: returns pillar_scores dict with reliability, security, cost, ops, performance;
                each score 0-100; based on inventory snapshot in Cosmos

  Story ACA-13-010  WAF reliability pillar rules (APRL checklist integration)
    Source: 18-azure-best/05-resiliency/aprl.md
    FP: L=9  Sprint: 4
    EVA-STORY tag: # EVA-STORY: ACA-13-010
    Acceptance: maps at least 5 APRL items to findings; linked to finding IDs

Feature 13.2 -- FinOps Best Practices Rules
  Story ACA-13-011  FinOps advisor rules R-13 to R-17 from best-practices library
    Source: 18-azure-best/08-finops/ (all .md files)
    FP: L=9  Sprint: 4
    EVA-STORY tag: # EVA-STORY: ACA-13-011
    Acceptance: 5 new rules pass unit tests in services/analysis/tests/

  Story ACA-13-012  Idle resource detection rule (classic cost waste)
    Source: 18-azure-best/08-finops/cost-optimization.md
    FP: M=5  Sprint: 4
    EVA-STORY tag: # EVA-STORY: ACA-13-012
    Acceptance: detects VMs stopped but not deallocated; finding effort_class=trivial

Feature 13.3 -- Security Assessment Rules
  Story ACA-13-013  RBAC hygiene check (over-scoped contributor assignments)
    Source: 18-azure-best/12-security/rbac.md
    FP: M=5  Sprint: 4
    EVA-STORY tag: # EVA-STORY: ACA-13-013
    Acceptance: flags subscriptions where Owner or Contributor > 5 principals

  Story ACA-13-014  Key Vault access policy audit (legacy vs RBAC mode)
    Source: 18-azure-best/12-security/key-vault.md
    FP: S=3  Sprint: 4
    EVA-STORY tag: # EVA-STORY: ACA-13-014
    Acceptance: detects Key Vaults not in RBAC mode; risk_class=medium

  Story ACA-13-015  MCSB control compliance check (Defender for Cloud)
    Source: 18-azure-best/12-security/mcsb.md
    FP: M=5  Sprint: 5
    EVA-STORY tag: # EVA-STORY: ACA-13-015
    Acceptance: queries Defender score via REST; maps each MCSB control gap to a finding

Feature 13.4 -- APIM and API Design Rules
  Story ACA-13-016  APIM rate-limit policy health check
    Source: 18-azure-best/03-architecture-center/apim.md
    FP: S=3  Sprint: 4
    EVA-STORY tag: # EVA-STORY: ACA-13-016
    Acceptance: detects APIs without rate-limit policy; finding effort_class=easy

  Story ACA-13-017  API design compliance check (versioning, idempotency, error codes)
    Source: 18-azure-best/03-architecture-center/api-design.md
    FP: S=3  Sprint: 5
    EVA-STORY tag: # EVA-STORY: ACA-13-017
    Acceptance: checks ACA-own API spec against design rules; CI gate added

Feature 13.5 -- IaC Quality Gate
  Story ACA-13-018  PSRule for Azure gate on all Bicep templates
    Source: 18-azure-best/07-iac/bicep.md
    FP: M=5  Sprint: 5
    EVA-STORY tag: # EVA-STORY: ACA-13-018
    Acceptance: PSRule runs in CI; FAIL blocks merge; existing violations suppressed

  Story ACA-13-019  Best-practice tag enforcement (cost-center, environment, owner)
    Source: 18-azure-best/07-iac/bicep.md
    FP: S=3  Sprint: 5
    EVA-STORY tag: # EVA-STORY: ACA-13-019
    Acceptance: Bicep template outputs enforce 3 mandatory tags; CI gate validates

Total Epic 13 FP estimate: 55 FP (11 stories)

=============================================================================
EPIC 14 -- DPDCA CLOUD AGENT (GitHub Actions Sprint Automation)
=============================================================================

Milestone: M2.4
Sprint: 3-5
Status: IN PROGRESS
WBS: 14.x.x
Description: A fully governed CI/CD agent loop where sprint backlog items are
  discussed in chat, submitted as GitHub Issues with the DPDCA template, and
  executed by a gpt-4o-mini-powered GitHub Actions workflow. Evidence is recorded
  to .eva/evidence/ and verified by Veritas on every run. No work ships without a
  passing trust score and a merged PR.

Model: gpt-4o-mini via GitHub Models API (models.inference.ai.azure.com)
       Azure OpenAI deployment as fallback (marco-sandbox-openai-v2)

Feature 14.1 -- Sprint Backlog Item Template
  Story ACA-14-001  .github/ISSUE_TEMPLATE/agent-task.yml captures Story ID, WBS ID,
    Epic, FP Size (XS/S/M/L/XL), Sprint, User Story, Inputs, Outputs, Acceptance,
    Spec References, Files to modify, Constraints, Depends On, Pre-flight checklist
    FP: S=3  Sprint: 3
    Status: DONE (this session)
    EVA-STORY tag: // EVA-STORY: ACA-14-001
    Source: .github/ISSUE_TEMPLATE/agent-task.yml

  Story ACA-14-002  Issue template validation: Story ID must match ACA-NN-NNN format
    FP: XS=1  Sprint: 3
    Status: DONE (inline in workflow parse step)
    EVA-STORY tag: // EVA-STORY: ACA-14-002

Feature 14.2 -- GitHub Actions DPDCA Workflow
  Story ACA-14-003  .github/workflows/dpdca-agent.yml D1 phase: parse issue, load
    PLAN.md + copilot-instructions into agent-context.txt
    FP: M=5  Sprint: 3
    Status: DONE (this session)
    EVA-STORY tag: // EVA-STORY: ACA-14-003
    Source: .github/workflows/dpdca-agent.yml

  Story ACA-14-004  P phase: Python Plan-step calls gpt-4o-mini with context,
    writes agent-plan.md to artifacts
    FP: M=5  Sprint: 3
    Status: DONE (this session)
    EVA-STORY tag: // EVA-STORY: ACA-14-004

  Story ACA-14-005  D2 phase: create branch agent/ACA-NN-NNN-TIMESTAMP, write
    evidence receipt .eva/evidence/ACA-NN-NNN-DATE.json
    FP: S=3  Sprint: 3
    Status: DONE (this session)
    EVA-STORY tag: // EVA-STORY: ACA-14-005

  Story ACA-14-006  C phase: run ruff check + pytest --co; fail workflow on error
    FP: M=5  Sprint: 3
    Status: DONE (this session -- stub, tests may fail until code is written)
    EVA-STORY tag: // EVA-STORY: ACA-14-006

  Story ACA-14-007  A phase: commit with Story ID in message, run Veritas audit,
    enforce no-deploy NOT in actions before opening PR
    FP: M=5  Sprint: 3
    Status: DONE (this session)
    EVA-STORY tag: // EVA-STORY: ACA-14-007

Feature 14.3 -- Agent Context and Model Wiring
  Story ACA-14-008  GitHub Models API integration (GITHUB_TOKEN, endpoint, model param)
    FP: S=3  Sprint: 12
    Status: DONE
    EVA-STORY tag: # EVA-STORY: ACA-14-008
    Acceptance: Plan step returns structured JSON with phases, files, acceptance_check fields

  Story ACA-14-009  Azure OpenAI fallback wiring (AZURE_OPENAI_KEY + endpoint env vars)
    FP: S=3  Sprint: 12
    Status: DONE
    EVA-STORY tag: # EVA-STORY: ACA-14-009
    Acceptance: if GITHUB_TOKEN absent, fallback activates with no code change required

Feature 14.4 -- Evidence and Veritas Integration
  Story ACA-14-010  Evidence receipt schema validation: story_id, wbs_id, epic,
    branch, model, test_result fields all required
    FP: S=3  Sprint: 12
    Status: DONE
    EVA-STORY tag: # EVA-STORY: ACA-14-010
    Acceptance: malformed receipt causes workflow FAIL; Veritas confirms .eva/evidence/ readable

Feature 14.5 -- Sprint Workflow V2 Foundation (Observability Infrastructure)
  Story 14.5.1 [ACA-14-001]  As the sprint agent I want a unified SprintContext class that merges
    correlation ID, LM tracer, and timeline tracking so that I can eliminate 100+
    manual propagation points and ensure complete audit trail coverage
    FP: M=5  Sprint: 11
    Status: DONE
    EVA-STORY tag: # EVA-STORY: ACA-14-011
    Files to create:
      - .github/scripts/sprint_context.py (SprintContext class, ~200 lines)
      - .github/scripts/aca_lm_tracer.py (ACALMTracer adapted from 37-data-model, ~180 lines)
    Files to modify:
      - .github/scripts/sprint_agent.py (initialize SprintContext, pass to all story functions)
    Acceptance:
      - SprintContext("SPRINT-11") generates correlation_id in format ACA-S11-YYYYMMDD-uuid8
      - ctx.log("D1", "test") outputs [TRACE:ACA-S11-...] [D1] test
      - ctx.record_lm_call(model="gpt-4o-mini", tokens_in=1000, tokens_out=500, phase="D1") stores LMCall
      - ctx.save() writes .eva/sprints/SPRINT-11-context.json with correlation_id + timeline + lm_calls
      - Sprint 11 execution logs show 50+ [TRACE:...] lines
    Implementation notes:
      - Correlation ID format simplified per Opus review: ACA-S{NN}-{YYYYMMDD}-{uuid[:8]}
      - The context object is passed through all DPDCA phases
      - Every log line, LM call, and timeline mark goes through SprintContext methods
      - Zero manual propagation needed

  Story 14.5.2 [ACA-14-002]  As the sprint agent I want a state lock mechanism that prevents duplicate
    sprint dispatch so that concurrent workflow triggers do not corrupt evidence or data model
    FP: S=3  Sprint: 11
    Status: DONE
    EVA-STORY tag: # EVA-STORY: ACA-14-012
    Files to create:
      - .eva/locks/.gitkeep (ensure directory exists in git)
      - .github/scripts/state_lock.py (acquire_lock, release_lock functions, ~80 lines)
    Files to modify:
      - .github/scripts/sprint_agent.py (add lock acquisition at start, release in finally block)
    Acceptance:
      - First acquire_lock("SPRINT-11", "12345", "ACA-S11-...") creates .eva/locks/SPRINT-11.lock, returns True
      - Second acquire_lock("SPRINT-11", "67890", "ACA-S11-...") returns False (lock exists)
      - release_lock("SPRINT-11") deletes .eva/locks/SPRINT-11.lock
      - Sprint agent workflow fails immediately (exit 1) if lock acquisition fails
      - Lock is released on both success and exception (finally block)
    Implementation notes:
      - Lock file contains: sprint_id, workflow_run_id, started_at, correlation_id, locked_by
      - This is the idempotency guard recommended by Opus (Risk #2)
      - Prevents data corruption from user re-trigger, network retry, agent restart

  Story 14.5.3 [ACA-14-003]  As the sprint agent I want phase verification checkpoints after each DPDCA
    phase so that silent failures are caught early before multi-agent handoffs in Phase 3
    FP: M=6  Sprint: 11
    Status: DONE
    EVA-STORY tag: # EVA-STORY: ACA-14-013
    Files to create:
      - .github/scripts/phase_verifier.py (5 verification functions, ~120 lines)
      - .github/scripts/test_phase_verifier.py (pytest tests for all 5 checkpoints)
    Files to modify:
      - .github/scripts/sprint_agent.py (call verify functions after each DPDCA phase)
      - .github/workflows/dpdca-agent.yml (add --skip-checkpoint flag for transient issues)
    Acceptance:
      - verify_d1_evidence("SPRINT-10", 6) returns True (Sprint 10 has 6 evidence files)
      - verify_d2_repo_audit(ctx) parses pytest output, returns True if test_count > 0
      - verify_p_plan_update(ctx, "SPRINT-10", 4) checks PLAN.md for 4 [x] marks
      - verify_d3_story_selection(ctx, "SPRINT-11") checks docs/SPRINT-11-MANIFEST.md exists
      - Intentional failure (break pytest) causes workflow to stop with clear error message
    Implementation notes:
      - Moved from Phase 4 to Phase 1 per Opus recommendation
      - Needed before multi-agent handoffs (Phase 3) to ensure safe context transfer
      - Allow override via --skip-checkpoint flag for known transient issues (e.g., data model temporarily unreachable)
      - On failure: log error, halt workflow, return exit code 1

Total Epic 14 FP estimate: 50 FP (13 stories)

=============================================================================
EPIC 15 -- ONBOARDING SYSTEM (M4.0)
=============================================================================

Goal: Comprehensive client onboarding automation. CLI + SaaS backend + React UI.
Retrieve inventory, costs, Azure Advisor + analysis. Generate immutable evidence.

Status: PLANNED (Architecture: ARCHITECTURE-ONBOARDING-SYSTEM.md, v2.0.0, Grade A-)
Revised Effort: 52 FP (5.2 sprints @ 10 FP/sprint) [gap analysis added 7 FP]
Dependencies: 18-azure-best library (patterns integration), 31-eva-faces (React UI)

Feature 15.1 -- Infrastructure & Cosmos DB Setup
  Story 15.1.1 [ACA-15-000]  Infrastructure provisioning: Bicep for Cosmos (9 containers)
    FP: 2  Sprint: 14  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-000
    Files to create:
      - infra/onboarding.bicep (Cosmos containers, TTL, indexes, RBAC)
      - infra/keyvault.bicep (HMAC signing key)
      - infra/rbac.bicep (ACA Managed Identity role assignments)
    Acceptance:
      - [ ] 9 Cosmos containers created: onboarding-sessions, role-assessments, extraction-manifests,
            inventories, cost-data, advisor-recommendations, findings, extraction-logs, evidence-receipts
      - [ ] All containers have partition key /subscriptionId
      - [ ] TTL policies: 90 days (operational), 365 days (findings), NEVER (evidence-receipts)
      - [ ] Indexes on: engagementId, subscriptionId, currentGate, status
      - [ ] RU/s: 400 shared (MVP), autoscale production
      - [ ] ACA MI has Reader + Cost Management Reader roles

  Story 15.1.2 [ACA-15-001]  Cosmos DB schema implementation (9 containers all deployed)
    FP: 3  Sprint: 14  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-001
    Files:
      - services/aca-onboarding/cosmos_schema.py (container initialization, indexed fields)
    Acceptance:
      - [ ] All 9 containers exist with correct partition key
      - [ ] TTL policies applied per Section 1.3 of arch spec
      - [ ] Schema document validates against actual Cosmos DB
      - [ ] Test: Insert documents in each container, verify partition isolation

  Story 15.1.2a [ACA-15-001a]  GDPR/PIPEDA data residency constraint (Canada-only enforcement)
    FP: 1  Sprint: 14  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-001a
    Files:
      - infra/cosmos.bicep (geo-replication disable policy)
      - services/aca-onboarding/models.py (add gdpr_consent_timestamp field)
    GAP-5 Resolution:
      - [ ] Bicep enforces: allowRegionForGeoRepFlag = false (no multi-region replication)
      - [ ] GDPR consent timestamp captured on GATE_0
      - [ ] All Cosmos writes restricted to canadacentral (policy enforced)
      - [ ] Test: Verify Cosmos replication disabled, consent captured

Feature 15.2 -- Gate State Machine & FastAPI Backend
  Story 15.2.1 [ACA-15-002]  Gate state machine (7-gate workflow with timeout/retry logic)
    FP: 3  Sprint: 14  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-002
    Files:
      - services/aca-onboarding/state_machine.py (200 lines, gate transitions, timeouts)
      - services/aca-onboarding/models.py (Enums: Gate, GateStatus, state transition rules)
    Acceptance:
      - [ ] Enum: Gate (1-7), GateStatus (PASSED, FAILED, TIMEOUT, RETRY_REQUESTED, etc)
      - [ ] State machine class with transition rules + timeout handling
      - [ ] All 7 gate transitions defined: GATE_1 ? GATE_2 ? ... ? COMPLETED
      - [ ] Timeout on GATE_2 (client decision): 4 hours
      - [ ] GATE_1 retry on role elevation: supported
      - [ ] Test: Verify all state transitions, timeout firing

  Story 15.2.1a [ACA-15-002a]  User consent & terms acceptance flow (GATE_0 pre-flight consent)
    FP: 2  Sprint: 14  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-002a
    Files:
      - services/aca-onboarding/models.py (add consent fields: terms_version_accepted, consent_timestamp)
      - services/aca-onboarding/state_machine.py (add GATE_0 transition rule)
    GAP-8 Resolution:
      - [ ] GATE_0 (before GATE_1): "Accept data extraction and analysis ToS"
      - [ ] Consent timestamp + version stored (terms_version_accepted: "2026-03-01")
      - [ ] Flow fails if consent not accepted
      - [ ] Consent persists across sessions
      - [ ] Test: Verify flow fails without consent, persists with consent

  Story 15.2.2 [ACA-15-003]  FastAPI backend routes (POST /init, GET /{id}, decision handling)
    FP: 4  Sprint: 15  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-003
    Files:
      - services/aca-onboarding/main.py (FastAPI app, routes with auth)
      - services/aca-onboarding/auth.py (JWT validation, delegated token refresh)
    Acceptance:
      - [ ] POST /api/v1/onboarding/init (create session, start GATE_1)
      - [ ] GET /api/v1/onboarding/{engagementId} (retrieve session state)
      - [ ] POST /api/v1/onboarding/{engagementId}/decision (record gate decision)
      - [ ] Bearer token validation on all endpoints
      - [ ] Rate limiting: 100 req/min per subscription (APIM policy)
      - [ ] Health endpoint: GET /health ? {"status": "ok"}
      - [ ] All routes support tenant isolation (partition_key=subscriptionId)

  Story 15.2.2a [ACA-15-003a]  OpenAPI/Swagger specification (auto-generated from FastAPI)
    FP: 2  Sprint: 15  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-003a
    Files:
      - services/aca-onboarding/openapi.yaml (generated from FastAPI, checked into repo)
      - docs/api-spec.md (OpenAPI reference and SDK generation guide)
    GAP-1 Resolution:
      - [ ] Generate OpenAPI 3.0 spec from FastAPI routes (auto-generates via /openapi.json)
      - [ ] Document OpenAPI spec endpoint, validate schema completeness
      - [ ] Publish spec to GitHub releases for SDK generation (Python, TypeScript clients)
      - [ ] Test: Generate SDK from spec, verify all endpoints work

  Story 15.2.2b [ACA-15-003b]  Unified error response schema with error codes (ACA-ERR-001, etc)
    FP: 1  Sprint: 15  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-003b
    Files:
      - services/aca-onboarding/errors.py (error code enum: ACA-ERR-001, ACA-ERR-002, ...)
      - services/aca-onboarding/models.py (ErrorResponse schema)
    GAP-2 Resolution:
      - [ ] Error code enum: ACA-ERR-001 (ROLE_MISSING), ACA-ERR-002 (QUOTA_EXCEEDED), etc
      - [ ] Response schema: {"error": "ACA-ERR-001", "message": "...", "details": {...}}
      - [ ] Add error schema to all endpoints
      - [ ] Test: Verify 20+ error scenarios return correct error codes

Feature 15.3 -- Azure SDK Wrappers (Paginated, Rate-Limit Aware)
  Story 15.3.1 [ACA-15-004]  Azure SDK wrappers + pagination + retry logic
    FP: 6  Sprint: 15  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-004
    Files:
      - services/aca-onboarding/azure_sdk.py (600 lines: Resource Graph, Cost API, Advisor)
    CRITICAL:
      - Resource Graph pagination (1,000 items/page, 15 req/sec limit)
      - Cost Management pagination (1,000 rows/page, 10 req/min, 30-day windows)
      - Advisor pagination (100 items/page, 5 req/sec)
      - Exponential backoff for 429 (4s, 8s, 16s, 32s, 64s)
      - 3 concurrent workers for cost data (respect 10 req/min)
      - Batch writes to Cosmos (100 items/batch)
    Acceptance:
      - [ ] Resource Graph query wrapper (paginated, respects rate limit)
      - [ ] Cost API wrapper (91-day query, 30-day windows, 3 workers)
      - [ ] Advisor wrapper (paginated, handles 403 gracefully)
      - [ ] Retry logic: 429 retried with exponential backoff
      - [ ] Batch write: write_cost_data_batch(100 items/batch)
      - [ ] Integration test: extract 500+ resources, 45K cost rows from marco-sandbox
      - [ ] Performance test: extract 45K rows in <10 minutes
      - [ ] Simulate 429: verify retry succeeds

Feature 15.4 -- CLI & Extraction Pipeline
  Story 15.4.1 [ACA-15-005]  CLI command structure (init, resume, list, get, logs, retry-extract)
    FP: 3  Sprint: 15  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-005
    Files:
      - cli/aca_cli.py (400 lines, command structure)
      - cli/auth.py (Azure CLI tok acquisition + device code fallback)
    CRITICAL:
      - Azure CLI token: `az account get-access-token`
      - Device code fallback: if Azure CLI not installed
      - Token refresh: auto-refresh if expires
    Acceptance:
      - [ ] Commands: init, resume, list, get, extract-logs, retry-extraction
      - [ ] Auth: Azure CLI integration, device code fallback, token refresh
      - [ ] Prompts: yes/no decisions, progress display, estimated times
      - [ ] Output: table, json, text formats
      - [ ] Test: CLI end-to-end (interactive, no actual extraction)
      - [ ] Test: Device code flow (no Azure CLI requirement)

  Story 15.4.2 [ACA-15-006]  Extraction pipeline (inventory + costs + advisor with recovery)
    FP: 5  Sprint: 16  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-006
    Files:
      - services/aca-onboarding/extraction.py (700 lines, 3 extraction phases)
    Acceptance:
      - [ ] extract_inventory() with pagination, logs progress
      - [ ] extract_cost_data() with 3 parallel workers, logs progress (respect 10 req/min)
      - [ ] extract_advisor() with pagination, skip if role missing (not a failure)
      - [ ] Recovery checkpoints: lastSuccessfulPage, lastSuccessfulWindow
      - [ ] All operations log to extraction-logs container (phase, operation, progress, checkpoint)
      - [ ] Integration test: extract from marco-sandbox, verify Cosmos write
      - [ ] Performance test: 500+ resources in <2min, 45K cost rows in <10min

  Story 15.4.2a [ACA-15-006a]  Token refresh during long extractions (20+ min extraction window)
    FP: 2  Sprint: 15  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-006a
    Files:
      - services/aca-onboarding/auth.py (add token refresh loop)
      - services/aca-onboarding/models.py (add refresh_token field, token_expires_at)
    GAP-3 & GAP-9 Resolution:
      - [ ] Implement token refresh loop: check expiry before each Azure SDK call
      - [ ] Use MSAL acquire_token_by_refresh_token() if access token within 2-min expiry
      - [ ] Store refresh token securely (Cosmos encrypted field, not in logs)
      - [ ] Exponential backoff if refresh fails (retry 3x)
      - [ ] Test: Simulate 15-min token expiry mid-extraction, verify extraction completes

  Story 15.4.2b [ACA-15-006b]  Partial failure handling (API timeout resilience)
    FP: 3  Sprint: 15  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-006b
    Files:
      - services/aca-onboarding/extraction.py (add try/except per API)
      - services/aca-onboarding/logging.py (failure logging with skip-flag)
    GAP-6 Resolution:
      - [ ] Extraction succeeds even if 1/3 APIs fails (inventory + costs succeeds, Advisor times out)
      - [ ] Log failure to extraction-logs, note "advisor_skipped=true" in manifest
      - [ ] Analysis accepts partial findings (cost + heuristics work without Advisor)
      - [ ] Test: Simulate Advisor 504, verify extraction succeeds with cost data only

  Story 15.4.3 [ACA-15-007]  Logging + recovery mechanism (detailed operation logs, resume)
    FP: 2  Sprint: 16  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-007
    Files:
      - services/aca-onboarding/logging.py (200 lines, extraction-logs writes)
    Acceptance:
      - [ ] Every operation logs to extraction-logs container
      - [ ] Recovery checkpoint stored with each log (lastSuccessfulPage, nextPage, resumeAt)
      - [ ] GET /extract-logs returns paginated logs with checkpoints
      - [ ] POST /extract/retry resumes from last checkpoint
      - [ ] Test: Simulate extraction failure, verify resume succeeds

Feature 15.5 -- Analysis + Evidence
  Story 15.5.1 [ACA-15-008]  Analysis rules engine (18-azure-best pattern integration)
    FP: 6  Sprint: 16  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-008
    Files:
      - services/aca-onboarding/analysis.py (600 lines)
      - services/aca-onboarding/heuristics/*.py (7 pattern modules)
    CRITICAL:
      - Integration with 18-azure-best patterns (cost-optimization, anti-patterns)
      - 7 heuristics: vm-rightsizing, reserved-capacity, storage-tiering, orphan-resources,
        unattached-disks, idle-resources, cost-anomalies
      - Narrative generation (explain WHY recommendation applies, reference 18-azure-best)
    Acceptance:
      - [ ] Heuristics: right-sizing (CPU <30%), reserved capacity, storage tiering
      - [ ] Anti-pattern detection (10 patterns from 18-azure-best)
      - [ ] Findings: ranked by savings (DESC), filtered by effort (easy/medium/hard)
      - [ ] Narratives reference 18-azure-best documentation URLs
      - [ ] Test: Apply rules to 100-item test dataset, verify 12+ findings
      - [ ] Test: Validate narratives reference 18-azure-best

  Story 15.5.2 [ACA-15-009]  Evidence receipt generation (HMAC-SHA256 cryptographic signing)
    FP: 2  Sprint: 16  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-009
    Files:
      - services/aca-onboarding/evidence.py (200 lines, HMAC signing)
    CRITICAL:
      - HMAC-SHA256 signature computed over canonical JSON (sorted keys, no whitespace)
      - Key Vault integration: retrieve ACA-HMAC-SigningKey
      - Verification function: verify_evidence_receipt returns True/False
    Acceptance:
      - [ ] Build immutable evidence-receipt per ARCHITECTURE Section 7.2
      - [ ] HMAC-SHA256 signature computed + appended
      - [ ] Key Vault integration (retrieve signing key via DefaultAzureCredential)
      - [ ] Signature fields: signature, signedAt, signatureAlgorithm, keyVaultKeyId
      - [ ] Verification: detect tampered receipts
      - [ ] Cosmos write: evidence-receipts container, NO TTL (permanent retention)
      - [ ] GET /evidence returns full receipt + tamper_check (is_valid=True/False)
      - [ ] Test: Modify receipt, verify verification fails
      - [ ] Test: Rotate HMAC key, verify old receipts still verify

  Story 15.5.2a [ACA-15-009a]  Evidence-receipts search/indexing strategy (composite indexes)
    FP: 2  Sprint: 16  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-009a
    Files:
      - infra/cosmos.bicep (add evidence-receipts indexes)
      - services/aca-onboarding/evidence.py (add search methods: query_by_subscription_date)
    GAP-7 Resolution:
      - [ ] Add composite indexes: (subscriptionId, signedAt), (subscriptionId, status), (subscriptionId, heuristic_count)
      - [ ] Cosmos create indexes in Bicep (cosmosIndexPolicy)
      - [ ] Implement search methods: query_evidence_by_subscription_date(subscriptionId, startDate, endDate)
      - [ ] Test: Query evidence by subscription + date range, measure RU/s consumption

  Story 15.5.3 [ACA-15-010]  Integration tests (all gates, security, performance)
    FP: 4  Sprint: 16  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-010
    Files:
      - tests/test_onboarding_gates.py (500 lines, end-to-end flow)
      - tests/test_security.py (200 lines, GDPR, token validation, RBAC)
      - tests/test_performance.py (150 lines, latency, extraction time, RU/s)
    Acceptance:
      - [ ] End-to-end test: init ? role assessment ? decision ? preflight ? extraction ? analysis ? evidence
      - [ ] Test with marco-sandbox subscription
      - [ ] All 7 gates pass with no errors
      - [ ] Evidence receipt valid (signature verification passes)
      - [ ] Security: GDPR delete removes PII from 8 operational containers
      - [ ] Security: Evidence receipt PII redacted (not deleted)
      - [ ] Security: Invalid token returns 401, cross-tenant access returns 403
      - [ ] Performance: POST /init latency <500ms
      - [ ] Performance: Extract 500 resources in <2min, 45K cost rows in <10min
      - [ ] Performance: Analysis completes in <5min

Feature 15.6 -- React UI Integration (via 31-eva-faces)
  Story 15.6.1 [ACA-15-011]  React components (role assessment, preflight, extraction progress)
    FP: 5  Sprint: 17  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-011
    Files: 31-eva-faces/src/components/onboarding/*.tsx
    Acceptance:
      - [ ] Role assessment report card (show discovered roles, recommendation)
      - [ ] Preflight manifest card (extraction plan, sizes, duration)
      - [ ] Extraction progress card (real-time logs, progress bar, ETA)
      - [ ] Polling: GET /extract-logs every 2 seconds during extraction

  Story 15.6.2 [ACA-15-012]  Findings report UI (savings display, PDF export, tier selector)
    FP: 5  Sprint: 17  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-012
    Files: 31-eva-faces/src/pages/findings.tsx
    Acceptance:
      - [ ] Display savings opportunities (ranked, effort, risk)
      - [ ] PDF export (findings + evidence summary)
      - [ ] Service menu tier selector (Tier 1/2/3 gating)
      - [ ] Evidence receipt display (with tamper check)

  Story 15.6.2a [ACA-15-012a]  Export formats (CSV/Excel/PDF) for findings report
    FP: 3  Sprint: 17  Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-15-012a
    Files:
      - services/aca-onboarding/export.py (CSV/Excel helpers, ~200 lines)
      - Route: GET /findings/export?format=csv|excel|pdf
    GAP-10 Resolution:
      - [ ] PDF export: findings + savings bar chart + evidence summary (existing)
      - [ ] CSV export: one row per finding (id, category, saving_low, saving_high, effort, heuristic)
      - [ ] Excel export: CSV + second sheet (pivot: category x effort with counts, savings totals)
      - [ ] Test: Export 100 findings, verify data integrity and pivot calculations

Total Epic 15 FP estimate: 72 FP (22 stories: 12 original + 10 gaps)

=============================================================================
SPRINT: PRE-FLIGHT
Added: 2026-02-27 (opus review session -- human approved all 5 stories)
Goal: Unblock Sprint 2 by fixing CRITICAL bugs, creating missing spec docs,
      and stabilizing the governance baseline.
Blocker gate: MTI >= 30 (lowered from 70; restore at Sprint 3 boundary)
=============================================================================

  Story ACA-06-021  Remove duplicate Stripe webhook stub
    FP: XS=1  Model: XS  Sprint: pre-flight  Epic: 6
    Status: PLANNED
    EVA-STORY tag: # EVA-STORY: ACA-06-021
    Files: services/api/app/routers/checkout.py
    Description: Delete the duplicate @router.post("/webhook") stub at lines 351-403
                 that shadows the real verified handler at line 149. This is a revenue-
                 breaking bug (C-05): FastAPI registers the LAST definition, so the stub
                 with no signature verification is the active handler. Stripe revenue
                 is completely broken until this is fixed.
    Acceptance:
    - Only one @router.post("/webhook") decorator exists in checkout.py
    - Real handler at line 149 survives: reads raw_body, calls stripe.Webhook.construct_event
    - pytest: POST /v1/checkout/webhook with invalid sig returns 400
    - pytest: POST /v1/checkout/webhook with valid sig calls handler logic
    - No duplicate route error in FastAPI startup log

  Story ACA-03-021  Fix FindingsAssembler missing cosmos_client argument
    FP: XS=1  Model: XS  Sprint: pre-flight  Epic: 3
    Status: DONE (Sprint-02)
    EVA-STORY tag: # EVA-STORY: ACA-03-021
    Files: services/analysis/app/main.py
    Description: FindingsAssembler.__init__ requires 3 args: scan_id, subscription_id,
                 cosmos_client. The current call in main.py passes only 2 args (missing
                 cosmos_client), causing TypeError on every analysis run (bug C-04).
    Acceptance:
    - services/analysis/app/main.py instantiates FindingsAssembler with all 3 args
    - C:\eva-foundry\.venv\Scripts\python.exe -c "from services.analysis.app.main import run; print('[PASS]')" succeeds
    - pytest: FindingsAssembler with mock cosmos_client constructs without error

  Story ACA-07-021  Fix generate_blob_sas call and SAS_HOURS constant
    FP: S=3  Model: S  Sprint: pre-flight  Epic: 7
    Status: DONE (Sprint-02)
    EVA-STORY tag: # EVA-STORY: ACA-07-021
    Files: services/delivery/app/packager.py
    Description: Two bugs in packager.py (bug C-07):
                 (1) generate_blob_sas() called with credential=DefaultAzureCredential()
                     which is an invalid API call -- TypeError at runtime. Must use account_key.
                 (2) SAS_HOURS = 24 but spec requires 168 (7 days per docs/12-IaCscript.md).
    Acceptance:
    - SAS_HOURS = 168 in packager.py
    - generate_blob_sas() called with account_key parameter (not credential)
    - pytest: mock blob client test confirms SAS token generated without TypeError
    - SAS expiry is confirmed to be datetime.now(utc) + timedelta(hours=168)

  Story ACA-12-021  Create missing spec docs in docs/
    FP: S=3  Model: S  Sprint: pre-flight  Epic: 12
    Status: DONE (this session 2026-02-27)
    EVA-STORY tag: # EVA-STORY: ACA-12-021
    Files: docs/02-preflight.md, docs/05-technical.md, docs/08-payment.md,
           docs/saving-opportunity-rules.md, docs/12-IaCscript.md
    Description: Five spec docs referenced in copilot-instructions.md did not exist.
                 All created this session with authoritative content from P2.1-P2.9.
    Acceptance:
    - docs/02-preflight.md exists (onboarding + pre-flight RBAC probes spec)
    - docs/05-technical.md exists (full API spec, 27 endpoints, code patterns)
    - docs/08-payment.md exists (Stripe flow, webhook safety, tier model)
    - docs/saving-opportunity-rules.md exists (12 rules, FINDING schema, tier gating)
    - docs/12-IaCscript.md exists (IaC template library, 12 template folders, SAS rules)
    - All files are ASCII-only with EVA-STORY: ACA-12-021 tag

  Story ACA-12-022  Lower MTI gate to 30 for Sprint 2 pre-flight
    FP: XS=1  Model: XS  Sprint: pre-flight  Epic: 12
    Status: DONE (this session 2026-02-27)
    EVA-STORY tag: # EVA-STORY: ACA-12-022
    Files: .github/copilot-instructions.md
    Description: MTI baseline was 70 but honest MTI=5 (250 stories vs ~8 tagged files).
                 Gate lowered to 30 with explicit sunset at Sprint 3 boundary.
                 Human approved this decision 2026-02-27.
    Acceptance:
    - CA.2 Veritas gate reads MTI >= 30
    - CA.5 Current baseline reads MTI=30 with sunset note
    - Restore to 70 condition documented
    - EVA-STORY tag present in copilot-instructions.md

Total Pre-flight Sprint FP estimate: 9 FP (5 stories; 2 DONE, 3 PLANNED)

=============================================================================
END OF PLAN
=============================================================================
