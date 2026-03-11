<#
.SYNOPSIS
    Create GitHub issues for cloud agent execution of 8-week build plan

.DESCRIPTION
    Session 45+ - Autonomous generation via GitHub Copilot cloud agents
    
    Creates GitHub issues for automatable work from 8-WEEK-BUILD-PLAN-20260311.md v2.0
    Each issue contains complete sprint manifest (machine-readable) for autonomous execution:
    - Story IDs with acceptance criteria
    - Files to create/modify
    - Implementation patterns and references
    - Quality gates (pytest, ruff, mypy, axe-core)
    
    Issues are labeled "sprint-task" to trigger .github/workflows/sprint-agent.yml
    Assigned to: @copilot
    
    Based on CLOUD-AGENT-AUTOMATION-ANALYSIS.md findings:
    - 108 automatable stories (~425 FP)
    - 16 cloud agent issues (or 9 high-priority batches for Weeks 1-5)
    - 62% of implementation work automatable

.PARAMETER DryRun
    Preview issues without creating them

.PARAMETER Batch
    Create specific batch only (1-9 for high-priority, 1-16 for all)

.PARAMETER Priority
    Create only high-priority batches (1-9, Weeks 1-5, ~265 FP)

.PARAMETER RepoOwner
    GitHub repository owner (default: eva-foundry or MarcoPresta)

.PARAMETER RepoName
    GitHub repository name (default: 51-ACA)

.EXAMPLE
    .\create-cloud-agent-issues-8week.ps1 -DryRun
    # Preview all 16 issues

.EXAMPLE
    .\create-cloud-agent-issues-8week.ps1 -Batch 1
    # Create Batch 1 only (Analysis Rules Completion)

.EXAMPLE
    .\create-cloud-agent-issues-8week.ps1 -Priority
    # Create batches 1-9 (high-priority, Weeks 1-5)

.EXAMPLE
    .\create-cloud-agent-issues-8week.ps1 -RepoOwner "MarcoPresta" -RepoName "51-ACA"
    # Create all issues for specific repo
#>

param(
    [switch]$DryRun,
    [int]$Batch = 0,
    [switch]$Priority,
    [string]$RepoOwner = "eva-foundry",
    [string]$RepoName = "51-ACA"
)

$ErrorActionPreference = "Stop"

# Setup logging (professional standard: dual logging)
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$logsDir = Join-Path $rootDir "logs"
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }
$logFile = Join-Path $logsDir "cloud-agent-issues-8week_$timestamp.log"

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",  # INFO, PASS, FAIL, ERROR
        [switch]$ConsoleOnly
    )
    
    $logLine = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    
    # Console output (ASCII-only)
    Write-Host $logLine
    
    # File output (unless ConsoleOnly)
    if (-not $ConsoleOnly) {
        $logLine | Out-File -FilePath $logFile -Append -Encoding ASCII
    }
}

Write-Log "[INFO] Cloud Agent Issue Creation Script v1.0.0"
Write-Log "[INFO] Log file: $logFile"
Write-Log "[INFO] Mode: $(if ($DryRun) { 'DRY-RUN' } else { 'LIVE' })"

# Pre-flight checks
Write-Log "[INFO] Running pre-flight checks..."

# Check GitHub CLI
try {
    $ghVersion = gh --version 2>&1 | Select-String "gh version" | Out-String
    Write-Log "[PASS] GitHub CLI installed: $($ghVersion.Trim())"
} catch {
    Write-Log "[FAIL] GitHub CLI not found. Install from: https://cli.github.com/" "ERROR"
    exit 2
}

# Check GitHub auth
try {
    $ghUser = gh auth status 2>&1 | Select-String "Logged in" | Out-String
    Write-Log "[PASS] GitHub CLI authenticated: $($ghUser.Trim())"
} catch {
    Write-Log "[FAIL] GitHub CLI not authenticated. Run: gh auth login" "ERROR"
    exit 2
}

# Check repo exists
try {
    $repoCheck = gh repo view "$RepoOwner/$RepoName" --json name 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "[PASS] Repository $RepoOwner/$RepoName accessible"
    } else {
        throw "Repository not found"
    }
} catch {
    Write-Log "[FAIL] Repository $RepoOwner/$RepoName not accessible" "ERROR"
    exit 2
}

Write-Log "[PASS] All pre-flight checks passed"

