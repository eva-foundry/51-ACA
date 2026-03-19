# PLAN-02: API, Frontend, and Billing (Epics 4-6)

**Module**: PLAN-02  
**Epics**: 4 (API and Auth), 5 (Frontend), 6 (Billing)  
**Stories**: 88 total (28 + 42 + 18)  
**Function Points**: 365 (125 + 175 + 65)

---

## Epic 4: API and Auth Layer

**Goal**: All 25+ API endpoints implemented, JWT-validated, APIM-proxied. Multi-tenant architecture (authority=common).  
**Status**: IN PROGRESS  
**Stories**: 28  
**Function Points**: 125

**Key Decision**: ACA is standalone private-sector SaaS. NOT tied to EsDAICoE organization. Multi-tenant: authority=https://login.microsoftonline.com/common. Any client with a Microsoft account (any tenant) can sign in. What matters: delegated token has Reader + Cost Management Reader on CLIENT's subscription. ACA app registration must be multi-tenant in Azure portal.

---

## Feature 4.1: Authentication (multi-tenant)

### Story ACA-04-001: Multi-tenant sign-in
As a client I can sign in via Microsoft Identity (any Microsoft tenant); I do not need to be in any specific organization to use ACA

**Acceptance**: MSAL configured with authority=common, any tenant user can authenticate

### Story ACA-04-002: JWT validation
As the API I validate the JWT on every authenticated endpoint using JWKS from https://login.microsoftonline.com/common/discovery/keys

**Status**: DONE (Sprint-02)  
**Acceptance**: API rejects invalid JWTs, validates signature against JWKS

### Story ACA-04-003: Session and tier resolution
As the API I extract subscriptionId from the session (stored after connect); tier is read from the Cosmos clients container (not from JWT claims)

**Acceptance**: Tier enforcement reads from Cosmos, not JWT claims

### Story ACA-04-004: Multi-mode subscription connection
As a client I can connect my Azure subscription (POST /v1/auth/connect) in Mode A (delegated, any-tenant), Mode B (service principal provided by client), or Mode C (Azure Lighthouse delegation)

**Acceptance**: All 3 modes supported, stored in clients container with mode field

### Story ACA-04-005: Disconnection and token revocation
As a client I can disconnect (POST /v1/auth/disconnect) and all access tokens are invalidated and removed from Key Vault

**Acceptance**: Tokens deleted from KV, refresh tokens revoked, scan records marked disconnected

### Story ACA-04-006: Auth implementation beyond stubs
As a developer auth.py is reworked: MSAL authority=common, no EsDAICoE org dependency, all 3 endpoints (connect/preflight/disconnect) implemented beyond 501 stubs. Refresh token stored per-scan in KV, not per-user.

**Status**: DONE (Sprint-02)  
**Acceptance**: auth.py implements full MSAL flow, stores tokens securely

### Story ACA-04-007: Frontend MSAL integration
As the frontend LoginPage, sign-in CTA calls MSAL.js with authority=common so any Microsoft account (personal or work) is accepted

**Acceptance**: MSAL.js configured correctly, popup or redirect auth flow works

---

## Feature 4.2: Core API endpoints (Spark paths)

### Story ACA-04-008: Connect subscription endpoint
POST /v1/auth/connect -- Connect Azure subscription

**Status**: DONE (Sprint-02)  
**Acceptance**: Endpoint stores mode, subscriptionId, tokens in Cosmos + KV

### Story ACA-04-009: Preflight probes endpoint
POST /v1/auth/preflight -- Run pre-flight probes

**Acceptance**: Endpoint returns probe results (identity, RBAC, inventory, cost, advisor)

### Story ACA-04-010: Disconnect endpoint
POST /v1/auth/disconnect -- Disconnect subscription

**Acceptance**: Endpoint deletes tokens, revokes refresh, updates client record

### Story ACA-04-011: Collection start endpoint
POST /v1/collect/start -- Trigger collector job (was /v1/scans)

**Acceptance**: Creates scan record, triggers collector job, returns scanId

### Story ACA-04-012: Collection status endpoint
GET /v1/collect/status -- Poll collection progress (was /v1/scans/:scanId)

