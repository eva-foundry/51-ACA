# ACA -- Solution Architecture

Version: 1.0.0
Updated: 2026-02-28
Status: Active
Audience: Executives, Product Managers, Solution Architects, Clients

---

## EXECUTIVE SUMMARY

Azure Cost Advisor (ACA) is a commercial SaaS application that automates Azure cost
optimization analysis and delivers actionable remediation guidance. The solution analyzes
Azure subscriptions using a combination of heuristic rules and AI-enhanced analysis to
identify cost savings opportunities worth an average of 15-30% of annual Azure spend.

**Target market**: Azure customers with monthly spend > $5,000 CAD
**Business model**: Freemium SaaS (Tier 1 free, Tier 2/3 subscription)
**Delivery model**: Multi-tenant cloud service (Azure Container Apps)

---

## BUSINESS PROBLEM

Azure customers face three persistent challenges in cost optimization:

1. **Visibility Gap**: Native tools (Cost Management, Advisor) provide data but not
   actionable insights. Users see costs but don't know WHERE to optimize.

2. **Expertise Barrier**: Optimization requires deep Azure knowledge. Most teams lack
   dedicated FinOps expertise to translate recommendations into safe IaC changes.

3. **Implementation Friction**: Advisor recommendations are generic. Translating them
   into deployable scripts (Bicep/Terraform) requires hours of manual work per finding.

**Customer pain point**: "Azure Advisor tells me I have $50k/year in savings, but I
don't know which changes are safe, how to prioritize them, or how to deploy them
without breaking my production systems."

---

## SOLUTION POSITIONING

ACA bridges the gap between Cost Management data and deployed optimizations.

**Value proposition:**
- **Tier 1 (Free)**: Executive summary report -- total estimated savings, high-level
  opportunity categories, effort classification. Drives awareness.
- **Tier 2 (Paid)**: Detailed findings with AI-enhanced narratives, resource-specific
  recommendations, risk/effort scoring. Enables informed decision-making.
- **Tier 3 (Premium)**: Ready-to-deploy IaC templates (Bicep + Terraform), step-by-step
  implementation guides, safety validation via redteam agent. Eliminates implementation friction.

**Competitive differentiation:**
- No manual data upload (delegated Azure auth, automatic collection)
- AI-enhanced analysis (GPT-4o enrichment, context-aware narratives)
- Actionable deliverables (not just recommendations -- actual runnable scripts)
- Safety-first approach (redteam agent validates all changes)
- Multi-tenant SaaS (no self-hosting, instant onboarding)

---

## SYSTEM CONTEXT DIAGRAM

```
                                    ┌──────────────────┐
                                    │  User (Customer) │
                                    │  Azure Tenant    │
                                    └────────┬─────────┘
                                             │
                                             │ 1. OIDC Login
                                             │ 2. Delegate Azure Auth
                                             v
┌────────────────────────────────────────────────────────────────┐
│                       ACA SaaS Platform                        │
│                                                                │
│  ┌─────────────┐     ┌──────────────┐     ┌────────────────┐ │
│  │  Frontend   │────>│  API Service │────>│  Cosmos DB     │ │
│  │  (React)    │<────│  (FastAPI)   │<────│  (NoSQL)       │ │
│  └─────────────┘     └──────┬───────┘     └────────────────┘ │
│                              │                                │
│                              │ Orchestrate Jobs               │
│                              v                                │
│  ┌──────────────┬─────────────────┬─────────────────┐        │
│  │  Collector   │   Analysis      │   Delivery      │        │
│  │  (Azure SDK) │   (Rules + AI)  │   (IaC Gen)     │        │
│  └──────┬───────┴─────────┬───────┴────────┬────────┘        │
│         │                 │                │                 │
└─────────┼─────────────────┼────────────────┼─────────────────┘
          │                 │                │
          v                 v                v
┌───────────────────┐  ┌──────────────┐  ┌──────────────┐
│  Customer Azure   │  │  Azure       │  │  Blob        │
│  Subscription     │  │  OpenAI      │  │  Storage     │
│  (Read-Only)      │  │  (GPT-4o)    │  │  (IaC Zip)   │
└───────────────────┘  └──────────────┘  └──────────────┘
```

