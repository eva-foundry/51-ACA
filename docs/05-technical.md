# ACA Full API Technical Specification
# EVA-STORY: ACA-12-002

Version: 1.0.0
Updated: 2026-02-27
Status: AUTHORITATIVE -- agents must read this before implementing any endpoint.

---

## 1. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Fluent UI v9 |
| API | FastAPI 0.115+, Python 3.12 |
| Auth | MSAL Python (delegated + SP modes), Entra OIDC |
| Database | Cosmos DB NoSQL (marco-sandbox-cosmos Phase 1) |
| AI / LLM | Azure OpenAI GPT-4o via marco-sandbox-openai-v2 |
| Agent framework | 29-foundry (collection, analysis, generation, redteam agents) |
| Payment | Stripe (Tier 2 / Tier 3 checkout, webhook unlock) |
| Infra Phase 1 | Bicep -- reuse marco* resources |
| Delivery | Azure Blob Storage (SAS URLs, 7-day / 168-hour expiry) |
| Observability | Application Insights (marco-sandbox-appinsights) |
| CI/CD | GitHub Actions (OIDC federation to Azure) |

---

## 2. Architecture Overview

```
Client browser
  -> frontend React (Vite dev server / ACA static)
  -> services/api FastAPI (APIM + Entra auth, port 8080)
  -> collector job (Azure SDK -> Cosmos inventories)
  -> analysis job (Cosmos inventories -> findings JSON -> Cosmos findings)
  -> frontend shows Tier 1 report
  -> Stripe checkout -> tier upgrade in Cosmos entitlements
  -> delivery job (findings + inventory -> zip + SHA-256 manifest -> Blob SAS URL)
```

Services:

| Service | Type | Purpose |
|---|---|---|
| services/api | Container App | Orchestration, auth, tier gating, APIM-facing |
| services/collector | Container App Job | Azure SDK inventory + cost + advisor pull |
| services/analysis | Container App Job | 12 rules + 29-foundry agents -> findings |
| services/delivery | Container App Job | IaC generator + zip packager (Tier 3) |
| frontend | Static ACA | React 19 UI (Tier 1/2/3, checkout, download) |

---

## 3. Cosmos DB Containers

All containers use `subscriptionId` as the partition key unless noted.

| Container | Partition Key | Purpose |
|---|---|---|
| scans | subscriptionId | Scan run records (status, timestamps, preflight_result) |
| inventories | subscriptionId | Azure resource inventory (ARM Resource Graph) |
| cost-data | subscriptionId | 91-day daily cost rows (Cost Management) |
| advisor | subscriptionId | Azure Advisor recommendations |
| findings | subscriptionId | Analysis rule findings (tiered) |
| entitlements | subscriptionId | Customer tier, Stripe subscription state |
| payments | subscriptionId | Stripe payment events (immutable audit log) |
| clients | tenantId | Multi-tenant client records (ACA-specific) |
| stripe-map | stripeCustomerId | Stripe customer to subscriptionId mapping |

Tenant isolation rule: Every Cosmos query MUST include the partition key.
The API middleware extracts subscriptionId from the auth token and injects it
into every DB operation. Never call cosmos_client.query_items() without partition_key.

---

## 4. Endpoint Inventory (27 endpoints)

### 4.1 Auth Router (/v1/auth)

| Method | Path | Status | Auth | Description |
|---|---|---|---|---|
| POST | /v1/auth/connect | stub | none | Initiate delegated MSAL auth flow |
| POST | /v1/auth/preflight | stub | none | Exchange code, run 5 RBAC probes |
| DELETE | /v1/auth/disconnect | stub | bearer | Revoke refresh token, disconnect |

### 4.2 Scans Router (/v1/scans)

| Method | Path | Status | Auth | Description |
|---|---|---|---|---|
| POST | /v1/scans | stub | bearer | Create scan record, return scan_id |
| GET | /v1/scans/{scan_id} | stub | bearer | Poll scan status + progress |
| GET | /v1/scans | stub | bearer | List scans for subscription |

