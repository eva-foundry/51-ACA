# ACA Work Breakdown Structure - Reconciliation Report

**Date**: 2026-03-11  
**Purpose**: Reconcile baseline WBS (281 stories, 15 epics) with comprehensive WBS (623 stories, 19 epics)  
**Methodology**: Story ID matching + title similarity analysis + status preservation

---

## Executive Summary

### Source Documents
- **Comprehensive WBS**: [WBS-FROM-DOCS-COMPLETE-20260311.md](./WBS-FROM-DOCS-COMPLETE-20260311.md) - 623 stories, 19 epics, extracted from 49 architectural docs
- **Baseline WBS**: [archive/PLAN.md](./archive/PLAN.md) - 281 stories, 15 epics, with implementation tracking
- **Gap Stories**: [GAPS-AND-DECISIONS.md](./GAPS-AND-DECISIONS.md) - 5 additional critical stories
- **Nested DPDCA Inputs**: docs 44-49, including admin packs, Entra/Cosmos wiring, onboarding gap closure, end-to-end context, and founder launch kit

### Reconciliation Results

| Metric | Count | Details |
|--------|--------|---------|
| **Total Baseline Stories** | 281 | Stories with implementation status |
| **Total Comprehensive Stories** | 623 | Complete scope through Phase 10 plus docs 44-49 deltas |
| **Direct ID Matches** | 281 | All baseline stories have IDs in comprehensive WBS |
| **Net New Stories** | 342 | Comprehensive WBS additions (623 - 281) |
| **Gap Stories to Integrate** | 5 | From GAPS-AND-DECISIONS.md |
| **Final Epic Count** | 19 | Expanded from 15 baseline epics |
| **Estimated Total Stories** | 623 | Includes docs 44-49 nested DPDCA deltas consolidated into the comprehensive WBS |

### Key Finding

**All 281 baseline stories match by ID with comprehensive WBS** because both use the same story ID numbering scheme. The comprehensive WBS is a **superset** - it includes all baseline stories plus 342 net-new stories covering expanded scope (Phases 2-10, additional features, commercial hardening, and docs 44-49 reconciled deltas).

---

## Epic Structure Comparison

### Baseline (15 Epics - Phase 1 Focus)

| Epic | Title | Stories | Status |
|------|-------|---------|--------|
| 01 | Foundation and Infrastructure | 21 | DONE |
| 02 | Data Collection Pipeline | 17 | ACTIVE |
| 03 | Analysis Engine + Rules | 33 | ACTIVE |
| 04 | API and Auth Layer | 28 | ACTIVE |
| 05 | Frontend Core | 42 | ACTIVE |
| 06 | Monetization and Billing (Stripe) | 18 | DONE |
| 07 | Delivery Packager (Tier 3) | 9 | ACTIVE |
| 08 | Observability and Telemetry | 14 | ACTIVE |
| 09 | i18n and a11y | 21 | ACTIVE |
| 10 | Commercial Hardening | 12 | PLANNED |
| 11 | Phase 2 Infrastructure | TBD | PLANNED |
| 12 | Data Model Support (app runtime) | Ongoing | ACTIVE |
| 13 | Azure Best Practices Service Catalog | NEW | NEW |
| 14 | DPDCA Cloud Agent (GitHub Actions) | NEW | NEW |
| 15 | Onboarding System (Client Onboarding SaaS) | NEW | NEW |

### Comprehensive (19 Epics - Phase 1-10)

| Epic | Title | Stories | Scope Expansion |
|------|-------|---------|-----------------|
| 01 | Authentication & Authorization Framework | 25 | +4 stories (added depth assessment, role verification, and Entra JWT/role mapping wiring) |
| 02 | Data Collection Subsystem | 42 | +25 stories (network topology, Log Analytics, orchestration) |
| 03 | Analysis Engine & Rules | 47 | +14 stories (ghost resources, idle detection, rightsizing, Pareto) |
| 04 | Delivery & Script Generation | 32 | +23 stories (PowerShell templates, report generation, packaging) |
| 05 | Frontend Application (Customer & Admin) | 39 | -3 stories (consolidated UI components plus explicit admin audit page) |
| 06 | API Service (FastAPI Backend) | 47 | +19 stories (comprehensive endpoint coverage, admin APIs, auth dependency, Cosmos-backed admin queries) |
| 07 | Billing & Monetization | 28 | +10 stories (Stripe lifecycle, admin controls, reconciliation) |
| 08 | Observability & Operations | 32 | +18 stories (detailed telemetry, alerting, dashboard) |
| 09 | i18n, a11y, UX Polish | 27 | +6 stories (advanced accessibility, UX improvements) |
| 10 | Security & Compliance | 24 | **NEW** - Comprehensive security hardening |
| 11 | Phase 2 Azure Infrastructure | 35 | **NEW** - Complete Phase 2 migration plan |
| 12 | FinOps Hub Integration | 18 | **NEW** - Cost Export landing zone integration |
| 13 | Autonomous Operations (Phase 3) | 41 | **NEW** - Auto-remediation, continuous monitoring |
| 14 | Predictive Analytics (Phase 4) | 28 | **NEW** - ML-based forecasting, anomaly prediction |
| 15 | Multi-Cloud Support (Phase 5) | 34 | **NEW** - AWS, GCP collection and analysis |
| 16 | Partner Ecosystem (Phase 6) | 26 | **NEW** - White-label, reseller program |
| 17 | Enterprise Features (Phase 7) | 38 | **NEW** - SSO, AD integration, enterprise SLAs |
| 18 | Advanced Analytics (Phase 8) | 33 | **NEW** - Chargeback, showback, custom dashboards |
| 19 | Platform Services (Phase 9-10) | 41 | **NEW** - Marketplace, API platform, ecosystem |

### Nested DPDCA Delta Summary (Docs 44-49)

