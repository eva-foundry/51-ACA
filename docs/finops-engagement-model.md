# FinOps Consulting Engagement Model

**Document Type**: Engagement Framework & Playbook  
**Target**: Replicable consulting model for Azure cost optimization (single subscription focus)  
**Version**: 1.0  
**Created**: March 1, 2026  
**Scope**: Phases 1-5 (Pre-Flight through Service Delivery)  
**Success Criteria**: Repeatable process; data-driven service menu; client ROI alignment

---

## Overview: The 5-Phase Engagement

```
PHASE 1: Pre-Flight        PHASE 2: Data Extraction    PHASE 3: Data Science     PHASE 4: Service Menu    PHASE 5: Delivery
(Week 1)                   (Weeks 1-2)                 (Weeks 2-3)               (Week 4)                 (Week 5)
├─ Role Assessment         ├─ Full Inventory           ├─ EDA                     ├─ Service Specs          ├─ Client Selection
├─ Scope Confirmation      ├─ 90-Day Cost Records      ├─ Baseline Metrics        ├─ Code (tested)          ├─ Deploy Services
└─ Permission Mapping      ├─ Cost Advisor Extract     ├─ Savings Analysis        ├─ Pricing                └─ Final Report
                           └─ Load to Database         ├─ Anomaly Detection       └─ Documentation
                                                       └─ Client-Specific Report

DELIVERABLES BY PHASE:
1. Scope Confirmation Doc + Permission Matrix
2. Inventory Report + Cost Database (populated)
3. Savings Opportunities Report (client-specific) + Data Profile
4. Service Menu Catalog (with pricing, code, docs)
5. Final FinOps Service Engagement Report + Deployed Services
```

---

## PHASE 1: Pre-Flight & Discovery (Week 1)

### 1.1 Role Assessment Framework

**Goal**: Understand what the client's Azure identity can access; document scope + gaps

**Process**:
```powershell
# Template: scripts/phase1-role-assessment.ps1
# Run from: Client subscription context (requires: Connect-AzAccount)

# Step 1: Capture Active Identity
$context = Get-AzContext
$principal = Get-AzADUser | Where-Object UserPrincipalName -eq $context.Account

# Step 2: Enumerate Effective RBAC Roles
$subscriptionId = (Get-AzContext).Subscription.Id
$roleAssignments = Get-AzRoleAssignment -Scope "/subscriptions/$subscriptionId"

# Step 3: Map Permissions to FinOps Scope
$finopsRequiredRoles = @(
    "Cost Management Reader",      # Can read cost data
    "Billing Reader",              # Can read billing records
    "Reader",                       # Can list resources
    "Resource Group Reader",        # Lower alternative
    "Monitoring Reader"            # Can read metrics
)

$roleGaps = @()
foreach ($role in $finopsRequiredRoles) {
    if ($roleAssignments.RoleDefinitionName -notcontains $role) {
        $roleGaps += $role
    }
}

# Output: Permission Matrix
# Format: Role | Required | Have | Scope | Data Access | Gaps
```

**Deliverable: Permission Matrix Document**

| Role | Required | Have | Scope | Data Access | Impact if Missing |
|---|---|---|---|---|---|
| **Cost Management Reader** | ✅ Critical | ? | Subscription | Cost data (Billing exports) | Cannot extract cost data |
| **Billing Reader** | ✅ Critical | ? | Subscription | Billing records, invoices | Limited cost granularity |
| **Reader** | ✅ Required | ? | Subscription | All resource metadata | Cannot inventory resources |
| **Monitoring Reader** | ⚠️ Recommended | ? | Sub/RG | Performance metrics | Cannot correlate cost + utilization |
| **Storage Blob Reader** | ⚠️ Optional | ? | Storage accounts | Blob inventory, access logs | Cannot analyze storage patterns |
| **Network Contributor** | ⚠️ Optional | ? | VNets | Network topology details | Limited network optimization |

**Template Location**: `/51-ACA/templates/permission-matrix-template.md`

---

### 1.2 Scope Confirmation Checklist

**Use template**: `CLIENT-SCOPE-CONFIRMATION.md`

```markdown
## Pre-Flight Scope Confirmation

**Client Name**: ________________  
**Subscription ID**: ________________  
**Analysis Period**: 90 days (Last date obtained: ________)  
**Engagement Duration**: 3 months access window  
**Client Contact**: ________________ (email, phone)  

### Access Granted (Initial)
- [x] Cost Management Reader
- [x] Billing Reader  
- [x] Reader (all resources)
- [ ] Monitoring Reader (optional)
- [ ] Storage Blob Reader (optional)
- [ ] Network Contributor (optional)

### Known Limitations
- [ ] Azure Policy restrictions (may hide some resource details)
- [ ] Federated identity (may affect access to some subscriptions)
- [ ] Dedicated hosts (not visible to Cost Mgmt)
- [ ] Transferred subscriptions (billing history may be incomplete)

### Blind Spots & Workaround
(Document what we cannot see + why)

### Client Sign-Off
- [ ] Confirm scope acceptable
- [ ] Confirm 90-day cost data available
- [ ] Confirm timeline (5 weeks for delivery)
- [ ] Confirm contact for escalations

Approved By: ________________ Date: __________
```

---

## PHASE 2: Data Extraction & Database Loading (Weeks 1-2)

### 2.1 Data Extraction Playbook

**Reference**: `/14-az-finops/scripts/` (tools to adapt)

#### 2.1.1 Inventory Extraction

