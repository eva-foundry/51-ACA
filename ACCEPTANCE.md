---
project: 51-ACA
last_updated: 20260311
current_gate: 13 / 17
last_audit: 20260311
mti_score: 99
p1_gates: 12 / 12 pass
---

# Acceptance Criteria

## Quality Gate Checklist

### Phase 1 Gates (P1-01 to P1-12)

| Gate | Scope | Status | Notes |
|---|---|---|---|
| P1-01 | Local development readiness | pass | Baseline completed in prior sprint evidence set |
| P1-02 | Phase 1 infrastructure deployment | pass | Bicep-based deployment evidence exists |
| P1-03 | Data collection integrity | pass | Collector and storage path validated |
| P1-04 | Analysis engine and rule stability | pass | Rule execution and findings generation validated |
| P1-05 | API and auth behavior | pass | Endpoint and auth baseline validated |
| P1-06 | Frontend critical flows | pass | Core customer/admin UI paths validated |
| P1-07 | Billing and entitlement flow | pass | Stripe flow baseline validated |
| P1-08 | Deliverable generation | pass | Tier 3 packaging path validated |
| P1-09 | Observability telemetry | pass | Telemetry stack configured and verified |
| P1-10 | Internationalization | pass | Locale framework validated |
| P1-11 | Accessibility conformance | pass | Baseline WCAG checks completed |
| P1-12 | Veritas MTI and traceability | pass | Audit executed; MTI 97, consistency restored, Epic 15 implementation gaps closed for ACA-15-001..012 |

### Phase 2+ Gates (P2-01 to P2-05)

| Gate | Scope | Status |
|---|---|---|
| P2-01 | Standalone infra cutover | planned |
| P2-02 | Performance and scale baseline | planned |
| P2-03 | Security hardening and red-team closure | planned |
| P2-04 | Compliance package and legal docs | planned |
| P2-05 | Production launch sign-off | planned |

## Required Automated Quality Criteria

- [x] All tests pass (exit 0) [EVIDENCE: `pytest services/api/tests -q --maxfail=1` -> 17 passed]
- [ ] Linting passes with no blocking violations [EVIDENCE: `ruff check services/api` currently failing]
- [ ] Code coverage is >= 80% [EVIDENCE: `evidence/api-coverage.xml` current total 56.77%]
- [x] MTI score is >= 70 [EVIDENCE: `51-ACA/.eva/trust.json` currently 99]
- [ ] Data model synchronization is complete when governance changes occur [EVIDENCE: pending sync artifact]
- [x] Documentation updated for this session (`PLAN.md`, `STATUS.md`, `ACCEPTANCE.md`)
- [x] No encoding violations introduced (ASCII safe)

## Evidence Requirements

Each gate closure must include the artifacts below:

1. Test report reference (unit, integration, and E2E where applicable)
2. Lint output reference or explicit PASS artifact
3. MTI calculation evidence (Veritas output)
4. Coverage report reference
5. Governance file diff reference for traceability

Current primary references:

1. `docs/WBS-FROM-DOCS-COMPLETE-20260311.md`
2. `docs/WBS-RECONCILIATION-20260311.md`
3. `PLAN.md`
4. `STATUS.md`
5. `README.md`

## Manual Gate Criteria

Reviewer must verify the following before approving gate progression:

1. Product acceptance: backlog scope and story priority align to commercial objectives.
2. Technical acceptance: architecture, traceability, and evidence links are internally consistent.
3. Operational acceptance: deployment and monitoring controls are sufficient for target phase.
4. Debt policy: unresolved technical debt has explicit owners, dates, and risk classification.

## Open Gate Actions (Post P1-12)

1. Normalize WBS metadata fields (`sprint`, `assignee`, `ado_id`) for done stories reported by the audit.
2. Refresh full-suite test, lint, and coverage evidence after onboarding merge.
3. Keep MTI >= 70 in ongoing sprint gate checks.
4. Promote current P1-12 evidence pack into release readiness checklist.