**External integrations:**
- Azure Resource Management (ARM) -- inventory collection
- Azure Cost Management -- 90-day billing data
- Azure Advisor -- native recommendations (enriched)
- Azure OpenAI -- GPT-4o for narrative generation
- Stripe -- payment processing (Tier 2/3 checkout)
- Entra ID (Microsoft Identity) -- authentication

---

## ARCHITECTURE PRINCIPLES

### 1. Tenant Isolation by Design
Every data operation scoped to subscriptionId (Cosmos partition key). No code path can
query cross-tenant data. Authentication tokens validated on every request.

### 2. Least Privilege Access
ACA requires ONLY Reader role on customer subscriptions. No write permissions, no
resource modifications. Collection is read-only by design.

### 3. Fail-Safe Defaults
All generated IaC templates are reviewed by redteam agent before delivery. Changes
flagged as high-risk (data loss, downtime) are rejected. Tier 3 deliverables include
rollback scripts.

### 4. Graceful Degradation
If Azure OpenAI unavailable, analysis still produces findings (heuristic-only, no
narrative). If Cost Management times out, analysis proceeds with available data
(warnings noted).

### 5. Stateless Services
All state in Cosmos. API and job services are ephemeral (no local cache). Enables
horizontal scaling and zero-downtime deployments.

### 6. Evidence-First Development
Every feature tracked via story ID (ACA-NN-NNN). Every commit tagged with EVA-STORY.
Evidence receipts capture agent execution metrics. Veritas MTI score gates deployment.

---

## TIER MODEL (PRICING TIERS)

### Tier 1: Free Report (Marketing Funnel)

**What customer gets:**
- One-page executive summary
- Total estimated savings (low/high range)
- Breakdown by opportunity category (compute, storage, network, etc.)
- Effort classification (trivial, easy, medium, involved, strategic)
- High-level finding titles (no implementation details)

**Purpose**: Drive awareness, demonstrate value, convert to Tier 2

**Limitations:**
- No detailed narratives (what/why/how redacted)
- No resource-specific recommendations
- No IaC deliverables
- Findings refresh: manual trigger only (no auto-refresh)

**Example finding (Tier 1):**
```
Title: Dev Box instances run nights and weekends
Category: Compute Scheduling
Estimated Savings: $5,548 - $7,902 CAD/year
Effort: Trivial
[Upgrade to Tier 2 to see detailed recommendations]
```

---

### Tier 2: Detailed Analysis ($199 CAD/month or $1,990 CAD/year)

**What customer gets:**
- All Tier 1 content PLUS:
- Detailed findings narratives (AI-enhanced)
  - WHAT: specific resources affected
  - WHY: business/technical justification
  - HOW: high-level implementation approach
- Risk classification (none, low, medium, high)
- Resource-level detail (SKU, region, tags)
- Effort estimates (hours, FTE impact)
- Savings confidence score
- Nightly auto-refresh (findings updated as inventory changes)

**Purpose**: Enable informed decision-making, prioritization

**Limitations:**
- No ready-to-deploy IaC templates
- Customer must implement manually
- No step-by-step guides

**Example finding (Tier 2):**
```
Title: Dev Box instances run nights and weekends
Category: Compute Scheduling
Estimated Savings: $5,548 - $7,902 CAD/year
Effort: Trivial (2 hours)
Risk: None (safe auto-stop settings)

NARRATIVE:
Your subscription has 12 Dev Box instances running 24/7 in canadacentral.
Analysis of 90-day cost data shows these instances are idle 68% of the time
(weeknights 6pm-8am, weekends). Implementing auto-stop schedules (stop at
6pm, start at 8am weekdays) would save approximately $6,725/year with no
impact to developer workflows.

AFFECTED RESOURCES:
- devbox-frontend-01 (Standard_D4s_v5) -- $412/month current
- devbox-backend-02 (Standard_D4s_v5) -- $412/month current
... (10 more)

IMPLEMENTATION APPROACH:
Azure Dev Box supports native scheduling. Configure auto-stop via Azure Portal
or REST API. No downtime required. Changes reversible within 5 minutes.

RISK ASSESSMENT:
None. Auto-stop schedules are non-destructive. VMs retain state. Developers can
manually override schedules if needed for on-call work.
```