**What to pull**:
```
1. Compute Resources
   ├─ VMs (Name, SKU, Status, Tags, Managed Disk info, Last Power Event)
   ├─ App Services (Plan SKU, Instances, Regions, Custom Domains)
   ├─ Container Apps (Environment, Replicas, Memory/CPU)
   ├─ AKS Clusters (Node pools, Node SKUs, Add-ons)
   └─ Scale Sets (Min/Max instances, VM SKU, Rules)

2. Storage Resources
   ├─ Storage Accounts (Kind, Performance Tier, Access Tier, Replication)
   ├─ Blob Containers (Size, Last Modified, Access Tier, Lifecycle Policy)
   ├─ File Shares (Quota, Tier — Standard vs Premium)
   ├─ Data Lake (Storage, Replication, Hierarchical NS enabled)
   └─ Managed Disks (Type, Size, Snapshot count, Encryption)

3. Networking Resources
   ├─ Virtual Networks (Address space, Subnets, VPN/ExpressRoute)
   ├─ Network Security Groups (Rules count, Associated resources)
   ├─ Public IPs (Allocation method, Associated resource)
   ├─ Load Balancers (SKU, Backend pool size)
   ├─ Application Gateways (SKU, Certificate count)
   ├─ NAT Gateways (Outbound IP rules)
   ├─ Private Endpoints (Linked service, IP allocation)
   └─ Virtual WAN (Hubs, Sites, VPN/ExpressRoute connections)

4. Database Resources
   ├─ SQL Databases (Edition, DTU, Backup retention, Geo-replication)
   ├─ Managed Instances (vCore, Storage tier)
   ├─ PostgreSQL/MySQL (SKU, Storage, Replicas)
   ├─ Cosmos DB (API, Throughput RU, Multi-region)
   └─ Redis Cache (SKU, Size, Cluster nodes)

5. Security & Compliance
   ├─ Key Vaults (RBAC vs Access Policy, Purge protection)
   ├─ Resource Locks (CanNotDelete, ReadOnly)
   ├─ Azure Policy Assignments (Scope, Effect)
   ├─ RBAC Role Assignments (Scope, Principal type)
   └─ Managed Identities (User-assigned vs System-assigned)

6. Cost Attribution Tags
   ├─ All tags on all resources
   ├─ Tag coverage by resource type
   ├─ Untagged resource count + cost
```

**Script Template**: `/51-ACA/scripts/phase2-inventory-extraction.ps1`

```powershell
# Pseudocode structure (actual implementation in referenced scripts)
param(
    [string]$SubscriptionId,
    [string]$OutputPath = "./inventory-extracts",
    [switch]$IncludeMetrics
)

# 1. Compute Inventory
$vms = Get-AzVM | Select-Object Name, ResourceGroupName, HardwareProfile, PowerState, Tags, Location
$vms | Export-Csv "$OutputPath/inventory-vms.csv" -NoTypeInformation

$appServices = Get-AzWebApp | Select-Object Name, AppServicePlanId, ResourceGroup, State, Tags
$appServices | Export-Csv "$OutputPath/inventory-appservices.csv" -NoTypeInformation

# 2. Storage Inventory
$storageAccounts = Get-AzStorageAccount | Select-Object StorageAccountName, Kind, SkuName, Location, Tags
$storageAccounts | Export-Csv "$OutputPath/inventory-storage.csv" -NoTypeInformation

foreach ($sa in $storageAccounts) {
    $context = $sa | New-AzStorageContext
    $containers = Get-AzStorageContainer -Context $context
    $containers | Select-Object @{N='StorageAccount'; E={$sa.StorageAccountName}}, Name, Properties | 
        Export-Csv "$OutputPath/inventory-containers.csv" -Append -NoTypeInformation
}

# 3. Networking Inventory
$vnets = Get-AzVirtualNetwork | Select-Object Name, Location, AddressSpace, Tags
$subnets = Get-AzVirtualNetworkSubnetConfig -VirtualNetwork $vnets
# ... etc

# Output: Consolidated JSON manifest
$manifest = @{
    ExtractionDate = (Get-Date).ToUniversalTime()
    SubscriptionId = $SubscriptionId
    ResourceCounts = @{
        VMs = $vms.Count
        AppServices = $appServices.Count
        StorageAccounts = $storageAccounts.Count
        # ...
    }
    Files = @(
        "inventory-vms.csv",
        "inventory-appservices.csv",
        "inventory-storage.csv",
        "inventory-containers.csv",
        "inventory-networking.csv",
        "inventory-tags-analysis.csv"
    )
}
$manifest | ConvertTo-Json | Out-File "$OutputPath/manifest.json"
```

**Reference Scripts** (from project 14):
- `/14-az-finops/tools/finops/az-inventory-finops.ps1` — Comprehensive inventory model (650 lines, tested)
- `/14-az-finops/scripts/inspect-csv.ps1` — Validate extraction output
- `/14-az-finops/scripts/check-env.ps1` — Verify connectivity

**Output**: CSV files + manifest JSON (ready for database import)

---

#### 2.1.2 Cost Data Extraction (90-Day Historical)

**What to pull**:
```
1. Daily Cost Records
   ├─ PreTaxCost (daily aggregate)
   ├─ ResourceName, ResourceType, ResourceGroup
   ├─ ServiceName, MeterCategory, MeterSubCategory
   ├─ Tags (all custom tags applied to resource)
   ├─ Date, SubscriptionId
   └─ Quantity, Unit, UnitPrice

2. Cost Advisor Recommendations
   ├─ Resource Name
   ├─ Recommendation Category (Right-size, Reserve, Hybrid)
   ├─ Potential Saving (annual)
   ├─ Implementation Effort
   ├─ Risk Level
   └─ Confidence Score

3. Billing Records
   ├─ Monthly invoices
   ├─ Reservations purchased (start/end dates, commitment amount)
   ├─ Credits applied
```

**Reference Scripts** (from project 14):
- `/14-az-finops/scripts/extract_costs_sdk.py` — Python SDK-based extraction (handles pagination)
- `/14-az-finops/scripts/Backfill-Costs-REST.ps1` — REST API fallback (if SDK pagination breaks)
- `/14-az-finops/scripts/Configure-EsDAICoESub-CostExport.ps1` — Configure daily cost exports via Portal

**Note**: Project 14 discovered SDK pagination bug (>5K rows) with azure-mgmt-costmanagement 4.0.1. Use REST API or Portal exports as primary method.

**Script Template**: `/51-ACA/scripts/phase2-cost-extraction.ps1`

```powershell
param(
    [string]$SubscriptionId,
    [int]$DaysBack = 90,
    [string]$OutputPath = "./cost-extracts"
)

# Method 1: Cost Management API via REST (recommended, handles pagination)
$startDate = (Get-Date).AddDays(-$DaysBack).ToString('yyyy-MM-01')
$endDate = (Get-Date).ToString('yyyy-MM-dd')

$body = @{
    type      = "Usage"
    timeframe = "Custom"
    timePeriod = @{
        from = "$($startDate)T00:00:00Z"
        to   = "$($endDate)T23:59:59Z"
    }
    dataset = @{
        granularity = "Daily"
        aggregation = @{
            totalCost = @{
                name   = "PreTaxCost"
                filter = $null
            }
        }
        grouping = @(
            @{ type = "Dimension"; name = "ResourceId" }
            @{ type = "Dimension"; name = "ResourceName" }
            @{ type = "Dimension"; name = "ServiceName" }
        )
        filter = @{
            dimensions = @{
                name   = "SubscriptionId"
                operator = "In"
                values = @($SubscriptionId)
            }
        }
    }
} | ConvertTo-Json -Depth 10

# Call Cost Management API pagination loop
# ... handle nextLink + pagination
# Export to CSV: $DaysBack days × $ResourceCount rows = typical 5K-50K rows

Export-Csv "$OutputPath/costs-daily-$startDate-$endDate.csv" -NoTypeInformation
```

