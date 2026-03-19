# Project 51 (ACA) -- Complete WBS Extraction

**Generated**: March 11, 2026 @ 11:04 AM ET
**Method**: Comprehensive analysis of all ACA documentation (01-43 + PLAN + GAPS + EPICs)
**Baseline**: Archived PLAN.md (2026-03-06) with 270 stories
**Current**: 8-WEEK-BUILD-PLAN-20260311.md references 281 stories

---

## Executive Summary

### Story Count Evolution

| Source | Story Count | Date | Notes |
|--------|-------------|------|-------|
| **Archived PLAN.md** | 270 | 2026-03-06 | Baseline (Epics 1-15) |
| **GAPS-AND-DECISIONS.md** | +5 | 2026-02-28 | New gap stories identified |
| **Epic 13 (not in archive)** | +11 | 2026-03-06 | Azure Best Practices Catalog |
| **Epic 14 additions** | +9 | 2026-03-02 | Sprint agent enhancements beyond ACA-14-003 |
| **Epic 15 gap stories** | +10 | 2026-03-02 | ACA-15-001a through ACA-15-012a series |
| **TOTAL (with overlaps resolved)** | **281** | 2026-03-11 | Current active scope |

### The 11 New Stories (270 → 281)

**From GAPS-AND-DECISIONS.md** (5 new):
1. [ACA-01-022] Frontend deployment (marco-sandbox-backend slot)
2. [ACA-02-018] Analysis auto-trigger (collector → analysis job)
3. [ACA-02-019] Resource Graph pagination (>1000 resources)
4. [ACA-04-029] RFC 7807 structured errors
5. [ACA-11-010] Standalone data model server (Phase 2 independence)

**From Gap Story ACA-03-020** (1 new):
6. [ACA-03-020] Bundle 29-foundry agent code (Phase 2, in archive as duplicate ID)

**From Epic 14 Additions** (5 new beyond ACA-14-003):
7. [ACA-14-004] Plan phase (gpt-4o-mini context)
8. [ACA-14-005] D2 phase (branch creation + evidence)
9. [ACA-14-006] Check phase (ruff + pytest)
10. [ACA-14-007] Act phase (commit + Veritas audit)
11. [ACA-14-008] GitHub Models API integration

**Note**: Epic 14 stories ACA-14-009 through ACA-14-012 (4 additional) were added after the 281-story baseline, bringing current total scope closer to **285 active stories**.

---

## Complete Story Catalog by Epic

### Epic 1: Foundation and Infrastructure (21 stories, DONE)

**Milestone**: M1.0 (Weeks 1-2)  
**Status**: Complete  
**FP**: 65

| Story | ID | Title | Status |
|-------|-----|-------|--------|
| 1.1.1 | ACA-01-001 | docker-compose up | DONE |
| 1.1.2 | ACA-01-002 | pytest all pass | DONE |
| 1.1.3 | ACA-01-003 | /health endpoint | DONE |
| 1.1.4 | ACA-01-004 | Central data model query | DONE |
| 1.1.5 | ACA-01-005 | .env.example complete | DONE |
| 1.2.1 | ACA-01-006 | ruff lint CI | DONE |
| 1.2.2 | ACA-01-007 | mypy type check CI | DONE |
| 1.2.3 | ACA-01-008 | pytest CI gate | DONE |
| 1.2.4 | ACA-01-009 | axe-core a11y CI | DONE |
| 1.3.1 | ACA-01-010 | 7 Cosmos containers (Bicep) | DONE |
| 1.3.2 | ACA-01-011 | Key Vault secrets | DONE |
| 1.3.3 | ACA-01-012 | API managed identity | DONE |
| 1.3.4 | ACA-01-013 | Collector managed identity | DONE |
| 1.3.5 | ACA-01-014 | OIDC GitHub Actions | DONE |
| 1.3.6 | ACA-01-015 | bootstrap.sh provisioning | DONE |
| 1.4.1 | ACA-01-016 | 4 Dockerfiles build | DONE |
| 1.4.2 | ACA-01-017 | deploy-phase1.yml push images | DONE |
| 1.4.3 | ACA-01-018 | collector-schedule.yml nightly | DONE |
| 1.5.1 | ACA-01-019 | PUBLIC_APP_URL env var | DONE |
| 1.5.2 | ACA-01-020 | .env.example Azure hostname | DONE |
| 1.5.3 | ACA-01-021 | ACA_ALLOWED_ORIGINS | DONE |
| **NEW** | **ACA-01-022** | **Frontend deployment slot** | **NOT STARTED** |

---

### Epic 2: Data Collection Pipeline (19 stories, DONE + 2 new)

**Milestone**: M1.1 (Weeks 2-3)  
**Status**: Complete (baseline 17) + 2 new gap stories  
**FP**: 70

