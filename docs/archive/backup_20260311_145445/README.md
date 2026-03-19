# Project 51 (ACA) -- Azure Cost Advisor

**Version**: 1.0.0  
**Status**: Phase 1 Active (marco* sandbox deployment)  
**Last Updated**: 2026-03-11  
**Maturity**: Active Development  
**Owner**: Marco Presta / EVA AI COE

---

## EVA Ecosystem Integration

| Tool | Purpose | How to Use |
|------|---------|------------|
| **37-data-model** | Central source of truth (cloud API): All 51-ACA stories, WBS hierarchy, evidence | `GET https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io/model/projects/51-ACA` |
| **29-foundry** | Agentic capabilities (search, RAG, eval, observability) | C:\eva-foundry\eva-foundation\29-foundry |
| **48-eva-veritas** | Trust score and coverage audit, MTI quality gate | MCP tool: `audit_repo` / `get_trust_score` |
| **07-foundation-layer** | Copilot instructions primer + governance templates | MCP tool: `apply_primer` / `audit_project` |

**Agent rule**: Query the data model API before reading source files.

```powershell
# Bootstrap session with live API data
$base = "https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io"
Invoke-RestMethod "$base/model/agent-guide"             # complete protocol
Invoke-RestMethod "$base/model/projects/51-ACA"         # project metadata
Invoke-RestMethod "$base/model/wbs?project_id=51-ACA"   # all WBS records
```

---

##

 Product Vision

**ACA is consulting-as-a-product.** 

A client navigates to the ACA web application, connects their Azure subscription with read-only consent, and receives a prioritized cost optimization report in under 5 minutes. The report delivers insights that previously required a 3-day consulting engagement as a self-serve SaaS product with three tiers: free summary, paid advisory report, and paid implementation deliverable package.

**Target Market**: Cloud platform managers or directors responsible for Azure subscriptions with $300K-$2M+ annual spend (CAD). They know costs are high but lack time to investigate. ACA performs the analysis and packages findings in board-ready language.

**Differentiators**:
1. **Read-only, zero-touch access** -- No resource modifications, revocable consent, fully audited
2. **Consulting-grade output, SaaS-grade delivery** -- Board language for executives, practitioner language for teams
3. **Multi-tenant architecture** -- Any Microsoft tenant can sign in (authority=common), no EsDAICoE dependency

---

## Service Tiers

### Tier 1 -- Free Scan
- **Price**: Free
- **Access**: No payment required. Sign in, connect subscription, collect data, view report.
- **Scope**: Opportunity titles + estimated savings range (CAD low/high). No narrative, no implementation guidance.
- **Purpose**: Lead generation. Conversion funnel to Tier 2 or Tier 3.

### Tier 2 -- Advisory Report
- **Price**: CAD $499 one-time OR CAD $150/month subscription
- **Access**: Unlocked after Stripe checkout (entitlements stored in Cosmos)
- **Scope**: Full prioritized findings with:
  - Narrative explaining each finding
  - Effort classification (trivial / easy / medium / involved / strategic)
  - Risk rating (none / low / medium / high)
  - Beyond-cost signals (SKU right-sizing, network hardening, policy gaps)
- **Delivery**: Interactive dashboard view + optional PDF export

### Tier 3 -- Deliverable Package
- **Price**: CAD $1,499 per subscription engagement
- **Access**: Unlocked after Stripe checkout. Triggers automated delivery agent.
- **Scope**: Everything in Tier 2 PLUS:
  - Bicep templates (Phase 1) parameterized for the client's subscription
  - Terraform templates (Phase 2+)
  - PowerShell/Bash automation scripts with subscription-specific values
  - Implementation guide PDF with rollback instructions
- **Delivery**: 168-hour (7-day) SAS URL to Azure Blob Storage download. Fully automated generation, no manual consultant hours.

---

## Architecture Overview

### Infrastructure (Phase 1 -- marco* sandbox)