### 4.3 Collector Router (/v1/collect)

| Method | Path | Status | Auth | Description |
|---|---|---|---|---|
| POST | /v1/collect/start | stub | bearer | Trigger collector Container App Job |
| GET | /v1/collect/status/{scan_id} | stub | bearer | Collection job status |

### 4.4 Findings Router (/v1/findings)

| Method | Path | Status | Auth | Description |
|---|---|---|---|---|
| GET | /v1/findings/{scan_id} | stub | bearer | Tier-gated findings for scan |
| GET | /v1/findings/{scan_id}/summary | stub | bearer | Savings summary (Tier 1 safe) |

### 4.5 Checkout Router (/v1/checkout)

| Method | Path | Status | Auth | Description |
|---|---|---|---|---|
| POST | /v1/checkout/tier2 | implemented | bearer | Create Stripe checkout session Tier 2 |
| POST | /v1/checkout/tier3 | implemented | bearer | Create Stripe checkout session Tier 3 |
| POST | /v1/checkout/webhook | implemented | none | Stripe webhook receiver (raw body) |
| POST | /v1/checkout/portal | implemented | bearer | Stripe billing portal redirect |
| GET | /v1/checkout/entitlements/{sub_id} | implemented | bearer | Check customer tier |

### 4.6 Admin Router (/v1/admin)

| Method | Path | Status | Auth | Description |
|---|---|---|---|---|
| GET | /v1/admin/tenants | stub | admin | List all registered tenants |
| GET | /v1/admin/scans | stub | admin | List all scans across tenants |
| POST | /v1/admin/lock/{scan_id} | stub | admin | Lock scan record (immutable) |
| DELETE | /v1/admin/tenant/{tenant_id} | stub | admin | Soft-delete tenant data |

### 4.7 Delivery Router (/v1/delivery) -- MISSING, needs implementation

| Method | Path | Status | Auth | Description |
|---|---|---|---|---|
| GET | /v1/deliverables/{deliverable_id} | missing | bearer | Get SAS URL for Tier 3 ZIP |
| POST | /v1/delivery/trigger/{scan_id} | stub | bearer | Trigger delivery job |

---

## 5. FastAPI App Structure

```
services/api/app/
  main.py             -- FastAPI app factory, router mounts, CORS, middleware
  routers/
    auth.py           -- /v1/auth/*
    scans.py          -- /v1/scans/*
    collector.py      -- /v1/collect/*
    findings.py       -- /v1/findings/*
    checkout.py       -- /v1/checkout/*
    admin.py          -- /v1/admin/*
  middleware/
    tenant.py         -- subscriptionId injection from auth token (MISSING -- needs create)
    tier_gate.py      -- request-level tier enforcement (MISSING -- needs create)
  models/
    scan.py           -- ScanRecord, ScanStatus Pydantic models
    finding.py        -- Finding, FindingTier1, FindingTier2, FindingTier3
    entitlement.py    -- Entitlement, TierEnum
  db/
    cosmos.py         -- Cosmos client, upsert_item, query_items, get_container
  settings.py         -- pydantic-settings (ACA_COSMOS_URL, STRIPE_SECRET_KEY, etc.)
```

---

## 6. Critical Code Patterns

### Pattern 1: Tenant Isolation Middleware

```python
# services/api/app/middleware/tenant.py
from fastapi import Request, HTTPException

def get_subscription_id(request: Request) -> str:
    sub_id = getattr(request.state, "subscription_id", None)
    if not sub_id:
        raise HTTPException(status_code=403, detail="No subscription context")
    return sub_id
```

### Pattern 2: Tier Gating on Findings

