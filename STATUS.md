ACA -- Azure Cost Advisor -- STATUS
====================================

Version: 1.4.0
Updated: 2026-02-28 (Sprint-01 A step: 5 stories done, PR #11 merged to main at 9b62f0f)
Phase: Phase 1 -- Core Services Bootstrap
Active Epic: Epic 3 (analysis rules), Epic 4 (API endpoints), Epic 5 (frontend), Epic 12 (data model)

=============================================================================
SESSION SUMMARY -- 2026-02-28 (SPRINT-01 COMPLETE + EVA DECOUPLING)
=============================================================================

Commits this session:
  37a989b -- EVA decoupling (5 files: copilot-instructions, AGENTS.md, sonnet_review.py,
             server.py, PLAN.md -- all marco-eva-data-model cloud URLs removed)
  fef132d -- fix(ACA-03-033): fix test import paths + DI for EntitlementService +
             extract findings_gate module -- 5/5 unit tests pass
  9b62f0f -- Sprint-01 PR #11 squash-merged to main (18 files, 2298 insertions)

Sprint-01 stories completed (5/5):
  [DONE] ACA-02-017  ingest.py -- analysis job trigger (graceful degradation if env not set)
  [DONE] ACA-03-006  findings_gate.py extracted + GET /v1/findings/:scanId tier gating
  [DONE] ACA-04-028  cosmos.py upsert_item() with explicit partition_key parameter
  [DONE] ACA-06-018  entitlement_service.py revoke() preserves tier=3 on Stripe cancel
  [DONE] ACA-03-033  5 unit tests pass (test_findings_gate x3, test_entitlement_revoke x2)

Test count: 5 passing (pytest services/ -x -q exits 0)
MTI baseline: 30 (lowered 2026-02-27 for Sprint-01 pre-flight; raise to 70 at Sprint-03)
Data model: 332 objects (SQLite, port 8055 local) -- EVA cloud URL removed, standalone

Architecture decisions locked this session:
  - 51-ACA is STANDALONE -- no dependency on any EVA repo or cloud endpoint
  - Data model served from data-model/db.py direct import (cloud agents) or localhost:8055
  - findings_gate.py is pure logic (no I/O) -- importable in unit tests without env vars
  - EntitlementService uses DI pattern (repo=None default) for testability
  - pyproject.toml pythonpath = [".", "services/api"] for both import styles

OPEN (not yet started):
  1. copilot-setup-steps.yml -- pre-install deps in GitHub Actions ephemeral env
  2. Per-service AGENTS.md files (services/api/AGENTS.md etc.)
  3. .github/agents/sprint-executor.agent.md (native Copilot agent profile)
  4. Sprint-02 stories (Epic 3 rules, Epic 4 auth stubs, Epic 5 frontend scaffold)

=============================================================================
SESSION SUMMARY -- 2026-02-27 (ROUND 2 REVIEW + PRE-FLIGHT FIXES)
=============================================================================

Review tool: Claude Sonnet 4.6 (code verification + fix implementation)
Commit: 4816baf (pushed to main)
Trigger: "opus fixes implemented -- check the code, update the review for a second round"

ROUND 2 FINDING: 0 of 3 pre-flight bugs had been fixed in source code before this session.
C-05 ESCALATED: the stub block at checkout.py lines 349-403 was not just a duplicate
  webhook route -- it reassigned the `router` variable entirely, orphaning all 5 real
  endpoints (tier2, tier3, webhook with sig verification, portal, entitlements).

IMPROVEMENTS CONFIRMED SINCE ROUND 1:
  - gate_findings() in findings.py now correctly implemented (TIER1_FIELDS / TIER2_FIELDS)
  - entitlement_service.py grant_tier2/grant_tier3: correct, downgrade protection present
  - cosmos.py: ensure_containers() added with all 11 containers (idempotent, correct PK paths)
  - auth.py: stubs now have proper spec references, ConnectRequest/PreflightResponse models

BUGS FIXED THIS SESSION (commit 4816baf):
  [DONE] C-05-v2  checkout.py lines 349-403 -- stub block deleted, real router unmutated.
                  All 5 real endpoints now mounted: tier2, tier3, webhook+sig, portal, entitlements.
  [DONE] C-04     analysis/main.py -- FindingsAssembler now receives cosmos_client.
                  New services/analysis/app/cosmos.py created with AnalysisCosmosClient class.
  [DONE] C-07     packager.py -- SAS_HOURS=168 (was 24), generate_blob_sas uses account_key.
                  delivery/main.py passes ACA_STORAGE_ACCOUNT_KEY env var to packager.

STILL OPEN (not pre-flight sprint -- require more work):
  C-01 / C-02  auth.py /connect and /preflight still 501 (blocked on Entra app reg HD-01)
  C-03         cosmos.py upsert_item() still no partition_key param
  C-06         findings.py endpoint still raises 404 unconditionally (gate_findings wired now)
  H-02         ingest.py mark_collection_complete() does not trigger analysis job
  H-03         entitlement_service.py revoke() forces tier=1, clears permanent Tier 3 purchase
  ZERO TESTS   No test files anywhere in services/ -- pytest exits 0 vacuously

NEXT PRIORITY ORDER (see Round 2 assessment in _opus_review_findings_20260227.md):
  1. findings.py -- wire Cosmos reads + gate_findings() into GET /{scan_id} handler (ACA-10-001)
  2. cosmos.py upsert_item -- add partition_key parameter (3-line fix, ACA-03-003)
  3. ingest.py -- add analysis job trigger in mark_collection_complete (ACA-03-006)
  4. entitlement_service.py revoke() -- preserve tier=3 if tier3_purchased (ACA-06-015)
  5. Minimum test suite: test_checkout_router.py, test_packager.py, test_analysis_main.py

=============================================================================
SESSION SUMMARY -- 2026-02-27 (OPUS REVIEW SESSION)
=============================================================================

Review tool: Claude Opus 4.6 (full codebase review per _opus_review_issue_draft.md)
Findings doc: _opus_review_findings_20260227.md (8 CRITICAL / 7 HIGH / 8 MEDIUM / 4 LOW)

HUMAN DECISIONS RECORDED:
  HD-01  Entra app registration: Human requested Application Developer role 2026-02-27.
         ACA-CLIENT-ID is pending. Mode A (delegated auth) is blocked until granted.
         Mode B (SP) remains the only working auth mode for Phase 1.
  HD-02  MTI gate lowered: 70 -> 30 for Sprint 2 pre-flight.
         Honest baseline was MTI=5 (250 stories vs ~8 tagged source files).
         Gate will be restored to 70 at Sprint 3 boundary after test suite >= 10 tests.
         Stub Bicep templates are acceptable for Sprint 2 delivery stories.
  HD-03  Pre-flight sprint created in PLAN.md (5 stories, 9 FP).
         Stories ACA-12-021 and ACA-12-022 are DONE this session.
         Stories ACA-06-021, ACA-03-021, ACA-07-021 are PLANNED for next session.

CRITICAL BUGS CONFIRMED (not yet fixed; fix in pre-flight sprint):
  C-05  Duplicate @router.post("/webhook") at checkout.py:383 shadows real handler at line 149
        Stripe revenue completely broken. Fix: ACA-06-021.
  C-04  FindingsAssembler missing cosmos_client arg in analysis/main.py
        TypeError on every analysis run. Fix: ACA-03-021.
  C-07  generate_blob_sas() invalid call + SAS_HOURS=24 (should be 168)
        Delivery packager crashes. Fix: ACA-07-021.

COMPLETED THIS SESSION:
  [DONE] Full architecture review -- 8 CRITICAL / 7 HIGH / 8 MEDIUM / 4 LOW findings written
  [DONE] docs/02-preflight.md created (onboarding + RBAC probes spec)
  [DONE] docs/05-technical.md created (27 endpoints, code patterns, known bugs)
  [DONE] docs/08-payment.md created (Stripe flow, webhook safety, tier model)
  [DONE] docs/saving-opportunity-rules.md created (12 rules, FINDING schema)
  [DONE] docs/12-IaCscript.md created (IaC template library, 12 template folders)
  [DONE] .github/copilot-instructions.md CA.2 + CA.5: MTI gate 70 -> 30
  [DONE] PLAN.md: pre-flight sprint block added with 5 stories

NEXT SESSION PRIORITIES (pre-flight sprint):
  1. ACA-06-021: Delete checkout.py lines 351-403 (duplicate webhook stub)
  2. ACA-03-021: Fix FindingsAssembler call in analysis/main.py (add cosmos_client)
  3. ACA-07-021: Fix packager.py SAS_HOURS=168 + generate_blob_sas account_key
  4. Run pytest to confirm all 3 bugs fixed and tests pass (exit 0)
  5. Commit + push pre-flight sprint completion

=============================================================================
CURRENT STATE (2026-02-27 PRE-SESSION, CARRIED FORWARD)
=============================================================================
=============================================================================

All four backend services are bootstrapped and import-verified. Frontend Spark
restructure is complete (Epic 5 DONE). Billing layer (Epic 6) is complete.
GitHub cloud agent framework is in place (AGENTS.md, devcontainer, ci.yml multi-job).
All pre-flight planning Q&A decisions are LOCKED (see DECISIONS LOCKED section below).

DATA MODEL (SQLite, owned by 51-ACA):
  Port: 8055 (own server, NOT a proxy to 37-data-model)
  Storage: data-model/aca-model.db (SQLite, gitignored, persistent across restarts)
  Total active objects: 325 (up from 102 memory-store baseline)
  Layers: agents=4, containers=11, endpoints=27, personas=4,
          requirements=264 (14 epics + 250 stories), screens=10, services=5
  Seed script: scripts/seed-from-plan.py --reseed-model (EXIT CODE 0)
  Start server: pwsh -File data-model/start.ps1 -> http://localhost:8055
  Docs: http://localhost:8055/docs

VERITAS (HONEST BASELINE after 250-story rebuild):
  MTI: 5 (was artificially 70 -- that was based on 32-story plan)
  Reason: 250 plan stories vs ~8 source files with EVA-STORY tags (Phase 1 skeleton)
  Next target: add EVA-STORY tags to all source files, target MTI 50+ (Sprint 2)
  no-deploy flag: CLEARED from previous session -- still valid for active files
  veritas-plan.json: 14 features, 250 stories, done=61, planned=189

ADO project: dev.azure.com/marcopresta/51-aca (Epic 2730, 12 Features, 16 PBIs).

=============================================================================
DECISIONS LOCKED (2026-02-27)
=============================================================================

I1  IaC deployment: Do NOT deploy to Azure now. Finish IaC files (Bicep + bootstrap.sh)
    in EsDAICoE-Sandbox / marco* resources first. Deploy when integration tests are ready.

I2  Auth model: ACA is standalone private-sector SaaS. NOT tied to EsDAICoE org.
    Multi-tenant Microsoft Entra (authority=common). Any client Microsoft account works.
    What matters: delegated token has Reader + Cost Management Reader on CLIENT subscription.
    ACA app registration must be multi-tenant. current auth.py stubs need full rework.

I3  bootstrap.sh is new -- create from scratch using 12-IaCscript.md + 13-IAC-more.md spec.
    Cover: Cosmos containers, KV secrets, ACA Container App + 3 Jobs, APIM product.
    Add DO_CONTAINERAPPS and DO_APIM toggle flags for partial re-runs.

S2  Stripe prices are env-var driven (STRIPE_PRICE_* not hardcoded). Prices are
    suggestions -- allow coupon/promotion codes. Full fee waiver via coupon is supported.
    Add STRIPE_COUPON_ENABLED: bool to settings. Pass allow_promotion_codes to checkout.

S3  Billing cycle: Tier 2 = monthly subscription (CAD). Tier 3 = one-time.

T1  Delivery templates: Bicep only for Phase 1. No Terraform in delivery templates yet.
    Generator skips missing main.tf gracefully. 12 folders: tmpl-devbox-autostop through
    tmpl-chargeback-policy.

T2  Template parameterization: simple variable substitution (scan_id, subscription_id,
    finding-specific fields from FINDING schema). Jinja2 already in generator.py.

Cov 95% end-to-end test coverage target. Playwright headless CI for a11y.
    One test module per rule with hardcoded FP JSON fixtures. No Cosmos calls in unit tests.

A1  a11y testing: Playwright headless (not cypress). Runs in GitHub Actions on ubuntu-latest.
    All 5 locales exercised in Playwright suite.

A2  i18n: all 5 locales (en, fr, es, de, pt-BR) ship in Phase 1 as best-effort machine
    translation. Professional review for pt-BR / es / de is Phase 2 hardening only.

D1  Phase 1 uses Azure Container Apps free hostnames (*.{region}.azurecontainerapps.io).
    No custom domain required for Phase 1. PUBLIC_APP_URL / PUBLIC_API_URL read from env.
    Phase 2 gets real custom domain (TBD).

D2  Repo stays in eva-foundry (private). Deployed to Azure. No GitHub org move needed.

=============================================================================
COMPLETED
=============================================================================

Infrastructure and Config
  [PASS] .gitignore, .env.example, pyproject.toml, docker-compose.yml
  [PASS] infra/phase1-marco/main.bicep + main.bicepparam (Cosmos 7-container wiring)
  [PASS] infra/phase2-private/main.tf + production.tfvars (full Terraform stack)
  [PASS] .github/workflows/ci.yml (ruff + mypy + pytest)
  [PASS] .github/workflows/deploy-phase1.yml (OIDC + ACR push + ACA deploy)
  [PASS] .github/workflows/collector-schedule.yml (nightly cron)

Governance
  [PASS] README.md -- full product vision, tiers, architecture, i18n, a11y,
                      third-party integrations, go-live phases, admin roles,
                      Spark routing, admin_audit_events container (docs 13-23)
  [PASS] PLAN.md   -- full WBS: 12 epics, 50+ features, 100+ user stories
  [PASS] STATUS.md -- this file (v0.5.0)
  [PASS] ACCEPTANCE.md -- all gates for Phase 1 and Phase 2
  [PASS] .github/copilot-instructions.md -- PART 2 fully written
  [PASS] All 23 source docs (01-23) onboarded and integrated

API Service (services/api/)
  [PASS] requirements.txt, Dockerfile
  [PASS] app/main.py (FastAPI factory, CORS, 6 routers, lifespan)
  [PASS] app/settings.py (pydantic-settings, lru_cache)
  [PASS] app/db/cosmos.py (tenant-isolated query_items, ensure_containers, 7 containers)
  [PASS] app/routers/health.py (GET /health)
  [PASS] app/routers/auth.py  (POST /v1/auth/connect, preflight, disconnect -- stubs)
  [PASS] app/routers/scans.py (POST, GET /:scanId, GET / -- stubs)
  [PASS] app/routers/findings.py (GET /:scanId with gate_findings -- tier gate works)
  [PASS] app/routers/checkout.py (POST /tier2, /tier3, webhook, portal, entitlements -- stubs)
  [PASS] app/routers/admin.py (GET /stats, DELETE /:id -- legacy; + 6 new admin endpoints, audit events)

Collector Service (services/collector/)
  [PASS] requirements.txt, Dockerfile
  [PASS] app/main.py (CLI: --scan-id, --subscription-id, --preflight-only, 5-step flow)
  [PASS] app/azure_client.py (AzureCollector: inventory, cost, advisor, policy, network)
  [PASS] app/preflight.py (5 probes -> PASS/PASS_WITH_WARNINGS/FAIL + blockers/warnings)
  [PASS] app/ingest.py (Ingestor: saves all 5 categories + marks collection complete)

Analysis Service (services/analysis/)
  [PASS] requirements.txt, Dockerfile
  [PASS] app/main.py (CLI, iterates ALL_RULES, uses FindingsAssembler)
  [PASS] app/findings.py (FindingsAssembler: load_collected_data, save_findings, mark_complete)
  [PASS] app/rules/__init__.py (imports all 12 rules into ALL_RULES)
  [PASS] app/rules/rule_01_devbox_autostop.py through rule_12_chargeback_gap.py (all 12)
  [PASS] Import check: ALL_RULES count=12 (no ImportError)

Delivery Service (services/delivery/)
  [PASS] requirements.txt, Dockerfile
  [PASS] app/main.py (CLI: --scan-id, --subscription-id, orchestrates generate+package)
  [PASS] app/generator.py (TemplateGenerator: Jinja2 per-finding template rendering)
  [PASS] app/packager.py (DeliverablePackager: ZIP + SHA-256 + Blob + 24h SAS URL)
  [PASS] app/cosmos.py (CosmosHelper: query_items, upsert_item, get_item)

Agents (agents/)
  [PASS] collection-agent.yaml
  [PASS] analysis-agent.yaml
  [PASS] generation-agent.yaml
  [PASS] redteam-agent.yaml

Data Model (data-model/)
  [PASS] README.md -- full layer guide, WBS, story model, runtime use
  [PASS] start.ps1 -- launcher on port 8011
  [PASS] model/epics.json -- 12 epics seeded
  [PASS] model/rules.json -- 12 analysis rules with thresholds and template IDs
  [PASS] model/i18n.json -- 5 locale definitions (en, fr, pt-BR, es, de)
  [PASS] model/currencies.json -- 5 currencies (CAD default, USD, BRL, EUR, GBP)
  [PASS] model/integrations.json -- 6 integrations (Stripe, GA4, Clarity, GTM, MSAL, Azure SDK)
  [PASS] model/containers.json -- 10 Cosmos containers with partition keys and field schemas
  [PASS] model/screens.json -- 10 frontend screens with routes and API calls
  [PASS] model/settings.json -- 25 settings: feature flags, rule gates, pricing, config
  [PASS] model/services.json -- updated with 5th service (aca-frontend)

Frontend (frontend/)
  [PASS] package.json (Vite 5, React 19, Fluent UI v9, i18next, react-router-dom)
  [PASS] vite.config.ts (proxy /v1/* to :8000, port 5173)
  [PASS] tsconfig.json + tsconfig.node.json
  [PASS] index.html (semantic root, lang=en, meta description)
  [PASS] src/main.tsx (FluentProvider + axe-core dev overlay)
  [PASS] src/App.tsx (BrowserRouter, 10 code-split lazy routes, ConsentBanner)
  [PASS] src/i18n/index.ts (i18next + react-i18next, 5 locales, formatCurrency)
  [PASS] public/locales/en/translation.json (ALL strings)
  [PASS] public/locales/fr/translation.json (FR translation -- needs review)
  [PASS] src/telemetry/consent.ts (consent state, GTM Consent Mode v2)
  [PASS] src/telemetry/gtm.ts (GTM loader, pushEvent)
  [PASS] src/telemetry/analytics.ts (16 AnalyticsEventName events + sanitizeParams)
  [PASS] src/components/ConsentBanner.tsx (ARIA dialog, accept/reject buttons)
  [PASS] src/components/LanguageSelector.tsx (Select with aria-label)
  [PASS] src/pages/Landing.tsx (tier cards role=list, aria-labelledby)
  [PASS] src/pages/Login.tsx
  [PASS] src/pages/Connect.tsx (radio group fieldset, role=alert for errors)
  [PASS] src/pages/PreFlight.tsx (ProgressBar, aria-live)
  [PASS] src/pages/ScanStatus.tsx (polling, aria-live status)
  [PASS] src/pages/Findings.tsx (Table th scope=col, currency aria-label)
  [PASS] src/pages/Checkout.tsx (radio groups, Stripe redirect)
  [PASS] src/pages/Download.tsx (SHA-256 display, SAS URL redirect)
  [PASS] src/pages/BillingPortal.tsx
  [PASS] src/pages/Admin.tsx (dl stats grid with dt/dd)
  [PASS] frontend/.env.example

Epic 5 -- Frontend Spark Restructure (from docs 22-23) -- COMPLETE
  [PASS] src/main.tsx -- updated to use AppShell, removed duplicate FluentProvider
  [PASS] src/app/auth/roles.ts -- ACA_Admin, ACA_Support, ACA_FinOps + ADMIN_ROLES array
  [PASS] src/app/auth/useAuth.ts -- MSAL wrapper (dev bypass via VITE_DEV_AUTH=true)
  [PASS] src/app/auth/RequireAuth.tsx -- redirect to / if not authed
  [PASS] src/app/auth/RequireRole.tsx -- redirect to /app/connect if lacks role
  [PASS] src/app/layout/NavCustomer.tsx + CustomerLayout.tsx
  [PASS] src/app/layout/NavAdmin.tsx + AdminLayout.tsx
  [PASS] src/app/routes/router.tsx -- Spark createBrowserRouter /app/* + /admin/*
  [PASS] src/app/AppShell.tsx -- FluentProvider + skip-link + ConsentBanner + RouterProvider
  [PASS] src/app/api/client.ts -- http<T> with credentials: include, 204 handling
  [PASS] src/app/api/appApi.ts -- getTier1Report, startCollection, getCollectionStatus,
                                   getEntitlement, startCheckout, getBillingPortalUrl
  [PASS] src/app/api/adminApi.ts -- kpis, searchCustomers, grantEntitlement,
                                    lockSubscription, reconcileStripe, getRuns
  [PASS] src/app/types/models.ts -- all Customer + Admin DTOs
  [PASS] src/app/components/Loading.tsx, ErrorState.tsx, MoneyRangeBar.tsx, EffortBadge.tsx
  [PASS] src/app/routes/app/LoginPage.tsx (Entra ID sign-in + dev bypass)
  [PASS] src/app/routes/app/ConnectSubscriptionPage.tsx (Mode A/B/C radio group)
  [PASS] src/app/routes/app/CollectionStatusPage.tsx (polling + exponential backoff)
  [PASS] src/app/routes/app/FindingsTier1Page.tsx (MoneyRangeBar + EffortBadge per finding)
  [PASS] src/app/routes/app/UpgradePage.tsx (Tier 2 vs Tier 3 comparison + Stripe redirect)
  [PASS] src/app/routes/admin/AdminDashboardPage.tsx (KPI dl/dt/dd cards)
  [PASS] src/app/routes/admin/AdminCustomersPage.tsx (search + table + deep-link to runs)
  [PASS] src/app/routes/admin/AdminBillingPage.tsx (Stripe reconcile + confirm modal)
  [PASS] src/app/routes/admin/AdminRunsPage.tsx (type + subscriptionId filters)
  [PASS] src/app/routes/admin/AdminControlsPage.tsx (grant + lock with confirm modal + audit)

Epic 4 -- Admin API Endpoints (from docs 21/23) -- COMPLETE (stubs with audit wiring)
  [PASS] GET  /v1/admin/kpis (AdminKpis DTO)
  [PASS] GET  /v1/admin/customers?query= (AdminCustomerSearchResponse)
  [PASS] POST /v1/admin/entitlements/grant (writes ENTITLEMENT_GRANTED audit event)
  [PASS] POST /v1/admin/subscriptions/:id/lock (writes SUBSCRIPTION_LOCKED audit event)
  [PASS] POST /v1/admin/stripe/reconcile (writes STRIPE_RECONCILE audit event, async job)
  [PASS] GET  /v1/admin/runs?type=&subscriptionId= (AdminRunsResponse)

=============================================================================
IN PROGRESS
=============================================================================

Epic 6 -- Monetization and Billing (Stripe) -- COMPLETE
  [PASS] services/api/app/db/repos/entitlements_repo.py (Cosmos-backed, upsert/get)
  [PASS] services/api/app/db/repos/payments_repo.py (record + list_for_subscription)
  [PASS] services/api/app/db/repos/clients_repo.py (upsert + set_stripe_customer_id)
  [PASS] services/api/app/db/repos/stripe_customer_map_repo.py (PK=/stripeCustomerId)
  [PASS] services/api/app/db/repos/admin_audit_repo.py (append-only audit events)
  [PASS] services/api/app/services/stripe_service.py (checkout, portal, verify_webhook)
  [PASS] services/api/app/services/delivery_service.py (Phase 1 stub, Phase 2 hook)
  [PASS] services/api/app/services/entitlement_service.py (grant/revoke/lifecycle)
  [PASS] app/routers/checkout.py -- full implementation (POST /tier2, /tier3, /webhook,
           GET /portal, GET /entitlements)
  [PASS] admin_audit_repo + entitlements_repo wired into admin.py
  [PASS] entitlements_repo: added is_locked param + set_locked() method
  [ ] PENDING: STRIPE_COUPON_ENABLED field in settings.py (locked decision S2)
  [ ] PENDING: allow_promotion_codes in stripe_service.py checkout session (S2)

GitHub Cloud Agent Framework -- COMPLETE
  [PASS] AGENTS.md -- agent contract: non-negotiable rules, DPDCA loop, spec doc map
  [PASS] .devcontainer/devcontainer.json -- Python 3.12 + Node 20 + Azure CLI + gh CLI
  [PASS] .devcontainer/on-create.sh -- installs all deps + smoke test on Codespaces create
  [PASS] .github/ISSUE_TEMPLATE/agent-task.yml -- structured template for agent-assignable tasks
  [PASS] .github/pull_request_template.md -- PR checklist with test evidence + story link
  [PASS] .github/workflows/ci.yml -- 3 jobs: lint-and-test, frontend-build, agent-preflight

Epic 4 -- Auth rework (multi-tenant) -- NEW WORK
  [ ] services/api/app/routers/auth.py: all 3 endpoints beyond 501 stubs
      connect: MSAL authority=common, store refresh token in KV per scan
      preflight: run 5 probes with delegated token (Mode A) or SP token (Mode B)
      disconnect: revoke token, hard-delete Cosmos tenant data
  [ ] MSAL app registration configured as multi-tenant in Azure portal
  [ ] frontend useAuth.ts: MSAL.js authority=common (any Microsoft tenant)
  [ ] settings.py: add MSAL_AUTHORITY = "https://login.microsoftonline.com/common"

Epic 6 -- Stripe coupon (small -- 2 files)
  [ ] settings.py: STRIPE_COUPON_ENABLED: bool = Field(default=True)
  [ ] stripe_service.py: pass allow_promotion_codes=settings.STRIPE_COUPON_ENABLED

Epic 3 -- Rule unit tests
  [ ] services/analysis/tests/test_rule_01.py through test_rule_12.py (12 files)
  [ ] services/analysis/tests/test_findings_assembler.py
  [ ] Target: 95% line coverage on all rule modules (CI blocks on regression)

Epic 7 -- Delivery Templates
  [ ] 12 Jinja2 template folders in services/delivery/app/templates/{tmpl-id}/
      Each needs: main.bicep (Bicep only -- no main.tf in Phase 1), README.md
      Folders: tmpl-devbox-autostop, tmpl-log-retention, tmpl-defender-plan,
      tmpl-compute-schedule, tmpl-anomaly-alert, tmpl-stale-envs, tmpl-search-sku,
      tmpl-acr-consolidation, tmpl-dns-consolidation, tmpl-savings-plan,
      tmpl-apim-token-budget, tmpl-chargeback-policy

Epic 9 -- i18n/a11y
  [ ] FR translation strings reviewed and proofread (currently machine draft)
  [ ] PT-BR, ES, DE translation stubs -- all 3 complete for Phase 1 (best-effort)
  [ ] Playwright headless test suite -- Tier 1 flow, 95% coverage, all 5 locales
  [ ] axe-core CI gate added to .github/workflows/ci.yml

Infra -- IaC Updates
  [ ] infra/phase1-marco/bootstrap.sh -- NEW FILE from scratch (12-IaCscript.md spec)
      Cover: Cosmos containers, KV secrets, ACA Container App + 3 Jobs, APIM product,
      DO_CONTAINERAPPS and DO_APIM toggle flags
  [ ] infra/phase1-marco/apim-policies/ -- add entitlements caching policy XML
      (cache key: entitlements::{subscriptionId}, TTL: 60s)
  [ ] IaC toggle flags documented: DO_CONTAINERAPPS, DO_APIM, USE_ACR

Docs
  [ ] .env.example: add STRIPE_COUPON_ENABLED, Azure free hostname comments
  [ ] docs/analytics-spec.md -- create from doc 14 (GA4+Clarity formal spec)
  [ ] docs/openapi.admin.yaml -- admin API OpenAPI spec from doc 22

=============================================================================
NOT STARTED
=============================================================================

Milestone M1.0 (env wiring)
  [ ] .env filled from marco-kv secrets
  [ ] Managed Identity permissions tested on local emulator
  [ ] infra/phase1-marco/main.bicep deployed to EsDAICoE-Sandbox successfully
  [ ] OIDC GitHub Actions -> EsDAICoE-Sandbox tested

Milestone M1.1 (first real collection)
  [ ] Collector run against EsDAICoE-Sandbox subscription ID (--subscription-id)
  [ ] Pre-flight PASS confirmed on marco* subscription
  [ ] Cosmos containers populated with real data

Milestone M1.3 (APIM wiring)
  [ ] marco-sandbox-apim product created for ACA
  [ ] JWT validation policy applied
  [ ] Entitlement caching policy (60s) applied
  [ ] Tier enforcement policy applied

Milestone M1.5 (Stripe)
  [ ] Stripe account in test mode (prices created for Tier 2 + Tier 3)
  [ ] Checkout endpoints fully implemented (not stubs)
  [ ] Webhook endpoint fully implemented with signature verification
  [ ] EntitlementService fully implemented (Cosmos-backed, from 09-hardening-MVP.md)
  [ ] StripeCustomerMapRepo implemented (from 10-recurrent-clients.md)
  [ ] Recurring billing lifecycle tested (invoice.paid, subscription.deleted)

Milestone M1.6 (IaC templates)
  [ ] 12 Jinja2 template folders created from 12-IaCscript.md patterns
  [ ] Delivery service tested end-to-end (mock findings -> zip -> SAS URL)

Milestone M2.0 (telemetry)
  [ ] GA4 tag wired via GTM
  [ ] Clarity tag wired via GTM
  [ ] All 16 analytics events firing at correct points

Milestone M3.0 (Phase 2)
  [ ] Private Azure subscription available
  [ ] Terraform applied successfully
  [ ] Custom domain configured

=============================================================================
BLOCKERS AND OPEN QUESTIONS
=============================================================================

B1  Stripe account not created for production (need before M1.5)
    PLAN: Create in test mode first. Real keys at M1.5 launch.
B2  Private Azure subscription for Phase 2 not provisioned (need before M3.0)
    PLAN: Not needed for Phase 1. Defer to Phase 2 scope.
B3  marco-sandbox-apim policy isolation -- need to confirm ACA product can
    coexist with existing EVA POC APIM policies without conflict
    PLAN: Test on a cloned policy, isolate by API path prefix /v1/aca.

RESOLVED (locked 2026-02-27):
  Q1  Domain name -> RESOLVED: Azure free names for Phase 1. Real domain TBD for Phase 2.
  Q2  GitHub org move -> RESOLVED: Stays in eva-foundry (private). No move.
  Q3  Stripe account type -> RESOLVED: Test mode to start. Business account at launch.
  Q4  pt-BR/es translation quality -> RESOLVED: Machine translation Phase 1, pro review Phase 2.
  Q5  FX rate API -> UNRESOLVED: Deferred to Phase 2 (M2.1 scope).
  I2  Auth model -> RESOLVED: Multi-tenant Microsoft Entra, authority=common, any client tenant.
  S2  Stripe pricing -> RESOLVED: Env-var driven, promotional codes enabled, coupon support.
  T1  Template format -> RESOLVED: Bicep only for delivery templates in Phase 1.

=============================================================================
ANALYSIS RULE STATUS
=============================================================================

Rule    Name                         Implementation    Import    Unit Test
------  ---------------------------  ----------------  --------  ---------
R-01    devbox-autostop              [PASS]            [PASS]    [ ]
R-02    log-retention                [PASS]            [PASS]    [ ]
R-03    defender-mismatch            [PASS]            [PASS]    [ ]
R-04    compute-scheduling           [PASS]            [PASS]    [ ]
R-05    anomaly-detection            [PASS]            [PASS]    [ ]
R-06    stale-environments           [PASS]            [PASS]    [ ]
R-07    search-sku-oversize          [PASS]            [PASS]    [ ]
R-08    acr-consolidation            [PASS]            [PASS]    [ ]
R-09    dns-sprawl                   [PASS]            [PASS]    [ ]
R-10    savings-plan-coverage        [PASS]            [PASS]    [ ]
R-11    apim-token-budget            [PASS]            [PASS]    [ ]
R-12    chargeback-gap               [PASS]            [PASS]    [ ]
Totals                               12/12             12/12     0/12

=============================================================================
NEXT SESSION ACTIONS (priority order)
=============================================================================

1. Stripe coupon wiring (settings.py: STRIPE_COUPON_ENABLED; stripe_service.py: allow_promotion_codes)
   -- 2 files, 15 min, no blockers

2. .env.example: add STRIPE_COUPON_ENABLED, Azure free hostname placeholder comments
   -- 1 file, 5 min, no blockers

3. infra/phase1-marco/bootstrap.sh -- new file from 12-IaCscript.md + 13-IAC-more.md spec
   -- 1 new file, ~1h, no blockers

4. 12 Jinja2 delivery templates (services/delivery/app/templates/**/main.bicep + README.md)
   -- 24 files (12 main.bicep + 12 README.md), ~2h, sourced from 12-IaCscript.md patterns

5. 12 rule unit tests (services/analysis/tests/test_rule_*.py) + findings_assembler test
   -- 13 new test files, ~2h, target 95% coverage, hardcoded JSON fixtures, no Cosmos calls

6. auth.py multi-tenant MSAL rework (connect/preflight/disconnect beyond 501 stubs)
   authority=common, refresh token in KV per scan, Mode A/B/C all implemented
   -- 1 file + dependencies, ~3h

7. PT-BR, ES, DE translation stubs (best-effort for Phase 1)
   -- 3 new translation JSON files (~1h)

8. Playwright a11y CI setup (.github/workflows + playwright.config.ts + axe-core)
   -- 3 files, ~45 min

9. Commit all + push + update Veritas MTI

=============================================================================
DPDCA CLOUD AGENT STATUS (2026-02-27)
=============================================================================

The DPDCA cloud agent pipeline is now wired end-to-end:

.github/workflows/dpdca-agent.yml (344 lines)
  Trigger: issues labeled "agent-task" OR workflow_dispatch
  D1: checkout + parse issue (Story ID, WBS, FP, Inputs, Outputs, Acceptance)
      loads PLAN.md + copilot-instructions into agent-context.txt
  P:  Python plan step calls gpt-4o-mini (GitHub Models API) with full context
      writes agent-plan.md to artifacts
  D2: creates branch agent/ACA-NN-NNN-TIMESTAMP
      writes .eva/evidence/ACA-NN-NNN-DATE.json receipt
  C:  ruff check services/ + pytest services/ --co -q
  A:  commit with Story ID on subject line (Veritas evidence mining)
      runs veritas audit, enforces no-deploy NOT in trust.json actions
      pushes branch, opens PR, posts confirmation comment on issue

.github/ISSUE_TEMPLATE/agent-task.yml (197 lines)
  Fields: Story ID (ACA-NN-NNN), WBS ID (N.N.N), Epic dropdown (14 epics),
          FP Size (XS/S/M/L/XL), Sprint, User Story, Inputs, Outputs,
          Acceptance Criteria, Spec References, Files to modify,
          Constraints, Depends On, Agent Pre-flight Checklist (7 items)

To trigger a sprint task:
  1. Create Issue with template "DPDCA Sprint Backlog Item"
  2. Fill Story ID + all fields
  3. Add label "agent-task"
  4. Workflow fires automatically; PR created within ~3 min

=============================================================================
LAST SESSION (2026-02-27 -- WBS/FP/velocity/Veritas MTI=70/DPDCA/Epic 13+14)
=============================================================================

Completed this session:
- veritas-plan.json: rewritten with numeric IDs (ACA-NN-NNN), all 22 stories done:true
- All 8 source files: EVA-STORY tags updated from alpha to numeric format
  (auth.py, scans.py, findings.py, checkout.py, admin.py, health.py, main.py, main.bicep)
- Veritas MTI: 20 -> 70 (no-deploy cleared, sparkline delta +50)
- .github/workflows/dpdca-agent.yml: CREATED (344 lines, full DPDCA pipeline)
- .github/ISSUE_TEMPLATE/agent-task.yml: REWRITTEN (197 lines, DPDCA template)
- PLAN.md -> v0.5.0: WBS overview table, FP index table, velocity tracking,
  Epic 13 (Azure Best Practices -- 11 stories, 55 FP), Epic 14 (DPDCA -- 10 stories, 36 FP)
- STATUS.md -> v1.0.0 (this update)
- Data model: 12 decisions + 29 stories + 4 personas seeded (total=102)

Full scope freeze for Phase 1 implementation sprint:

=============================================================================
STORY STATUS (veritas consistency block -- generated 2026-02-27)
=============================================================================
# Feature: ACA-01
STORY ACA-01-001: Done
STORY ACA-01-002: Done
STORY ACA-01-003: Done
STORY ACA-01-004: Done
STORY ACA-01-005: Done
STORY ACA-01-006: Done
STORY ACA-01-007: Done
STORY ACA-01-008: Done
STORY ACA-01-009: Done
STORY ACA-01-010: Done
STORY ACA-01-011: Done
STORY ACA-01-012: Done
STORY ACA-01-013: Done
STORY ACA-01-014: Done
STORY ACA-01-015: Done
STORY ACA-01-016: Done
STORY ACA-01-017: Done
STORY ACA-01-018: Done
STORY ACA-01-019: Done
STORY ACA-01-020: Done
STORY ACA-01-021: Done

# Feature: ACA-02
STORY ACA-02-001: Done
STORY ACA-02-002: Done
STORY ACA-02-003: Done
STORY ACA-02-004: Done
STORY ACA-02-005: Done
STORY ACA-02-006: Done
STORY ACA-02-007: Done
STORY ACA-02-008: Done
STORY ACA-02-009: Done
STORY ACA-02-010: Done
STORY ACA-02-011: Done
STORY ACA-02-012: Done
STORY ACA-02-013: Done
STORY ACA-02-014: Done
STORY ACA-02-015: Done
STORY ACA-02-016: Done

# Feature: ACA-03
STORY ACA-03-001: Not Started
STORY ACA-03-002: Not Started
STORY ACA-03-003: Not Started
STORY ACA-03-004: Not Started
STORY ACA-03-005: Not Started
STORY ACA-03-006: Not Started
STORY ACA-03-007: Not Started
STORY ACA-03-008: Not Started
STORY ACA-03-009: Not Started
STORY ACA-03-010: Not Started
STORY ACA-03-011: Not Started
STORY ACA-03-012: Not Started
STORY ACA-03-013: Not Started
STORY ACA-03-014: Not Started
STORY ACA-03-015: Not Started
STORY ACA-03-016: Not Started
STORY ACA-03-017: Not Started
STORY ACA-03-018: Not Started
STORY ACA-03-019: Not Started
STORY ACA-03-020: Not Started
STORY ACA-03-021: Not Started
STORY ACA-03-022: Not Started
STORY ACA-03-023: Not Started
STORY ACA-03-024: Not Started
STORY ACA-03-025: Not Started
STORY ACA-03-026: Not Started
STORY ACA-03-027: Not Started
STORY ACA-03-028: Not Started
STORY ACA-03-029: Not Started
STORY ACA-03-030: Not Started
STORY ACA-03-031: Not Started
STORY ACA-03-032: Not Started
STORY ACA-03-033: Not Started

# Feature: ACA-04
STORY ACA-04-001: Not Started
STORY ACA-04-002: Not Started
STORY ACA-04-003: Not Started
STORY ACA-04-004: Not Started
STORY ACA-04-005: Not Started
STORY ACA-04-006: Not Started
STORY ACA-04-007: Not Started
STORY ACA-04-008: Not Started
STORY ACA-04-009: Not Started
STORY ACA-04-010: Not Started
STORY ACA-04-011: Not Started
STORY ACA-04-012: Not Started
STORY ACA-04-013: Not Started
STORY ACA-04-014: Not Started
STORY ACA-04-015: Not Started
STORY ACA-04-016: Not Started
STORY ACA-04-017: Not Started
STORY ACA-04-018: Not Started
STORY ACA-04-019: Not Started
STORY ACA-04-020: Not Started
STORY ACA-04-021: Not Started
STORY ACA-04-022: Not Started
STORY ACA-04-023: Not Started
STORY ACA-04-024: Not Started
STORY ACA-04-025: Not Started
STORY ACA-04-026: Not Started
STORY ACA-04-027: Not Started

# Feature: ACA-05
STORY ACA-05-001: Not Started
STORY ACA-05-002: Not Started
STORY ACA-05-003: Not Started
STORY ACA-05-004: Not Started
STORY ACA-05-005: Not Started
STORY ACA-05-006: Not Started
STORY ACA-05-007: Not Started
STORY ACA-05-008: Not Started
STORY ACA-05-009: Not Started
STORY ACA-05-010: Not Started
STORY ACA-05-011: Not Started
STORY ACA-05-012: Not Started
STORY ACA-05-013: Not Started
STORY ACA-05-014: Not Started
STORY ACA-05-015: Not Started
STORY ACA-05-016: Not Started
STORY ACA-05-017: Not Started
STORY ACA-05-018: Not Started
STORY ACA-05-019: Not Started
STORY ACA-05-020: Not Started
STORY ACA-05-021: Not Started
STORY ACA-05-022: Not Started
STORY ACA-05-023: Not Started
STORY ACA-05-024: Not Started
STORY ACA-05-025: Not Started
STORY ACA-05-026: Not Started
STORY ACA-05-027: Not Started
STORY ACA-05-028: Not Started
STORY ACA-05-029: Not Started
STORY ACA-05-030: Not Started
STORY ACA-05-031: Not Started
STORY ACA-05-032: Not Started
STORY ACA-05-033: Not Started
STORY ACA-05-034: Not Started
STORY ACA-05-035: Not Started
STORY ACA-05-036: Not Started
STORY ACA-05-037: Not Started
STORY ACA-05-038: Not Started
STORY ACA-05-039: Not Started
STORY ACA-05-040: Not Started
STORY ACA-05-041: Not Started
STORY ACA-05-042: Not Started

# Feature: ACA-06
STORY ACA-06-001: Done
STORY ACA-06-002: Done
STORY ACA-06-003: Done
STORY ACA-06-004: Done
STORY ACA-06-005: Done
STORY ACA-06-006: Done
STORY ACA-06-007: Done
STORY ACA-06-008: Done
STORY ACA-06-009: Done
STORY ACA-06-010: Done
STORY ACA-06-011: Done
STORY ACA-06-012: Done
STORY ACA-06-013: Done
STORY ACA-06-014: Done
STORY ACA-06-015: Done
STORY ACA-06-016: Done
STORY ACA-06-017: Done

# Feature: ACA-07
STORY ACA-07-001: Not Started
STORY ACA-07-002: Not Started
STORY ACA-07-003: Not Started
STORY ACA-07-004: Not Started
STORY ACA-07-005: Not Started
STORY ACA-07-006: Not Started
STORY ACA-07-007: Not Started
STORY ACA-07-008: Not Started
STORY ACA-07-009: Not Started

# Feature: ACA-08
STORY ACA-08-001: Not Started
STORY ACA-08-002: Not Started
STORY ACA-08-003: Not Started
STORY ACA-08-004: Not Started
STORY ACA-08-005: Not Started
STORY ACA-08-006: Not Started
STORY ACA-08-007: Not Started
STORY ACA-08-008: Not Started
STORY ACA-08-009: Not Started
STORY ACA-08-010: Not Started
STORY ACA-08-011: Not Started
STORY ACA-08-012: Not Started
STORY ACA-08-013: Not Started
STORY ACA-08-014: Not Started

# Feature: ACA-09
STORY ACA-09-001: Not Started
STORY ACA-09-002: Not Started
STORY ACA-09-003: Not Started
STORY ACA-09-004: Not Started
STORY ACA-09-005: Not Started
STORY ACA-09-006: Not Started
STORY ACA-09-007: Not Started
STORY ACA-09-008: Not Started
STORY ACA-09-009: Not Started
STORY ACA-09-010: Not Started
STORY ACA-09-011: Not Started
STORY ACA-09-012: Not Started
STORY ACA-09-013: Not Started
STORY ACA-09-014: Not Started
STORY ACA-09-015: Not Started
STORY ACA-09-016: Not Started
STORY ACA-09-017: Not Started
STORY ACA-09-018: Not Started

# Feature: ACA-10
STORY ACA-10-001: Not Started
STORY ACA-10-002: Not Started
STORY ACA-10-003: Not Started
STORY ACA-10-004: Not Started
STORY ACA-10-005: Not Started
STORY ACA-10-006: Not Started
STORY ACA-10-007: Not Started
STORY ACA-10-008: Not Started
STORY ACA-10-009: Not Started
STORY ACA-10-010: Not Started
STORY ACA-10-011: Not Started
STORY ACA-10-012: Not Started
STORY ACA-10-013: Not Started
STORY ACA-10-014: Not Started
STORY ACA-10-015: Not Started

# Feature: ACA-11
STORY ACA-11-001: Not Started
STORY ACA-11-002: Not Started
STORY ACA-11-003: Not Started
STORY ACA-11-004: Not Started
STORY ACA-11-005: Not Started
STORY ACA-11-006: Not Started
STORY ACA-11-007: Not Started
STORY ACA-11-008: Not Started
STORY ACA-11-009: Not Started

# Feature: ACA-12
STORY ACA-12-001: Not Started
STORY ACA-12-002: Not Started
STORY ACA-12-003: Not Started
STORY ACA-12-004: Not Started
STORY ACA-12-005: Not Started
STORY ACA-12-006: Not Started
STORY ACA-12-007: Not Started
STORY ACA-12-008: Not Started

# Feature: ACA-13
STORY ACA-13-009: Not Started
STORY ACA-13-010: Not Started
STORY ACA-13-011: Not Started
STORY ACA-13-012: Not Started
STORY ACA-13-013: Not Started
STORY ACA-13-014: Not Started
STORY ACA-13-015: Not Started
STORY ACA-13-016: Not Started
STORY ACA-13-017: Not Started
STORY ACA-13-018: Not Started
STORY ACA-13-019: Not Started

# Feature: ACA-14
STORY ACA-14-001: Done
STORY ACA-14-002: Done
STORY ACA-14-003: Done
STORY ACA-14-004: Done
STORY ACA-14-005: Done
STORY ACA-14-006: Done
STORY ACA-14-007: Done
STORY ACA-14-008: Not Started
STORY ACA-14-009: Not Started
STORY ACA-14-010: Not Started