| Component | Resource Name | Purpose |
|-----------|---------------|---------|
| **Cosmos DB** | `msub-sandbox-cosmos` | 11 containers: scans, inventories, cost-data, advisor, findings, clients, deliverables, entitlements, payments, stripe_customer_map, admin_audit_events |
| **Container Apps** | `msub-aca-api` | FastAPI backend (25+ REST endpoints, JWT-validated) |
| **Container Apps Jobs** | `msub-aca-collector` | Data collection worker (Azure Resource Graph, Cost Management, Advisor) |
| | `msub-aca-analysis` | Analysis engine (12 rules: R-01 through R-12) |
| | `msub-aca-delivery` | IaC template generator + ZIP packager (Tier 3) |
| **APIM** | `msub-sandbox-apim` | Tier-gated rate limiting, JWT validation, 60s entitlement cache |
| **Key Vault** | `msubsandkv202603031449` | All secrets (STRIPE_SECRET_KEY, COSMOS_KEY, etc.) |
| **Storage** | `msubsandblob` | Tier 3 deliverable storage with 7-day SAS URLs |
| **ACR** | `msubsandacr202603031449` | 4 container images: api, collector, analysis, delivery |

**Resource Group**: EVA-Sandbox-dev  
**Region**: Canada Central  
**Subscription**: MarcoSub (`c59ee575-eb2a-4b51-a865-4b618f9add0a`)

### Services

1. **API Service** (`services/api/`)
   - FastAPI with 25+ REST endpoints
   - JWT validation via JWKS (authority=common, multi-tenant)
   - Cosmos DB data layer (11 containers)
   - Stripe integration (checkout, webhooks, billing portal)
   - Admin endpoints (KPIs, customer search, entitlement grants, subscription lock)

2. **Collector Service** (`services/collector/`)
   - Pre-flight validation (5 capability probes: identity, RBAC, inventory, cost, advisor)
   - Azure Resource Graph queries (full subscription inventory)
   - Cost Management API (91 days historical cost data)
   - Azure Advisor recommendations
   - Policy compliance state, network signals (NSG, DNS, Public IP, VNet peering)

3. **Analysis Service** (`services/analysis/`)
   - Rule engine with 12 production rules (R-01 through R-12)
   - Findings assembly (category, title, savings estimate, effort/risk classification)
   - Tier-aware field gating (Tier 1: title+savings only, Tier 2: +narrative, Tier 3: +deliverables)
   - Isolation: one rule failure does not stop the engine

4. **Delivery Service** (`services/delivery/`)
   - Jinja2 template library (12 IaC templates: tmpl-devbox-autostop, tmpl-log-retention, etc.)
   - Bicep generation (Phase 1), Terraform deferred to Phase 2
   - ZIP assembly with findings.json manifest
   - SHA-256 signing, Azure Blob upload, 7-day SAS URL generation

5. **Frontend** (`frontend/`)
   - React 19 + TypeScript + Fluent UI v9
   - Spark architecture: `/app/*` (customer pages) + `/admin/*` (admin dashboard)
   - 5 customer pages: Login, Connect, Status, Findings, Upgrade
   - 5 admin pages: Dashboard, Customers, Billing, Runs, Controls
   - i18n: 5 locales (EN, FR, PT-BR, ES, DE) with react-i18next
   - a11y: WCAG 2.1 AA compliance, axe-core CI gate, keyboard navigation

### 12 Analysis Rules

| Rule | Template ID | Title | Threshold | Category |
|------|-------------|-------|-----------|----------|
| R-01 | tmpl-devbox-autostop | Dev Box auto-stop | Annual Dev Box cost > $1,000 | Compute |
| R-02 | tmpl-log-retention | Log retention tuning | Annual Log Analytics cost > $500 (non-prod) | Observability |
| R-03 | tmpl-defender-plan | Defender plan optimization | Annual Defender cost > $2,000 | Security |
| R-04 | tmpl-compute-schedule | Compute scheduling | Annual schedulable compute > $5,000 | Compute |
| R-05 | tmpl-anomaly-alert | Anomaly detection | Category z-score > 3.0 | FinOps |
| R-06 | tmpl-stale-envs | Stale environment cleanup | >= 3 App Service sites | Waste |
| R-07 | tmpl-search-sku | Search SKU right-sizing | Annual Search cost > $2,000 | Data |
| R-08 | tmpl-acr-consolidation | ACR consolidation | >= 3 ACR registries | Infrastructure |
| R-09 | tmpl-dns-consolidation | DNS sprawl reduction | Annual DNS cost > $1,000 | Networking |
| R-10 | tmpl-savings-plan | Savings plan coverage | Annual compute > $20,000 | Commitment |
| R-11 | tmpl-apim-token-budget | APIM token budget alert | APIM + OpenAI both present | Risk |
| R-12 | tmpl-chargeback-policy | Chargeback gap detection | Total period cost > $5,000 | Governance |

