ACA -- Azure Cost Advisor
=========================

Version: 0.7.0
Updated: 2026-03-02T21:50:00Z (Sprint-002 Complete: Multi-Agent Orchestration delivered, 5 stories, 34 FP, 100% acceptance criteria)
Maturity: active -- Phase 1 multi-agent failure recovery pipeline complete; Sprint-003 ready to start

=============================================================================
PRODUCT VISION
=============================================================================

ACA is a consulting-session-as-a-product.

A client navigates to the ACA app URL (Phase 1: Azure Container Apps free hostname;
Phase 2: custom domain), connects their Azure
subscription with read-only consent, and in under five minutes receives a
prioritized cost and optimization report built from 12 months of billing
signals, Azure Advisor output, network topology, and policy compliance data.

They get the insight that previously required a three-day consulting engagement
delivered as a self-serve SaaS in three tiers -- free summary, paid advisory,
paid IaC deliverable package.

Target buyer: the cloud platform manager or director responsible for a
development Azure subscription in the CAD $300K-$2M+ annual spend range.
They know costs are high. They do not have time to investigate. ACA does the
investigation and packages the answer in board-ready language.

=============================================================================
SERVICE TIERS
=============================================================================

Tier 1 -- Free Scan
  Price   : Free
  Access  : No payment required. Sign in, connect, collect, report.
  Scope   : Opportunity title + estimated saving range (CAD low / high).
            No narrative. No IaC. No implementation detail.
  Purpose : Lead generation. Convert to Tier 2 or Tier 3.

Tier 2 -- Advisory Report
  Price   : CAD $499 one-time  OR  CAD $150/month subscription
  Access  : Unlocked after Stripe checkout (stored in Cosmos entitlements).
  Scope   : Full prioritized findings with:
            - Narrative explaining the finding
            - Effort classification (trivial / easy / medium / involved / strategic)
            - Risk rating (none / low / medium / high)
            - Beyond-cost signals (SKU right-sizing, network hardening, policy gaps)
  Delivery: Interactive dashboard view + optional PDF export.

Tier 3 -- Deliverable Package
  Price   : CAD $1,499 per subscription engagement
  Access  : Unlocked after Stripe checkout. Trigger delivery agent.
  Scope   : Everything in Tier 2 plus a zip archive containing:
            - Terraform templates (Phase 2-ready) parameterized for this subscription
            - Bicep templates (Phase 1) for marco* sandbox wiring
            - PowerShell / Bash automation scripts with subscription-specific values
            - Implementation guide PDF with rollback instructions
  Delivery: 24-hour SAS URL to Azure Blob Storage download.
  Promise : No manual consultant hours. Fully automated generation.

=============================================================================
PRODUCT DIFFERENTIATORS
=============================================================================

1. Read-only, zero-touch access
   ACA never modifies resources. Read-only delegated consent or SP-based access.
   Clients can revoke at any time. All access is audited.

2. Consulting-grade output, SaaS-grade delivery
   Reports are authored in board language (managers, directors).
   Implementation guides are authored in practitioner language (the team).
   Both ship automatically from the same analysis run.

3. Three onboarding modes
   ACA is a standalone private-sector SaaS. It is NOT tied to any specific
   Microsoft Entra organization. The ACA app registration uses
   authority=https://login.microsoftonline.com/common (multi-tenant).
   Any client with a Microsoft account from any tenant can sign in.
   What matters is that their delegated token has Reader + Cost Management Reader
   on the CLIENT's Azure subscription -- not any ACA organization membership.

   Mode A: Delegated sign-in via Microsoft, any tenant (quick scan, trial-friendly)
   Mode B: Service principal provided by client (enterprise governance-friendly)
   Mode C: Azure Lighthouse delegation (MSP-grade, multi-subscription)

4. 12+1 analysis rules from real production data
   All 12 heuristics are seeded from real spending patterns in
   C:\AICOE\eva-foundry\14-az-finops -- not generic advice.

5. Privacy-first telemetry
   GA4 (via GTM) and Microsoft Clarity track product events only.
   No Azure identifiers, no resource names, no costs are sent to analytics.
   Full consent banner (GDPR/PIPEDA/LGPD-compatible).

6. Accessible and multilingual by design
   WCAG 2.1 AA accessibility from sprint 1.
   i18n from sprint 1. No bolted-on translation.

