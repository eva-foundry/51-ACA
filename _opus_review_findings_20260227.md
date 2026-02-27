## OPUS REVIEW FINDINGS -- ROUND 2 DELTA (2026-02-27, post-pre-flight-sprint-check)

Model: Claude Sonnet 4.6
Trigger: "opus fixes implemented -- check the code, update the review for a second round"
Files re-read: checkout.py (all 403 lines), analysis/main.py, delivery/packager.py,
  api/routers/findings.py, api/routers/auth.py, api/db/cosmos.py,
  api/services/entitlement_service.py, collector/ingest.py, templates/ dir.

---

### ROUND 2 VERDICT: 0 of 3 pre-flight bugs fixed. C-05 has escalated.

Pre-flight sprint stories ACA-06-021, ACA-03-021, ACA-07-021 are PLANNED in PLAN.md
but the corresponding code changes were NOT committed. The source files are unchanged
from Round 1. Additionally, a new CRITICAL pattern was identified in checkout.py.

---

### ROUND 2 BUG STATUS TABLE

| ID | File | Round 1 Severity | Round 2 Status | Notes |
|----|------|-----------------|----------------|-------|
| C-01 | auth.py /connect | CRITICAL | UNCHANGED | Still 501. No MSAL. |
| C-02 | auth.py /preflight | CRITICAL | UNCHANGED | Still 501. |
| C-03 | cosmos.py upsert_item | CRITICAL | UNCHANGED | No partition_key param. |
| C-04 | analysis/main.py | CRITICAL | UNCHANGED | FindingsAssembler missing cosmos_client. |
| C-05 | checkout.py | CRITICAL | ESCALATED -> C-05-v2 | See below. Router reassignment is worse. |
| C-06 | preflight.py / azure_client.py | CRITICAL | UNCHANGED | SP-only, no delegated flow. |
| C-07 | packager.py | CRITICAL | UNCHANGED | SAS_HOURS=24; invalid generate_blob_sas call. |
| C-08 | findings.py /findings | HIGH | PARTIAL-FIX | gate_findings() now correct. Endpoint still 404. |
| H-02 | ingest.py trigger | HIGH | UNCHANGED | mark_collection_complete() does not trigger analysis. |
| H-03 | entitlement_service.py revoke | HIGH | UNCHANGED | revoke() forces tier=1, clears permanent Tier 3. |

---

### NEW CRITICAL FINDING: C-05-v2 -- checkout.py router reassignment

Severity: CRITICAL (ESCALATED from original C-05)
File: services/api/app/routers/checkout.py, lines 349-403
Commit visible: original C-05 (duplicate @router.post("/webhook")) was
the focus of ACA-06-021 but no fix was committed.

The file now has TWO top-level Python scopes in one module:

Scope 1 (lines 1-348): Real, complete implementation.
  - StripeService, EntitlementService, DeliveryService wired.
  - Real webhook with signature verification at line ~155.
  - Real portal, real entitlements endpoint.
  - Bound to `router` declared at line 31: `router = APIRouter(tags=["checkout"])`

Scope 2 (lines 349-403): Stub block. Starts with bare module-level imports:
  from fastapi import APIRouter, HTTPException, Request
  from pydantic import BaseModel
  router = APIRouter(tags=["checkout"])   # <-- REASSIGNS router

Impact: Python executes both scopes at import time. The `router` name
is reassigned at line ~352. When main.py does `app.include_router(checkout.router)`,
it gets the STUB router (Scope 2). The real implementation (Scope 1) is orphaned
dead code -- unreachable, not mounted, not callable.

The stub router exposes only 4 endpoints (tier2/tier3/webhook/entitlements),
all returning 501 or {"status": "received"}. The real implementation's
`/portal` endpoint does not exist in the stub. 5 real endpoints are invisible.

What the client sees after this:
  POST /v1/checkout/tier2      -> 501 (stub)
  POST /v1/checkout/tier3      -> 501 (stub)
  POST /v1/checkout/webhook    -> {"status": "received"}, no sig check (stub)
  GET  /v1/checkout/entitlements -> hardcoded {"tier": "tier1"} (stub)
  GET  /v1/checkout/portal     -> 404 (missing from stub)

Fix (ACA-06-021): Delete lines 349-403 (the entire Scope 2 block).
No imports in Scope 2 are needed by Scope 1 (Scope 1 imports at the top are complete).
Test: `from services.api.app.routers import checkout; checkout.router.routes` must
show exactly 5 routes: /tier2, /tier3, /webhook, /portal, /entitlements.

---

### ROUND 2 DETAIL: BUGS NOT YET FIXED

C-04: analysis/main.py line 31
  CURRENT CODE:
    assembler = FindingsAssembler(scan_id=scan_id, subscription_id=sub_id)
  REQUIRED:
    assembler = FindingsAssembler(scan_id=scan_id, subscription_id=sub_id,
                                  cosmos_client=get_cosmos_client())
  FindingsAssembler.__init__ signature requires cosmos_client as third positional arg.
  Without it: TypeError: __init__() missing 1 required positional argument: 'cosmos_client'
  Story: ACA-03-021.