**Output**: CSV with 55+ columns (standard Azure cost export format)

**Duration**: 30-90 minutes (API calls + export)

---

### 2.2 Database Design & Schema

**Goal**: Load extracted data into queryable database for analytics

**Choice: SQLite (for simplicity) or PostgreSQL (for scale)**

**Recommended**: SQLite for prototype; PostgreSQL for production

**Path**: `/51-ACA/data/finops-schema.sql`

```sql
-- Core Tables (optimized for analytics)

CREATE TABLE subscriptions (
    subscription_id TEXT PRIMARY KEY,
    display_name TEXT,
    state TEXT,
    extract_date TIMESTAMP
);

CREATE TABLE resources (
    resource_id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    resource_group TEXT,
    resource_name TEXT,
    resource_type TEXT,
    location TEXT,
    status TEXT,
    tags JSON,
    sku TEXT,
    created_date DATE,
    last_modified DATE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
);

CREATE INDEX idx_resources_rg ON resources(resource_group);
CREATE INDEX idx_resources_type ON resources(resource_type);
CREATE INDEX idx_resources_location ON resources(location);

CREATE TABLE daily_costs (
    cost_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id TEXT,
    date DATE,
    resource_id TEXT,
    resource_name TEXT,
    service_name TEXT,
    meter_category TEXT,
    meter_subcategory TEXT,
    pre_tax_cost DECIMAL(12, 2),
    quantity DECIMAL(20, 4),
    unit_price DECIMAL(12, 4),
    unit TEXT,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
);

CREATE INDEX idx_costs_date ON daily_costs(date);
CREATE INDEX idx_costs_resource ON daily_costs(resource_id);
CREATE INDEX idx_costs_service ON daily_costs(service_name);

CREATE TABLE cost_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_id INTEGER,
    tag_key TEXT,
    tag_value TEXT,
    FOREIGN KEY (cost_id) REFERENCES daily_costs(cost_id)
);

CREATE INDEX idx_tags_key ON cost_tags(tag_key, tag_value);

CREATE TABLE cost_advisor_recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id TEXT,
    resource_id TEXT,
    resource_name TEXT,
    category TEXT,
    recommendation_text TEXT,
    annual_savings DECIMAL(12, 2),
    implementation_effort TEXT,
    confidence_score DECIMAL(3, 2),
    risk_level TEXT,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
);

CREATE INDEX idx_advisor_savings ON cost_advisor_recommendations(annual_savings DESC);

-- Materialized Views (for fast analytics)

CREATE VIEW v_daily_cost_by_service_date AS
SELECT 
    date,
    service_name,
    SUM(pre_tax_cost) as total_cost,
    COUNT(DISTINCT resource_id) as resource_count,
    SUM(quantity) as total_quantity
FROM daily_costs
GROUP BY date, service_name;

CREATE VIEW v_cost_by_resource_group AS
SELECT 
    rg.resource_group,
    SUM(dc.pre_tax_cost) as total_cost,
    COUNT(DISTINCT dc.resource_id) as resource_count,
    MIN(dc.date) as first_cost_date,
    MAX(dc.date) as last_cost_date
FROM daily_costs dc
JOIN resources rg ON dc.resource_id = rg.resource_id
GROUP BY rg.resource_group;

CREATE VIEW v_cost_by_tag AS
SELECT 
    ct.tag_key,
    ct.tag_value,
    SUM(dc.pre_tax_cost) as total_cost,
    COUNT(DISTINCT dc.resource_id) as resource_count
FROM daily_costs dc
JOIN cost_tags ct ON dc.cost_id = ct.cost_id
GROUP BY ct.tag_key, ct.tag_value;

-- Insert Operations

INSERT INTO subscriptions (subscription_id, display_name, extract_date) VALUES (?, ?, ?);
INSERT INTO resources (...) VALUES (...);
INSERT INTO daily_costs (...) VALUES (...);
INSERT INTO cost_advisor_recommendations (...) VALUES (...);
```

**Import Process** (pseudocode):

```python
# Script: /51-ACA/scripts/phase2-load-database.py
import sqlite3
import pandas as pd
import json
from pathlib import Path

def load_inventory(db_conn, inventory_dir):
    """Load CSV extracts into resources table"""
    for csv_file in Path(inventory_dir).glob("inventory-*.csv"):
        df = pd.read_csv(csv_file)
        df.to_sql('resources', db_conn, if_exists='append', index=False)

def load_costs(db_conn, cost_csv):
    """Load daily cost records"""
    df = pd.read_csv(cost_csv)
    # Normalize tags (JSON column)
    df['tags'] = df['tags'].apply(lambda x: json.loads(x) if pd.notna(x) else {})
    df.to_sql('daily_costs', db_conn, if_exists='append', index=False)

def load_cost_advisor(db_conn, recommendations_csv):
    """Load Cost Advisor recommendations"""
    df = pd.read_csv(recommendations_csv)
    df.to_sql('cost_advisor_recommendations', db_conn, if_exists='append', index=False)

# Main
db = sqlite3.connect('/51-ACA/data/finops.db')
load_inventory(db, '/inventory-extracts')
load_costs(db, '/cost-extracts/costs-daily-*.csv')
load_cost_advisor(db, '/cost-extracts/recommendations.csv')
db.commit()
db.close()
```

**Output**: Queryable SQLite database (ready for analytics)

---

## PHASE 3: Data Science & Discovery (Weeks 2-3)

### 3.1 Exploratory Data Analysis (EDA)

**Goal**: Profile the data; surface patterns, anomalies, opportunities

**Script Template**: `/51-ACA/scripts/phase3-eda.py`