# Define batches (9 high-priority + 7 medium-priority)
$batches = @(
    @{
        Id = 1
        Title = "[SPRINT-004-BATCH-1] Analysis Rules Completion (R-09 to R-12)"
        Week = 1
        Stories = @("ACA-03-019", "ACA-03-020", "ACA-03-021", "ACA-03-022")
        FP = 10
        Epic = "ACA-03"
        Priority = "HIGH"
        Description = @"
## Overview
Complete remaining 4 analysis rules (R-09 DNS Sprawl, R-10 Savings Plan, R-11 APIM Token Budget, R-12 Chargeback Gap)
Pattern: Follow existing R-01 through R-08 implementations
Location: services/analysis/app/rules/
Tests: services/analysis/tests/

## Story 1: ACA-03-019 -- R-09 DNS Sprawl Detection

**Feature**: 3.3 Analysis Rules -- DNS Sprawl (R-09)
**Acceptance**:
- [ ] services/analysis/app/rules/r09_dns_sprawl.py exists
- [ ] Rule detects when annual DNS cost > `$1,000`
- [ ] Finding includes: dns_zone_count, annual_dns_cost, finding_type=cost_optimization
- [ ] effort_class=easy (consolidate DNS zones)
- [ ] Tests in services/analysis/tests/test_r09_dns_sprawl.py pass (positive, negative, edge cases)

**Implementation**:
- Read existing rule pattern from r01_devbox_autostop.py
- Query cost-data container for DNS service costs
- Aggregate annual DNS spend: SUM(cost WHERE service='Microsoft.Network/dnszones')
- If > 1000, create finding with saving estimate (assume 30% consolidation savings)

**Pattern Reference**: r01_devbox_autostop.py (threshold check + evidence_refs)

---

## Story 2: ACA-03-020 -- R-10 Savings Plan Coverage

**Feature**: 3.3 Analysis Rules -- Savings Plan (R-10)
**Acceptance**:
- [ ] services/analysis/app/rules/r10_savings_plan.py exists
- [ ] Rule detects when total compute cost > `$20,000` annually
- [ ] Finding suggests Savings Plan commitment (1-year or 3-year)
- [ ] Saving estimate: 15-30% of compute spend
- [ ] effort_class=involved (requires procurement approval)
- [ ] Tests pass

**Implementation**:
- Query cost-data for compute services: VM, AKS, App Service, Functions, Container Apps
- Aggregate annual compute spend
- If > 20000, create finding with 20% savings estimate (mid-range)
- Include link to Azure Savings Plan calculator

**Pattern Reference**: 14-az-finops/cost-optimization.md savings plan section

---

## Story 3: ACA-03-021 -- R-11 APIM Token Budget

**Feature**: 3.3 Analysis Rules -- APIM Token Budget (R-11)
**Acceptance**:
- [ ] services/analysis/app/rules/r11_apim_token_budget.py exists
- [ ] Rule detects when APIM + Azure OpenAI both present
- [ ] risk_class=high (token budget control missing)
- [ ] saving_range_low=0, saving_range_high=0 (risk-only, no saving)
- [ ] effort_class=medium (implement token budget policy)
- [ ] Tests pass

**Implementation**:
- Query inventories container for APIM instances (Microsoft.ApiManagement/service)
- Query inventories for OpenAI deployments (Microsoft.CognitiveServices/openAI)
- If BOTH exist, create risk-only finding (no dollar saving)
- Narrative: "APIM + OpenAI without token budget policy creates runaway cost risk"

**Pattern Reference**: r03_defender_mismatch.py (risk-only finding)

---

## Story 4: ACA-03-022 -- R-12 Chargeback Gap

**Feature**: 3.3 Analysis Rules -- Chargeback Gap (R-12)
**Acceptance**:
- [ ] services/analysis/app/rules/r12_chargeback_gap.py exists
- [ ] Rule detects when period cost > `$5,000` AND tagging compliance < 80%
- [ ] Suggests chargeback tagging strategy (cost-center, project, owner tags)
- [ ] effort_class=strategic (FinOps organizational change)
- [ ] Tests pass

**Implementation**:
- Query cost-data for period total cost
- Query inventories for tag compliance (resources with cost-center/project/owner tags)
- If cost > 5000 AND tagging < 80%, create finding
- Saving estimate: 0 (strategic benefit, not dollar savings)

**Pattern Reference**: 14-az-finops/tagging.md chargeback patterns

---

## Quality Gates

**Before PR**:
- [ ] All 4 rule modules exist and import without error
- [ ] ruff lint: 0 errors
- [ ] mypy: 0 unresolved types
- [ ] pytest passes: 4 rule tests + negative tests
- [ ] Coverage >= 95% for new code

**Evidence Receipt**:
- duration_ms
- tokens_used (if LLM calls)
- files_changed: 4 rules + 4 tests = 8 files
- test_count_before/after

---

## Files to Create

**Rules** (services/analysis/app/rules/):
1. r09_dns_sprawl.py
2. r10_savings_plan.py
3. r11_apim_token_budget.py
4. r12_chargeback_gap.py

**Tests** (services/analysis/tests/):
1. test_r09_dns_sprawl.py
2. test_r10_savings_plan.py
3. test_r11_apim_token_budget.py
4. test_r12_chargeback_gap.py

---

**Target Branch**: `sprint/004-analysis-completion`
**Est. Cloud Execution**: ~45 minutes
**Next Sprint**: Batch 2 (Core API Endpoints)
"@
    }
    @{
        Id = 2
        Title = "[SPRINT-005-BATCH-2] Core API Endpoints (Routes 11-16)"
        Week = 2
        Stories = @("ACA-04-011", "ACA-04-012", "ACA-04-013", "ACA-04-014", "ACA-04-015", "ACA-04-016")
        FP = 20
        Epic = "ACA-04"
        Priority = "HIGH"
        Description = @"
## Overview
Implement 6 core API endpoints: collect trigger/status, reports (tier1), Stripe checkout/portal, webhooks
Pattern: Existing routers in services/api/app/routers/
Location: services/api/app/routers/collect.py, reports.py, billing.py, webhooks.py

## Story 1: ACA-04-011 -- POST /v1/collect/start

**Acceptance**:
- [ ] POST /v1/collect/start endpoint exists
- [ ] Triggers collector job via Azure Container Apps Jobs API
- [ ] Returns 202 Accepted with job_id
- [ ] Graceful degradation if ACA_ANALYSIS_JOB_NAME env var not set (returns 503)
- [ ] Test with mock Container Apps client

**Implementation**:
- services/api/app/routers/collect.py (NEW or EXTEND)
- Use azure.mgmt.containerinstance (or azure.mgmt.appcontainers if available)
- Read settings.ACA_COLLECTOR_JOB_NAME
- Call start_job() with subscription_id in environment
- Return {"job_id": "...", "status": "queued"}

---

## Story 2: ACA-04-012 -- GET /v1/collect/status

**Acceptance**:
- [ ] GET /v1/collect/status endpoint exists
- [ ] Queries Cosmos scans container by subscriptionId
- [ ] Returns scan status: queued/running/succeeded/failed
- [ ] Includes metrics: inventoryCount, costRows, collectionDurationMs
- [ ] Test with mock Cosmos data

**Implementation**:
- services/api/app/routers/collect.py
- Query scans container with partition_key=subscriptionId
- Order by scan_started_at DESC, limit 1
- Return ScanStatusResponse DTO

---

## Story 3: ACA-04-013 -- GET /v1/reports/tier1

**Acceptance**:
- [ ] GET /v1/reports/tier1 endpoint exists
- [ ] Tier-gated: returns findings with title + saving_range only
- [ ] Excludes: narrative, deliverable_template_id, evidence_refs
- [ ] Test with tier1 mock entitlement

**Implementation**:
- services/api/app/routers/reports.py (NEW)
- Call existing gate_findings() from services/analysis/app/tier_gating.py
- Return Tier1FindingsResponse (list of FindingTier1DTO)

---

## Story 4: ACA-04-014 -- POST /v1/billing/checkout

**Acceptance**:
- [ ] POST /v1/billing/checkout endpoint exists
- [ ] Creates Stripe checkout session for tier2 or tier3
- [ ] Returns checkout URL
- [ ] Webhook processes stripe.checkout.session.completed event
- [ ] Test with Stripe test mode

**Implementation**:
- services/api/app/routers/billing.py (MODIFY if exists, or CREATE)
- Unify tier2/tier3 into single endpoint with tier in request body
- Use stripe.checkout.Session.create()
- success_url, cancel_url, subscription metadata

---

## Story 5: ACA-04-015 -- GET /v1/billing/portal

**Acceptance**:
- [ ] GET /v1/billing/portal endpoint exists
- [ ] Creates Stripe billing portal session
- [ ] Returns redirect URL for authenticated customer
- [ ] Test with Stripe test customer

**Implementation**:
- services/api/app/routers/billing.py
- stripe.billing_portal.Session.create(customer=stripe_customer_id)
- Return {"portal_url": "..."}

---

## Story 6: ACA-04-016 -- POST /v1/webhooks/stripe

**Acceptance**:
- [ ] POST /v1/webhooks/stripe endpoint exists (verify if already done in Epic 6)
- [ ] Signature validation (Stripe-Signature header + whsec_ secret)
- [ ] Handles checkout.session.completed, customer.subscription.updated, customer.subscription.deleted
- [ ] Idempotent processing (dedupe by stripe event_id)
- [ ] Test with Stripe webhook test events

**Implementation**:
- services/api/app/routers/webhooks.py
- If duplicate with Epic 6 implementation (ACA-06-021), verify single handler exists
- stripe.Webhook.construct_event() for signature validation
- Write to Cosmos entitlements container on subscription events

---

## Quality Gates

**Before PR**:
- [ ] All 6 endpoints respond 200/202 (or appropriate status)
- [ ] ruff lint: 0 errors
- [ ] mypy: 0 unresolved types
- [ ] pytest passes (mock Cosmos, mock Azure, mock Stripe)
- [ ] Coverage >= 95%

---

## Files to Create/Modify

1. services/api/app/routers/collect.py (NEW or EXTEND)
2. services/api/app/routers/reports.py (NEW)
3. services/api/app/routers/billing.py (MODIFY or CREATE)
4. services/api/app/routers/webhooks.py (VERIFY or MODIFY)
5. services/api/tests/test_collect.py (NEW)
6. services/api/tests/test_reports.py (NEW)
7. services/api/tests/test_billing.py (MODIFY)
8. services/api/tests/test_webhooks.py (MODIFY)

**Target Branch**: `sprint/005-api-core`
**Est. Cloud Execution**: ~60 minutes
"@
    }
    @{
        Id = 3
        Title = "[SPRINT-005-BATCH-3] Admin API (6 Endpoints)"
        Week = 2
        Stories = @("ACA-04-022", "ACA-04-023", "ACA-04-024", "ACA-04-025", "ACA-04-026", "ACA-04-027")
        FP = 25
        Epic = "ACA-04"
        Priority = "HIGH"
        Description = @"
## Overview
Implement admin API surface: KPIs, customer search, entitlement grant, subscription lock, Stripe reconcile, runs list
Pattern: Admin audit events logging (admin_audit_events container)
RBAC: ACA_Admin, ACA_Support, ACA_FinOps roles
Location: services/api/app/routers/admin.py

## Story 1: ACA-04-022 -- GET /v1/admin/kpis

**Acceptance**:
- [ ] GET /v1/admin/kpis endpoint exists
- [ ] Requires role: ACA_Admin OR ACA_Support OR ACA_FinOps
- [ ] Returns: mrrCad, activeSubscriptions, scansLast24h, failureRate
- [ ] Aggregates from Cosmos containers: scans, clients, payments
- [ ] Test with mock admin token

**Implementation**:
- services/api/app/routers/admin.py (NEW)
- Requires RBAC decorator: @require_role(["ACA_Admin", "ACA_Support", "ACA_FinOps"])
- Query scans container for last 24h count
- Query clients container for active subscriptions
- Query payments container for MRR calculation
- Return AdminKpisResponse DTO

---

## Story 2: ACA-04-023 -- GET /v1/admin/customers?query=

**Acceptance**:
- [ ] GET /v1/admin/customers endpoint exists
- [ ] Search by subscriptionId or stripeCustomerId
- [ ] Returns list of AdminCustomerRow (tier, paymentStatus, isLocked, lastScanAt)
- [ ] Test with query parameter

**Implementation**:
- services/api/app/routers/admin.py
- Query clients container with search filter
- Return list of AdminCustomerRow DTOs

---

## Story 3: ACA-04-024 -- POST /v1/admin/entitlements/grant

**Acceptance**:
- [ ] POST /v1/admin/entitlements/grant endpoint exists
- [ ] Requires role: ACA_Admin OR ACA_Support
- [ ] Grants tier to subscription (manual override)
- [ ] Writes admin_audit_events record (who, what, when, why)
- [ ] Test: verify audit event created

**Implementation**:
- services/api/app/routers/admin.py
- Request body: {subscriptionId, tier, reason}
- Write to entitlements container
- Write audit event: {actor, action="grant_entitlement", subject=subscriptionId, reason, timestamp}

---

## Story 4: ACA-04-025 -- POST /v1/admin/subscriptions/:id/lock

**Acceptance**:
- [ ] POST /v1/admin/subscriptions/:id/lock endpoint exists
- [ ] Marks subscription locked in clients container (isLocked=true)
- [ ] Writes admin_audit_events record
- [ ] Locked subscriptions: API returns 403 on all requests

**Implementation**:
- services/api/app/routers/admin.py
- Update clients container: set isLocked=true
- Write audit event

---

## Story 5: ACA-04-026 -- POST /v1/admin/stripe/reconcile

**Acceptance**:
- [ ] POST /v1/admin/stripe/reconcile endpoint exists
- [ ] Requires role: ACA_Admin (strictest)
- [ ] Enqueues Stripe reconciliation job
- [ ] Returns jobId
- [ ] Test: verify job creation (mock)

**Implementation**:
- services/api/app/routers/admin.py
- Call Azure Container Apps Jobs API to start reconciliation job
- Return {"job_id": "..."}

---

## Story 6: ACA-04-027 -- GET /v1/admin/runs?type=scan|analysis|delivery

**Acceptance**:
- [ ] GET /v1/admin/runs endpoint exists
- [ ] Filters by run type (scan, analysis, delivery)
- [ ] Filters by subscriptionId (optional)
- [ ] Pagination: limit=50, offset=0
- [ ] Test with query parameters

**Implementation**:
- services/api/app/routers/admin.py
- Query scans/analysis/delivery containers based on type filter
- Return list of AdminRunRow DTOs (runId, subscriptionId, status, startedAt, durationMs)

---

## Quality Gates

**Before PR**:
- [ ] All 6 admin endpoints respond
- [ ] RBAC: endpoints reject requests without required role (403)
- [ ] Admin audit events: all write operations log to admin_audit_events container
- [ ] ruff lint: 0 errors
- [ ] mypy: 0 unresolved types
- [ ] pytest passes (mock RBAC, mock Cosmos)
- [ ] Coverage >= 95%

---

## Files to Create/Modify

1. services/api/app/routers/admin.py (NEW)
2. services/api/app/middleware/rbac.py (NEW -- require_role decorator)
3. services/api/app/models/admin.py (NEW -- AdminCustomerRow, AdminKpisResponse, AdminRunRow DTOs)
4. services/api/tests/test_admin.py (NEW)

**Target Branch**: `sprint/005-admin-api`
**Est. Cloud Execution**: ~75 minutes
"@
    }
    @{
        Id = 4
        Title = "[SPRINT-005-BATCH-4a] Rule Unit Tests (R-01 to R-06)"
        Week = 2
        Stories = @("ACA-03-020", "ACA-03-021", "ACA-03-022", "ACA-03-023", "ACA-03-024", "ACA-03-025")
        FP = 12
        Epic = "ACA-03"
        Priority = "HIGH"
        Description = @"
## Overview
Unit tests for analysis rules R-01 through R-06
Pattern: Existing test structure (fixtures, positive/negative, edge cases)
Target: >= 95% coverage per rule module
Location: services/analysis/tests/

## Stories (6 test files)

### ACA-03-020: test_r01_devbox_autostop.py
- Positive: VM annual cost > 5000 → finding created
- Negative: VM annual cost < 5000 → no finding
- Edge: VM with no cost data → no finding

### ACA-03-021: test_r02_log_retention.py
- Positive: Log retention > 30 days → finding created
- Negative: Log retention <= 30 days → no finding
- Edge: No Log Analytics workspace → no finding

### ACA-03-022: test_r03_defender_mismatch.py
- Positive: Defender disabled + production tag → finding (risk-only)
- Negative: Defender enabled → no finding
- Edge: No production tag → no finding

### ACA-03-023: test_r04_compute_scheduling.py
- Positive: VM running 24/7 + dev environment → finding
- Negative: VM with auto-shutdown scheduled → no finding
- Edge: Production VM → no finding (always-on expected)

### ACA-03-024: test_r05_anomaly_detection.py
- Positive: Cost spike > 50% month-over-month → finding
- Negative: Cost increase < 50% → no finding
- Edge: First month data (no prior month) → no finding

### ACA-03-025: test_r06_stale_environments.py
- Positive: Resource group last modified > 90 days ago → finding
- Negative: Resource group modified within 90 days → no finding
- Edge: Resource group with no activity log → no finding

---

## Quality Gates

**Before PR**:
- [ ] All 6 test files exist and pass
- [ ] pytest --cov shows >= 95% coverage for R-01 through R-06 modules
- [ ] Fixtures: mock cost-data, mock inventories, mock advisor
- [ ] Each test file: 5+ test cases (positive, negative, edge)
- [ ] ruff lint: 0 errors
- [ ] mypy: 0 unresolved types

---

## Files to Create

services/analysis/tests/:
1. test_r01_devbox_autostop.py
2. test_r02_log_retention.py
3. test_r03_defender_mismatch.py
4. test_r04_compute_scheduling.py
5. test_r05_anomaly_detection.py
6. test_r06_stale_environments.py

**Target Branch**: `sprint/005-rule-tests-batch-1`
**Est. Cloud Execution**: ~45 minutes
**Next**: Batch 4b (R-07 to R-12 tests)
"@
    }
    @{
        Id = 5
        Title = "[SPRINT-005-BATCH-4b] Rule Unit Tests (R-07 to R-12)"
        Week = 2
        Stories = @("ACA-03-026", "ACA-03-027", "ACA-03-028", "ACA-03-029", "ACA-03-030", "ACA-03-031")
        FP = 13
        Epic = "ACA-03"
        Priority = "HIGH"
        Description = @"
## Overview
Unit tests for analysis rules R-07 through R-12
Continues from Batch 4a
Target: >= 95% coverage per rule module

## Stories (6 test files)

### ACA-03-026: test_r07_search_sku_oversize.py
- Positive: Search SKU = Standard + query volume < 1M/month → finding
- Negative: Search SKU = Basic → no finding
- Edge: No search service → no finding

### ACA-03-027: test_r08_acr_consolidation.py
- Positive: 3+ ACR instances in same region → finding
- Negative: 1 ACR instance → no finding
- Edge: ACRs in different regions → no finding

### ACA-03-028: test_r09_dns_sprawl.py
- Positive: Annual DNS cost > 1000 → finding
- Negative: Annual DNS cost < 1000 → no finding
- Edge: No DNS zones → no finding

### ACA-03-029: test_r10_savings_plan.py
- Positive: Annual compute cost > 20000 → finding
- Negative: Annual compute cost < 20000 → no finding
- Edge: No compute resources → no finding

### ACA-03-030: test_r11_apim_token_budget.py
- Positive: APIM + OpenAI both present → risk finding
- Negative: Only APIM (no OpenAI) → no finding
- Edge: Only OpenAI (no APIM) → no finding

### ACA-03-031: test_r12_chargeback_gap.py
- Positive: Cost > 5000 + tagging < 80% → finding
- Negative: Cost < 5000 → no finding
- Edge: Cost > 5000 + tagging > 80% → no finding

---

## Quality Gates

**Before PR**:
- [ ] All 6 test files exist and pass
- [ ] pytest --cov shows >= 95% coverage for R-07 through R-12 modules
- [ ] Fixtures: mock cost-data, mock inventories
- [ ] Each test file: 5+ test cases
- [ ] Total rule test coverage: R-01 through R-12 all >= 95%
- [ ] ruff lint: 0 errors
- [ ] mypy: 0 unresolved types

---

## Files to Create

services/analysis/tests/:
1. test_r07_search_sku_oversize.py
2. test_r08_acr_consolidation.py
3. test_r09_dns_sprawl.py
4. test_r10_savings_plan.py
5. test_r11_apim_token_budget.py
6. test_r12_chargeback_gap.py

**Target Branch**: `sprint/005-rule-tests-batch-2`
**Est. Cloud Execution**: ~45 minutes
"@
    }
    @{
        Id = 6
        Title = "[SPRINT-006-BATCH-5] Frontend Auth Layer + Router"
        Week = 3
        Stories = @("ACA-05-001", "ACA-05-002", "ACA-05-003", "ACA-05-004", "ACA-05-005", "ACA-05-011", "ACA-05-012", "ACA-05-013", "ACA-05-014", "ACA-05-015")
        FP = 20
        Epic = "ACA-05"
        Priority = "HIGH"
        Description = @"
## Overview
Frontend authentication layer + React Router v6 setup
Pattern: React 19 + MSAL.js + React Router v6 with lazy loading
Location: frontend/src/

## Auth Layer Stories (ACA-05-001..005)

### ACA-05-001: roles.ts
- Define role constants: ACA_Admin, ACA_Support, ACA_FinOps
- Export as const enum or string constants

### ACA-05-002: useAuth.ts
- MSAL React hook wrapper
- DEV bypass mode: if VITE_DEV_AUTH=true, return mock user
- authority: https://login.microsoftonline.com/common

### ACA-05-003: RequireAuth.tsx
- Guard component: redirect to / if not authenticated
- Checks useAuth().isAuthenticated

### ACA-05-004: RequireRole.tsx
- Guard component: redirect to /app/connect if missing required role
- Checks useAuth().roles

### ACA-05-005: Admin route guards
- All /admin/* routes wrapped in RequireAuth + RequireRole

---

## Router Stories (ACA-05-011..015)

### ACA-05-011: router.tsx
- createBrowserRouter (not BrowserRouter)
- All routes defined in single object

### ACA-05-012: Route /
- LoginPage (no auth guard)

### ACA-05-013: Routes /app/*
- RequireAuth → CustomerLayout → Outlet
- Pages: /app/connect, /app/status, /app/findings, /app/upgrade

### ACA-05-014: Routes /admin/*
- RequireAuth → RequireRole(["ACA_Admin", "ACA_Support", "ACA_FinOps"]) → AdminLayout → Outlet
- Pages: /admin/dashboard, /admin/customers, /admin/billing, /admin/runs, /admin/controls

### ACA-05-015: Lazy loading
- All page components lazy-loaded with React.lazy
- Suspense with Loading component fallback

---

## Quality Gates

**Before PR**:
- [ ] All auth/router files exist and compile
- [ ] DEV bypass works (VITE_DEV_AUTH=true → mock authenticated user)
- [ ] Route guards: unauthenticated → redirect to /
- [ ] Role guards: missing role → redirect to /app/connect
- [ ] ruff lint: 0 errors (TypeScript equivalent)
- [ ] npm run build succeeds

---

## Files to Create

frontend/src/:
1. auth/roles.ts
2. auth/useAuth.ts
3. auth/RequireAuth.tsx
4. auth/RequireRole.tsx
5. router.tsx
6. pages/LoginPage.tsx (stub)
7. pages/app/ConnectSubscriptionPage.tsx (stub)
8. pages/admin/AdminDashboardPage.tsx (stub)
9. components/Loading.tsx

**Target Branch**: `sprint/006-auth-router`
**Est. Cloud Execution**: ~60 minutes
"@
    }
    @{
        Id = 7
        Title = "[SPRINT-006-BATCH-6] Frontend Layouts"
        Week = 3
        Stories = @("ACA-05-006", "ACA-05-007", "ACA-05-008", "ACA-05-009", "ACA-05-010")
        FP = 15
        Epic = "ACA-05"
        Priority = "HIGH"
        Description = @"
## Overview
Fluent UI v9 layout components: CustomerLayout, AdminLayout, Navigation, AppShell
Pattern: Existing Fluent UI patterns from P31 (eva-faces)
Location: frontend/src/layouts/

## Story 1: ACA-05-006 -- CustomerLayout.tsx

**Acceptance**:
- [ ] CustomerLayout component exists
- [ ] Top nav: logo, NavCustomer, LanguageSelector, user menu
- [ ] Fluent UI v9 tokens and makeStyles
- [ ] Outlet for nested routes
- [ ] Responsive design (mobile + desktop)

**Implementation**:
- Use @fluentui/react-components v9
- Top nav with makeStyles
- Outlet from react-router-dom

---

## Story 2: ACA-05-007 -- AdminLayout.tsx

**Acceptance**:
- [ ] AdminLayout component exists
- [ ] Top nav + left sidebar
- [ ] Left sidebar: NavAdmin
- [ ] Outlet for nested routes
- [ ] Collapsed sidebar on mobile

**Implementation**:
- Fluent UI v9 NavigationRail or custom sidebar
- Top nav with user menu
- Sidebar width: 240px desktop, collapsed mobile

---

## Story 3: ACA-05-008 -- NavCustomer.tsx

**Acceptance**:
- [ ] NavCustomer component exists
- [ ] Links: /app/connect, /app/status, /app/findings
- [ ] Active link styling
- [ ] Accessible (aria-current="page")

**Implementation**:
- Use Link from react-router-dom
- useLocation() to detect active route

---

## Story 4: ACA-05-009 -- NavAdmin.tsx

**Acceptance**:
- [ ] NavAdmin component exists
- [ ] Links: /admin/dashboard, /admin/customers, /admin/billing, /admin/runs, /admin/controls
- [ ] Active link styling
- [ ] Icons from Fluent UI v9

**Implementation**:
- NavigationRailItem or TabList
- Icons: DashboardIcon, PersonIcon, MoneyIcon, etc.

---

## Story 5: ACA-05-010 -- AppShell.tsx

**Acceptance**:
- [ ] AppShell component wraps entire app
- [ ] FluentProvider with webLightTheme
- [ ] ConsentBanner component (stub for now)
- [ ] RouterProvider with router from router.tsx

**Implementation**:
- FluentProvider setup
- ConsentBanner placeholder
- RouterProvider integration

---

## Quality Gates

**Before PR**:
- [ ] All layout components render without error
- [ ] Navigation links work (no 404s)
- [ ] Active link styling correct
- [ ] Responsive: mobile sidebar collapses
- [ ] Fluent UI v9 tokens applied
- [ ] npm run build succeeds

---

## Files to Create

frontend/src/layouts/:
1. CustomerLayout.tsx
2. AdminLayout.tsx
3. NavCustomer.tsx
4. NavAdmin.tsx
5. AppShell.tsx
6. components/ConsentBanner.tsx (stub)
7. components/LanguageSelector.tsx (stub)

**Target Branch**: `sprint/006-layouts`
**Est. Cloud Execution**: ~50 minutes
"@
    }
    @{
        Id = 8
        Title = "[SPRINT-006-BATCH-7] API Client + Shared Components"
        Week = 3
        Stories = @("ACA-05-026", "ACA-05-027", "ACA-05-028", "ACA-05-029", "ACA-05-030", "ACA-05-031", "ACA-05-032", "ACA-05-033", "ACA-05-034")
        FP = 20
        Epic = "ACA-05"
        Priority = "HIGH"
        Description = @"
## Overview
TypeScript API client layer + Fluent UI shared components
Pattern: Existing frontend patterns (http client, DTOs, Fluent UI primitives)
Location: frontend/src/api/ and frontend/src/components/

## API Client Stories (ACA-05-026..029)

### ACA-05-026: client.ts
- Base http<T> function with credentials
- Error handling wrapper
- Authorization header injection

### ACA-05-027: appApi.ts
- Customer API calls: getTier1Report(), startCollection(), getCollectionStatus(), checkout()
- Uses client.ts http<T>

### ACA-05-028: adminApi.ts
- Admin API calls: getKpis(), searchCustomers(), grantEntitlement(), lockSubscription(), reconcileStripe(), getRuns()

### ACA-05-029: models.ts
- TypeScript DTOs: Tier1Report, Finding, AdminKpis, AdminCustomerRow, AdminRunRow
- Matches backend Pydantic models

---

## Shared Components (ACA-05-030..034)

### ACA-05-030: Loading.tsx
- Fluent UI Spinner with aria-label
- Centered layout

### ACA-05-031: ErrorState.tsx
- Fluent UI MessageBar (error intent)
- Retry button
- Error message display

### ACA-05-032: DataTable.tsx
- Accessible table: <th scope="col">
- Column sorting (optional)
- Pagination (optional)

### ACA-05-033: MoneyRangeBar.tsx
- Visualization: low/high saving range
- Fluent UI ProgressBar or custom SVG
- Format: CAD $X,XXX - $Y,YYY

### ACA-05-034: EffortBadge.tsx
- Badge variants: trivial, easy, medium, involved, strategic
- Fluent UI Badge or custom styled component

---

## Quality Gates

**Before PR**:
- [ ] All API client functions exist and type-check
- [ ] All shared components render without error
- [ ] TypeScript: 0 type errors
- [ ] ESLint: 0 errors
- [ ] npm run build succeeds

---

## Files to Create

frontend/src/api/:
1. client.ts
2. appApi.ts
3. adminApi.ts
4. models.ts

frontend/src/components/:
1. Loading.tsx
2. ErrorState.tsx
3. DataTable.tsx
4. MoneyRangeBar.tsx
5. EffortBadge.tsx

**Target Branch**: `sprint/006-api-client-components`
**Est. Cloud Execution**: ~60 minutes
"@
    }
    @{
        Id = 9
        Title = "[SPRINT-008-BATCH-8] IaC Template Library (12 Templates)"
        Week = 5
        Stories = @("ACA-07-001", "ACA-07-002", "ACA-07-003", "ACA-07-004")
        FP = 25
        Epic = "ACA-07"
        Priority = "HIGH"
        Description = @"
## Overview
Generate 12 Jinja2 template folders for IaC delivery (Bicep Phase 1)
Pattern: 12-IaCscript.md patterns
Location: services/delivery/app/templates/

## Story 1: ACA-07-001 -- 12 Jinja2 Template Folders

**Acceptance**:
- [ ] 12 folders exist in services/delivery/app/templates/
- [ ] Each folder has main.bicep and README.md
- [ ] Folder naming: tmpl-devbox-autostop, tmpl-log-retention-policy, etc.

**Implementation**:
Create 12 folders:
1. tmpl-devbox-autostop
2. tmpl-log-retention-policy
3. tmpl-defender-enable
4. tmpl-compute-schedule
5. tmpl-anomaly-alert
6. tmpl-cleanup-rg
7. tmpl-search-sku-downgrade
8. tmpl-acr-consolidate
9. tmpl-dns-consolidate
10. tmpl-savings-plan-commitment
11. tmpl-apim-token-budget-policy
12. tmpl-chargeback-policy

---

## Story 2: ACA-07-002 -- Template Structure

**Acceptance**:
- [ ] Each folder has main.bicep file
- [ ] main.bicep parameterized with scan_id, subscription_id, finding fields
- [ ] README.md explains template purpose

**Implementation**:
- main.bicep structure: parameters, resources, outputs
- README.md template: "# Template: [name]\n\n## Purpose\n\n## Parameters\n\n## Resources Created"

---

## Story 3: ACA-07-003 -- Template Parameterization

**Acceptance**:
- [ ] All templates accept: scan_id, subscription_id
- [ ] Finding-specific parameters extracted from findings.json manifest
- [ ] Example: tmpl-devbox-autostop accepts vm_resource_id parameter

**Implementation**:
- Bicep parameters: @description decorators
- Default values where applicable

---

## Story 4: ACA-07-004 -- Template Content from Patterns

**Acceptance**:
- [ ] Bicep content sourced from docs/12-IaCscript.md patterns
- [ ] Each template creates functional Azure resources
- [ ] Templates idempotent (multiple applies = same result)

**Implementation**:
- Read 12-IaCscript.md for each rule
- Convert to parameterized Bicep
- Example: tmpl-devbox-autostop creates Auto-Shutdown schedule resource

---

## Quality Gates

**Before PR**:
- [ ] All 12 folders exist
- [ ] All main.bicep files valid (az bicep build succeeds)
- [ ] All README.md files complete
- [ ] ruff lint: 0 errors (Python glue code if any)

---

## Files to Create

services/delivery/app/templates/:
1. tmpl-devbox-autostop/ (main.bicep, README.md)
2. tmpl-log-retention-policy/
3. tmpl-defender-enable/
4. tmpl-compute-schedule/
5. tmpl-anomaly-alert/
6. tmpl-cleanup-rg/
7. tmpl-search-sku-downgrade/
8. tmpl-acr-consolidate/
9. tmpl-dns-consolidate/
10. tmpl-savings-plan-commitment/
11. tmpl-apim-token-budget-policy/
12. tmpl-chargeback-policy/

**Target Branch**: `sprint/008-iac-templates`
**Est. Cloud Execution**: ~75 minutes
"@
    }
)

# Filter batches based on parameters
if ($Batch -gt 0) {
    $filteredBatches = [System.Collections.ArrayList]@()
    $batches | Where-Object { $_.Id -eq $Batch } | ForEach-Object { $null = $filteredBatches.Add($_) }
}
elseif ($Priority) {
    $filteredBatches = [System.Collections.ArrayList]@()
    $batches | Where-Object { $_.Priority -eq "HIGH" -and $_.Id -le 9 } | ForEach-Object { $null = $filteredBatches.Add($_) }
}
else {
    $filteredBatches = [System.Collections.ArrayList]$batches
}

Write-Log "[INFO] Batches to create: $($filteredBatches.Count)"

# Create evidence directory
$evidenceDir = Join-Path $rootDir "evidence"
if (-not (Test-Path $evidenceDir)) { New-Item -ItemType Directory -Path $evidenceDir | Out-Null }

# Create issues
$issuesCreated = 0
$issuesFailed = 0
$evidence = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    script = "create-cloud-agent-issues-8week.ps1"
    mode = if ($DryRun) { "dry-run" } else { "live" }
    batches_total = $filteredBatches.Count
    issues_created = 0
    issues_failed = 0
    issues = @()
}

foreach ($batchItem in $filteredBatches) {
    Write-Log "[INFO] Processing Batch $($batchItem.Id): $($batchItem.Title)"
    Write-Log "[INFO]   Week: $($batchItem.Week), FP: $($batchItem.FP), Stories: $($batchItem.Stories.Count), Priority: $($batchItem.Priority)"
    
    $issueBody = $batchItem.Description
    
    # Query Data Model API for story details
    $dataModelUrl = "https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io"
    $storyObjects = @()
    
    foreach ($storyId in $batchItem.Stories) {
        Write-Log "[INFO]   Querying Data Model for story: $storyId"
        
        try {
            # Query stories layer (L28) for this story
            $response = Invoke-RestMethod -Uri "$dataModelUrl/model/stories/$storyId" -Method Get -TimeoutSec 5 -ErrorAction Stop
            
            if ($response -and $response.id) {
                Write-Log "[PASS]   Found story in Data Model: $($response.title)"
                
                # Build story object from Data Model data
                $storyObj = @{
                    id = $response.id
                    title = $response.title
                    epic = $response.epic_id
                    wbs = $response.wbs_id
                }
                
                # Add optional fields if present
                if ($response.acceptance_criteria) {
                    $storyObj.acceptance = $response.acceptance_criteria
                }
                if ($response.implementation_notes) {
                    $storyObj.implementation_notes = $response.implementation_notes
                }
                if ($response.files_to_create) {
                    $storyObj.files_to_create = $response.files_to_create
                }
                if ($response.size) {
                    $storyObj.size = $response.size
                }
                
                $storyObjects += $storyObj
            }
            else {
                throw "Story not found in Data Model"
            }
        }
        catch {
            Write-Log "[WARN]   Data Model query failed for $storyId : $_" "WARN"
            Write-Log "[INFO]   Falling back to description parsing"
            
            # Fallback: Parse description to extract story title
            $pattern = "## Story \d+: $storyId\s*--\s*(.+?)[\r\n]"
            if ($issueBody -match $pattern) {
                $storyTitle = $Matches[1].Trim()
            } else {
                $storyTitle = "Story $storyId"
            }
            
            $storyObjects += @{
                id = $storyId
                title = $storyTitle
                epic = $batchItem.Epic
                wbs = "3.3"
                acceptance = @("Complete implementation as specified in issue description")
                implementation_notes = "Follow existing rule patterns. See issue description for detailed requirements."
            }
        }
    }
    
    # Add SPRINT_MANIFEST (machine-readable)
    $manifest = @{
        sprint_id = "SPRINT-$('{0:000}' -f $batchItem.Week)-BATCH-$($batchItem.Id)"
        sprint_title = $batchItem.Title
        target_branch = "sprint/$('{0:00}' -f $batchItem.Week)-batch-$($batchItem.Id)"
        epic = $batchItem.Epic
        stories = $storyObjects
        function_points = $batchItem.FP
        week = $batchItem.Week
        priority = $batchItem.Priority
    } | ConvertTo-Json -Depth 5 -Compress
    
    $issueBodyWithManifest = "<!-- SPRINT_MANIFEST`n$manifest`n-->`n`n$issueBody"
    
    if ($DryRun) {
        Write-Log "[INFO] DRY-RUN: Would create issue: $($batchItem.Title)"
        Write-Log "[INFO]   Repo: $RepoOwner/$RepoName"
        Write-Log "[INFO]   Labels: sprint-task, cloud-agent, week-$($batchItem.Week), priority-$($batchItem.Priority.ToLower())"
        Write-Log "[INFO]   Assignee: @copilot"
        Write-Log "[INFO]   Body length: $($issueBodyWithManifest.Length) chars"
    }
    else {
        try {
            # Create temp file for issue body (gh issue create doesn't accept --body for large content)
            $tempFile = New-TemporaryFile
            $issueBodyWithManifest | Out-File -FilePath $tempFile -Encoding UTF8
            
            # Create issue
            $result = gh issue create `
                --repo "$RepoOwner/$RepoName" `
                --title $batchItem.Title `
                --body-file $tempFile.FullName `
                --label "sprint-task,cloud-agent,week-$($batchItem.Week),priority-$($batchItem.Priority.ToLower())" `
                --assignee "@copilot" 2>&1
            
            Remove-Item $tempFile -Force
            
            if ($LASTEXITCODE -eq 0) {
                $issuesCreated++
                $issueUrl = $result | Select-String "https://" | Out-String | ForEach-Object { $_.Trim() }
                Write-Log "[PASS] Issue created: $issueUrl"
                
                $evidence.issues += @{
                    batch_id = $batchItem.Id
                    title = $batchItem.Title
                    week = $batchItem.Week
                    url = $issueUrl
                    status = "created"
                }
            }
            else {
                throw "gh issue create failed: $result"
            }
        }
        catch {
            $issuesFailed++
            Write-Log "[FAIL] Failed to create issue for Batch $($batchItem.Id): $_" "ERROR"
            
            $evidence.issues += @{
                batch_id = $batchItem.Id
                title = $batchItem.Title
                week = $batchItem.Week
                error = $_.ToString()
                status = "failed"
            }
        }
    }
}

$evidence.issues_created = $issuesCreated
$evidence.issues_failed = $issuesFailed

# Write evidence
$evidenceFile = Join-Path $evidenceDir "cloud-agent-issues-8week_$timestamp.json"
$evidence | ConvertTo-Json -Depth 5 | Out-File -FilePath $evidenceFile -Encoding UTF8
Write-Log "[INFO] Evidence saved: $evidenceFile"

# Summary
Write-Log "[INFO] ========================================="
Write-Log "[INFO] Cloud Agent Issue Creation Complete"
Write-Log "[INFO] ========================================="
Write-Log "[INFO] Mode: $(if ($DryRun) { 'DRY-RUN' } else { 'LIVE' })"
Write-Log "[INFO] Batches processed: $($filteredBatches.Count)"
if (-not $DryRun) {
    Write-Log "[PASS] Issues created: $issuesCreated"
    if ($issuesFailed -gt 0) {
        Write-Log "[FAIL] Issues failed: $issuesFailed" "ERROR"
    }
}
Write-Log "[INFO] Evidence: $evidenceFile"
Write-Log "[INFO] Next: Monitor GitHub Actions for cloud agent execution"

# Exit code
if ($issuesFailed -gt 0) {
    exit 1
}
exit 0
