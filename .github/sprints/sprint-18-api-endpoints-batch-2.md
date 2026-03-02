# Sprint 18 Manifest -- Feature 4.2: Core API Endpoints (Batch 2)

**Sprint**: 18  
**Feature**: 4.2 -- Azure Cost Advisor / Core Endpoints  
**Stories**: 7 (ACA-04-011 through ACA-04-016, ACA-04-017)  
**Est. FP**: 21 (3 FP per endpoint + integration testing)  
**Timeline**: 20-30 minutes (1.8 FP/min pace from prior sprints)  
**Date/Time**: March 2, 2026, 8:43 AM ET  

---

## Story 1: ACA-04-011 -- POST /v1/collect/start (Trigger Collector Job)

**Feature**: 4.2 Core Endpoints -- Trigger collection run  
**Acceptance**:
- [ ] Endpoint callable via POST /v1/collect/start
- [ ] Requires JWT auth (401 if missing)
- [ ] Body: { subscriptionId?, scanName?, description? } (subscriptionId from context if not in body)
- [ ] Returns: { scanId, status, startedAt, estimatedCompletionAt } (stub: all fields return stable test values)
- [ ] Writes to Cosmos scans container (stub: would enqueue collector job)
- [ ] Story tested in test_collect.py

**API Spec**: 
```
POST /v1/collect/start
Content-Type: application/json
Authorization: Bearer eyJ0eXAi...

Body (optional fields):
{
  "subscriptionId": "00000000-0000-0000-0000-000000000001",  // optional; default from context
  "scanName": "prod-cost-review-2026-03",
  "description": "Monthly FinOps review"
}

Response (200 OK):
{
  "scanId": "scan-001-2026-03-02-0843",
  "status": "running",
  "startedAt": "2026-03-02T08:43:00Z",
  "estimatedCompletionAt": "2026-03-02T08:55:00Z",
  "subscriptionId": "00000000-0000-0000-0000-000000000001"
}

Error (401):
{
  "detail": "Not authenticated"
}
```

**Files**:
- services/api/app/routers/collect.py (NEW) -- POST /start endpoint
- services/api/tests/test_collect.py (NEW) -- test_collect_start_authenticated, test_collect_start_missing_auth

---

## Story 2: ACA-04-012 -- GET /v1/collect/status (Poll Collection Progress)

**Feature**: 4.2 Core Endpoints -- Poll scan status  
**Acceptance**:
- [ ] Endpoint callable via GET /v1/collect/status?scanId=...
- [ ] Requires JWT auth (401 if missing)
- [ ] Params: scanId (required)
- [ ] Returns: { scanId, status, progress, startedAt, completedAt?, inventoryCount?, analysisCount? } (stub: always 100% complete)
- [ ] Reads from Cosmos scans container (stub: return hardcoded record)
- [ ] Story tested in test_collect.py

**API Spec**:
```
GET /v1/collect/status?scanId=scan-001-2026-03-02-0843
Authorization: Bearer eyJ0eXAi...

Response (200 OK):
{
  "scanId": "scan-001-2026-03-02-0843",
  "status": "completed",
  "progress": 100,
  "startedAt": "2026-03-02T08:43:00Z",
  "completedAt": "2026-03-02T08:54:00Z",
  "inventoryCount": 487,
  "analysisCount": 12
}

Error (401): Not authenticated
Error (404): Scan not found
```

**Files**:
- services/api/app/routers/collect.py (MODIFIED) -- GET /status endpoint
- services/api/tests/test_collect.py (MODIFIED) -- test_collect_status_authenticated, test_collect_status_missing_auth, test_collect_status_not_found

---

## Story 3: ACA-04-013 -- GET /v1/reports/tier1 (Tier 1 Findings Report)

**Feature**: 4.2 Core Endpoints -- Return tier-gated findings  
**Acceptance**:
- [ ] Endpoint callable via GET /v1/reports/tier1?scanId=...
- [ ] Requires JWT auth (401 if missing)
- [ ] Params: scanId (required)
- [ ] Returns: { scanId, tier, findings: [ { id, title, category, estimatedSavingLow, estimatedSavingHigh, effortClass } ], totalFindings, totalSavingRange }
- [ ] Tier 1 findings: strips narrative, deliverable_template_id, rule_id
- [ ] Reads from Cosmos findings container (stub: return 3 hardcoded findings)
- [ ] Story tested in test_reports.py

