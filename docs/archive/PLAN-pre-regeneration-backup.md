# ACA -- Azure Cost Advisor -- PLAN

**Version**: 1.0.0  
**Updated**: 2026-03-11  
**Phase**: Phase 1 Active (Core Services Build)  
**Format**: Veritas-compliant WBS (H2→Feature, H3→Story)

---

## Overview

This is the Work Breakdown Structure (WBS) for Project 51 (ACA -- Azure Cost Advisor).

The PLAN is split into 5 modules for maintainability:

| Module | Epics | Stories | File |
|--------|-------|---------|------|
| **PLAN-01** | Epics 1-3 | Foundation, Collection, Analysis | [PLAN-01.md](PLAN-01.md) |
| **PLAN-02** | Epics 4-6 | API/Auth, Frontend, Billing | [PLAN-02.md](PLAN-02.md) |
| **PLAN-03** | Epics 7-9 | Delivery, Observability, i18n/a11y | [PLAN-03.md](PLAN-03.md) |
| **PLAN-04** | Epics 10-12 | Hardening, Phase 2 Infra, Data Model | [PLAN-04.md](PLAN-04.md) |
| **PLAN-05** | Epics 13-15 | Azure Best Practices, DPDCA Agent, Onboarding | [PLAN-05.md](PLAN-05.md) |

**Total**: 15 Epics, ~281 Stories, ~1,382 Function Points

---

## Epic Summary

| Epic | Title | Stories | FP | Status |
|------|-------|---------|----|----|
| **1** | Foundation and Infrastructure | 21 | 65 | DONE |
| **2** | Data Collection Pipeline | 17 | 70 | DONE |
| **3** | Analysis Engine and Rules | 33 | 155 | PARTIAL |
| **4** | API and Auth Layer | 28 | 125 | IN PROGRESS |
| **5** | Frontend Core | 42 | 175 | IN PROGRESS |
| **6** | Monetization and Billing (Stripe) | 18 | 65 | DONE |
| **7** | Delivery Packager (Tier 3) | 9 | 80 | NOT STARTED |
| **8** | Observability and Telemetry | 14 | 55 | PARTIAL |
| **9** | i18n and a11y | 21 | 85 | IN PROGRESS |
| **10** | Commercial Hardening | 15 | 90 | NOT STARTED |
| **11** | Phase 2 Infrastructure | 9 | 100 | NOT STARTED |
| **12** | Data Model Support (app runtime) | 34 | 75 | ONGOING |
| **13** | Azure Best Practices Service Catalog | 12 | 55 | PLANNED |
| **14** | DPDCA Cloud Agent (GitHub Actions) | 10 | 65 | IN PROGRESS |
| **15** | Onboarding System (Client Onboarding SaaS) | 22 | 72 | PLANNED |

---

## Milestones

| Milestone | Target | Epic(s) | Deliverable |
|-----------|--------|---------|-------------|
| **M1.0** | Week 2 | 1 | Local dev works. Phase 1 Bicep deployed. |
| **M1.1** | Week 3 | 2 | Collector runs against EsDAICoE-Sandbox. |
| **M1.2** | Week 3 | 3 | 12 rules produce findings. Tier gate passes. |
| **M1.3** | Week 3 | 4 | All 25 API endpoints live behind APIM. |
| **M1.4** | Week 4 | 5 | All 9 frontend pages. Tier 1 flow end-to-end. |
| **M1.5** | Week 4 | 6 | Stripe checkout + webhook + entitlements live. |
| **M1.6** | Week 5 | 7 | Tier 3 ZIP delivered via SAS URL. |
| **M2.0** | Week 5 | 8 | GA4 + Clarity + App Insights all live. |
| **M2.1** | Week 6 | 9 | EN + FR live. axe-core CI gate green. |
| **M2.2** | Week 7 | 10 | Red-team passes. Privacy docs published. |
| **M3.0** | Week 10 | 11 | Phase 2 infra live. Custom domain active. |

---

## Story ID Format

- **Pattern**: `ACA-NN-NNN` where NN = epic number (01-15), NNN = sequential within epic
- **Commit Tag**: `# EVA-STORY: ACA-NN-NNN` (Python) or `// EVA-STORY: ACA-NN-NNN` (JS/TS)
- **Status Values**: not-started, in-progress, done

---

## Function Point Sizing

| Size | FP | Description |
|------|----|----|
| **XS** | 1 | Config only, flag, env var |
| **S** | 3 | Single route, simple model |
| **M** | 5 | Feature + unit tests |
| **L** | 9 | Cross-service integration |
| **XL** | 20 | Major integration: multi-service + UI + tests |

---

## Dependencies

1. **14-az-finops** -- saving-opportunities.md (seeded all 12 rules)
2. **18-azure-best** -- 11-module playbook (infra patterns, APIM, Terraform)
3. **Azure AI Foundry Agent SDK** -- AI agent framework for collection/analysis/generation/redteam
4. **Fluent UI v9** -- Microsoft component library for React 19 frontend
5. **48-eva-veritas** -- Traceability (audit_repo gates trust score)
6. **Stripe account** (marco production) -- needed before M1.5
7. **Google Analytics 4** property ID (existing marco account) -- needed at M2.0
8. **Microsoft Clarity** project ID (existing marco account) -- needed at M2.0
9. **Private Azure subscription** for Phase 2 -- needed before M3.0
10. **GitHub Models API token** (GITHUB_TOKEN) -- consumed by Epic 14 DPDCA agent

---

## Key Decisions (Locked)

1. **Multi-tenant architecture**: authority=common (any Microsoft tenant can sign in)
2. **Cosmos partition strategy**: subscriptionId for all tenant-scoped data
3. **Tier enforcement**: APIM policies + 60s entitlement cache
4. **IaC templates**: Bicep only in Phase 1, Terraform deferred to Phase 2
5. **i18n locales**: EN, FR, PT-BR, ES, DE (5 total)
6. **a11y standard**: WCAG 2.1 AA with axe-core CI gate
7. **Unit test coverage**: 95% across all 12 rule modules
8. **SAS URL duration**: 168 hours (7 days) for Tier 3 deliverables
9. **Cosmos containers**: 11 total (scans, inventories, cost-data, advisor, findings, clients, deliverables, entitlements, payments, stripe_customer_map, admin_audit_events)
10. **Admin roles**: ACA_Admin, ACA_Support, ACA_FinOps

---

**For detailed story breakdowns, see individual PLAN modules:**
- [PLAN-01.md](PLAN-01.md) -- Epics 1-3 (Foundation, Collection, Analysis)
- [PLAN-02.md](PLAN-02.md) -- Epics 4-6 (API/Auth, Frontend, Billing)
- [PLAN-03.md](PLAN-03.md) -- Epics 7-9 (Delivery, Observability, i18n/a11y)
- [PLAN-04.md](PLAN-04.md) -- Epics 10-12 (Hardening, Phase 2, Data Model)
- [PLAN-05.md](PLAN-05.md) -- Epics 13-15 (Best Practices, DPDCA, Onboarding)

---

**Last Updated**: 2026-03-11 (Ground-up regeneration from docs 01-43 following Veritas audit standards)