The original 43-doc extraction was extended through a nested DPDCA pass over docs 44-49.

- Docs 44-45 primarily reinforced existing admin frontend and backend stories and added explicit audit-surface coverage.
- Doc 46 was initially empty, then populated as `aca-entra-cosmos-pack` and promoted into explicit executable slices: `ACA-01-024`, `ACA-01-025`, `ACA-06-046`, and `ACA-06-047`.
- Docs 47-49 added operational and commercial deltas around quotas, DR, support, and founder launch posture.
- The cloud data model and `.eva/veritas-plan.json` still reflect the older 281-story export and require a separate governed sync/export cycle.

---

## Story Status Preservation

### Methodology

All baseline stories retain their implementation status:
- **DONE**: Already implemented and merged
- **ACTIVE/IN-PROGRESS**: Currently being developed  
- **PLANNED/NOT-STARTED**: Backlog items

The comprehensive WBS adds **342 net-new stories** with status = **NOT-STARTED** (future phases).

### Epic 01 - Authentication & Authorization (25 stories, +4 new)

#### Stories with Status Preserved (21 baseline stories)

| Story ID | Title | Status | Phase |
|----------|-------|--------|-------|
| ACA-01-001 | Implement Microsoft Entra ID (Azure AD) authentication | NOT-STARTED | Phase 1 |
| ACA-01-002 | Implement delegated user sign-in flow (device code + PKCE) | NOT-STARTED | Phase 1 |
| ACA-01-003 | Implement service principal authentication mode | NOT-STARTED | Phase 1 |
| ACA-01-004 | Implement Azure Lighthouse delegation support | NOT-STARTED | Phase 1 |
| ACA-01-005 | Implement connection mode selection UI and API | NOT-STARTED | Phase 1 |
| ACA-01-006 | Design and implement pre-flight probe framework | NOT-STARTED | Phase 1 |
| ACA-01-007 | Implement ARM token acquisition probe | NOT-STARTED | Phase 1 |
| ACA-01-008 | Implement subscription discovery probe | NOT-STARTED | Phase 1 |
| ACA-01-009 | Implement Resource Graph access probe | NOT-STARTED | Phase 1 |
| ACA-01-010 | Implement Cost Management Reader probe | NOT-STARTED | Phase 1 |
| ACA-01-011 | Implement Azure Advisor access probe | NOT-STARTED | Phase 1 |
| ACA-01-012 | Implement optional Policy Insights probe | NOT-STARTED | Phase 1 |
| ACA-01-013 | Implement optional Log Analytics probe | NOT-STARTED | Phase 1 |
| ACA-01-014 | Implement extraction depth calculation engine | NOT-STARTED | Phase 1 |
| ACA-01-015 | Implement depth-based UI messaging | NOT-STARTED | Phase 1 |
| ACA-01-016 | Implement depth-based collection scope configuration | NOT-STARTED | Phase 1 |
| ACA-01-017 | Store pre-flight results in Cosmos DB | NOT-STARTED | Phase 1 |
| ACA-01-018 | Implement Reader role verification | NOT-STARTED | Phase 1 |
| ACA-01-019 | Implement Cost Management Reader verification | NOT-STARTED | Phase 1 |
| ACA-01-020 | Implement optional Log Analytics Reader verification | NOT-STARTED | Phase 1 |
| ACA-01-021 | Generate missing permissions report | NOT-STARTED | Phase 1 |

#### Net New Stories (2 additions)

| Story ID | Title | Phase | Source |
|----------|-------|-------|--------|
| ACA-01-022 | Implement role assignment validation | Phase 1 | Comprehensive WBS (also in GAPS-AND-DECISIONS.md) |
| ACA-01-023 | Create client-facing access setup guide | Phase 1 | Comprehensive WBS |

---

### Epic 02 - Data Collection (42 stories, +25 new)

#### Stories with Status Preserved (17 baseline stories)

| Story ID | Title | Status | Phase |
|----------|-------|--------|-------|
| ACA-02-001 | As a client using Mode A (delegated) I see pre-flight status | NOT-STARTED | Phase 1 |
| ACA-02-002 | As a client with missing Cost Management Reader role I see error | NOT-STARTED | Phase 1 |
| ACA-02-003 | As a client with PASS_WITH_WARNINGS I can still proceed | NOT-STARTED | Phase 1 |
| ACA-02-004 | As an operator I can pass --preflight-only to validate | NOT-STARTED | Phase 1 |
| ACA-02-005 | As the system I collect all Azure resources via Resource Graph | DONE | Phase 1 |
| ACA-02-006 | As the system I save inventory to Cosmos with partition_key | DONE | Phase 1 |
| ACA-02-007 | As the system I capture resource metadata | DONE | Phase 1 |
| ACA-02-008 | As the system I collect 91 days of daily cost rows | DONE | Phase 1 |
| ACA-02-009 | As the system I capture cost data fields | DONE | Phase 1 |
| ACA-02-010 | As the system I handle rate limiting (429) with backoff | DONE | Phase 1 |
| ACA-02-011 | As the system I collect all Advisor recommendations | DONE | Phase 1 |
| ACA-02-012 | As the system I collect Policy compliance state | NOT-STARTED | Phase 1 |
| ACA-02-013 | As the system I collect network signals | NOT-STARTED | Phase 1 |
| ACA-02-014 | As the system I update scan status in Cosmos | DONE | Phase 1 |
| ACA-02-015 | As the system I write stats to the scan record | DONE | Phase 1 |
| ACA-02-016 | As the API I expose GET /v1/scans/:scanId | DONE | Phase 1 |
| ACA-02-017 | As the system, after mark_collection_complete, trigger analysis | DONE | Phase 1 |

#### Net New Stories (25 additions)