---

### Tier 3: IaC Deliverables ($499 CAD/month or $4,990 CAD/year)

**What customer gets:**
- All Tier 1 + Tier 2 content PLUS:
- Ready-to-deploy IaC templates (Bicep AND Terraform)
- Parameterized for specific subscription/resources
- Step-by-step implementation guides (per finding)
- Rollback scripts (safety net)
- Redteam agent validation report (safety check)
- SHA-256 signed manifest (tamper detection)
- 7-day SAS URL download link

**Purpose**: Eliminate implementation friction, enable rapid deployment

**Deliverable package structure:**
```
aca-deliverables-{subscription_id}-{timestamp}.zip
  manifest.json           -- SHA-256 checksums for verification
  README.md               -- Prerequisites, execution order, support contacts
  findings.json           -- Full findings array (unfiltered)
  scripts/
    bicep/
      rule-01-dev-box-autostop.bicep
      rule-01-dev-box-autostop.bicepparam
      rule-02-vm-rightsizing.bicep
      ... (one per finding)
    terraform/
      rule-01-dev-box-autostop.tf
      rule-01-dev-box-autostop.tfvars
      ... (one per finding)
  docs/
    rule-01-implementation-guide.md
    rule-02-implementation-guide.md
    ... (one per finding)
  rollback/
    rule-01-rollback.bicep
    ... (one per finding)
```

**Example IaC template (Tier 3, Bicep snippet):**
```bicep
// rule-01-dev-box-autostop.bicep
// AUTO-GENERATED by ACA Tier 3 Delivery Service
// Subscription: abc123, Generated: 2026-02-28T08:15:00Z

targetScope = 'subscription'

param devBoxInstances array = [
  'devbox-frontend-01'
  'devbox-backend-02'
  // ... (all 12 instances)
]

param autoStopTime string = '18:00'  // 6pm
param autoStartTime string = '08:00' // 8am
param timeZone string = 'Eastern Standard Time'

resource devBoxSchedule 'Microsoft.DevCenter/devcenters/schedules@2023-04-01' = [for instance in devBoxInstances: {
  name: '${instance}-autostop'
  properties: {
    stopTime: autoStopTime
    startTime: autoStartTime
    timeZone: timeZone
    frequency: 'Daily'
    state: 'Enabled'
  }
}]
```

**Safety validation (redteam agent report):**
Each deliverable includes a `redteam-report.json`:
```json
{
  "finding_id": "rule-01-dev-box-autostop",
  "validation_status": "PASS",
  "checks": [
    {"check": "no_data_loss", "result": "PASS", "note": "Auto-stop preserves VM state"},
    {"check": "no_downtime", "result": "PASS", "note": "Schedules apply outside work hours"},
    {"check": "reversible", "result": "PASS", "note": "Schedules can be disabled in <5 min"},
    {"check": "no_cost_increase", "result": "PASS", "note": "Only reduces costs, no new charges"}
  ],
  "overall_risk": "none",
  "deployment_recommendation": "Safe to deploy. Recommend staging test on 1-2 Dev Boxes first."
}
```

---

## END-TO-END USER FLOWS

### Flow 1: New Customer Onboarding (Tier 1 Free)

