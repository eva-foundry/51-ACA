# Project 51: FinOps Consulting Engagement — Complete Resource Index

**Last Updated**: March 1, 2026  
**Status**: Ready for Agent 51 to execute engagements  
**Audience**: Project 51 team (operations, data scientists, consultants)

---

## 📍 Where to Start

1. **First time?** Read in order:
   - **This file** (you are here) — overview + navigation
   - `/51-ACA/docs/AGENT-51-QUICKSTART.md` (2,000 words, 20 min read)
   - `/51-ACA/docs/finops-engagement-model.md` (7,500 words, full playbook)

2. **Starting a new engagement?** Bookmark this:
   - **AGENT-51-QUICKSTART.md** — Use for weekly reference
   - **finops-engagement-model.md** — Deep dive when needed

3. **Need to do a specific task?** Jump to the checklist:
   - Phase 1 role assessment → Section 2.1 below
   - Extract cost data → Section 2.2 below
   - Generate savings report → Section 2.3 below
   - Design service menu → Section 2.4 below
   - Deploy service → Section 2.5 below

---

## 🎯 What This Engagement Model Solves

| Problem | Solution | Where |
|---|---|---|
| "We offer generic consulting, no process" | 📋 Structured 5-phase engagement framework | finops-engagement-model.md |
| "Don't know what to charge" | 💰 Tiered pricing model (setup + recurring) | finops-engagement-model.md §4.1 |
| "Can't extract Azure data reliably" | 🔧 Tested scripts from project 14 | finops-engagement-model.md §2.1 |
| "Database design uncertain" | 📊 Production schema (PostgreSQL) | finops-engagement-model.md §2.2 |
| "Don't know what to analyze" | 📈 EDA template + anomaly detection | finops-engagement-model.md §3.1 |
| "How to position services to clients?" | 🛍️ Service menu with specs + pricing | finops-engagement-model.md §4.1 |
| "How do I deliver services?" | ✅ Deployment checklists per service | finops-engagement-model.md §5.1 |
| "Too intimidating to start" | 🚀 Quickstart guide with decision trees | AGENT-51-QUICKSTART.md |

---

## 📚 Complete Document Map

### Main Engagement Playbook

**File**: `/51-ACA/docs/finops-engagement-model.md` (1,427 lines)

| Section | Topic | Use Case |
|---|---|---|
| **Overview** | 5-phase flow diagram | Understand the overall process (10 min) |
| **1.1-1.2** | Pre-flight assessment + scope confirmation | Before client engagement (Day 1-2) |
| **2.1** | Inventory extraction playbook | Extract Azure resources (Day 3-5) |
| **2.1.2** | Cost data extraction (90-day historical) | Pull billing data (Day 5-7) |
| **2.2** | PostgreSQL database schema | Load data, run analytics (Day 7-9) |
| **3.1** | EDA template + Python code | Data profiling (Day 10-11) |
| **3.2** | Generate savings-opportunities report | Client-specific analysis (Day 12-14) |
| **4.1** | Service catalog (8 services) | Define what you offer (Day 15-18) |
| **4.1** | Pricing model (setup + recurring) | Price your services (Day 18-20) |
| **5.1** | Deployment checklist per service | Deploy after client approves (Day 21-35) |

### Quick Reference Guide

**File**: `/51-ACA/docs/AGENT-51-QUICKSTART.md` (368 lines)

| Section | Content | Use Case |
|---|---|---|
| **TL;DR Flow** | 5-week timeline visual | 30-second overview |
| **Phase-by-Phase** | Weekly checklist + what to do | Execute each week |
| **Point-in-Time Resources** | Where to find reusable code | During execution |
| **Service Decision Tree** | Which services to offer | During Phase 4 |
| **Pricing Quick Ref** | Setup + monthly costs | When quoting |
| **Before-You-Start** | Prerequisites + tools | Pre-engagement |
| **Success Metrics** | What "done" looks like | Handoff readiness |

### Supporting Documentation (Project 14 Reference)

**Path**: `/14-az-finops/`

| Asset | What It Does | Phase | Status |
|---|---|---|---|
| `docs/saving-opportunities.md` | Example savings report (model to follow) | 3 | ✅ Template |
| `docs/ADVANCED-CAPABILITIES-SHOWCASE.md` | 12 analytics services (inspiration) | 4 | ✅ Reference |
| `tools/finops/az-inventory-finops.ps1` | Extract all Azure resources (650 lines) | 2 | ✅ Tested |
| `scripts/Backfill-Costs-REST.ps1` | Extract 90-day cost data (pagination works) | 2 | ✅ Tested |
| `scripts/extract_costs_sdk.py` | Alternative: Python SDK (slower) | 2 | ⚠️ Bug >5K rows |
| `docs/finops/02-target-architecture.md` | Database schema + KQL templates | 2-3 | ✅ Production |
| `scripts/kql/*.kql` | 20+ KQL queries (anomaly, cost by tag, etc.) | 3-4 | ✅ Tested |

