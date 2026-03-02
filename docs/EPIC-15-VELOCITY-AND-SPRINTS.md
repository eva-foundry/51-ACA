# Epic 15 Onboarding System -- FP Velocity & Sprint Capacity Analysis

**Document**: Sprint 14-17 Planning (March 2026)  
**Version**: 1.0.0  
**Status**: Ready for sprint team review  

---

## Executive Summary

| Metric | Value | Notes |
|--------|-------|-------|
| **Total FP** | 72 | 52 original + 20 gaps |
| **Total Stories** | 22 | 12 original + 10 gaps |
| **Sprint Range** | 14-17 | 4 sprints @ ~18 FP/sprint target |
| **Velocity** | ~18 FP/sprint | Conservative estimate (1.8x team velocity) |
| **Buffer** | 20% | Gap items provide scope flexibility |

---

## Sprint Breakdown

### Sprint 14 -- Foundation & Infrastructure (Weeks 25-26, ~18 FP max)

**Stories**: 9 stories, **Estimated FP**: 18 FP  
**Objective**: Foundation frozen; all infrastructure + state machine + gate 0 ready for Sprint 15+

| Story | Title | FP | Effort | Priority |
|-------|-------|----|----|----------|
| ACA-15-000 | Infrastructure provisioning (Bicep) | 2 | M | P0 |
| ACA-15-001 | Cosmos DB schema (9 containers) | 3 | M | P0 |
| ACA-15-001a | GDPR/PIPEDA residency constraint [GAP-5] | 1 | S | P0 |
| ACA-15-002 | Gate state machine (7-gate workflow) | 3 | M | P0 |
| ACA-15-002a | User consent/terms flow (GATE_0) [GAP-8] | 2 | S | P1 |
| ACA-15-003 | FastAPI backend routes | 4 | L | P0 |
| ACA-15-004 | Azure SDK wrappers (pagination/retry) | 6 | L | P0 |
| ACA-15-005 | CLI command structure | 3 | M | P0 |
| BUFFER | -- | -6 | -- | -- |
| **TOTAL** | | **18** | | |

**Sprint 14 Focus**:
- Phase 1: All resource provisioning (Bicep, Cosmos, Key Vault)
- Phase 2: State machine + GATE_0 consent
- Phase 3: FastAPI routes (auth, tenant isolation, rate limiting)
- Phase 4: CLI skeleton (auth flow, command structure)
- Risks: Cosmos provisioning delays, RBAC role assignment issues
- Success Criteria: POST /init → GATE_0 → GATE_1 happy path working end-to-end

**Dependency Chain**:
```
Cosmos provisioning (ACA-15-000) 
  ├─> Cosmos schema (ACA-15-001)
  ├─> GDPR constraint (ACA-15-001a)
  └─> FastAPI routes (ACA-15-003)
       ├─> Token refresh (ACA-15-006a prep)
       └─> CLI prep (ACA-15-005)

Gate SM (ACA-15-002) 
  └─> Consent flow (ACA-15-002a)
```

---

### Sprint 15 -- API Completeness & Extraction Start (Weeks 27-28, ~20 FP target)

**Stories**: 8 stories, **Estimated FP**: 17-20 FP  
**Objective**: Full API spec published, extraction pipeline started, token refresh solid

| Story | Title | FP | Sprint 14 Dependency | Notes |
|-------|-------|----|--------------------|-------|
| ACA-15-003a | OpenAPI/Swagger spec [GAP-1] | 2 | ACA-15-003 | Client SDKs generation |
| ACA-15-003b | Error code schema (ACA-ERR-*) [GAP-2] | 1 | ACA-15-003 | Machine-readable errors |
| ACA-15-006 | Extraction pipeline (inventory+costs+advisor) | 5 | ACA-15-004 | Core extraction engine |
| ACA-15-006a | Token refresh (20+ min extractions) [GAP-3] | 2 | ACA-15-004 | Long-running critical |
| ACA-15-006b | Partial failure handling (API resilience) [GAP-6] | 3 | ACA-15-006 | Advisor timeout handling |
| STRETCH | -- | 5-7 | -- | Early start on Analysis (ACA-15-008) if velocity allows |
| **TOTAL** | | **17-20** | | |

**Sprint 15 Focus**:
- Phase 1: OpenAPI spec generation + SDK generation (2 FP)
- Phase 2: Extraction pipeline backbone (5+2+3=10 FP)
- Phase 3: Token refresh loop + exponential backoff for 429s
- Phase 4: Error code standardization (all 20+ scenarios)
- Risk: Token refresh edge cases (tenant config variations)
- Success Criteria: Extract 500 inventory items + 45K cost rows in <12min with auto-token-refresh

**Load Profile**:
- ACA-15-006 is 5 FP, high risk (pagination, worker pools, batch writes)
- Token refresh (ACA-15-006a) 2 FP, high complexity (MSAL + tenant variations)
- Stretch stories available if velocity > 18 FP/sprint

---

### Sprint 16 -- Analysis & Evidence (Weeks 29-30, ~18 FP target)