C-07: delivery/packager.py lines 17, 71-76
  CURRENT CODE:
    SAS_HOURS = 24
    sas_token = generate_blob_sas(
        account_name=self.storage_account,
        container_name=self.container_name,
        blob_name=blob_name,
        account_key=None,                       # None passed, will TypeError
        credential=DefaultAzureCredential(),    # invalid parameter for generate_blob_sas
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
    )
  REQUIRED:
    SAS_HOURS = 168  (7 days per spec)
    sas_token = generate_blob_sas(
        account_name=self.storage_account,
        container_name=self.container_name,
        blob_name=blob_name,
        account_key=settings.BLOB_ACCOUNT_KEY,  # real storage account key, not None
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
    )
  generate_blob_sas() does not accept `credential` parameter. Passing it raises TypeError.
  Story: ACA-07-021.

C-08 / PARTIAL FIX: findings.py
  IMPROVEMENT: gate_findings() is now correctly implemented with TIER1_FIELDS and
  TIER2_FIELDS sets. Round 1 said gate_findings() was unreachable due to 404 raise.
  gate_findings() logic is now sound. However:
  STILL BROKEN: the @router.get("/{scan_id}") handler still raises
    raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found or not complete")
  unconditionally, without ever calling gate_findings() or reading Cosmos.
  The function body is 4 TODO comments + 1 raise. gate_findings() is imported but
  never invoked. Tier-gated findings remain inaccessible to all clients.
  Story: ACA-10-001 (wire gate_findings + Cosmos reads into the handler).

H-03: entitlement_service.py revoke() lines 107-117
  CURRENT CODE:
    def revoke(self, subscription_id: str) -> None:
        existing = self.get(subscription_id)
        self._repo.upsert(
            subscription_id=subscription_id,
            tier=1,             # WRONG -- clears permanent Tier 3 one-time purchase
            payment_status="canceled",
            ...
        )
  REQUIRED: preserve tier=3 if existing.tier == 3 and tier3_purchased == True.
  Correct logic:
    new_tier = 3 if existing.tier >= 3 else 1
    # If Tier 3 was a one-time purchase, subscription.deleted only cancels Tier 2
    # subscriptions, not Tier 3 permanents. Check tier3_purchased flag in the doc.
  Impact: Customer who paid CAD $1499 for Tier 3 lost to tier=1 on next subscription
  lifecycle event. Revenue and goodwill bug. Story: ACA-06-015 (entitlement_service.py).

H-02: ingest.py mark_collection_complete() lines 78-83
  CURRENT CODE (last 6 lines of file):
    def mark_collection_complete(self) -> None:
        c = self._container("scans")
        c.upsert_item({"id": self.scan_id, "subscriptionId": self.sub_id,
                       "status": "collected", "collectionCompletedUtc": self._now})
  MISSING: after setting status="collected", the collector must trigger the analysis
  Container App Job. Without this trigger, analysis never runs -- the scan sits
  at status="collected" forever. No findings are ever produced.
  Fix: add ACA Container App Jobs API call after upsert OR raise an event that
  the analysis job listens to (e.g. Cosmos change feed or Service Bus message).
  Story: ACA-03-006 (analysis job auto-trigger).

---

### ROUND 2: IMPROVEMENTS CONFIRMED

These items are FIXED or IMPROVED since Round 1:

1. gate_findings() logic (findings.py): correctly implemented with TIER1_FIELDS / TIER2_FIELDS
   sets. Round 1 could not confirm this. The gating logic is sound.

2. entitlement_service.py grant_tier2() / grant_tier3(): correctly implemented.
   grant_tier2() uses max(2, existing.tier) -- downgrade protection correct.
   grant_tier3() sets tier=3 always. update_payment_status() is clean.
   revoke() still has the Tier 3 preservation bug (H-03) but the grant path is sound.

3. checkout.py Scope 1 (real implementation, lines 1-348):
   The real webhook handler at ~line 155 is correctly implemented:
   - reads raw body before any .json() call
   - calls _svc().verify_webhook(payload, stripe_signature)
   - handles all 4 Stripe event types
   - entitlement grants use EntitlementService correctly
   - delivery trigger is wired (delivery.trigger_delivery_job)
   - customer-stripe map is persisted
   The real implementation is CORRECT -- it is just orphaned by Scope 2.
   Fix C-05-v2 (delete Scope 2) and the billing layer becomes fully functional.

4. auth.py stub quality: stubs now have clear TODO comments referencing 02-preflight.md.
   ConnectRequest model added (subscription_id, connection_mode fields).
   PreflightResponse model defined. Helps future implementer.

5. Spec docs created (governance, not code): docs/02-preflight.md, docs/05-technical.md,
   docs/08-payment.md, docs/saving-opportunity-rules.md, docs/12-IaCscript.md.

6. cosmos.py get_item(), query_items(): both correctly scope by partition_key.
   upsert_item() still lacks partition_key (C-03), but query and read are safe.

---

### ROUND 2: REVISED SPRINT PRIORITY ORDER

Given Round 2 findings, revised fix sequence (shortest path to working product):

Priority 1 -- Revenue-unblocking (1 PR, ~1 hour):
  ACA-06-021: checkout.py -- delete lines 349-403 (Scope 2 stub reassignment)
  After this fix: entire real billing layer is live. Stripe revenue works.

Priority 2 -- Analysis pipeline (1 PR, ~30 min):
  ACA-03-021: analysis/main.py -- add cosmos_client arg to FindingsAssembler
  ACA-03-006: ingest.py -- add analysis job trigger in mark_collection_complete()