---

## 🔧 Reusable Code & Scripts (You Don't Have to Write from Scratch)

### From Project 14

1. **Inventory Extraction** (Phase 2.1.1)
   ```powershell
   # Copy & customize:
   cp /14-az-finops/tools/finops/az-inventory-finops.ps1 \
      /51-ACA/scripts/phase2-inventory-extraction.ps1
   # Then: Update subscription ID, output paths
   ```
   - What it pulls: VMs, App Services, Storage, Networking, RBAC, tags
   - Output: CSV files ready for database import
   - Time: 30 minutes execution

2. **Cost Data Extraction** (Phase 2.1.2)
   ```powershell
   # Recommended: REST API (handles pagination)
   cp /14-az-finops/scripts/Backfill-Costs-REST.ps1 \
      /51-ACA/scripts/phase2-cost-extraction.ps1
   # Fallback: Python SDK (slower, but easier to understand)
   cp /14-az-finops/scripts/extract_costs_sdk.py \
      /51-ACA/scripts/phase2-cost-extraction.py
   ```
   - What it extracts: 90-day daily cost records (55+ columns)
   - Output: CSV ready for PostgreSQL
   - Time: 1-2 hours (API calls + download)

3. **Database Schema** (Phase 2.2)
   ```sql
   -- Copy schema from:
   # Document: /14-az-finops/docs/finops/02-target-architecture.md
   # Creates: 
   #   - resources table (all Azure resources)
   #   - daily_costs table (daily cost records)
   #   - cost_tags table (normalized tags)
   #   - Materialized views for fast analytics
   ```
   - Tables: resources, daily_costs, cost_tags, cost_advisor_recommendations
   - Views: v_daily_cost_by_service_date, v_cost_by_resource_group, v_cost_by_tag
   - Time: 30 minutes setup (copy SQL, run in PostgreSQL)

4. **KQL Anomaly Detection Queries** (Phase 4.1, if offering anomaly service)
   ```kql
   // Copy from: /14-az-finops/scripts/kql/
   // Examples:
   //   - 04-anomaly-detection.kql (z-score based)
   //   - 05-cost-trend-by-service.kql
   //   - 06-resource-efficiency.kql
   ```
   - Use as baseline; customize thresholds, time windows
   - Time: 30 minutes (search + copy + test)

### Templates You Need to Create

| Template | Phase | Create From | Time |
|---|---|---|---|
| `scripts/phase1-role-assessment.ps1` | 1 | Pseudocode in playbook | 1 hr |
| `docs/CLIENT-SCOPE-CONFIRMATION.md` | 1 | Markdown template in playbook | 30 min |
| `scripts/phase2-load-database.py` | 2 | Python pseudocode in playbook | 2 hrs |
| `scripts/phase3-eda.py` | 3 | Python pseudocode in playbook | 3-4 hrs |
| `scripts/phase3-generate-savings-report.py` | 3 | Python pseudocode in playbook | 3-4 hrs |

---

## 💾 Technology Stack (What You Need to Install)

### Local Development

```powershell
# PowerShell (for inventory + cost extraction)
# Already installed on Windows

# Python (for data loading + EDA)
python --version  # Need 3.10+
pip install pandas numpy scipy matplotlib statsmodels scikit-learn
pip install azure-identity azure-costmanagement reportlab

# Database Client
# Option 1: DBeaver (GUI)
# Option 2: psql (CLI)
```

### Cloud Infrastructure (What the Client Needs)

```
Client's Subscription:
├─ Azure Database for PostgreSQL (Small SKU: ~$50/month)
│   └─ Schema: /51-ACA/schema.sql
├─ App Insights (if offering anomaly alerts)
├─ Log Analytics (for KQL queries)
└─ Optional: ADX cluster (if >100M records)

Your Infrastructure (51-ACA):
├─ GitHub repo (git clone project 51)
├─ Local or cloud file storage (for reports/extracts)
└─ Optional: Your own Analytics database (aggregate multi-client insights)
```

---

## 📋 Phase Checklists (Copy-Paste Ready)

### Phase 1: Pre-Flight (Week 1)

```markdown
## Pre-Flight Checklist — [CLIENT_NAME]

- [ ] Received subscription ID
- [ ] Received client contact info (name, email, phone)
- [ ] Created Azure session (az login)
- [ ] Queried `Get-AzRoleAssignment` on subscription
- [ ] Mapped actual roles vs required roles
  - [ ] Cost Management Reader — Have? ___ Required? YES
  - [ ] Billing Reader — Have? ___ Required? YES
  - [ ] Reader — Have? ___ Required? YES
  - [ ] Monitoring Reader — Have? ___ Optional
  - [ ] Role gaps escalated to client
- [ ] Created `CLIENT-SCOPE-CONFIRMATION.md`
- [ ] Got client sign-off (email confirmation)
- [ ] Confirmed 90-day cost data available in Cost Management
- [ ] Scheduled Phase 2 kickoff call
```