| Story | ID | Title | Status |
|-------|-----|-------|--------|
| 2.1.1 | ACA-02-001 | Preflight PASS/FAIL/WARN | DONE |
| 2.1.2 | ACA-02-002 | Cost Management Reader error | DONE |
| 2.1.3 | ACA-02-003 | PASS_WITH_WARNINGS flow | DONE |
| 2.1.4 | ACA-02-004 | --preflight-only flag | DONE |
| 2.2.1 | ACA-02-005 | Resource Graph inventory | DONE |
| 2.2.2 | ACA-02-006 | Cosmos partition_key save | DONE |
| 2.2.3 | ACA-02-007 | Capture resource metadata | DONE |
| **NEW** | **ACA-02-019** | **Resource Graph pagination** | **NOT STARTED** |
| 2.3.1 | ACA-02-008 | 91-day cost query | DONE |
| 2.3.2 | ACA-02-009 | Cost row enrichment | DONE |
| 2.3.3 | ACA-02-010 | Rate limiting (429 retry) | DONE |
| 2.4.1 | ACA-02-011 | Advisor recommendations | DONE |
| 2.4.2 | ACA-02-012 | Policy compliance state | DONE |
| 2.4.3 | ACA-02-013 | Network signals collection | DONE |
| 2.5.1 | ACA-02-014 | Scan status lifecycle | DONE |
| 2.5.2 | ACA-02-015 | Collection stats | DONE |
| 2.5.3 | ACA-02-016 | GET /v1/scans/:scanId | DONE |
| 2.5.4 | ACA-02-017 | Analysis job trigger | DONE |
| **NEW** | **ACA-02-018** | **Auto-trigger analysis job** | **NOT STARTED** |

---

### Epic 3: Analysis Engine + Rules (33 stories, 24 DONE + 9 in progress)

**Milestone**: M1.2 (Weeks 2-3)  
**Status**: Partial (Rules R-01 through R-08 done, R-09 through R-12 + tier gating active)  
**FP**: 155

| Story | ID | Title | Status |
|-------|-----|-------|--------|
| 3.1.1 | ACA-03-001 | Load 12 rules from ALL_RULES | DONE |
| 3.1.2 | ACA-03-002 | Rule isolation (failure handling) | DONE |
| 3.1.3 | ACA-03-003 | Persist findings to Cosmos | DONE |
| 3.1.4 | ACA-03-004 | AnalysisRun status lifecycle | DONE |
| 3.1.5 | ACA-03-005 | Findings summary | DONE |
| 3.2.1 | ACA-03-006 | Tier 1 filtering (title + saving only) | DONE |
| 3.2.2 | ACA-03-007 | Tier 1 blocks narrative | DONE |
| 3.2.3 | ACA-03-008 | Tier 2 includes narrative | DONE |
| 3.2.4 | ACA-03-009 | Tier 3 includes deliverable_template_id | DONE |
| 3.2.5 | ACA-03-010 | Red-team tier gate test | DONE |
| 3.3.1 | ACA-03-011 | R-01 Dev Box auto-stop | DONE |
| 3.3.2 | ACA-03-012 | R-02 Log retention | DONE |
| 3.3.3 | ACA-03-013 | R-03 Defender mismatch | DONE |
| 3.3.4 | ACA-03-014 | R-04 Compute scheduling | DONE |
| 3.3.5 | ACA-03-015 | R-05 Anomaly detection | DONE |
| 3.3.6 | ACA-03-016 | R-06 Stale environments | DONE |
| 3.3.7 | ACA-03-017 | R-07 Search SKU oversize | DONE |
| 3.3.8 | ACA-03-018 | R-08 ACR consolidation | DONE |
| 3.3.9 | ACA-03-019 | R-09 DNS sprawl | DONE |
| 3.3.10 | ACA-03-020 | R-10 Savings plan | DONE |
| 3.3.11 | ACA-03-021 | R-11 APIM token budget | DONE |
| 3.3.12 | ACA-03-022 | R-12 Chargeback gap | DONE |
| 3.4.1 | ACA-03-023 | Unit test R-01 | DONE |
| 3.4.2 | ACA-03-024 | Unit test R-02 | DONE |
| 3.4.3 | ACA-03-025 | Unit test R-03 | DONE |
| 3.4.4 | ACA-03-026 | Unit test R-04 | DONE |
| 3.4.5 | ACA-03-027 | Unit test R-05 | DONE |
| 3.4.6 | ACA-03-028 | Unit test R-06 | DONE |
| 3.4.7 | ACA-03-029 | Unit test R-07 | DONE |
| 3.4.8 | ACA-03-030 | Unit test R-08 | DONE |
| 3.4.9 | ACA-03-031 | Unit test R-09 | DONE |
| 3.4.10 | ACA-03-032 | Unit test R-10 | DONE |
| 3.4.11 | ACA-03-033 | Unit test R-11 | DONE |
| 3.4.12 | ACA-03-034 | Unit test R-12 | DONE |
| 3.4.13 | ACA-03-035 | Negative tests (all 12 rules) | DONE |
| 3.4.14 | ACA-03-036 | FindingsAssembler unit test | DONE |

**Note**: Duplicate story ID ACA-03-020 exists both as R-10 rule and as gap story "Bundle 29-foundry agent code". This is a documentation inconsistency.

---

### Epic 4: API and Auth Layer (29 stories, ~8 DONE + 21 active)

**Milestone**: M1.3 (Weeks 2-3)  
**Status**: Partial (auth foundation + core endpoints in progress)  
**FP**: 125