---

## Phase 2 Quality Gates (Production Hardening)

Phase 2 validates security, privacy, production infrastructure, and public launch readiness.

### Gate P2-01: Security Review

**Epic**: 10 (Commercial Hardening)  
**Stories**: ACA-10-001 through ACA-10-006

**Acceptance Criteria**:
- [ ] Red-team testing passed (tier bypass, tenant isolation verified)
- [ ] Stripe webhook signature validation enforced
- [ ] Admin token rotation implemented (90-day schedule)
- [ ] SQL injection prevention verified (parameterized queries only)
- [ ] CSP header enforced (blocking unauthorized scripts)
- [ ] Security audit report published with 0 critical findings

**Verification**: Security team review + penetration testing

**Status**: 🔶 **NOT STARTED**

---

### Gate P2-02: Privacy Compliance

**Epic**: 10 (Commercial Hardening)  
**Stories**: ACA-10-007 through ACA-10-012

**Acceptance Criteria**:
- [ ] Privacy policy published in all 5 locales
- [ ] Terms of service published in all 5 locales
- [ ] Data retention policy enforced (90-day TTL on Cosmos containers)
- [ ] Data deletion on disconnect functional (DELETE all tenant data)
- [ ] GA4 IP anonymization enabled, 14-month retention configured
- [ ] Clarity GDPR compliance verified (recordings deletable on request)

**Verification**: Legal team review + privacy audit

**Status**: 🔶 **NOT STARTED**

---

### Gate P2-03: Phase 2 Infrastructure

**Epic**: 11 (Phase 2 Infra)  
**Stories**: ACA-11-001 through ACA-11-009

**Acceptance Criteria**:
- [ ] Terraform provisioning completes without error
- [ ] Custom domains configured (app.aca.example.com, api.aca.example.com)
- [ ] TLS certificates valid and auto-renewing
- [ ] Cosmos geo-replication configured (3 regions, automatic failover)
- [ ] APIM instance dedicated to ACA with tier policies
- [ ] GitHub Actions OIDC authentication to private subscription
- [ ] Phase 2 smoke test passed (full Tier 1→Tier 3 flow)
- [ ] Phase 1 rollback tested

**Verification**: Terraform apply + smoke test + rollback test

**Status**: 🔶 **NOT STARTED**

---

### Gate P2-04: Data Model Integration

**Epic**: 12 (Data Model)  
**Stories**: ACA-12-001 through ACA-12-034

**Acceptance Criteria**:
- [ ] All 281 stories seeded to Data Model WBS layer
- [ ] Feature flags layer operational (runtime feature gating)
- [ ] Rules layer synchronized with analysis service
- [ ] Endpoints layer reflects live API surface
- [ ] Containers layer documents Cosmos schema
- [ ] Safe cleanup/restore workflow tested (Stories ACA-12-029 through ACA-12-034)
- [ ] Veritas audit score ≥70 (production threshold)
- [ ] Evidence complete for all stories

**Verification**: Run Veritas audit, verify MTI ≥70

**Status**: 🔶 **IN PROGRESS** (partial - ongoing Epic 12 work)

---

### Gate P2-05: Public Launch Readiness

**Epic**: 15 (Onboarding and Launch)  
**Stories**: ACA-15-001 through ACA-15-011

**Acceptance Criteria**:
- [ ] Phase 2 cutover complete (DNS switched, rollback tested)
- [ ] Marketing site live at aca.example.com
- [ ] GA4 production property operational with conversion tracking
- [ ] Clarity production project operational with privacy masking
- [ ] Status page integrated (uptime metrics visible)
- [ ] Onboarding wizard tested (new user flow)
- [ ] Demo subscription available (no Azure connection required)
- [ ] First-scan notification email working
- [ ] Upgrade flow A/B test completed, winner deployed
- [ ] Referral program operational ($10 credit mechanics verified)
- [ ] Launch announcement published

