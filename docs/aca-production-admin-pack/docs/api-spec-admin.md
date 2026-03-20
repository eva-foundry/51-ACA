# ACA Admin API Spec

Base path: `/v1/admin`

## Roles
- `ACA_Admin` — full access
- `ACA_Support` — support actions and views
- `ACA_FinOps` — billing/KPI read access

## Endpoints

### GET /v1/admin/kpis
Returns:
- revenueMtd
- activeSubscriptions
- churnMtd
- scans24h
- analyses24h
- deliveries24h
- failureRate24h
- webhookLagSecondsP95

Access: `ACA_Admin`, `ACA_FinOps`

### GET /v1/admin/customers?query=...
Search subscriptions/customers by:
- ACA subscriptionId prefix
- Stripe customer id
- payment status

Access: `ACA_Admin`, `ACA_Support`

### GET /v1/admin/customers/{subscriptionId}
Returns:
- entitlement
- stripeCustomerId
- locked
- lastScanUtc
- lastAnalysisUtc
- lastDeliveryUtc

Access: `ACA_Admin`, `ACA_Support`

### POST /v1/admin/entitlements/grant
Manual trial/override grant.

### POST /v1/admin/subscriptions/lock
Lock a subscription to prevent execution.

### POST /v1/admin/subscriptions/unlock
Unlock a subscription.

Access: `ACA_Admin`, `ACA_Support`

### POST /v1/admin/reconcile/stripe
Reconcile Stripe status to entitlements.
Used to repair missed webhooks or drift.

Access: `ACA_Admin`

### GET /v1/admin/runs?type=scan|analysis|delivery&subscriptionId=...&status=...
List run history.

Access: `ACA_Admin`, `ACA_Support`

### GET /v1/admin/audit?subscriptionId=...
List admin audit events.

Access: `ACA_Admin`
