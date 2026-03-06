ACA -- Azure Cost Advisor -- ACCEPTANCE
=========================================

Version: 0.3.0
Updated: 2026-03-06T19:38:00-05:00 (2:38 PM ET - Sprint-003 Baseline Locked)
Method: Each gate is verified manually OR by an automated test/check.
        [PASS] = verified. [ ] = not yet tested. [FAIL] = known failure.

DATA MODEL STATE (as of 2:38 PM ET):
- Cloud model row_version: 2 (synced after DPDCA cycle)
- 281 stories planned across 15 epics
- Coverage: 95.7% (269/281 stories with artifacts)
- Evidence: 92.9% (261/281 stories with proof)
- Gaps: 23 (12 missing_impl ACA-15, 11 orphan_tags in docs)
- Status: SPRINT-003 ready for agent execution

=============================================================================
PHASE 1 ACCEPTANCE (marco* dev go-live)
=============================================================================

GATE P1-01 -- Infrastructure
  [ ] P1-01a: infra/phase1-marco/main.bicep deploys successfully to EsDAICoE-Sandbox
  [ ] P1-01b: All 7 Cosmos containers exist in marco-sandbox-cosmos database aca-db
  [ ] P1-01c: All secrets are in marcosandkv20260203 (COSMOS_KEY, STRIPE_SECRET_KEY, etc.)
  [ ] P1-01d: API Container App has managed identity with KV read permission
  [ ] P1-01e: GitHub Actions OIDC federated credential configured for EsDAICoE-Sandbox
  [ ] P1-01f: deploy-phase1.yml runs without error and deploys all 4 Container Apps

GATE P1-02 -- API Service Startup
  [ ] P1-02a: GET /health returns { status: "ok", version: "0.3.0" } with HTTP 200
  [ ] P1-02b: All 6 routers load without ImportError (check app startup logs)
  [ ] P1-02c: Cosmos connection validated on startup (health check includes cosmos status)
  [ ] P1-02d: Settings load from KV references without error (no missing env vars)

GATE P1-03 -- Data Collection
  [ ] P1-03a: Collector preflight against EsDAICoE-Sandbox returns verdict=PASS or PASS_WITH_WARNINGS
  [ ] P1-03b: Collector completes a full collection run in < 10 minutes
  [ ] P1-03c: inventories container has at least 1 document after collection
  [ ] P1-03d: cost-data container has at least 1 document (91 days of rows)
  [ ] P1-03e: advisor container has at least 1 document
  [ ] P1-03f: scan record status = "succeeded" after collector completes

GATE P1-04 -- Analysis Engine
  [ ] P1-04a: Analysis engine runs all 12 rules without unhandled exception
  [ ] P1-04b: At least 3 rules produce findings for the EsDAICoE-Sandbox subscription
  [ ] P1-04c: findings container has documents with correct partition_key=subscriptionId
  [ ] P1-04d: AnalysisRun status = "succeeded" after analysis completes
  [ ] P1-04e: findingsSummary.findingCount > 0 and totalSavingLow > 0

GATE P1-05 -- Tier Gating (CRITICAL -- security gate)
  [PASS] P1-05a: gate_findings() function exists in services/api/app/routers/findings.py
  [ ] P1-05b: Tier 1 GET /v1/findings/:scanId response does NOT contain "narrative" field
  [ ] P1-05c: Tier 1 GET /v1/findings/:scanId response does NOT contain "deliverable_template_id"
  [ ] P1-05d: Tier 2 GET /v1/findings/:scanId response DOES contain "narrative" field
  [ ] P1-05e: Tier 3 GET /v1/findings/:scanId response DOES contain "deliverable_template_id"
  [ ] P1-05f: redteam-agent.yaml assertion passes against a live Tier 1 token
  [ ] P1-05g: No Cosmos query returns documents from a different subscriptionId (cross-tenant test)

GATE P1-06 -- Stripe Integration
  [ ] P1-06a: POST /v1/checkout/tier2 returns a valid Stripe checkout session URL
  [ ] P1-06b: Completing Tier 2 checkout (test mode) fires webhook to POST /v1/webhooks/stripe
  [ ] P1-06c: After webhook, entitlements container has a document with tier=2 for that subscriptionId
  [ ] P1-06d: After Tier 2 entitlement, GET /v1/entitlements returns { tier: 2 }
  [ ] P1-06e: GET /v1/findings/:scanId with a Tier 2 token now returns narrative field
  [ ] P1-06f: customer.subscription.deleted webhook downgrades entitlement to tier=1
  [ ] P1-06g: Stripe webhook signature verification rejects requests without valid Stripe-Signature

