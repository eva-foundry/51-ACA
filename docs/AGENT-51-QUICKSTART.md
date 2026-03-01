# Agent 51: FinOps Engagement Model — Quick Reference

**Document**: Quick startup guide for executing FinOps consulting engagements  
**For**: Agent 51 (51-ACA team)  
**Status**: Ready to use; customize per engagement  
**Main Playbook**: `/51-ACA/docs/finops-engagement-model.md`

---

## TL;DR: 5-Week Engagement Flow

```
WEEK 1      WEEK 2-3         WEEK 4           WEEK 5
PRE-FLIGHT  DATA EXTRACTION  DATA SCIENCE     SERVICE MENU     DELIVERY
├─ Assess   ├─ Inventory     ├─ EDA           ├─ Define 8      ├─ Deploy
│  roles    │  pull          │  profile        │  services      │  services
├─ Confirm  ├─ Cost data     ├─ Savings       ├─ Price each    ├─ Train
│  scope    │  (90 days)      │  analysis      │  service        │  client
└─ Get      ├─ Load to       └─ Generate      └─ Client        └─ Handoff
   approval │  database         report          picks           (30d
            └─ Validate       (tailored to                       support)
               data quality    their sub)

DELIVERABLES:
1. Permission Matrix (client sign-off)
2. Cost Database (populated, queryable)
3. Savings Report (client-specific + baseline)
4. Service Menu (with pricing + code)
5. Deployed Services + Training

EFFORT: ~20 days; parallelizable (can compress to 3-4 weeks)
COST: $14-17K setup + $300-$1,500/month per service
PAYBACK: 2-6 months (depending on services chosen)
```

---

## Phase-by-Phase: What You Do Each Week

### PHASE 1: Pre-Flight (Week 1)

**Your Checklist**:
1. ✅ Get subscription ID, client contact, access
2. ✅ Create Azure session; query `Get-AzRoleAssignment`
3. ✅ Map actual roles against required roles (template: `PHASE1-ROLE-ASSESSMENT.ps1`)
4. ✅ Fill out `CLIENT-SCOPE-CONFIRMATION.md`
5. ✅ Get client sign-off on scope + gaps
6. ✅ Confirm 90-day cost data available (check Cost Mgmt export dates)

**Template Location**: `/51-ACA/scripts/phase1-role-assessment.ps1` (create from playbook)

**You Need**: 
- Client's subscription ID
- Your Azure credentials (with Cost Management Reader role)
- 4 hours

---

### PHASE 2: Data Extraction & Loading (Weeks 1-2, parallelizable with Phase 1)

**Your Checklist**:
1. ✅ Spin up PostgreSQL database (Azure Database for PostgreSQL; $50/month small SKU)
   - Connection string: `Server=...; Database=finops; User=finops-user@...;`
2. ✅ Run inventory extraction script (⏱️ 30 min)
   ```powershell
   pwsh -File ./scripts/phase2-inventory-extraction.ps1 -SubscriptionId [ID] -OutputPath ./inventory-extracts
   ```
3. ✅ Extract 90-day cost data (⏱️ 1-2 hours, can be slow via API)
   - Method 1: REST API (recommended; handles pagination)
   - Method 2: Portal exports (manual; guaranteed to work)
   - Reference: `/14-az-finops/scripts/Backfill-Costs-REST.ps1`
4. ✅ Validate cost data sum vs Azure Portal (must match within 1%)
5. ✅ Load data to PostgreSQL (⏱️ 30 min)
   - Run `phase2-load-database.py`
   - Verify row counts + data distribution

**Output You'll Have**:
- CSV files (inventory, costs, recommendations)
- PostgreSQL database populated with schema (📊 ready for analytics)

**You Need**:
- Azure CLI or PowerShell (to extract)
- Python + pandas (to load)
- PostgreSQL client (to verify)
- 6-8 hours total

---

### PHASE 3: Data Science & Discovery (Weeks 2-3)

**Your Checklist**:
1. ✅ Run EDA script (⏱️ 2-3 hours)
   ```python
   python ./scripts/phase3-eda.py --db finops.db --output ./eda-report
   ```
   - Output: Baseline metrics JSON + visualization PNGs
2. ✅ Identify anomalies (visual inspection of z-score report)
3. ✅ Pull Cost Advisor recommendations from database
4. ✅ Generate `savings-opportunities.md` (customize template)
   - Use `phase3-generate-savings-report.py`
   - Replace [SUB_NAME], [COST_FIGURES], [TIMELINES]
5. ✅ Review with client: any surprises or missed savings?

**Output You'll Have**:
- **savings-opportunities.md** (fully tailored to their subscription)
- Anomaly list (with dates + z-scores)
- EDA report (JSON: cost profile, trends, tag quality)

**You Need**:
- Python + scipy/numpy/pandas
- SQL query knowledge (queries provided in template)
- 5-6 hours

---

### PHASE 4: Service Menu & Pricing (Week 4)

**Your Checklist**:
1. ✅ Decide which 8 services to offer (template: `SERVICE-MENU-TEMPLATE.md`)
   - Core: Anomaly Detection + Cost Forecasting (highest ROI)
   - Optional: Chargeback + Right-Sizing (if applicable to their sub)
   - Check: Do they have APIM? Offer APIM cost attribution