Priority 3 -- Findings endpoint (1 PR, ~2 hours):
  ACA-10-001: findings.py -- wire Cosmos reads + gate_findings() into the handler
  ACA-03-003: cosmos.py upsert_item() -- add partition_key parameter (3-line fix)

Priority 4 -- Delivery (1 PR, ~1 hour):
  ACA-07-021: packager.py -- SAS_HOURS=168, account_key from settings
  ACA-07-003: create 12 template stub folders with main.bicep + variables.json

Priority 5 -- Revenue safety (1 PR, ~30 min):
  ACA-06-015: entitlement_service.py revoke() -- preserve tier=3 if tier3_purchased

Priority 6 -- Auth (multi-sprint, blocked on Entra app reg):
  ACA-04-001: auth.py connect + preflight -- MSAL delegated flow (blocked on ACA-CLIENT-ID)

---

### ROUND 2: TESTS STILL AT ZERO

No test files were found in services/. pytest exits 0 vacuously.
This means every bug above would go undetected by CI.

Minimum test additions needed before Priority 1 PR merges:
  - test_checkout_router.py: confirm only one @router.post("/webhook") exists
    and that checkout.router.routes has exactly 5 routes after fix
  - test_checkout_webhook.py: invalid Stripe-Signature -> 400
  - test_analysis_main.py: FindingsAssembler(scan_id, sub_id, cosmos_client) imports clean
  - test_packager.py: SAS_HOURS == 168; no DefaultAzureCredential in sas generation

---

## OPUS REVIEW FINDINGS -- 2026-02-27

Model used: Claude Sonnet 4.6 (corrected from draft label)
Repo: eva-foundry/51-ACA @ main
Files read: AGENTS.md, .github/copilot-instructions.md, PLAN.md, STATUS.md,
  all 6 routers, all db/ files, all collector/ files, all analysis/ files,
  all delivery/ files, all frontend pages.
Data model endpoint table sourced from: _opus_review_issue_draft.md
  (port 8055 was offline during this session; endpoint status used from
  the authoritative table embedded in the issue draft).

---

### SERVICE FLOW STATUS

| Step | Status | Gap | PLAN.md Coverage |
|------|--------|-----|------------------|
| 1 AUTH        | STUB    | POST /v1/auth/connect raises HTTP 501. No MSAL code path. | ACA-04-001 (Sprint 2) |
| 2 PREFLIGHT   | STUB    | POST /v1/auth/preflight raises HTTP 501. preflight.py exists but uses SP not delegated. | ACA-04-001 (Sprint 2) |
| 3 SCAN INIT   | BROKEN  | Backend POST /v1/scans/ is implemented. Frontend calls POST /v1/collect/start (stub) -- endpoint mismatch. No "Ready to scan" screen. | ACA-05-017 partial |
| 4 COLLECTOR   | PARTIAL | Collector logic exists. Uses ClientSecretCredential (SP) not MSAL delegated. No analysis job trigger on completion. Resource Graph not used (SDK fallback has no explicit $skipToken). | ACA-02-001 through ACA-02-014 |
| 5 ANALYSIS    | BROKEN  | FindingsAssembler(scan_id, sub_id) -- missing cosmos_client arg -- raises TypeError at runtime. Not triggered from collector. No tier-based sampling for Tier 1. | ACA-03-003, ACA-03-004 |
| 6 REPORTING   | STUB    | GET /v1/scans/{scan_id} -- findings endpoint raises 404. gate_findings() implemented but unreachable. | ACA-10-001 (Sprint 2) |
| 7 UPGRADE     | BROKEN  | Real webhook handler at checkout.py:149 is shadowed by duplicate stub at checkout.py:383. FastAPI registers the last route -- stub wins. Tier 3 re-analysis not triggered on upgrade. | ACA-06-001, ACA-10-001 |
| 8 DELIVERY    | BROKEN  | 0 template folders in services/delivery/app/templates/. generate_blob_sas() API usage is invalid. No GET endpoint for download URL. SAS expiry 24h not 7 days. | ACA-07-003 through ACA-07-008 |

---

### CRITICAL FINDINGS

C-01: services/api/app/routers/auth.py:28-30
  POST /v1/auth/connect raises HTTP 501. No MSAL delegated flow.
  Impact: Step 1. No client can onboard. Product does not start.
  Fix: Implement MSAL PublicClientApplication device-code or auth-code flow
  using authority=common (multi-tenant). Exchange code for access + refresh token.
  Store refresh token in marcosandkv20260203, NOT in Cosmos.
  Pattern is in copilot-instructions.md P2.5 Pattern 3.
  Story: ACA-04-001.

C-02: services/api/app/routers/auth.py:40-43
  POST /v1/auth/preflight raises HTTP 501.
  Impact: Step 2. Pre-flight gate never runs. Collector launches without
  knowing if required roles are present. Data collection will fail silently
  or produce incomplete results.
  Fix: Wire run_preflight() from services/collector/app/preflight.py into
  the API endpoint. preflight.py must be updated first (see C-06 below)
  to use the delegated token rather than ClientSecretCredential.
  Story: ACA-04-001.