### Phase 2: Data Extraction (Weeks 1-2)

```markdown
## Data Extraction Checklist — [CLIENT_NAME]

- [ ] PostgreSQL instance spun up (connection string: _____)
- [ ] Database schema loaded (tables + views created)
- [ ] Inventory extraction script run
  ```powershell
  pwsh -File ./scripts/phase2-inventory-extraction.ps1 \
    -SubscriptionId [SUB_ID] -OutputPath ./inventory-extracts
  ```
  - [ ] Output CSVs generated: inventory-vms.csv, inventory-storage.csv, etc.
  - [ ] Manifest.json created
- [ ] Cost data extraction run
  ```powershell
  # Method 1: REST API (recommended)
  pwsh -File ./scripts/phase2-cost-extraction.ps1
  # Expected output: costs-daily-[DATE].csv (~10-50MB)
  ```
  - [ ] CSV generated
  - [ ] Row count: _____ (expect 1K-50K rows)
  - [ ] Date range: _____ to _____
- [ ] Data validation: Sum of CSV = Portal reported cost (within 1%)
  - [ ] Validation passed? YES / NO / Investigate
- [ ] Data loaded to PostgreSQL
  ```python
  python ./scripts/phase2-load-database.py
  ```
  - [ ] Row counts match source CSVs
  - [ ] No import errors
- [ ] Database queries tested:
  - [ ] SELECT COUNT(*) FROM daily_costs (expect: _____)
  - [ ] SELECT DISTINCT DATE FROM daily_costs (date range: _____)
  - [ ] SELECT * FROM resources LIMIT 5 (sample rows returned)
- [ ] Cost Advisor recommendations extracted (if available)
- [ ] Phase 3 data handoff complete
```

### Phase 3: Data Science (Weeks 2-3)

```markdown
## Discovery Checklist — [CLIENT_NAME]

- [ ] EDA script run
  ```python
  python ./scripts/phase3-eda.py
  ```
  - [ ] EDA report JSON generated: eda-report.json
  - [ ] Visualizations created (PNG files)
- [ ] Baseline metrics captured:
  - [ ] Total spend (90 days): $______
  - [ ] Annualized run-rate: $______
  - [ ] Service breakdown (top 5): _____
- [ ] Anomalies identified (z-score > 3.0):
  - [ ] Any anomalies found? YES / NO
  - [ ] If YES: Date, cost, z-score: _______________
- [ ] Tag quality assessed:
  - [ ] % of cost tagged with key dimensions: ____%
  - [ ] Untagged cost: $_____ (target: < 1%)
- [ ] Savings opportunities identified:
  - [ ] Number of opportunities: _____
  - [ ] Total potential saving: $_______
- [ ] `savings-opportunities.md` generated
  - [ ] Customized to subscription (not template)
  - [ ] Includes: Baseline + top 5-7 quick wins + effort estimates
  - [ ] Ranked by effort/impact
- [ ] Client review scheduled (30 min walkthrough)
```

### Phase 4: Service Menu (Week 4)

```markdown
## Service Menu Checklist — [CLIENT_NAME]

- [ ] Identified 8-10 candidate services (from ADVANCED-CAPABILITIES)
- [ ] For each service, defined:
  - [ ] What we do (1-2 paragraphs)
  - [ ] Deliverables (list)
  - [ ] Setup cost (setup days × $150/hr)
  - [ ] Recurring cost ($/month + what's included)
  - [ ] SLA (response time, uptime, etc.)
  - [ ] Implementation checklist (ready for Phase 5)
- [ ] Service decision tree followed (AGENT-51-QUICKSTART.md)
  - [ ] Recommended 3-4 services for client
- [ ] Bundle pricing calculated:
  - [ ] Starter bundle: $_____ setup + $___/mo
  - [ ] Professional bundle: $_____ setup + $___/mo
  - [ ] Enterprise bundle: Custom quote
- [ ] Service menu PDF created (ready to send)
- [ ] Proposal meeting scheduled (30-45 min)
- [ ] Client feedback captured: Which services approved?
  - [ ] Service 1: [NAME] — APPROVED / PENDING / REJECTED
  - [ ] Service 2: [NAME] — APPROVED / PENDING / REJECTED
  - [ ] Service 3: [NAME] — APPROVED / PENDING / REJECTED
- [ ] Phase 5 implementation plan created (per service)
```

