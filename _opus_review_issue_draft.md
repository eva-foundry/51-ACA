## TITLE
[OPUS-REVIEW] Sprint 2 architecture review -- service flow, gap analysis, sprint backlog proposal

## LABEL
opus-review

## MODEL
Claude Sonnet 4.6

---

## BODY

INSTRUCTIONS FOR CLAUDE SONNET 4.6
====================================

This is a READ-ONLY analysis task. Do NOT write code. Do NOT open PRs.
Do NOT commit. Your only deliverable is a structured comment on this issue.

Read AGENTS.md and .github/copilot-instructions.md in full before doing
anything else. They are your operating contract for this repo.

---

INTENDED SERVICE FLOW (source of truth)
-----------------------------------------

This is what the product is supposed to do, end to end. Your job is to
verify that the current codebase actually delivers this flow, identify every
gap, and propose the ordered Sprint 2 story list to close them.

STEP 1 -- AUTHENTICATION
  User lands on the ACA frontend (/login).
  They click "Connect your Azure subscription".
  Frontend redirects to Microsoft Entra (authority=common, multi-tenant).
  User signs in with their Microsoft account (any tenant, not EsDAICoE).
  MSAL returns an authorization code.
  Frontend POSTs to: POST /v1/auth/connect
    Body: { authorization_code, tenant_id, subscription_id }
  API exchanges code for access_token + refresh_token via MSAL delegated flow.
  Refresh token is stored in Key Vault (NOT Cosmos).
  access_token is used immediately for pre-flight. It is NOT stored.

STEP 2 -- PRE-FLIGHT PROBE
  POST /v1/auth/preflight is called immediately after /connect succeeds.
  The pre-flight probe verifies the access_token has the required RBAC roles
  on the specified subscription:
    - Reader (required)
    - Cost Management Reader (required)
    - Advisor Reader or Reader is sufficient (required)
    - Network Contributor is optional (used for network topology)
  Returns: { all_clear: bool, missing_roles: [], capabilities: {} }
  If all_clear is false: frontend shows a "Grant permissions" remediation screen.
  If all_clear is true: frontend shows a "Ready to scan" confirmation screen.

STEP 3 -- CLIENT CONFIRMS / SCAN INITIATED
  User clicks "Start Scan" on the confirmation screen.
  Frontend POSTs to: POST /v1/scans  (or equivalent trigger endpoint)
  API creates a scan record in Cosmos (container: scans, partition: subscriptionId).
  API triggers the collector Container App Job asynchronously.
  Frontend polls: GET /v1/scans/{scan_id} for status (queued/running/done/failed).

STEP 4 -- COLLECTOR JOB (runs as Azure Container App Job)
  Collector reads the scan record from Cosmos to get subscriptionId + refresh token ref.
  Gets a fresh access_token from Key Vault refresh token via MSAL.
  Collects in parallel:
    a) Resource inventory via Azure Resource Graph (all resource types, all RGs)
       -- paginated with $skipToken until no more pages
       -- written to Cosmos container: inventories, partition: subscriptionId
    b) Daily cost data: 91 days of daily granularity via Cost Management API
       -- written to Cosmos container: cost-data, partition: subscriptionId
    c) Azure Advisor recommendations: all categories (Cost, Security, Reliability,
       Performance, OperationalExcellence)
       -- written to Cosmos container: advisor, partition: subscriptionId
    d) Network topology: VNet list + peering + public IPs + NSG rules
       -- appended to inventories container
  On completion: updates scan record status to "collected".
  On failure: updates status to "failed", writes error detail.

STEP 5 -- ANALYSIS JOB (runs as Azure Container App Job)
  Triggered when scan status = "collected".
  Reads inventory + cost-data + advisor from Cosmos for this subscriptionId.
  Determines scope based on entitlement tier:
    Tier 1 (free):  analyze a representative 10% sample of resource inventory.
                    Sample selection: highest-cost resources first.
                    Rules R-01 through R-12 run, but only on sampled resources.
                    Estimated savings reflect sampled scope -- labelled as "partial".
    Tier 2 (paid):  analyze 100% of resource inventory.
                    All 12 rules run on full data set.
    Tier 3 (paid):  same as Tier 2, plus deliverable_template_id is populated
                    in every finding that has a matching template.
  Results: a findings list conforming to the FINDING schema (see copilot-instructions P2.5).
  Written to Cosmos container: findings, partition: subscriptionId.
  Scan status updated to "analyzed".

STEP 6 -- REPORTING (API + frontend)
  GET /v1/scans/{scan_id}/findings
  API calls gate_findings(findings, tier) before returning:
    Tier 1: returns { id, title, category, estimated_saving_low,
                      estimated_saving_high, effort_class } only.
             narrative and deliverable_template_id are stripped.
             A "partial scan" banner is included in the response metadata.
    Tier 2: returns all fields except deliverable_template_id.
    Tier 3: returns full FINDING object including deliverable_template_id.
  Frontend renders:
    Tier 1: OpportunityCard list with SavingsBar + TierGate CTA ("See full report").
    Tier 2: Full findings dashboard with narrative, effort, risk classifications.
    Tier 3: Full dashboard + "Download Package" button.