---

## Repository Structure

```
51-ACA/
├── README.md                   # This file (product vision, architecture)
├── PLAN.md                     # Work Breakdown Structure (15 epics, ~281 stories)
├── STATUS.md                   # Sprint tracking, completion metrics
├── ACCEPTANCE.md               # Quality gates (Phase 1: 12 gates, Phase 2: 5 gates)
├── services/
│   ├── api/                    # FastAPI backend (25+ REST endpoints)
│   ├── collector/              # Data collection worker
│   ├── analysis/               # Analysis engine + 12 rules
│   └── delivery/               # IaC template generator
├── frontend/                   # React 19 + TypeScript + Fluent UI v9
│   ├── src/
│   │   ├── app/                # Customer pages (/app/*)
│   │   ├── admin/              # Admin pages (/admin/*)
│   │   ├── i18n/               # 5 locales (EN, FR, PT-BR, ES, DE)
│   │   └── components/         # Shared UI components
│   └── public/
├── infra/
│   ├── phase1-marco/           # Bicep templates (marco* sandbox)
│   └── phase2-private/         # Terraform templates (private subscription)
├── scripts/                    # Data seeding, harvest, reconciliation
├── docs/                       # 43 design docs + architecture + guides
│   ├── 01-feasibility.md
│   ├── 02-preflight.md
│   ├── ...
│   ├── 43-ph10-ecosystem.md
│   └── archive/                # Archived governance files (replaced by re-prime)
└── .eva/                       # Veritas audit artifacts
    ├── veritas-plan.json       # Canonical WBS (281 stories)
    ├── discovery.json          # Artifact coverage
    ├── reconciliation.json     # Evidence + gap analysis
    ├── trust.json              # MTI score + sparkline
    └── model-export.json       # Full data model export
```

---

## Getting Started

### Prerequisites

- Python 3.10+ (services)
- Node.js 20+ (frontend)
- Azure CLI (infra deployment)
- Docker + Docker Compose (local dev)
- Access to MarcoSub subscription (deployment)

### Local Development

```bash
# 1. Clone and navigate
git clone <repo-url>
cd 51-ACA

# 2. Configure environment
cp .env.example .env
# Edit .env with local values (see docs/AGENT-51-QUICKSTART.md)

# 3. Start all services
docker-compose up

# 4. Verify health
curl http://localhost:8080/health
# Expected: {"status": "ok", "version": "1.0.0"}

# 5. Run tests
cd services/api && pytest -x -q
cd services/collector && pytest -x -q
cd services/analysis && pytest -x -q
cd services/delivery && pytest -x -q
cd frontend && npm test
```

### Deployment (Phase 1)

```bash
# 1. Authenticate to Azure
az login
az account set --subscription "MarcoSub"

# 2. Deploy infrastructure
cd infra/phase1-marco
az deployment group create \
  --resource-group EVA-Sandbox-dev \
  --template-file main.bicep \
  --parameters @parameters.json

# 3. Deploy services via GitHub Actions
# Push to main branch triggers .github/workflows/deploy-phase1.yml

# 4. Verify deployment
curl https://<container-app-url>/health
```

---

## Data Model Integration

**Cloud API**: `https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io`

All 281 stories are registered in the WBS layer with epic → feature → user_story hierarchy. Query examples:

```powershell
# Get all WBS records for 51-ACA
$wbs = Invoke-RestMethod "$base/model/wbs?project_id=51-ACA&limit=500"

# Get project metadata
$project = Invoke-RestMethod "$base/model/projects/51-ACA"

# Get specific story
$story = Invoke-RestMethod "$base/model/wbs/WBS-S042"

# Get all features for Epic 3
$features = $wbs | Where-Object { $_.parent_wbs_id -eq "WBS-E03" -and $_.level -eq "feature" }

# Get all stories for Feature 3.3
$stories = $wbs | Where-Object { $_.parent_wbs_id -eq "WBS-F03" -and $_.level -eq "user_story" }
```

---

## Quality Gates

Project 51-ACA uses **MTI (Minimum Trust Index)** from Project 48 (eva-veritas) as the primary quality gate.

**MTI Formula** (5-component):
```
MTI = 0.35×coverage + 0.20×evidence + 0.25×consistency + 0.10×complexity + 0.10×field_population
```

**Gate Thresholds**:
- **< 60**: Fail (block deployment)
- **60-70**: Review required (manual approval)
- **70-85**: Pass (merge with approval)
- **≥ 85**: Excellent (auto-merge eligible)

**Current Status** (as of 2026-03-11):
- MTI: TBD (re-prime in progress)
- Coverage: TBD
- Evidence: TBD
- Consistency: TBD
- Action: Run Veritas audit after PLAN.md regeneration

---

## Contributing

1. **Story Selection**: Pick a story from PLAN.md with status "not-started"
2. **Branch**: Create feature branch `feature/ACA-NN-NNN-short-title`
3. **Development**: Follow story acceptance criteria + DPDCA cycle
4. **Commit**: Include `# EVA-STORY: ACA-NN-NNN` in commit message
5. **Tests**: All tests must pass (`pytest` + `npm test`)
6. **PR**: Create PR with story ID in title, link to story in PLAN.md
7. **Review**: Veritas audit runs automatically, MTI must be ≥ 60
8. **Merge**: Approved PRs update story status to "done" in data model

---

## Milestones

| Milestone | Target | Epic(s) | Deliverable |
|-----------|--------|---------|-------------|
| **M1.0** | +2 weeks | 1 | Local dev works. Phase 1 Bicep deployed. |
| **M1.1** | +3 weeks | 2 | Collector runs against EsDAICoE-Sandbox. |
| **M1.2** | +3 weeks | 3 | 12 rules produce findings. Tier gate passes. |
| **M1.3** | +3 weeks | 4 | All 25 API endpoints live behind APIM. |
| **M1.4** | +4 weeks | 5 | All 9 frontend pages. Tier 1 flow end-to-end. |
| **M1.5** | +4 weeks | 6 | Stripe checkout + webhook + entitlements live. |
| **M1.6** | +5 weeks | 7 | Tier 3 ZIP delivered via SAS URL. |
| **M2.0** | +5 weeks | 8 | GA4 + Clarity + App Insights all live. |
| **M2.1** | +6 weeks | 9 | EN + FR live. axe-core CI gate green. |
| **M2.2** | +7 weeks | 10 | Red-team passes. Privacy docs published. |
| **M3.0** | +10 weeks | 11 | Phase 2 infra live. Custom domain active. |

---

## Support

- **Documentation**: [docs/](docs/) (43 design docs)
- **Quick Start**: [docs/AGENT-51-QUICKSTART.md](docs/AGENT-51-QUICKSTART.md)
- **Cloud Agent Guide**: [docs/CLOUD-AGENT-EXECUTION-GUIDE.md](docs/CLOUD-AGENT-EXECUTION-GUIDE.md)
- **Data Model Assessment**: [docs/DATA-MODEL-ASSESSMENT.md](docs/DATA-MODEL-ASSESSMENT.md)
- **Architecture**: [docs/ARCHITECTURE-ONBOARDING-SYSTEM.md](docs/ARCHITECTURE-ONBOARDING-SYSTEM.md)
- **Engagement Model**: [docs/README-ENGAGEMENT-MODEL.md](docs/README-ENGAGEMENT-MODEL.md)

---

## License

Proprietary -- EVA AI COE / Marco Presta

---

**Last Re-Prime**: 2026-03-11 (Ground-up regeneration from docs 01-43 following Veritas audit standards)
