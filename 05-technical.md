Below are \*\*three artifacts\*\* you can paste directly into your repo:



1\. `docs/api-spec.md`

2\. \*\*Technical API/code skeleton guidance\*\* (FastAPI structure + key modules)

3\. \*\*ASCII architecture diagram\*\*



(Everything aligns with your ACA scope/tiers/services.  )



---



\## 1) `docs/api-spec.md`



```markdown

\# ACA API Specification

======================



Version: 0.1

Updated: 2026-02-26

Audience: ACA backend/frontend developers, APIM policy authors



This document defines the public and internal APIs for ACA (Azure Cost Advisor).



Scope

-----

\- Client onboarding + subscription connection

\- Pre-flight validation (RBAC + capability probes)

\- Scan orchestration (collector job)

\- Analysis orchestration (analysis job)

\- Findings retrieval (Tier 1/2 gating)

\- Checkout (Tier 2/3)

\- Deliverable packaging (Tier 3)

\- Audit log access



ACA system context: three services (collector, analysis, delivery) orchestrated via an API and jobs. See PLAN/README. (Ref) :contentReference\[oaicite:2]{index=2} :contentReference\[oaicite:3]{index=3}



-------------------------------------------------------------------------------

1\. API SECURITY MODEL

-------------------------------------------------------------------------------



1.1 Authentication

\- Primary: Microsoft Entra ID (OIDC) for end-users accessing the ACA UI

\- Secondary: APIM subscription key for client-level throttling / tier enforcement

\- Internal: Managed Identity for service-to-service access (jobs, Cosmos, Key Vault)



1.2 Authorization

\- A "client" in ACA maps to a subscription-scoped tenant boundary.

\- All tenant data operations require a subscriptionId and enforce:

&nbsp; - Cosmos partition key = subscriptionId

&nbsp; - API middleware enforces partition filter for every DB query (no cross-tenant)



1.3 Tier gating

\- Tier 1: high-level findings only (no implementation detail)

\- Tier 2: full findings (narrative, effort/risk, beyond-cost signals)

\- Tier 3: downloadable deliverable package (zip) generated after payment



-------------------------------------------------------------------------------

2\. BASE URLS \& VERSIONING

-------------------------------------------------------------------------------



Public API (via APIM):

\- Base: https://api.aca.example.com

\- Version prefix: /v1



Internal job endpoints (optional, not exposed publicly):

\- Base: http://aca-api.internal

\- Version prefix: /v1/internal



-------------------------------------------------------------------------------

3\. CORE ENTITIES (DATA CONTRACTS)

-------------------------------------------------------------------------------



3.1 Client

\- clientId: string (ACA internal)

\- tenantId: string (Entra tenant)

\- primaryEmail: string

\- createdUtc: datetime

\- tier: "tier1" | "tier2" | "tier3"

\- paymentStatus: "none" | "active" | "past\_due" | "canceled"

\- allowedSubscriptions: string\[] (subscriptionIds)



3.2 SubscriptionConnection

\- subscriptionId: string

\- subscriptionName: string

\- tenantId: string

\- principalType: "User" | "ServicePrincipal"

\- principalId: string

\- connectedUtc: datetime

\- connectionMode: "delegated" | "service\_principal" | "lighthouse"

\- status: "connected" | "disconnected"



3.3 PreFlightResult

\- preflightId: string

\- subscriptionId: string

\- principal: { tenantId, principalId, principalType, displayName? }

\- requiredRoles: \[{ roleName, scope, mandatory }]

\- roleValidation: { status, evidence\[] }

\- capabilityProbes: \[{ name, mandatory, status, httpStatus, latencyMs, evidenceRef }]

\- verdict: { status: "PASS"|"PASS\_WITH\_WARNINGS"|"FAIL", warnings\[], blockers\[] }

\- createdUtc: datetime



3.4 Scan (Collector Run)

\- scanId: string

\- subscriptionId: string

\- preflightId: string

\- requestedBy: principalId

\- status: "queued" | "running" | "succeeded" | "failed" | "canceled"

\- startedUtc: datetime?

\- completedUtc: datetime?

\- stats: { inventoryCount?, costRows?, advisorRecs?, policyStates? }

\- error?: { code, message, details? }



3.5 AnalysisRun

\- analysisId: string

\- subscriptionId: string

\- scanId: string

\- status: "queued" | "running" | "succeeded" | "failed"

\- startedUtc: datetime?

\- completedUtc: datetime?

\- findingsSummary: { findingCount, totalSavingLow, totalSavingHigh, categories\[] }

\- error?: { code, message, details? }



3.6 Finding (Tiered View)

\- id: string

\- category: string

\- title: string

\- estimated\_saving\_low: number

\- estimated\_saving\_high: number

\- effort\_class: "trivial"|"easy"|"medium"|"involved"|"strategic"

\- risk\_class: "none"|"low"|"medium"|"high"

\- heuristic\_source: string

\- narrative?: string           (Tier 2+)

\- deliverable\_template\_id?: string (Tier 3)

\- evidence\_refs?: string\[]     (Tier 2+)



3.7 Deliverable (Tier 3)

\- deliverableId: string

\- subscriptionId: string

\- analysisId: string

\- status: "pending\_payment" | "queued" | "generating" | "ready" | "failed"

\- createdUtc: datetime

\- artifact: { blobPath, sha256, sizeBytes }?

\- download: { sasUrl, expiresUtc }?  (only when ready)



3.8 AuditEvent

\- auditId: string

\- subscriptionId: string

\- actor: { principalId, principalType }

\- action: string

\- target: string

\- status: "ok"|"error"

\- timestampUtc: datetime

\- correlationId: string

\- metadata: object (sanitized)



-------------------------------------------------------------------------------

4\. PUBLIC API ENDPOINTS (/v1)

-------------------------------------------------------------------------------



4.1 Health

GET /v1/health

Response: { status: "ok", version: "0.1", timeUtc: "..." }



4.2 Current user \& entitlements

GET /v1/me

Response:

{

&nbsp; "clientId": "...",

&nbsp; "tenantId": "...",

&nbsp; "email": "...",

&nbsp; "tier": "tier1",

&nbsp; "allowedSubscriptions": \["..."]

}



4.3 Subscription discovery (post-login)

GET /v1/subscriptions

Returns Azure subscriptions visible to the signed-in principal (delegated) OR

returns the ACA-connected subscriptions if using service principal mode.

Response: { subscriptions: \[{ subscriptionId, name, state }] }



4.4 Connect subscription

POST /v1/subscriptions/connect

Body:

{

&nbsp; "mode": "delegated" | "service\_principal",

&nbsp; "subscriptionId": "....",

&nbsp; "servicePrincipal": {

&nbsp;   "tenantId": "...",

&nbsp;   "clientId": "...",

&nbsp;   "clientSecret": "..."   // only for service\_principal mode

&nbsp; }

}

Response:

{

&nbsp; "connection": { ...SubscriptionConnection... }

}



Security notes:

\- For delegated mode, Body.servicePrincipal must be omitted.

\- Client secrets must never be logged; store in Key Vault.



4.5 Disconnect subscription

POST /v1/subscriptions/{subscriptionId}/disconnect

Response: { status: "disconnected" }



4.6 Pre-flight validation (MANDATORY before scan)

POST /v1/onboarding/preflight

Body:

{

&nbsp; "subscriptionId": "...",

&nbsp; "features": {

&nbsp;   "enableLogAnalyticsSignals": false,

&nbsp;   "enableNetworkSignals": true,

&nbsp;   "policyInsightsMandatory": true

&nbsp; }

}

Response: PreFlightResult



4.7 Start scan (collector run)

POST /v1/scans

Body:

{

&nbsp; "subscriptionId": "...",

&nbsp; "preflightId": "...",

&nbsp; "windowDays": 91,

&nbsp; "force": false

}

Response: { scanId: "...", statusUrl: "/v1/scans/{scanId}" }



Rules:

\- Requires latest preflight PASS for the subscriptionId.

\- Enforce Tier 1 scan frequency limits (e.g., one per 30 days) at APIM + API.



4.8 Scan status

GET /v1/scans/{scanId}

Response: Scan



4.9 List scans (per subscription)

GET /v1/subscriptions/{subscriptionId}/scans?limit=20

Response: { scans: Scan\[] }



4.10 Start analysis

POST /v1/analyses

Body:

{

&nbsp; "subscriptionId": "...",

&nbsp; "scanId": "...",

&nbsp; "mode": "tier1" | "tier2"

}

Response: { analysisId: "...", statusUrl: "/v1/analyses/{analysisId}" }



Rules:

\- Tier 1 analysis allowed free.

\- Tier 2 analysis requires entitlement (tier2 or tier3 paid).



4.11 Analysis status

GET /v1/analyses/{analysisId}

Response: AnalysisRun



4.12 Findings summary (Tier 1-safe)

GET /v1/analyses/{analysisId}/findings/summary

Response:

{

&nbsp; "findingCount": 12,

&nbsp; "totalSavingLow": 1500,

&nbsp; "totalSavingHigh": 4200,

&nbsp; "categories": \[{ "name": "Compute", "count": 4 }]

}



4.13 Findings list (tier-gated)

GET /v1/analyses/{analysisId}/findings

Query: ?tier=1|2

Response:

{

&nbsp; "tier": 1,

&nbsp; "findings": \[ Finding\[] ]

}



Gating:

\- tier=1 always allowed (titles/categories/savings only, no narrative/templates)

\- tier=2 requires paid entitlement



4.14 Checkout (Tier 2)

POST /v1/checkout/tier2

Body:

{

&nbsp; "subscriptionId": "...",

&nbsp; "analysisId": "..."

}

Response:

{

&nbsp; "checkoutSessionId": "...",

&nbsp; "redirectUrl": "https://checkout.stripe.com/..."

}



4.15 Checkout (Tier 3)

POST /v1/checkout/tier3

Body:

{

&nbsp; "subscriptionId": "...",

&nbsp; "analysisId": "..."

}

Response:

{

&nbsp; "checkoutSessionId": "...",

&nbsp; "redirectUrl": "https://checkout.stripe.com/..."

}



4.16 Stripe webhook

POST /v1/webhooks/stripe

\- Validates signature

\- On successful payment:

&nbsp; - unlock tier2 entitlement OR

&nbsp; - trigger delivery job (tier3)



Response: 200 OK



4.17 Create deliverable (Tier 3 trigger, internal/after payment)

POST /v1/deliverables

Body:

{

&nbsp; "subscriptionId": "...",

&nbsp; "analysisId": "..."

}

Response: Deliverable



4.18 Deliverable status

GET /v1/deliverables/{deliverableId}

Response: Deliverable



4.19 Deliverable download link (Tier 3 gated)

POST /v1/deliverables/{deliverableId}/download

Response:

{

&nbsp; "sasUrl": "...",

&nbsp; "expiresUtc": "..."

}

Rules:

\- Only when deliverable.status=ready

\- Short-lived SAS (e.g., 7 days) and single-subscription enforcement



4.20 Audit events (client-accessible)

GET /v1/subscriptions/{subscriptionId}/audit?limit=200

Response: { events: AuditEvent\[] }



-------------------------------------------------------------------------------

5\. INTERNAL ENDPOINTS (/v1/internal) (OPTIONAL)

-------------------------------------------------------------------------------



If you prefer jobs to call Cosmos directly, you can omit these. If you want an

orchestration layer, implement as internal-only endpoints.



POST /v1/internal/jobs/collector/run

POST /v1/internal/jobs/analysis/run

POST /v1/internal/jobs/delivery/run



Each takes: subscriptionId, correlationId, and job parameters, returns jobRunId.



-------------------------------------------------------------------------------

6\. ERROR MODEL

-------------------------------------------------------------------------------



All errors return:

{

&nbsp; "error": {

&nbsp;   "code": "MISSING\_PERMISSION|AUTH\_FAILED|NOT\_FOUND|TIER\_LOCKED|RATE\_LIMITED|INTERNAL",

&nbsp;   "message": "Human-readable",

&nbsp;   "details": { ...optional... },

&nbsp;   "correlationId": "..."

&nbsp; }

}



Common codes:

\- MISSING\_PERMISSION: preflight fails or probe denied

\- TIER\_LOCKED: requesting tier2/3 endpoints without entitlement

\- RATE\_LIMITED: APIM throttle triggered

\- VALIDATION\_FAILED: request body invalid

\- STRIPE\_WEBHOOK\_INVALID: signature check failed



-------------------------------------------------------------------------------

7\. OPENAPI (COMPACT SNIPPET)

-------------------------------------------------------------------------------



This is a minimal snippet. Generate the full OpenAPI from FastAPI.



openapi: 3.0.3

info:

&nbsp; title: ACA API

&nbsp; version: "0.1"

paths:

&nbsp; /v1/onboarding/preflight:

&nbsp;   post:

&nbsp;     summary: Run pre-flight permission validation

&nbsp;     requestBody:

&nbsp;       required: true

&nbsp;       content:

&nbsp;         application/json:

&nbsp;           schema:

&nbsp;             type: object

&nbsp;             required: \[subscriptionId]

&nbsp;             properties:

&nbsp;               subscriptionId: { type: string }

&nbsp;               features:

&nbsp;                 type: object

&nbsp;                 properties:

&nbsp;                   enableLogAnalyticsSignals: { type: boolean, default: false }

&nbsp;                   enableNetworkSignals: { type: boolean, default: true }

&nbsp;                   policyInsightsMandatory: { type: boolean, default: true }

&nbsp;     responses:

&nbsp;       "200":

&nbsp;         description: PreFlightResult

&nbsp;         content:

&nbsp;           application/json:

&nbsp;             schema:

&nbsp;               type: object

&nbsp;               properties:

&nbsp;                 preflightId: { type: string }

&nbsp;                 subscriptionId: { type: string }

&nbsp;                 verdict:

&nbsp;                   type: object

&nbsp;                   properties:

&nbsp;                     status: { type: string, enum: \[PASS, PASS\_WITH\_WARNINGS, FAIL] }



&nbsp; /v1/scans:

&nbsp;   post:

&nbsp;     summary: Start collector run

&nbsp;     responses:

&nbsp;       "200": { description: Scan started }



&nbsp; /v1/analyses:

&nbsp;   post:

&nbsp;     summary: Start analysis run

&nbsp;     responses:

&nbsp;       "200": { description: Analysis started }



-------------------------------------------------------------------------------

8\. NON-FUNCTIONAL REQUIREMENTS (API)

-------------------------------------------------------------------------------



Latency targets:

\- Preflight: < 5s typical

\- Health: < 200ms

\- Findings list: < 1s typical (cached/optimized)



Logging:

\- Every request includes correlationId

\- Do not log secrets, tokens, or client secrets



Idempotency:

\- /scans POST supports idempotency key: (subscriptionId + day) unless force=true

\- /deliverables creation is idempotent per (analysisId)



-------------------------------------------------------------------------------

END

-------------------------------------------------------------------------------

```