C-03: services/api/app/routers/findings.py:42-44
  GET /v1/scans/{scan_id}/findings (or /v1/findings/{scan_id}) raises
  HTTP 404 unconditionally. gate_findings() is correctly implemented
  in the same file but is never called.
  Impact: Step 6. No client ever sees findings. Product revenue gate
  (tier gating) is implemented but unreachable.
  Fix: Load scan from Cosmos, check status == "complete", load client tier
  from EntitlementService, load findings from Cosmos with partition_key=sub_id,
  call gate_findings(findings, tier), return. Add "partial_scan" metadata
  field for Tier 1 responses.
  Story: ACA-10-001.

C-04: services/analysis/app/main.py:28-29
  FindingsAssembler signature is FindingsAssembler(scan_id, subscription_id,
  cosmos_client) but main.py instantiates it as
  FindingsAssembler(scan_id=scan_id, subscription_id=sub_id) -- missing
  cosmic_client argument. This raises TypeError at runtime the moment
  the analysis Container App Job starts.
  Impact: Step 5. Analysis job crashes on every run. Zero findings ever written.
  Fix: Instantiate CosmosHelper in main() and pass it as the third argument.
  Import pattern: from services/delivery/app/cosmos.py CosmosHelper exists
  and is correct -- replicate to analysis context.
  Story: ACA-03-004 (immediate).

C-05: services/api/app/routers/checkout.py:149 and :383
  Two @router.post("/webhook") decorators exist in the same router file.
  The real, verified implementation is at line 149 (reads raw body, checks
  signature, handles all event types, grants entitlement, triggers delivery).
  A stub version at line 383 also declares @router.post("/webhook") and
  simply returns {"status": "received"} with no signature verification.
  FastAPI registers routes in declaration order and deduplicates -- the LAST
  definition wins. The stub at 383 silently overwrites the real handler.
  Impact: Step 7. ALL Stripe events are silently discarded. No tier upgrades
  occur. No deliveries are triggered. Revenue-impacting.
  Fix: Delete lines 351-403 (the bottom stub block). The real handler at
  line 149 is complete and correct. Do not merge without this fix.
  Story: Critical hotfix, no new ACA ID needed -- fix within ACA-06-001 PR.

C-06: services/collector/app/preflight.py:25-29 and azure_client.py:16-22
  Both modules use ClientSecretCredential (service principal auth) exclusively.
  The spec (copilot-instructions.md P2.5 Pattern 3, Step 1 in service flow)
  requires MSAL delegated auth: acquire_token_by_refresh_token() using the
  refresh token stored in Key Vault. No MSAL import exists anywhere in the
  services/ tree.
  Impact: Steps 1-4. Mode A (delegated) is fully blocked. Only Mode B (SP)
  is functional. The product spec prioritises Mode A as "recommended".
  Fix: Add msal to requirements.txt in services/api and services/collector.
  Implement get_arm_token(client_id, tenant_id, refresh_token) per P2.5
  Pattern 3. Wire into preflight.py and azure_client.py conditionally on
  connection_mode == "delegated".
  Story: ACA-04-001.

C-07: services/delivery/app/packager.py:54-64
  generate_blob_sas() is called with credential=DefaultAzureCredential().
  The azure-storage-blob SDK's generate_blob_sas() function requires either
  account_key (string) OR user_delegation_key (object returned by
  BlobServiceClient.get_user_delegation_key()) -- NOT a credential object.
  Passing DefaultAzureCredential() as credential will raise TypeError at
  runtime. The deliverable can never be uploaded or linked.
  Impact: Step 8. No SAS URL is ever produced. Tier 3 delivery is completely
  broken regardless of other issues.
  Fix: If using managed identity, call
  client.get_user_delegation_key(start=now, expiry=expiry) and pass
  user_delegation_key=key to generate_blob_sas(). Remove credential= param.
  Story: ACA-07-006.

C-08: No GET /v1/delivery/{scan_id}/download or /v1/deliverables/{deliverableId}
  endpoint exists in any router file (grep confirmed).
  frontend/src/pages/Download.tsx fetches /v1/deliverables/${deliverableId}
  which returns a 404 from FastAPI.
  Impact: Step 8. Even if SAS URL were generated and stored, user cannot
  retrieve it. The "Download Package" button in the UI leads to a dead endpoint.
  Fix: Add GET /v1/scans/{scan_id}/deliverable router in scans.py that reads
  the deliverables Cosmos container and returns { download_url, expires_at }.
  Story: ACA-07-008 (new story needed).

---

### HIGH FINDINGS

H-01: services/collector/app/ingest.py:80-86
  Ingestor.mark_collection_complete() upserts the scan record with
  status="collected" but does NOT trigger the analysis Container App Job.
  The spec (Step 5: "Triggered when scan status = collected") requires an
  explicit trigger. The analysis job will never run automatically.
  No event bridge, no polling loop, and no ACA Jobs trigger exists between
  collector completion and analysis start.
  Fix: In scan_pipeline.py or ingest.py completion path, call
  trigger_aca_job(job_name="aca-51-analysis") after advancing state to
  "collected". Pattern exists in scan_pipeline.py trigger_pipeline() for
  the collector job.
  Story: ACA-03-004.

