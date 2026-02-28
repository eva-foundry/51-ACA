# ACA -- Application Architecture

Version: 1.0.0
Updated: 2026-02-28
Status: Active
Audience: Development teams, Solution Architects, Technical PMs

---

## PURPOSE

This document defines the detailed application architecture for Azure Cost Advisor
(ACA), covering component design, service interactions, state management, data flow
patterns, and development patterns for the SaaS application layer.

Read this document when: implementing new features, debugging service interactions,
planning refactoring, or understanding the application's internal design decisions.

---

## SYSTEM CONTEXT

ACA is a multi-tenant SaaS application that analyzes Azure subscriptions to identify
cost optimization opportunities and deliver actionable remediation guidance. The 
application operates across three pricing tiers (Tier 1: free report, Tier 2: detailed
findings, Tier 3: IaC deliverables) and follows a job-orchestrated pipeline architecture.

---

## APPLICATION COMPONENTS

### 1. API Service (services/api/)

**Role**: Orchestration hub, authentication gateway, tier enforcement
**Tech**: FastAPI 0.115+, Python 3.12, uvicorn ASGI server
**Port**: 8080 (dev), ACA-managed in prod
**State**: Stateless (session state in Cosmos, no local cache)

**Key modules:**

```
app/
  main.py              FastAPI application factory, CORS, middleware stack
  routers/
    auth.py            Entra OIDC + MSAL delegated auth handshake
    scans.py           POST /v1/scans + GET /v1/scans/:id (scan orchestration)
    findings.py        GET /v1/findings (tier-gated response filtering)
    checkout.py        POST /v1/checkout/session (Stripe checkout)
    entitlements.py    GET /v1/entitlements (tier + feature flags)
    admin.py           Tenant lock/unlock, scan reconcile, audit log
  middleware/
    tenant.py          Partition key injection (subscriptionId extraction)
    timing.py          ASGI timing middleware (X-Request-Duration-Ms)
    tier_gate.py       Feature flag + tier enforcement on protected routes
  db/
    cosmos.py          CosmosClient wrapper with partition-scoped queries
    repos/             Repository pattern: scans_repo, findings_repo, entitlements_repo
  models/
    schemas.py         Pydantic request/response models (API contract)
  settings.py          pydantic-settings (env var validation + secrets)
```

**Design patterns:**
- Repository pattern for Cosmos access (abstraction over raw SDK)
- Middleware-driven cross-cutting concerns (auth, timing, tenant isolation)
- Dependency injection via FastAPI dependency system (cosmos_client = Depends(get_cosmos))
- Tier gating at route level (findings endpoint returns different schemas per tier)
- Partition key enforcement: every DB call includes `partition_key=subscription_id`

**Critical constraints:**
- ALL Cosmos queries MUST include partition_key (enforced by tenant middleware)
- NO cross-tenant queries allowed (middleware fails if subscriptionId missing)
- Tier 1 responses MUST NOT leak narrative or template_id fields
- All secrets via Key Vault (no .env in production)

---

### 2. Collector Service (services/collector/)

**Role**: Azure SDK data ingestion worker
**Tech**: Python 3.12, Azure SDK, scheduled Container App Job
**Execution**: On-demand (POST /v1/scans) + nightly cron (02:00 UTC)
**State**: Ephemeral (writes to Cosmos, no local state)

**Key modules:**

```
app/
  main.py              Entry point (job runner, parses --subscription-id CLI arg)
  azure_client.py      Azure SDK wrappers (ARM, Resource Graph, Cost Management, Advisor)
  preflight.py         RBAC + capability probe (validates permissions before collection)
  ingest.py            Normalize + write to Cosmos (inventories, cost-data, advisor containers)
```

**Data sources:**
- Azure Resource Graph (inventory: all resources in subscription)
- Cost Management API (90-day cost export via marcosandboxfinopshub)
- Azure Advisor (recommendations)
- Network Watcher (optional - topology data for ACA-03-015 network flow optimization rule)

**Preflight checks** (02-preflight.md):
1. Reader role on subscription
2. Cost Management Reader on subscription (for billing data)
3. Resource Graph query access
4. Advisor read access
5. Network Watcher read access (if available)

