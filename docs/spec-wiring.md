# ACA Data Model Cross-Layer Wiring Specification
<!-- EVA-STORY: ACA-12-021 -->

This document is the authoritative reference for all cross-layer relationships in the ACA
data model.  It is the source used to populate the `seed-from-plan.py` DEFS blocks.
Every sprint that adds a new endpoint, container, screen, hook, or feature flag MUST
update both this doc and the corresponding DEF in the seed script in the same commit.

---

## 1. Kanban Evidence Chain (DoD-to-Source)

Reading right-to-left: to close a story as Done the evidence must exist at every layer.

```
[DoD gate]
  <- screen renders correct data              (screens.api_calls wired)
  <- endpoint returns gated response          (endpoints.status=implemented)
  <- endpoint reads/writes container          (endpoints.cosmos_reads/writes)
  <- container holds correct field set        (containers.fields)
  <- analysis job wrote findings              (agents -> containers.findings)
  <- collector job wrote inventory            (agents -> containers.inventories/cost-data/advisor)
  <- subscription connected by user           (auth endpoints -> containers.clients)
  <- user paid correct tier                   (checkout endpoints -> containers.entitlements)
  <- infrastructure provisioned               (infrastructure layer)
```

Each layer in the data model maps to one column in this chain.  An empty field in any
layer means there is a gap in the evidence -- the DoD gate cannot close.

---

## 2. Endpoint -> Container Map

| Endpoint | Reads | Writes |
|---|---|---|
| GET /health | -- | -- |
| GET /v1/admin/stats | scans, clients | -- |
| DELETE /v1/admin/scans/{scan_id} | scans | scans, admin_audit_events |
| GET /v1/scans/ | scans | -- |
| GET /v1/scans/{scan_id} | scans | -- |
| POST /v1/scans/ | clients | scans |
| POST /v1/auth/connect | -- | clients |
| POST /v1/auth/preflight | clients | -- |
| POST /v1/auth/disconnect | -- | clients |
| POST /v1/checkout/tier2 | clients | entitlements, payments |
| POST /v1/checkout/tier3 | clients | entitlements, payments |
| POST /v1/checkout/webhook | stripe_customer_map | entitlements, payments, clients |
| GET /v1/checkout/entitlements | entitlements, clients | -- |
| GET /v1/findings/{scan_id} | findings, clients | -- |
| GET /v1/admin/kpis | scans, clients, entitlements | -- |
| GET /v1/admin/customers | clients | -- |
| GET /v1/admin/runs | scans | -- |
| POST /v1/admin/entitlements/grant | clients | entitlements, admin_audit_events |
| POST /v1/admin/subscriptions/{id}/lock | clients | clients, admin_audit_events |
| POST /v1/admin/stripe/reconcile | payments, entitlements | entitlements |
| POST /v1/collect/start | clients | scans |
| GET /v1/collect/status | scans | -- |
| GET /v1/reports/tier1 | findings, clients | -- |
| POST /v1/billing/checkout | clients | payments |
| GET /v1/billing/portal | clients, payments | -- |
| POST /v1/webhooks/stripe | stripe_customer_map | payments, entitlements, clients |
| GET /v1/entitlements | entitlements, clients | -- |

---

## 3. Container Field Registry

| Container | Partition Key | Key Fields |
|---|---|---|
| scans | /subscriptionId | id, subscriptionId, status, started_at, completed_at, scan_type, trigger |
| inventories | /subscriptionId | id, subscriptionId, scan_id, resource_type, resource_id, resource_name, location, properties |
| cost-data | /subscriptionId | id, subscriptionId, scan_id, date, service_name, resource_id, cost_usd, currency |
| advisor | /subscriptionId | id, subscriptionId, scan_id, recommendation_id, category, impact, short_description, resource_id |
| findings | /subscriptionId | id, subscriptionId, scan_id, rule_id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class, narrative, deliverable_template_id |
| clients | /subscriptionId | id, subscriptionId, auth_mode, status, tier, stripe_customer_id, entra_tenant_id, created_at, last_scan_at |
| entitlements | /subscriptionId | id, subscriptionId, tier, stripe_session_id, activated_at, expires_at, status |
| payments | /subscriptionId | id, subscriptionId, stripe_event_id, event_type, amount, currency, created_at, raw_payload |
| deliverables | /subscriptionId | id, subscriptionId, scan_id, tier, zip_blob_name, sas_url, sas_expires_at, sha256 |
| admin_audit_events | /subscriptionId | id, subscriptionId, actor, action, target, ts, details |
| stripe_customer_map | /stripeCustomerId | id, stripeCustomerId, subscriptionId, created_at |

