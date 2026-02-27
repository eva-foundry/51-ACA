# ACA Stripe Payment Backend Spec
# EVA-STORY: ACA-12-002

Version: 1.0.0
Updated: 2026-02-27
Status: AUTHORITATIVE -- agents must read this before implementing any checkout or billing story.

---

## 1. Tier Model

ACA is a gated-access SaaS with three tiers.

| Tier | Price | Purchase Type | Unlocks |
|---|---|---|---|
| Tier 1 | Free | No payment | Summary report: title, category, saving range, effort class |
| Tier 2 | CAD $499/month | Stripe subscription (recurring) | Full analysis narrative, heuristic detail |
| Tier 3 | CAD $1499 one-time | Stripe payment_intent | IaC template ZIP download, SHA-256 manifest |

Tier 3 is a one-time purchase and must never be revoked when a Stripe subscription is cancelled.
Tier 2 subscription cancellation reverts to Tier 1 only.

---

## 2. Stripe Integration Architecture

```
Frontend
  -> POST /v1/checkout/tier2 or /v1/checkout/tier3
  -> Stripe checkout.sessions.create()
  -> Client receives session.url (Stripe-hosted checkout page)
  -> User completes payment on Stripe
  -> Stripe sends webhook to POST /v1/checkout/webhook
  -> Webhook verifies signature, grants entitlement, triggers delivery (Tier 3)
  -> Frontend polls GET /v1/checkout/entitlements/{sub_id} until tier updated
```

---

## 3. Checkout Endpoints

### POST /v1/checkout/tier2

Creates a Stripe recurring subscription checkout session.

Request headers:
- Authorization: Bearer <token>
- X-Subscription-ID: <azure-subscription-id>

Request body: none required (subscriptionId from auth context)

Response 200:
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_...",
  "session_id": "cs_..."
}
```

Stripe session parameters:
```python
stripe.checkout.Session.create(
    mode="subscription",
    line_items=[{"price": STRIPE_TIER2_PRICE_ID, "quantity": 1}],
    customer_email=customer_email,
    metadata={"subscription_id": sub_id, "tier": "tier2"},
    success_url=f"{PUBLIC_APP_URL}/app/status?tier_upgrade=2",
    cancel_url=f"{PUBLIC_APP_URL}/app/findings",
    allow_promotion_codes=STRIPE_COUPON_ENABLED,
)
```

### POST /v1/checkout/tier3

Creates a Stripe one-time payment checkout session.

Same structure as tier2 except:
```python
stripe.checkout.Session.create(
    mode="payment",
    line_items=[{"price": STRIPE_TIER3_PRICE_ID, "quantity": 1}],
    metadata={"subscription_id": sub_id, "tier": "tier3"},
    payment_intent_data={"metadata": {"subscription_id": sub_id}},
    ...
)
```

### POST /v1/checkout/portal

Creates a Stripe customer portal session for subscription management.

Response 200:
```json
{
  "portal_url": "https://billing.stripe.com/p/..."
}
```

### GET /v1/checkout/entitlements/{subscription_id}

Returns current tier for a subscription. Called by frontend to poll after checkout.

Response 200:
```json
{
  "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tier": 1 | 2 | 3,
  "tier2_active": true | false,
  "tier3_purchased": true | false
}
```

---

## 4. Webhook Handler (POST /v1/checkout/webhook)

### CRITICAL: Raw Body Before JSON

The Stripe webhook signature verification REQUIRES the raw request body before
ANY JSON parsing. This is the most common cause of 400 webhook failures.

```python
@router.post("/webhook")
async def stripe_webhook(request: Request):
    raw_body = await request.body()      # MUST be first -- before JSON parsing
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload=raw_body,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    # process event
```

Do NOT call await request.json() before construct_event.
Do NOT use a dependency that consumes the body before the webhook handler.

### CRITICAL BUG (C-05)

As of 2026-02-27, services/api/app/routers/checkout.py contains a DUPLICATE
@router.post("/webhook") decorator at line 383. This stub returns {"status": "received"}
without verifying the signature. FastAPI registers the last definition, so the stub
overwrites the real handler at line 149. Stripe revenue is completely broken.

Fix: Delete lines 351-403 (the entire stub block at the bottom of checkout.py).
Story: ACA-06-HOT-01.

### Webhook Event Map

| Stripe Event | Action |
|---|---|
| checkout.session.completed | Extract session.metadata.tier, grant entitlement, trigger delivery if tier3 |
| customer.subscription.updated | Update tier2_active in entitlements |
| customer.subscription.deleted | Revoke Tier 2 only; Tier 3 one-time purchase is permanent |
| invoice.payment_failed | Set tier2_active=false temporarily; notify customer |
| payment_intent.succeeded | Confirm Tier 3 one-time purchase |

### Entitlement Grant Functions

```python
# services/api/app/services/entitlement_service.py

def grant_tier2(sub_id: str) -> None:
    existing = repo.get(sub_id)
    new_tier = max(2, existing.tier)   # never downgrade
    repo.upsert(sub_id, tier=new_tier, tier2_active=True)

def grant_tier3(sub_id: str) -> None:
    repo.upsert(sub_id, tier=3, tier3_purchased=True)
    # tier3_purchased is permanent -- never cleared

def revoke_tier2(sub_id: str) -> None:
    existing = repo.get(sub_id)
    # DO NOT clear tier3_purchased -- one-time purchase is permanent
    new_tier = 3 if existing.tier3_purchased else 1
    repo.upsert(sub_id, tier=new_tier, tier2_active=False)
```

Note: The existing entitlement_service.py has a bug in customer.subscription.deleted
handling that may incorrectly clear Tier 3 one-time entitlements. See opus review H-03.

---

## 5. Delivery Trigger on Tier 3 Purchase

When Tier 3 is granted, the webhook handler must trigger the delivery Container App Job.
Phase 1 stub returns a placeholder string. Real implementation queues the job.

```python
# services/api/app/services/delivery_service.py

async def trigger_delivery(scan_id: str, sub_id: str) -> str:
    # Phase 1 stub -- replace with real ACA job trigger
    # Real: az containerapp job start --name aca-delivery-job ...
    return f"delivery-{scan_id}-pending"
```

---

## 6. Idempotency

All webhook events must be idempotent. Stripe may replay events.

- Check entitlement state before granting -- do not double-grant
- Store Stripe event ID in payments container to detect replay
- Stripe checkout session ID must be stored on scan record to prevent duplicate charges

```python
# Idempotency check pattern
existing_payment = payments_repo.get_by_stripe_event(event["id"])
if existing_payment:
    return {"status": "already_processed"}
```

---

## 7. Environment Variables

| Variable | Required | Source |
|---|---|---|
| STRIPE_SECRET_KEY | Phase 1 (Tier 2 launch) | marcosandkv20260203 |
| STRIPE_WEBHOOK_SECRET | Phase 1 (Tier 2 launch) | marcosandkv20260203 |
| STRIPE_TIER2_PRICE_ID | Phase 1 (Tier 2 launch) | .env.example |
| STRIPE_TIER3_PRICE_ID | Phase 1 (Tier 3 launch) | .env.example |
| STRIPE_COUPON_ENABLED | optional (default false) | .env |

---

## 8. Test Coverage Required

Before Tier 2 launch:
- Webhook signature verification test (valid sig -> 200, invalid sig -> 400)
- Tier 2 grant idempotency test
- Tier 3 permanent purchase test (subscription.deleted must NOT clear tier3)
- Duplicate webhook decorator test (C-05 must be resolved first)

---

*See also: 05-technical.md (endpoint list), PLAN.md Epic 6 (billing stories)*