```python
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import json

db = sqlite3.connect('/51-ACA/data/finops.db')

# ===== SECTION 1: Cost Profiling =====

query = """
SELECT 
    date,
    service_name,
    SUM(pre_tax_cost) as daily_cost
FROM daily_costs
GROUP BY date, service_name
ORDER BY date DESC
"""
df_costs = pd.read_sql_query(query, db)

# Baseline metrics
total_cost = df_costs['daily_cost'].sum()
avg_daily_cost = df_costs['daily_cost'].mean()
std_daily_cost = df_costs['daily_cost'].std()
cost_min = df_costs['daily_cost'].min()
cost_max = df_costs['daily_cost'].max()

print(f"""
=== COST BASELINE (90-Day Period) ===
Total Spend: ${total_cost:,.2f}
Average Daily: ${avg_daily_cost:,.2f}
Std Dev: ${std_daily_cost:,.2f}
Min Day: ${cost_min:,.2f}
Max Day: ${cost_max:,.2f}
Monthly Run-Rate (Annualized): ${(total_cost/90*365):,.2f}
""")

# ===== SECTION 2: Service Breakdown =====

query_svc = """
SELECT 
    service_name,
    SUM(pre_tax_cost) as total_cost,
    COUNT(DISTINCT resource_id) as resource_count,
    AVG(pre_tax_cost) as avg_daily_cost
FROM daily_costs
GROUP BY service_name
ORDER BY total_cost DESC
"""
df_services = pd.read_sql_query(query_svc, db)

print("\n=== TOP 10 COST DRIVERS (by service) ===")
print(df_services.head(10).to_string())

# ===== SECTION 3: Anomaly Detection =====

# Time series decomposition + z-score detection
df_ts = df_costs.set_index('date').resample('D')['daily_cost'].sum()

# Calculate rolling mean + std
rolling_mean = df_ts.rolling(window=7).mean()
rolling_std = df_ts.rolling(window=7).std()
z_scores = (df_ts - rolling_mean) / rolling_std

anomalies = df_ts[z_scores > 3.0]  # 99.7% confidence threshold

print(f"\n=== ANOMALIES DETECTED (z-score > 3.0) ===")
for date, cost in anomalies.items():
    z = z_scores[date]
    print(f"{date}: ${cost:,.2f} (z-score: {z:.2f})")

# ===== SECTION 4: Resource Efficiency =====

query_res = """
SELECT 
    r.resource_name,
    r.resource_type,
    r.location,
    SUM(dc.pre_tax_cost) as total_cost,
    COUNT(DISTINCT dc.date) as active_days
FROM daily_costs dc
JOIN resources r ON dc.resource_id = r.resource_id
GROUP BY r.resource_id
ORDER BY total_cost DESC
LIMIT 20
"""
df_resources = pd.read_sql_query(query_res, db)

print("\n=== TOP 20 COSTLIEST RESOURCES ===")
print(df_resources.to_string())

# ===== SECTION 5: Tag Coverage & Quality =====

query_tags = """
SELECT 
    tag_key,
    COUNT(DISTINCT tag_id) as tag_count,
    COUNT(DISTINCT cost_id) as cost_records_tagged
FROM cost_tags
GROUP BY tag_key
"""
df_tags = pd.read_sql_query(query_tags, db)

total_cost_records = pd.read_sql_query(
    "SELECT COUNT(*) as cnt FROM daily_costs", db
)['cnt'][0]

print(f"\n=== TAG QUALITY ANALYSIS ===")
print(f"Total Cost Records: {total_cost_records:,}")
print(f"Cost Records Tagged: {df_tags['cost_records_tagged'].sum():,}")
print(f"Tag Coverage: {(df_tags['cost_records_tagged'].sum()/total_cost_records)*100:.1f}%")
print("\nTag Keys Present:")
print(df_tags.to_string())

# ===== SECTION 6: Cost Advisor Recommendations =====

query_rec = """
SELECT 
    category,
    SUM(annual_savings) as potential_savings,
    COUNT(*) as recommendation_count,
    AVG(confidence_score) as avg_confidence
FROM cost_advisor_recommendations
GROUP BY category
ORDER BY potential_savings DESC
"""
df_recs = pd.read_sql_query(query_rec, db)

print(f"\n=== COST ADVISOR OPPORTUNITIES ===")
print(df_recs.to_string())

# ===== SECTION 7: Growth Trend =====

query_trend = """
SELECT 
    strftime('%Y-%m', date) as month,
    SUM(pre_tax_cost) as monthly_cost
FROM daily_costs
GROUP BY strftime('%Y-%m', date)
ORDER BY month
"""
df_trend = pd.read_sql_query(query_trend, db)

print(f"\n=== MONTHLY TREND ===")
print(df_trend.to_string())

# Calculate month-over-month growth
df_trend['mom_growth'] = df_trend['monthly_cost'].pct_change() * 100
print("\nMonth-over-Month Growth:")
print(df_trend[['month', 'mom_growth']].to_string())

# ===== SECTION 8: Cost Distribution (by Percentile) =====

percentiles = [10, 25, 50, 75, 90, 95, 99]
print(f"\n=== COST DISTRIBUTION (Percentiles) ===")
for p in percentiles:
    val = np.percentile(df_ts, p)
    print(f"P{p}: ${val:,.2f}")

# Save report
report = {
    "extraction_date": pd.Timestamp.now().isoformat(),
    "total_cost": float(total_cost),
    "avg_daily": float(avg_daily_cost),
    "annualized_cost": float(total_cost/90*365),
    "services": df_services.to_dict('records')[:10],
    "anomalies": anomalies.to_dict(),
    "tag_coverage": float((df_tags['cost_records_tagged'].sum()/total_cost_records)*100),
    "advisor_savings_potential": float(df_recs['potential_savings'].sum())
}

with open('/51-ACA/data/eda-report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)
```

**Output**: EDA report + JSON metrics (foundation for savings analysis)

---

### 3.2 Client-Specific Savings Opportunities Report

**Goal**: Generate `saving-opportunities.md` equivalent (tailored to their subscription)

**Model**: Follow project 14's structure, but:
- Use ONLY this subscription's data (not 14's multi-sub example)
- Rank by effort + impact (effort-matrix)
- Include specific resource names + costs
- Add risk assessment + implementation timeline

**Template**: `/51-ACA/scripts/phase3-generate-savings-report.py`