```
1. User lands on aca.example.com
   -> Marketing page: "See how much you can save on Azure"
   -> CTA: "Get Your Free Report"

2. User clicks "Get Free Report"
   -> Redirect to /login
   -> Sign in with Microsoft (Entra OIDC)

3. User authenticates
   -> Redirect to /connect
   -> "Connect your Azure subscription"
   -> Azure OAuth consent screen (Reader role requested)

4. User grants consent
   -> API receives delegated auth token
   -> POST /v1/scans (trigger collection job)
   -> Redirect to /status

5. Collection job runs (3-5 minutes typical)
   -> Frontend polls GET /v1/scans/:id every 5 seconds
   -> Status page shows progress: "Collecting inventory... Analyzing costs... Running analysis..."

6. Analysis completes
   -> Status page redirects to /findings
   -> Tier 1 gated view: titles + savings only
   -> Bottom CTA: "Unlock detailed analysis -- $199/month"

7. User sees Tier 1 report
   -> "You have 18 optimization opportunities"
   -> "Est. savings: $42,300 - $58,900 CAD/year"
   -> Breakdown: Compute (8), Storage (5), Network (3), Database (2)
   -> Effort: Trivial (4), Easy (7), Medium (5), Involved (2)

8. User clicks "Upgrade to Tier 2"
   -> POST /v1/checkout/session (Stripe)
   -> Redirect to Stripe checkout
   -> Payment form: $199 CAD/month or $1,990/year

9. User completes payment
   -> Stripe webhook -> API updates entitlements
   -> Redirect to /findings
   -> Tier 2 unlocked: full narratives now visible
```

---

### Flow 2: Tier 2 Customer Reviews Findings

```
1. User logs into /findings (Tier 2 active)
   -> Sees full list of 18 findings with detailed narratives

2. User filters by effort "Trivial"
   -> 4 findings shown
   -> Clicks first finding: "Dev Box auto-stop"

3. Finding detail panel opens
   -> Full narrative visible
   -> Affected resources list (12 Dev Boxes)
   -> Risk: None, Effort: 2 hours
   -> Estimated savings: $6,725/year

4. User thinks: "I need the deployment script"
   -> Bottom CTA: "Get IaC templates -- Upgrade to Tier 3"
   -> Clicks "Upgrade to Tier 3"

5. Stripe checkout ($499/month or $4,990/year)
   -> User completes payment
   -> Entitlements updated to tier3

6. User returns to /findings
   -> New button visible: "Download Deliverables"
   -> Clicks download button

7. POST /v1/delivery/package
   -> Delivery job generates IaC templates (30-60 seconds)
   -> Returns SAS URL
   -> Frontend redirects to blob storage
   -> Browser downloads aca-deliverables-abc123-20260228.zip

8. User extracts zip locally
   -> Runs: az deployment sub create --template-file scripts/bicep/rule-01-dev-box-autostop.bicep --parameters @rule-01-dev-box-autostop.bicepparam
   -> Auto-stop schedules deployed to 12 Dev Boxes
   -> Next month: $412/month savings confirmed in Azure Cost Management
```

---

### Flow 3: Nightly Auto-Refresh (Tier 2+)

```
1. Cron job triggers at 02:00 UTC (GitHub Actions: collector-schedule.yml)
   -> Runs for ALL Tier 2+ subscriptions (entitlements.tier >= tier2)

2. For each subscription:
   -> POST /v1/scans (collector job)
   -> Collection runs (inventory + cost data refresh)
   -> Analysis runs (findings recalculated)

3. If NEW findings detected (delta from previous run):
   -> Email notification sent to customer
   -> Subject: "ACA: New cost optimization opportunities detected"
   -> Body: "We found 3 new optimization opportunities worth $2,400/year. Log in to review."

4. If savings INCREASED on existing findings:
   -> Email notification
   -> "Your Dev Box auto-stop opportunity increased from $6,725 to $7,200/year due to usage pattern changes."

5. If resources REMOVED (e.g. Dev Boxes deleted):
   -> Finding archived
   -> Email: "Good news: 2 opportunities resolved (resources no longer exist)."
```

---

## SCALABILITY AND PERFORMANCE

### Phase 1 Targets (marco* resources)

**Concurrent users:** 50
**Concurrent scans:** 10
**Scan execution time:** p95 < 5 minutes (for subscriptions with <500 resources)
**API response time:** p95 < 300ms (GET /v1/findings)
**Uptime SLA:** 95% (best-effort, no formal SLA)

**Resource quotas:**
- Cosmos: 400 RU/s (shared, no autoscale)
- API: 0-10 Container App instances (autoscale on CPU)
- Jobs: Manual concurrency limit (no queue, sequential execution)
- Storage: 100 GB blob quota

**Estimated max capacity:**
- 100 active subscriptions
- 10 scans per day
- 1,000 findings total across all tenants