```python
# services/api/app/routers/findings.py
def gate_findings(findings: list, tier: str) -> list:
    if tier == "tier1":
        return [
            {
                "id": f["id"],
                "title": f["title"],
                "category": f["category"],
                "estimated_saving_low": f["estimated_saving_low"],
                "estimated_saving_high": f["estimated_saving_high"],
                "effort_class": f["effort_class"],
            }
            for f in findings
        ]
    if tier == "tier2":
        return [
            {k: v for k, v in f.items() if k != "deliverable_template_id"}
            for f in findings
        ]
    return findings  # tier3: full object including deliverable_template_id
```

Tier 1 MUST NOT return: narrative, deliverable_template_id, heuristic_source (full detail).
Tier 2 MUST NOT return: deliverable_template_id.
Tier 3: all fields returned.

### Pattern 3: Cosmos Partition Safety

```python
# services/api/app/db/cosmos.py
def query_findings(sub_id: str) -> list:
    # CORRECT -- always partition-scoped
    return list(container.query_items(
        query="SELECT * FROM c WHERE c.subscriptionId = @sub",
        parameters=[{"name": "@sub", "value": sub_id}],
        partition_key=sub_id,   # MANDATORY -- never omit
    ))

def upsert_item(container_name: str, item: dict, partition_key: str) -> dict:
    # partition_key must be an explicit parameter -- not inferred from item
    container = get_container(container_name)
    return container.upsert_item(body=item, partition_key=partition_key)
```

---

## 7. Settings (pydantic-settings)

```python
# services/api/app/settings.py
class Settings(BaseSettings):
    # Cosmos
    ACA_COSMOS_URL: str
    ACA_COSMOS_KEY: str        # or COSMOS_CONN_STR for connection string mode
    ACA_COSMOS_DB: str = "aca-db"

    # Auth
    ACA_CLIENT_ID: str         # Entra app registration (pending Phase 1)
    ACA_TENANT_ID: str
    ACA_CLIENT_SECRET: str     # SP mode only

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_TIER2_PRICE_ID: str = "price_tier2_cad"
    STRIPE_TIER3_PRICE_ID: str = "price_tier3_cad"
    STRIPE_COUPON_ENABLED: bool = False

    # OpenAI
    ACA_OPENAI_ENDPOINT: str
    ACA_OPENAI_KEY: str
    ACA_OPENAI_DEPLOYMENT: str = "gpt-4o"

    # Delivery
    BLOB_CONN_STR: str          # Azure Storage connection string
    BLOB_CONTAINER: str = "aca-deliverables"
    SAS_HOURS: int = 168        # 7 days; do NOT lower below 168

    # CORS
    ACA_ALLOWED_ORIGINS: str    # comma-separated list of allowed origins
```

All secrets sourced from marcosandkv20260203 Key Vault via ACA managed identity.
Never hard-code secrets. Never log secrets.

---

## 8. Health Endpoint

```
GET /health
Response 200:
{
  "status": "ok",
  "cosmos": "reachable" | "error",
  "version": "0.1.0"
}
```

Must return HTTP 200 for ACA Container App liveness probe.

---

## 9. Known Bugs (from 2026-02-27 review)

| Bug ID | Severity | File | Description |
|---|---|---|---|
| C-05 | CRITICAL | routers/checkout.py | Duplicate @router.post("/webhook") at line 383 shadows real handler at line 149 -- revenue broken |
| C-04 | CRITICAL | analysis/main.py | FindingsAssembler missing cosmos_client arg -- TypeError every analysis run |
| C-03 | HIGH | db/cosmos.py | upsert_item has no partition_key param -- tenant isolation not enforced at code level |
| C-06 | HIGH | routers/findings.py | GET /v1/findings/{scan_id} raises 404 unconditionally -- gate_findings never called |
| C-07 | HIGH | delivery/packager.py | generate_blob_sas() invalid API call -- TypeError; SAS_HOURS=24 not 168 |

Fix C-05 and C-04 before any Tier 2/3 launch. No exceptions.

---

*See also: 02-preflight.md (auth flow), 08-payment.md (Stripe), saving-opportunity-rules.md (12 rules)*