GATE P1-07 -- Delivery (Tier 3)
  [ ] P1-07a: POST /v1/checkout/tier3 -> completed payment triggers delivery agent
  [ ] P1-07b: Delivery service generates at least 1 IaC artifact from findings
  [ ] P1-07c: ZIP is uploaded to Azure Blob Storage with correct container
  [ ] P1-07d: GET /v1/download/:deliverableId returns a working 24h SAS URL
  [ ] P1-07e: ZIP contains findings.json at root
  [ ] P1-07f: Deliverable record in Cosmos has sha256 field that matches downloaded ZIP

GATE P1-08 -- Frontend (Tier 1 flow)
  [ ] P1-08a: Landing page renders with tier cards and "Start Free Scan" CTA
  [ ] P1-08b: User can sign in via Entra ID and land on /connect
  [ ] P1-08c: User can connect subscription in Mode A (delegated)
  [ ] P1-08d: Pre-flight result page shows PASS/WARN/FAIL per probe with names
  [ ] P1-08e: Scan status page polls and shows "running" then "succeeded"
  [ ] P1-08f: Findings page shows Tier 1 view (titles + saving range, narrative blurred)
  [ ] P1-08g: "Unlock full report" CTA navigates to checkout
  [ ] P1-08h: Consent banner appears on first visit and can be accepted or rejected
  [ ] P1-08i: Accepting consent enables GA4 + Clarity tags (verified in GTM Preview)
  [ ] P1-08j: Rejecting consent suppresses all analytics tags

