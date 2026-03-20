# ACA Production Admin Pack

This pack contains a production-oriented starter for the **ACA admin surface**:
- FastAPI admin router with role guards
- Entra/JWT dependency stub points
- Cosmos-backed repository interfaces
- Admin audit events
- React admin shell with pages
- Fluent-friendly plain React structure
- OpenAPI spec for admin endpoints
- Wiring notes

## Included routes
- `/admin/dashboard`
- `/admin/customers`
- `/admin/billing`
- `/admin/runs`
- `/admin/audit`

## Included API
- `GET /v1/admin/kpis`
- `GET /v1/admin/customers`
- `GET /v1/admin/customers/{subscriptionId}`
- `POST /v1/admin/entitlements/grant`
- `POST /v1/admin/subscriptions/lock`
- `POST /v1/admin/subscriptions/unlock`
- `POST /v1/admin/reconcile/stripe`
- `GET /v1/admin/runs`
- `GET /v1/admin/audit`

## Production notes
- Frontend route hiding is UX only. Backend RBAC is authoritative.
- Replace the Entra JWT stub with your tenant-specific validation.
- Keep admin actions audited.
- Do not expose raw Azure identifiers, resource names, or tenant IDs in admin UI.

## Wire into FastAPI
```python
from app.routers import admin
app.include_router(admin.router)
```

## Wire into React
Mount `AdminApp` at `/admin/*`.
