ACA -- Azure Cost Advisor -- STATUS
====================================

Version: 0.9.0
Updated: 2026-02-27 (plan refinement: multi-tenant auth, coupon/promo codes,
         Azure free hostnames, Bicep-only templates, Playwright a11y, all 5 locales Phase 1,
         bootstrap.sh new, 12 rule unit tests target, all Q&A decisions locked)
Phase: Phase 1 -- Core Services Bootstrap
Active Epic: Epic 4 (auth rework), Epic 7 (Delivery templates), Epic 9 (i18n/a11y completion)

=============================================================================
CURRENT STATE (2026-02-26)
=============================================================================

All four backend services are bootstrapped and import-verified. Frontend Spark
restructure is complete (Epic 5 DONE). Billing layer (Epic 6) is complete.
GitHub cloud agent framework is in place (AGENTS.md, devcontainer, ci.yml multi-job).
All pre-flight planning Q&A decisions are LOCKED (see DECISIONS LOCKED section below).
Veritas MTI: 50. Data model: http://localhost:8011 (store=memory, total=57).
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
LAST SESSION (2026-02-27 -- plan refinement, all Q&A decisions locked)
=============================================================================

Completed this session:
- Read all governance docs (README.md, PLAN.md, STATUS.md, ACCEPTANCE.md)
- Conducted pre-flight Q&A (12 questions, all answered)
- Locked all planning decisions (see DECISIONS LOCKED section above)
- README.md -> v0.5.0: multi-tenant auth clarification, Azure free hostnames,
  Stripe coupon documentation, i18n Phase 1 all-5-locales note
- PLAN.md -> v0.4.0: new Feature 1.5 (Azure free URLs), Feature 3.4 (unit tests),
  multi-tenant auth Feature 4.1 (7 stories), Stripe coupon Feature 6.1 (8 stories),
  Bicep-only Feature 7.1, all-5-locales Phase 1 Story 9.1.8, Playwright Story 9.2.11
- STATUS.md -> v0.9.0 (this update)

Full scope freeze for Phase 1 implementation sprint:
