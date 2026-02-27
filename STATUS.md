ACA -- Azure Cost Advisor -- STATUS
====================================

Version: 0.7.0
Updated: 2026-02-26 (updated: Epic 6 billing layer -- repos, services, full checkout.py; Veritas MTI 0->50)
Phase: Phase 1 -- Core Services Bootstrap
Active Epic: Epic 6 (Billing/Stripe -- repos+services done, checkout full), Epic 7 (Delivery templates), Epic 9 (i18n/a11y completion)

=============================================================================
CURRENT STATE (2026-02-26)
=============================================================================

All four backend services are bootstrapped and import-verified. Frontend Spark
restructure is complete (Epic 5 DONE). Billing layer (Epic 6) is substantially
complete: all 5 Cosmos repos, 3 service classes, and full checkout.py implemented
with Stripe webhook lifecycle (checkout, invoice.paid, subscription updated/deleted).
Veritas MTI raised from 0 to 50 (22/22 stories tagged, 0 gaps).
Data model server: http://localhost:8011 (store=memory, total=57).
ADO project: dev.azure.com/marcopresta/51-aca (Epic 2730, 12 Features, 16 PBIs).

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

Epic 6 -- Billing (Stripe)
  [PASS] services/api/app/db/repos/entitlements_repo.py (Cosmos-backed, upsert/get)
  [PASS] services/api/app/db/repos/payments_repo.py (record + list_for_subscription)
  [PASS] services/api/app/db/repos/clients_repo.py (upsert + set_stripe_customer_id)
  [PASS] services/api/app/db/repos/stripe_customer_map_repo.py (PK=/stripeCustomerId)
  [PASS] services/api/app/db/repos/admin_audit_repo.py (append-only audit events)
  [PASS] services/api/app/services/stripe_service.py (checkout, portal, verify_webhook)
  [PASS] services/api/app/services/delivery_service.py (Phase 1 stub, Phase 2 hook)
  [PASS] services/api/app/services/entitlement_service.py (grant/revoke/lifecycle)
  [PASS] app/routers/checkout.py -- full implementation (was 501 stubs):
           POST /tier2, /tier3 (Stripe checkout session creation)
           POST /webhook (sig verify + checkout.session.completed + invoice lifecycle)
           GET  /portal (billing portal via stripeCustomerId from clients repo)
           GET  /entitlements (Entitlement dataclass + access flags)
  [PASS] settings.py updated: PUBLIC_APP_URL, PUBLIC_API_URL, STRIPE_ENABLE_SUBSCRIPTIONS,
           COSMOS_CONTAINER_* names for 5 new containers
  [PASS] cosmos.py CONTAINERS updated: +entitlements, +payments, +stripe_customer_map,
           +admin_audit_events; clients PK fixed to /subscriptionId
  [PASS] Import check: all 9 new modules import clean (stripe 14.4.0)
  [ ] admin_audit_repo wired into admin.py grant/lock/reconcile endpoints

Epic 7 -- Delivery Templates
  [ ] 12 Jinja2 template folders in services/delivery/app/templates/{tmpl-id}/
      Each needs: main.bicep, main.tf, README.md

Epic 9 -- i18n/a11y
  [ ] FR translation strings reviewed and proofread (currently machine draft)
  [ ] PT-BR, ES, DE translation stubs (Phase 2 gating flag exists)
  [ ] axe-core CI gate added to .github/workflows/ci.yml

Infra -- IaC Updates (from docs 13/20)
  [ ] infra/phase1-marco/bootstrap.sh -- update with Container Apps Jobs
      (CA_COLLECTOR_JOB, CA_ANALYSIS_JOB, CA_DELIVERY_JOB)
  [ ] infra/phase1-marco/apim-policies/ -- add entitlements caching policy XML
      (cache key: entitlements::{subscriptionId}, TTL: 60s)
  [ ] Update Cosmos container create calls to add admin_audit_events container
      (PK /subscriptionId, RU 400)
  [ ] IaC toggle flags documented: DO_CONTAINERAPPS, DO_APIM, USE_ACR

Docs
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
B2  Private Azure subscription for Phase 2 not provisioned (need before M3.0)
B3  marco-sandbox-apim policy isolation -- need to confirm ACA product can
    coexist with existing EVA POC APIM policies without conflict

Q1  Which domain name? app.aca.example.com is a placeholder.
    Real domain needs DNS delegation and TLS before Phase 2.
Q2  GitHub org: will 51-ACA stay in eva-foundry or move to a commercial org?
Q3  Stripe account -- personal or business? Business account required for
    production payments in Canada.
Q4  Will pt-BR and es translations be machine-translated or professionally reviewed?
Q5  What FX rate API will be used for currency display? (Open Exchange Rates, fixer.io?)

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

1. Frontend Spark restructure -- create auth layer, layouts, router.tsx, API clients
2. Create 5 admin pages (AdminDashboardPage, AdminCustomersPage, AdminBillingPage,
   AdminRunsPage, AdminControlsPage)
3. Add 6 admin API endpoints to admin.py
4. Create admin_audit_repo.py (Cosmos write for every admin action)
5. Wire .env from marco-kv secrets + run first collector run
6. Implement Stripe checkout + webhook fully (from docs 16/17/18)
7. Add 12 Jinja2 IaC templates
8. Create docs/analytics-spec.md and docs/openapi.admin.yaml
9. Update IaC bootstrap.sh with Container Apps Jobs + admin_audit_events container
10. Add axe-core to ci.yml

=============================================================================
LAST SESSION (2026-02-26 continuation -- docs 13-23 onboarded)
=============================================================================

Completed this session:
- Read all 11 previously-unread source docs (13-23)
- Identified 4 genuinely new docs (21, 22, 23, 13/20 IaC update)
  - 14/15/16/17/18/19 are deeper/duplicate versions of 06/07/08/09/10/11
- Updated README.md with: admin_audit_events container, Spark routing architecture,
  admin role model (ACA_Admin/ACA_Support/ACA_FinOps), API client mapping,
  project files map entries 13-23
- Updated STATUS.md (this file) with full Spark frontend task list
- Updated PLAN.md with Epic 5 Spark stories + admin API stories
- Updated data-model: added admin_audit_events to containers.json,
  added 6 admin endpoints + 3 customer endpoint corrections to endpoints.json,
  updated screens.json to /app/* + /admin/* Spark routing,
  added ACA_Admin/ACA_Support/ACA_FinOps roles layer entry