```python
# Pseudocode: Build savings opportunities from database patterns

import sqlite3
import pandas as pd

db = sqlite3.connect('/51-ACA/data/finops.db')

# ===== OPPORTUNITY 1: Idle/Unattached Resources =====

# Find resources with zero cost in last 30 days
query = """
SELECT 
    r.resource_name,
    r.resource_type,
    r.location,
    COALESCE(SUM(dc.pre_tax_cost), 0) as cost_90d
FROM resources r
LEFT JOIN daily_costs dc ON r.resource_id = dc.resource_id 
    AND dc.date >= date('now', '-30 days')
GROUP BY r.resource_id
HAVING COALESCE(SUM(dc.pre_tax_cost), 0) = 0
"""
df_idle = pd.read_sql_query(query, db)

print(f"OPPORTUNITY 1: Delete Idle Resources")
print(f"Found {len(df_idle)} resources with $0 cost in last 30 days")
print(f"Recommended Action: Delete after 60-day notice period")
print(f"Risk Level: Low (if truly idle)")

# ===== OPPORTUNITY 2: Right-Sizing (VMs, Databases) =====

# Pull Cost Advisor recommendations
query = """
SELECT 
    resource_name,
    recommendation_text,
    annual_savings,
    confidence_score
FROM cost_advisor_recommendations
WHERE category = 'Right-size'
ORDER BY annual_savings DESC
"""
df_rs = pd.read_sql_query(query, db)

print(f"\nOPPORTUNITY 2: Virtual Machine Right-Sizing")
print(f"Found {len(df_rs)} right-sizing opportunities")
print(f"Total Potential Saving: ${df_rs['annual_savings'].sum():,.2f}/yr")
print(f"Avg Confidence: {df_rs['confidence_score'].mean():.1%}")

# ===== OPPORTUNITY 3: Reserved Instances / Commitments =====

query = """
SELECT 
    resource_name,
    recommendation_text,
    annual_savings
FROM cost_advisor_recommendations
WHERE category IN ('Reserve', 'Hybrid Benefit')
ORDER BY annual_savings DESC
"""
df_ri = pd.read_sql_query(query, db)

print(f"\nOPPORTUNITY 3: Reserved Instance Purchases")
print(f"Total Potential Saving: ${df_ri['annual_savings'].sum():,.2f}/yr")
print(f"Effort: 2-4 hours (Portal purchase)")
print(f"Payback Period: <3 months")

# ===== OPPORTUNITY 4: Compute Scheduling (Auto-shutdown nights/weekends) =====

# Identify compute resources with idle periods
query = """
SELECT 
    r.resource_name,
    r.resource_type,
    SUM(dc.pre_tax_cost) as total_cost_90d
FROM daily_costs dc
JOIN resources r ON dc.resource_id = r.resource_id
WHERE r.resource_type IN ('Microsoft.Compute/virtualMachines', 
                           'Microsoft.Web/serverfarms',
                           'Microsoft.ContainerInstance/containerGroups')
GROUP BY r.resource_id
ORDER BY total_cost_90d DESC
"""
df_compute = pd.read_sql_query(query, db)

print(f"\nOPPORTUNITY 4: Compute Scheduling (Nights/Weekends)")
print(f"Found {len(df_compute)} compute resources")
print(f"Est. Saving if scheduled (33% nights): ${(df_compute['total_cost_90d'].sum()/90*365*0.33):,.2f}/yr")
print(f"Effort: 5 days (GitHub Actions + testing)")
print(f"Risk: Deployment delays; mitigation = manual override")

# ===== OPPORTUNITY 5: Storage Tier Optimization =====

query = """
SELECT 
    r.resource_name,
    r.sku as storage_sku,
    SUM(dc.pre_tax_cost) as monthly_cost_avg
FROM daily_costs dc
JOIN resources r ON dc.resource_id = r.resource_id
WHERE r.resource_type LIKE '%Storage%'
GROUP BY r.resource_id
ORDER BY monthly_cost_avg DESC
"""
df_storage = pd.read_sql_query(query, db)

print(f"\nOPPORTUNITY 5: Storage Tier Optimization")
print(f"Found {len(df_storage)} storage resources")
print(f"Potential Saving (move Hot→Cool): ${(df_storage['monthly_cost_avg'].sum()*0.5*12):,.2f}/yr")
print(f"Effort: 1 day (lifecycle policy + testing)")

# ===== OPPORTUNITY 6: Network Egress Reduction =====

# Identify outbound data transfer costs
query = """
SELECT 
    meter_subcategory,
    SUM(pre_tax_cost) as total_cost_90d,
    SUM(quantity) as total_quantity,
    unit
FROM daily_costs
WHERE meter_subcategory LIKE '%egress%' OR meter_subcategory LIKE '%transfer%'
GROUP BY meter_subcategory
ORDER BY total_cost_90d DESC
"""
df_net = pd.read_sql_query(query, db)

if len(df_net) > 0:
    print(f"\nOPPORTUNITY 6: Network Egress Reduction")
    print(f"Current Egress Cost (annualized): ${(df_net['total_cost_90d'].sum()/90*365):,.2f}/yr")
    print(f"Potential Saving (10% reduction): ${(df_net['total_cost_90d'].sum()/90*365*0.1):,.2f}/yr")
    print(f"Actions: Azure Content Delivery Network, Private Endpoints, ExpressRoute")

# ===== FINAL SUMMARY =====

total_opportunities = (
    df_idle['cost_90d'].sum() * 4 +  # annualize
    df_rs['annual_savings'].sum() +
    df_ri['annual_savings'].sum() +
    (df_compute['total_cost_90d'].sum()/90*365*0.33) +
    (df_storage['monthly_cost_avg'].sum()*0.5*12)
)

print(f"\n" + "="*60)
print(f"TOTAL OPPORTUNITY IDENTIFIED: ${total_opportunities:,.2f}/yr")
print(f"(Assuming 3 months data, annualized x12)")
print(f"="*60)

# Export as markdown
markdown_report = f"""
# Cost Saving Opportunities — {subscription_id}

> Data: 3-month actuals  
> Generated: {pd.Timestamp.now().strftime('%B %d, %Y')}  
> Scope: Single Subscription Analysis

## Baseline

| Metric | Value |
|---|---|
| 90-Day Total | ${total_cost:,.2f} |
| Monthly Avg | ${total_cost/3:,.2f} |
| Annualized Run-Rate | ${(total_cost/90*365):,.2f} |

## Saving Opportunities (Ranked by Effort)

### 1. Delete Idle Resources — 1 day — ${df idle Saving:,.2f}/yr
(details...)

# ... continue for each opportunity
"""

with open('/51-ACA/reports/savings-opportunities.md', 'w') as f:
    f.write(markdown_report)
```

**Output**: `savings-opportunities.md` (tailored to subscription)

---

## PHASE 4: Service Menu Proposal (Week 4)

### 4.1 Service Catalog Template

**Goal**: Define 8-12 services; justify pricing; document each service

**Template**: `/51-ACA/docs/SERVICE-MENU-TEMPLATE.md`