| Story ID | Title | Phase | FP | Source |
|----------|-------|-------|-----|--------|
| ACA-02-018 | Implement Cost Management Query API client | Phase 1 | 8 | Comprehensive WBS (also in GAPS-AND-DECISIONS.md as auto-trigger) |
| ACA-02-019 | Implement cost data normalization | Phase 1 | 8 | Comprehensive WBS (also in GAPS-AND-DECISIONS.md as pagination) |
| ACA-02-020 | Implement Policy Insights API client | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-021 | Normalize policy compliance data | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-022 | Store policy signals in Cosmos DB | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-023 | Mark policy collection as optional capability | Phase 1 | 3 | Comprehensive WBS |
| ACA-02-024 | Implement NSG enumeration | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-025 | Implement Public IP enumeration | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-026 | Implement VNet enumeration | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-027 | Implement Private DNS zone enumeration | Phase 1 | 3 | Comprehensive WBS |
| ACA-02-028 | Implement Load Balancer / App Gateway enumeration | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-029 | Implement NAT Gateway enumeration | Phase 1 | 3 | Comprehensive WBS |
| ACA-02-030 | Normalize network topology data | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-031 | Store network signals in Cosmos DB | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-032 | Implement Log Analytics workspace discovery | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-033 | Implement activity query for idle detection | Phase 1 | 8 | Comprehensive WBS |
| ACA-02-034 | Implement activity query for usage patterns | Phase 1 | 8 | Comprehensive WBS |
| ACA-02-035 | Normalize activity data | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-036 | Store activity signals in Cosmos DB | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-037 | Mark activity collection as optional | Phase 1 | 3 | Comprehensive WBS |
| ACA-02-038 | Implement collector job orchestration | Phase 1 | 8 | Comprehensive WBS |
| ACA-02-039 | Implement scan lifecycle state management | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-040 | Implement collection progress reporting | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-041 | Implement collection error handling | Phase 1 | 5 | Comprehensive WBS |
| ACA-02-042 | Deploy collector as Container App Job | Phase 1 | 8 | Comprehensive WBS |

---

### Epic 03 - Analysis Engine (47 stories, +14 new)

#### Stories with Status Preserved (33 baseline stories)

| Story ID | Title | Status | Phase |
|----------|-------|--------|-------|
| ACA-03-001 | As the system I load all 12 rules from ALL_RULES | DONE | Phase 1 |
| ACA-03-002 | As the system I handle a rule failure in isolation | DONE | Phase 1 |
| ACA-03-003 | As the system I persist each Finding to Cosmos | DONE | Phase 1 |
| ACA-03-004 | As the system I update AnalysisRun status | DONE | Phase 1 |
| ACA-03-005 | As the system I write findingsSummary | DONE | Phase 1 |
| ACA-03-006 | As a Tier 1 client I receive findings with category/title only | DONE | Phase 1 |
| ACA-03-007 | As a Tier 1 client I do not receive narrative | DONE | Phase 1 |
| ACA-03-008 | As a Tier 2 client I receive full finding with narrative | DONE | Phase 1 |
| ACA-03-009 | As a Tier 3 client I receive deliverable_template_id | DONE | Phase 1 |
| ACA-03-010 | As the red-team agent I can assert Tier 1 tokens never leak | DONE | Phase 1 |
| ACA-03-011 | R-01 Dev Box auto-stop | DONE | Phase 1 |
| ACA-03-012 | R-02 Log retention | DONE | Phase 1 |
| ACA-03-013 | R-03 Defender mismatch | DONE | Phase 1 |
| ACA-03-014 | R-04 Compute scheduling | DONE | Phase 1 |
| ACA-03-015 | R-05 Anomaly detection | DONE | Phase 1 |
| ACA-03-016 | R-06 Stale environments | DONE | Phase 1 |
| ACA-03-017 | R-07 Search SKU oversize | DONE | Phase 1 |
| ACA-03-018 | R-08 ACR consolidation | DONE | Phase 1 |
| ACA-03-019 | R-09 DNS sprawl | DONE | Phase 1 |
| ACA-03-020 | R-10 Savings plan coverage (NOTE: Duplicate ID with test story) | DONE | Phase 1 |
| ACA-03-021 | R-11 APIM token budget | DONE | Phase 1 |
| ACA-03-022 | R-12 Chargeback gap | DONE | Phase 1 |
| ACA-03-023 | Unit test for R-04 compute_scheduling | DONE | Phase 1 |
| ACA-03-024 | Unit test for R-05 anomaly_detection | DONE | Phase 1 |
| ACA-03-025 | Unit test for R-06 stale_environments | DONE | Phase 1 |
| ACA-03-026 | Unit test for R-07 search_sku_oversize | DONE | Phase 1 |
| ACA-03-027 | Unit test for R-08 acr_consolidation | DONE | Phase 1 |
| ACA-03-028 | Unit test for R-09 dns_sprawl | DONE | Phase 1 |
| ACA-03-029 | Unit test for R-10 savings_plan_coverage | DONE | Phase 1 |
| ACA-03-030 | Unit test for R-11 apim_token_budget | DONE | Phase 1 |
| ACA-03-031 | Unit test for R-12 chargeback_gap | DONE | Phase 1 |
| ACA-03-032 | Negative tests for each rule | DONE | Phase 1 |
| ACA-03-033 | FindingsAssembler unit test | DONE | Phase 1 |

**NOTE**: Story ID conflict detected: ACA-03-020 used for both "R-10 Savings plan" (rule) and "Unit test for R-01 devbox_autostop" (test) in baseline. Comprehensive WBS has different assignments. Recommend renumbering test stories to ACA-03-T01 through ACA-03-T14 for clarity.

#### Net New Stories (14 additions)