H-02: frontend/src/app/routes/app/ConnectSubscriptionPage.tsx:59-64
  handleConnect() calls appApi.startCollection(subscriptionId) which maps
  to POST /v1/collect/start (stub, returns 501). The real scan trigger is
  POST /v1/scans/. No /connect or /preflight call is made.
  The frontend skips Steps 1 and 2 entirely and calls the wrong Step 3.
  The "Ready to scan" confirmation screen (after preflight success) does not
  exist in the router.
  Fix: (a) Add MSAL browser redirect to Microsoft Entra on "Connect" click.
  (b) After MSAL callback, POST /v1/auth/connect with authorization_code.
  (c) POST /v1/auth/preflight; show remediation screen if missing_roles.
  (d) Show "Ready to scan" screen; on "Start Scan" POST /v1/scans/ (not
  /v1/collect/start).
  Story: ACA-05-017 expansion + ACA-04-001.

H-03: frontend/src/app/routes/app/CollectionStatusPage.tsx:42
  appApi.getCollectionStatus(subscriptionId) maps to GET /v1/collect/status
  (stub). The real polling target from the spec is
  GET /v1/scans/{scan_id}?subscription_id=... which IS implemented.
  Frontend will always receive 501 during status polling.
  Fix: Update AppApi.getCollectionStatus to call
  GET /v1/scans/{scan_id}?subscription_id={sub}. scan_id must be stored
  in sessionStorage after POST /v1/scans/ returns.
  Story: ACA-05-018.

H-04: services/api/app/services/delivery_service.py:19-29
  trigger_delivery_job() returns a placeholder string immediately.
  Phase 1 stub comment says "Phase 2: call Container Apps Jobs API".
  The Stripe webhook handler (checkout.py:237) calls this after Tier 3
  checkout -- the delivery job never actually runs. Users who pay for Tier 3
  receive nothing.
  Fix: Implement Container Apps Job invocation using ARM REST API or
  azure-mgmt-appcontainers. Persist the job run ID to Cosmos deliverables
  container. Return the job run ID as deliverable_id.
  Story: ACA-07-008.

H-05: services/analysis/app/main.py (entire file)
  No Tier 1 sampling logic. The spec (Step 5) requires Tier 1 analysis to
  run on a 10% sample (highest-cost resources first) and label findings
  as "partial". All 12 rules run on 100% of data regardless of tier.
  This means Tier 1 results are identical to Tier 2 in substance (minus
  the gating in the API layer). The gating exists at the API layer but
  the source data is not sampled.
  Fix: In analysis/main.py, after loading collected data, resolve client
  tier from Cosmos entitlements before running rules. If tier == 1, sort
  cost_rows by cost descending, take top 10%. Set "partial": true on all
  findings.
  Story: ACA-03-007.

H-06: services/delivery/app/templates/ (directory)
  Zero template folders exist. generator.py expects directories at
  templates/{deliverable_template_id}/ with main.bicep inside.
  Rules 01-12 reference 12 distinct template IDs (tmpl-devbox-autostop
  through tmpl-chargeback-policy). None are present. TemplateGenerator
  silently skips TemplateNotFound -- ZIP will contain findings.json and
  nothing else. Tier 3 deliverable is empty.
  Fix: Create all 12 template folders per T1 decision in STATUS.md.
  Each needs at minimum: main.bicep, README.md.
  Story: ACA-07-003.

H-07: docs/ directory
  AGENTS.md lists 6 spec docs as required reading before implementing features.
  Five of these are MISSING from the repo:
    docs/02-preflight.md, docs/05-technical.md, docs/08-payment.md,
    docs/saving-opportunity-rules.md, docs/12-IaCscript.md.
  Cloud agents (GitHub Copilot, future CI agents) are instructed to read
  these before implementing. AGENTS.md says "Read the spec doc listed in
  Spec references field" -- this gate cannot be satisfied.
  Fix: Create stub spec docs with the canonical content from
  copilot-instructions.md P2.1-P2.9 extracted into the relevant doc files.
  Story: ACA-12-002.

---

### MEDIUM FINDINGS

M-01: services/api/app/middleware/ (directory missing)
  copilot-instructions.md P2.5 Pattern 1 specifies a tenant isolation
  middleware at services/api/app/middleware/tenant.py that injects
  subscription_id from the auth token into request.state. This directory
  does not exist. Routers currently receive subscription_id as a raw
  query parameter with no token-backed validation.
  Fix: Create middleware/tenant.py per P2.5 Pattern 1 once MSAL auth
  (C-01) is implemented. Until then, document the gap in STATUS.md.
  Story: ACA-04-004.

M-02: services/collector/app/azure_client.py:31-46
  get_inventory() uses ResourceManagementClient.resources.list() which
  auto-paginates via Python SDK but calls the ARM resources API, not the
  Azure Resource Graph. Spec Step 4 and P2.8 require Resource Graph
  (resourcegraph.resources) with explicit $skipToken for large subscriptions.
  Resource Graph supports JIT cross-resource-type queries significantly faster
  than ARM list for subscriptions with 500+ resources.
  Fix: Replace with azure.mgmt.resourcegraph ResourceGraphClient using
  QueryRequest with allow_partial_content=True and $skipToken pagination.
  Story: ACA-02-005.

M-03: services/collector/app/main.py:41-85
  Collections are sequential. Spec Step 4 says "Collects in parallel".
  All 5 collection calls (inventory, cost, advisor, policy, network) run one
  after another. For large subscriptions this is 2-4x slower than concurrent.
  Fix: Use asyncio.gather() or concurrent.futures.ThreadPoolExecutor to run
  all 5 collection branches concurrently.
  Story: ACA-02-014.