**Output containers** (Cosmos):
- `inventories` -- partition=subscriptionId, normalized resource records
- `cost-data` -- partition=subscriptionId, 90-day cost time series
- `advisor` -- partition=subscriptionId, native Advisor recommendations

**Error handling:**
- Preflight FAIL -> write `scans` record with status=BLOCKED, error_code=RBAC_INSUFFICIENT
- Partial failure (e.g. Cost Management timeout) -> status=PASS_WITH_WARNINGS, warnings array
- Network Watcher unavailable -> skip network rules, status=PASS (graceful degradation)

---

### 3. Analysis Service (services/analysis/)

**Role**: Rule engine + agent-enhanced analysis
**Tech**: Python 3.12, 29-foundry agent SDK, Azure OpenAI GPT-4o
**Execution**: Triggered after collector PASS (webhook or poll from API)
**State**: Ephemeral (reads Cosmos inventories/cost-data, writes findings)

**Key modules:**

```
app/
  main.py              Entry point (job runner, --subscription-id)
  rules/               12 rule modules (one per optimization category)
    rule_01_dev_box_autostop.py
    rule_02_vm_rightsizing.py
    rule_03_disk_unattached.py
    rule_04_app_service_idle.py
    rule_05_sql_reserved.py
    rule_06_cosmos_autoscale.py
    rule_07_storage_tier.py
    rule_08_network_gateway_idle.py
    rule_09_public_ip_orphaned.py
    rule_10_snapshot_expiry.py
    rule_11_keyvault_soft_delete.py
    rule_12_rbac_audit.py
  agents/
    analysis_agent.py    29-foundry agent: enriches findings with context
    redteam_agent.py     29-foundry agent: validates proposed changes (safety)
  findings.py            FindingsAssembler (aggregates rule outputs, tier gating)
```

**Rule output schema** (docs/saving-opportunity-rules.md):

```python
{
  "id": "rule-01-dev-box-autostop",  # kebab-case, stable
  "category": "compute-scheduling",
  "title": "Dev Box instances run nights and weekends",  # plain English, no how-to
  "estimated_saving_low": 5548,   # CAD/yr
  "estimated_saving_high": 7902,
  "effort_class": "trivial",      # trivial|easy|medium|involved|strategic
  "risk_class": "none",           # none|low|medium|high
  "heuristic_source": "rule-01",
  "narrative": "...",             # Tier 2+ only
  "deliverable_template_id": "tmpl-dev-box-autostop",  # Tier 3 only
}
```

**Agent augmentation:**
- `analysis_agent`: reads inventory context, enriches each finding's narrative with
  specific resource names, SKUs, and quantified business impact
- `redteam_agent`: validates proposed IaC changes against safety rules (no data loss,
  no downtime risk, reversible changes only)

**Output container**:
- `findings` -- partition=subscriptionId, array of finding objects, tier-gated on read

**Agent LLM config**:
- Model: GPT-4o (marco-sandbox-openai-v2, canadaeast)
- Temperature: 0.2 (deterministic for consistency across runs)
- Max tokens: 2000 per finding narrative
- Fallback: if OpenAI unavailable, findings still produced (narrative blank, heuristic only)

---

### 4. Delivery Service (services/delivery/)

**Role**: IaC template parameterization + zip packaging (Tier 3 only)
**Tech**: Python 3.12, Jinja2, Azure Blob Storage SDK
**Execution**: POST /v1/delivery/package (after Tier 3 unlock)
**State**: Ephemeral (writes zip to Blob Storage, returns SAS URL)

**Key modules:**

```
app/
  main.py              Entry point (job runner, --subscription-id --finding-ids)
  templates/           IaC template library (12 categories, Bicep + Terraform)
  generator.py         Parametrize templates from findings + inventory context
  packager.py          Assemble zip, SHA-256 manifest, upload to Blob, generate SAS URL
```

