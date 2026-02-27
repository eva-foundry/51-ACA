ACA -- Azure Cost Advisor -- PLAN
=================================

Version: 0.3.0
Updated: 2026-02-26
Phase: Phase 1 active

This plan is the Work Breakdown Structure (WBS) for ACA.
Each Epic maps to one or more data-model layers.
Features map to user stories seeded into the data-model stories layer.
All milestone dates are relative to 2026-02-26 (project bootstrap complete).

=============================================================================
WBS OVERVIEW
=============================================================================

Epic 1  -- Foundation and Infrastructure          (M1.0)   Weeks 1-2
Epic 2  -- Data Collection Pipeline               (M1.1)   Weeks 2-3
Epic 3  -- Analysis Engine + Rules                (M1.2)   Weeks 2-3
Epic 4  -- API and Auth Layer                     (M1.3)   Weeks 2-3
Epic 5  -- Frontend Core (5 pages, Tier 1)        (M1.4)   Weeks 3-4
Epic 6  -- Monetization and Billing (Stripe)      (M1.5)   Weeks 3-4
Epic 7  -- Delivery Packager (Tier 3)             (M1.6)   Week 4
Epic 8  -- Observability and Telemetry            (M2.0)   Week 4
Epic 9  -- i18n and a11y                          (M2.1)   Weeks 4-5
Epic 10 -- Commercial Hardening                   (M2.2)   Weeks 5-6
Epic 11 -- Phase 2 Infrastructure                 (M3.0)   Weeks 7-9
Epic 12 -- Data Model Support (app runtime)       (ongoing)

=============================================================================
EPIC 1 -- FOUNDATION AND INFRASTRUCTURE (M1.0)
=============================================================================

Goal: All four services boot cleanly. Local dev stack works. Phase 1 infra wired.

Feature 1.1 -- Local dev environment
  Story 1.1.1  As a developer I can run `docker-compose up` and all services start
  Story 1.1.2  As a developer I can run `pytest services/ -x -q` and all tests pass
  Story 1.1.3  As a developer I can hit http://localhost:8080/health and get status=ok
  Story 1.1.4  As a developer I can run the data-model on port 8011 (start.ps1)
  Story 1.1.5  As a developer I can use the .env.example as a complete checklist

Feature 1.2 -- CI pipeline
  Story 1.2.1  As a developer, every PR triggers ruff lint. Zero lint errors = green.
  Story 1.2.2  As a developer, every PR triggers mypy type check. No unresolved types.
  Story 1.2.3  As a developer, every PR triggers pytest. No test failures = merge allowed.
  Story 1.2.4  As a developer, main branch push triggers axe-core a11y check on frontend.

Feature 1.3 -- Phase 1 marco* infra wiring
  Story 1.3.1  As an operator I can run infra/phase1-marco/main.bicep and get 7 Cosmos containers
  Story 1.3.2  As an operator all secrets are in marcosandkv20260203 (no .env in production)
  Story 1.3.3  As an operator the API Container App has managed identity approved on KV
  Story 1.3.4  As an operator the collector job has managed identity with Cosmos read/write
  Story 1.3.5  As an operator OIDC is configured on the GitHub Actions workflow for EsDAICoE-Sandbox

Feature 1.4 -- Container build + push
  Story 1.4.1  As a developer all 4 Dockerfiles build without error on ubuntu-latest
  Story 1.4.2  As an operator deploy-phase1.yml pushes 4 images to marcosandacr20260203
  Story 1.4.3  As an operator collector-schedule.yml triggers nightly at 02:00 UTC

=============================================================================
EPIC 2 -- DATA COLLECTION PIPELINE (M1.1)
=============================================================================

Goal: Collector job runs against a real Azure subscription and saves data to Cosmos.