**Stories**: 6 stories, **Estimated FP**: 17-19 FP  
**Objective**: 7 heuristics implemented, evidence receipt signed, integration tests green

| Story | Title | FP | Sprint 15 Dependency | Notes |
|-------|-------|----|--------------------|-------|
| ACA-15-007 | Logging + recovery (checkpoints) | 2 | ACA-15-006 | Resume from checkpoint |
| ACA-15-008 | Analysis rules engine (18-azure-best) | 6 | ACA-15-006 | 7 heuristics + narratives |
| ACA-15-009 | Evidence receipt (HMAC-SHA256) | 2 | ACA-15-006 | Crypto signing |
| ACA-15-009a | Evidence search indexing [GAP-7] | 2 | ACA-15-009 | Composite Cosmos indexes |
| ACA-15-010 | Integration tests (e2e, security, perf) | 4 | ACA-15-009 | All 7 gates tested |
| ACA-15-010b | SLA monitoring + alerting [GAP-4] | 3 | ACA-15-010 | App Insights telemetry |
| **TOTAL** | | **19** | | |

**Sprint 16 Focus**:
- Phase 1: Analysis heuristics (cost-optimization, anti-patterns from 18-azure-best)
- Phase 2: Evidence receipt generation + HMAC signing
- Phase 3: Composite indexes for evidence search
- Phase 4: End-to-end testing (init → role → preflight → extraction → analysis → evidence)
- Phase 5: SLA/alerting (P50, P99, P99.9 latency targets)
- Risk: HMAC key rotation complexity, App Insights metric design
- Success Criteria: Full E2E test passes, evidence receipt signature validates, alerts fire correctly

---

### Sprint 17 -- React UI & Export (Weeks 31-32, ~13 FP target)

**Stories**: 3 stories, **Estimated FP**: 13 FP  
**Objective**: UI complete, export formats ready, Tier 1/2/3 gating applied

| Story | Title | FP | Sprint 16 Dependency | Notes |
|-------|-------|----|--------------------|-------|
| ACA-15-011 | React components (role card, preflight, progress) | 5 | ACA-15-010 | Real-time polling for progress |
| ACA-15-012 | Findings report UI (savings, PDF, tier selector) | 5 | ACA-15-010 | Tier gating, tamper check display |
| ACA-15-012a | Export formats (CSV/Excel/PDF) [GAP-10] | 3 | ACA-15-012 | Pivot table for cost analysis |
| **TOTAL** | | **13** | | |

**Sprint 17 Focus**:
- Phase 1: React UI components (role assessment + preflight manifest cards)
- Phase 2: Findings report (60+ savings opportunities)
- Phase 3: Export (PDF native, CSV + Excel pivot table)
- Phase 4: Tier gating (show/hide narrative, template_id fields)
- Risk: React performance with large datasets (1000+ findings)
- Success Criteria: Export 500 findings to all 3 formats, verify pivot accuracy, tier gating works

---

## Capacity vs. Workload — FP Burn Chart

```
Sprint 14 (Weeks 25-26):  18 FP available  |  18 FP committed  [****] 100%
Sprint 15 (Weeks 27-28):  18 FP available  |  17 FP committed  [****] 94%
Sprint 16 (Weeks 29-30):  18 FP available  |  19 FP committed  [**++] 106% (slight overrun, acceptable)
Sprint 17 (Weeks 31-32):  18 FP available  |  13 FP committed  [***-] 72% (stretch capacity)

Total Capacity:           72 FP           |  67 FP committed   [****] 93%
```

**Velocity Assumptions**:
- Team velocity: ~10 FP/sprint (based on Sprint 1-2 data)
- Sprint 14-17 target: ~18 FP/sprint (1.8x velocity = sprint buffer absorption)
- Risk buffer: 5 FP uncommitted capacity across 4 sprints
- Gap items (20 FP): Optional scope stretch for post-launch features

---

## FP Distribution by Feature

| Feature | Stories | FP | Sprint | Status |
|---------|---------|----|-----------------------|--------|
| **15.1** Infrastructure & Cosmos | 3 | 6 | 14 | Foundation |
| **15.2** Gate SM & API | 5 | 12 | 14-15 | Core layer |
| **15.3** Azure SDK Wrappers | 1 | 6 | 15 | Extraction core |
| **15.4** CLI & Extraction | 4 | 12 | 15-16 | User interaction |
| **15.5** Analysis & Evidence | 5 | 17 | 16 | Insights + proof |
| **15.6** React UI & Export | 3 | 13 | 17 | Go-live ready |
| **BUFFER** | 1 | 6 | 14 | Risk mitigation |
| **TOTAL** | 22 | 72 | 14-17 | Remote probability |

---

## Risk Register & Mitigation