**API Spec**:
```
GET /v1/reports/tier1?scanId=scan-001-2026-03-02-0843
Authorization: Bearer eyJ0eXAi...

Response (200 OK):
{
  "scanId": "scan-001-2026-03-02-0843",
  "tier": "TIER1",
  "findings": [
    {
      "id": "finding-001",
      "title": "Dev Box instances run nights and weekends",
      "category": "compute-scheduling",
      "estimatedSavingLow": 5548,
      "estimatedSavingHigh": 7902,
      "effortClass": "trivial"
    },
    {
      "id": "finding-002",
      "title": "Storage account access tiers suboptimal",
      "category": "storage-access-tiers",
      "estimatedSavingLow": 1200,
      "estimatedSavingHigh": 2800,
      "effortClass": "easy"
    }
  ],
  "totalFindings": 3,
  "totalSavingRange": {
    "low": 6748,
    "high": 10702
  }
}

Error (401): Not authenticated
Error (404): Scan or findings not found
```

**Files**:
- services/api/app/routers/reports.py (NEW) -- GET /tier1 endpoint
- services/api/tests/test_reports.py (NEW) -- test_reports_tier1_authenticated, test_reports_tier1_gated, test_reports_tier1_not_found

---

## Story 4: ACA-04-014 -- POST /v1/billing/checkout (Stripe Checkout Session)

**Feature**: 4.2 Core Endpoints -- Create Stripe checkout for tier upgrade  
**Acceptance**:
- [ ] Endpoint callable via POST /v1/billing/checkout
- [ ] Requires JWT auth (401 if missing)
- [ ] Body: { desiredTier: "TIER2" | "TIER3" }
- [ ] Returns: { sessionId, checkoutUrl, expiresAt } (stub: returns hardcoded Stripe test URL)
- [ ] Creates Stripe CheckoutSession in sandbox (stub: return mock session ID)
- [ ] Story tested in test_billing.py

**API Spec**:
```
POST /v1/billing/checkout
Content-Type: application/json
Authorization: Bearer eyJ0eXAi...

Body:
{
  "desiredTier": "TIER2"
}

Response (200 OK):
{
  "sessionId": "cs_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "checkoutUrl": "https://checkout.stripe.com/pay/cs_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "expiresAt": "2026-03-02T09:43:00Z"
}

Error (400): Invalid tier
Error (401): Not authenticated
```

**Files**:
- services/api/app/routers/billing.py (NEW) -- POST /checkout endpoint
- services/api/tests/test_billing.py (NEW) -- test_billing_checkout_authenticated, test_billing_checkout_invalid_tier, test_billing_checkout_missing_auth

---

## Story 5: ACA-04-015 -- GET /v1/billing/portal (Stripe Billing Portal)

**Feature**: 4.2 Core Endpoints -- Redirect to Stripe customer portal  
**Acceptance**:
- [ ] Endpoint callable via GET /v1/billing/portal
- [ ] Requires JWT auth (401 if missing)
- [ ] Returns: { portalUrl, expiresAt } (stub: returns hardcoded Stripe test portal URL)
- [ ] Creates Stripe BillingPortal session (stub: return mock URL)
- [ ] Story tested in test_billing.py

**API Spec**:
```
GET /v1/billing/portal
Authorization: Bearer eyJ0eXAi...

Response (200 OK):
{
  "portalUrl": "https://billing.stripe.com/session/test_Y1NhZWEzZWFjODJfUno3q1VlPZY0UXkPxfG7",
  "expiresAt": "2026-03-02T09:43:00Z"
}

Error (401): Not authenticated
Error (500): Customer not found in Stripe
```

**Files**:
- services/api/app/routers/billing.py (MODIFIED) -- GET /portal endpoint
- services/api/tests/test_billing.py (MODIFIED) -- test_billing_portal_authenticated, test_billing_portal_missing_auth

---

## Story 6: ACA-04-016 -- POST /v1/webhooks/stripe (Stripe Event Handler)

