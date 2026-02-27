# AGENTS.md -- services/api
# EVA-STORY: ACA-12-022

ACA API service patterns for GitHub Copilot coding agents and sprint_agent.py.
Updated: 2026-02-28 (Sprint-01 execution learnings)

---

## 1. Module Structure

```
services/api/
  app/
    db/
      cosmos.py          -- tenant-isolated Cosmos helpers (ACA-04-028)
      repos/             -- Cosmos CRUD wrappers per container
    routers/             -- FastAPI route handlers (thin -- delegates to services/)
    services/
      findings_gate.py   -- pure tier-gating logic, NO I/O (ACA-03-006)
      entitlement_service.py  -- entitlement business logic (ACA-06-018)
    middleware/          -- tenant isolation, tier gating JWT check
    models/              -- Pydantic schemas
    settings.py          -- pydantic-settings (loaded lazily, not at import time)
  tests/                 -- pytest, lives at services/tests/
```

---

## 2. Cosmos -- Tenant Isolation (MANDATORY)

Every Cosmos call MUST pass `partition_key=subscription_id`. No exceptions.

```python
# CORRECT
container.query_items(
    query="SELECT * FROM c WHERE c.subscriptionId = @sub",
    parameters=[{"name": "@sub", "value": sub_id}],
    partition_key=sub_id,  # MANDATORY -- ACA-04-028
)

# CORRECT
from app.db.cosmos import upsert_item
upsert_item(container_name, doc, partition_key=subscription_id)

# WRONG -- never infer partition key from doc
container.upsert_item(body=doc)
```

File: `app/db/cosmos.py` -- import from here, never instantiate CosmosClient directly in routers.

---

## 3. Tier Gating (ACA-03-006)

Tier-gating logic lives in `app/services/findings_gate.py` -- pure logic, no I/O.
Import it; do NOT redefine `gate_findings` inline in routers.

```python
from app.services.findings_gate import gate_findings, TIER1_FIELDS, TIER2_FIELDS

# usage in router
raw_findings: list[dict] = load_from_cosmos(scan_id, sub_id)
return gate_findings(raw_findings, client_tier)  # returns list[dict]
```

TIER1_FIELDS = {id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class}
TIER2_FIELDS = TIER1_FIELDS + {narrative, heuristic_source}
TIER3 = full pass-through

---

## 4. Service Dependency Injection Pattern (ACA-06-018)

All service classes MUST accept an injected repo for testability.
Never call `get_settings()` or `EntitlementsRepo()` in `__init__` unconditionally.

```python
# CORRECT -- DI pattern (Sprint-01 established)
class EntitlementService:
    def __init__(self, repo: "Optional[EntitlementsRepo]" = None) -> None:
        self._repo = repo if repo is not None else EntitlementsRepo()

# Usage in test (no env vars needed)
mock_repo = MagicMock()
mock_repo.get.return_value = {"tier": 2, "paymentStatus": "active", "subscriptionId": "sub-123"}
svc = EntitlementService(repo=mock_repo)

# WRONG -- breaks unit tests without Cosmos env vars
class EntitlementService:
    def __init__(self) -> None:
        self._repo = EntitlementsRepo()  # calls get_settings() immediately
```

---

## 5. Cosmos Mock Pattern for Unit Tests

Cosmos documents are plain dicts. Use dict return values in mocks, NOT MagicMock attributes.

```python
# CORRECT -- service calls doc.get("tier", 1) -- dict method
mock_repo.get.return_value = {
    "tier": 2,
    "paymentStatus": "active",
    "subscriptionId": "sub-123",
    "customerId": "cus_abc",
}

# WRONG -- doc.get() fails on MagicMock (returns MagicMock, not int)
mock_repo.get.return_value = MagicMock(tier=2)
```

---

## 6. Import Paths

`pyproject.toml` sets `pythonpath = [".", "services/api"]`.
This enables two styles -- use the FULL path in test files, RELATIVE path inside services/api:

```python
# In services/tests/*.py  (full path from repo root)
from services.api.app.services.findings_gate import gate_findings

# In services/api/app/**/*.py  (relative from services/api root)
from app.services.findings_gate import gate_findings
from app.db.cosmos import upsert_item
```

Do NOT use `from services.analysis.app.*` for API-layer logic -- wrong service.

---

## 7. Settings -- Lazy Load

`get_settings()` uses `@lru_cache`. It WILL fail without env vars if called at module
import time. Always call it inside function bodies, not at module level.

```python
# CORRECT
def get_cosmos_client() -> CosmosClient:
    s = get_settings()  # called at function call, not import
    return CosmosClient(s.cosmos_url, credential=s.cosmos_key)

# WRONG -- fails pytest collect if env var missing
s = get_settings()  # module level
client = CosmosClient(s.cosmos_url, ...)
```

---

## 8. Stripe Webhook -- Body Must Not Be Pre-Consumed

Stripe signature validation requires the raw bytes body.
Read `await request.body()` BEFORE any JSON parsing.

```python
@router.post("/webhook")
async def stripe_webhook(request: Request):
    raw_body = await request.body()  # MUST be first
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(raw_body, sig, settings.stripe_webhook_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    # only now parse JSON
    ...
```

---

## 9. EVA-STORY Tags

Every source file modified in a sprint MUST have `# EVA-STORY: ACA-NN-NNN` on a functional line.
One tag per file minimum. Multiple tags allowed if the file covers multiple stories.

```python
# EVA-STORY: ACA-04-028   <- on the FIRST functional line (not in a blank docstring)
```

Missing tag = veritas coverage gap = MTI regression.
