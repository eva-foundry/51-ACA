# ACA -- Infrastructure Architecture

Version: 1.0.0
Updated: 2026-02-28
Status: Active
Audience: DevOps Engineers, Cloud Architects, SREs

---

## PURPOSE

This document defines the Azure infrastructure deployment model for Azure Cost Advisor
(ACA), covering resource topology, networking, identity configuration, deployment
pipelines, and migration strategy from Phase 1 (proof of concept) to Phase 2 (production).

Read this document when: provisioning resources, debugging deployment issues, planning
capacity changes, or understanding the difference between Phase 1 and Phase 2 topologies.

---

## DEPLOYMENT PHASES OVERVIEW

ACA follows a two-phase infrastructure strategy:

**Phase 1 (Q1 2026)**: Proof of concept -- reuse existing marco-sandbox-* resources
in the EsDAICoE-Sandbox resource group. Goal: validate product-market fit with ZERO
new Azure spend.

**Phase 2 (Q2 2026)**: Production -- provision isolated private subscription with clean
resource naming, dedicated networking, and production-grade observability. Goal: support
10,000 active subscriptions with 99.9% uptime SLA.

---

## PHASE 1 INFRASTRUCTURE (PROOF OF CONCEPT)

### Resource Group Topology

```
Subscription: d2d4e571-e0f2-4f6c-901a-f88f7669bcba (EsDAICoESub)
Resource Group: EsDAICoE-Sandbox
Region: canadacentral (primary), canadaeast (OpenAI + Foundry)

┌────────────────────────────────────────────────────────────────────┐
│  EsDAICoE-Sandbox Resource Group                                   │
│                                                                     │
│  ┌──────────────────────┐     ┌─────────────────────────────┐     │
│  │  Identity & Secrets  │     │  Compute & Orchestration    │     │
│  │                      │     │                             │     │
│  │  marcosandkv         │────>│  ACA API (Container App)    │     │
│  │  20260203            │     │  ACA Collector (Job)        │     │
│  │                      │     │  ACA Analysis (Job)         │     │
│  │  Entra App Reg       │     │  ACA Delivery (Job)         │     │
│  │  (ACA-CLIENT-ID)     │     │                             │     │
│  └──────────────────────┘     └─────────────────────────────┘     │
│                                                                     │
│  ┌──────────────────────┐     ┌─────────────────────────────┐     │
│  │  Data & Storage      │     │  Gateway & Observability    │     │
│  │                      │     │                             │     │
│  │  marco-sandbox-      │     │  marco-sandbox-apim         │     │
│  │  cosmos              │────>│  (API Management)           │     │
│  │                      │     │                             │     │
│  │  marcosand20260203   │     │  marco-sandbox-appinsights  │     │
│  │  (Blob Storage)      │     │  (Application Insights)     │     │
│  └──────────────────────┘     └─────────────────────────────┘     │
│                                                                     │
│  ┌──────────────────────┐     ┌─────────────────────────────┐     │
│  │  AI & ML Services    │     │  FinOps Hub                 │     │
│  │                      │     │                             │     │
│  │  marco-sandbox-      │     │  marcosandboxfinopshub      │     │
│  │  openai-v2           │────>│  (Storage Account)          │     │
│  │  (canadaeast)        │     │                             │     │
│  │                      │     │  marco-sandbox-finops-adf   │     │
│  │  marco-sandbox-      │     │  (Data Factory)             │     │
│  │  foundry             │     │                             │     │
│  │  (canadaeast)        │     └─────────────────────────────┘     │
│  └──────────────────────┘                                          │
│                                                                     │
│  ┌──────────────────────┐     ┌─────────────────────────────┐     │
│  │  Container Registry  │     │  Additional Services        │     │
│  │                      │     │  (future use)               │     │
│  │  marcosandacr        │     │                             │     │
│  │  20260203            │     │  marco-sandbox-search       │     │
│  │                      │     │  marco-sandbox-aisvc        │     │
│  └──────────────────────┘     │  marco-sandbox-docint       │     │
│                                └─────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────┘
```