### Phase 5: Deployment (Week 5)

```markdown
## Deployment Checklist — [CLIENT_NAME]

### For Each Approved Service:

#### [SERVICE_NAME]
- [ ] Code developed and tested locally
- [ ] Deployment runbook created
- [ ] Client infrastructure provisioned (if needed)
  - [ ] Example: ADX cluster, Power BI workspace, etc.
- [ ] Service deployed to client environment
- [ ] End-to-end test passed:
  - [ ] Input: _____ (e.g., historical cost data)
  - [ ] Output: _____ (e.g., anomaly alerts)
  - [ ] Expected vs actual: Match / Mismatch (investigate)
- [ ] Client training performed (1-2 hours)
  - [ ] Attendees: _____
  - [ ] Topics covered: _____
  - [ ] Q&A captured
- [ ] Documentation provided:
  - [ ] User guide (how to access/use the service)
  - [ ] Runbook (operational procedures)
  - [ ] FAQ (common questions + answers)
  - [ ] Support contact info (email + phone)
- [ ] Support SLA documented:
  - [ ] Response time: _____ (e.g., 4 hours)
  - [ ] Resolution time: _____ (e.g., 1 business day)
  - [ ] Escalation path: _____

### Final Handoff

- [ ] ALL services deployed + tested
- [ ] Client can access all dashboards/tools independently
- [ ] 30-day support window started (calendar reminder set)
- [ ] Welcome email sent (support contact details)
- [ ] Day 7 check-in scheduled (how's it going?)
- [ ] Day 30 renewal discussion scheduled
- [ ] Feedback survey sent to client
```

---

## 📊 Pricing Template (Copy-Paste)

```markdown
# Pricing Proposal — [CLIENT_NAME]

## Setup Costs (One-Time)

| Service | Effort | Cost |
|---|---|---|
| Anomaly Detection | 3 days | $3,500 |
| Cost Forecasting | 5 days | $4,000 |
| Chargeback Service | 10 days | $6,000 |
| Right-Sizing | 7 days | $5,000 |
| **Subtotal** | | |

## Recurring Costs (Monthly)

| Service | Effort (per month) | Cost |
|---|---|---|
| Anomaly Detection | 4h support + maintenance | $800 |
| Cost Forecasting | 3h support + refresh | $600 |
| Chargeback Service | 5h invoice + support | $1,200 |
| Right-Sizing | 2h + impl hours ($150/hr) | $400+ |
| **Subtotal** | | |

## Recommended Bundle

**Professional Tier** (3-4 services)
- Anomaly Detection + Cost Forecasting + Right-Sizing Quarterly
- Setup: $12,500
- Monthly: $1,800
- Includes: 30-day support + monthly review call
```

---

## 🚀 From Here: Next Steps for Agent 51

**Today**:
1. Read `/51-ACA/docs/AGENT-51-QUICKSTART.md` (20 min)
2. Skim `/51-ACA/docs/finops-engagement-model.md` (1 hr)
3. Bookmark both files

**When first client arrives**:
1. Read full playbook (cover to cover, 2-3 hrs)
2. Create project folder: `/51-ACA/engagements/[CLIENT_NAME]/`
3. Copy templates from playbook into project folder
4. Start Phase 1 (role assessment)
5. Reference quickstart guide weekly

**Reusing for second client**:
1. Copy successful scripts from Client 1 engagement
2. Customize for Client 2's subscription ID
3. Follow same 5-phase process
4. Build a library of reusable scripts (faster each time)

---

## 📞 Support & Questions

| Question | Answer | Who |
|---|---|---|
| "Where's the code for [PHASE]?" | finops-engagement-model.md § [PHASE] | Playbook |
| "How do I quote pricing?" | finops-engagement-model.md §4.1 + template | Playbook |
| "Can I reuse project 14 scripts?" | YES — `/14-az-finops/scripts/` | Project 14 |
| "What's the database schema?" | finops-engagement-model.md §2.2 | Playbook |
| "My client wants custom services?" | Design with Marco; use service template | Marco P. |
| "Which services should I offer?" | AGENT-51-QUICKSTART.md decision tree | Quickstart |

---

## ✅ Success = This Is What Good Looks Like

After 5 weeks, you've handed off to client:

- ✅ Comprehensive cost analysis (baseline + trends)
- ✅ $XXK in identified savings  
- ✅ 2-3 deployed services (automated cost intelligence)
- ✅ Client trained + empowered to use tools
- ✅ 30-day support included (you're on-call)
- ✅ Renewal path clear (annual review scheduled)
- ✅ Client quote: "We didn't know we could do that with our data."

---

**Ready to build FinOps services at scale? Start here. Questions? Ask Marco.**

**Last Updated**: March 1, 2026  
**Status**: v1.0 — Ready for production engagements