```markdown
# FinOps Services Menu

**Subscription**: ________________  
**Analysis Period**: 90-day baseline  
**Total Identified Opportunity**: $XXX,XXX/yr  
**Client Decision Due**: [DATE]

---

## SERVICE TIER 1: Foundation Services (Quick Wins)

### 1.1 Idle & Unattached Resource Cleanup
**Category**: Cost Reduction (One-Time)  
**Applicability**: 100% of subscriptions  
**Time to Implement**: 1-2 weeks (including 60-day notice period)

**What We Do**:
- Identify resources with zero cost in last 30+ days
- Confirm with client (manual gate)
- Delete after notice period
- Generate evidence for audit trail

**Setup Cost**: $2,000 (1 week)  
**Recurring Cost**: $0  
**Potential Saving**: $XXX/yr (from your subscription data)  
**Payback Period**: <1 month

**Deliverables**:
- Resource cleanup report (CSV + recommendations)
- 60-day notice emails to resource owners
- Delete runbook (automated via script)
- Audit log (before/after inventory)

---

### 1.2 Quick Cost Analysis Report
**Category**: Discovery & Reporting (One-Time)  
**Applicability**: 100% of subscriptions  
**Time to Implement**: Immediate (included in engagement)

**What We Do**:
- Cost breakdown by service, resource group, resource
- Top 20 cost drivers identified
- Monthly trend analysis
- Tag quality assessment
- Cost Advisor recommendations analysis

**Setup Cost**: $0 (included in Phase 1-3)  
**Recurring Cost**: $0  
**Value**: Data-driven decisions for next 12 months

**Deliverables**:
- Cost Analysis Report (PDF)
- Data extracts (CSV for your archival)
- Trend graphs + visualizations
- External benchmark comparison

---

## SERVICE TIER 2: Ongoing Cost Intelligence

### 2.1 Anomaly Detection & Cost Control Service
**Category**: Monitoring + Alerting (Recurring)  
**Applicability**: Subscriptions with 20+ resources and >$5K/mo spend  
**Maintenance**: 24/7 monitoring; incident response

**What We Do**:
- Deploy KQL anomaly detection rule (z-score > 3.0)
- Daily data ingestion from Cost Management
- Slack/Teams/Email alerts on detected spikes
- Root cause analysis support (on-call, 4h SLA)
- Monthly anomaly review meeting

**Setup Cost**: $3,500 (3 days)  
- Database setup + schema design
- Anomaly detection model tuning
- Alert routing + notification setup
- Training on investigation playbooks

**Recurring Cost**: $800/month  
- Azure Log Analytics retention (7 months)
- On-call support (4h response SLA, monthly)
- Alert maintenance + tuning
- Report generation

**Potential Value**: Prevent $100K+ incidents (based on your data, April event cost $158K)  
**Payback Period**: <1 month (if one incident prevented)

**Deliverables**:
- Deployed anomaly detection in ADX/Log Analytics
- Alert rules (configurable thresholds)
- Investigation playbook (root cause steps)
- Monthly anomaly report (trends + risk assessment)
- Slack bot (daily cost summary)

**SLA**: 
- Alert delivery: <5 minutes
- Case response: <4 hours
- Monthly review: Scheduled call

---

### 2.2 Cost Forecasting Service
**Category**: Planning & Budgeting (Recurring)  
**Applicability**: Subscriptions with growth trajectory or budget planning cycles  
**Maintenance**: Monthly forecast refresh

**What We Do**:
- ARIMA time-series forecasting (seasonality + trend)
- 30/60/90-day lookahead with confidence intervals
- What-if scenario modeling (new projects, growth rates)
- Budget vs actual tracking + variance alerts
- Quarterly rolling forecast (always 12-month visibility)

**Setup Cost**: $4,000 (5 days)  
- Historical data analysis + model tuning
- What-if scenario template
- Power BI dashboard setup
- Forecast validation (backtest)

**Recurring Cost**: $600/month  
- Monthly data refresh + model refit
- Dashboard updates
- Scenario modeling (on-demand, 3 scenarios/month included)
- Finance team support (email)

**Accuracy**: 90-95% within ±15% (from test data)  
**Payback Period**: 2-3 months (via budget planning efficiency)

**Deliverables**:
- Monthly 30/60/90-day forecast (PDF + data)
- Power BI dashboard (real-time)
- What-if scenario templates (5+ pre-built)
- Rolling 12-month forecast (updated monthly)
- Budget variance alerts (>10% threshold)

---

## SERVICE TIER 3: Advanced Analytics

### 3.1 Chargeback & Attribution Service
**Category**: Finance Automation (Recurring)  
**Applicability**: Multi-tenant subscriptions OR organizations with cost centers  
**Maintenance**: Flexible (weekly to monthly invoicing)

**What We Do**:
- Extract 3-6 billing dimensions from your tags (department, project, owner, cost center)
- Allocate shared services by usage (network, storage, monitoring)
- Generate monthly chargeback invoices (CSV for SAP/NetSuite import)
- Cost center dashboards (Power BI)
- Finance reconciliation support

**Setup Cost**: $6,000 (2 weeks)  
- Charge allocation model design (with finance team)
- Tag standardization (if needed)
- Dashboard development (3-4 cost center views)
- SAP/NetSuite integration (if applicable)
- Testing + validation

**Recurring Cost**: $1,200/month  
- Monthly invoice generation + validation
- Cost center manager dashboards (updates)
- Allocation rule maintenance
- Finance reconciliation support (4h/month)
- Ad-hoc chargeback queries

**Tag Requirement**: 80%+ of cost must be tagged with allocation-relevant keys  
**Payback Period**: 3-4 months (via finance process efficiency + cost accountability)

**Deliverables**:
- Monthly chargeback invoices (PDF + CSV)
- Cost center dashboards (Power BI, real-time)
- Allocation model documentation
- Finance user training (2 hours)
- Reconciliation playbook
- Escalation runbook (disputes)

---

### 3.2 Right-Sizing & Optimization Service
**Category**: Cost Reduction (Recurring)  
**Applicability**: Subscriptions with 10+ VMs AND/OR multi-region deployments  
**Maintenance**: Quarterly recommendations, on-demand implementation

**What We Do**:
- Quarterly VM right-sizing analysis (CPU/memory utilization)
- Storage tier recommendations (Hot → Cool → Archive lifecycle)
- Reserved Instance optimization (1-year vs 3-year)
- Database scaling recommendations
- Implementation guidance + validation testing

**Setup Cost**: $5,000 (1 week initial analysis)  
- Metrics collection setup (Azure Monitor exports)
- Right-sizing model development
- Dashboard creation
- Recommendation ranking

**Recurring Cost**: $400/month + implementation costs  
- Quarterly analysis + recommendations
- Metrics collection + storage
- Dashboard maintenance
- Implementation support (hourly: $150/hr, typical 20-40 hrs/quarter)

**Potential Savings**: 8-15% on compute + storage (subscription-dependent)  
**Payback Period**: 2-8 months (depends on implementation pace)

**Deliverables**:
- Quarterly right-sizing report (ranked by ROI)
- Implementation runbooks (per recommendation)
- Pre/post validation scripts
- Cost impact projections
- Rollback procedures
- Change management templates

---

## SERVICE TIER 4: Strategic Services (Optional, AI-Driven)

### 4.1 Sustainability & Carbon Reporting
**Category**: ESG + Compliance (Recurring)  
**Applicability**: Organizations with sustainability mandates  
**Maintenance**: Monthly reporting

**What We Do**:
- Convert cost to carbon footprint (CO2e emissions)
- Track carbon intensity by service
- Compare year-over-year trends
- Identify high-carbon resources
- Calculate carbon credit offset cost
- Board-level ESG reporting

**Setup Cost**: $3,500 (1 week)  
- Carbon conversion model validation
- Dashboard development
- Benchmark comparison setup

**Recurring Cost**: $300/month  
- Monthly carbon report (PDF + data)
- Dashboard updates
- Carbon credit pricing updates
- ESG stakeholder support

**Value**: ESG narrative + potential carbon credit monetization  
**Payback Period**: Intangible (compliance + brand)

**Deliverables**:
- Monthly carbon footprint report (tons CO2e)
- Carbon trend dashboard
- Service-level carbon breakdown
- Carbon credit offset quotes (annual)
- Board presentation template

---

## PRICING SUMMARY

| Service | Setup | Monthly | Annual (Recurring) | 1-Year Total |
|---|---|---|---|---|
| Idle Resource Cleanup | $2,000 | $0 | $0 | $2,000 |
| Quick Analysis Report | (included) | $0 | $0 | Included |
| Anomaly Detection | $3,500 | $800 | $9,600 | $13,100 |
| Cost Forecasting | $4,000 | $600 | $7,200 | $11,200 |
| Chargeback Service | $6,000 | $1,200 | $14,400 | $20,400 |
| Right-Sizing Service | $5,000 | $400 + impl | $4,800+ | $9,800+ |
| Sustainability | $3,500 | $300 | $3,600 | $7,100 |

## BUNDLED OFFERS

**Starter Kit** (for <$10K/mo subscriptions)
- Idle Resource Cleanup
- Quick Analysis Report
- Anomaly Detection (first month free)
- Total: $5,500 + $800/mo

**Professional** (for $10-50K/mo subscriptions)
- All Starter services
- Cost Forecasting
- Right-Sizing (quarterly analysis, no impl cost)
- Total: $12,500 Year 1 + $1,800/mo thereafter

**Enterprise** (for >$50K/mo subscriptions)
- All services + custom configurations
- Dedicated account manager (4h/month)
- Quarterly strategic reviews
- Total: Custom quote (typical $25K Year 1 + $3,500/mo)

---

## NEXT STEPS

1. **Decision Due**: [DATE]
2. **Review**: Which services match your priorities?
3. **Confirm**: Approve services + timeline
4. **Deploy**: Start Phase 5 (service deployment + training)
```