**Template categories** (docs/12-IaCscript.md):
1. Compute scheduling (autostop, autoscale)
2. VM rightsizing (SKU change scripts)
3. Storage tiering (lifecycle policies)
4. SQL reserved capacity (reservation purchase scripts)
5. Cosmos autoscale (RU/s adjustment)
6. App Service plan consolidation
7. Network gateway removal (unused ExpressRoute/VPN)
8. Public IP cleanup
9. Snapshot retention policies
10. Key Vault soft-delete enforcement
11. RBAC cleanup (orphaned assignments)
12. Cost alerting (budget + action groups)

**Delivery package structure:**

```
aca-deliverables-{subscription_id}-{timestamp}.zip
  manifest.json           SHA-256 checksums for all files
  README.md               Execution instructions + prerequisites
  findings.json           Full findings array (Tier 3 unfiltered)
  scripts/
    bicep/
      {finding_id}.bicep
      {finding_id}.bicepparam
    terraform/
      {finding_id}.tf
      {finding_id}.tfvars
  docs/
    {finding_id}-guide.md   Step-by-step implementation guide
```

**SAS URL generation:**
- Expiry: 168 hours (7 days)
- Permissions: Read-only
- Storage account: marcosand20260203 (Phase 1) / aca-delivery-store (Phase 2)
- Container: deliverables (private, no public access)

**Error handling:**
- Template generation failure -> skip that finding, continue with others
- If ALL templates fail -> return 422 with error details
- Blob upload failure -> retry 3x with exponential backoff, then fail with 500

---

### 5. Frontend (frontend/)

**Role**: User-facing React SPA (Tier 1/2/3 UI, checkout, download)
**Tech**: React 19, Fluent UI v9, Vite, TypeScript 5.3
**Port**: 3000 (dev), served via Azure Static Web App or App Service (Phase 1)
**State**: Client-side only (React Context + sessionStorage, no Redux)

**Key directories:**

```
src/
  pages/
    Login.tsx              Entra OIDC login + MSAL handshake
    ConnectSubscription.tsx  Azure subscription connection wizard
    Status.tsx             Scan progress polling (POST /v1/scans, GET /v1/scans/:id)
    Findings.tsx           Tier-gated findings list (Tier 1: summary cards only)
    Download.tsx           Tier 3 deliverable download (SAS URL redirect)
  components/
    OpportunityCard.tsx    Fluent UI Card for single finding
    SavingsBar.tsx         Horizontal bar chart (estimated_saving_low/high)
    TierGate.tsx           Paywall component (shows Stripe checkout CTA)
    CheckoutCTA.tsx        Stripe checkout button (POST /v1/checkout/session)
  hooks/
    useFindings.ts         GET /v1/findings with tier-aware response parsing
    useScanStatus.ts       Poll GET /v1/scans/:id every 5s during RUNNING state
    useCheckout.ts         POST /v1/checkout/session + redirect to Stripe
  api/
    client.ts              Typed fetch wrapper (auth headers, error handling)
```

**Routing** (React Router 6.20):

```
/                    -> Login (if not authenticated)
/connect             -> ConnectSubscription (Azure OAuth flow)
/status              -> Status (scan progress)
/findings            -> Findings (tier-gated list)
/download            -> Download (Tier 3 only)
```

**Auth flow** (MSAL.js 3.x):
1. User clicks "Sign in with Microsoft"
2. MSAL redirects to login.microsoftonline.com (Entra OIDC)
3. Redirect back to /connect with auth code
4. MSAL exchanges code for access token + refresh token
5. Frontend stores tokens in sessionStorage (not localStorage for security)
6. All API calls include `Authorization: Bearer {access_token}` header

**Tier enforcement on frontend:**
- useFindings hook checks entitlements before rendering
- TierGate component wraps protected UI (shows upgrade CTA if tier insufficient)
- Tier 1: shows OpportunityCard with title + estimated savings only
- Tier 2: shows full narrative + effort/risk classification
- Tier 3: shows Download button + deliverable package info

**i18n** (Epic 9):
- react-i18next for translations
- 5 locales in Phase 1: en-CA, fr-CA, en-US, fr-FR, es-MX
- All user-facing strings in translation files (no hardcoded English)
- Locale detection: browser Accept-Language header, fallback to en-CA