Feature 2.1 -- Pre-flight validation
  Story 2.1.1  As a client using Mode A (delegated) I see a PASS/FAIL/WARN status
               for each of the 5 capability probes before collection starts
  Story 2.1.2  As a client with missing Cost Management Reader role I see a clear
               error message naming the missing role and linking to the access guide
  Story 2.1.3  As a client with PASS_WITH_WARNINGS I can still proceed with collection
               and the warnings are recorded in the scan record
  Story 2.1.4  As an operator I can pass --preflight-only to the collector to validate
               without collecting

Feature 2.2 -- Resource inventory
  Story 2.2.1  As the system I collect all Azure resources via Resource Graph in < 60s
               for a subscription with up to 500 resources
  Story 2.2.2  As the system I save inventory to Cosmos with partition_key=subscriptionId
  Story 2.2.3  As the system I capture: resource type, name, SKU, region, resource group, tags

Feature 2.3 -- Cost data
  Story 2.3.1  As the system I collect 91 days of daily cost rows via Cost Management Query API
  Story 2.3.2  As the system I capture: date, MeterCategory, MeterName, resourceGroup,
               resourceId (hashed), PreTaxCost in subscription currency
  Story 2.3.3  As the system I handle rate limiting (429) with exponential backoff + retry

Feature 2.4 -- Advisor, Policy, Network
  Story 2.4.1  As the system I collect all Advisor recommendations across all categories
  Story 2.4.2  As the system I collect Policy compliance state (compliant / non-compliant counts)
  Story 2.4.3  As the system I collect network signals: NSG rule counts, private DNS zones,
               public IP count, VNet peering map

Feature 2.5 -- Collection lifecycle
  Story 2.5.1  As the system I update scan status in Cosmos: queued -> running -> succeeded/failed
  Story 2.5.2  As the system I write stats to the scan record (inventoryCount, costRows, advisorRecs)
  Story 2.5.3  As the API I expose GET /v1/scans/:scanId so the frontend can poll status

=============================================================================
EPIC 3 -- ANALYSIS ENGINE AND RULES (M1.2)
=============================================================================

Goal: Analysis engine runs all 12 rules and persists tiered findings to Cosmos.

Feature 3.1 -- Rule engine
  Story 3.1.1  As the system I load all 12 rules from ALL_RULES and run each in sequence
  Story 3.1.2  As the system I handle a rule failure in isolation (one rule crash does not
               stop the engine; the error is logged and that rule is skipped)
  Story 3.1.3  As the system I persist each Finding to Cosmos with full schema:
               id, category, title, estimated_saving_low, estimated_saving_high,
               effort_class, risk_class, heuristic_source, narrative,
               deliverable_template_id, evidence_refs
  Story 3.1.4  As the system I update AnalysisRun status: queued -> running -> succeeded/failed
  Story 3.1.5  As the system I write findingsSummary to the analysis run record
               (findingCount, totalSavingLow, totalSavingHigh, categories[])

Feature 3.2 -- Tier gating
  Story 3.2.1  As a Tier 1 client calling GET /v1/findings/:scanId I receive findings
               with category, title, estimated_saving_low, estimated_saving_high only
  Story 3.2.2  As a Tier 1 client I do not receive narrative or deliverable_template_id
               even if they are stored in Cosmos
  Story 3.2.3  As a Tier 2 client I receive the full finding including narrative and
               evidence_refs but not deliverable_template_id
  Story 3.2.4  As a Tier 3 client I receive the full finding including deliverable_template_id
  Story 3.2.5  As the red-team agent I can assert that Tier 1 tokens never leak
               narrative or deliverable_template_id fields (redteam-agent.yaml gate)