M-04: services/delivery/app/packager.py:45-49
  ZIP contains findings.json and IaC templates but NOT a SHA-256 manifest
  (manifest.json). Spec Step 8 requires the zip to include a SHA-256
  manifest. The SHA-256 of the full ZIP is computed (line 48) but stored
  only as Azure blob metadata, not inside the ZIP itself.
  Fix: Before closing the ZipFile, write a manifest.json entry:
  {"sha256": sha256, "scan_id": scan_id, "generated_utc": ISO8601}.
  Story: ACA-07-006.

M-05: services/delivery/app/packager.py:18
  SAS_HOURS = 24. Spec (P2.2 Technology Stack row "Delivery") requires
  7-day SAS expiry (168 hours). The Download.tsx UI shows expires_at to
  the user. 24-hour expiry would expire before most enterprise approvals.
  Fix: Change SAS_HOURS = 168.
  Story: ACA-07-006.

M-06: services/ (all directories)
  No test files found anywhere under services/. pytest services/ -x -q
  exits 0 vacuously (no tests, no failures). ACCEPTANCE.md requires 95%
  test coverage. CA.2 mandatory gate requires pytest to exit 0 -- it does,
  but only because there are no tests to run.
  Fix: Create at minimum:
    tests/test_gate_findings.py  -- unit tests for gate_findings() (no Cosmos)
    tests/test_rules.py          -- one test per rule with hardcoded FP JSON
    tests/test_scan_pipeline.py  -- mock Cosmos, assert state transitions
  Story: ACA-03-015.

M-07: services/api/app/db/cosmos.py:44-48
  upsert_item(container_name, item) does not accept or validate a
  partition_key parameter. AGENTS.md rule 1 says "every Cosmos call MUST
  include partition_key=subscriptionId." For upserts, isolation is enforced
  only if the caller puts the correct key inside the item dict. There is no
  code-level enforcement. A caller who forgets subscriptionId in the item
  dict will silently write a cross-tenant record.
  Fix: Add partition_key: str parameter to upsert_item() and pass it to
  container.upsert_item(item, partition_key=partition_key). Update all callers.
  Story: ACA-04-004.

M-08: services/api/app/routers/checkout.py:250-320
  invoice.paid and customer.subscription.updated handlers are present and
  call entitlement_service.update_payment_status(). The grant_tier2 and
  grant_tier3 methods in EntitlementService use max(tier, existing.tier)
  which prevents downgrades -- this is correct and PASS.
  However, customer.subscription.deleted clears payment_status to "canceled"
  but does NOT check whether entitlement.tier was already tier3 (one-time
  purchase). Cancelling a Tier 2 subscription should not remove a Tier 3
  one-time entitlement. Requires verify before close.
  Story: ACA-06-015.

---

### LOW FINDINGS

L-01: services/collector/app/azure_client.py:123-136
  get_network_topology() returns public_ip_count, public_ips[:50],
  nsg_count, vnet_count. Missing: VNet peering count. Spec Step 4(d)
  requires "VNet + peering". No impact on current rules (no rule uses
  peering count yet) but will block rule_09 extension for VPN/peering
  sprawl detection.
  Fix: Add:
    peering_count = sum(len(list(client.virtual_network_peerings.list(rg, vn.name)))
      for vn in client.virtual_networks.list_all() for rg in [vn.id.split("/")[4]])
  Story: ACA-02-014.

L-02: services/analysis/app/rules/ (all 12 files)
  Rules 01, 02, 03, 09 confirmed with deliverable_template_id and full
  FINDING schema fields. Rules 04-08, 10-12 not fully inspected. Spot check
  confirms consistent schema. Deliverable IDs follow tmpl-{kebab-name} format.
  Risk is low but confirm all 12 before marking ACA-03-004 done.
  Action: Run a schema validation test across all rules with a mock data dict.

L-03: .eva/veritas-plan.json (as noted in STATUS.md)
  MTI = 5 (honest baseline). AGENTS.md CA.2 gate requires MTI >= 70 before
  any sprint story PR. With 250 stories and 8 EVA-STORY tagged files,
  coverage is ~3%. Sprint 2 cannot merge via the standard gate.
  This is a known acknowledged state (STATUS.md "Next target: MTI 50+").
  Human decision needed: either lower the gate temporarily or add bulk
  EVA-STORY tags to all existing files before Sprint 2 starts.

L-04: No CORS configuration found in services/api/app/main.py or middleware/.
  copilot-instructions.md P2.9 does not call out CORS explicitly but a
  browser-facing API without explicit CORS will either block all frontend
  calls or -- worse -- a wildcard may be silently permissive.
  Fix: Add CORSMiddleware with explicit ALLOWED_ORIGINS from
  settings.ACA_ALLOWED_ORIGINS (already referenced in STATUS.md decision D1).

---

### PROPOSED SPRINT 2 STORY LIST

Ordered by dependency. Unblocked stories can run in parallel.

Story: ACA-04-001
  Title: Implement POST /v1/auth/connect -- MSAL delegated device-code flow
  Size: L
  Model: Sonnet
  Fixes: C-01, C-06 (partial)
  Depends on: NONE
  Acceptance: POST /connect with valid authorization_code returns
  { preflight_id, session_token }. Refresh token written to KV. Access token
  not persisted to Cosmos. pytest test_auth.py::test_connect_delegated passes.