### Resource Inventory (Phase 1)

| Resource Name | Type | SKU | Purpose in ACA | Notes |
|---|---|---|---|---|
| **marcosandkv20260203** | Key Vault | Standard | Secrets (Cosmos conn, OpenAI key, Stripe key) | RBAC-enabled, soft-delete + purge protection |
| **marco-sandbox-cosmos** | Cosmos DB | Serverless NoSQL | ACA database (scans, inventories, findings, entitlements) | 400 RU/s (no autoscale), canadacentral |
| **marcosand20260203** | Storage Account | Standard LRS | IaC deliverables (Tier 3 zip files) | Blob container: `deliverables` (private) |
| **marcosandacr20260203** | Container Registry | Basic | ACA Docker images (API, collector, analysis, delivery) | 100 GB storage quota |
| **marco-sandbox-apim** | API Management | Consumption | API gateway (auth, throttling, cost attribution headers) | ACA product + subscription key |
| **marco-sandbox-openai-v2** | Azure OpenAI | S0 | GPT-4o for analysis narratives | canadaeast, gpt-4o deployment |
| **marco-sandbox-foundry** | AI Services | S0 | Agent orchestration (29-foundry) | canadaeast, Foundry project |
| **marco-sandbox-appinsights** | Application Insights | Classic | Observability (logs, metrics, traces) | 30-day retention |
| **marcosandboxfinopshub** | Storage Account | Standard LRS | Cost Management export landing (91-day data) | FinOps Toolkit integration |
| **marco-sandbox-finops-adf** | Data Factory | - | Cost ingestion pipeline (already working) | Ingests to Cosmos or datalake |
| **marco-sandbox-search** | AI Search | Free | Full-text + semantic search (Phase 2 candidate) | Not used in Phase 1 |
| **marco-sandbox-aisvc** | Cognitive Services | S0 | NLP / content moderation | Not used in Phase 1 |
| **marco-sandbox-docint** | Form Recognizer | S0 | IaC parsing (Tier 3, Phase 2) | Not used in Phase 1 |

**Container Apps (ACA-specific, NEW in Phase 1):**

| Name | Type | Image | Replicas | Notes |
|---|---|---|---|---|
| **aca-api** | Container App | ghcr.io/eva-foundry/aca-api:latest | 0-10 (autoscale) | FastAPI, port 8080 |
| **aca-collector** | Container App Job | ghcr.io/eva-foundry/aca-collector:latest | On-demand | Triggered by API, nightly cron |
| **aca-analysis** | Container App Job | ghcr.io/eva-foundry/aca-analysis:latest | On-demand | Triggered after collection |
| **aca-delivery** | Container App Job | ghcr.io/eva-foundry/aca-delivery:latest | On-demand | Tier 3 only |

**Frontend (Phase 1):**
- Option A: Azure Static Web App (not yet provisioned)
- Option B: Azure App Service (reuse marco-sandbox-backend slot)
- Decision: TBD (depends on Phase 1 deployment timeline)

---

### Cosmos DB Schema (Phase 1)

**Database:** `aca-db`
**Containers (partition key = subscriptionId):**

| Container | Partition Key | Purpose | TTL | Indexes |
|---|---|---|---|---|
| **scans** | subscriptionId | Scan orchestration records | None | status, started_at |
| **inventories** | subscriptionId | Azure resource inventory | 90 days | resource_type, location |
| **cost-data** | subscriptionId | 90-day cost time series | 90 days | date |
| **advisor** | subscriptionId | Azure Advisor recommendations | 30 days | category, impact |
| **findings** | subscriptionId | Analysis rule outputs | None | rule_id, category |
| **entitlements** | subscriptionId | Tier + feature flags per subscription | None | tier, valid_until |

**RU/s allocation:**
- Shared throughput: 400 RU/s (no autoscale, cost constraint)
- Estimated max: 100 subscriptions, 10,000 documents total