GATE P1-09 -- APIM
  [ ] P1-09a: All /v1/* routes return 401 without a valid JWT
  [ ] P1-09b: Tier enforcement: Tier 1 token + Tier 2 endpoint returns 403 TIER_REQUIRED
  [ ] P1-09c: Entitlements cache: two rapid calls to /v1/entitlements hit cache on second call
               (verify via APIM log: "Cache hit" in trace)
  [ ] P1-09d: Throttling: > 100 req/min from same subscription key returns 429

GATE P1-10 -- Accessibility (EN only for Phase 1)
  [ ] P1-10a: axe-core CI check passes with zero critical or serious violations on all 9 pages
  [ ] P1-10b: Full keyboard-only walkthrough of Tier 1 flow: Landing -> Connect -> Scan -> Findings
  [ ] P1-10c: Screen reader (NVDA or VoiceOver) can read findings table headers and values
  [ ] P1-10d: Consent banner is fully keyboard-accessible
  [ ] P1-10e: All icon-only buttons have visible aria-label

GATE P1-11 -- i18n (FR required for Phase 1)
  [ ] P1-11a: Language selector is visible and functional
  [ ] P1-11b: Switching to FR renders all user-visible strings in French (no EN fallback visible)
  [ ] P1-11c: FR translations are reviewed and do not contain placeholder text
  [ ] P1-11d: Date/number formats are locale-aware (en-CA vs fr-CA)
  [ ] P1-11e: Stripe checkout page renders in FR when FR locale is selected

GATE P1-12 -- CI
  [PASS] P1-12a: ci.yml exists and runs ruff + mypy + pytest on PR
  [PASS] P1-12b: All 12 rule files import without error (ALL_RULES count=12 verified)
  [ ] P1-12c: At least 12 unit tests pass (one per rule minimum)
  [ ] P1-12d: axe-core check added to ci.yml and gates merge on violations

=============================================================================
PHASE 2 ACCEPTANCE (commercial MVP go-live)
=============================================================================

GATE P2-01 -- Infrastructure
  [ ] P2-01a: terraform apply on infra/phase2-private completes with 0 errors
  [ ] P2-01b: All 4 Container Apps are deployed in the private subscription ACA environment
  [ ] P2-01c: Custom domain app.aca.example.com resolves to ACA frontend Container App
  [ ] P2-01d: Custom domain api.aca.example.com resolves to ACA API Container App via APIM
  [ ] P2-01e: Managed TLS certificate issued and valid for both domains
  [ ] P2-01f: Cosmos DB has 3 geo-replicas (HA requirement for commercial)

GATE P2-02 -- End-to-end smoke test (Phase 2 infra)
  [ ] P2-02a: Full Tier 1 flow (connect -> scan -> analyze -> findings) on Phase 2 infra
  [ ] P2-02b: Full Tier 2 flow (checkout -> entitlement -> full findings) on Phase 2 infra
  [ ] P2-02c: Full Tier 3 flow (checkout -> delivery -> download zip) on Phase 2 infra
  [ ] P2-02d: All 3 onboarding modes (A/B/C) tested on Phase 2 infra

GATE P2-03 -- i18n complete
  [ ] P2-03a: EN, FR, pt-BR, ES, DE all render without fallback text
  [ ] P2-03b: All 5 locales reviewed by a native or near-native speaker
  [ ] P2-03c: Currency display works for CAD, USD, BRL, EUR
  [ ] P2-03d: Stripe checkout locale set correctly for each of the 5 locales
  [ ] P2-03e: Error messages returned by API are localized (Accept-Language header)

GATE P2-04 -- Accessibility (all locales)
  [ ] P2-04a: axe-core CI passes zero critical/serious for all 9 pages in EN and FR
  [ ] P2-04b: RTL test: no layout breakage for future RTL locales (padding, flex-direction)
  [ ] P2-04c: PDF report (if generated) uses tagged PDF with language attribute set
  [ ] P2-04d: WCAG 2.1 AA manual audit completed by someone other than the developer

GATE P2-05 -- Security and privacy
  [ ] P2-05a: Penetration test (manual): no cross-tenant data leakage found
  [ ] P2-05b: Penetration test: Tier 1 token cannot access Tier 2 data via any API path
  [ ] P2-05c: Penetration test: webhook accepts ONLY Stripe-signed events (reject tampered)
  [ ] P2-05d: CSP header enforced: inline scripts blocked, only GTM/Stripe/Clarity allowed
  [ ] P2-05e: Privacy policy at /privacy published in all 5 locales
  [ ] P2-05f: Terms of service at /terms published in all 5 locales
  [ ] P2-05g: Data retention TTL verified: scans/inventories/cost-data purged after 90 days
  [ ] P2-05h: Client data deletion via POST /v1/auth/disconnect hard-deletes all Cosmos docs

GATE P2-06 -- Telemetry
  [ ] P2-06a: GA4 real-time dashboard shows events on Phase 2 production traffic
  [ ] P2-06b: Clarity session replay is active and capturing funnel drop-off events
  [ ] P2-06c: App Insights shows structured logs from all 4 services with no PII
  [ ] P2-06d: Alerts fire correctly (API 5xx > 5%, collector job failure)
  [ ] P2-06e: No Azure subscriptionId or resource name appears in any GA4 or Clarity event

GATE P2-07 -- Stripe production
  [ ] P2-07a: Stripe live mode keys configured (not test keys) in production KV
  [ ] P2-07b: Stripe webhook endpoint registered in Stripe dashboard for Phase 2 domain
  [ ] P2-07c: First live Tier 2 payment processed successfully
  [ ] P2-07d: Recurring subscription renewal fires invoice.paid and renews entitlement
  [ ] P2-07e: Stripe billing portal accessible from /billing page

GATE P2-08 -- Support and documentation
  [ ] P2-08a: docs/client-access-guide.md published at /docs/access-guide in all 5 locales
  [ ] P2-08b: FAQ page covers top 10 support questions
  [ ] P2-08c: Status page (uptime) linked from footer
  [ ] P2-08d: Support email or chat widget live (Intercom or equivalent)

GATE P2-09 -- Performance
  [ ] P2-09a: API response time p99 < 500ms for GET /v1/findings/:scanId on Phase 2 infra
  [ ] P2-09b: Frontend Lighthouse score > 90 (Performance) on /findings page
  [ ] P2-09c: Collector completes for a 1,000-resource subscription in < 15 minutes
  [ ] P2-09d: Analysis completes in < 5 minutes for a 91-day cost dataset of 50,000 rows

GATE P2-10 -- Go-live readiness
  [ ] P2-10a: Business registration for ACA SaaS product in place
  [ ] P2-10b: Stripe business account verified (not personal) for production payments
  [ ] P2-10c: DNS TTL lowered 48h before cutover
  [ ] P2-10d: Phase 1 marco* infra kept live for 30 days post-cutover as rollback
  [ ] P2-10e: First 10 external client accounts created and basic onboarding validated