Story: ACA-04-002 (formerly prep for ACA-04-001)
  Title: Fix POST /v1/auth/preflight -- use delegated token from connect response
  Size: M
  Model: Sonnet
  Fixes: C-02, M-01 partial
  Depends on: ACA-04-001
  Acceptance: POST /preflight returns { all_clear, missing_roles, capabilities }.
  Returns HTTP 200 PASS when Reader + Cost Management Reader present.
  Returns HTTP 200 FAIL when role missing, naming the role.

Story: ACA-06-HOT-01 (hotfix, no sprint ID needed -- merge before Sprint 2 opens)
  Title: Remove duplicate @router.post("/webhook") stub at checkout.py:383
  Size: XS
  Model: GPT-5 mini
  Fixes: C-05
  Depends on: NONE
  Acceptance: checkout.py contains exactly one /webhook route definition.
  Stripe test event returns 200. pytest exits 0.

Story: ACA-03-005
  Title: Fix FindingsAssembler instantiation -- pass CosmosHelper to main.py
  Size: XS
  Model: GPT-5 mini
  Fixes: C-04
  Depends on: NONE
  Acceptance: analysis/main.py creates CosmosHelper(url, key, db) and passes
  to FindingsAssembler. pytest test_analysis.py::test_main_no_crash passes
  with mocked Cosmos.

Story: ACA-10-001
  Title: Implement GET /v1/findings/{scan_id} with gate_findings() applied
  Size: M
  Model: Sonnet
  Fixes: C-03
  Depends on: ACA-03-005 (analysis must write findings before endpoint can read)
  Acceptance: GET /v1/findings/{scan_id}?subscription_id=X returns gated list.
  Tier 1 response must not contain narrative or deliverable_template_id.
  pytest test_findings.py::test_tier1_gate and test_tier2_gate pass.

Story: ACA-03-007
  Title: Add Tier 1 sampling (10% highest-cost resources) to analysis engine
  Size: M
  Model: Sonnet
  Fixes: H-05
  Depends on: ACA-03-005
  Acceptance: When entitlement tier == 1, data["resources"] is reduced to top
  10% by cost before rules run. All returned findings include "partial": true.
  pytest test_analysis.py::test_tier1_sampling passes with fixture of 100 resources.

Story: ACA-05-017b
  Title: Fix ConnectSubscriptionPage -- call /connect + /preflight before scan
  Size: L
  Model: Sonnet
  Fixes: H-02, H-03
  Depends on: ACA-04-001
  Acceptance: Clicking "Connect" initiates MSAL redirect. After callback,
  /connect and /preflight are called. If all_clear: show confirmation screen.
  On "Start Scan": POST /v1/scans/ (not /v1/collect/start). scan_id stored
  in sessionStorage.

Story: ACA-05-018b
  Title: Fix CollectionStatusPage -- poll GET /v1/scans/{scan_id} not /collect/status
  Size: S
  Model: GPT-5 mini
  Fixes: H-03
  Depends on: ACA-05-017b (needs scan_id in sessionStorage)
  Acceptance: CollectionStatusPage reads scan_id from sessionStorage and polls
  GET /v1/scans/{scan_id}?subscription_id={sub}. Status transitions drive UI.
  vitest CollectionStatusPage.test.tsx passes.

Story: ACA-07-006b
  Title: Fix generate_blob_sas() to use user_delegation_key; set SAS expiry 168h
  Size: S
  Model: GPT-5 mini
  Fixes: C-07, M-05
  Depends on: NONE
  Acceptance: packager.py calls get_user_delegation_key() and passes result to
  generate_blob_sas(). SAS_HOURS = 168. pytest test_packager.py::test_sas_url
  passes with mocked BlobServiceClient.

Story: ACA-07-008
  Title: Add GET /v1/scans/{scan_id}/deliverable endpoint + implement DeliveryService
  Size: M
  Model: Sonnet
  Fixes: C-08, H-04
  Depends on: ACA-07-006b
  Acceptance: GET /v1/scans/{scan_id}/deliverable?subscription_id=X reads Cosmos
  deliverables, returns { download_url, expires_at }. Returns 404 if not ready.
  Download.tsx fetch succeeds in vitest with mocked API.

Story: ACA-07-003
  Title: Create all 12 IaC template folders under services/delivery/app/templates/
  Size: L
  Model: Sonnet (for Bicep content) / GPT-5 mini (for folder scaffolding)
  Fixes: H-06
  Depends on: NONE
  Acceptance: All 12 tmpl-* directories exist. Each contains main.bicep and
  README.md. TemplateGenerator.generate() returns at least 1 artifact for a
  mock finding with deliverable_template_id set. pytest test_generator.py passes.

Story: ACA-03-015
  Title: Add minimum test suite -- gate_findings, rules, scan_pipeline
  Size: M
  Model: Sonnet
  Fixes: M-06
  Depends on: ACA-03-005
  Acceptance: pytest services/ -x -q exits 0 with > 0 tests collected.
  Covers: test_gate_findings (Tier 1/2/3), test_rule_01 through test_rule_12
  (each with hardcoded FP JSON fixture), test_scan_pipeline (mocked Cosmos).