**Feature**: 4.2 Core Endpoints -- Handle Stripe events (subscription updated, invoice paid)  
**Acceptance**:
- [ ] Endpoint callable via POST /v1/webhooks/stripe
- [ ] Does NOT require JWT (Stripe signs with HMAC-SHA256)
- [ ] Validates Stripe signature using STRIPE_WEBHOOK_SECRET
- [ ] Handles event types: customer.subscription.updated, invoice.payment_succeeded
- [ ] On subscription.updated: update entitlements in Cosmos
- [ ] On invoice.payment_succeeded: log payment record
- [ ] Returns: { status: "received" } on 200, 400 on signature fail, 500 on processing error
- [ ] Story tested in test_billing.py (no auth required for this one)

**API Spec**:
```
POST /v1/webhooks/stripe
Content-Type: application/json
Stripe-Signature: t=1614556800,v1=...

Body (Stripe event):
{
  "id": "evt_...",
  "type": "customer.subscription.updated",
  "data": {
    "object": {
      "id": "sub_...",
      "customer": "cus_...",
      "status": "active",
      "current_period_end": 1617235200
    }
  }
}

Response (200 OK):
{
  "status": "received",
  "eventId": "evt_..."
}

Error (400): Invalid Stripe signature
Error (500): Processing failed
```

**Files**:
- services/api/app/routers/webhooks.py (NEW) -- POST /stripe endpoint
- services/api/tests/test_webhooks.py (NEW) -- test_stripe_webhook_valid_signature, test_stripe_webhook_invalid_signature, test_stripe_webhook_subscription_updated

---

## Story 7: ACA-04-017 -- GET /v1/entitlements (Current Tier for Subscription)

**Feature**: 4.2 Core Endpoints -- Fetch current tier/entitlements  
**Acceptance**:
- [ ] Endpoint callable via GET /v1/entitlements
- [ ] Requires JWT auth (401 if missing)
- [ ] Returns: { subscriptionId, tier, expiresAt?, status } (stub: returns TIER1 with no expiry)
- [ ] Reads from Cosmos entitlements container (stub: return hardcoded record)
- [ ] APIM will cache this for 60s per subscriptionId
- [ ] Story tested in test_entitlements.py

**API Spec**:
```
GET /v1/entitlements
Authorization: Bearer eyJ0eXAi...

Response (200 OK):
{
  "subscriptionId": "00000000-0000-0000-0000-000000000001",
  "tier": "TIER1",
  "expiresAt": null,
  "status": "active"
}

Response (200 OK - tier2 with expiry):
{
  "subscriptionId": "00000000-0000-0000-0000-000000000002",
  "tier": "TIER2",
  "expiresAt": "2026-04-02T00:00:00Z",
  "status": "active"
}

Error (401): Not authenticated
```

**Files**:
- services/api/app/routers/entitlements.py (NEW) -- GET / endpoint
- services/api/tests/test_entitlements.py (NEW) -- test_entitlements_authenticated, test_entitlements_missing_auth

---

## Integration Testing

**File**: services/api/tests/test_core_endpoints_integration.py (NEW)
**Tests** (3-5 assertions per story):
- [ ] test_full_flow_collect_to_reports() -- collect/start -> collect/status -> reports/tier1
- [ ] test_billing_flow() -- checkout -> portal -> entitlements
- [ ] test_webhook_flow() -- POST stripe webhook -> entitlements updated
- [ ] test_all_endpoints_callable_with_auth() -- All 7 endpoints 401 without JWT, 200+ with JWT

---

## Summary

| Story | Endpoint | Method | Auth | Status |
|---|---|---|---|---|
| ACA-04-011 | /v1/collect/start | POST | JWT | NEW |
| ACA-04-012 | /v1/collect/status | GET | JWT | NEW |
| ACA-04-013 | /v1/reports/tier1 | GET | JWT | NEW |
| ACA-04-014 | /v1/billing/checkout | POST | JWT | NEW |
| ACA-04-015 | /v1/billing/portal | GET | JWT | NEW |
| ACA-04-016 | /v1/webhooks/stripe | POST | None (HMAC) | NEW |
| ACA-04-017 | /v1/entitlements | GET | JWT | NEW |

**Total Stories**: 7  
**Total FP**: 21 (3 FP per story)  
**Total Tests**: 18-20  
**Files to Create/Modify**: 10 (routers + tests)  

---

**Ready to Execute**: Proceed with DO phase.