---

### Phase 2 Targets (private subscription)

**Concurrent users:** 500
**Concurrent scans:** 50
**Scan execution time:** p95 < 3 minutes (optimized Resource Graph queries)
**API response time:** p95 < 100ms (Cosmos autoscale)
**Uptime SLA:** 99.9% (formal SLA, Azure Front Door + multi-region)

**Resource quotas:**
- Cosmos: 4,000 RU/s autoscale (burst to 20,000)
- API: 1-50 Container App instances (CPU + memory autoscale)
- Jobs: Azure Service Bus queue (1,000 concurrent jobs)
- Storage: 1 TB blob quota, lifecycle policies (archive after 30 days)

**Estimated max capacity:**
- 10,000 active subscriptions
- 500 scans per day
- 100,000 findings total

**Growth plan:**
- Phase 1: Proof of concept (Q1 2026, 10-50 customers)
- Phase 2: Commercial launch (Q2 2026, 50-500 customers)
- Phase 3: Enterprise (Q3 2026, 500-5,000 customers, multi-region deployment)

---

## DATA RESIDENCY AND COMPLIANCE

### Data Classification

**Customer Azure metadata (Tier 1 / Collection):**
- Resource inventory (ARM resource IDs, SKUs, locations)
- Cost data (aggregated, no PII, no sensitive workload data)
- Azure Advisor recommendations (native Microsoft data)
- Classification: INTERNAL (no customer workload data collected)

**ACA analysis outputs (Tier 2 / Findings):**
- AI-generated narratives (based on metadata only)
- Estimated savings calculations (heuristic + ML model)
- Risk/effort classifications
- Classification: INTERNAL (derived insights, no regulated data)

**IaC templates (Tier 3 / Deliverables):**
- Parameterized Bicep/Terraform (resource IDs, SKUs)
- No secrets, no connection strings, no PII
- Classification: INTERNAL

### Compliance Posture

**Phase 1 (Proof of Concept):**
- Data residency: Canada Central (Azure region)
- Encryption: At-rest (Cosmos default), in-transit (TLS 1.2+)
- Identity: Entra ID + MSAL (Microsoft native, no custom auth)
- Logging: Application Insights (30-day retention)
- Backup: Cosmos continuous backup (7-day PITR)
- Certifications: NONE (proof-of-concept status)

**Phase 2 (Commercial Launch):**
- Data residency: Customer choice (Canada, US, EU)
- Encryption: Customer-managed keys (Key Vault)
- Identity: Same (Entra ID)
- Logging: 90-day retention, Log Analytics export
- Backup: 35-day PITR
- Certifications: SOC 2 Type II (target Q3 2026)

**GDPR / Privacy:**
- No PII collected (email stored for billing only, Stripe manages)
- Data deletion: Customer can delete subscription -> all data purged within 30 days
- Data export: Customer can request findings.json export (Tier 2+)
- Right to be forgotten: Implemented via cascading Cosmos delete

---

## SECURITY MODEL

### Threat Model Summary (see security-architecture.md for details)

**Trust boundaries:**
1. Internet -> Frontend (public, authenticated)
2. Frontend -> API (authenticated, HTTPS only)
3. API -> Cosmos (managed identity, no connection strings)
4. API -> Azure (delegated auth token, read-only)
5. API -> Stripe (webhook signature verification)

**Key threats mitigated:**
- **Cross-tenant data leak**: Cosmos partition key enforcement
- **Auth bypass**: MSAL token validation on every request
- **API abuse**: Rate limiting (10 requests/sec per subscription)
- **Payment fraud**: Stripe webhook signature validation
- **Malicious IaC**: Redteam agent pre-validates all templates (Tier 3)

**Attack surface reduction:**
- No customer secrets stored (delegated auth tokens only, refresh token in Key Vault)
- No write permissions on customer Azure (Reader role only)
- No user-generated code execution (templates parameterized, not user-provided)
- No admin panel (admin operations via API with bearer token, no web UI)

---

## DISASTER RECOVERY

### RTO / RPO Targets