---

## PHASE 5: Service Delivery (Week 5)

### 5.1 Deployment Checklist

**Template**: `/51-ACA/docs/DELIVERY-CHECKLIST.md`

```markdown
# Service Delivery Checklist

**Engagement**: [Client Name]  
**Services Selected**: [List]  
**Deployment Start**: [DATE]  
**Final Handoff**: [DATE]

## Pre-Deployment

- [ ] Client approves services + pricing
- [ ] Database access verified (prod database created)
- [ ] Service code reviewed + tested
- [ ] Documentation complete (runbooks + FAQs)
- [ ] Training scheduled (date + attendees)
- [ ] Support contacts confirmed (escalations)

## Service 1: Anomaly Detection Deployment

- [ ] ADX cluster provisioned + database created
- [ ] Anomaly detection KQL rule deployed
- [ ] Alert routing configured (Slack/Teams/Email)
- [ ] Test: Trigger manual alert + verify delivery
- [ ] Runbook distributed (root cause investigation steps)
- [ ] Training: 1-hour walkthrough (client ops team)
- [ ] Support schedule: 24/7 on-call (4h SLA)

## Service 2: Cost Forecasting Deployment

- [ ] Historical data loaded (last 12 months or available)
- [ ] ARIMA model trained + validated
- [ ] Power BI dashboard deployed + shared
- [ ] What-if scenario templates created (5 scenarios)
- [ ] Test: Run forecast; validate accuracy within ±15%
- [ ] Training: 1-hour dashboard walkthrough (finance team)
- [ ] Monthly refresh process automated (e.g., Logic App)

## Service 3: Chargeback Service Deployment

- [ ] Cost allocation model finalized (client sign-off)
- [ ] Tag standardization completed (if needed)
- [ ] Chargeback invoice template created
- [ ] SAP/NetSuite integration tested (if applicable)
- [ ] Cost center manager dashboards deployed
- [ ] Test: Generate Month 1 invoice; reconcile with actual
- [ ] Training: 2-hour finance process walkthrough
- [ ] Monthly invoice calendar scheduled

## Final Handoff

- [ ] All services tested end-to-end
- [ ] Client sign-off (deliverables met)
- [ ] Documentation provided (all runbooks, FAQs, contacts)
- [ ] 30-day support window begun (email + chat)
- [ ] Monthly review scheduled (subscription health check)
- [ ] Renewal options discussed (contract next steps)

---

## Support SLA (30-Day Window)

| Severity | Response | Resolution Target |
|---|---|---|
| **Critical** (service down) | 1 hour | 4 hours |
| **High** (reduced functionality) | 4 hours | 1 business day |
| **Medium** (minor issue) | 1 business day | 3 business days |
| **Low** (question/advice) | 2 business days | 5 business days |
```

---

## REFERENCE MATERIALS FOR AGENT 51

### From Project 14 (Reusable Code & Patterns)