---

## DATA FLOW PATTERNS

### Pattern 1: Scan Execution (Happy Path)

```
1. User clicks "Run Scan" on frontend
   -> POST /v1/scans (API)
   -> API creates scan record in Cosmos (status=PENDING)
   -> API triggers collector job (Container App Job invocation)
   -> Returns scan_id to frontend

2. Collector job starts
   -> Runs preflight checks (RBAC validation)
   -> If PASS: pulls inventory + cost + advisor data via Azure SDK
   -> Writes to Cosmos: inventories, cost-data, advisor containers
   -> Updates scan record: status=COLLECTED

3. API detects scan status=COLLECTED (webhook or poll)
   -> Triggers analysis job

4. Analysis job starts
   -> Reads inventories, cost-data from Cosmos
   -> Runs 12 rules (parallel execution)
   -> Runs analysis_agent (GPT-4o enrichment)
   -> Writes findings to Cosmos
   -> Updates scan record: status=COMPLETED

5. Frontend polls GET /v1/scans/:id
   -> Detects status=COMPLETED
   -> Redirects to /findings

6. Frontend calls GET /v1/findings
   -> API reads findings from Cosmos
   -> Applies tier gating (strips fields for Tier 1)
   -> Returns findings array

7. User clicks "Upgrade to Tier 2"
   -> POST /v1/checkout/session
   -> API creates Stripe checkout session
   -> Returns Stripe URL
   -> Frontend redirects to Stripe

8. User completes payment
   -> Stripe webhook POST /v1/webhooks/stripe
   -> API validates signature, updates entitlements in Cosmos
   -> Frontend redirects to /findings (now Tier 2 unlocked)

9. User clicks "Download Deliverables" (Tier 3 only)
   -> POST /v1/delivery/package
   -> API triggers delivery job
   -> Delivery job generates IaC templates, zips, uploads to Blob
   -> Returns SAS URL
   -> Frontend redirects to SAS URL (browser downloads zip)
```

### Pattern 2: Tenant Isolation (Every Request)

```
All API requests include:
  Authorization: Bearer {access_token}  (Entra OIDC)
  X-Subscription-Id: {subscription_id} (client-provided)

Tenant middleware (app/middleware/tenant.py):
  1. Extracts subscription_id from header or JWT claims
  2. Validates token (MSAL signature verification)
  3. Injects subscription_id into request.state.subscription_id
  4. ALL downstream Cosmos queries use this as partition_key

Cosmos query pattern (enforced):
  container.query_items(
    query="SELECT * FROM c WHERE c.subscriptionId = @sub",
    parameters=[{"name": "@sub", "value": subscription_id}],
    partition_key=subscription_id  # MANDATORY
  )

Cross-tenant query prevention:
  - Partition key missing -> middleware returns 403
  - Query without partition_key -> Cosmos returns 400 (invalid request)
  - No code path can bypass partition filter
```

### Pattern 3: Tier Gating (Findings Response)

```python
# services/api/app/routers/findings.py

def gate_findings(findings: list, tier: str) -> list:
    if tier == "tier1":
        # Tier 1: title + category + estimated savings + effort class only
        return [
            {
                "id": f["id"],
                "title": f["title"],
                "category": f["category"],
                "estimated_saving_low": f["estimated_saving_low"],
                "estimated_saving_high": f["estimated_saving_high"],
                "effort_class": f["effort_class"],
            }
            for f in findings
        ]
    if tier == "tier2":
        # Tier 2: full finding except deliverable_template_id
        return [
            {k: v for k, v in f.items() if k != "deliverable_template_id"}
            for f in findings
        ]
    # tier3: full finding (no filtering)
    return findings
```

**Enforcement points:**
1. API route: GET /v1/findings checks entitlements before calling gate_findings()
2. Frontend: TierGate component prevents UI rendering of gated fields
3. Delivery job: checks tier=tier3 before generating templates (403 otherwise)

---

## STATE MANAGEMENT

### Cosmos DB Containers (Partition Key: subscriptionId)