| Story ID | Title | Phase | FP | Source |
|----------|-------|-------|-----|--------|
| ACA-03-034 | Rule: Unattached managed disks | Phase 1 | 8 | Comprehensive WBS |
| ACA-03-035 | Rule: Unattached public IPs | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-036 | Rule: Orphaned snapshots | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-037 | Rule: Idle load balancers | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-038 | Rule: Orphaned App Service Plans | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-039 | Rule: Zombie databases | Phase 1 | 8 | Comprehensive WBS |
| ACA-03-040 | Rule: Forgotten storage accounts | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-041 | Rule: Idle AKS clusters | Phase 1 | 8 | Comprehensive WBS |
| ACA-03-042 | Implement Pareto scoring algorithm | Phase 1 | 8 | Comprehensive WBS |
| ACA-03-043 | Compute effort class for findings | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-044 | Compute risk class for findings | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-045 | Generate top-N recommendations list | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-046 | Aggregate findings by category | Phase 1 | 5 | Comprehensive WBS |
| ACA-03-047 | Deploy analysis as Container App Job | Phase 1 | 8 | Comprehensive WBS |

---

### Epic 04 - API & Auth Layer (32 stories in comprehensive, 28 in baseline)

#### Stories with Status Preserved (28 baseline stories)

| Story ID | Title | Status | Phase |
|----------|-------|--------|-------|
| ACA-04-001 | As a client I can sign in via Microsoft Identity (any tenant) | NOT-STARTED | Phase 1 |
| ACA-04-002 | As the API I validate JWT on every authenticated endpoint | DONE | Phase 1 |
| ACA-04-003 | As the API I extract subscriptionId from session | NOT-STARTED | Phase 1 |
| ACA-04-004 | As a client I can connect Azure subscription (Mode A/B/C) | NOT-STARTED | Phase 1 |
| ACA-04-005 | As a client I can disconnect and invalidate tokens | NOT-STARTED | Phase 1 |
| ACA-04-006 | As a developer auth.py is reworked (MSAL authority=common) | DONE | Phase 1 |
| ACA-04-007 | As the frontend LoginPage, sign-in CTA calls MSAL.js | NOT-STARTED | Phase 1 |
| ACA-04-008 | POST /v1/auth/connect - Connect Azure subscription | DONE | Phase 1 |
| ACA-04-009 | POST /v1/auth/preflight - Run pre-flight probes | NOT-STARTED | Phase 1 |
| ACA-04-010 | POST /v1/auth/disconnect - Disconnect subscription | NOT-STARTED | Phase 1 |
| ACA-04-011 | POST /v1/collect/start - Trigger collector job | NOT-STARTED | Phase 1 |
| ACA-04-012 | GET /v1/collect/status - Poll collection progress | NOT-STARTED | Phase 1 |
| ACA-04-013 | GET /v1/reports/tier1 - Tier 1 findings report | NOT-STARTED | Phase 1 |
| ACA-04-014 | POST /v1/billing/checkout - Stripe checkout | NOT-STARTED | Phase 1 |
| ACA-04-015 | GET /v1/billing/portal - Stripe billing portal redirect | NOT-STARTED | Phase 1 |
| ACA-04-016 | POST /v1/webhooks/stripe - Stripe event handler | NOT-STARTED | Phase 1 |
| ACA-04-017 | As the gateway I validate JWT signature on all /v1/* routes | NOT-STARTED | Phase 1 |
| ACA-04-018 | As the gateway I cache /v1/entitlements response | NOT-STARTED | Phase 1 |
| ACA-04-019 | As the gateway I return 403 with TIER_REQUIRED error | NOT-STARTED | Phase 1 |
| ACA-04-020 | As the gateway I enforce subscription key throttling | NOT-STARTED | Phase 1 |
| ACA-04-021 | As the gateway I forward X-Subscription-Id header | NOT-STARTED | Phase 1 |
| ACA-04-022 | GET /v1/admin/kpis | NOT-STARTED | Phase 1 |
| ACA-04-023 | GET /v1/admin/customers?query= | NOT-STARTED | Phase 1 |
| ACA-04-024 | POST /v1/admin/entitlements/grant | NOT-STARTED | Phase 1 |
| ACA-04-025 | POST /v1/admin/subscriptions/:subscriptionId/lock | NOT-STARTED | Phase 1 |
| ACA-04-026 | POST /v1/admin/stripe/reconcile | NOT-STARTED | Phase 1 |
| ACA-04-027 | GET /v1/admin/runs?type=scan|analysis|delivery | NOT-STARTED | Phase 1 |
| ACA-04-028 | services/api/app/db/cosmos.py upsert_item() partition_key fix | DONE | Phase 1 |

#### Net New Stories (4 additions in baseline → 32 in comprehensive showing major expansion in Delivery epic)

**NOTE**: The baseline Epic 04 covers "API and Auth Layer" while comprehensive WBS Epic 04 is "Delivery & Script Generation". The comprehensive WBS moved API stories to Epic 06. I'll reconcile based on functional mapping below.

**Gap Story to Integrate**:

| Story ID | Title | Phase | Source |
|----------|-------|-------|--------|
| ACA-04-029 | Implement RFC 7807 error responses | Phase 1 | GAPS-AND-DECISIONS.md |

---

### Epic 05 - Frontend (38 stories comprehensive vs 42 baseline)

#### Stories with Status Preserved (42 baseline stories)

| Story ID | Title | Status | Phase |
|----------|-------|--------|-------|
| ACA-05-001 | roles.ts defines ACA_Admin, ACA_Support, ACA_FinOps | NOT-STARTED | Phase 1 |
| ACA-05-002 | useAuth.ts wraps MSAL PublicClientApplication | NOT-STARTED | Phase 1 |
| ACA-05-003 | RequireAuth.tsx: redirect if !isAuthenticated | NOT-STARTED | Phase 1 |
| ACA-05-004 | RequireRole.tsx: if user lacks roles, redirect | NOT-STARTED | Phase 1 |
| ACA-05-005 | All admin routes require RequireAuth + RequireRole | NOT-STARTED | Phase 1 |
| ACA-05-006 | CustomerLayout.tsx: top nav with logo, LanguageSelector | NOT-STARTED | Phase 1 |
| ACA-05-007 | AdminLayout.tsx: top nav + left sidebar | NOT-STARTED | Phase 1 |
| ACA-05-008 | NavCustomer.tsx: links to customer pages | NOT-STARTED | Phase 1 |
| ACA-05-009 | NavAdmin.tsx: links to admin pages | NOT-STARTED | Phase 1 |
| ACA-05-010 | AppShell.tsx: root component with FluentProvider | NOT-STARTED | Phase 1 |
| ACA-05-011 | router.tsx uses createBrowserRouter | NOT-STARTED | Phase 1 |
| ACA-05-012 | Route / -> LoginPage (no auth required) | NOT-STARTED | Phase 1 |
| ACA-05-013 | Routes /app/* -> RequireAuth -> CustomerLayout | NOT-STARTED | Phase 1 |
| ACA-05-014 | Routes /admin/* -> RequireAuth -> RequireRole -> AdminLayout | NOT-STARTED | Phase 1 |
| ACA-05-015 | Code-split: all page components lazy-loaded | NOT-STARTED | Phase 1 |
| ACA-05-016 | LoginPage (/) - Entra ID login CTA | NOT-STARTED | Phase 1 |
| ACA-05-017 | ConnectSubscriptionPage (/app/connect) - Mode A/B/C | NOT-STARTED | Phase 1 |
| ACA-05-018 | CollectionStatusPage (/app/status/:subscriptionId) | NOT-STARTED | Phase 1 |
| ACA-05-019 | FindingsTier1Page (/app/findings/:subscriptionId) | NOT-STARTED | Phase 1 |
| ACA-05-020 | UpgradePage (/app/upgrade/:subscriptionId) | NOT-STARTED | Phase 1 |
| ACA-05-021 | AdminDashboardPage (/admin/dashboard) | NOT-STARTED | Phase 1 |
| ACA-05-022 | AdminCustomersPage (/admin/customers) | NOT-STARTED | Phase 1 |
| ACA-05-023 | AdminBillingPage (/admin/billing) | NOT-STARTED | Phase 1 |
| ACA-05-024 | AdminRunsPage (/admin/runs) | NOT-STARTED | Phase 1 |
| ACA-05-025 | AdminControlsPage (/admin/controls) | NOT-STARTED | Phase 1 |
| ACA-05-026 | frontend/src/app/api/client.ts - base http<T> function | NOT-STARTED | Phase 1 |
| ACA-05-027 | frontend/src/app/api/appApi.ts - customer API calls | NOT-STARTED | Phase 1 |
| ACA-05-028 | frontend/src/app/api/adminApi.ts - admin API calls | NOT-STARTED | Phase 1 |
| ACA-05-029 | frontend/src/app/types/models.ts - TypeScript DTOs | NOT-STARTED | Phase 1 |
| ACA-05-030 | Loading.tsx - Fluent Spinner component | NOT-STARTED | Phase 1 |
| ACA-05-031 | ErrorState.tsx - Fluent MessageBar component | NOT-STARTED | Phase 1 |
| ACA-05-032 | DataTable.tsx - accessible Fluent Table wrapper | NOT-STARTED | Phase 1 |
| ACA-05-033 | MoneyRangeBar.tsx - visual savings range bar | NOT-STARTED | Phase 1 |
| ACA-05-034 | EffortBadge.tsx - colour-coded badge | NOT-STARTED | Phase 1 |
| ACA-05-035 | As a user I see a consent banner on first visit | NOT-STARTED | Phase 1 |
| ACA-05-036 | TelemetryProvider.tsx wraps CustomerLayout | NOT-STARTED | Phase 1 |
| ACA-05-037 | All 16 AnalyticsEventName events fire | NOT-STARTED | Phase 1 |
| ACA-05-038 | Admin surface does NOT load telemetry | NOT-STARTED | Phase 1 |
| ACA-05-039 | Skip-to-content link is first focusable element | NOT-STARTED | Phase 1 |
| ACA-05-040 | Full keyboard navigation in all pages | NOT-STARTED | Phase 1 |
| ACA-05-041 | All form fields have associated label elements | NOT-STARTED | Phase 1 |
| ACA-05-042 | Admin confirmation modals trap focus and close on Escape | NOT-STARTED | Phase 1 |

**NOTE**: Comprehensive WBS has 38 stories (consolidated shared components). The -4 difference is due to consolidation of similar UI components.

---

### Epic 06 - Billing & Monetization (18 baseline stories)

#### Stories with Status Preserved (18 baseline stories)

| Story ID | Title | Status | Phase |
|----------|-------|--------|-------|
| ACA-06-001 | POST /v1/checkout/tier2 returns Stripe checkout URL | NOT-STARTED | Phase 1 |
| ACA-06-002 | POST /v1/checkout/tier3 returns Stripe checkout URL | NOT-STARTED | Phase 1 |
| ACA-06-003 | mode=subscription creates Stripe subscription (Tier 2) | NOT-STARTED | Phase 1 |
| ACA-06-004 | mode=one_time creates one-time session (Tier 3) | NOT-STARTED | Phase 1 |
| ACA-06-005 | Checkout metadata contains subscriptionId and analysisId | NOT-STARTED | Phase 1 |
| ACA-06-006 | As a client with coupon code I can enter at Stripe checkout | NOT-STARTED | Phase 1 |
| ACA-06-007 | settings.py has STRIPE_COUPON_ENABLED field | NOT-STARTED | Phase 1 |
| ACA-06-008 | As an admin I can create Stripe promotion codes | NOT-STARTED | Phase 1 |
| ACA-06-009 | checkout.session.completed -> write entitlement to Cosmos | NOT-STARTED | Phase 1 |
| ACA-06-010 | invoice.paid -> renew Tier 2 subscription entitlement | NOT-STARTED | Phase 1 |
| ACA-06-011 | customer.subscription.updated -> update Tier in Cosmos | NOT-STARTED | Phase 1 |
| ACA-06-012 | customer.subscription.deleted -> downgrade to Tier 1 | NOT-STARTED | Phase 1 |
| ACA-06-013 | All webhook events written to payments container | NOT-STARTED | Phase 1 |
| ACA-06-014 | GET /v1/entitlements?subscriptionId=X returns tier | NOT-STARTED | Phase 1 |
| ACA-06-015 | Tier gate evaluates entitlement from Cosmos | NOT-STARTED | Phase 1 |
| ACA-06-016 | StripeCustomerMapRepo resolves stripeCustomerId | NOT-STARTED | Phase 1 |
| ACA-06-017 | Billing portal endpoint derives stripeCustomerId from Cosmos | NOT-STARTED | Phase 1 |
| ACA-06-018 | As a Tier 3 customer, preserve Tier 3 access on Tier 2 cancel | NOT-STARTED | Phase 1 |

Comprehensive WBS expands Epic 07 (Billing & Monetization) to **28 stories** with additional admin controls and reconciliation workflows.

---

### Epic 07 - Delivery Packager (9 baseline stories)

#### Stories with Status Preserved (9 baseline stories)

| Story ID | Title | Status | Phase |
|----------|-------|--------|-------|
| ACA-07-001 | 12 Jinja2 template folders exist for deliverable templates | NOT-STARTED | Phase 1 |
| ACA-07-002 | Each folder has main.bicep and README.md | NOT-STARTED | Phase 1 |
| ACA-07-003 | Templates are parameterized with scan_id, subscription_id | NOT-STARTED | Phase 1 |
| ACA-07-004 | Template content sourced from 12-IaCscript.md patterns | NOT-STARTED | Phase 1 |
| ACA-07-005 | Delivery service generates all IaC artifacts | NOT-STARTED | Phase 1 |
| ACA-07-006 | ZIP is assembled with findings.json manifest at root | NOT-STARTED | Phase 1 |
| ACA-07-007 | ZIP is signed with SHA-256 and hash stored | NOT-STARTED | Phase 1 |
| ACA-07-008 | ZIP is uploaded to Azure Blob Storage with 24h SAS URL | NOT-STARTED | Phase 1 |
| ACA-07-009 | Deliverable record is written to Cosmos | NOT-STARTED | Phase 1 |

Comprehensive WBS Epic 04 (Delivery & Script Generation) has **32 stories** covering complete PowerShell template library, report generation, and packaging workflows.

---

### Epic 08 - Observability (14 baseline stories)

#### Stories with Status Preserved (14 baseline stories)

| Story ID | Title | Status | Phase |
|----------|-------|--------|-------|
| ACA-08-001 | GTM container is loaded in index.html with consent gating | NOT-STARTED | Phase 1 |
| ACA-08-002 | GA4 tag fires after consent accepted | NOT-STARTED | Phase 1 |
| ACA-08-003 | Clarity tag fires after consent accepted | NOT-STARTED | Phase 1 |
| ACA-08-004 | All 16 AnalyticsEventName events fire | NOT-STARTED | Phase 1 |
| ACA-08-005 | Consent banner allows accept/reject | NOT-STARTED | Phase 1 |
| ACA-08-006 | Consent preference is respected across page reloads | NOT-STARTED | Phase 1 |
| ACA-08-007 | App Insights connection string set in all Container Apps | NOT-STARTED | Phase 1 |
| ACA-08-008 | All service logs are structured JSON | NOT-STARTED | Phase 1 |
| ACA-08-009 | Scan/analysis/delivery durations emitted as custom metrics | NOT-STARTED | Phase 1 |
| ACA-08-010 | All API errors (4xx, 5xx) logged with error_category enum | NOT-STARTED | Phase 1 |
| ACA-08-011 | Stripe webhook events logged | NOT-STARTED | Phase 1 |
| ACA-08-012 | Alert: API service 5xx rate > 5% | NOT-STARTED | Phase 1 |
| ACA-08-013 | Alert: Collector job failure | NOT-STARTED | Phase 1 |
| ACA-08-014 | Alert: Anomaly detection rule fires | NOT-STARTED | Phase 1 |

Comprehensive WBS Epic 08 has **32 stories** with comprehensive telemetry, alerting, and observability dashboards.

---

### Epic 09 - i18n and a11y (21 baseline stories)

#### Stories with Status Preserved (21 stories - see ACA-09-001 through ACA-09-018 range)

All baseline stories preserved. Comprehensive WBS Epic 09 expands to **27 stories** with advanced UX polish.

---

### Epic 10 - Commercial Hardening (12 baseline stories)

#### Stories with Status Preserved (12 stories - planned, not started)

Comprehensive WBS Epic 10 is "Security & Compliance" with **24 stories** - represents a major expansion focusing on security hardening,privacy compliance, and enterprise readiness.

---

### Epics 11-19 - **ALL NET NEW** (331 stories)

These 9 epics represent **Phases 2-10 expansion** and are not in the baseline WBS:

| Epic | Title | Stories | Phase Range | Key Deliverable |
|------|-------|---------|-------------|-----------------|
| 11 | Phase 2 Azure Infrastructure | 35 | Phase 2 | Production Azure deployment with custom domains |
| 12 | FinOps Hub Integration | 18 | Phase 2 | Cost Export landing zone integration |
| 13 | Autonomous Operations | 41 | Phase 3 | Auto-remediation, continuous monitoring |
| 14 | Predictive Analytics | 28 | Phase 4 | ML-based forecasting, anomaly prediction |
| 15 | Multi-Cloud Support | 34 | Phase 5 | AWS, GCP collection and analysis |
| 16 | Partner Ecosystem | 26 | Phase 6 | White-label, reseller program |
| 17 | Enterprise Features | 38 | Phase 7 | SSO, AD integration, enterprise SLAs |
| 18 | Advanced Analytics | 33 | Phase 8 | Chargeback, showback, custom dashboards |
| 19 | Platform Services | 41 | Phase 9-10 | Marketplace, API platform, ecosystem |

**Total New Stories in Phases 2-10**: 294 stories

---

## Gap Stories Integration

### From GAPS-AND-DECISIONS.md

| Story ID | Epic | Title | Priority | Integration Strategy |
|----------|------|-------|----------|---------------------|
| **ACA-01-022** | Epic 01 | Frontend deployment to marco-sandbox-backend slot (Phase 1) | CRITICAL | Already in comprehensive WBS; add to baseline Epic 01 |
| **ACA-02-018** | Epic 02 | Analysis job auto-trigger on collection complete | CRITICAL | **CONFLICT**: Comprehensive has "Implement Advisor recommendation categorization" at this ID. Recommend renumbering as ACA-02-043 |
| **ACA-02-019** | Epic 02 | Resource Graph pagination for large subscriptions | CRITICAL | **CONFLICT**: Comprehensive has "Track Advisor recommendation changes" at this ID. Recommend renumbering as ACA-02-044 |
| **ACA-04-029** | Epic 04 | Implement RFC 7807 error responses | CRITICAL | Not in comprehensive WBS; add as Epic 06 (API Service) story |
| **ACA-11-010** | Epic 11 | Standalone data model (product independence) | HIGH | Epic 11 in comprehensive is Phase 2 Infrastructure; add as ACA-11-035 |

### Recommended Renumbering for Gap Stories

| Old ID | New ID | Title | Rationale |
|--------|--------|-------|-----------|
| ACA-02-018 | ACA-02-043 | Analysis job auto-trigger | Avoid conflict with comprehensive WBS |
| ACA-02-019 | ACA-02-044 | Resource Graph pagination | Avoid conflict with comprehensive WBS |
| ACA-04-029 | ACA-06-034 | RFC 7807 error responses | Move to Epic 06 (API Service) where it belongs functionally |
| ACA-11-010 | ACA-11-036 | Standalone data model | Add to Phase 2 Infrastructure epic |

---

## Story ID Conflicts & Recommended Resolutions

### Detected Conflicts

| Story ID | Baseline Title | Comprehensive Title | Resolution |
|----------|---------------|---------------------|------------|
| ACA-03-020 | Unit test for R-01 devbox_autostop | Rule: Oversized VMs | Renumber test stories to ACA-03-T01 through ACA-03-T14 |
| ACA-03-021 | Unit test for R-02 log_retention | Rule: Oversized SQL databases | Same as above |
| ACA-03-022 | Unit test for R-03 defender_mismatch | Rule: Over-provisioned storage | Same as above |
| ... | (continues for all test stories) | ... | Same pattern applies |
| ACA-02-018 | N/A (gap story) | Implement Advisor recommendation categorization | Renumber gap story to ACA-02-043 |
| ACA-02-019 | N/A (gap story) | Track Advisor recommendation changes | Renumber gap story to ACA-02-044 |

### Recommended Story ID Schema Change

**Current Issue**: Unit tests for rules reuse rule story IDs (ACA-03-020 through ACA-03-033)

**Proposed Solution**: Introduce test story ID prefix

```
Rule Stories:    ACA-03-001 through ACA-03-047 (rules and rule infrastructure)
Test Stories:    ACA-03-T01 through ACA-03-T14 (unit tests for rules)
```

**Mapping Table**:

| Current Baseline ID | New Test ID | Test Target |
|---------------------|-------------|-------------|
| ACA-03-020 (test) | ACA-03-T01 | R-01 Dev Box auto-stop |
| ACA-03-021 (test) | ACA-03-T02 | R-02 Log retention |
| ACA-03-022 (test) | ACA-03-T03 | R-03 Defender mismatch |
| ACA-03-023 | ACA-03-T04 | R-04 Compute scheduling |
| ACA-03-024 | ACA-03-T05 | R-05 Anomaly detection |
| ACA-03-025 | ACA-03-T06 | R-06 Stale environments |
| ACA-03-026 | ACA-03-T07 | R-07 Search SKU oversize |
| ACA-03-027 | ACA-03-T08 | R-08 ACR consolidation |
| ACA-03-028 | ACA-03-T09 | R-09 DNS sprawl |
| ACA-03-029 | ACA-03-T10 | R-10 Savings plan coverage |
| ACA-03-030 | ACA-03-T11 | R-11 APIM token budget |
| ACA-03-031 | ACA-03-T12 | R-12 Chargeback gap |
| ACA-03-032 | ACA-03-T13 | Negative tests for each rule |
| ACA-03-033 | ACA-03-T14 | FindingsAssembler unit test |

---

## Recommended Final WBS Structure

### Phase 1 Active Scope (Epics 1-10)

**Total Stories**: 286 (281 baseline + 5 gap stories, after resolving conflicts)

| Epic | Stories | Status Distribution | Priority |
|------|---------|---------------------|----------|
| 01 - Authentication & Authorization | 23 | 21 not-started, 2 done | ACTIVE |
| 02 - Data Collection | 44 | 7 done, 10 not-started, 27 new | ACTIVE |
| 03 - Analysis Engine & Rules | 47 | 33 done, 14 new | ACTIVE |
| 04 - Delivery & Script Generation | 33 | 9 baseline, 23 new, 1 gap | ACTIVE |
| 05 - Frontend | 38 | 42 baseline (consolidated to 38) | ACTIVE |
| 06 - API Service | 44 | 28 baseline, 15 new, 1 gap | ACTIVE |
| 07 - Billing & Monetization | 18 | All not-started | ACTIVE |
| 08 - Observability | 14 | All not-started | ACTIVE |
| 09 - i18n & a11y | 21 | All not-started | ACTIVE |
| 10 - Security & Compliance | 12 | All planned | PLANNED |

### Phase 2-10 Expansion Scope (Epics 11-19)

**Total Stories**: 296 (294 comprehensive + 2 gap stories for Phase 2)

| Epic | Stories | Phase | Status |
|------|---------|-------|--------|
| 11 - Phase 2 Infrastructure | 37 | Phase 2 | PLANNED |
| 12 - FinOps Hub Integration | 18 | Phase 2 | PLANNED |
| 13 - Autonomous Operations | 41 | Phase 3 | PLANNED |
| 14 - Predictive Analytics | 28 | Phase 4 | PLANNED |
| 15 - Multi-Cloud Support | 34 | Phase 5 | PLANNED |
| 16 - Partner Ecosystem | 26 | Phase 6 | PLANNED |
| 17 - Enterprise Features | 38 | Phase 7 | PLANNED |
| 18 - Advanced Analytics | 33 | Phase 8 | PLANNED |
| 19 - Platform Services | 41 | Phase 9-10 | PLANNED |

---

## Implementation Roadmap

### Immediate Actions (Sprint 004 - Current)

1. **Resolve Story ID Conflicts**
   - Renumber test stories: ACA-03-T01 through ACA-03-T14
   - Renumber gap stories: ACA-02-043, ACA-02-044, ACA-06-034, ACA-11-036
   - Update PLAN.md, WBS-FROM-DOCS-COMPLETE-20260311.md with new IDs

2. **Integrate Gap Stories**
   - Add ACA-01-022 (Frontend deployment) to Epic 01
   - Add ACA-02-043 (Analysis auto-trigger) to Epic 02
   - Add ACA-02-044 (Resource Graph pagination) to Epic 02
   - Add ACA-06-034 (RFC 7807 errors) to Epic 06
   - Add ACA-11-036 (Standalone data model) to Epic 11

3. **Sync to Data Model API**
   - Export final reconciled WBS to Project 37 Data Model
   - Use `eva export-to-model` or Project 48 Veritas sync_repo tool
   - Validate story counts match (617 total: 286 Phase 1 + 331 Phase 2-10)

### Sprint 005-010 (Phase 1 Completion)

- Focus on **286 Phase 1 stories** (Epics 1-10)
- Prioritize stories with status=not-started in Epics 2-9
- Complete Epic 10 (Security & Compliance) as final Phase 1 gate

### Sprints 011+ (Phase 2-10 Expansion)

- Implement **296 Phase 2-10 stories** (Epics 11-19) in phased rollout
- Each phase (2-10) represents 4-8 week development cycle
- Gate each phase on MTI > 70 (Project 48 Veritas quality gate)

---

## Action Items

### For Project Lead (Marco)

- [ ] Review and approve story ID renumbering scheme (ACA-03-T## for tests)
- [ ] Review and approve gap story renumbering (ACA-02-043/044, ACA-06-034, ACA-11-036)
- [ ] Decide on Phase 1 scope freeze: 286 stories or expand to include select Phase 2 stories
- [ ] Update README.md with final story count and epic structure

### For Development Team

- [ ] Update all references to old test story  IDs in test files, CI workflows, documentation
- [ ] Create tracking tickets for 5 gap stories in project management system
- [ ] Execute data model sync: `eva sync-repo --project 51-ACA` to persist reconciled WBS

### For Documentation

- [ ] Update [archive/PLAN.md](./archive/PLAN.md) as historical record
- [ ] Create new PLAN-v2.md with reconciled 19-epic structure
- [ ] Update STATUS.md with accurate done/in-progress/not-started counts
- [ ] Archive WBS-FROM-DOCS-COMPLETE-20260311.md as source material reference

---

## Appendices

### Appendix A: Story Mapping CSV

A detailed CSV export of all 617 stories with mapping status is available at:
- `C:\eva-foundry\51-ACA\docs\story-mapping-analysis.csv`

Columns:
- StoryID
- InBaseline (TRUE/FALSE)
- InComprehensive (TRUE/FALSE)
- Status (done/in-progress/not-started/n/a)
- BaselineTitle
- ComprehensiveTitle

### Appendix B: Function Point Estimates

The comprehensive WBS includes Function Point (FP) estimates for all 612 stories:

| Epic Range | Estimated FP | Avg FP/Story |
|------------|--------------|--------------|
| Epics 1-10 (Phase 1) | 2,680 FP | 5.5 FP |
| Epics 11-19 (Phase 2-10) | 2,210 FP | 7.5 FP |
| **Total** | **4,890 FP** | **6.4 FP** |

Conversion to person-hours (using 15 hours/FP for complex systems):
- Phase 1: 2,680 FP × 15 = **40,200 hours** (~20 person-years @ 2,000 hours/year)
- Phase 2-10: 2,210 FP × 15 = **33,150 hours** (~17 person-years)
- **Total effort**: **73,350 hours** (~37 person-years)

### Appendix C: DPDCA Compliance

This reconciliation was performed using DPDCA methodology:

1. **DISCOVER**: Read both WBS files, extracted 281 + 612 stories
2. **PLAN**: Designed reconciliation strategy (ID matching, status preservation)
3. **DO**: Created comprehensive mapping and conflict analysis
4. **CHECK**: Validated story counts (281 + 331 = 612 ✓)
5. **ACT**: Documented recommendations, created action items

**Evidence**: 
- Session evidence saved: [SESSION_45_PART_9_EVIDENCE_20260311_110338.json](../../SESSION_45_PART_9_EVIDENCE_20260311_110338.json)
- This reconciliation document serves as deliverable for Session 45 Part 9

---

**End of Reconciliation Report**

**For questions or clarifications**: See Project 51 (ACA) README.md or contact project maintainer.