**Phase 1 (Proof of Concept):**
- RTO: 24 hours (manual recovery, best-effort)
- RPO: 24 hours (Cosmos continuous backup, 7-day PITR)

**Phase 2 (Commercial):**
- RTO: 4 hours (automated recovery, runbooks)
- RPO: 1 hour (Cosmos continuous backup, 35-day PITR)

### Backup Strategy

**Cosmos DB:**
- Continuous backup enabled (automatic, no manual snapshots)
- PITR restore available via Azure Portal or CLI
- Cross-region replica for Phase 2 (read-only)

**Blob Storage (IaC deliverables):**
- Lifecycle policy: move to Cool tier after 7 days, Archive after 30 days
- No backup (regenerable from findings data)

**Key Vault secrets:**
- Soft-delete enabled (90-day retention)
- Purge protection enabled (cannot be permanently deleted for 90 days)

### Incident Response

**Severity 1 (Service Down):**
- Pager: On-call engineer (PagerDuty integration planned Phase 2)
- Response time: 30 minutes
- Communication: Status page + email to all Tier 2+ customers

**Severity 2 (Degraded Performance):**
- Response time: 2 hours
- Communication: Status page only

**Severity 3 (Non-critical bug):**
- Response time: Next business day
- Communication: GitHub issue + CHANGELOG.md entry

---

## ROADMAP AND EVOLUTION

### Phase 1 (Q1 2026) -- Proof of Concept [COMPLETED]
- [x] Core collection + analysis pipeline
- [x] Tier 1/2/3 gating
- [x] Stripe integration
- [x] 12 optimization rules
- [x] AI narrative generation (GPT-4o)
- [x] Redteam agent validation
- [x] IaC template library (Bicep + Terraform)
- [x] 24 passing tests, MTI 100
- [x] Full ADO integration (257 stories)

### Phase 2 (Q2 2026) -- Commercial Launch [IN PLANNING]
- [ ] Private Azure subscription (Terraform provisioning)
- [ ] Custom domain (aca.example.com)
- [ ] Azure Front Door (CDN + WAF)
- [ ] Multi-region deployment (Canada + US)
- [ ] Service Bus job queue (scale to 50 concurrent scans)
- [ ] Cosmos autoscale (4,000 RU/s)
- [ ] SOC 2 Type II audit prep
- [ ] Customer-managed keys
- [ ] Advanced RBAC (team collaboration features)

### Phase 3 (Q3 2026) -- Enterprise Features [PLANNED]
- [ ] Multi-subscription rollup (org-level view)
- [ ] Custom rule builder (bring-your-own-logic)
- [ ] Slack/Teams notifications
- [ ] API key access (programmatic integration)
- [ ] Terraform Cloud integration (auto-apply findings)
- [ ] Azure DevOps pipeline integration
- [ ] SSO (SAML, Okta, Azure AD B2C)

### Phase 4 (Q4 2026) -- Multi-Cloud [VISION]
- [ ] AWS support (Cost Explorer + Compute Optimizer integration)
- [ ] GCP support (Billing + Recommender API)
- [ ] Cross-cloud optimization (workload placement recommendations)

---

## DECISION LOG

### ADL-001: Cosmos NoSQL over SQL
**Date:** 2026-01-15
**Decision:** Use Cosmos DB NoSQL API (partition key = subscriptionId) over Azure SQL
**Rationale:** Horizontal scaling, natural tenant isolation, JSON schema flexibility
**Alternatives considered:** Azure SQL (RBAC per subscription), PostgreSQL Flexible Server
**Status:** ACCEPTED

### ADL-002: FastAPI over Flask
**Date:** 2026-01-18
**Decision:** FastAPI with Pydantic for API service
**Rationale:** Async/await support, auto-generated OpenAPI docs, type safety
**Alternatives considered:** Flask + Marshmallow, Django REST Framework
**Status:** ACCEPTED

### ADL-003: React 19 + Fluent UI v9
**Date:** 2026-01-20
**Decision:** React 19 with Fluent UI v9 for frontend
**Rationale:** Align with 31-eva-faces patterns, Microsoft design system, accessibility
**Alternatives considered:** Vue 3 + PrimeVue, Angular 17 + Material
**Status:** ACCEPTED