2. ✅ For EACH service, create:
   - Service spec (what you do, deliverables, support SLA)
   - Setup cost estimate (days × $150/hr)
   - Recurring cost (monthly + what's included)
   - Test scenario (how you'd test it)
3. ✅ Bundle pricing (Starter/Professional/Enterprise)
   - Starter: Anomaly + Forecasting = $5.5K setup + $800/mo
   - Professional: + Chargeback + Right-Sizing = $12.5K + $1,800/mo
   - Enterprise: All + 4h/month dedicated support = custom quote
4. ✅ Create service menu (PowerPoint or PDF) for client review
5. ✅ Schedule proposal meeting (30 min walkthrough)

**Output You'll Have**:
- Service Menu catalog (PDF, ready to email)
- Pricing matrix
- Service implementation checklists (ready for Phase 5)

**You Need**:
- Client's problem domain (hint: use savings opportunities report)
- Pricing template from engagement model
- 8-10 hours

---

### PHASE 5: Deploy & Handoff (Week 5)

**Your Checklist** (per service selected):
1. ✅ **Anomaly Detection Service** (if selected)
   - Deploy ADX cluster + KQL rules
   - Setup Slack bot alerts
   - Test: Trigger alert manually; confirm Slack message
   - Deliver: Runbook + training video
2. ✅ **Cost Forecasting Service** (if selected)
   - Load 12-month historical data
   - Train ARIMA model
   - Build Power BI dashboard
   - Test: Forecast month N+1; validate against actuals
   - Deliver: Dashboard access + user guide
3. ✅ **Chargeback Service** (if selected)
   - Design allocation model (with client's finance team)
   - Build chargeback invoice template
   - Automate monthly generation
   - Test: Generate Month 1 invoice; reconcile
   - Deliver: Finance user training + SAP integration runbook
4. ✅ Deliver all services
5. ✅ Train client (1-2 hours per service)
6. ✅ Start 30-day support window (calendar reminder)

**Output You'll Have**:
- Fully deployed services
- Documentation (runbooks, FAQs, user guides)
- Client knowledge transfer (trained staff)
- Support schedule (30 days included; then $150/hr overages)

**You Need**:
- Code from Phase 4 implementation checklist
- Time: 40-60 hours (depends on service complexity)

**Quality Gate**: Before handoff, confirm:
- [ ] All services tested end-to-end
- [ ] Client can access all dashboards/tools
- [ ] Documentation is complete + understandable
- [ ] Support contact info + SLA provided
- [ ] Next renewal discussion scheduled

---

## Point-in-Time Reference: What You Have Available

### From Project 14 (Proven Code & Patterns)

| Asset | What It Does | Phase | Path | Status |
|---|---|---|---|---|
| **az-inventory-finops.ps1** | Pulls all Azure resources from subscription | 2 | `/14-az-finops/tools/finops/` | ✅ Tested, 650 lines |
| **extract_costs_sdk.py** | Cost Mgmt API via Python SDK | 2 | `/14-az-finops/scripts/` | ⚠️ Pagination bug >5K rows (use REST API instead) |
| **Backfill-Costs-REST.ps1** | Cost Mgmt API via REST (pagination works) | 2 | `/14-az-finops/scripts/` | ✅ Tested, recommended |
| **Database schema** | Optimized tables + materialized views | 2 | `/14-az-finops/docs/finops/02-target-architecture.md` | ✅ Production-ready |
| **KQL templates** | Anomaly detection, cost by tag, etc. | 3-4 | `/14-az-finops/scripts/kql/` | ✅ 20+ queries |
| **saving-opportunities.md** | Model for client-specific report | 3 | `/14-az-finops/docs/saving-opportunities.md` | ✅ Template |
| **ADVANCED-CAPABILITIES-SHOWCASE.md** | 12 analytics + service ideas | 4 | `/14-az-finops/docs/` | ✅ Inspiration |

### From Project 18: Azure Best Practices

| Asset | What It Has | Why It Matters | Path |
|---|---|---|---|
| **RBAC best practices** | Role design, least privilege | Pre-flight assessment | `/18-azure-best/12-security/rbac.md` |
| **Cost optimization pillar** | Official FinOps patterns | Service design | `/18-azure-best/02-well-architected/cost-optimization.md` |
| **AI security** | If client has OpenAI/Foundry | Service bundling | `/18-azure-best/04-ai-workloads/` |

### Data Science Tools (Install First)

```powershell
# Python environment setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install pandas numpy scipy matplotlib statsmodels scikit-learn
pip install azure-identity azure-costmanagement
pip install reportlab psycopg2-binary  # for PDF + PostgreSQL
```

### Database Setup (Choose One)

| DB | Setup Time | Cost | Scale | Recommendation |
|---|---|---|---|---|
| **SQLite** | 5 min | $0 | <1GB | PoC / small subs |
| **PostgreSQL (Azure)** | 2 hrs | $40-200/mo | 10GB+ | **RECOMMENDED** |
| **Cosmos DB** | 1 hr | $$$ | Infinite | Overkill (unless already have) |

**Quick Setup (PostgreSQL)**:
```powershell
# Create via Azure Portal OR CLI
az postgres flexible-server create `
  --resource-group [RG] `
  --name finops-[client-name] `
  --admin-user finops-user `
  --tier Burstable --sku-name Standard_B1ms `
  --storage-db 32 `
  --public-access all

# Import schema
psql -h finops-[client-name].postgres.database.azure.com \
     -U finops-user@finops-[client-name] \
     -d finops \
     -f /51-ACA/schema.sql
```

---

## Quick Decision Tree: Which Service Should I Offer?

```
Q1: Does the subscription have anomalies in cost history?
    ├─ YES → Offer ANOMALY DETECTION SERVICE (ROI: prevent $100K+ incidents)
    └─ NO → Skip (or offer quarterly review alternative)

Q2: Does the client have budget planning cycles or growth plans?
    ├─ YES → Offer COST FORECASTING SERVICE (ROI: accurate budget for 12-month)
    └─ NO → Skip (or offer on-demand forecasting)

Q3: Multi-tenant or cost center chargeback needed?
    ├─ YES → Offer CHARGEBACK SERVICE (ROI: process automation + accountability)
    ├─ MAYBE → Offer as Phase 2 optional
    └─ NO → Skip

Q4: Many VMs or databases with variable usage?
    ├─ YES → Offer RIGHT-SIZING SERVICE (ROI: 8-15% compute savings)
    └─ NO → Skip

Q5: ESG / sustainability initiative?
    ├─ YES → Offer CARBON REPORTING (ROI: compliance + board narrative)
    └─ NO → Skip

Q6: Have OpenAI, Cognitive Search, or other expensive APIs?
    ├─ YES → Offer APIM COST ATTRIBUTION (if they have APIM gateway)
    └─ NO → Skip

COMMON BUNDLES:
├─ Startup (any sub): Anomaly Detection + Forecasting [$5.5K setup + $800/mo]
├─ Enterprise (>$50K/mo): All services + dedicated support [custom quote]
└─ Custom: Pick 2-3 based on their needs
```

---

## Pricing Quick Reference

**Setup Costs** (one-time):
```
Anomaly Detection Service:  $3,500 (3 days)
Cost Forecasting:          $4,000 (5 days)
Chargeback Service:         $6,000 (10 days)
Right-Sizing Service:       $5,000 (7 days)
Sustainability:             $3,500 (5 days)
```

**Recurring Costs** (per month):
```
Anomaly Detection:          $800/mo
Cost Forecasting:           $600/mo
Chargeback Service:         $1,200/mo
Right-Sizing Service:       $400/mo + implementation hours
Sustainability:             $300/mo
```

**Bundle Discount Strategy**:
- Starter (2 services): Base pricing (no discount)
- Professional (4 services): -10% monthly recurring
- Enterprise (all + support): -15% monthly + dedicated account manager

---

## Before You Start: Checklist

- [ ] Have you read `/51-ACA/docs/finops-engagement-model.md` in full?
- [ ] Do you have access to project 14 scripts (`/14-az-finops/scripts/`)?
- [ ] Python environment set up (pandas, numpy, scipy installed)?
- [ ] PostgreSQL client installed (`psql` or DBeaver)?
- [ ] ADO project created for engagement (to track work)?
- [ ] Git repo cloned (for version control of scripts/data)?
- [ ] Client's subscription ID + contact info documented?

---

## Emergency Contacts

| Question | Who To Ask | How |
|---|---|---|
| "How do I extract cost data again?" | Marco (14-az-finops owner) | marco.presta@hrsdc-rhdcc.gc.ca |
| "Can I reuse this KQL query?" | Marco | Same email |
| "What's the pricing for similar engagement?" | Leadership | ADO query historical quotes |
| "Client wants custom service?" | Design with Marco | Start with service template + modify |

---

## Success Metrics

After 5 weeks, you should have delivered:

✅ **Phase 1**: Permission matrix + client sign-off  
✅ **Phase 2**: Populated database (500K+ cost records, validated)  
✅ **Phase 3**: Client-specific savings report ($XXK identified opportunity)  
✅ **Phase 4**: Service menu (8 services, priced, client reviewed)  
✅ **Phase 5**: 1-3 services deployed + trained  

**Client happiness indicator**: "We didn't know we could do that with our data."

---

## What's Different from One-Off Consulting?

| Aspect | One-Off | Engagement Model |
|---|---|---|
| **Scope** | Ad-hoc questions | Structured 5-phase framework |
| **Data** | Client tells us | We extract systematically |
| **Analysis** | Single question | Comprehensive discovery |
| **Deliverables** | Report + email | Database + services + training |
| **Support** | Done after handoff | 30 days included |
| **Renewal** | One-time | Recurring services (ongoing) |
| **Price** | $3-5K | $14K setup + $300-1.5K/mo |
| **ROI** | Cost savings identified | Cost savings + operational automation |

---

**Ready to execute?** Start with Phase 1 (approval letter + scope document) and follow the playbook!

Questions? Ask Marco or post in ADO engagement board.