=============================================================================
ARCHITECTURE
=============================================================================

Internet Browser
    |
    v
[ Next.js / React 19 / Fluent UI v9 / i18next / Vite ]
    |   (HTTPS + Entra ID OIDC -- any Microsoft tenant, multi-tenant app registration)
    v
[ Azure API Management (APIM) ]
    |   - Subscription key throttling
    |   - Entitlement caching (60s per subscriptionId)
    |   - Tier enforcement at the gateway
    v
[ API Service -- FastAPI / Python 3.12 -- Azure Container App ]
    |   - Auth: MSAL delegated + managed identity
    |   - 6 router groups: health, auth, scans, findings, checkout, admin
    |   - Tenant isolation enforced: every DB call uses partition_key=subscriptionId
    +----> [ Cosmos DB NoSQL ] -- 9 containers (see Containers section)
    |
    +----> [ Collector Job -- ACA Job -- Azure Container App Job ]
    |          - Azure Resource Graph (inventory)
    |          - Cost Management Query API (91 days daily)
    |          - Azure Advisor API
    |          - Azure Policy Insights
    |          - Network topology (ARM read)
    |
    +----> [ Analysis Service -- ACA Job -- Azure Container App Job ]
    |          - 12 heuristic rules engine (see Rules section)
    |          - FindingsAssembler -> Cosmos findings container
    |          - (Future) 29-foundry AI agents for narrative generation
    |
    +----> [ Delivery Service -- ACA Job -- Azure Container App Job ]
    |          - Jinja2 IaC template parametrization (12 templates)
    |          - ZIP + SHA-256 + Azure Blob Storage
    |          - 24h SAS URL returned
    |
    +----> [ Stripe ]  -- checkout + webhook lifecycle
    +----> [ GTM / GA4 / Microsoft Clarity ]  -- product telemetry (consent-gated)

=============================================================================
COSMOS DB CONTAINERS
=============================================================================

Container              Partition Key        Purpose
---------------------  -------------------  ----------------------------------
scans                  /subscriptionId      Scan lifecycle (status, stats, error)
inventories            /subscriptionId      Resource inventory snapshots
cost-data              /subscriptionId      Daily cost rows (91 days)
advisor                /subscriptionId      Advisor recommendations
findings               /subscriptionId      Analysis output (tiered view)
clients                /subscriptionId      Client record + tier assignment
deliverables           /subscriptionId      Delivery artifact record + SAS URL
entitlements           /subscriptionId      Tier unlock grants
payments               /subscriptionId      Stripe payment records
stripe_customer_map    /stripeCustomerId    Reverse-lookup: Stripe -> subscriptionId
admin_audit_events     /subscriptionId      Admin action audit trail (grant/lock/reconcile)

RULE: Every read/write on tenant data -- MUST pass partition_key=subscriptionId.
      No cross-tenant queries ever. No SELECT * without partition filter.

admin_audit_events document schema (doc id: aae::<uuid>):
  actor.userId, actor.upn, actor.roles[]
  action: ENTITLEMENT_GRANTED | SUBSCRIPTION_LOCKED | STRIPE_RECONCILE | ...
  target: { type, id }
  request: action-specific payload
  result: { status, message }
  correlationId, utc, ip (optional), userAgent (optional)

=============================================================================
FRONTEND -- SPARK ARCHITECTURE (docs 22-23)
=============================================================================