### ADL-004: Tier 3 IaC generation (not manual)
**Date:** 2026-01-25
**Decision:** Auto-generate IaC templates via Jinja2 parameterization
**Rationale:** Scale to 100s of customers, consistent quality, redteam validation
**Alternatives considered:** Manual template writing per customer, customer self-service editor
**Status:** ACCEPTED

### ADL-005: Stripe over Azure Marketplace
**Date:** 2026-02-01
**Decision:** Stripe for payment processing (Phase 1), defer Azure Marketplace to Phase 2
**Rationale:** Faster integration, global payment support, webhook reliability
**Alternatives considered:** Azure Marketplace (co-sell requirement), PayPal
**Status:** ACCEPTED (revisit for Phase 2 Azure Marketplace listing)

### ADL-006: Phase 1 reuse marco* resources
**Date:** 2026-02-10
**Decision:** Reuse existing marco-sandbox-* resources (no new Azure spend)
**Rationale:** Proof-of-concept budget constraint, de-risk before Phase 2 investment
**Alternatives considered:** New sandbox subscription, Azure free tier
**Status:** ACCEPTED (Phase 2 will provision private resources)

### ADL-007: Story-level ADO PBIs (not feature-level)
**Date:** 2026-02-28
**Decision:** Import every ACA-NN-NNN story as individual PBI in ADO
**Rationale:** Enable granular velocity tracking, agent comment posting per story
**Alternatives considered:** Feature-level aggregation (loses granularity)
**Status:** ACCEPTED (256 story-level PBIs created)

---

## ASSUMPTIONS AND CONSTRAINTS

**Assumptions:**
- Customers grant Reader role (minimum permission for collection)
- Azure subscriptions have Cost Management data (90-day export available)
- Customers trust AI-generated narratives (GPT-4o accuracy acceptable)
- Stripe payments process within 2 minutes (no long delays)
- Azure Resource Graph returns <10k resources per subscription (pagination not yet implemented)

**Constraints:**
- Phase 1 budget: $0 new Azure spend (reuse marco* resources)
- Phase 1 timeline: Q1 2026 (proof of concept by March 31)
- Cosmos RU/s limit: 400 (no autoscale in Phase 1)
- Container App Job concurrency: 10 max (no queue, sequential only)
- IaC template library: 12 categories (fixed, no custom rules in Phase 1)

**Dependencies:**
- Azure OpenAI (marco-sandbox-openai-v2, canadaeast) -- service availability
- Stripe webhook delivery -- payment unlock timing
- Azure Advisor API -- recommendation quality
- Cost Management API -- billing data export timing (up to 48-hour delay)

---

## GLOSSARY

**ACA**: Azure Cost Advisor (this product)
**Cosmos**: Azure Cosmos DB NoSQL (database)
**Tier 1/2/3**: Pricing tiers (Free, Paid, Premium)
**Finding**: A single optimization opportunity (output of one rule)
**Scan**: End-to-end execution (collection + analysis) for one subscription
**IaC**: Infrastructure as Code (Bicep or Terraform)
**Deliverable**: Tier 3 zip package (IaC templates + guides)
**Partition key**: Cosmos DB subscriptionId (tenant isolation mechanism)
**Redteam agent**: AI safety validator (checks IaC for risk before delivery)
**MTI**: Mean Trust Index (Veritas metric, gates deployment)
**Story ID**: ACA-NN-NNN identifier (epic-story numbering)
**EVA**: Enterprise Value Accelerator (foundry framework)

---

## RELATED DOCUMENTS

- [Application Architecture](./application-architecture.md) -- technical component details
- [Infrastructure Architecture](./infrastructure-architecture.md) -- deployment topology
- [Security Architecture](./security-architecture.md) -- threat model and controls
- [PLAN.md](../../PLAN.md) -- work breakdown structure (14 epics, 257 stories)
- [CHANGELOG.md](../../CHANGELOG.md) -- 72-hour retrospective (44 commits, 6 phases)
- [05-technical.md](../05-technical.md) -- API specification reference

---

END OF SOLUTION ARCHITECTURE