```
scans          -- scan orchestration records
  id: scan_id (GUID)
  subscriptionId: Azure subscription ID (partition key)
  status: PENDING|RUNNING|COLLECTED|ANALYZING|COMPLETED|FAILED
  started_at, completed_at, error_code, warnings

inventories    -- normalized Azure resource records
  id: resource_id (ARM resource ID)
  subscriptionId: partition key
  resource_type, location, sku, tags, properties

cost-data      -- 90-day cost time series
  id: date_subscription (e.g. "2026-02-26_abc123")
  subscriptionId: partition key
  date, cost_usd, cost_cad, resource_breakdown

advisor        -- Azure Advisor recommendations (raw)
  id: advisor_recommendation_id
  subscriptionId: partition key
  category, impact, description, action

findings       -- analysis rule outputs
  id: finding_id (GUID)
  subscriptionId: partition key
  rule_id, category, title, estimated_saving_low, estimated_saving_high,
  effort_class, risk_class, narrative, deliverable_template_id

entitlements   -- tier + feature flags per subscription
  id: subscriptionId (partition key = id)
  tier: tier1|tier2|tier3
  valid_until: ISO timestamp
  features: array of feature flag names
  stripe_customer_id, stripe_subscription_id
```

**No in-memory cache:**
- All state in Cosmos (stateless API/jobs)
- Frontend state in React Context + sessionStorage (ephemeral)
- No Redis, no distributed cache (Phase 1 simplicity)

---

## ERROR HANDLING PATTERNS

### Principle: Fail fast, log structured, return actionable errors

**API error responses** (RFC 7807 Problem Details):

```json
{
  "type": "https://aca.example.com/errors/permission-denied",
  "title": "Permission Denied",
  "status": 403,
  "detail": "Subscription abc123 requires Reader role for scan execution",
  "instance": "/v1/scans/scan-xyz",
  "trace_id": "req-abc123",
  "timestamp": "2026-02-28T12:34:56Z"
}
```

**Job error handling:**
- Preflight FAIL -> scan status=BLOCKED, error_code in scan record
- Transient failure (network timeout) -> retry 3x exponential backoff, then FAIL
- Partial success (Cost Management timeout) -> status=PASS_WITH_WARNINGS, warnings array
- Fatal error (Cosmos write failure) -> scan status=FAILED, detailed error in logs

**Frontend error display:**
- API 4xx/5xx -> Toast notification (Fluent UI MessageBar)
- Scan failure -> Status page shows error_code + suggested actions
- Payment failure -> Checkout page shows Stripe error message

---

## PERFORMANCE PATTERNS

### API latency targets:
- GET /v1/findings: p50 < 100ms, p95 < 300ms
- POST /v1/scans: p50 < 200ms (synchronous), job async
- POST /v1/checkout/session: p50 < 500ms (Stripe round-trip)

### Optimization techniques:
- Cosmos queries always use partition key (single-partition reads)
- Findings pagination: limit=50 default, max=500
- Frontend lazy loading: React.lazy() for all page components
- Blob Storage SAS URLs: 7-day expiry, client-side download (no proxy)

### Scalability constraints (Phase 1):
- API: Azure Container App, autoscale 0-10 instances
- Jobs: Container App Jobs, manual concurrency limit (no queue)
- Cosmos: 400 RU/s (shared across all containers)
- Estimated max: 100 subscriptions, 10 concurrent scans

### Future optimization (Phase 2):
- Cosmos autoscale (4000 RU/s burst)
- Job queue (Azure Service Bus) for scan orchestration
- CDN (Azure Front Door) for frontend static assets
- Application Insights adaptive sampling (reduce telemetry cost)

---

## OBSERVABILITY

### Structured logging (all services):

```python
# services/api/app/main.py
import structlog

logger = structlog.get_logger()
logger.info(
    "scan_started",
    scan_id=scan_id,
    subscription_id=subscription_id,
    tier=tier,
    duration_ms=0,
)
```

**Log aggregation:**
- Phase 1: Application Insights (marco-sandbox-appinsights)
- Phase 2: Log Analytics Workspace + Kusto queries