**Backup:**
- Continuous backup enabled (7-day PITR)
- No manual snapshots

**Consistency:**
- Session (default) -- acceptable for single-region

---

### Key Vault Secrets (Phase 1)

**Vault:** marcosandkv20260203 (canadacentral)
**Access policy:** RBAC mode

| Secret Name | Purpose | Rotation | Used By |
|---|---|---|---|
| **ADO-PAT** | Azure DevOps PAT (len=84, admin) | 90 days | ado-import scripts, parse-agent-log.py |
| **ACA-CLIENT-ID** | MSAL app client ID (delegated auth) | Manual | API service (auth.py) |
| **ACA-OPENAI-KEY** | Azure OpenAI key | Manual | Analysis service (OpenAI SDK) |
| **ACA-COSMOS-CONN** | Cosmos connection string | Managed identity (Phase 2) | API + all jobs |
| **STRIPE-SECRET-KEY** | Stripe secret key | Manual | API service (checkout.py) |
| **STRIPE-WEBHOOK-SECRET** | Stripe webhook signing secret | Manual | API service (webhooks.py) |

**RBAC assignments:**
- `Key Vault Secrets User`: aca-api managed identity, aca-collector MI, aca-analysis MI, aca-delivery MI
- `Key Vault Administrator`: EsDAICoESub owner (manual admin access)

---

### Networking (Phase 1)

**No private networking:**
- All resources on public endpoints (Phase 1 simplicity)
- TLS 1.2+ enforced (Azure default)
- API Management as gateway (public IP, no VNET injection)

**Firewall rules:**
- Cosmos: Allow all Azure services (no IP whitelist in Phase 1)
- Storage: Allow all Azure services
- Key Vault: No IP restrictions (RBAC only)

**DNS:**
- APIM custom domain: NOT configured in Phase 1 (default .azure-api.net domain)
- Frontend custom domain: NOT configured (Tier 1 uses Azure default)

---

### Managed Identity Flow (Phase 1)

```
┌──────────────┐        ┌──────────────────┐        ┌──────────────┐
│  Container   │───1───>│  Azure AD        │───2───>│  Key Vault   │
│  App (API)   │        │  (Managed        │        │              │
│              │<──4────│   Identity)      │<──3────│  Secrets     │
└──────────────┘        └──────────────────┘        └──────────────┘
      │                                                      │
      │ 5. Use secret                                       │
      v                                                      │
┌──────────────┐        ┌──────────────────┐               │
│  Cosmos DB   │───6───>│  Azure AD        │───────────────┘
│              │        │  (Token          │
│              │        │   Validation)    │
└──────────────┘        └──────────────────┘

Flow:
1. Container App requests Key Vault secret via managed identity
2. Azure AD validates identity and issues token
3. Key Vault checks RBAC (Key Vault Secrets User)
4. Key Vault returns secret (e.g. Cosmos connection string)
5. Container App uses secret to connect to Cosmos
6. Cosmos validates token (connection string includes auth key)
```

**No connection strings in code:**
- Environment variables: `COSMOS_URL`, `OPENAI_URL`, `KV_NAME`
- Secrets fetched at runtime via Azure SDK: `DefaultAzureCredential()`

---

### Deployment Pipeline (Phase 1)

**Infrastructure as Code:** Bicep (infra/phase1-marco/)

```
infra/phase1-marco/
  main.bicep                 -- Entry point, orchestrates all modules
  main.bicepparam            -- Parameter file (cosmosDbName, kvName, etc.)
  bootstrap.sh               -- Shell script: creates RG, deploys main.bicep
  cosmos-containers.bicep    -- Cosmos DB + containers definition
  apim/
    apim-products.bicep      -- APIM product + subscription key policy
    apim-policy.xml          -- Cost attribution headers, rate limiting
```

**Deployment sequence:**