---



\## 2) Technical API / code skeleton (FastAPI)



This is a \*\*practical layout\*\* that matches your “API + jobs” model. 



```text

services/api/

&nbsp; app/

&nbsp;   main.py

&nbsp;   settings.py

&nbsp;   deps.py

&nbsp;   middleware/

&nbsp;     correlation\_id.py

&nbsp;     subscription\_scope.py   # enforces subscriptionId + Cosmos partition filter

&nbsp;     tier\_gate.py            # tier1/tier2/tier3 access checks

&nbsp;   auth/

&nbsp;     entra\_oidc.py           # validates user JWT (frontend login)

&nbsp;     sp\_credentials.py       # service principal mode: store/retrieve in Key Vault

&nbsp;   routers/

&nbsp;     health.py

&nbsp;     me.py

&nbsp;     subscriptions.py

&nbsp;     onboarding.py           # preflight endpoints

&nbsp;     scans.py

&nbsp;     analyses.py

&nbsp;     findings.py

&nbsp;     checkout.py

&nbsp;     deliverables.py

&nbsp;     audit.py

&nbsp;     webhooks\_stripe.py

&nbsp;   services/

&nbsp;     preflight\_service.py

&nbsp;     scan\_service.py         # triggers collector job

&nbsp;     analysis\_service.py     # triggers analysis job

&nbsp;     delivery\_service.py     # triggers delivery job

&nbsp;     entitlement\_service.py  # tier checks

&nbsp;     audit\_service.py

&nbsp;   azure/

&nbsp;     arm.py

&nbsp;     resource\_graph.py

&nbsp;     cost\_mgmt.py

&nbsp;     advisor.py

&nbsp;     policy\_insights.py

&nbsp;     network.py

&nbsp;     log\_analytics.py

&nbsp;   db/

&nbsp;     cosmos.py

&nbsp;     repos/

&nbsp;       clients\_repo.py

&nbsp;       preflight\_repo.py

&nbsp;       scans\_repo.py

&nbsp;       analyses\_repo.py

&nbsp;       findings\_repo.py

&nbsp;       deliverables\_repo.py

&nbsp;       audit\_repo.py

&nbsp;   models/

&nbsp;     dtos.py                 # request/response models (Pydantic)

&nbsp;     enums.py

```