**Acceptance**: Returns current status, progress %, stats (inventoryCount, costRows)

### Story ACA-04-013: Tier 1 report endpoint
GET /v1/reports/tier1 -- Tier 1 findings report (was /v1/findings/:scanId)

**Acceptance**: Returns findings filtered by tier, respects entitlement

### Story ACA-04-014: Stripe checkout endpoint
POST /v1/billing/checkout -- Stripe checkout (tier2 or tier3 in body)

**Acceptance**: Creates Stripe session, returns checkout URL

### Story ACA-04-015: Stripe billing portal endpoint
GET /v1/billing/portal -- Stripe billing portal redirect URL

**Acceptance**: Returns portal URL for customer's Stripe session

### Story ACA-04-016: Stripe webhook handler
POST /v1/webhooks/stripe -- Stripe event handler

**Acceptance**: Verifies signature, processes lifecycle events, updates entitlements

### Story ACA-04-017: Entitlements endpoint
GET /v1/entitlements -- Current tier for subscriptionId

**Acceptance**: Returns tier, validUntil,  features array from Cosmos

### Story ACA-04-018: Health check endpoint
GET /health -- Health check (unauthenticated)

**Acceptance**: Returns status, version, no authentication required

---

## Feature 4.3: APIM policies

### Story ACA-04-019: JWT validation policy
As the gateway I validate JWT signature on all /v1/* routes

**Acceptance**: APIM policy rejects requests without valid JWT

### Story ACA-04-020: Entitlement caching
As the gateway I cache /v1/entitlements response for 60s per subscriptionId using cache key entitlements::{subscriptionId} (from doc 19)

**Acceptance**: Cache hit logged on repeated requests within 60s window

### Story ACA-04-021: Tier enforcement policy
As the gateway I return 403 with TIER_REQUIRED error when a Tier 1 client calls a Tier 2+ endpoint

**Acceptance**: Policy checks tier from cached entitlement, blocks unauthorized access

### Story ACA-04-022: Rate limiting policy
As the gateway I enforce subscription key throttling (100 req/min default)

**Acceptance**: APIM returns 429 after 100 requests in 60s window

### Story ACA-04-023: Subscription ID forwarding
As the gateway I forward X-Subscription-Id header to the API on all calls

**Acceptance**: API receives header, uses for partition key resolution

---

## Feature 4.4: Admin API endpoints

### Story ACA-04-024: Admin KPIs endpoint
GET /v1/admin/kpis -- Returns { utc, mrrCad, activeSubscriptions, scansLast24h, analysesLast24h, deliveriesLast24h, failureRatePctLast24h }. Requires role: ACA_Admin | ACA_Support | ACA_FinOps

**Acceptance**: Endpoint calculates metrics from Cosmos, enforces RBAC

### Story ACA-04-025: Admin customer search endpoint
GET /v1/admin/customers?query= -- Searches by subscriptionId, stripeCustomerId; returns list of AdminCustomerRow (subscriptionId, stripeCustomerId, tier, paymentStatus, lastActivityUtc, isLocked). Requires role: ACA_Admin | ACA_Support | ACA_FinOps

**Acceptance**: Query searches multiple fields, returns paginated results

### Story ACA-04-026: Admin grant entitlement endpoint
POST /v1/admin/entitlements/grant -- Body: { subscriptionId, tier, days, reason }. Writes entitlement to Cosmos + writes admin_audit_events record. Requires role: ACA_Admin | ACA_Support

**Acceptance**: Creates entitlement, logs audit event with reason and operator

### Story ACA-04-027: Admin lock subscription endpoint
POST /v1/admin/subscriptions/:subscriptionId/lock -- Body: { reason }. Marks subscription locked in clients container. Writes admin_audit_events record. Requires role: ACA_Admin | ACA_Support

**Acceptance**: Sets isLocked=true, logs event, blocks future scans

### Story ACA-04-028: Admin Stripe reconciliation endpoint
POST /v1/admin/stripe/reconcile -- Enqueues reconcile job: fetches all active Stripe subscriptions and repairs missing entitlements in Cosmos. Returns { jobId, acceptedUtc }. Requires role: ACA_Admin

**Acceptance**: Job enqueued, reconciles Stripe vs Cosmos, logs discrepancies

### Story ACA-04-029: Admin runs listing endpoint
GET /v1/admin/runs?type=scan|analysis|delivery -- Lists job run records (scan/analysis/delivery) from Cosmos. Supports filter by subscriptionId and type. Requires role: ACA_Admin | ACA_Support | ACA_FinOps

**Acceptance**: Returns runs filtered by type, paginated, includes status and duration

---

## Feature 4.5: Data layer correctness

### Story ACA-04-030: Cosmos upsert partition key enforcement
services/api/app/db/cosmos.py upsert_item() must accept partition_key as a required third parameter and pass it explicitly to container.upsert_item(). Without this, the Cosmos SDK infers partition_key from the item dict which is unreliable and silently fails tenant isolation on malformed documents. All callers of upsert_item() must be updated to pass partition_key=subscription_id.

**Status**: DONE (Sprint-01, merged PR #11)  
**Acceptance**: upsert_item signature requires partition_key, all callers updated

---

## Epic 5: Frontend Core

**Goal**: Spark /app/* + /admin/* routing live. RequireAuth + RequireRole guards. All 5 customer pages + 5 admin pages functional. Tier 1 flow end-to-end.  
**Status**: IN PROGRESS  
**Stories**: 42  
**Function Points**: 175

---

## Feature 5.1: Auth layer

### Story ACA-05-001: Role constants definition
roles.ts defines ACA_Admin, ACA_Support, ACA_FinOps role constants

**Acceptance**: TypeScript enum or const with 3 roles defined

### Story ACA-05-002: useAuth hook implementation
useAuth.ts wraps MSAL PublicClientApplication; exposes user, roles, isAuthenticated, login(), logout(). DEV bypass mode: when VITE_DEV_AUTH=true, simulates signed-in user with configurable roles + subscriptionId (no MSAL call needed)

**Acceptance**: Hook provides auth state, supports dev bypass for local testing

### Story ACA-05-003: RequireAuth guard component
RequireAuth.tsx: if !isAuthenticated redirect to /

**Acceptance**: Component redirects unauthenticated users to login page

### Story ACA-05-004: RequireRole guard component
RequireRole.tsx: if user lacks anyOf roles, redirect to /app/connect. Destructive action gating: confirmation modal before grant/lock/reconcile

**Acceptance**: Component enforces RBAC, shows confirmation for destructive actions

### Story ACA-05-005: Admin route protection
All admin routes require RequireAuth + RequireRole (ACA_Admin|Support|FinOps)

**Acceptance**: Admin routes inaccessible without proper role

---

## Feature 5.2: Layout layer

### Story ACA-05-006: Customer layout component
CustomerLayout.tsx: top nav with logo, LanguageSelector, user menu. Wraps all /app/* routes via Outlet

**Acceptance**: Layout renders consistently on all customer pages

### Story ACA-05-007: Admin layout component
AdminLayout.tsx: top nav + left sidebar with admin nav items. Wraps all /admin/* routes via Outlet

**Acceptance**: Layout includes navigation to all 5 admin pages

### Story ACA-05-008: Customer navigation component
NavCustomer.tsx: links to /app/connect, /app/status, /app/findings

**Acceptance**: Navigation highlights active route, accessible

### Story ACA-05-009: Admin navigation component
NavAdmin.tsx: links to /admin/dashboard, /admin/customers, /admin/billing, /admin/runs, /admin/controls

**Acceptance**: Sidebar navigation with icons and labels

### Story ACA-05-010: App shell root component
AppShell.tsx: root component with FluentProvider + ConsentBanner + RouterProvider (replaces App.tsx BrowserRouter pattern)

**Acceptance**: App shell wraps entire application, provides theme context

---

## Feature 5.3: Router (Spark createBrowserRouter pattern)

### Story ACA-05-011: Router configuration
router.tsx uses createBrowserRouter (not BrowserRouter + <Routes>)

**Acceptance**: Router configured with static route objects

### Story ACA-05-012: Login route
Route / -> LoginPage (no auth required)

**Acceptance**: Root route accessible without authentication

### Story ACA-05-013: Customer routes
Routes /app/* -> RequireAuth -> CustomerLayout -> Outlet

**Acceptance**: All customer routes protected by auth guard

### Story ACA-05-014: Admin routes
Routes /admin/* -> RequireAuth -> RequireRole -> AdminLayout -> Outlet

**Acceptance**: All admin routes protected by auth + role guards

### Story ACA-05-015: Code splitting
Code-split: all page components lazy-loaded with React.lazy

**Acceptance**: Initial bundle size < 200KB, pages load on demand

---

## Feature 5.4: Customer pages (/app/*)

### Story ACA-05-016: Login page
LoginPage (/) -- Entra ID login CTA + dev bypass link

**Acceptance**: Page renders SSO button, triggers MSAL flow

### Story ACA-05-017: Connect subscription page
ConnectSubscriptionPage (/app/connect) -- Mode A/B/C radio group; calls POST /v1/auth/connect then POST /v1/collect/start; stores subscriptionId in sessionStorage after connect

**Acceptance**: Page supports 3 connection modes, navigates to status on success

### Story ACA-05-018: Collection status page
CollectionStatusPage (/app/status/:subscriptionId) -- polls GET /v1/collect/status with backoff; shows named steps + progress bar; links to /app/findings/:subscriptionId when collection complete

**Acceptance**: Page polls every 3s, shows progress, auto-navigates when complete

### Story ACA-05-019: Findings Tier 1 page
FindingsTier1Page (/app/findings/:subscriptionId) -- renders Tier 1 report from GET /v1/reports/tier1; shows MoneyRangeBar + EffortBadge per finding; blurred upgrade CTA rows for Tier 2+ findings

**Acceptance**: Page displays findings table, tier-gated content blurred

### Story ACA-05-020: Upgrade page
UpgradePage (/app/upgrade/:subscriptionId) -- Tier 2 vs Tier 3 cards; calls POST /v1/billing/checkout with tier in body; handles redirectUrl from Stripe response

**Acceptance**: Page displays tier comparison, redirects to Stripe checkout

---

## Feature 5.5: Admin pages (/admin/*)

### Story ACA-05-021: Admin dashboard page
AdminDashboardPage (/admin/dashboard) -- calls GET /v1/admin/kpis; displays MRR (CAD), active subscriptions, scans/day, failure rate %

**Acceptance**: Dashboard shows 6 KPI cards with real-time data

### Story ACA-05-022: Admin customers page
AdminCustomersPage (/admin/customers) -- search input calls GET /v1/admin/customers?query=; displays tier, paymentStatus, isLocked, lastActivityUtc; deep links to customer runs

**Acceptance**: Search filters customer list, table sortable and paginated

### Story ACA-05-023: Admin billing page
AdminBillingPage (/admin/billing) -- Stripe billing portal link; webhook health indicator; "Reconcile Stripe" button calls POST /v1/admin/stripe/reconcile with confirmation modal

**Acceptance**: Page shows webhook status, reconciliation triggers job

### Story ACA-05-024: Admin runs page
AdminRunsPage (/admin/runs) -- lists runs from GET /v1/admin/runs; supports filter by subscriptionId and type (scan|analysis|delivery)

**Acceptance**: Page displays run history, filterable by type and subscription

### Story ACA-05-025: Admin controls page
AdminControlsPage (/admin/controls) -- grant tier form (subscriptionId, tier, days, reason); lock/unlock subscription form; rate-limit override; feature flag toggles; incident banner text input; all destructive actions write admin_audit_events via backend

**Acceptance**: Page provides admin controls, requires confirmation for dangerous actions

---

## Feature 5.6: API client layer

### Story ACA-05-026: Base HTTP client
frontend/src/app/api/client.ts -- base http<T> function; includes credentials; throws on non-ok; Content-Type application/json

**Acceptance**: Client handles auth headers, errors, JSON serialization

### Story ACA-05-027: Customer API functions
frontend/src/app/api/appApi.ts -- customer API calls: getTier1Report, startCollection, getStatus, getEntitlement, startCheckout, getBillingPortalUrl

**Acceptance**: All customer endpoints wrapped with TypeScript types

### Story ACA-05-028: Admin API functions
frontend/src/app/api/adminApi.ts -- admin API calls: kpis, searchCustomers, grantEntitlement, lockSubscription, reconcileStripe, getRuns

**Acceptance**: All admin endpoints wrapped, RBAC enforced client-side

### Story ACA-05-029: TypeScript DTOs
frontend/src/app/types/models.ts -- TypeScript DTOs: Tier1Report, Finding, AdminKpis, AdminCustomerRow, Entitlement, CollectionStatus, AdminCustomerSearchResponse

**Acceptance**: All API responses typed, enforced by TypeScript

---

## Feature 5.7: Shared components

### Story ACA-05-030: Loading component
Loading.tsx -- full-page or inline Fluent Spinner with aria-label

**Acceptance**: Component renders accessible spinner with customizable size

### Story ACA-05-031: Error state component
ErrorState.tsx -- Fluent MessageBar (error) with retry callback

**Acceptance**: Component displays error message, provides retry button

### Story ACA-05-032: Data table component
DataTable.tsx -- accessible Fluent Table wrapper (th scope=col)

**Acceptance**: Table component supports sorting, pagination, accessibility

### Story ACA-05-033: Money range bar component
MoneyRangeBar.tsx -- visual low/high saving range bar with currency label

**Acceptance**: Component displays savings range as horizontal bar chart

### Story ACA-05-034: Effort badge component
EffortBadge.tsx -- colour-coded badge: trivial/easy/medium/involved/strategic

**Acceptance**: Badge uses semantic colors, accessible contrast ratios

---

## Feature 5.8: Consent and telemetry integration

### Story ACA-05-035: Consent banner
As a user I see a consent banner on first visit (ConsentBanner reused)

**Acceptance**: Banner shows on first visit, choice persisted in localStorage

### Story ACA-05-036: Telemetry provider
TelemetryProvider.tsx wraps CustomerLayout; loads GTM + Clarity scripts only when VITE_ENABLE_TELEMETRY=true AND consent granted

**Acceptance**: Scripts load conditionally, respect consent preference

### Story ACA-05-037: Analytics event tracking
All 16 AnalyticsEventName events fire at correct points in customer flow

**Acceptance**: Events tracked: page_view, scan_start, scan_complete, tier_upgrade, etc.

### Story ACA-05-038: Admin telemetry exclusion
Admin surface does NOT load telemetry (no GA4 in admin pages)

**Acceptance**: Telemetry scripts not loaded on /admin/* routes

---

## Feature 5.9: Accessibility

### Story ACA-05-039: Skip to content link
Skip-to-content link is first focusable element on every page

**Acceptance**: Link visible on focus, jumps to main content

### Story ACA-05-040: Keyboard navigation
Full keyboard navigation in all customer and admin pages

**Acceptance**: All interactive elements focusable, logical tab order

### Story ACA-05-041: Form labels
All form fields have associated label elements

**Acceptance**: Labels correctly associated via htmlFor, no placeholder-only fields

### Story ACA-05-042: Modal focus trapping
Admin confirmation modals trap focus and close on Escape

**Acceptance**: Focus cycles within modal, Escape key closes modal

---

## Epic 6: Monetization and Billing (Stripe)

**Goal**: Stripe checkout, webhook, entitlements, recurring billing lifecycle all work.  
**Status**: DONE  
**Stories**: 18  
**Function Points**: 65

**Key Decisions**: Prices are env-var driven (STRIPE_PRICE_* settings). NOT hardcoded. Billing is monthly subscription for Tier 2. Tier 3 is one-time. Promotion codes are supported (full fee waiver for trials/partnerships).

---

## Feature 6.1: Stripe checkout

### Story ACA-06-001: Tier 2 checkout session
POST /v1/checkout/tier2 returns a Stripe checkout session URL

**Acceptance**: Endpoint creates Stripe session, returns checkout URL

### Story ACA-06-002: Tier 3 checkout session
POST /v1/checkout/tier3 returns a Stripe checkout session URL

**Acceptance**: Endpoint creates Stripe session for one-time payment

### Story ACA-06-003: Subscription mode checkout
mode=subscription creates a Stripe subscription (Tier 2 monthly)

**Acceptance**: Stripe session configured for recurring billing

### Story ACA-06-004: One-time mode checkout
mode=one_time creates a one-time session (Tier 2 one-time, Tier 3)

**Acceptance**: Stripe session configured for single payment

### Story ACA-06-005: Checkout metadata
Checkout metadata contains subscriptionId and analysisId

**Acceptance**: Metadata attached to Stripe session, accessible in webhooks

### Story ACA-06-006: Coupon code support
As a client with a coupon code I can enter it at Stripe checkout and receive a partial or full fee waiver (allow_promotion_codes=True when STRIPE_COUPON_ENABLED=true)

**Acceptance**: Checkout page shows promo code field, discounts applied

### Story ACA-06-007: Coupon feature flag
settings.py has STRIPE_COUPON_ENABLED: bool = True field. stripe_service.py passes allow_promotion_codes=setting to checkout session

**Acceptance**: Feature flag controls coupon availability

### Story ACA-06-008: Admin coupon creation
As an admin I can create Stripe promotion codes for trial clients without any code changes (pure Stripe dashboard action)

**Acceptance**: Codes created in Stripe dashboard work immediately

---

## Feature 6.2: Webhook lifecycle

### Story ACA-06-009: Checkout completion handler
checkout.session.completed -> write entitlement to Cosmos, trigger delivery if Tier 3

**Acceptance**: Webhook creates entitlement, starts delivery job for Tier 3

### Story ACA-06-010: Invoice payment handler
invoice.paid -> renew Tier 2 subscription entitlement for next period

**Acceptance**: Webhook extends entitlement validUntil date

### Story ACA-06-011: Subscription update handler
customer.subscription.updated -> update Tier in Cosmos clients container

**Acceptance**: Webhook syncs subscription tier changes to Cosmos

### Story ACA-06-012: Subscription deletion handler
customer.subscription.deleted -> downgrade to Tier 1 in Cosmos unless Tier 3 permanent

**Acceptance**: Webhook preserves Tier 3, downgrades Tier 2 to Tier 1

### Story ACA-06-013: Webhook audit trail
All webhook events written to payments container for audit trail

**Acceptance**: Every webhook event logged with timestamp and payload

---

## Feature 6.3: Entitlement service

### Story ACA-06-014: Entitlement query endpoint
GET /v1/entitlements?subscriptionId=X returns { tier, validUntil, features[] }

**Acceptance**: Endpoint queries Cosmos, returns current entitlement

### Story ACA-06-015: Tier gate evaluation
Tier gate evaluates entitlement from Cosmos (with APIM 60s cache)

**Acceptance**: Gate checks tier, blocks unauthorized access

### Story ACA-06-016: Stripe customer mapping
StripeCustomerMapRepo resolves stripeCustomerId -> subscriptionId for webhooks

**Acceptance**: Repository maintains bidirectional mapping

### Story ACA-06-017: Billing portal security
Billing portal endpoint derives stripeCustomerId from Cosmos clients container (never from browser input -- security requirement)

**Acceptance**: Portal URL generation reads customer ID from server-side Cosmos, not request body

### Story ACA-06-018: Tier 3 entitlement preservation
As a Tier 3 customer, when my Tier 2 subscription is canceled (subscription.deleted) my Tier 3 one-time purchase access is preserved. revoke() must not unconditionally set tier=1. Correct logic: if existing.tier >= 3, new_tier = 3 else new_tier = 1. payment_status is always set to canceled regardless. A customer who paid $1,499 one-time for Tier 3 must not lose access due to a Tier 2 subscription lifecycle event.

**Acceptance**: Tier 3 entitlements persist after Tier 2 subscription cancellation

---

**End of PLAN-02** -- Continue to [PLAN-03.md](PLAN-03.md) for Epics 7-9