```bash
# 1. Login to Azure
az login --use-device-code
az account set --subscription d2d4e571-e0f2-4f6c-901a-f88f7669bcba

# 2. Run bootstrap script (idempotent)
cd infra/phase1-marco
bash bootstrap.sh

# 3. Script output:
#    - Creates Cosmos containers if not exist
#    - Configures APIM product "51-ACA"
#    - Assigns managed identities to Key Vault
#    - Returns API Management subscription key (set in GitHub Actions secrets)
```

**CI/CD Pipeline:** GitHub Actions (.github/workflows/deploy-phase1.yml)

```yaml
name: Deploy ACA Phase 1

on:
  push:
    branches: [main]
    paths:
      - 'services/**'
      - 'frontend/**'
      - 'infra/phase1-marco/**'
      - '.github/workflows/deploy-phase1.yml'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # 1. Build Docker images
      - name: Build API image
        run: |
          docker build -t ghcr.io/eva-foundry/aca-api:${{ github.sha }} services/api
          docker push ghcr.io/eva-foundry/aca-api:${{ github.sha }}
      
      # 2. Build collector/analysis/delivery images (similar)
      
      # 3. Deploy infrastructure (Bicep)
      - name: Deploy Bicep
        run: |
          az deployment group create \
            --resource-group EsDAICoE-Sandbox \
            --template-file infra/phase1-marco/main.bicep \
            --parameters @infra/phase1-marco/main.bicepparam
      
      # 4. Update Container App revisions
      - name: Update API Container App
        run: |
          az containerapp update \
            --name aca-api \
            --resource-group EsDAICoE-Sandbox \
            --image ghcr.io/eva-foundry/aca-api:${{ github.sha }}
      
      # 5. Run smoke tests
      - name: Smoke test API
        run: curl -f https://aca-api.canadacentral.azurecontainerapps.io/health
```

**Rollback strategy:**
- Container App revisions: keep last 3 revisions
- Manual rollback: `az containerapp revision activate --revision <previous>`
- Cosmos: PITR restore (up to 7 days)

---

## PHASE 2 INFRASTRUCTURE (PRODUCTION)

### Strategic Goals

1. **Isolation**: Private subscription, no shared resources
2. **Scalability**: Support 10,000 subscriptions, 500 concurrent scans
3. **Reliability**: 99.9% uptime SLA, multi-region
4. **Security**: Customer-managed keys, private networking, SOC 2 ready
5. **Cost attribution**: Accurate per-tenant cost tracking

---

### Resource Group Topology (Phase 2)

```
Subscription: TBD (new private subscription -- Phase 2 provisioned)
Resource Group: aca-prod-canadacentral
Region: canadacentral (primary), canadaeast (secondary for OpenAI + Foundry)

┌────────────────────────────────────────────────────────────────────┐
│  aca-prod-canadacentral Resource Group                             │
│                                                                     │
│  ┌──────────────────────┐     ┌─────────────────────────────┐     │
│  │  Identity & Secrets  │     │  Compute & Orchestration    │     │
│  │                      │     │                             │     │
│  │  aca-kv-prod         │────>│  aca-api (Container App)    │     │
│  │  (customer-managed   │     │  aca-collector (Job)        │     │
│  │   keys)              │     │  aca-analysis (Job)         │     │
│  │                      │     │  aca-delivery (Job)         │     │
│  │  Entra App Reg       │     │  (Service Bus queue)        │     │
│  │  (prod client ID)    │     │                             │     │
│  └──────────────────────┘     └─────────────────────────────┘     │
│                                                                     │
│  ┌──────────────────────┐     ┌─────────────────────────────┐     │
│  │  Data & Storage      │     │  Gateway & Frontend         │     │
│  │                      │     │                             │     │
│  │  aca-cosmos-prod     │────>│  aca-apim-prod              │     │
│  │  (4000 RU/s          │     │  (Consumption or Standard)  │     │
│  │   autoscale)         │     │                             │     │
│  │                      │     │  aca-frontend (Static Web)  │     │
│  │  aca-delivery-store  │     │  (CDN enabled)              │     │
│  │  (deliverables)      │     │                             │     │
│  └──────────────────────┘     └─────────────────────────────┘     │
│                                                                     │
│  ┌──────────────────────┐     ┌─────────────────────────────┐     │
│  │  AI & ML Services    │     │  Observability & Monitoring │     │
│  │                      │     │                             │     │
│  │  aca-openai-prod     │────>│  aca-loganalytics (90-day)  │     │
│  │  (canadaeast)        │     │  aca-appinsights            │     │
│  │                      │     │  aca-frontdoor (WAF)        │     │
│  │  aca-foundry-prod    │     │                             │     │
│  │  (canadaeast)        │     └─────────────────────────────┘     │
│  └──────────────────────┘                                          │
│                                                                     │
│  ┌──────────────────────┐     ┌─────────────────────────────┐     │
│  │  Container Registry  │     │  Networking                 │     │
│  │                      │     │                             │     │
│  │  aca-acr-prod        │────>│  aca-vnet (10.0.0.0/16)     │     │
│  │  (Geo-replication)   │     │    - subnet-api             │     │
│  │                      │     │    - subnet-jobs            │     │
│  └──────────────────────┘     │    - subnet-data            │     │
│                                └─────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────┘
```