**Verification**: Full end-to-end launch simulation + stakeholder approval

**Status**: 🔶 **NOT STARTED**

---

## Quality Metrics

### Code Quality

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Unit Test Coverage** | ≥80% | TBD | ⏳ |
| **Integration Test Coverage** | ≥70% | TBD | ⏳ |
| **E2E Test Coverage** | ≥50% | TBD | ⏳ |
| **Lighthouse Performance** | ≥90 | TBD | ⏳ |
| **Lighthouse Accessibility** | ≥90 | TBD | ⏳ |
| **Lighthouse Best Practices** | ≥90 | TBD | ⏳ |
| **Lighthouse SEO** | ≥90 | TBD | ⏳ |
| **axe-core Violations** | 0 | 0 | ✅ |
| **ESLint Errors** | 0 | TBD | ⏳ |
| **Pylint Score** | ≥8.0 | TBD | ⏳ |

### Security Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Critical CVEs** | 0 | 0 | ✅ |
| **High CVEs** | 0 | 0 | ✅ |
| **OWASP Top 10 Compliance** | 100% | TBD | ⏳ |
| **Dependency Scan Frequency** | Daily | Daily | ✅ |
| **Secret Scanning** | Enabled | Enabled | ✅ |
| **Code Scanning (CodeQL)** | Enabled | Enabled | ✅ |

### Reliability Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Uptime SLA** | ≥99.9% | TBD | ⏳ |
| **Mean Time to Recovery (MTTR)** | <15 min | TBD | ⏳ |
| **Error Rate** | <0.1% | TBD | ⏳ |
| **API Response Time (p95)** | <500ms | TBD | ⏳ |
| **API Response Time (p99)** | <1000ms | TBD | ⏳ |

### Governance Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **MTI Score (Veritas)** | ≥70 | TBD | ⏳ |
| **Evidence Completeness** | 100% | TBD | ⏳ |
| **Story Coverage** | 100% | 72% | 🔶 |
| **Function Points Delivered** | 1,382 | 817 | 🔶 |
| **H2→Feature Compliance** | 100% | 100% | ✅ |
| **H3→Story Compliance** | 100% | 100% | ✅ |

---

## Testing Strategy

### Unit Tests
- **Scope**: Individual functions, classes, components
- **Framework**: pytest (Python), Jest (JS)
- **Target Coverage**: ≥80%
- **Run Frequency**: Every commit (pre-commit hook + CI)

### Integration Tests
- **Scope**: API endpoints, database operations, inter-service communication
- **Framework**: pytest + FastAPI TestClient (Python), Supertest (JS)
- **Target Coverage**: ≥70%
- **Run Frequency**: Every PR (CI)

### End-to-End Tests
- **Scope**: Critical user flows (login, scan, view findings, upgrade, download)
- **Framework**: Playwright
- **Target Coverage**: ≥50% of user flows
- **Run Frequency**: Every release (CI + nightly)

### Performance Tests
- **Scope**: API response times, database query performance, frontend load times
- **Framework**: Locust (load testing), Lighthouse (frontend)
- **Target**: API p95 <500ms, frontend load <3s
- **Run Frequency**: Weekly + before major releases

### Security Tests
- **Scope**: OWASP Top 10, dependency vulnerabilities, secret scanning
- **Framework**: OWASP ZAP, Dependabot, GitHub Advanced Security
- **Target**: 0 critical/high vulnerabilities
- **Run Frequency**: Daily (dependency scan), weekly (OWASP ZAP), continuous (secret scan)

### Accessibility Tests
- **Scope**: WCAG 2.1 AA compliance, keyboard navigation, screen reader
- **Framework**: axe-core (automated), NVDA/JAWS (manual)
- **Target**: 0 axe-core violations, manual test pass
- **Run Frequency**: Every PR (axe-core CI), monthly (manual)