Routing pattern: /app/* (customer surface) + /admin/* (admin surface)
Framework: React 19 + Vite + Fluent UI v9 + react-router-dom v6
Auth guards: RequireAuth (all authed routes), RequireRole (admin routes)

Customer Surface (/app/*)
  Route                          Component                  Notes
  -----------------------------  -------------------------  ------------------
  /                              LoginPage                  Entra ID OIDC entry
  /app/connect                   ConnectSubscriptionPage    Mode A/B/C choice
  /app/status/:subscriptionId    CollectionStatusPage       Live polling, steps
  /app/findings/:subscriptionId  FindingsTier1Page          Tier 1 + upgrade CTA
  /app/upgrade/:subscriptionId   UpgradePage                Tier 2 vs Tier 3 CTA

Admin Surface (/admin/*) -- roles required: ACA_Admin | ACA_Support | ACA_FinOps
  Route                  Component               Notes
  ---------------------  ----------------------  -------------------------------
  /admin/dashboard       AdminDashboardPage      MRR, active subs, scans/day
  /admin/customers       AdminCustomersPage      Search, tier, lock/unlock
  /admin/billing         AdminBillingPage        Stripe health, reconcile job
  /admin/runs            AdminRunsPage           Scan/analysis/delivery history
  /admin/controls        AdminControlsPage       Grant tier, rate-limit overrides,
                                                  feature flags, incident banner

Global Components
  ConsentBanner          global                  GDPR/PIPEDA/LGPD
  LanguageSelector       in CustomerLayout nav

=============================================================================
ADMIN ROLE MODEL (doc 21)
=============================================================================

Role          Permissions
------------  ----------------------------------------------------------------
ACA_Admin     Full access: grant tier, lock/unlock, reconcile, rerun jobs,
              rate-limit overrides, feature flags
ACA_Support   Read + grant trial + lock/unlock (no feature flags, no reconcile)
ACA_FinOps    Read-only: billing KPIs, usage stats, Stripe health

Admin roles sourced from Entra ID groups.
Destructive actions (grant/lock/reconcile) require confirmation modal.
Every admin action writes an admin_audit_events Cosmos record.

=============================================================================
FRONTEND -- API CLIENTS (doc 22)
=============================================================================

Customer API client (appApi.ts):
  GET  /v1/reports/tier1?subscriptionId=  -- Tier 1 report
  POST /v1/collect/start                  -- trigger collection
  GET  /v1/collect/status?subscriptionId= -- poll collection progress
  POST /v1/billing/checkout               -- Stripe checkout (tier2/tier3)
  GET  /v1/billing/portal                 -- Stripe billing portal URL
  GET  /v1/entitlements?subscriptionId=   -- check current entitlement tier

Admin API client (adminApi.ts):
  GET  /v1/admin/kpis                               -- MRR, subs, scans/day
  GET  /v1/admin/customers?query=                   -- search customers
  POST /v1/admin/entitlements/grant                 -- grant tier N for D days
  POST /v1/admin/subscriptions/:id/lock             -- lock subscription
  POST /v1/admin/stripe/reconcile                   -- repair missed webhooks
  GET  /v1/admin/runs?type=scan|analysis|delivery   -- job history

=============================================================================
i18n AND CURRENCY
=============================================================================

Supported locales (sprint 1):
  en     -- English (Canada/US default)
  fr     -- French (Canada, fr-CA)    [Phase 1 -- complete before M2.1]
  pt-BR  -- Portuguese (Brazil)        [Phase 1 -- best-effort machine translation]
  es     -- Spanish (Latin America)    [Phase 1 -- best-effort machine translation]
  de     -- German                     [Phase 1 -- best-effort machine translation]

Note: all 5 locales are live in Phase 1 with best-effort machine translation.
Professional review for pt-BR / es / de is a Phase 2 hardening item.

i18n library: i18next + react-i18next
Translation source: /frontend/src/i18n/locales/{locale}/*.json
RTL: not required for these locales but layout must not hardcode LTR

Currency display (Stripe checkout + findings report):
  CAD    -- Canadian Dollar (default)
  USD    -- US Dollar
  BRL    -- Brazilian Real
  EUR    -- Euro (DE/ES)
  GBP    -- British Pound (future)

Currency is display-only. Stripe checkout currency is CAD by default.
Client can see estimated savings figures in their preferred currency
using a stored FX rate refreshed daily from an open FX API.

=============================================================================
ACCESSIBILITY
=============================================================================

Target: WCAG 2.1 Level AA throughout.

Requirements:
- All interactive elements keyboard-accessible (no mouse-only interactions)
- Colour contrast ratio >= 4.5:1 for normal text, 3:1 for large text
- Screen reader labels on all icons, charts, status indicators
- Focus visible on all focusable elements
- Skip-to-content link on every page
- No content flashing > 3Hz
- Error messages programmatically associated with form fields
- All data tables have proper <th> scope attributes
- PDF reports generated with tagged PDF (a11y-aware export)
- Automated: axe-core in CI (zero critical/serious violations gate)
- Manual: keyboard-only walkthrough before each milestone sign-off

Fluent UI v9 components are used because they ship ARIA attributes by default.
Any custom component must include a WCAG audit before merge.

=============================================================================
THIRD-PARTY INTEGRATIONS
=============================================================================

Stripe
  Purpose : Payment processing -- Tier 2 and Tier 3 checkout
  SDK     : stripe-python (backend), Stripe.js + Elements (frontend)
  Events  : checkout.session.completed, invoice.paid,
            customer.subscription.updated, customer.subscription.deleted
  Webhook : POST /v1/webhooks/stripe -- signed with whsec_... secret
  Pattern : Entitlement written to Cosmos on confirmed payment.
            Delivery job triggered on Tier 3 payment confirmed.
  Billing : Tier 2 = monthly subscription (CAD). Prices are env-var driven --
            not hardcoded. set STRIPE_PRICE_* env vars before launch.
  Coupons : Promotion codes supported at checkout (allow_promotion_codes=true).
            Use STRIPE_COUPON_ENABLED=true to enable (default: true).
            Full fee waiver via coupon is supported for trials and partnerships.

Google Analytics 4 (GA4)
  Purpose : Product usage funnels, conversion tracking, A/B event data
  Account : Existing GA4 account (marco)
  Deploy  : Via Google Tag Manager (GTM) -- no direct SDK in bundle
  Events  : login_success, preflight_pass, preflight_fail, scan_started,
            scan_completed, analysis_completed, unlock_cta_clicked,
            checkout_started, checkout_completed, deliverable_downloaded
  Privacy : Consent-gated. No Azure identifiers. Only opaque ACA IDs.

Microsoft Clarity
  Purpose : Session replay + heatmaps for UX improvement
  Account : Existing Clarity account (marco)
  Deploy  : Via GTM
  Events  : Key funnel drop-off events mirrored from GA4 via clarityEvent()
  Privacy : Consent-gated. Masking enabled for all form fields.

GTM (Google Tag Manager)
  Purpose : Single tag deployment point for GA4 + Clarity
  Deploy  : One GTM container script in index.html
  Consent : dataLayer "consent" event gates all tags until user accepts

Azure APIM
  Purpose : API gateway for ACA public API
  Phase 1 : marco-sandbox-apim (reuse)
  Phase 2 : Dedicated APIM instance in private subscription
  Policies: JWT validation, entitlement caching (60s), tier enforcement,
            token-budget enforcement (Ocp-Apim-Subscription-Key)

Azure Key Vault
  Purpose : All secrets -- Cosmos key, Stripe keys, MSAL secrets, APIM key
  Phase 1 : marcosandkv20260203
  Phase 2 : Dedicated KV in private subscription
  Access  : Managed Identity only. No secrets in env files in production.

=============================================================================
COLLECTION SCOPE (read-only)
=============================================================================

Category              API / Source                     Notes
--------------------  -------------------------------  ----------------------
Resource inventory    Azure Resource Graph             All types, tags, SKUs
Cost data             Cost Management Query API        91 days, daily rows
Advisor recs          Azure Advisor API                All categories
Policy state          Azure Policy Insights            Compliance summaries
Network topology      ARM read (NSG, DNS, VNet, PIPs)  Topology signals
Activity (optional)   Activity Logs (if LA enabled)    Idle detection

Roles required by client:
  Reader                   (subscription scope, mandatory)
  Cost Management Reader   (subscription scope, mandatory)
  Log Analytics Reader     (workspace scope, optional)
  Policy Insights Reader   (subscription scope, optional)

=============================================================================
ANALYSIS RULES
=============================================================================

ID    Name                         Est. Saving (CAD/yr)    Effort    Risk
----  ---------------------------  ----------------------  --------  ------
R-01  Dev Box auto-stop            $5,548 - $7,902         trivial   none
R-02  Log Analytics retention      custom                  trivial   none
R-03  Defender plan mismatch       $4,000 - $6,000         easy      low
R-04  Compute scheduling (HIGHEST) $33,764 - $48,088       easy      none
R-05  Anomaly detection            $156K+/incident         easy      varies
R-06  Stale environments           $33,000 - $63,000       easy      low
R-07  Search SKU right-size        custom                  medium    medium
R-08  ACR consolidation            custom                  medium    low
R-09  Private DNS sprawl           custom                  involved  medium
R-10  Savings plan coverage        12-20% of compute       involved  low
R-11  APIM token budget gap        risk-only (no saving)   involved  high
R-12  Chargeback tagging gap       15-25% behavioural      strategic low

Total modelled dev run-rate from marco* data: CAD $235K/yr
Typical client impact: 25-40% annual reduction with Tier 3 implementation.

=============================================================================
GO-LIVE PHASES
=============================================================================

Phase 1 -- marco* dev go-live (TARGET: 4 weeks from 2026-02-26)
  Infrastructure : Reuse marco* sandbox resources in EsDAICoE-Sandbox
                   (marco-sandbox-cosmos, marcosandkv20260203,
                    marco-sandbox-apim, marcosandacr20260203)
  URL            : Azure Container Apps free hostnames (*.{region}.azurecontainerapps.io)
                   No custom domain required for Phase 1.
                   PUBLIC_APP_URL and PUBLIC_API_URL are read from env vars.
  Scope          : Internal-use, dogfood on marco* own subscription
  Goal           : Prove the full pipeline end-to-end (collect -> analyze ->
                   display -> tier-gate -> checkout -> deliver)
  Auth           : Multi-tenant Microsoft Entra (any client tenant). ACA app
                   registration authority=common. No EsDAICoE membership required.

Phase 2 -- Commercial MVP go-live (TARGET: 10 weeks from 2026-02-26)
  Infrastructure : Dedicated private Azure subscription
                   (Terraform-provisioned: ACA-specific Cosmos, APIM, KV,
                    Container Apps env, Storage, App Insights, ACR)
  Scope          : First 10 external paying clients
  Domain         : Custom domain (TBD -- real DNS + TLS, Phase 2 only)
  Compliance     : PIPEDA (Canada), GDPR (EU clients), LGPD (BR clients)
  Support        : Intercom or similar, help docs in 5 locales

=============================================================================
LOCAL DEVELOPMENT
=============================================================================

Prerequisites:
  - Python 3.12   (C:\AICOE\.venv)
  - Node 22+      (for frontend)
  - Docker Desktop (for docker-compose local stack)
  - az CLI        (logged in to EsDAICoE-Sandbox)

Quick start:
  1. Copy .env.example -> .env and fill all values from marco-kv secrets
  2. docker-compose up               # starts api (8080), frontend (5173), cosmos-emulator (8081)
  3. python -m pytest services/ -x   # all service tests
  4. cd frontend && npm run dev       # Vite dev server

Data model (local port 8011):
  pwsh C:\AICOE\eva-foundry\51-ACA\data-model\start.ps1

=============================================================================
PROJECT FILES MAP
=============================================================================

51-ACA/
  README.md             -- this file
  PLAN.md               -- WBS: epics, features, milestones, risks
  STATUS.md             -- current sprint state and blockers
  ACCEPTANCE.md         -- acceptance gates for Phase 1 and Phase 2
  01-feasibility.md     -- auth pattern analysis (delegated/SP/Lighthouse)
  02-preflight.md       -- onboarding + permission validation spec
  03-aca-documentation.md -- client access guide + preflight acceptance gates
  04-security.md        -- security and data handling policy
  05-technical.md       -- API spec + FastAPI skeleton
  06-integration.md     -- GA4 + Clarity analytics spec + event taxonomy
  07-react.md           -- React telemetry stubs (consent, GTM, Clarity)
  08-payment.md         -- Stripe backend stubs (checkout, webhook, portal)
  09-hardening-MVP.md   -- Cosmos-backed entitlement service + recurring billing
  10-recurrent-clients.md -- StripeCustomerMap + subscription lifecycle
  11-caching.md         -- APIM caching patterns (entitlements, preflight)
  12-IaCscript.md       -- AZ CLI bootstrap script v1 (Phase 1 + Phase 2)
  13-IAC-more.md        -- AZ CLI bootstrap script v2 (adds Container Apps Jobs,
                           APIM optional, UAMI+KV RBAC, DO_CONTAINERAPPS/DO_APIM flags)
  14-analytcs.md        -- GA4+Clarity analytics spec (duplicate of 06 -- more detail)
  15-frontend.md        -- React telemetry stubs (duplicate of 07 -- more detail)
  16-stripe-backend.md  -- Stripe FastAPI full implementation (duplicate of 08 -- full)
  17-pahse2hardneing.md -- EntitlementService + PaymentsRepo + webhook lifecycle (full)
  18-customer-mapping.md -- StripeCustomerMapRepo full implementation
  19-apim-cache.md      -- APIM caching policy XML (entitlements 60s, preflight)
  20-iac-resources.md   -- Duplicate of 13-IAC-more.md
  21-managing-buz.md    -- Admin surface strategy: same-app /admin/* MVP rec
  22-spark-frontend.md  -- FULL Spark frontend: router, layouts, auth, page skeletons,
                           API clients, OpenAPI admin spec, admin_audit_events schema
  23-spark-prompt.md    -- Spark agent prompt: output file list, behavior requirements,
                           API path mapping, security/RBAC requirements
  data-model/           -- local EVA data model (WBS, epics, stories, layers)
  services/api/         -- FastAPI API service
  services/collector/   -- Azure data collector job
  services/analysis/    -- 12-rule analysis engine
  services/delivery/    -- IaC template packager
  frontend/             -- React 19 + Fluent UI v9 + i18next
  agents/               -- 4 AI agent YAML definitions
  infra/phase1-marco/   -- Bicep (marco* sandbox wiring)
  infra/phase2-private/ -- Terraform (full private subscription)
  .github/workflows/    -- CI, deploy-phase1, collector-schedule,
                           dpdca-agent.yml (DPDCA Cloud Agent workflow)

=============================================================================
AZURE BEST PRACTICES SERVICE CATALOG (18-azure-best integration)
=============================================================================

ACA's analysis engine and service endpoints are powered by the EVA Azure Best
Practices Library at C:\AICOE\eva-foundry\18-azure-best (32 modules, read-only).
Each ACA service offering maps to one or more library modules:

| ACA Endpoint / Service           | 18-azure-best Module                                    |
|----------------------------------|---------------------------------------------------------|
| WAF Assessment (GET /assessment) | 02-well-architected/waf-overview.md                     |
| Reliability pillar rules         | 05-resiliency/aprl.md (APRL checklist)                  |
| FinOps rules R-13 to R-17        | 08-finops/cost-optimization.md                          |
| Idle resource detection          | 08-finops/cost-optimization.md                          |
| RBAC hygiene check               | 12-security/rbac.md                                     |
| Key Vault audit (RBAC vs policy) | 12-security/key-vault.md                                |
| MCSB compliance check            | 12-security/mcsb.md                                     |
| APIM rate-limit policy check     | 03-architecture-center/apim.md                          |
| API design compliance            | 03-architecture-center/api-design.md                    |
| IaC quality gate (PSRule)        | 07-iac/bicep.md                                         |
| Tag enforcement in delivery      | 07-iac/bicep.md                                         |

All Epic 13 analysis rules must import from facts collected by the collector job
(Cosmos cosmos/inventories partition). Rules return a FINDING dict conforming to
the P2.5 Pattern 4 schema. Rules are unit-tested in services/analysis/tests/.

=============================================================================
DPDCA CLOUD AGENT WORKFLOW
=============================================================================

Spring backlog items are submitted as GitHub Issues and executed by the DPDCA
GitHub Actions pipeline automatically:

  1. Open GitHub Issue using template "DPDCA Sprint Backlog Item"
     (.github/ISSUE_TEMPLATE/agent-task.yml)
     Fill: Story ID (ACA-NN-NNN), WBS, Epic, FP Size, Inputs, Outputs, Acceptance

  2. Add label "agent-task" to the issue

  3. .github/workflows/dpdca-agent.yml fires:
     D1: parses issue, loads PLAN.md + copilot-instructions into context
     P:  gpt-4o-mini (GitHub Models API) generates agent-plan.md
     D2: creates branch agent/ACA-NN-NNN-TIMESTAMP, writes evidence receipt
     C:  ruff + pytest --co gate
     A:  commits with Story ID on subject, runs Veritas audit, opens PR

  4. Veritas confirms MTI did not regress before PR merge is allowed

  Model: gpt-4o-mini via models.inference.ai.azure.com (GitHub Models API)
  Fallback: Azure OpenAI marco-sandbox-openai-v2
