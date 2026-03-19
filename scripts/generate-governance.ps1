# Generate Comprehensive Governance Files for Project 51-ACA
# Based on WBS Reconciliation (617 stories, 19 epics)
# Date: 2026-03-11

param(
    [string]$OutputDir = "C:\eva-foundry\51-ACA",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$reconciliationDoc = "$OutputDir\docs\WBS-RECONCILIATION-20260311.md"
$comprehensiveDoc = "$OutputDir\docs\WBS-FROM-DOCS-COMPLETE-20260311.md"

Write-Host "[INFO] Starting comprehensive governance generation..." -ForegroundColor Cyan
Write-Host "[INFO] Source: $reconciliationDoc"
Write-Host "[INFO] Source: $comprehensiveDoc"
Write-Host "[INFO] Output: $OutputDir"

# Epic metadata (from reconciliation)
$epics = @(
    @{ ID="01"; Title="Authentication & Authorization Framework"; Stories=23; FP=180; Phase=1; Status="ACTIVE" }
    @{ ID="02"; Title="Data Collection Subsystem"; Stories=42; FP=320; Phase=1; Status="ACTIVE" }
    @{ ID="03"; Title="Analysis Engine & Rules"; Stories=47; FP=380; Phase=1; Status="ACTIVE" }
    @{ ID="04"; Title="Delivery & Script Generation"; Stories=32; FP=240; Phase=1; Status="PLANNED" }
    @{ ID="05"; Title="Frontend Application (Customer & Admin)"; Stories=38; FP=280; Phase=1; Status="ACTIVE" }
    @{ ID="06"; Title="API Service (FastAPI Backend)"; Stories=43; FP=310; Phase=1; Status="ACTIVE" }
    @{ ID="07"; Title="Billing & Payment Integration"; Stories=28; FP=180; Phase=1; Status="ACTIVE" }
    @{ ID="08"; Title="Infrastructure & Deployment"; Stories=32; FP=200; Phase=1; Status="ACTIVE" }
    @{ ID="09"; Title="Analytics & Telemetry"; Stories=27; FP=90; Phase=1; Status="ACTIVE" }
    @{ ID="10"; Title="Phase 6 - Continuous Monitoring"; Stories=22; FP=220; Phase=3; Status="PLANNED" }
    @{ ID="11"; Title="Phase 7 - Enterprise Multi-Tenant Platform"; Stories=36; FP=280; Phase=4; Status="PLANNED" }
    @{ ID="12"; Title="Phase 8 - Autonomous Optimization"; Stories=35; FP=310; Phase=5; Status="PLANNED" }
    @{ ID="13"; Title="Phase 9 - Predictive & Strategic Optimization"; Stories=28; FP=260; Phase=6; Status="PLANNED" }
    @{ ID="14"; Title="Phase 10 - Ecosystem & Intelligence Platform"; Stories=34; FP=320; Phase=7; Status="PLANNED" }
    @{ ID="15"; Title="Testing & Quality Assurance"; Stories=24; FP=180; Phase="Ongoing"; Status="ACTIVE" }
    @{ ID="16"; Title="Documentation"; Stories=18; FP=120; Phase="Ongoing"; Status="ACTIVE" }
    @{ ID="17"; Title="DevOps & CI/CD"; Stories=22; FP=150; Phase="Ongoing"; Status="ACTIVE" }
    @{ ID="18"; Title="Marketing & Go-To-Market"; Stories=15; FP=100; Phase="Future"; Status="PLANNED" }
    @{ ID="19"; Title="Compliance & Governance"; Stories=17; FP=120; Phase="Ongoing"; Status="ACTIVE" }
)

$totalStories = ($epics | Measure-Object -Property Stories -Sum).Sum
$totalFP = ($epics | Measure-Object -Property FP -Sum).Sum

Write-Host "[INFO] Total Epics: $($epics.Count)"
Write-Host "[INFO] Total Stories: $totalStories"
Write-Host "[INFO] Total FP: $totalFP"

# Generate README.md
$readmeContent = @"
# ACA - Azure Cost Advisor

**Version**: 1.0.0  
**Status**: Active Development (Phase 1)  
**Last Updated**: 2026-03-11  
**Project ID**: 51-ACA  
**Total Stories**: $totalStories  
**Total Function Points**: $totalFP FP  
**EVA Foundation**: Primed ✅  

---

## Table of Contents

- [Product Vision](#product-vision)
- [Service Tiers](#service-tiers)
- [Key Differentiators](#key-differentiators)
- [Architecture Overview](#architecture-overview)
- [Epic Roadmap](#epic-roadmap)
- [Infrastructure](#infrastructure)
- [Analysis Rules](#analysis-rules)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [EVA Ecosystem Integration](#eva-ecosystem-integration)
- [Quality Gates](#quality-gates)
- [Contributing](#contributing)
- [Support](#support)

---

## Product Vision

**ACA is consulting-as-a-product.**

A client navigates to the ACA app URL, connects their Azure subscription with read-only consent, and in under five minutes receives a prioritized cost and optimization report built from 12 months of billing signals, Azure Advisor output, network topology, and policy compliance data.

They get the insight that previously required a three-day consulting engagement delivered as a self-serve SaaS in three tiers:
- **Tier 1 (Free)**: Opportunity summary with estimated savings ranges
- **Tier 2 (Advisory)**: Full narrative with effort/risk classification and beyond-cost signals
- **Tier 3 (Deliverable)**: IaC templates, PowerShell scripts, and implementation guides

**Target Buyer**: Cloud platform managers or directors responsible for development Azure subscriptions in the CAD `$300K-`$2M+ annual spend range. They know costs are high but lack time to investigate. ACA does the investigation and packages the answer in board-ready language.

---

## Service Tiers

### Tier 1 - Free Scan

| Attribute | Value |
|-----------|-------|
| **Price** | Free |
| **Access** | No payment required - sign in, connect, collect, report |
| **Scope** | Opportunity title + estimated saving range (CAD low/high) - no narrative, no IaC |
| **Purpose** | Lead generation - convert to Tier 2 or Tier 3 |

### Tier 2 - Advisory Report

| Attribute | Value |
|-----------|-------|
| **Price** | CAD `$499 one-time OR CAD `$150/month subscription |
| **Access** | Unlocked after Stripe checkout (stored in Cosmos entitlements) |
| **Scope** | Full prioritized findings with narrative, effort classification, risk rating, beyond-cost signals |
| **Delivery** | Interactive dashboard view + optional PDF export |

**Full Tier 2 Features**:
- Detailed narrative explaining each finding
- Effort classification: trivial / easy / medium / involved / strategic
- Risk rating: none / low / medium / high
- SKU right-sizing recommendations
- Network hardening opportunities
- Policy compliance gaps

### Tier 3 - Deliverable Package

| Attribute | Value |
|-----------|-------|
| **Price** | CAD `$1,499 per subscription engagement |
| **Access** | Unlocked after Stripe checkout - triggers delivery agent |
| **Scope** | Everything in Tier 2 + automated IaC/script generation |
| **Delivery** | 24-hour SAS URL to Azure Blob Storage download |

**Tier 3 Package Contents**:
- Terraform templates (Phase 2-ready) parameterized for subscription
- Bicep templates (Phase 1) for infrastructure wiring
- PowerShell/Bash automation scripts with subscription-specific values
- Implementation guide PDF with rollback instructions
- 12+ script templates for common optimization tasks

**Promise**: No manual consultant hours. Fully automated generation.

---

## Key Differentiators

### 1. Read-Only, Zero-Touch Access

ACA never modifies resources. All access is read-only through:
- Delegated consent (Microsoft Entra ID)
- Service principal (client-provided)
- Azure Lighthouse delegation (MSP-grade)

Clients can revoke at any time. All access is audited.

### 2. Consulting-Grade Output, SaaS-Grade Delivery

- **Reports**: Board language for managers and directors
- **Implementation Guides**: Practitioner language for engineering teams
- **Both**: Ship automatically from the same analysis run

### 3. Three Onboarding Modes

**Multi-Tenant Architecture**: ACA uses ``authority=https://login.microsoftonline.com/common`` - any client with a Microsoft account from any tenant can sign in.

| Mode | Description | Use Case |
|------|-------------|----------|
| **Mode A** | Delegated sign-in via Microsoft (any tenant) | Quick scan, trial-friendly |
| **Mode B** | Service principal provided by client | Enterprise governance-friendly |
| **Mode C** | Azure Lighthouse delegation | MSP-grade, multi-subscription |

**What Matters**: Delegated token has Reader + Cost Management Reader on CLIENT's subscription.

### 4. 12+ Analysis Rules from Real Production Data

All heuristics are seeded from real spending patterns in ``C:\eva-foundry\14-az-finops`` - not generic advice.

### 5. Privacy-First Telemetry

- GA4 (via GTM) and Microsoft Clarity track product events only
- No Azure identifiers, no resource names, no costs sent to analytics
- Full consent banner (GDPR/PIPEDA/LGPD-compatible)

### 6. Accessible and Multilingual by Design

- WCAG 2.1 AA accessibility from sprint 1
- i18n from sprint 1 - not bolted on
- Supported locales: en, fr-CA, pt-BR, es, de

---

## Architecture Overview

### System Architecture

``````
Internet Browser
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Next.js / React 19 / Fluent UI v9 / i18next    │
│ HTTPS + Entra ID OIDC (multi-tenant)           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
         ┌──────────────┐
         │     APIM     │
         │ - Throttling │
         │ - Caching    │
         │ - Tier Gates │
         └──────┬───────┘
                │
                ▼
┌────────────────────────────────────────────────┐
│    API Service (FastAPI / Python 3.12)        │
│    Azure Container App                         │
├────────────────────────────────────────────────┤
│ Routers: health, auth, scans, findings,       │
│          checkout, admin                       │
└─┬──────────────────────────────────────────────┘
  │
  ├─────────────────┐
  │                 │
  ▼                 ▼
┌──────────┐   ┌────────────────────┐
│ Cosmos   │   │ Container App Jobs │
│ DB NoSQL │   ├────────────────────┤
│          │   │ 1. Collector       │
│ 9        │   │ 2. Analysis        │
│ Containers│  │ 3. Delivery        │
└──────────┘   └────────────────────┘
     │
     └─────────────┐
                   │
     ┌─────────────┴─────────────┐
     │                           │
     ▼                           ▼
┌─────────┐              ┌──────────────┐
│ Stripe  │              │ GTM / GA4 /  │
│ Billing │              │ MS Clarity   │
└─────────┘              └──────────────┘
``````

### Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| **Frontend** | React | 19 | Vite build, Fluent UI v9 |
| **Backend API** | FastAPI | 0.109+ | Python 3.12, async/await |
| **Database** | Azure Cosmos DB | NoSQL API | Partition key: subscriptionId |
| **Identity** | Microsoft Entra ID | Multi-tenant | OIDC + MSAL |
| **Payments** | Stripe | API v2024 | Checkout + webhooks |
| **Analytics** | GA4 + Clarity | - | Consent-gated |
| **i18n** | i18next | 23+ | react-i18next |
| **Infrastructure** | Azure Container Apps | - | API + 3 jobs |
| **Gateway** | Azure APIM | - | Throttling + caching |

---

## Epic Roadmap

### Phase 1 - MVP Foundation (Epics 01-09)

**Target**: M1.0 Launch (8 weeks from March 11, 2026)  
**Scope**: 312 stories across 9 epics  
**Status**: Active development (47 sprints completed)

"@

# Add epic table for Phase 1
$readmeContent += "`n| Epic | Title | Stories | FP | Status |`n"
$readmeContent += "|------|-------|---------|-----|--------|`n"

$phase1Epics = $epics | Where-Object { $_.Phase -eq 1 }
foreach ($epic in $phase1Epics) {
    $readmeContent += "| **$($epic.ID)** | $($epic.Title) | $($epic.Stories) | $($epic.FP) | $($epic.Status) |`n"
}

$phase1Total = ($phase1Epics | Measure-Object -Property Stories -Sum).Sum
$phase1FP = ($phase1Epics | Measure-Object -Property FP -Sum).Sum

$readmeContent += "`n**Phase 1 Total**: $phase1Total stories, $phase1FP FP`n`n"

$readmeContent += @"
### Complete Epic Summary

**All 19 Epics** (Phase 1-10):

| Epic | Title | Stories | FP | Phase | Status |
|------|-------|---------|-----|-------|--------|

"@

foreach ($epic in $epics) {
    $readmeContent += "| **$($epic.ID)** | $($epic.Title) | $($epic.Stories) | $($epic.FP) | Phase $($epic.Phase) | $($epic.Status) |`n"
}

$readmeContent += "`n**Total Program**: $totalStories stories, $totalFP FP (~37 person-years estimated)`n`n"

$readmeContent += @"
---

## Infrastructure

### Phase 1 - Shared EVA Infrastructure (Current)

**Resource Group**: EVA-Sandbox-dev  
**Region**: Canada Central/East  
**Naming**: ``msub-*`` prefix

| Resource | Name | Purpose |
|----------|------|---------|
| **Container Apps Environment** | msub-ACA-env | Hosts API + 3 jobs |
| **Container App (API)** | msub-aca-api | FastAPI backend |
| **Container App Job (Collector)** | msub-aca-collector | Data collection job |
| **Container App Job (Analysis)** | msub-aca-analysis | Analysis engine job |
| **Container App Job (Delivery)** | msub-aca-delivery | Script generation job |
| **Cosmos DB** | msub-sandbox-cosmos | ACA-specific containers |
| **APIM** | msub-sandbox-apim | Gateway with throttling |
| **Key Vault** | msubsandkv202603031449 | Secrets, connection strings |
| **ACR** | msubsandacr202603031449 | Container images |
| **Blob Storage** | msubsandboxstorage | Deliverable packages |

### Cosmos DB Containers

| Container | Partition Key | Purpose |
|-----------|---------------|---------|
| **scans** | /subscriptionId | Scan lifecycle (status, stats, errors) |
| **inventories** | /subscriptionId | Resource inventory snapshots |
| **cost-data** | /subscriptionId | Daily cost rows (91 days) |
| ** advisor** | /subscriptionId | Advisor recommendations |
| **findings** | /subscriptionId | Analysis output (tiered view) |
| **clients** | /subscriptionId | Client records + tier assignments |
| **deliverables** | /subscriptionId | Delivery artifacts + SAS URLs |
| **entitlements** | /subscriptionId | Tier unlock grants |
| **payments** | /subscriptionId | Stripe payment records |

**Critical Rule**: Every read/write on tenant data MUST pass ``partition_key=subscriptionId``. No cross-tenant queries. No ``SELECT *`` without partition filter.

---

## Analysis Rules

ACA implements 12+ analysis rules across 7 categories.

### Rule Categories

| Category | Rules | Purpose |
|----------|-------|---------|
| **Ghost Resources** | 8 | Detect orphaned/unattached resources |
| **Idle Resources** | 5 | Identify shutdown/scheduling opportunities |
| **Rightsizing** | 6 | Recommend SKU downgrades |
| **Reservations** | 4 | Calculate RI/savings plan opportunities |
| **Advisor-Backed** | 5 | Enrich Advisor recommendations |
| **Governance** | 4 | Policy/tagging/naming compliance |
| **Network** | 4 | Network optimization opportunities |

---

## Repository Structure

``````
51-ACA/
├── README.md              # This file
├── PLAN.md               # Complete WBS ($totalStories stories)
├── STATUS.md             # Sprint tracking, project health
├── ACCEPTANCE.md         # Quality gates (Phase 1-10)
├── docs/                 # 43 architectural documents
├── services/             # Backend services (API, collector, analysis, delivery)
├── frontend/            # React frontend
├── infra/              # Infrastructure as Code
├── tools/              # CLI utilities
└── tests/             # Test suites
``````

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Azure CLI 2.57+
- Docker Desktop
- VS Code + Azure extensions

### Local Development - Backend

``````powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uv icorn app.main:app --reload --port 8000
``````

### Local Development - Frontend

``````powershell
cd frontend
npm install
npm run dev
``````

Visit ``http://localhost:5173``

---

## EVA Ecosystem Integration

ACA integrates with the EVA Data Model and workspace tools:

### Data Model API (Project 37)

**Endpoint**: ``https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io``

**Bootstrap Pattern**:

``````powershell
`$base = "https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io"
`$session = @{
    base = `$base
    guide = (Invoke-RestMethod "`$base/model/agent-guide")
    userGuide = (Invoke-RestMethod "`$base/model/user-guide")
}
``````

### EVA Veritas (Project 48)

**Purpose**: Requirements traceability and MTI quality gate

**MCP Tools Available**:
- ``audit_repo``: Full repo MTI audit with gap analysis
- ``get_trust_score``: Quick MTI score
- ``sync_repo``: Paperless DPDCA cycle
- ``export_to_model``: Upload to data model

**Sprint Gate**: MTI score > 70 required before sprint advance.

---

## Quality Gates

### Sprint-Level Gates

| Gate | Threshold | Tool |
|------|-----------|------|
| MTI Trust Score | > 70 | eva audit-repo |
| Evidence Coverage | > 80% | Veritas evidence scan |
| Consistency Score | > 90% | Veritas consistency check |
| Test Coverage | > 80% | pytest + coverage |

---

## Contributing

1. **Story Selection**: Pick from PLAN.md with status "NOT-STARTED"
2. **Branch**: Create ``feature/ACA-NN-NNN-description``
3. **Development**: Follow DPDCA cycle
4. **Tests**: All tests must pass
5. **PR**: Link to story ID
6. **Merge**: MTI ≥ 70 required

---

## Support

- **Documentation**: [docs/](./docs/) - 43 specification documents
- **WBS**: [PLAN.md](./PLAN.md) - All $totalStories stories
- **Status**: [STATUS.md](./STATUS.md) - Sprint tracking
- **Quality**: [ACCEPTANCE.md](./ACCEPTANCE.md) - Gate criteria

---

**Last Updated**: 2026-03-11  
**Version**: 1.0.0  
**Generated**: Comprehensive governance regeneration from WBS reconciliation
"@

# Write README
if (-not $DryRun) {
    $readmePath = Join-Path $OutputDir "README.md"
    $readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
    Write-Host "[PASS] Generated README.md ($($readmeContent.Length) chars)" -ForegroundColor Green
} else {
    Write-Host "[DRY-RUN] Would generate README.md ($($readmeContent.Length) chars)" -ForegroundColor Yellow
}

Write-Host "`n[INFO] README.md generation complete"
Write-Host "[INFO] PLAN.md generation requires full story extraction from comprehensive WBS"
Write-Host "[INFO] That will be done in a follow-up script due to size (3000+ lines)"