Tenant isolation rule: every query MUST include partition_key=subscriptionId.
No cross-tenant query is possible at the code level (enforced by middleware).

---

## 4. Screen -> Endpoint -> Persona Map

| Screen | Route | Personas | Endpoints Called |
|---|---|---|---|
| LoginPage | / | (none) | -- |
| ConnectSubscriptionPage | /app/connect | tier1, tier2, tier3 | POST /v1/auth/connect, POST /v1/auth/preflight |
| CollectionStatusPage | /app/status/:id | tier1, tier2, tier3 | POST /v1/collect/start, GET /v1/collect/status |
| FindingsTier1Page | /app/findings/:id | tier1 | GET /v1/reports/tier1 |
| UpgradePage | /app/upgrade/:id | tier1 | POST /v1/billing/checkout |
| AdminDashboardPage | /admin/dashboard | aca-admin | GET /v1/admin/kpis |
| AdminCustomersPage | /admin/customers | aca-admin | GET /v1/admin/customers |
| AdminBillingPage | /admin/billing | aca-admin | POST /v1/admin/stripe/reconcile, GET /v1/billing/portal |
| AdminRunsPage | /admin/runs | aca-admin | GET /v1/admin/runs |
| AdminControlsPage | /admin/controls | aca-admin | POST /v1/admin/entitlements/grant, POST /v1/admin/subscriptions/{id}/lock |

---

## 5. Feature Flag -> Persona Gate

| Flag ID | Description | Granted To |
|---|---|---|
| tier1_report | Summarized savings (no narrative, no IaC) | tier1, tier2, tier3 |
| tier2_narrative | Full narrative + evidence | tier2, tier3 |
| tier3_deliverable | ZIP IaC package download | tier3 |
| admin_dashboard | Internal admin controls | aca-admin |

---

## 6. Frontend Hooks -> Endpoint Wiring

| Hook | Repo Path | Endpoints | Used By |
|---|---|---|---|
| useFindings | frontend/src/hooks/useFindings.ts | GET /v1/findings/{scan_id}, GET /v1/reports/tier1 | FindingsTier1Page |
| useScanStatus | frontend/src/hooks/useScanStatus.ts | POST /v1/collect/start, GET /v1/collect/status, GET /v1/scans/{scan_id} | CollectionStatusPage |
| useCheckout | frontend/src/hooks/useCheckout.ts | POST /v1/checkout/tier2, POST /v1/checkout/tier3, GET /v1/checkout/entitlements | UpgradePage |

---

## 7. Infrastructure Layer (Phase 1 -- marco* resources)

All resources in subscription d2d4e571 / EsDAICoE-Sandbox / canadacentral unless noted.

| Resource | Type | Phase | Notes |
|---|---|---|---|
| marco-sandbox-cosmos | Cosmos DB NoSQL | 1 | aca-db, 11 containers |
| marco-sandbox-apim | API Management | 1 | ACA product + key policy |
| marco-sandbox-openai-v2 | Azure OpenAI | 1 | GPT-4o, canadaeast |
| marco-sandbox-foundry | Azure AI Foundry | 1 | 29-foundry agents, canadaeast |
| marcosandacr20260203 | Container Registry | 1 | ACA service images |
| marcosandkv20260203 | Key Vault | 1 | ACA-CLIENT-ID, ACA-COSMOS-CONN, STRIPE-* |
| marco-sandbox-appinsights | Application Insights | 1 | Observability |
| marcosand20260203 | Storage Account | 1 | Tier 3 ZIP blob + SAS URLs |
| marcosandboxfinopshub | Storage Account | 1 | 91-day cost export landing |
| marco-sandbox-finops-adf | Data Factory | 1 | Cost ingestion pipeline |

---

## 8. Same-PR Rule

Every source change that affects a model object MUST update the model in the same commit:

- New FastAPI endpoint -> add to ENDPOINT_DEFS (with cosmos_reads/writes) + update this doc
- Stub -> implemented -> update ENDPOINT_DEFS status field + run --reseed-model
- New Cosmos field -> update CONTAINER_DEFS.fields + update section 3 above
- New React screen -> add to SCREEN_DEFS (with api_calls + personas) + update section 4
- New hook -> add to HOOK_DEFS + update section 6
- New feature flag -> add to FEATURE_FLAG_DEFS + update section 5
- New Azure resource -> add to INFRASTRUCTURE_DEFS + update section 7

Never defer. A stale model is worse than no model.