Feature 3.3 -- Individual rules (one story per rule)
  Story 3.3.1  R-01 Dev Box auto-stop: returns finding when annual Dev Box cost > $1,000
  Story 3.3.2  R-02 Log retention: returns finding when annual LA cost > $500 in non-prod
  Story 3.3.3  R-03 Defender mismatch: returns finding when annual Defender cost > $2,000
  Story 3.3.4  R-04 Compute scheduling: returns finding when annual schedulable compute > $5,000
  Story 3.3.5  R-05 Anomaly detection: returns finding for each category with z-score > 3.0
  Story 3.3.6  R-06 Stale environments: returns finding when >= 3 App Service sites exist
  Story 3.3.7  R-07 Search SKU oversize: returns finding when annual Search cost > $2,000
  Story 3.3.8  R-08 ACR consolidation: returns finding when >= 3 registries exist
  Story 3.3.9  R-09 DNS sprawl: returns finding when annual DNS cost > $1,000
  Story 3.3.10 R-10 Savings plan: returns finding when annual total compute > $20,000
  Story 3.3.11 R-11 APIM token budget: returns finding when APIM + OpenAI both present
  Story 3.3.12 R-12 Chargeback gap: returns finding when total period cost > $5,000

=============================================================================
EPIC 4 -- API AND AUTH LAYER (M1.3)
=============================================================================

Goal: All 25+ API endpoints implemented, JWT-validated, APIM-proxied.

Feature 4.1 -- Authentication
  Story 4.1.1  As a client I can sign in via Entra ID OIDC and receive a JWT
  Story 4.1.2  As the API I validate the JWT on every authenticated endpoint
  Story 4.1.3  As the API I extract subscriptionId and tier from the JWT claims
               or from the Cosmos clients container
  Story 4.1.4  As a client I can connect my Azure subscription (POST /v1/auth/connect)
               in Mode A (delegated), Mode B (service principal), or Mode C (Lighthouse)
  Story 4.1.5  As a client I can disconnect (POST /v1/auth/disconnect) and all access
               tokens are invalidated and removed from Key Vault

Feature 4.2 -- Core API endpoints (Spark paths from docs 22-23)
  Story 4.2.1  POST /v1/auth/connect         -- Connect Azure subscription
  Story 4.2.2  POST /v1/auth/preflight       -- Run pre-flight probes
  Story 4.2.3  POST /v1/auth/disconnect      -- Disconnect subscription
  Story 4.2.4  POST /v1/collect/start        -- Trigger collector job (was /v1/scans)
  Story 4.2.5  GET  /v1/collect/status       -- Poll collection progress (was /v1/scans/:scanId)
  Story 4.2.6  GET  /v1/reports/tier1        -- Tier 1 findings report (was /v1/findings/:scanId)
  Story 4.2.7  POST /v1/billing/checkout     -- Stripe checkout (tier2 or tier3 in body)
  Story 4.2.8  GET  /v1/billing/portal       -- Stripe billing portal redirect URL
  Story 4.2.9  POST /v1/webhooks/stripe      -- Stripe event handler
  Story 4.2.10 GET  /v1/entitlements         -- Current tier for subscriptionId
  Story 4.2.11 GET  /health                  -- Health check (unauthenticated)