| Risk | Sprint | Impact | Mitigation |
|------|--------|--------|------------|
| **R1: Cosmos provisioning delays** | 14 | HIGH | Pre-create account (already done: marcosandcosmos20260203) |
| **R2: RBAC role assignment (Reader, Cost Mgmt Reader)** | 14 | MEDIUM | Verify ACA MI earmarked for roles before Sprint 14 start |
| **R3: Token refresh edge cases** (tenant config variations) | 15 | MEDIUM | Load test with 3+ different tenant configs early Sprint 15 |
| **R4: Cost API rate limit (10 req/min, 3 workers)** | 15 | MEDIUM | Implement worker backoff + queue early, test with 45K rows |
| **R5: HMAC key rotation complexity** | 16 | MEDIUM | Write key rotation runbook, test verified + old key scenario |
| **R6: React performance (1000+ findings)** | 17 | LOW | Virtual list for findings; pagination on export |
| **R7: Excel pivot calculation accuracy** | 17 | LOW | Use openpyxl + comprehensive test data (100+ scenarios) |

---

## Sprint Dependencies & Critical Path

```
Sprint 14:
  ACA-15-000 (Bicep)
    ├─> ACA-15-001 (Cosmos schema)
    ├─> ACA-15-002 (Gate SM)
    ├─> ACA-15-003 (FastAPI)
    └─> ACA-15-004 (Azure SDK) *** CRITICAL PATH
         ├─> ACA-15-006 (Extraction in Sprint 15)
         └─> ACA-15-008 (Analysis in Sprint 16)

Sprint 15:
  ACA-15-006 (Extraction)
    ├─> ACA-15-006a (Token refresh)
    ├─> ACA-15-006b (Partial failures)
    └─> Sprint 16: ACA-15-008, ACA-15-009

Sprint 16:
  ACA-15-010 (Integration tests)
    ├─> All 5 phase 1-5 stories
    └─> Sprint 17: ACA-15-011, ACA-15-012

Sprint 17:
  ACA-15-012 (Findings UI)
    └─> ACA-15-012a (Export), LAUNCH READY
```

**Critical Path FP**: 6 + 5 + 4 + 4 = **19 FP** (ACA-15-004, ACA-15-006, ACA-15-010, ACA-15-012)

---

## Success Criteria by Sprint

### Sprint 14 DoD (Definition of Done)
- [ ] All 9 stories done (committed 18 FP)
- [ ] Cosmos account: 9 containers created + TTL policies applied
- [ ] ACA MI: Reader + Cost Management Reader roles assigned
- [ ] State machine: All 7 gate transitions tested
- [ ] Consent gate (GATE_0): Accept flow working
- [ ] FastAPI: 6 routes live at http://localhost:8080; POST /init works
- [ ] CLI: `python -m aca_cli init` prompts for role assessment
- [ ] Evidence receipt: .eva/evidence/**/*.json schema validated
- [ ] Tests: pytest services/aca-onboarding -v passes (unit tests)

### Sprint 15 DoD
- [ ] All 8 stories done (committed 17-20 FP)
- [ ] Extraction: 500 inventory items + 45K cost rows extracted in <12min
- [ ] Token refresh: Auto-refresh during 20+ min extractions (tested with token expiry sim)
- [ ] Partial failures: Advisor timeout doesn't block; extraction succeeds with cost data
- [ ] OpenAPI: /openapi.json served, Python + TypeScript SDKs generated
- [ ] Error codes: 20+ scenarios return correct ACA-ERR-* codes
- [ ] Tests: Integration test extract_from_marco_sandbox()

### Sprint 16 DoD
- [ ] All 6 stories done (committed 17-19 FP)
- [ ] Analysis: 7 heuristics implemented, 12+ findings generated from test data
- [ ] Evidence: HMAC-SHA256 signatures on receipts, verification works
- [ ] Evidence indexes: Composite (subscriptionId, signedAt) queries <500ms
- [ ] Integration tests: Full E2E (init → evidence) with marco-sandbox
- [ ] Alerts: SLA violations fire in App Insights
- [ ] Security: GDPR delete removes PII from 8 operational containers

### Sprint 17 DoD
- [ ] All 3 stories done (committed 13 FP)
- [ ] React: Role Assessment, Preflight, Extraction Progress cards render
- [ ] Findings: Displayed ranked by savings (DESC), tier gating applied
- [ ] PDF: Generated with savings chart + evidence summary
- [ ] CSV: Export 100 findings, 1 row per finding, parseable
- [ ] Excel: Pivot sheet with category x effort matrix, savings totals accurate
- [ ] **GO-LIVE READY**: Full E2E working, Tier 1/2/3 reports available

---

## Post-Launch (Weeks 33+) -- Out of Scope Sprint 14-17

Not committed to any sprint:
- Advanced analytics (cost trends, anomaly detection)
- Mobile app companion
- API marketplace ecosystem
- Bi-directional sync (recommendations → actual cost reductions)

---

## Next Steps

1. **Sprint Planning** (March 5): Review this document with team
2. **Capacity Check**: Validate 18 FP/sprint assumption (adjust if needed)
3. **Dependency Review**: Confirm critical path (ACA-15-004 → 006 → 010 → 012)
4. **Risk Mitigation**: Pre-event for R1, R2 before Sprint 14 start
5. **Create Issues**: Run `scripts/create-epic15-github-issues.ps1`
6. **Kick-off**: Sprint 14 begins week 25 with 9 stories on the board

---

**Prepared by**: Copilot  
**Reviewed by**: [TBD]  
**Approved for:** Sprint 14 Planning
