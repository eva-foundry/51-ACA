# ACA Admin API Spec

Base path: `/v1/admin`

## Roles
- ACA_Admin — full access
- ACA_Support — support actions and views
- ACA_FinOps — billing/KPI read access

## Endpoints
GET  /v1/admin/kpis
GET  /v1/admin/customers?query=...
GET  /v1/admin/customers/{subscriptionId}
POST /v1/admin/entitlements/grant
POST /v1/admin/subscriptions/lock
POST /v1/admin/subscriptions/unlock
POST /v1/admin/reconcile/stripe
GET  /v1/admin/runs?type=scan|analysis|delivery
GET  /v1/admin/audit