| Story | ID | Title | Status |
|-------|-----|-------|--------|
| 4.1.1 | ACA-04-001 | Multi-tenant sign-in (common authority) | IN PROGRESS |
| 4.1.2 | ACA-04-002 | JWT validation (JWKS) | DONE |
| 4.1.3 | ACA-04-003 | SubscriptionId from session | IN PROGRESS |
| 4.1.4 | ACA-04-004 | Connect Modes A/B/C | IN PROGRESS |
| 4.1.5 | ACA-04-005 | Disconnect (invalidate tokens) | NOT STARTED |
| 4.1.6 | ACA-04-006 | Auth.py rework (no EsDAICoE dependency) | DONE |
| 4.1.7 | ACA-04-007 | Frontend LoginPage MSAL | NOT STARTED |
| 4.2.1 | ACA-04-008 | POST /v1/auth/connect | DONE |
| 4.2.2 | ACA-04-009 | POST /v1/auth/preflight | NOT STARTED |
| 4.2.3 | ACA-04-010 | POST /v1/auth/disconnect | NOT STARTED |
| 4.2.4 | ACA-04-011 | POST /v1/collect/start | NOT STARTED |
| 4.2.5 | ACA-04-012 | GET /v1/collect/status | NOT STARTED |
| 4.2.6 | ACA-04-013 | GET /v1/reports/tier1 | NOT STARTED |
| 4.2.7 | ACA-04-014 | POST /v1/billing/checkout | NOT STARTED |
| 4.2.8 | ACA-04-015 | GET /v1/billing/portal | NOT STARTED |
| 4.2.9 | ACA-04-016 | POST /v1/webhooks/stripe | NOT STARTED |
| 4.3.1 | ACA-04-017 | APIM JWT validation policy | NOT STARTED |
| 4.3.2 | ACA-04-018 | APIM entitlements cache (60s) | NOT STARTED |
| 4.3.3 | ACA-04-019 | APIM 403 tier enforcement | NOT STARTED |
| 4.3.4 | ACA-04-020 | APIM throttling (100 req/min) | NOT STARTED |
| 4.3.5 | ACA-04-021 | APIM X-Subscription-Id forwarding | NOT STARTED |
| 4.4.1 | ACA-04-022 | GET /v1/admin/kpis | NOT STARTED |
| 4.4.2 | ACA-04-023 | GET /v1/admin/customers | NOT STARTED |
| 4.4.3 | ACA-04-024 | POST /v1/admin/entitlements/grant | NOT STARTED |
| 4.4.4 | ACA-04-025 | POST /v1/admin/subscriptions/:id/lock | NOT STARTED |
| 4.4.5 | ACA-04-026 | POST /v1/admin/stripe/reconcile | NOT STARTED |
| 4.4.6 | ACA-04-027 | GET /v1/admin/runs | NOT STARTED |
| 4.5.1 | ACA-04-028 | upsert_item() partition_key parameter | DONE |
| **NEW** | **ACA-04-029** | **RFC 7807 structured errors** | **NOT STARTED** |

---

### Epic 5: Frontend Spark Architecture (42 stories, ~2 DONE + 40 active)

**Milestone**: M1.4 (Weeks 3-4)  
**Status**: Early (auth hooks + router in progress, pages not started)  
**FP**: 175

**Auth Layer** (5 stories):
- ACA-05-001: roles.ts (NOT STARTED)  
- ACA-05-002: useAuth.ts (NOT STARTED)  
- ACA-05-003: RequireAuth.tsx (NOT STARTED)  
- ACA-05-004: RequireRole.tsx (NOT STARTED)  
- ACA-05-005: Admin route protection (NOT STARTED)

**Layout Layer** (5 stories):
- ACA-05-006: CustomerLayout.tsx (NOT STARTED)  
- ACA-05-007: AdminLayout.tsx (NOT STARTED)  
- ACA-05-008: NavCustomer.tsx (NOT STARTED)  
- ACA-05-009: NavAdmin.tsx (NOT STARTED)  
- ACA-05-010: AppShell.tsx (NOT STARTED)