### Key Differences (Phase 1 vs Phase 2)

| Aspect | Phase 1 (Proof of Concept) | Phase 2 (Production) |
|---|---|---|
| **Subscription** | Shared (EsDAICoESub) | Dedicated private |
| **Resource naming** | marco-sandbox-* (reuse) | aca-*-prod (clean naming) |
| **Networking** | Public endpoints | Private VNET, private endpoints |
| **Cosmos RU/s** | 400 (no autoscale) | 4,000 autoscale (burst to 20k) |
| **Cosmos backup** | 7-day PITR | 35-day PITR + geo-redundancy |
| **APIM tier** | Consumption (shared) | Standard (dedicated, VNET-injected) |
| **Frontend** | TBD (Static Web or App Service) | Static Web App + Front Door (CDN + WAF) |
| **Managed keys** | Microsoft-managed | Customer-managed (Key Vault) |
| **Job orchestration** | Manual concurrency (no queue) | Service Bus Standard (1,000 concurrent) |
| **Observability** | 30-day App Insights | 90-day Log Analytics + workbooks |
| **Cost tracking** | Best-effort (APIM headers) | Azure Cost Management tags per tenant |
| **DNS** | Default (*.azurecontainerapps.io) | Custom domain (aca.example.com) |
| **TLS** | Azure-managed cert | Custom cert (Let's Encrypt or Azure) |
| **Uptime SLA** | 95% (best-effort) | 99.9% (formal SLA) |
| **IaC tool** | Bicep | Terraform (reuse 18-azure-best modules) |
| **Deployment** | GitHub Actions | GitHub Actions + Terraform Cloud |

---

### Terraform Modules (Phase 2)

**Source:** `C:\eva-foundry\18-azure-best\04-terraform-modules`

```
infra/phase2-private/
  main.tf                    -- Root module, orchestrates child modules
  variables.tf               -- Input variables (subscription_id, location, etc.)
  production.tfvars          -- Production environment values
  modules/
    acr/                     -- Azure Container Registry (geo-replication)
    cosmos/                  -- Cosmos DB (autoscale, geo-replication)
    container-apps/          -- Container Apps + Jobs (VNET-injected)
    key-vault/               -- Key Vault (customer-managed keys)
    apim/                    -- API Management (Standard tier)
    static-web/              -- Static Web App (frontend)
    frontdoor/               -- Front Door (CDN + WAF)
    observability/           -- Log Analytics + Application Insights
    networking/              -- VNET + subnets + NSGs
    service-bus/             -- Service Bus (job queue)
```

**Deployment command:**

```bash
cd infra/phase2-private
terraform init
terraform plan -var-file=production.tfvars
terraform apply -var-file=production.tfvars
```

**State management:**
- Terraform Cloud workspace: `aca-prod-canadacentral`
- Remote state: Azure Blob Storage (separate storage account)
- State locking: Azure Blob lease

---

### Private Networking (Phase 2)

**VNET:** aca-vnet (10.0.0.0/16)

| Subnet | CIDR | Purpose | NSG Rules |
|---|---|---|---|
| **subnet-api** | 10.0.1.0/24 | Container Apps (API) | Allow 443 inbound from Internet, outbound to Cosmos |
| **subnet-jobs** | 10.0.2.0/24 | Container App Jobs | Outbound to Cosmos, OpenAI, Storage, Internet |
| **subnet-data** | 10.0.3.0/24 | Cosmos + Storage private endpoints | No Internet access |
| **subnet-apim** | 10.0.4.0/24 | APIM VNET injection | Allow 443 inbound, outbound to API subnet |

**Private Endpoints:**

| Resource | Private Endpoint | Purpose |
|---|---|---|
| Cosmos DB | pe-cosmos | API + jobs access via VNET (no public endpoint) |
| Storage Account | pe-storage | Deliverables upload via VNET |
| Key Vault | pe-keyvault | Secret retrieval via VNET |

**Service Endpoints:**
- Enable `Microsoft.Storage` on subnet-jobs (faster Blob access)
- Enable `Microsoft.AzureCosmosDB` on subnet-api and subnet-jobs

**Public Internet access:**
- Frontend (Static Web App): Public (via Front Door only)
- APIM: Public (restricted to Front Door origin via NSG)
- Container Apps: Internal VNET (APIM handles ingress)

---

### High Availability (Phase 2)

**Multi-region topology:**

```
Primary: canadacentral
  - All compute (Container Apps, APIM, jobs)
  - Cosmos primary write region
  - Log Analytics primary

Secondary: canadaeast (read-only failover)
  - Cosmos secondary read region
  - OpenAI (already in canadaeast)
  - Foundry (already in canadaeast)
```

**Failover strategy:**
1. Cosmos multi-region write enabled (automatic failover policy)
2. Container Apps: manual failover (redeploy to canadaeast environment via Terraform)
3. APIM: Traffic Manager for multi-region routing (Phase 3)

**RTO / RPO:**
- RTO: 4 hours (manual runbook execution)
- RPO: 1 hour (Cosmos continuous backup, 35-day PITR)

---

### Autoscaling Configuration (Phase 2)

**Container App (API):**
- Min replicas: 1
- Max replicas: 50
- Scale trigger: CPU > 70% or HTTP queue length > 100

**Container App Jobs:**
- Concurrency: 10 per job instance
- Max parallel jobs: 50 (Service Bus queue controls fan-out)
- Timeout: 10 minutes per job

**Cosmos DB:**
- Autoscale RU/s: 400 - 20,000
- Trigger: Requests throttled (429 errors)

**Service Bus:**
- Standard tier (no Premium in Phase 2)
- Max delivery count: 5 (dead-letter after 5 failures)
- Lock duration: 5 minutes

---

### Cost Optimization (Phase 2)

**Reserved Instances:**
- Cosmos: 1-year reserved capacity (30% discount) -- TBD after 3 months usage data
- Container Apps: Not available (pay-as-you-go only)

**Lifecycle Policies:**
- Deliverables blob storage: Move to Cool tier after 7 days, Archive after 30 days
- Log Analytics: Export to cold storage after 90 days (cost: $0.01/GB vs $2.90/GB hot)

**Cost attribution tags:**
- Every resource tagged with: `project=aca`, `environment=prod`, `cost-center=saas`
- Cosmos queries log tenant subscriptionId -> Cost Management filters by subscription

**Estimated monthly cost (Phase 2, 1,000 active subscriptions):**

| Resource | SKU | Est. Cost CAD |
|---|---|---|
| Cosmos DB | 4,000 RU/s autoscale | $850 |
| Container Apps (API) | 1-10 replicas avg | $200 |
| Container App Jobs | On-demand (500 jobs/day) | $150 |
| Service Bus | Standard | $10 |
| APIM | Standard (1 unit) | $800 |
| Storage Account | LRS, 100 GB | $20 |
| Key Vault | Standard | $5 |
| OpenAI | GPT-4o (100k tokens/day) | $300 |
| Log Analytics | 50 GB/month | $150 |
| Front Door | 1 TB egress | $100 |
| **Total** | | **$2,585 CAD/month** |

**Revenue model (breakeven at 13 Tier 2 customers or 6 Tier 3 customers):**
- Tier 2: $199 CAD/month x 13 = $2,587
- Tier 3: $499 CAD/month x 6 = $2,994

---

### Disaster Recovery Runbook (Phase 2)

**Scenario 1: API service down (Container App):**

```bash
# 1. Check health endpoint
curl https://aca-api.canadacentral.azurecontainerapps.io/health

# 2. View logs
az containerapp logs show --name aca-api --resource-group aca-prod-canadacentral --tail 100

# 3. Roll back to previous revision
az containerapp revision list --name aca-api --resource-group aca-prod-canadacentral
az containerapp revision activate --name aca-api --revision aca-api--<previous-revision>

# 4. Verify
curl https://aca-api.canadacentral.azurecontainerapps.io/health
```

**Scenario 2: Cosmos DB region failure:**

```bash
# 1. Check Cosmos health
az cosmosdb show --name aca-cosmos-prod --resource-group aca-prod-canadacentral --query "failoverPolicies"

# 2. Manual failover (if automatic failover didn't trigger)
az cosmosdb failover-priority-change \
  --name aca-cosmos-prod \
  --resource-group aca-prod-canadacentral \
  --failover-policies canadaeast=0 canadacentral=1

# 3. Update API connection string (if needed)
az containerapp update --name aca-api --set-env-vars COSMOS_URL=https://aca-cosmos-prod-canadaeast.documents.azure.com
```

**Scenario 3: Data corruption (accidental delete):**

```bash
# 1. Identify last known good timestamp
# Example: findings container was corrupted at 2026-03-01T14:30:00Z

# 2. PITR restore (35-day window)
az cosmosdb restore \
  --account-name aca-cosmos-prod \
  --target-database-account-name aca-cosmos-prod-restored \
  --resource-group aca-prod-canadacentral \
  --restore-timestamp "2026-03-01T14:00:00Z" \
  --databases-to-restore name=aca-db collections=findings

# 3. Verify restored data
# 4. Swap restored account with production (manual cutover)
```

---

### Migration Strategy (Phase 1 -> Phase 2)

**Pre-migration checklist:**
- [ ] Phase 2 Terraform provisioned (all resources green)
- [ ] DNS CNAME prepared (aca.example.com -> aca-apim-prod.azure-api.net)
- [ ] TLS cert installed (custom domain)
- [ ] Container images pushed to aca-acr-prod
- [ ] Key Vault secrets populated (all 6 secrets)
- [ ] Cosmos containers created (schema validated)
- [ ] Data migration pipeline tested (dry run on 10 subscriptions)

**Migration sequence (cutover weekend):**

```
Friday 6pm ET:
  - Announce maintenance window (email to Tier 2+ customers)
  - Disable nightly auto-refresh cron (prevent collection during migration)

Saturday 8am ET:
  - STEP 1: Data snapshot from Phase 1 Cosmos
    az cosmosdb sql container export \
      --account-name marco-sandbox-cosmos \
      --database aca-db \
      --container findings \
      --output aca-findings-export.json

  - STEP 2: Copy to Phase 2 Cosmos (6 containers x avg 100 MB = 600 MB)
    az cosmosdb sql container import \
      --account-name aca-cosmos-prod \
      --database aca-db \
      --container findings \
      --input aca-findings-export.json
    # Repeat for scans, inventories, cost-data, advisor, entitlements

  - STEP 3: Validate row counts
    az cosmosdb sql container query \
      --account-name aca-cosmos-prod \
      --database aca-db \
      --container findings \
      --query "SELECT VALUE COUNT(1) FROM c"
    # Compare with Phase 1 counts

  - STEP 4: Deploy Phase 2 Container Apps (images already pushed)
    terraform apply -var-file=production.tfvars

  - STEP 5: Smoke test Phase 2 API (internal VNET IP)
    curl -H "Host: aca-api.internal" https://10.0.1.10/health

Saturday 2pm ET:
  - STEP 6: Update DNS CNAME (TTL=300, 5-min propagation)
    aca.example.com CNAME aca-apim-prod.azure-api.net

  - STEP 7: Wait 10 minutes (DNS propagation)

  - STEP 8: Verify public access
    curl https://aca.example.com/health

  - STEP 9: Test full user flow (login -> scan -> findings)
    # Manual QA: 3 test subscriptions (Tier 1, Tier 2, Tier 3)

Saturday 4pm ET:
  - STEP 10: Re-enable nightly cron (Phase 2 infrastructure)

  - STEP 11: Monitor for 2 hours (Application Insights dashboards)
    # Check: API latency, Cosmos throttling, job success rate

Saturday 6pm ET:
  - STEP 12: Announce cutover complete (status page + email)

Sunday (monitoring day):
  - Monitor Cost Management (validate tags, cost attribution)
  - Monitor Application Insights (no errors, acceptable latency)

Monday (1 week post-cutover):
  - Review logs for anomalies
  - Confirm Stripe webhooks working (payment unlock Tier 2/3)
  - Validate backup/restore (test PITR on non-production container)

Friday (1 week post-cutover):
  - DECOMMISSION Phase 1 resources (if no rollback needed)
    terraform destroy -var-file=infra/phase1-marco/main.bicepparam
    # Keep ADO PAT in marco KV for historical reference
```

**Rollback plan (if critical failure detected):**
1. Revert DNS CNAME (5-min TTL, instant rollback)
2. Phase 1 resources still running (not decommissioned until 1 week post-cutover)
3. No data loss (Phase 1 Cosmos unchanged, Phase 2 data discarded)

---

## OBSERVABILITY PATTERNS

### Application Insights (Phase 1)

**Instrumentation:**
- FastAPI: `ApplicationInsightsMiddleware` (automatic request tracing)
- Python logging: `structlog` -> App Insights custom events

**Custom metrics:**
- `scan_duration_seconds` (job execution time)
- `findings_count` (per subscription)
- `api_request_duration_ms` (from TimingMiddleware)

**Queries (Kusto):**

```kql
// API latency p95
requests
| where timestamp > ago(1h)
| summarize percentile(duration, 95) by operation_Name
| order by percentile_duration_95 desc

// Failed jobs
traces
| where message contains "scan_failed"
| project timestamp, subscription_id=customDimensions.subscription_id, error_code=customDimensions.error_code
| order by timestamp desc
```

---

### Log Analytics (Phase 2)

**90-day retention:**
- All Container App logs
- Cosmos DB diagnostics (429 errors, RU consumption)
- APIM gateway logs

**Workbooks:**
- "ACA Tenant Usage" (scans per subscription, findings distribution)
- "ACA Performance" (API latency, Cosmos throttling, job success rate)
- "ACA Cost Attribution" (RU consumption by subscription)

**Alerts:**
- Cosmos 429 (throttling) -> PagerDuty
- API 5xx rate > 1% -> Email on-call
- Job failure rate > 10% -> Email on-call

---

## RELATED DOCUMENTS

- [Application Architecture](./application-architecture.md) -- component design
- [Solution Architecture](./solution-architecture.md) -- business context
- [Security Architecture](./security-architecture.md) -- threat model
- [PLAN.md](../../PLAN.md) -- WBS, story backlog
- [18-azure-best](../../18-azure-best/README.md) -- Terraform modules source

---

END OF INFRASTRUCTURE ARCHITECTURE