**Metrics (TimingMiddleware):**
- X-Request-Duration-Ms header on all API responses
- Structured log line: `api_request_completed` with status_code, path, duration_ms
- Application Insights custom metrics: scan_duration_seconds, findings_count

**Tracing:**
- No distributed tracing in Phase 1 (single-region, simple topology)
- Phase 2: OpenTelemetry + Application Insights correlation

---

## TESTING STRATEGY

### Unit tests (pytest):
- Target: 80% coverage on business logic (rules, repos, middleware)
- Location: services/*/tests/
- Run: `pytest services/ -x -q`
- CI gate: all tests MUST pass before merge

### Integration tests:
- Cosmos emulator for local dev (docker-compose.yml)
- Stripe test mode (webhook signature validation)
- MSAL mock (no real Entra calls in tests)

### E2E tests (Phase 2, Playwright):
- Full user flow: login -> connect -> scan -> findings -> checkout -> download
- Run against staging environment (Phase 1 marco* resources)

### Contract tests (Pact):
- Phase 2 only (API consumer/provider contract verification)

---

## DEPLOYMENT PATTERNS

### Phase 1 (marco* resources):
- API: Azure Container App (marcosandboxaca or new instance)
- Jobs: Container App Jobs (collector, analysis, delivery)
- Frontend: Azure Static Web App or App Service
- Infra: Bicep (infra/phase1-marco/main.bicep + bootstrap.sh)
- CI/CD: GitHub Actions (.github/workflows/deploy-phase1.yml)
- Secrets: Key Vault (marcosandkv20260203)

### Phase 2 (private subscription):
- Same topology, new resource group
- Terraform modules from 18-azure-best/04-terraform-modules
- Private DNS zone for custom domain (aca.example.com)
- Azure Front Door for CDN + WAF
- Separate Key Vault per environment (dev/staging/prod)

---

## DEVELOPMENT WORKFLOWS

### Local dev:

```bash
# Start all services + Cosmos emulator
docker-compose up

# API: http://localhost:8080
# Frontend: http://localhost:3000
# Cosmos emulator: https://localhost:8081 (cert warning expected)

# Run tests
pytest services/ -x -q
cd frontend && npm test
```

### Feature branch workflow:
1. Create feature branch from main
2. Implement + add tests
3. Run full test suite locally
4. Push to GitHub -> CI runs (lint + test)
5. Open PR -> automated review checks
6. Merge to main -> deploy-phase1 workflow runs

### Story implementation checklist:
- [ ] Code implementation
- [ ] Unit tests (>= 80% coverage on new code)
- [ ] EVA-STORY tag added to all modified files
- [ ] PLAN.md story marked Done
- [ ] veritas-plan.json updated (scripts/seed-from-plan.py)
- [ ] Evidence receipt written (.eva/evidence/{story_id}-receipt.json)
- [ ] ACA-METRICS commit trailer in commit message

---

## MIGRATION NOTES (Phase 1 -> Phase 2)

**Compatibility requirements:**
- Cosmos schema MUST NOT break (all fields optional or with defaults)
- API endpoints MUST NOT change URL or contract (versioned if breaking)
- Frontend MUST support both Phase 1 and Phase 2 backend URLs (env var)

**Migration path:**
1. Provision Phase 2 resources (Terraform apply)
2. Copy Cosmos data (Azure Data Factory pipeline)
3. Update DNS CNAME (frontend domain)
4. Update APIM subscription key policies
5. Cutover: API traffic to new ACA instances
6. Monitor for 7 days, then decommission Phase 1 resources

---

## RELATED DOCUMENTS

- [Solution Architecture](./solution-architecture.md) -- end-to-end solution view
- [Infrastructure Architecture](./infrastructure-architecture.md) -- deployment topology
- [Security Architecture](./security-architecture.md) -- threat model and controls
- [05-technical.md](../05-technical.md) -- API specification
- [PLAN.md](../../PLAN.md) -- WBS and story backlog
- [copilot-instructions.md](../../.github/copilot-instructions.md) -- dev patterns

---

END OF APPLICATION ARCHITECTURE