| Asset | Path | Use In Phase |
|---|---|---|
| **Inventory Script** | `/14-az-finops/tools/finops/az-inventory-finops.ps1` | 2.1.1 |
| **Cost Extraction (SDK)** | `/14-az-finops/scripts/extract_costs_sdk.py` | 2.1.2 |
| **Cost Extraction (REST)** | `/14-az-finops/scripts/Backfill-Costs-REST.ps1` | 2.1.2 |
| **Database Schema** | `/14-az-finops/docs/finops/02-target-architecture.md` | 2.2 |
| **ADF Pipeline** | `/14-az-finops/scripts/pipelines/` | 2.2 (optional automation) |
| **KQL Templates** | `/14-az-finops/scripts/kql/` | 3.1 + Phase 4 |
| **Savings Report** | `/14-az-finops/docs/saving-opportunities.md` | 3.2 (model) |
| **Advanced Analytics** | `/14-az-finops/docs/ADVANCED-CAPABILITIES-SHOWCASE.md` | 4.1 (service ideas) |

### Supporting Documentation

| Doc | Why It Matters | Path |
|---|---|---|
| **Azure RBAC Best Practices** | Understand role assessment | `/18-azure-best/12-security/rbac.md` |
| **Cost Management API Reference** | Correct API calls for extraction | Microsoft Docs: Cost Management API v2021-10-01 |
| **Azure Well-Architected Framework** | Context for recommendations | `/18-azure-best/02-well-architected/waf-overview.md` |
| **FinOps Toolkit Docs** | Industry reference | github.com/microsoft/finops-toolkit |

### Data Science Tools & Libraries

```
Required Python Packages:
├─ pandas (data manipulation)
├─ numpy (numerical analysis)
├─ scipy (statistical testing)
├─ matplotlib (visualization)
├─ statsmodels (ARIMA forecasting)
├─ scikit-learn (clustering, anomaly detection alternatives)
├─ sqlite3 (database)
├─ azure-identity (Azure auth)
├─ azure-costmanagement (Cost Mgmt API client)
└─ reportlab (PDF generation)

Install: pip install pandas numpy scipy matplotlib statsmodels scikit-learn azure-identity azure-costmanagement reportlab
```

### Database Technology Stack (Recommended)

**Option 1: SQLite** (lightweight, dev/PoC)
- Pros: No server, portable, great for <1GB datasets
- Cons: Single-user, limited concurrency
- Use case: Small subscriptions (<$50K spend), short-term analysis
- Setup: 10 minutes

**Option 2: PostgreSQL** (robust, production)
- Pros: Multi-user, scalability, advanced analytics
- Cons: Requires database server (Azure Database for PostgreSQL)
- Cost: $30-200/month (depends on SKU)
- Use case: Enterprise subscriptions, ongoing monitoring, multiple concurrent users
- Setup: 2 hours (Azure provisioning + schema)

**Option 3: Cosmos DB SQL API** (serverless, Azure-native)
- Pros: Integrated with Azure; no server management
- Cons: Cost model (RU-based) can spike; overkill for analysis
- Use case: If client has Cosmos DB in their subscription already
- Setup: 1 hour

**Agent 51 Recommendation**: Start with **PostgreSQL** (sweet spot between simplicity + robustness)

### Pricing Model Template

**Cost Structure** (for submitting quotes):

```
Setup (One-Time):
├─ Data Extraction & Database Load: 3-5 days × $150/hr = $3,600-$6,000
├─ EDA & Discovery: 3 days × $150/hr = $4,500
├─ Savings Report Generation: 2 days × $150/hr = $3,000
├─ Service Menu Design: 2 days × $150/hr = $3,000
└─ TOTAL SETUP: $14,100-$16,500

Per Service (Recurring):
├─ Development & Testing: 3-5 days (depends on complexity)
├─ Documentation & Runbooks: 2-3 days
├─ Deployment & Training: 1-2 days
├─ Monthly/Quarterly Maintenance: 4-8 hours/month
└─ Support (included first 30 days, then $150/hr overages)

Markup Strategy:
├─ Setup discounting: 10-20% off for multi-service commitments
├─ Volume discounts: 15% off if 5+ services
├─ Quarterly commitment: Discount monthly rate by 10%
└─ Annual prepay: Discount 15%
```

### Competitive Landscape

**Existing FinOps Consultants**:
- Microsoft FinOps partners: Typically $5-10K/month
- Third-party tools (Cloudzero, Densify, etc.): $2-50K/month + setup
- Internal teams: Cost of hiring FTE (~$120K/yr)

**Your Advantage**: Custom data model + tailored analytics (not one-size-fits-all SaaS)

**Positioning**: "Data-driven FinOps for [specific industry/use case]"

---

## APPENDIX: Checklist for Agent 51

### Pre-Engagement Kickoff

- [ ] Create engagement project in ADO (track work items)
- [ ] Set up source control repo (for client code, scripts, reports)
- [ ] Create shared documentation workspace (client access)
- [ ] Establish communication channel (Slack/Teams for real-time support)
- [ ] Schedule kickoff meeting (1h, with client decision-maker + technical lead)

### Technology Setup

- [ ] Spinup PostgreSQL instance (Azure Database for PostgreSQL)
- [ ] Create project folder structure:
  ```
  /{engagement-name}/
    ├─ scripts/ (extraction, EDA, deployment)
    ├─ data/ (database backups, extracts CSV)
    ├─ reports/ (savings, final deliverables)
    ├─ docs/ (runbooks, FAQs, training materials)
    └─ code/ (service implementations)
  ```
- [ ] Clone relevant assets from project 14
- [ ] Customize scripts for single-subscription context
- [ ] Test scripts against sample data

### Quality Gates (Before Client Delivery)

- [ ] Cost data validation: Sum of extracts = Azure Portal reported cost (within 1% tolerance)
- [ ] Database query performance: All analytic queries <5 seconds
- [ ] Report accuracy: Savings calculations validated against source data
- [ ] Code review: All Python/PowerShell scripts peer-reviewed
- [ ] Documentation completeness: Every service has runbook + FAQ
- [ ] Testing: End-to-end playthrough with test data

### Client Handoff

- [ ] All services deployed + tested
- [ ] Client trained on tools (1-2 hours per service)
- [ ] Support contact info provided (email + escalation path)
- [ ] 30-day support window starts (calendar invite for daily standup optional)
- [ ] Renewal discussion scheduled (Week 4 of engagement)

---

**Questions? Reach out to Marco (marco.presta@hrsdc-rhdcc.gc.ca) or Agent 51 team lead for clarifications.**

---

## Version History

| Date | Version | Changes |
|---|---|---|
| 2026-03-01 | 1.0 | Initial release; all 5 phases documented |