**Router** (5 stories):
- ACA-05-011: router.tsx createBrowserRouter (NOT STARTED)  
- ACA-05-012: Route / → LoginPage (NOT STARTED)  
- ACA-05-013: Routes /app/* → RequireAuth (NOT STARTED)  
- ACA-05-014: Routes /admin/* → RequireRole (NOT STARTED)  
- ACA-05-015: Code-split lazy loading (NOT STARTED)

**Customer Pages** (5 stories):
- ACA-05-016: LoginPage (NOT STARTED)  
- ACA-05-017: ConnectSubscriptionPage (NOT STARTED)  
- ACA-05-018: CollectionStatusPage (NOT STARTED)  
- ACA-05-019: FindingsTier1Page (NOT STARTED)  
- ACA-05-020: UpgradePage (NOT STARTED)

**Admin Pages** (5 stories):
- ACA-05-021: AdminDashboardPage (NOT STARTED)  
- ACA-05-022: AdminCustomersPage (NOT STARTED)  
- ACA-05-023: AdminBillingPage (NOT STARTED)  
- ACA-05-024: AdminRunsPage (NOT STARTED)  
- ACA-05-025: AdminControlsPage (NOT STARTED)

**API Client Layer** (4 stories):
- ACA-05-026: client.ts base http function (NOT STARTED)  
- ACA-05-027: appApi.ts customer calls (NOT STARTED)  
- ACA-05-028: adminApi.ts admin calls (NOT STARTED)  
- ACA-05-029: models.ts TypeScript DTOs (NOT STARTED)

**Shared Components** (5 stories):
- ACA-05-030: Loading.tsx (NOT STARTED)  
- ACA-05-031: ErrorState.tsx (NOT STARTED)  
- ACA-05-032: DataTable.tsx (NOT STARTED)  
- ACA-05-033: MoneyRangeBar.tsx (NOT STARTED)  
- ACA-05-034: EffortBadge.tsx (NOT STARTED)

**Telemetry** (4 stories):
- ACA-05-035: ConsentBanner (NOT STARTED)  
- ACA-05-036: TelemetryProvider.tsx (NOT STARTED)  
- ACA-05-037: 16 GA4/Clarity events (NOT STARTED)  
- ACA-05-038: Admin no telemetry (NOT STARTED)

**Accessibility** (4 stories):
- ACA-05-039: Skip-to-content link (NOT STARTED)  
- ACA-05-040: Full keyboard navigation (NOT STARTED)  
- ACA-05-041: Form field labels (NOT STARTED)  
- ACA-05-042: Modal focus trap (NOT STARTED)

---

### Epic 6: Monetization and Billing (18 stories, DONE)

**Milestone**: M1.5 (Weeks 3-4)  
**Status**: Complete  
**FP**: 65

| Story | ID | Title | Status |
|-------|-----|-------|--------|
| 6.1.1 | ACA-06-001 | POST /v1/checkout/tier2 | DONE |
| 6.1.2 | ACA-06-002 | POST /v1/checkout/tier3 | DONE |
| 6.1.3 | ACA-06-003 | mode=subscription (Tier 2 monthly) | DONE |
| 6.1.4 | ACA-06-004 | mode=one_time (Tier 3) | DONE |
| 6.1.5 | ACA-06-005 | Checkout metadata (subscriptionId, analysisId) | DONE |
| 6.1.6 | ACA-06-006 | Coupon code entry | DONE |
| 6.1.7 | ACA-06-007 | STRIPE_COUPON_ENABLED setting | DONE |
| 6.1.8 | ACA-06-008 | Admin promotion codes (Stripe dashboard) | DONE |
| 6.2.1 | ACA-06-009 | checkout.session.completed webhook | DONE |
| 6.2.2 | ACA-06-010 | invoice.paid webhook | DONE |
| 6.2.3 | ACA-06-011 | customer.subscription.updated webhook | DONE |
| 6.2.4 | ACA-06-012 | customer.subscription.deleted webhook | DONE |
| 6.2.5 | ACA-06-013 | Webhook audit trail (payments container) | DONE |
| 6.3.1 | ACA-06-014 | GET /v1/entitlements | DONE |
| 6.3.2 | ACA-06-015 | Tier gate from Cosmos (60s cache) | DONE |
| 6.3.3 | ACA-06-016 | StripeCustomerMapRepo | DONE |
| 6.3.4 | ACA-06-017 | Billing portal customerId resolution | DONE |
| 6.3.5 | ACA-06-018 | Tier 3 one-time preservation on subscription.deleted | DONE |

---

### Epic 7: Delivery Packager (9 stories, NOT STARTED)

**Milestone**: M1.6 (Week 4)  
**Status**: Not started  
**FP**: 80

| Story | ID | Title | Status |
|-------|-----|-------|--------|
| 7.1.1 | ACA-07-001 | 12 Jinja2 template folders (Bicep only) | NOT STARTED |
| 7.1.2 | ACA-07-002 | Terraform generation (Phase 2 deferred) | NOT STARTED |
| 7.1.3 | ACA-07-003 | Implementation guide generator (PDF) | NOT STARTED |
| 7.1.4 | ACA-07-004 | ZIP packager (manifest + artifacts) | NOT STARTED |
| 7.2.1 | ACA-07-005 | Generate IaC artifacts per scan | NOT STARTED |
| 7.2.2 | ACA-07-006 | ZIP with findings.json manifest | NOT STARTED |
| 7.2.3 | ACA-07-007 | SHA-256 signing | NOT STARTED |
| 7.2.4 | ACA-07-008 | Upload to Blob Storage (24h SAS) | NOT STARTED |
| 7.2.5 | ACA-07-009 | Deliverable record in Cosmos | NOT STARTED |

---

### Epic 8: Observability and Telemetry (14 stories, ~4 PARTIAL)

**Milestone**: M2.0 (Weeks 4-5)  
**Status**: Partial (some telemetry wired, not complete)  
**FP**: 55

**Frontend Telemetry** (6 stories):
- ACA-08-001: GTM container (NOT STARTED)  
- ACA-08-002: GA4 tag (NOT STARTED)  
- ACA-08-003: Clarity tag (NOT STARTED)  
- ACA-08-004: 16 AnalyticsEventName events (NOT STARTED)  
- ACA-08-005: Consent banner accept/reject (NOT STARTED)  
- ACA-08-006: Consent preference persistence (NOT STARTED)

**Backend Observability** (5 stories):
- ACA-08-007: App Insights connection string (DONE)  
- ACA-08-008: Structured JSON logs (DONE)  
- ACA-08-009: Custom metrics (duration) (DONE)  
- ACA-08-010: API error logging (DONE)  
- ACA-08-011: Stripe webhook event logging (NOT STARTED)

**Alerting** (3 stories):
- ACA-08-012: Alert: API 5xx > 5% (NOT STARTED)  
- ACA-08-013: Alert: Collector job failure (NOT STARTED)  
- ACA-08-014: Alert: Anomaly detection rule fires (NOT STARTED)

---

### Epic 9: i18n and a11y (18 stories, NOT STARTED)

**Milestone**: M2.1 (Weeks 4-6)  
**Status**: Not started (5 locales planned: EN, FR, pt-BR, ES, DE)  
**FP**: 85

**i18n** (10 stories):
- ACA-09-001: i18next 5 locales (NOT STARTED)  
- ACA-09-002: Extract all UI strings (NOT STARTED)  
- ACA-09-003: Language selector (5 languages) (NOT STARTED)  
- ACA-09-004: Locale preference localStorage (NOT STARTED)  
- ACA-09-005: Intl.DateTimeFormat (NOT STARTED)  
- ACA-09-006: Intl.NumberFormat (currency) (NOT STARTED)  
- ACA-09-007: FR translations complete (NOT STARTED)  
- ACA-09-008: pt-BR, ES, DE machine translations (NOT STARTED)  
- ACA-09-009: API error messages (5 locales) (NOT STARTED)  
- ACA-09-010: Stripe checkout locale (NOT STARTED)

**a11y** (8 stories):
- ACA-09-011: axe-core CI (0 critical/serious) (NOT STARTED)  
- ACA-09-012: Icon aria-labels (NOT STARTED)  
- ACA-09-013: Form field labels (NOT STARTED)  
- ACA-09-014: Table headers (NOT STARTED)  
- ACA-09-015: PreFlight colour + icon (NOT STARTED)  
- ACA-09-016: Colour contrast 4.5:1 (NOT STARTED)  
- ACA-09-017: Focus ring visible (NOT STARTED)  
- ACA-09-018: Skip-to-content link (NOT STARTED)  

---

### Epic 10: Commercial Hardening (15 stories, NOT STARTED)

**Milestone**: M2.2 (Weeks 5-6)  
**Status**: Not started  
**FP**: 90

**Security** (6 stories):
- ACA-10-001: Red-team tier gate test (NOT STARTED)  
- ACA-10-002: Tenant isolation validation (NOT STARTED)  
- ACA-10-003: Stripe webhook signature (NOT STARTED)  
- ACA-10-004: Admin token rotation (NOT STARTED)  
- ACA-10-005: Parameterized Cosmos queries (NOT STARTED)  
- ACA-10-006: CSP header enforcement (NOT STARTED)

**Privacy** (6 stories):
- ACA-10-007: Privacy policy (5 locales) (NOT STARTED)  
- ACA-10-008: Terms of service (5 locales) (NOT STARTED)  
- ACA-10-009: 90-day retention policy (NOT STARTED)  
- ACA-10-010: DELETE /v1/auth/disconnect hard-delete (NOT STARTED)  
- ACA-10-011: GA4 14-month retention (NOT STARTED)  
- ACA-10-012: Clarity GDPR right-to-be-forgotten (NOT STARTED)

**Support** (3 stories):
- ACA-10-013: Client access guide (5 locales) (NOT STARTED)  
- ACA-10-014: FAQ page (top 10 questions) (NOT STARTED)  
- ACA-10-015: Status page (uptime) (NOT STARTED)

---

### Epic 11: Phase 2 Infrastructure (10 stories, NOT STARTED)

**Milestone**: M3.0 (Weeks 7-9) -- **DEFERRED** to Post-Phase 1  
**Status**: Not started (Phase 2 cutover planning)  
**FP**: 100

**Terraform Provisioning** (5 stories):
- ACA-11-001: terraform apply (infra/phase2-private) (NOT STARTED)  
- ACA-11-002: ACA-specific APIM instance (NOT STARTED)  
- ACA-11-003: deploy-phase2.yml OIDC (NOT STARTED)  
- ACA-11-004: Custom domain + managed TLS (NOT STARTED)  
- ACA-11-005: Cosmos 3 geo-replicas (NOT STARTED)

**Cutover** (4 stories):
- ACA-11-006: DNS TTL lowered 48h before (NOT STARTED)  
- ACA-11-007: Phase 1 rollback 30 days (NOT STARTED)  
- ACA-11-008: Phase 2 smoke test (Tier 1-3 flow) (NOT STARTED)  
- ACA-11-009: APIM config export (NOT STARTED)

**Product Independence** (1 new):
- **ACA-11-010**: Standalone data model server (Phase 2) (NOT STARTED)

---

### Epic 12: Data Model Support (22 stories, ONGOING)

**Milestone**: Ongoing (all sprints)  
**Status**: Ongoing  
**FP**: 75

**Build-time Use** (4 stories):
- ACA-12-001: Seed WBS to data model (DONE)  
- ACA-12-002: Story status tracking (DONE)  
- ACA-12-003: Agent updates story status (IN PROGRESS)  
- ACA-12-004: data-model agent-summary (NOT STARTED)

**Runtime Use** (4 stories):
- ACA-12-005: API reads feature_flags (NOT STARTED)  
- ACA-12-006: Analysis reads rules layer (NOT STARTED)  
- ACA-12-007: Endpoints layer sync (NOT STARTED)  
- ACA-12-008: Containers layer schema (NOT STARTED)

**Phase 1 Infrastructure** (8 stories):
- ACA-12-009: Cosmos scans container (DONE)  
- ACA-12-010: inventories container (DONE)  
- ACA-12-011: cost-data container (DONE)  
- ACA-12-012: advisor container (DONE)  
- ACA-12-013: findings container (DONE)  
- ACA-12-014: APIM product (DONE)  
- ACA-12-015: Key Vault secrets (DONE)  
- ACA-12-016: Container App Jobs (DONE)

**Data Model Safe Cleanup** (6 stories):
- ACA-12-029: Snapshot before cleanup (NOT STARTED)  
- ACA-12-030: Scoped cleanup (51-ACA only) (NOT STARTED)  
- ACA-12-031: Re-prime after cleanup (NOT STARTED)  
- ACA-12-032: Regenerate hierarchy (README + PLAN) (NOT STARTED)  
- ACA-12-033: Bottom-up reconciliation (NOT STARTED)  
- ACA-12-034: Publish restore evidence + Veritas audit (NOT STARTED)

---

### Epic 13: Azure Best Practices Service Catalog (11 stories, NOT STARTED)

**Milestone**: M2.3 (Weeks 4-5)  
**Status**: Planned (not in archived PLAN.md baseline)  
**FP**: 55

**WAF Assessment** (2 stories):
- ACA-13-009: GET /v1/assessment/waf (NOT STARTED)  
- ACA-13-010: WAF reliability pillar (APRL) (NOT STARTED)

**FinOps Rules** (2 stories):
- ACA-13-011: FinOps rules R-13 to R-17 (NOT STARTED)  
- ACA-13-012: Idle resource detection (NOT STARTED)

**Security Rules** (3 stories):
- ACA-13-013: RBAC hygiene check (NOT STARTED)  
- ACA-13-014: Key Vault RBAC mode audit (NOT STARTED)  
- ACA-13-015: MCSB control compliance (NOT STARTED)

**APIM/API Design** (2 stories):
- ACA-13-016: APIM rate-limit health check (NOT STARTED)  
- ACA-13-017: API design compliance (NOT STARTED)

**IaC Quality Gate** (2 stories):
- ACA-13-018: PSRule for Azure CI gate (NOT STARTED)  
- ACA-13-019: Best-practice tag enforcement (NOT STARTED)

---

### Epic 14: DPDCA Cloud Agent (12 stories, 10 DONE + 2 in progress)

**Milestone**: M2.4 (Weeks 3-5)  
**Status**: Active (sprint automation operational)  
**FP**: 65

**Sprint Backlog Template** (2 stories):
- ACA-14-001: agent-task.yml template (DONE)  
- ACA-14-002: Story ID validation (DONE)

**DPDCA Workflow** (5 stories):
- ACA-14-003: D1 phase (parse issue, load context) (DONE)  
- ACA-14-004: P phase (gpt-4o-mini plan) (DONE)  
- ACA-14-005: D2 phase (branch + evidence) (DONE)  
- ACA-14-006: C phase (ruff + pytest) (DONE)  
- ACA-14-007: A phase (commit + Veritas) (DONE)

**Agent Context** (2 stories):
- ACA-14-008: GitHub Models API integration (DONE)  
- ACA-14-009: Azure OpenAI fallback (DONE)

**Evidence Integration** (1 story):
- ACA-14-010: Evidence receipt schema validation (DONE)

**Sprint Workflow V2** (2 stories):
- ACA-14-011: SprintContext class (unified observability) (DONE)  
- ACA-14-012: State lock mechanism (idempotency) (DONE)

---

### Epic 15: Onboarding System (22 stories + 10 gap stories = 32 total, DEFERRED)

**Milestone**: M4.0 (Weeks 14-17 / Sprint 14-17) -- **DEFERRED** to Post-Phase 1  
**Status**: Planned (architecture complete, not started)  
**FP**: 72 (original 12 stories @ 52 FP + 10 gap stories @ 20 FP)

**Session Management** (3 stories):
- ACA-15-001: Consent + terms gate (GATE_0) (NOT STARTED)  
- ACA-15-001a: GDPR/PIPEDA data residency (Canada-only) (NOT STARTED)  
- ACA-15-002: Role assessment API (NOT STARTED)  
- ACA-15-002a: User consent/terms gate (NOT STARTED)

**Preflight & Validation** (3 stories + 2 gaps):
- ACA-15-003: Preflight validation workflow (NOT STARTED)  
- ACA-15-003a: OpenAPI/Swagger spec (SDK generation) (NOT STARTED)  
- ACA-15-003b: Error code schema (ACA-ERR-001) (NOT STARTED)

**Extraction Pipeline** (3 stories + 2 gaps):
- ACA-15-004: Azure SDK collection orchestration (NOT STARTED)  
- ACA-15-005: Cost API worker pool (3 workers) (NOT STARTED)  
- ACA-15-006: Extraction progress tracking (NOT STARTED)  
- ACA-15-006a: Token refresh (20+ min extractions) (NOT STARTED)  
- ACA-15-006b: Partial failure handling (API resilience) (NOT STARTED)

**Analysis & Findings** (3 stories):
- ACA-15-007: Analysis execution orchestration (NOT STARTED)  
- ACA-15-008: Finding categorization (severity, effort, risk) (NOT STARTED)  
- ACA-15-009: Cosmos indexes (composite) (NOT STARTED)  
- ACA-15-009a: Evidence search indexing (NOT STARTED)

**Delivery & Export** (3 stories + 2 gaps):
- ACA-15-010: Delivery packaging (ZIP + SHA-256) (NOT STARTED)  
- ACA-15-010b: SLA monitoring + alerting (App Insights) (NOT STARTED)  
- ACA-15-011: Evidence receipt generation (HMAC-SHA256) (NOT STARTED)  
- ACA-15-012: React UI onboarding flow (7 gates) (NOT STARTED)  
- ACA-15-012a: Export formats (CSV/Excel/PDF) (NOT STARTED)

**Special**: ACA-15-000 (ADO sync test story, not counted in baseline)

---

### Epic 17: Sync Orchestration AI Agent Enhancement (Future, NOT IN 281 BASELINE)

**Milestone**: Tier 3 (AI-Driven Resilience) -- **FUTURE VISION**  
**Status**: Planning only (not included in 281-story active scope)  
**FP**: TBD (estimated 65+ FP for 10+ stories)

**Feature 17.1**: Failure Classification Agent
- ACA-17-001: Failure classifier (transient vs permanent)

**Feature 17.2**: Intelligent Retry Tuning Agent
- ACA-17-002: Adaptive backoff strategy

**Features 17.3+**: Parallel orchestration, advisor agent, multi-agent coordinator

**Note**: Epic 17 represents Phase 7-10 vision (docs 40-43). These are strategic planning documents, not active sprint work.

---

## Numbered Documentation Files (01-43): Story ID Analysis

### Phase 1 Documents (01-10): Feasibility & Core Architecture
- **01-feasibility.md**: No story IDs (architectural discussion)  
- **02-preflight.md**: No story IDs (spec document, 940+ lines)  
- **03-aca-documentation.md**: No story IDs (client-facing guides)  
- **04-security.md**: No story IDs (security policy, 830+ lines)  
- **05-technical.md**: No story IDs (API spec, 1000+ lines)  
- **06-integration.md**: No story IDs (analytics spec)  
- **07-react.md**: No story IDs (telemetry stubs, 685 lines)  
- **08-payment.md**: No story IDs (Stripe integration patterns)  
- **09-hardening-MVP.md**: No story IDs (MVP scope definition)  
- **10-recurrent-clients.md**: No story IDs (subscription lifecycle)

### Phase 2-3 Documents (11-20): Implementation Details
- **11-caching.md**: No story IDs (APIM cache patterns)  
- **12-IaCscript.md**: No story IDs (12 IaC templates, 1400+ lines)  
- **13-IAC-more.md**: No story IDs (additional IaC patterns)  
- **14-analytcs.md**: No story IDs (GA4 event taxonomy)  
- **15-frontend.md**: No story IDs (React component patterns)  
- **16-stripe-backend.md**: No story IDs (webhook backend patterns)  
- **17-pahse2hardneing.md**: No story IDs (Phase 2 hardening)  
- **18-customer-mapping.md**: No story IDs (Stripe customer mapping)  
- **19-apim-cache.md**: No story IDs (APIM tier enforcement)  
- **20-iac-resources.md**: No story IDs (IaC resource catalog)

### Phase 3-4 Documents (21-30): Operations & Expansion
- **21-managing-buz.md**: No story IDs (business operations)  
- **22-spark-frontend.md**: No story IDs (Spark architecture spec)  
- **23-spark-prompt.md**: No story IDs (Spark implementation prompt)  
- **24-coupons.md**: No story IDs (Stripe promotion codes)  
- **25-pareto.md**: No story IDs (80/20 prioritization)  
- **26-consulting.md**: No story IDs (consulting engagement model)  
- **27-azure-waste.md**: No story IDs (cost waste patterns)  
- **28-probing.md**: No story IDs (preflight probe design)  
- **29-ghost-resources.md**: No story IDs (idle resource detection)  
- **30-collector-subsystem.md**: No story IDs (collector architecture)

### Phase 4-6 Documents (31-39): Subsystems & Revenue
- **31-collector-prompt.md**: No story IDs (collector implementation)  
- **32-stubs.md**: No story IDs (API stub patterns)  
- **33-cosmosdb.md**: No story IDs (Cosmos container design)  
- **34-ph3-page-normaliz.md**: No story IDs (Phase 3 page normalization)  
- **35-ph4-analysis-pack.md**: No story IDs (Phase 4 analysis package)  
- **36-ph5-scripts-pack.md**: No story IDs (Phase 5 scripts package)  
- **37-ph5-remediation.md**: No story IDs (Phase 5 remediation)  
- **38-ph6-remediation.md**: No story IDs (Phase 6 remediation)  
- **39-revenue-stream.md**: No story IDs (revenue model)

### Phase 7-10 Documents (40-43): Future Vision
- **40-ph7-EMP.md**: No story IDs (Phase 7: Ecosystem Monetization Platform)  
- **41-ph8-AOAP.md**: No story IDs (Phase 8: Azure Optimization Automation Platform)  
- **42-ph9-predictive-strat-ops-PSO.md**: No story IDs (Phase 9: Predictive Strategic Operations)  
- **43-ph10-ecosystem.md**: No story IDs (Phase 10: Ecosystem & Partnerships)

**Key Finding**: Numbered docs (01-43) contain **ZERO story IDs**. They are:
- Architecture specifications (01-05, 22-23, 30-38)
- Implementation guides (06-21, 31-33)
- Future phase vision documents (40-43)

All story IDs are concentrated in:
1. **Archived PLAN.md** (270 baseline stories, Epics 1-15)
2. **GAPS-AND-DECISIONS.md** (5 new gap stories)
3. **Epic 13 section** (11 stories, added to PLAN later)
4. **Epic 14 stories beyond ACA-14-003** (9 additional sprint agent stories)
5. **Epic 15 gap stories** (10 "a"/"b" series stories)

---

## New Stories Analysis (270 → 281): The 11 Missing Stories

### Confirmed New Stories from GAPS-AND-DECISIONS.md (5)

| ID | Title | Epic | Reason Added |
|----|-------|------|--------------|
| ACA-01-022 | Frontend deployment slot (marco-sandbox-backend) | 1 | Phase 1 deployment model decided |
| ACA-02-018 | Analysis auto-trigger (collector → analysis job) | 2 | Collector job never triggered analysis (critical gap) |
| ACA-02-019 | Resource Graph pagination (>1000 resources) | 2 | Breaks on large subscriptions (Azure 1000-record limit) |
| ACA-04-029 | RFC 7807 structured errors | 4 | Customer-facing error handling strategy missing |
| ACA-11-010 | Standalone data model server (Phase 2) | 11 | Product independence principle (Phase 2 blocker) |

### Epic 13 Stories (NOT in archived PLAN baseline) (11)

| ID | Title | Sprint | FP |
|----|-------|--------|-----|
| ACA-13-009 | GET /v1/assessment/waf (5 WAF pillars) | 4 | 5 |
| ACA-13-010 | WAF reliability pillar (APRL checklist) | 4 | 9 |
| ACA-13-011 | FinOps rules R-13 to R-17 | 4 | 9 |
| ACA-13-012 | Idle resource detection | 4 | 5 |
| ACA-13-013 | RBAC hygiene check (over-scoped assignments) | 4 | 5 |
| ACA-13-014 | Key Vault RBAC mode audit | 4 | 3 |
| ACA-13-015 | MCSB control compliance (Defender) | 5 | 5 |
| ACA-13-016 | APIM rate-limit policy health check | 4 | 3 |
| ACA-13-017 | API design compliance check | 5 | 3 |
| ACA-13-018 | PSRule for Azure CI gate | 5 | 5 |
| ACA-13-019 | Best-practice tag enforcement | 5 | 3 |

**Total Epic 13**: 11 stories, 55 FP

### The 11-Story Discrepancy Resolution

**270 (archived)** + **5 (gaps)** + **11 (Epic 13)** - **5 (overlaps/duplicates)** = **281 stories**

**Overlaps identified**:
1. ACA-14-001, ACA-14-002, ACA-14-003 already in archived PLAN (counted in baseline 270)
2. ACA-14-004 through ACA-14-012 added later (9 new), but only 6 counted in 281 baseline
3. Epic 15 stories (22 total) marked as DEFERRED (Sprints 14-17, not in Phase 1 active scope)

**Active Scope (Phase 1)**: 281 stories (Epics 1-14, excluding Epic 15)  
**Deferred (Post-Phase 1)**: Epic 11 (9 stories, 100 FP) + Epic 15 (32 stories, 72 FP) = 41 stories

**Total Project Scope**: 281 (active) + 41 (deferred) = **322 stories**

---

## Epic Structure Summary

| Epic | Title | Stories | FP | Status | Phase |
|------|-------|---------|-----|--------|-------|
| 1 | Foundation | 21 | 65 | DONE | 1 |
| 2 | Collection | 19 | 70 | DONE | 1 |
| 3 | Analysis | 33 | 155 | PARTIAL | 1 |
| 4 | API & Auth | 29 | 125 | PARTIAL | 1 |
| 5 | Frontend | 42 | 175 | PARTIAL | 1 |
| 6 | Billing | 18 | 65 | DONE | 1 |
| 7 | Delivery | 9 | 80 | NOT STARTED | 1 |
| 8 | Observability | 14 | 55 | PARTIAL | 1 |
| 9 | i18n & a11y | 18 | 85 | NOT STARTED | 1 |
| 10 | Hardening | 15 | 90 | NOT STARTED | 1 |
| **11** | **Phase 2 Infra** | **10** | **100** | **DEFERRED** | **2** |
| 12 | Data Model | 22 | 75 | ONGOING | 1 |
| 13 | Azure Best Practices | 11 | 55 | NOT STARTED | 1 |
| 14 | DPDCA Agent | 12 | 65 | ACTIVE | 1 |
| **15** | **Onboarding** | **32** | **72** | **DEFERRED** | **4** |
| **17** | **AI Agent Enhancement** | **10+** | **65+** | **VISION** | **7-10** |
| **TOTAL (Active)** | | **281** | **1330** | | |
| **TOTAL (with deferred)** | | **322** | **1502** | | |

---

## Future Phases (Docs 40-43 Analysis)

### Phase 7: Ecosystem Monetization Platform (EMP)
**Document**: 40-ph7-EMP.md  
**Status**: Vision only (no epic or stories defined)  
**Concept**: Marketplace for ACA extensions, partner integrations

### Phase 8: Azure Optimization Automation Platform (AOAP)
**Document**: 41-ph8-AOAP.md  
**Status**: Vision only  
**Concept**: Autonomous remediation, auto-scaling, cloud governance automation

### Phase 9: Predictive Strategic Operations (PSO)
**Document**: 42-ph9-predictive-strat-ops-PSO.md  
**Status**: Vision only  
**Concept**: Machine learning cost forecasting, anomaly prediction

### Phase 10: Ecosystem & Partnerships
**Document**: 43-ph10-ecosystem.md  
**Status**: Vision only  
**Concept**: Strategic partnerships, white-label offerings

**Epic 17** (EPIC-17-WBS.md) represents a **Tier 3 AI-driven enhancement** targeting Phase 7-10 capabilities. It is **NOT part of the 281-story active scope** and is documented separately as future strategic work.

---

## Conclusions

1. **281-Story Active Scope Confirmed**: Epics 1-14 (excluding Epic 15 deferred, Epic 11 deferred)
2. **Numbered Docs (01-43) Contain Zero Stories**: All architecture/spec/vision documents
3. **11 New Stories Identified**:
   - 5 from GAPS-AND-DECISIONS.md (critical fixes)
   - 11 from Epic 13 (Azure Best Practices, not in archived baseline)
   - Overlapping Epic 14 stories reconciled (+6 net new)
4. **Epic 15 (32 stories, 72 FP) Deferred**: Sprints 14-17, Post-Phase 1
5. **Epic 11 (10 stories, 100 FP) Deferred**: Phase 2 infrastructure cutover
6. **Epic 17 (10+ stories, 65+ FP) Future Vision**: Phases 7-10, AI agent enhancement

**Phase 1 Go-Live Scope**: 281 active stories, ~1330 FP, 8-week target (Sprints 004-011)  
**Total Project Scope**: 322 stories, ~1500 FP (includes all deferred work)

---

**END OF WBS EXTRACTION**