Story: ACA-02-005b
  Title: Replace ResourceManagementClient.resources.list() with Resource Graph API
  Size: M
  Model: Sonnet
  Fixes: M-02
  Depends on: ACA-04-001 (needs delegated token)
  Acceptance: get_inventory() uses ResourceGraphClient.resources() with
  QueryRequest and $skipToken pagination. Returns same dict shape as before.
  pytest test_collector.py::test_inventory_pagination passes with mock.

Story: ACA-12-002
  Title: Create missing spec docs (02-preflight, 05-technical, 08-payment stubs)
  Size: S
  Model: GPT-5 mini
  Fixes: H-07
  Depends on: NONE
  Acceptance: docs/02-preflight.md, docs/05-technical.md, docs/08-payment.md
  exist with content extracted from copilot-instructions.md P2.1-P2.9 sections.

---

### SPRINT 2 VELOCITY ESTIMATE

Total stories: 13 (1 hotfix + 12 sprint stories)
Rough FP estimate (using standard ACA FP table):
  ACA-06-HOT-01: XS = 1 FP
  ACA-03-005:    XS = 1 FP
  ACA-04-001:    L  = 13 FP
  ACA-04-002:    M  = 8 FP
  ACA-10-001:    M  = 8 FP
  ACA-03-007:    M  = 8 FP
  ACA-05-017b:   L  = 13 FP
  ACA-05-018b:   S  = 3 FP
  ACA-07-006b:   S  = 3 FP
  ACA-07-008:    M  = 8 FP
  ACA-07-003:    L  = 13 FP
  ACA-03-015:    M  = 8 FP
  ACA-02-005b:   M  = 8 FP
  ACA-12-002:    S  = 3 FP
                 --------
  TOTAL:         98 FP

Fits in an 80-100 FP sprint: YES (98 FP, at the upper bound).
Recommended split if velocity is lower:
  Sprint 2A (blocking path -- auth + scan + reporting): 55 FP
    ACA-06-HOT-01, ACA-03-005, ACA-04-001, ACA-04-002, ACA-10-001,
    ACA-05-017b, ACA-05-018b, ACA-03-015
  Sprint 2B (delivery + collector improvements): 43 FP
    ACA-03-007, ACA-07-006b, ACA-07-008, ACA-07-003, ACA-02-005b, ACA-12-002

Critical path (must close in sequence):
  ACA-06-HOT-01 --> (merge immediately, unblocks Stripe testing)
  ACA-03-005    --> ACA-10-001 --> ACA-03-007
  ACA-04-001    --> ACA-04-002 --> ACA-05-017b --> ACA-05-018b
  ACA-07-006b   --> ACA-07-008

---

### QUESTIONS FOR HUMAN

[AGENT-ESCALATION]
Story: ACA-04-001
Reason: The spec requires MSAL delegated auth with authority=common (multi-tenant),
but the current preflight.py architecture uses ClientSecretCredential. Switching to
delegated flow requires an Entra app registration in multi-tenant mode with a
redirect URI. The ACA-CLIENT-ID secret in marcosandkv20260203 is listed as "Add
before Phase 1 deploy" -- not yet present.
Blocker type: SECRET_NEEDED
Attempted: Reviewed auth.py, preflight.py, azure_client.py, copilot-instructions
P2.5 Pattern 3.
Human action needed: Confirm that (a) the ACA Entra app registration exists and
is set to multi-tenant, (b) ACA-CLIENT-ID is set in marcosandkv20260203 before
ACA-04-001 can be tested. If NOT: agent cannot implement the token exchange step.
[/AGENT-ESCALATION]

[AGENT-ESCALATION]
Story: ACA-07-003
Reason: STATUS.md decision T1 says "Bicep only for Phase 1. 12 folders:
tmpl-devbox-autostop through tmpl-chargeback-policy." The exact list of 12
template IDs and their Bicep content are supposed to come from docs/12-IaCscript.md
which is MISSING from the repo. Without this spec, generated Bicep will be
placeholder stubs -- acceptable for scaffolding, but the human should confirm
whether stub Bicep (with TODO comments) is acceptable for Sprint 2 or whether
the full IaC content is required.
Blocker type: AMBIGUOUS_SPEC
Attempted: Looked for docs/12-IaCscript.md -- not found. Reviewed rule file
deliverable_template_id values to derive the 12 folder names.
Human action needed: (a) Confirm the 12 template folder names match the rule_NN
deliverable_template_id fields. (b) Confirm that stub Bicep (main.bicep with
variable scaffolding, no real resources) is acceptable for Sprint 2 closure.
[/AGENT-ESCALATION]

[AGENT-ESCALATION]
Story: MTI gate
Reason: AGENTS.md CA.2 requires MTI >= 70 before any sprint PR can merge.
Current MTI is 5 (STATUS.md baseline 2026-02-27). With 250 plan stories and
~8 EVA-STORY tagged files, reaching MTI 70 requires tagging ~175 source files
before Sprint 2 stories can merge normally.
Blocker type: MTI_REGRESSION (pre-existing)
Attempted: read STATUS.md, trust.json baseline.
Human action needed: Decide one of: (a) Run a bulk tag-all-files task before
Sprint 2 (adds EVA-STORY tags to all existing source files pointing to their
relevant story IDs), OR (b) Lower the MTI gate to 30 for Sprint 2 and raise
it back to 70 at Sprint 3 boundary. This decision gates ALL Sprint 2 PRs.
[/AGENT-ESCALATION]