STEP 7 -- UPGRADE FLOW (Tier 1 -> Tier 2 or Tier 3)
  User clicks "See full report" or "Download Package" CTA.
  Frontend redirects to checkout page.
  POST /v1/checkout/tier2 or POST /v1/checkout/tier3
    Creates Stripe Checkout Session with allow_promotion_codes=true.
    Stores pending entitlement in Cosmos (status: pending_payment).
  Stripe redirects to success URL after payment.
  Stripe fires webhook to POST /v1/checkout/webhook.
  Webhook handler:
    1. await request.body() BEFORE any JSON parsing (mandatory).
    2. Verifies Stripe signature with STRIPE_WEBHOOK_SECRET.
    3. On checkout.session.completed: upgrades entitlement in Cosmos.
    4. Re-triggers analysis job at new tier scope.
    5. Idempotent: double-delivery of same event does not double-upgrade.

STEP 8 -- DELIVERY (Tier 3 only)
  User clicks "Download Package".
  GET /v1/delivery/{scan_id}/download
  API triggers delivery Container App Job.
  Delivery job:
    Reads findings from Cosmos for this subscriptionId + scan_id.
    For each finding with deliverable_template_id:
      Loads Jinja2 template from templates/{deliverable_template_id}/
      Renders template with finding fields + subscription context.
    Assembles zip with:
      - All rendered templates (Bicep + optional scripts)
      - SHA-256 manifest (manifest.json)
      - Implementation guide PDF (or .md)
    Uploads zip to Azure Blob Storage (marcosand20260203).
    Generates SAS URL with 7-day expiry.
    Writes SAS URL to scan record in Cosmos.
  API returns { download_url: <SAS URL>, expires_at: <ISO8601> }.

---

REVIEW CHECKLIST
-----------------

For each gap, classify:
  [CRITICAL]  Blocks production go-live (security, data loss, broken flow)
  [HIGH]      Breaks a step in the service flow above
  [MEDIUM]    Degrades quality, coverage, or test safety
  [LOW]       Nice to have

GROUND TRUTH FROM DATA MODEL (port 8055, SQLite, generated 2026-02-27)
------------------------------------------------------------------------
Total objects: 325. Endpoints: 27. Source: GET http://localhost:8055/model/endpoints/

ENDPOINT STATUS TABLE (authoritative -- do NOT re-derive from file scan)
  IMPLEMENTED:
    GET  /health
    GET  /v1/admin/stats
    GET  /v1/checkout/entitlements
    GET  /v1/findings/{scan_id}
    GET  /v1/scans/
    GET  /v1/scans/{scan_id}
    POST /v1/auth/connect
    POST /v1/auth/disconnect
    POST /v1/auth/preflight
    POST /v1/checkout/tier2
    POST /v1/checkout/tier3
    POST /v1/checkout/webhook
    POST /v1/scans/
    DELETE /v1/admin/scans/{scan_id}

  STUB (route exists, logic not implemented):
    GET  /v1/admin/customers
    GET  /v1/admin/kpis
    GET  /v1/admin/runs
    GET  /v1/billing/portal
    GET  /v1/collect/status
    GET  /v1/entitlements
    GET  /v1/reports/tier1
    POST /v1/admin/entitlements/grant
    POST /v1/admin/stripe/reconcile
    POST /v1/admin/subscriptions/{subscriptionId}/lock
    POST /v1/billing/checkout
    POST /v1/collect/start
    POST /v1/webhooks/stripe

MISSING SPEC DOCS (files listed in original read-list that do NOT exist on disk):
  MISSING: docs/02-preflight.md
  MISSING: docs/05-technical.md
  MISSING: docs/08-payment.md
  MISSING: docs/saving-opportunity-rules.md
  MISSING: docs/12-IaCscript.md
  MISSING: services/api/app/middleware/   (directory does not exist)
  PRESENT: services/api/app/routers/      (6 files: admin.py auth.py checkout.py findings.py health.py scans.py)
  PRESENT: services/api/app/db/
  PRESENT: services/collector/app/
  PRESENT: services/analysis/app/
  PRESENT: services/delivery/app/
  PRESENT: frontend/src/pages/
  MTI: 100 (coverage=1.0, evidence=1.0, consistency=1.0) -- trust.json 2026-02-27

FILES TO READ (in this order)
  1. AGENTS.md
  2. .github/copilot-instructions.md
  3. PLAN.md + STATUS.md + ACCEPTANCE.md
  4. services/api/app/routers/       (all 6 files)
  5. services/api/app/db/           (all files)
  6. services/collector/app/        (all files)
  7. services/analysis/app/         (all files)
  8. services/delivery/app/         (all files)
  9. frontend/src/pages/            (all files)
  10. .eva/veritas-plan.json + .eva/trust.json
  NOTE: docs/ spec files are MISSING from the repo. Where the review references
        spec docs, compare against .github/copilot-instructions.md PART 2 sections
        P2.1-P2.9 which contain the canonical specs inline.