\### Key middleware you should implement first



\* `correlation\_id`: generate/propagate `X-Correlation-Id`

\* `subscription\_scope`: reject any request that touches data without `subscriptionId` and enforce partition key

\* `tier\_gate`: enforce `tier=1` safe redaction vs `tier=2` full payload vs `tier=3` download access



\### “Preflight” implementation notes



Implement preflight as a service with \*\*probe adapters\*\*:



```text

preflight\_service.run(subscriptionId, features):

&nbsp; - validate token

&nbsp; - subscriptions.list probe

&nbsp; - resource\_graph probe

&nbsp; - cost\_mgmt probe

&nbsp; - advisor probe

&nbsp; - policy\_insights probe

&nbsp; - network probes

&nbsp; - optional log\_analytics probe

&nbsp; - return verdict + store PreFlightResult

```



\### Job triggering pattern (Container Apps Jobs)



Expose a single internal function:



\* `enqueue\_job(jobType, payload)` where jobType in `{collector, analysis, delivery}`



Implementation options:



\* Call Container Apps Job “start” API (preferred)

\* Or put a message on a queue (future enhancement)



---



\## 3) ASCII architecture diagram



```text

&nbsp;                          ┌─────────────────────────────────────────────┐

&nbsp;                          │                Client / User                 │

&nbsp;                          │  Entra ID Login (MFA/CA) + Select Sub        │

&nbsp;                          └───────────────────────────┬─────────────────┘

&nbsp;                                                      │

&nbsp;                                                      v

┌─────────────────────────────────────────────────────────────────────────────────────┐

│                                 ACA FRONTEND (React)                                │

│  Pages: Login • Connect Subscription • Preflight Results • Findings • Checkout       │

└───────────────────────────┬────────────────────────────────────────────────────────┘

&nbsp;                           │ HTTPS

&nbsp;                           v

┌─────────────────────────────────────────────────────────────────────────────────────┐

│                                    APIM GATEWAY                                     │

│  - Subscription key (client throttle, tier limits)                                   │

│  - Token budget / rate limiting policies                                             │

│  - Routes /v1/\* to ACA API                                                           │

└───────────────────────────┬────────────────────────────────────────────────────────┘

&nbsp;                           │

&nbsp;                           v

┌─────────────────────────────────────────────────────────────────────────────────────┐

│                                 ACA API (FastAPI)                                   │

│  AuthN: Entra ID (user) / Service Principal (enterprise)                             │

│  AuthZ: subscriptionId scope enforced + tier gating                                  │

│  Endpoints: preflight • scans • analyses • findings • checkout • deliverables • audit│

└───────────────┬───────────────────────────────┬───────────────────────────────┬────┘

&nbsp;               │                               │                               │

&nbsp;               │ writes/reads                   │ secrets/tokens                │ job triggers

&nbsp;               v                               v                               v

&nbsp;     ┌──────────────────────┐        ┌──────────────────────┐        ┌──────────────────────┐

&nbsp;     │  Cosmos DB (ACA DB)   │        │     Key Vault        │        │ Container Apps Jobs  │

&nbsp;     │  PK = subscriptionId  │        │  SP creds, keys      │        │  collector/analysis  │

&nbsp;     │  containers:          │        └──────────────────────┘        │  delivery            │

&nbsp;     │   - preflights        │                                         └──────────┬──────────┘

&nbsp;     │   - scans             │                                                    │

&nbsp;     │   - inventories        │                                                    │

&nbsp;     │   - cost-data         │                                                    │

&nbsp;     │   - findings          │                                                    │

&nbsp;     │   - deliverables      │                                                    │

&nbsp;     │   - audit\_events      │                                                    │

&nbsp;     └───────────┬──────────┘                                                    │

&nbsp;                 │                                                                │

&nbsp;                 │                                                                │

&nbsp;                 v                                                                v

&nbsp;    ┌──────────────────────────┐                                  ┌──────────────────────────┐

&nbsp;    │  Observability           │                                  │  ACA Storage (Artifacts) │

&nbsp;    │  App Insights + Logs     │                                  │  - PDFs, ZIP packages     │

&nbsp;    │  - traces, metrics       │                                  │  - signed + SAS download  │

&nbsp;    └──────────────────────────┘                                  └──────────────────────────┘



DATA EXTRACTION PATH (read-only; client-controlled):

&nbsp; Collector Job -> Azure Resource Graph + ARM + Cost Mgmt + Advisor + Policy Insights (+ optional Logs)

&nbsp; -> writes inventory/cost/advisor/policy/network signals into Cosmos



ANALYSIS PATH:

&nbsp; Analysis Job -> rules + LLM agents -> findings JSON -> Cosmos -> API exposes tiered views



DELIVERY PATH (Tier 3):

&nbsp; Stripe webhook -> Delivery Job -> generate IaC/scripts -> ZIP -> Storage -> SAS link -> client

```



---



If you want the \*\*next “code-ready” artifact\*\*, I can generate:



\* `services/api/app/models/dtos.py` (Pydantic models for the entire contract)

\* `services/api/app/routers/onboarding.py` (preflight endpoint + stubs)

\* `services/api/app/middleware/subscription\_scope.py` (partition enforcement)

\* `services/api/app/azure/\*` probe adapters (Resource Graph / Cost / Advisor / Policy)



Just say “generate the stubs” and I’ll output them in a clean, copy/paste order.