---

## Definition of Done (Story-Level)

A story is considered "done" when ALL of the following are met:

1. **Code Complete**:
   - [ ] Implementation matches acceptance criteria
   - [ ] Code reviewed and approved
   - [ ] No merge conflicts
   - [ ] Commit tagged with `# EVA-STORY: ACA-NN-NNN` (Python) or `// EVA-STORY: ACA-NN-NNN` (JS/TS)

2. **Tests Pass**:
   - [ ] Unit tests written and passing (≥80% coverage for new code)
   - [ ] Integration tests passing (if applicable)
   - [ ] E2E tests passing (if user-facing feature)
   - [ ] CI green (all checks passed)

3. **Documentation Updated**:
   - [ ] README updated (if public interface changed)
   - [ ] API docs updated (if endpoint added/changed)
   - [ ] Code comments added for complex logic
   - [ ] Changelog entry added

4. **Evidence Logged**:
   - [ ] Evidence record created in Data Model (commit SHA, test results, artifacts)
   - [ ] Story status updated to "done" in WBS layer
   - [ ] Screenshot/video captured (if UI change)

5. **Deployed** (if releasable):
   - [ ] Merged to main branch
   - [ ] Deployed to Phase 1 (or Phase 2 if applicable)
   - [ ] Smoke test passed in deployed environment

---

## Definition of Done (Epic-Level)

An epic is considered "done" when ALL of the following are met:

1. **All Stories Complete**:
   - [ ] 100% of stories in epic marked "done"
   - [ ] All acceptance criteria verified

2. **Quality Gate Passed**:
   - [ ] Associated Phase 1 or Phase 2 gate passed
   - [ ] Manual review approved (if required)

3. **Documentation Complete**:
   - [ ] Epic summary published
   - [ ] Architecture decisions documented
   - [ ] Lessons learned captured

4. **Evidence Complete**:
   - [ ] Evidence records for all stories uploaded to Data Model
   - [ ] Veritas audit score reflects epic completion

5. **Stakeholder Acceptance**:
   - [ ] Demo completed and approved
   - [ ] Feedback incorporated

---

## Sign-Off Requirements

### Phase 1 Sign-Off
**Required Approvals**: Project Owner, Technical Lead  
**Criteria**:
- All 12 Phase 1 gates passed
- MTI score ≥60 (post-regeneration baseline acceptable)
- No critical blockers

**Approval Date**: TBD

---

### Phase 2 Sign-Off
**Required Approvals**: Project Owner, Technical Lead, Security Team, Legal Team  
**Criteria**:
- All 5 Phase 2 gates passed
- MTI score ≥70 (production threshold)
- Security audit completed with 0 critical findings
- Privacy compliance verified
- Public launch approved

**Approval Date**: TBD

---

## Lessons Learned (Quality Assurance)

### Lesson L-001: Early Accessibility Testing
**Context**: a11y issues discovered late in Epic 5 (Frontend) required significant rework  
**Lesson**: Integrate axe-core into CI early (Story ACA-05-001), run on every PR  
**Action**: Added axe-core to CI in Sprint 46, no rework since

### Lesson L-002: Tier Enforcement Caching
**Context**: Repeated Cosmos queries for tier check added 200ms latency  
**Lesson**: Cache tier metadata in APIM for 60s (Story ACA-04-016)  
**Action**: Latency reduced to <10ms for tier check

### Lesson L-003: Modular PLAN Structure
**Context**: Single PLAN.md file would exceed 2,000 lines for 281 stories  
**Lesson**: Adopt modular structure (PLAN.md index + PLAN-01 through PLAN-05) for maintainability  
**Action**: Implemented in Sprint 48 governance regeneration

---

**Document Status**: Regenerated 2026-03-11 per ground-up governance refresh. Awaiting Veritas audit verification (Gate P1-12).
