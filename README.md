# ACA - Azure Cost Advisor

# 51-ACA

<!-- Placeholders: 51-ACA = project folder name (e.g., "37-data-model", "48-eva-veritas") -->

**Template Version**: v5.0.0 (Session 44 - Governance Template Consolidation)  
**Part of EVA Foundry Workspace** | [Data Model](https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA) | [Veritas Audit](#veritas-audit)  
**Workspace Skills**: @sprint-advance | @progress-report | @gap-report | @sprint-report | @veritas-expert

---

## EVA Quick Links

| Resource | Link |
|----------|------|
| **Project Record** | `GET https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA` |
| **Live Session Data** | `GET .../model/project_work/?project_id=51-ACA&$orderby=id%20desc&$limit=10` |
| **Veritas Audit** | Run `audit_repo` MCP tool on `C:\eva-foundry\51-ACA` |
| **Trust Score** | Run `get_trust_score` MCP tool on `C:\eva-foundry\51-ACA` |
| **Sync to Model** | Run `sync_repo` MCP tool (full paperless DPDCA audit + write-back) |
| **Governance** | [PLAN.md](./PLAN.md) \| [STATUS.md](./STATUS.md) \| [ACCEPTANCE.md](./ACCEPTANCE.md) |
| **Instructions** | [.github/copilot-instructions.md](./.github/copilot-instructions.md) |

---


**Version**: 1.0.0  
**Status**: Active Development (Phase 1)  
**Last Updated**: 2026-03-11  
**Project ID**: 51-ACA  
**Total Stories**: 563  
**Total Function Points**: 4240 FP  
**EVA Foundation**: Primed ?  
# ACA - Azure Cost Advisor

**Version**: 1.0.0  
**Status**: Active Development (Phase 1)  
**Last Updated**: 2026-03-12 
**Project ID**: 51-ACA  
**Total Stories (full backlog)**: 546  
**Phase 1 Stories (data model)**: 281  
**Total Function Points**: 4,890 FP (preliminary)  
**EVA Foundation**: Primed ?  
**MTI Score**: 99 (gate: 70)  

---

## ?? FKTE Strategic Context

**ACA is the first implementation of the Fractal Knowledge Transformation Engine (FKTE)** - specifically, the **FinOps Factory**.

This project serves as:
- **Proof of Concept**: Validates FKTE pattern in production (6+ months battle-tested)
- **Reference Implementation**: Template for all future factories (Security, Compliance, Performance)
- **Phase 1 Product**: First revenue-generating factory ($3M ARR target, see [57-FKTE Business Model](../57-FKTE/docs/BUSINESS-MODEL-AND-GTM.md))

**FKTE Architecture Applied**:
```
Observatory   ? Azure Resource Graph API, Cost Management API, Azure Advisor
Analyzer      ? Pareto analysis (80/20 rule), cost ranking, SKU optimization
Synthesizer   ? Narrative generation, IaC templates, implementation guides
Publisher     ? Interactive dashboard, PDF reports, downloadable packages
```

**Economic Model**: Traditional Azure consulting costs $5K-$15K (3-5 days). ACA delivers same in 5 minutes for $499-$1,499.

**Strategic Value**: Proving this pattern enables replication to 50+ domains (see [57-FKTE docs](../57-FKTE/docs/)).

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

**Target Buyer**: Cloud platform managers or directors responsible for development Azure subscriptions in the CAD $300K-$2M+ annual spend range. They know costs are high but lack time to investigate. ACA does the investigation and packages the answer in board-ready language.

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
| **Price** | CAD $499 one-time OR CAD $150/month subscription |
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
| **Price** | CAD $1,499 per subscription engagement |
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

**Multi-Tenant Architecture**: ACA uses `authority=https://login.microsoftonline.com/common` - any client with a Microsoft account from any tenant can sign in.

| Mode | Description | Use Case |
|------|-------------|----------|
| **Mode A** | Delegated sign-in via Microsoft (any tenant) | Quick scan, trial-friendly |
| **Mode B** | Service principal provided by client | Enterprise governance-friendly |
| **Mode C** | Azure Lighthouse delegation | MSP-grade, multi-subscription |

**What Matters**: Delegated token has Reader + Cost Management Reader on CLIENT's subscription.

### 4. 12+ Analysis Rules from Real Production Data

All heuristics are seeded from real spending patterns in `C:\eva-foundry\14-az-finops` - not generic advice.

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

```
Internet Browser
    ?
    ?
???????????????????????????????????????????????????
? Next.js / React 19 / Fluent UI v9 / i18next    ?
? HTTPS + Entra ID OIDC (multi-tenant)           ?
???????????????????????????????????????????????????
                 ?
                 ?
         ????????????????
         ?     APIM     ?
         ? - Throttling ?
         ? - Caching    ?
         ? - Tier Gates ?
         ????????????????
                ?
                ?
??????????????????????????????????????????????????
?    API Service (FastAPI / Python 3.12)        ?
?    Azure Container App                         ?
??????????????????????????????????????????????????
? Routers: health, auth, scans, findings,       ?
?          checkout, admin                       ?
??????????????????????????????????????????????????
  ?
  ???????????????????
  ?                 ?
  ?                 ?
????????????   ??????????????????????
? Cosmos   ?   ? Container App Jobs ?
? DB NoSQL ?   ??????????????????????
?          ?   ? 1. Collector       ?
? 9        ?   ? 2. Analysis        ?
? Containers?  ? 3. Delivery        ?
????????????   ??????????????????????
     ?
     ???????????????
                   ?
     ?????????????????????????????
     ?                           ?
     ?                           ?
???????????              ????????????????
? Stripe  ?              ? GTM / GA4 /  ?
? Billing ?              ? MS Clarity   ?
???????????              ????????????????
```

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

| Epic | Title | Stories | FP | Status |
|------|-------|---------|-----|--------|
| **01** | Authentication & Authorization Framework | 23 | 180 | ACTIVE |
| **02** | Data Collection Subsystem | 42 | 320 | ACTIVE |
| **03** | Analysis Engine & Rules | 47 | 380 | ACTIVE |
| **04** | Delivery & Script Generation | 32 | 240 | PLANNED |
| **05** | Frontend Application (Customer & Admin) | 38 | 280 | ACTIVE |
| **06** | API Service (FastAPI Backend) | 43 | 310 | ACTIVE |
| **07** | Billing & Payment Integration | 28 | 180 | ACTIVE |
| **08** | Infrastructure & Deployment | 32 | 200 | ACTIVE |
| **09** | Analytics & Telemetry | 27 | 90 | ACTIVE |

**Phase 1 Total**: 312 stories, 2180 FP

### Complete Epic Summary

**All 19 Epics** (Phase 1-10):

| Epic | Title | Stories | FP | Phase | Status |
|------|-------|---------|-----|-------|--------|
| **01** | Authentication & Authorization Framework | 23 | 180 | Phase 1 | ACTIVE |
| **02** | Data Collection Subsystem | 42 | 320 | Phase 1 | ACTIVE |
| **03** | Analysis Engine & Rules | 47 | 380 | Phase 1 | ACTIVE |
| **04** | Delivery & Script Generation | 32 | 240 | Phase 1 | PLANNED |
| **05** | Frontend Application (Customer & Admin) | 38 | 280 | Phase 1 | ACTIVE |
| **06** | API Service (FastAPI Backend) | 43 | 310 | Phase 1 | ACTIVE |
| **07** | Billing & Payment Integration | 28 | 180 | Phase 1 | ACTIVE |
| **08** | Infrastructure & Deployment | 32 | 200 | Phase 1 | ACTIVE |
| **09** | Analytics & Telemetry | 27 | 90 | Phase 1 | ACTIVE |
| **10** | Phase 6 - Continuous Monitoring | 22 | 220 | Phase 3 | PLANNED |
| **11** | Phase 7 - Enterprise Multi-Tenant Platform | 36 | 280 | Phase 4 | PLANNED |
| **12** | Phase 8 - Autonomous Optimization | 35 | 310 | Phase 5 | PLANNED |
| **13** | Phase 9 - Predictive & Strategic Optimization | 28 | 260 | Phase 6 | PLANNED |
| **14** | Phase 10 - Ecosystem & Intelligence Platform | 34 | 320 | Phase 7 | PLANNED |
| **15** | Testing & Quality Assurance | 24 | 180 | Phase Ongoing | ACTIVE |
| **16** | Documentation | 18 | 120 | Phase Ongoing | ACTIVE |
| **17** | DevOps & CI/CD | 22 | 150 | Phase Ongoing | ACTIVE |
| **18** | Marketing & Go-To-Market | 15 | 100 | Phase Future | PLANNED |
| **19** | Compliance & Governance | 17 | 120 | Phase Ongoing | ACTIVE |

**Total Program**: 563 stories, 4240 FP (~37 person-years estimated)

---

## Infrastructure

### Phase 1 - Shared EVA Infrastructure (Current)

**Resource Group**: EVA-Sandbox-dev  
**Region**: Canada Central/East  
**Naming**: `msub-*` prefix

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

**Critical Rule**: Every read/write on tenant data MUST pass `partition_key=subscriptionId`. No cross-tenant queries. No `SELECT *` without partition filter.

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

```
51-ACA/
??? README.md              # This file
??? PLAN.md               # Complete WBS (563 stories)
??? STATUS.md             # Sprint tracking, project health
??? ACCEPTANCE.md         # Quality gates (Phase 1-10)
??? docs/                 # 43 architectural documents
??? services/             # Backend services (API, collector, analysis, delivery)
??? frontend/            # React frontend
??? infra/              # Infrastructure as Code
??? tools/              # CLI utilities
??? tests/             # Test suites
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Azure CLI 2.57+
- Docker Desktop
- VS Code + Azure extensions

### Local Development - Backend

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uv icorn app.main:app --reload --port 8000
```

### Local Development - Frontend

```powershell
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`

---

## EVA Ecosystem Integration

ACA is the proof-of-concept implementation of the **Fractal Knowledge Transformation Engine (FKTE)** pattern and integrates with multiple EVA Foundation projects.

### FKTE Architectural Home (Project 57)

**Reference**: [Fractal Knowledge Transformation Engine](../57-FKTE/docs/FRACTAL-KNOWLEDGE-TRANSFORMATION-ENGINE.md)

51-ACA demonstrates the FKTE Observatory ? Analyzer ? Synthesizer ? Publisher pattern and serves as the FinOps SaaS reference implementation. Future factories (Security, Compliance, Performance) use the same architectural patterns proven here.

**FKTE Sister Projects**:
- **Project 51-ACA** (FinOps SaaS): Reference implementation [this project]
- **Project 58-CyberSec** (Cybersecurity SaaS): Follow-on FKTE implementation validating domain independence

### Data Model API (Project 37)

**Endpoint**: `https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io`

**View Live 51-ACA Data**: [Model Portal](https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA)

**Bootstrap Pattern**:

```powershell
$base = "https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io"
$session = @{
    base = $base
    guide = (Invoke-RestMethod "$base/model/agent-guide")
    userGuide = (Invoke-RestMethod "$base/model/user-guide")
}
```

**Query Examples**:
```powershell
# Get project metadata
Invoke-RestMethod "$base/model/projects/51-ACA"

# List in-progress stories
Invoke-RestMethod "$base/model/wbs/?project_id=51-ACA&status=in-progress"

# Get latest evidence
Invoke-RestMethod "$base/model/evidence/?project_id=51-ACA&$limit=10&$orderby=created%20desc"
```

### Infrastructure Layers (Project 60-IaC)

**New Capability** (deployed March 13, 2026): Infrastructure-as-Code automation has expanded the data model from 91 ? 120 operational layers.

**ACA Integration Points**:
- **L112** (resource_catalog): 51-ACA onboarding references for multi-tenant resource management
- **L117** (cost_tracking): 51-ACA cost analysis rules integrate with infrastructure cost baseline
- **L119** (security_configuration): 51-ACA security findings link to infrastructure compliance state
- **L121+ (automation)**: Future autonomous compliance remediation (IaC generation on findings)

### EVA Veritas (Project 48)

**Purpose**: Requirements traceability and MTI quality gate

**MCP Tools Available**:
- `audit_repo`: Full repo MTI audit with gap analysis (discovers 281 stories from WBS)
- `get_trust_score`: Quick MTI score query
- `sync_repo`: Paperless DPDCA cycle (query ? audit ? write-back ? export)
- `export_to_model`: Upload WBS/evidence/decisions/risks to data model

**Sprint Gate**: MTI score > 70 required before sprint advance.

**Current Score**: MTI 98/100 (Coverage 100%, Consistency 100%, Field Population 84%)

### UI Generation (Project 30-UI-Bench & 37-Data-Model)

**Auto-Generated Dashboards**: 51-ACA dashboard screens are generated from data model layer definitions.
- Layer registry auto-generates 262+ screens (visible at 37-data-model `/model` portal)
- Admin dashboards, customer dashboards, and reports auto-generated from layer schemas
- No manual UI scaffold needed for new features

### Workspace Skills

Workspace-level skills available for 51-ACA:
- `@sprint-advance` ? Pre-sprint verification gates
- `@progress-report` ? Sprint progress tracking
- `@gap-report` ? Find discrepancies
- `@sprint-report` ? Sprint closure reporting
- `@veritas-expert` ? Full governance audit

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
2. **Branch**: Create `feature/ACA-NN-NNN-description`
3. **Development**: Follow DPDCA cycle
4. **Tests**: All tests must pass
5. **PR**: Link to story ID
6. **Merge**: MTI ? 70 required

---

## Support

- **Documentation**: [docs/](./docs/) - 43 specification documents
- **WBS**: [PLAN.md](./PLAN.md) - All 563 stories
- **Status**: [STATUS.md](./STATUS.md) - Sprint tracking
- **Quality**: [ACCEPTANCE.md](./ACCEPTANCE.md) - Gate criteria

---

**Last Updated**: 2026-03-11  
**Version**: 1.0.0  
**Generated**: Comprehensive governance regeneration from WBS reconciliation