Feature 4.3 -- APIM policies
  Story 4.3.1  As the gateway I validate JWT signature on all /v1/* routes
  Story 4.3.2  As the gateway I cache /v1/entitlements response for 60s per subscriptionId
               using cache key entitlements::{subscriptionId} (from doc 19)
  Story 4.3.3  As the gateway I return 403 with TIER_REQUIRED error when a Tier 1
               client calls a Tier 2+ endpoint
  Story 4.3.4  As the gateway I enforce subscription key throttling (100 req/min default)
  Story 4.3.5  As the gateway I forward X-Subscription-Id header to the API on all calls

Feature 4.4 -- Admin API endpoints (NEW from docs 21/23)
  Story 4.4.1  GET  /v1/admin/kpis
               Returns { utc, mrrCad, activeSubscriptions, scansLast24h,
               analysesLast24h, deliveriesLast24h, failureRatePctLast24h }
               Requires role: ACA_Admin | ACA_Support | ACA_FinOps
  Story 4.4.2  GET  /v1/admin/customers?query=
               Searches by subscriptionId, stripeCustomerId; returns list of
               AdminCustomerRow (subscriptionId, stripeCustomerId, tier,
               paymentStatus, lastActivityUtc, isLocked)
               Requires role: ACA_Admin | ACA_Support | ACA_FinOps
  Story 4.4.3  POST /v1/admin/entitlements/grant
               Body: { subscriptionId, tier, days, reason }
               Writes entitlement to Cosmos + writes admin_audit_events record
               Requires role: ACA_Admin | ACA_Support
  Story 4.4.4  POST /v1/admin/subscriptions/:subscriptionId/lock
               Body: { reason }
               Marks subscription locked in clients container
               Writes admin_audit_events record
               Requires role: ACA_Admin | ACA_Support
  Story 4.4.5  POST /v1/admin/stripe/reconcile
               Enqueues reconcile job: fetches all active Stripe subscriptions
               and repairs missing entitlements in Cosmos
               Returns { jobId, acceptedUtc }
               Requires role: ACA_Admin
  Story 4.4.6  GET  /v1/admin/runs?type=scan|analysis|delivery
               Lists job run records (scan/analysis/delivery) from Cosmos
               Supports filter by subscriptionId and type
               Requires role: ACA_Admin | ACA_Support | ACA_FinOps

=============================================================================
EPIC 5 -- FRONTEND SPARK ARCHITECTURE (M1.4)
=============================================================================

Goal: Spark /app/* + /admin/* routing live. RequireAuth + RequireRole guards.
      All 5 customer pages + 5 admin pages functional. Tier 1 flow end-to-end.

Feature 5.1 -- Auth layer (NEW from docs 22-23)
  Story 5.1.1  roles.ts defines ACA_Admin, ACA_Support, ACA_FinOps role constants
  Story 5.1.2  useAuth.ts wraps MSAL PublicClientApplication; exposes user, roles,
               isAuthenticated, login(), logout()
               DEV bypass mode: when VITE_DEV_AUTH=true, simulates signed-in user
               with configurable roles + subscriptionId (no MSAL call needed)
  Story 5.1.3  RequireAuth.tsx: if !isAuthenticated redirect to /
  Story 5.1.4  RequireRole.tsx: if user lacks anyOf roles, redirect to /app/connect
               Destructive action gating: confirmation modal before grant/lock/reconcile
  Story 5.1.5  All admin routes require RequireAuth + RequireRole (ACA_Admin|Support|FinOps)

Feature 5.2 -- Layout layer (NEW from docs 22-23)
  Story 5.2.1  CustomerLayout.tsx: top nav with logo, LanguageSelector, user menu
               Wraps all /app/* routes via Outlet
  Story 5.2.2  AdminLayout.tsx: top nav + left sidebar with admin nav items
               Wraps all /admin/* routes via Outlet
  Story 5.2.3  NavCustomer.tsx: links to /app/connect, /app/status, /app/findings
  Story 5.2.4  NavAdmin.tsx: links to /admin/dashboard, /admin/customers,
               /admin/billing, /admin/runs, /admin/controls
  Story 5.2.5  AppShell.tsx: root component with FluentProvider + ConsentBanner +
               RouterProvider (replaces App.tsx BrowserRouter pattern)

Feature 5.3 -- Router (Spark createBrowserRouter pattern)
  Story 5.3.1  router.tsx uses createBrowserRouter (not BrowserRouter + <Routes>)
  Story 5.3.2  Route / -> LoginPage (no auth required)
  Story 5.3.3  Routes /app/* -> RequireAuth -> CustomerLayout -> Outlet
  Story 5.3.4  Routes /admin/* -> RequireAuth -> RequireRole -> AdminLayout -> Outlet
  Story 5.3.5  Code-split: all page components lazy-loaded with React.lazy

Feature 5.4 -- Customer pages (/app/*)
  Story 5.4.1  LoginPage (/) -- Entra ID login CTA + dev bypass link
  Story 5.4.2  ConnectSubscriptionPage (/app/connect) -- Mode A/B/C radio group;
               calls POST /v1/auth/connect then POST /v1/collect/start;
               stores subscriptionId in sessionStorage after connect
  Story 5.4.3  CollectionStatusPage (/app/status/:subscriptionId) -- polls
               GET /v1/collect/status with backoff; shows named steps + progress bar;
               links to /app/findings/:subscriptionId when collection complete
  Story 5.4.4  FindingsTier1Page (/app/findings/:subscriptionId) -- renders Tier 1
               report from GET /v1/reports/tier1; shows MoneyRangeBar + EffortBadge
               per finding; blurred upgrade CTA rows for Tier 2+ findings
  Story 5.4.5  UpgradePage (/app/upgrade/:subscriptionId) -- Tier 2 vs Tier 3 cards;
               calls POST /v1/billing/checkout with tier in body;
               handles redirectUrl from Stripe response

Feature 5.5 -- Admin pages (/admin/*) (NEW from docs 21/22/23)
  Story 5.5.1  AdminDashboardPage (/admin/dashboard) -- calls GET /v1/admin/kpis;
               displays MRR (CAD), active subscriptions, scans/day, failure rate %
  Story 5.5.2  AdminCustomersPage (/admin/customers) -- search input calls
               GET /v1/admin/customers?query=; displays tier, paymentStatus,
               isLocked, lastActivityUtc; deep links to customer runs
  Story 5.5.3  AdminBillingPage (/admin/billing) -- Stripe billing portal link;
               webhook health indicator; "Reconcile Stripe" button calls
               POST /v1/admin/stripe/reconcile with confirmation modal
  Story 5.5.4  AdminRunsPage (/admin/runs) -- lists runs from GET /v1/admin/runs;
               supports filter by subscriptionId and type (scan|analysis|delivery)
  Story 5.5.5  AdminControlsPage (/admin/controls) -- grant tier form (subscriptionId,
               tier, days, reason); lock/unlock subscription form; rate-limit override;
               feature flag toggles; incident banner text input;
               all destructive actions write admin_audit_events via backend

Feature 5.6 -- API client layer (NEW from doc 22)
  Story 5.6.1  frontend/src/app/api/client.ts -- base http<T> function; includes
               credentials; throws on non-ok; Content-Type application/json
  Story 5.6.2  frontend/src/app/api/appApi.ts -- customer API calls:
               getTier1Report, startCollection, getStatus, getEntitlement,
               startCheckout, getBillingPortalUrl
  Story 5.6.3  frontend/src/app/api/adminApi.ts -- admin API calls:
               kpis, searchCustomers, grantEntitlement, lockSubscription,
               reconcileStripe, getRuns
  Story 5.6.4  frontend/src/app/types/models.ts -- TypeScript DTOs:
               Tier1Report, Finding, AdminKpis, AdminCustomerRow, Entitlement,
               CollectionStatus, AdminCustomerSearchResponse

Feature 5.7 -- Shared components (NEW from doc 22)
  Story 5.7.1  Loading.tsx -- full-page or inline Fluent Spinner with aria-label
  Story 5.7.2  ErrorState.tsx -- Fluent MessageBar (error) with retry callback
  Story 5.7.3  DataTable.tsx -- accessible Fluent Table wrapper (th scope=col)
  Story 5.7.4  MoneyRangeBar.tsx -- visual low/high saving range bar with currency label
  Story 5.7.5  EffortBadge.tsx -- colour-coded badge: trivial/easy/medium/involved/strategic

Feature 5.8 -- Consent and telemetry integration
  Story 5.8.1  As a user I see a consent banner on first visit (ConsentBanner reused)
  Story 5.8.2  TelemetryProvider.tsx wraps CustomerLayout; loads GTM + Clarity scripts
               only when VITE_ENABLE_TELEMETRY=true AND consent granted
  Story 5.8.3  All 16 AnalyticsEventName events fire at correct points in customer flow
  Story 5.8.4  Admin surface does NOT load telemetry (no GA4 in admin pages)

Feature 5.9 -- Accessibility
  Story 5.9.1  Skip-to-content link is first focusable element on every page
  Story 5.9.2  Full keyboard navigation in all customer and admin pages
  Story 5.9.3  All form fields have associated label elements
  Story 5.9.4  Admin confirmation modals trap focus and close on Escape

=============================================================================
EPIC 6 -- MONETIZATION AND BILLING (M1.5)
=============================================================================

Goal: Stripe checkout, webhook, entitlements, recurring billing lifecycle all work.

Feature 6.1 -- Stripe checkout
  Story 6.1.1  POST /v1/checkout/tier2 returns a Stripe checkout session URL
  Story 6.1.2  POST /v1/checkout/tier3 returns a Stripe checkout session URL
  Story 6.1.3  mode=subscription creates a Stripe subscription (Tier 2 monthly)
  Story 6.1.4  mode=one_time creates a one-time session (Tier 2 one-time, Tier 3)
  Story 6.1.5  Checkout metadata contains subscriptionId and analysisId

Feature 6.2 -- Webhook lifecycle
  Story 6.2.1  checkout.session.completed -> write entitlement to Cosmos, trigger delivery
               if Tier 3
  Story 6.2.2  invoice.paid -> renew Tier 2 subscription entitlement for next period
  Story 6.2.3  customer.subscription.updated -> update Tier in Cosmos clients container
  Story 6.2.4  customer.subscription.deleted -> downgrade to Tier 1 in Cosmos
  Story 6.2.5  All webhook events written to payments container for audit trail

Feature 6.3 -- Entitlement service
  Story 6.3.1  GET /v1/entitlements?subscriptionId=X returns { tier, validUntil, features[] }
  Story 6.3.2  Tier gate evaluates entitlement from Cosmos (with APIM 60s cache)
  Story 6.3.3  StripeCustomerMapRepo resolves stripeCustomerId -> subscriptionId for webhooks
  Story 6.3.4  Billing portal endpoint derives stripeCustomerId from Cosmos clients container
               (never from browser input -- security requirement)

=============================================================================
EPIC 7 -- DELIVERY PACKAGER (M1.6)
=============================================================================

Goal: Tier 3 deliverable ZIP generated, uploaded, SAS URL delivered.

Feature 7.1 -- IaC template library
  Story 7.1.1  12 Jinja2 template folders exist in services/delivery/app/templates/
               (one per deliverable_template_id from analysis rules)
  Story 7.1.2  Each folder has main.bicep (Phase 1), main.tf (Phase 2), README.md
  Story 7.1.3  Templates are parameterized with scan_id, subscription_id, and finding fields
  Story 7.1.4  Template content sourced from 12-IaCscript.md patterns

Feature 7.2 -- Package and deliver
  Story 7.2.1  Delivery service generates all IaC artifacts for a scan's findings
  Story 7.2.2  ZIP is assembled with findings.json manifest at root
  Story 7.2.3  ZIP is signed with SHA-256 and the hash stored in the deliverables container
  Story 7.2.4  ZIP is uploaded to Azure Blob Storage with 24h SAS URL
  Story 7.2.5  Deliverable record is written to Cosmos with sasUrl, sha256, artifactCount

=============================================================================
EPIC 8 -- OBSERVABILITY AND TELEMETRY (M2.0)
=============================================================================

Goal: GA4, Clarity, App Insights all wired. Zero PII in any telemetry event.

Feature 8.1 -- Frontend telemetry
  Story 8.1.1  GTM container is loaded in index.html with consent gating
  Story 8.1.2  GA4 tag fires after consent accepted
  Story 8.1.3  Clarity tag fires after consent accepted with form field masking ON
  Story 8.1.4  All 16 AnalyticsEventName events are fired at correct points in the UI
  Story 8.1.5  Consent banner allows accept/reject: rejected state suppresses all tags
  Story 8.1.6  Consent preference is respected across page reloads (localStorage)

Feature 8.2 -- Backend observability
  Story 8.2.1  App Insights connection string is set in all Container Apps via KV reference
  Story 8.2.2  All service logs are structured JSON and appear in Azure Monitor
  Story 8.2.3  Scan duration, analysis duration, delivery duration are emitted as custom metrics
  Story 8.2.4  All API errors (4xx, 5xx) are logged with error_category enum (no raw messages)
  Story 8.2.5  Stripe webhook events are logged with event type + subscriptionId (hashed)

Feature 8.3 -- Alerting
  Story 8.3.1  Alert: API service 5xx rate > 5% in 5 minutes -> PagerDuty / email
  Story 8.3.2  Alert: Collector job failure -> email + Cosmos audit record
  Story 8.3.3  Alert: Anomaly detection rule fires -> owner notified (Story R-05 output)

=============================================================================
EPIC 9 -- i18n AND a11y (M2.1)
=============================================================================

Goal: All 5 locales live. WCAG 2.1 AA passing in axe-core CI gate.

Feature 9.1 -- i18n
  Story 9.1.1  i18next is configured with 5 locale namespaces in frontend/src/i18n/
  Story 9.1.2  All user-visible strings are extracted to translation files (no hardcoded EN text)
  Story 9.1.3  Language selector is visible in the nav with locale names in their own language:
               English, Francais, Portugues (Brasil), Espanol, Deutsch
  Story 9.1.4  Locale preference is persisted in localStorage
  Story 9.1.5  Date formats use Intl.DateTimeFormat -- locale-aware, no hardcoded format
  Story 9.1.6  Number/currency formats use Intl.NumberFormat with locale and currency options:
               CAD, USD, BRL, EUR supported on findings page saving estimates
  Story 9.1.7  fr (fr-CA) translations are completed before Phase 1 go-live
               (required for Canadian market)
  Story 9.1.8  pt-BR and es and de translations completed before Phase 2 go-live
  Story 9.1.9  API error messages returned with Accept-Language header support for the
               5 supported locales (error codes + localized message)
  Story 9.1.10 Stripe checkout locale is set from user preference

Feature 9.2 -- a11y
  Story 9.2.1  axe-core CI check runs on every PR -- zero critical or serious violations gate
  Story 9.2.2  All icon-only buttons have aria-label in all 5 locales
  Story 9.2.3  All form fields have associated <label> elements (no placeholder-as-label)
  Story 9.2.4  Findings table has proper <th scope="col"> headers
  Story 9.2.5  PreFlight status indicators use both colour and icon/text (not colour-only)
  Story 9.2.6  Colour contrast ratio >= 4.5:1 for all body text (verified in Figma + axe)
  Story 9.2.7  Focus ring is visible and high-contrast on all focusable elements
  Story 9.2.8  Skip-to-content link is the first focusable element on every page
  Story 9.2.9  Consent banner is keyboard-accessible and screen-reader-labelled
  Story 9.2.10 Keyboard-only walkthrough of the full Tier 1 flow passes before M1.4 sign-off

=============================================================================
EPIC 10 -- COMMERCIAL HARDENING (M2.2)
=============================================================================

Goal: Security review passed, privacy compliance ready, support tooling live.

Feature 10.1 -- Security
  Story 10.1.1  Red-team agent runs Tier 1 token against findings API and asserts
                no narrative or deliverable_template_id in response
  Story 10.1.2  All endpoints validated: no tenant A can access tenant B data
                (partition key enforcement verified in integration tests)
  Story 10.1.3  Stripe webhook signature verified on every event (whsec_ secret)
  Story 10.1.4  Admin endpoints protected by bearer token rotation schedule
  Story 10.1.5  All Cosmos queries parameterized (no string concatenation in queries)
  Story 10.1.6  CSP header enforced: scripts from GTM/Stripe/Clarity only, no inline

Feature 10.2 -- Privacy compliance
  Story 10.2.1  Privacy policy published at /privacy in all 5 locales
  Story 10.2.2  Terms of service published at /terms in all 5 locales
  Story 10.2.3  Data retention policy: collected Azure data purged after 90 days
                (Cosmos container TTL = 7,776,000 seconds on scans, inventories, cost-data)
  Story 10.2.4  Client can request data deletion via DELETE /v1/auth/disconnect which
                hard-deletes all Cosmos documents for that subscriptionId
  Story 10.2.5  GA4 data retention set to 14 months. IP anonymization enabled.
  Story 10.2.6  Clarity data retention respects GDPR right-to-be-forgotten via Clarity API

Feature 10.3 -- Support and docs
  Story 10.3.1  docs/client-access-guide.md published at /docs/access-guide in all 5 locales
  Story 10.3.2  FAQ page covers top 10 support questions (from preflight failure analysis)
  Story 10.3.3  Status page (uptime) linked from footer

=============================================================================
EPIC 11 -- PHASE 2 INFRASTRUCTURE (M3.0)
=============================================================================

Goal: Private subscription provisioned, CI pointing to Phase 2, domain live.

Feature 11.1 -- Terraform provisioning
  Story 11.1.1  `terraform apply` on infra/phase2-private completes without error
  Story 11.1.2  ACA-specific APIM instance is deployed with Tier enforcement policies
  Story 11.1.3  GitHub Actions deploy-phase2.yml is wired to private subscription via OIDC
  Story 11.1.4  Custom domain (app.aca.example.com / api.aca.example.com) configured with
                managed TLS via Azure Container Apps ingress
  Story 11.1.5  Phase 2 Cosmos has 3 geo-replicas (canadacentral primary + failover)

Feature 11.2 -- Cutover
  Story 11.2.1  DNS TTL lowered 48h before cutover
  Story 11.2.2  Phase 1 marco* infra remains live as rollback for 30 days post-cutover
  Story 11.2.3  Phase 2 smoke test: full Tier 1 -> Tier 3 flow on Phase 2 infra
  Story 11.2.4  APIM configuration exported and version-controlled

=============================================================================
EPIC 12 -- DATA MODEL SUPPORT (ONGOING)
=============================================================================

Goal: EVA data model used as source of truth for build process and as app runtime API.

Feature 12.1 -- Build-time use
  Story 12.1.1  All epics, features, and stories from this PLAN are seeded into
                the data-model stories layer
  Story 12.1.2  Each story has status: not-started / in-progress / done
  Story 12.1.3  Story status is updated by the agent at start and end of each work item
  Story 12.1.4  data-model agent-summary reflects current overall completion percentage

Feature 12.2 -- Runtime use
  Story 12.2.1  API service reads feature_flags layer to gate unreleased features
  Story 12.2.2  Analysis service reads the rules layer to discover enabled/disabled rules
               (data-model rules layer matches services/analysis/app/rules/ files)
  Story 12.2.3  Endpoints layer is kept in sync with every shipped route (PUT on ship)
  Story 12.2.4  Containers layer reflects the actual Cosmos schema (fields, partition keys)

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
D3  29-foundry -- agent framework (collection, analysis, generation, redteam agents)
D4  31-eva-faces -- Fluent UI v9 patterns (frontend component patterns)
D5  37-data-model -- shared EVA data model API code (services/api, port 8011)
D6  48-eva-veritas -- traceability (audit_repo gates trust score)
D7  Stripe account (marco production) -- needed before M1.5
D8  Google Analytics 4 property ID (existing marco account) -- needed at M2.0
D9  Microsoft Clarity project ID (existing marco account) -- needed at M2.0
D10 Private Azure subscription for Phase 2 -- needed before M3.0