AREA 1 -- SERVICE FLOW COMPLETENESS
  Walk the 8 steps above against the actual code.
  For each step: IMPLEMENTED / STUB / MISSING / BROKEN
  If stub or missing: is there a story in PLAN.md that covers it?
  If no story exists: propose one.

AREA 2 -- TENANT ISOLATION
  Every Cosmos call has partition_key=subscriptionId.
  No query_items() without partition_key anywhere.
  Collector writes with correct partition key.

AREA 3 -- TIER GATING AND ANALYSIS SAMPLING
  gate_findings() is called correctly on all findings endpoints.
  The 10% sample logic for Tier 1 is implemented (or note it as missing).
  "partial scan" metadata is returned for Tier 1 responses.
  Re-triggering analysis at upgraded tier after Stripe webhook is wired.

AREA 4 -- AUTH FLOW
  POST /connect: MSAL delegated, multi-tenant, authority=common.
  Refresh token stored in Key Vault, not Cosmos.
  Access token NOT stored anywhere.
  POST /preflight: all 4 RBAC roles checked; returns missing_roles list.
  POST /disconnect: refresh token deleted from KV.

AREA 5 -- STRIPE WEBHOOK SAFETY
  raw body read before JSON parse.
  Signature verified with STRIPE_WEBHOOK_SECRET.
  Entitlement upgrade is idempotent.
  Tier downgrade blocked.

AREA 6 -- COLLECTOR COMPLETENESS
  Resource Graph: pagination with $skipToken.
  Cost Management: 91-day daily granularity.
  Advisor: all 5 categories.
  Network topology: VNet + peering + public IPs.

AREA 7 -- ANALYSIS RULES
  12 rules in services/analysis/app/rules/ -- which are implemented vs stub?
  Sampling logic (10% for Tier 1) -- implemented?
  deliverable_template_id populated for Tier 3 findings?

AREA 8 -- DELIVERY SERVICE
  12 template folders exist?
  Jinja2 rendering covers all FINDING schema fields?
  ZIP contains SHA-256 manifest?
  SAS URL is 7-day expiry?

AREA 9 -- FRONTEND FLOW
  Does the frontend actually navigate the 8 steps?
  Login -> ConnectSubscription -> PreflightStatus -> ScanStatus ->
  FindingsReport -> CheckoutCTA -> DownloadPackage
  Are TierGate components in place?
  Is the "partial scan" banner rendered for Tier 1?

AREA 10 -- TEST COVERAGE
  Which services have zero test files?
  Which steps in the service flow have no test coverage?
  Minimum test set to reach ACCEPTANCE.md DoD.

AREA 11 -- SECURITY / ENCODING
  No hardcoded secrets.
  CORS: wildcard not in prod config.
  No non-ASCII characters in any file.

---

OUTPUT FORMAT
--------------

Post a single comment with this exact structure:

  ## OPUS REVIEW FINDINGS -- 2026-02-27

  ### SERVICE FLOW STATUS
  | Step | Status | Gap | PLAN.md coverage |
  |------|--------|-----|-----------------|
  | 1 AUTH        | IMPLEMENTED / STUB / MISSING | ... | ACA-XX-XXX or NONE |
  | 2 PREFLIGHT   | ...
  | 3 SCAN INIT   | ...
  | 4 COLLECTOR   | ...
  | 5 ANALYSIS    | ...
  | 6 REPORTING   | ...
  | 7 UPGRADE     | ...
  | 8 DELIVERY    | ...

  ### CRITICAL FINDINGS
  C-01: [file:line] Description. Impact on service flow: Step N.
        Fix: exact action.

  ### HIGH FINDINGS
  H-01: ...

  ### MEDIUM FINDINGS
  M-01: ...

  ### LOW FINDINGS
  L-01: ...

  ### PROPOSED SPRINT 2 STORY LIST
  Ordered by dependency. For each story:
    Story ID: ACA-NN-NNN   (next available from roster in PLAN.md)
    Title: one line
    Size: XS/S/M/L/XL
    Model: Sonnet / GPT-5 mini
    Fixes: C-XX or H-XX finding reference
    Depends on: story ID or NONE
    Acceptance: one testable condition

  ### SPRINT 2 VELOCITY ESTIMATE
  Total FP. Achievable in 80-100 FP sprint? Yes/No. If no, propose split.

  ### QUESTIONS FOR HUMAN
  [AGENT-ESCALATION] format per AGENTS.md. Genuine blockers only.

---

CONSTRAINTS
  - No code changes. No PRs. No commits.
  - ASCII only in your comment.
  - If a file is not in the read list above but needed, read it.
  - Do not summarise spec docs -- cite them (file:line) and compare to code.
  - If the code does not match the spec, say so explicitly with file + line.
