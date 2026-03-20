# ACCEPTANCE: Azure Commercial Advisory (Project 51-ACA)

**Last Updated**: 2026-03-11  
**Project**: 51-ACA  
**Governance Standard**: Veritas MTI Framework  
**Quality Model**: Multi-layer gates (Phase 1 + Phase 2)

---

## Overview

This document defines the acceptance criteria and quality gates for Project 51-ACA. The project follows a phased approach:

- **Phase 1**: Foundation + MVP deployment to marco* sandbox (12 gates)
- **Phase 2**: Production hardening + private subscription cutover (5 gates)

All gates must pass before advancing to the next phase. Gates are enforced via:
- **Veritas MTI Score**: ≥70 required for production launch
- **Automated Tests**: CI must be green (unit + integration + E2E)
- **Manual Review**: Security, privacy, and UX gates require human approval

---

## Phase 1 Quality Gates (Foundation + MVP)

Phase 1 validates foundation, core functionality, and initial deployment to marco* sandbox.

### Gate P1-01: Local Development Environment

**Epic**: 1 (Foundation)  
**Stories**: ACA-01-001 through ACA-01-021

**Acceptance Criteria**:
- [ ] Docker Compose starts all services without error
- [ ] `docker-compose up` completes in <60 seconds
- [ ] All 3 services (API, analysis, frontend) accessible locally
- [ ] Health endpoints return 200 OK within 5 seconds
- [ ] Hot reload operational for frontend and API
- [ ] Unit tests run via `pytest` (Python) and `npm test` (JS)

**Verification**: Run `docker-compose up` and verify all services healthy

**Status**: ✅ **PASSED** (2025-12-15)

---

### Gate P1-02: Phase 1 Infrastructure Deployment

**Epic**: 1 (Foundation)  
**Stories**: ACA-01-005 through ACA-01-009

**Acceptance Criteria**:
- [ ] `az deployment group create` on infra/phase1-marco/main.bicep succeeds
- [ ] All 11 Cosmos containers created with correct partition keys
- [ ] APIM instance operational with ACA product subscription
- [ ] Key Vault secrets accessible by Container Apps via managed identity
- [ ] Container Apps deployed and accessible via public URL
- [ ] GitHub Actions CI green (build, test, deploy)

**Verification**: Run Bicep deployment, verify all resources in Azure Portal

**Status**: ✅ **PASSED** (2025-12-20)

---

### Gate P1-03: Azure Data Collection

**Epic**: 2 (Collection)  
**Stories**: ACA-02-001 through ACA-02-017

**Acceptance Criteria**:
- [ ] Preflight checks validate Azure roles (Reader, Cost Analyst)
- [ ] Inventory collection captures all resource types (VMs, disks, NICs, NSGs, public IPs, RGs, certs)
- [ ] Cost data ingested from FinOps hub landing zone
- [ ] Advisor recommendations fetched and stored
- [ ] All collected data written to Cosmos (scans, inventories, cost-data, advisor containers)
- [ ] Collection completes in <5 minutes for 100-resource subscription

**Verification**: Trigger collection job, verify data in Cosmos containers

**Status**: ✅ **PASSED** (2026-01-05)

---

### Gate P1-04: Analysis Rules Operational

**Epic**: 3 (Analysis)  
**Stories**: ACA-03-001 through ACA-03-033

**Acceptance Criteria**:
- [ ] All 12 analysis rules (R-01 through R-12) implemented and tested
- [ ] Each rule has unit tests with ≥80% coverage
- [ ] Rules execute in parallel with correct priority order
- [ ] Findings written to Cosmos findings container
- [ ] Risk classification (Low/Medium/High/Critical) accurate
- [ ] Effort classification (Quick-Fix/Moderate/Significant) accurate
- [ ] Rule execution completes in <2 minutes for 100-resource subscription

**Verification**: Run analysis job, verify findings match expected output

**Status**: ✅ **PASSED** (2026-02-05)

---

### Gate P1-05: API Endpoints Functional

**Epic**: 4 (API/Auth)  
**Stories**: ACA-04-001 through ACA-04-028

**Acceptance Criteria**:
- [ ] All 17 core API endpoints operational (GET/POST/PUT/DELETE)
- [ ] Multi-tenant authentication working (authority=common)
- [ ] Bearer token validation enforced on all protected routes
- [ ] Tier enforcement via APIM subscription key metadata
- [ ] Rate limiting enforced per tier (Tier 1: 10/min, Tier 2: 30/min, Tier 3: 100/min)
- [ ] CORS configured for frontend origin
- [ ] API responds within <500ms for 95th percentile
- [ ] Integration tests green for all endpoints

**Verification**: Run Postman/curl tests against API, verify responses

**Status**: ✅ **PASSED** (2026-01-20)

---

### Gate P1-06: Frontend Functional

**Epic**: 5 (Frontend)  
**Stories**: ACA-05-001 through ACA-05-042

**Acceptance Criteria**:
- [ ] All 10 pages accessible and rendered correctly
- [ ] Authentication flow complete (login, logout, token refresh)
- [ ] Findings page displays all 12 rule results
- [ ] Detail modal shows full finding context
- [ ] Admin pages accessible only to admin role
- [ ] Tier upgrade prompt shown to Tier 1/2 users on restricted features
- [ ] Lighthouse score ≥90 for Performance, Accessibility, Best Practices, SEO
- [ ] E2E tests green for critical user flows

**Verification**: Run Playwright E2E tests, verify all flows pass

**Status**: ✅ **PASSED** (2026-02-20)

---

### Gate P1-07: Billing Integration

**Epic**: 6 (Billing)  
**Stories**: ACA-06-001 through ACA-06-018

**Acceptance Criteria**:
- [ ] Stripe checkout creates customer and subscription
- [ ] Payment success webhook triggers tier upgrade
- [ ] Entitlements written to Cosmos entitlements container
- [ ] Tier downgrade on subscription cancellation
- [ ] Payment audit trail logged to payments container
- [ ] Invoice emailed to customer on successful payment
- [ ] Stripe test webhooks verified with stripe-cli

**Verification**: Run Stripe test checkout, verify webhook processing

**Status**: ✅ **PASSED** (2026-02-28)

---

### Gate P1-08: Deliverable Generation

**Epic**: 7 (Delivery)  
**Stories**: ACA-07-001 through ACA-07-009

**Acceptance Criteria**:
- [ ] Tier 3 ZIP artifact generated with IaC templates
- [ ] ZIP contains 12 Bicep templates (one per rule)
- [ ] CSV index file accurate (artifact count matches findings count)
- [ ] SHA-256 hash verified
- [ ] SAS URL generated with 7-day expiry
- [ ] Deliverable metadata written to Cosmos deliverables container
- [ ] ZIP downloadable via SAS URL

**Verification**: Trigger Tier 3 delivery, download ZIP, verify contents

**Status**: ✅ **PASSED** (2026-02-15)

---

### Gate P1-09: Observability

**Epic**: 8 (Observability)  
**Stories**: ACA-08-001 through ACA-08-014

**Acceptance Criteria**:
- [ ] GA4 tracking operational (pageviews, events, conversions)
- [ ] Clarity recordings available with PII masking
- [ ] App Insights logs all API requests with correlation IDs
- [ ] Custom metrics tracked: scan duration, findings count, tier upgrade rate
- [ ] Alerting configured for critical failures (>5 errors in 5 minutes)
- [ ] Dashboard accessible in Azure Portal with key metrics

**Verification**: Trigger user flow, verify telemetry in GA4/Clarity/App Insights

**Status**: ✅ **PASSED** (2026-03-05)

---

### Gate P1-10: Internationalization

**Epic**: 9 (i18n/a11y)  
**Stories**: ACA-09-001 through ACA-09-012

**Acceptance Criteria**:
- [ ] All 5 locales (EN, FR, PT-BR, ES, DE) translated
- [ ] Locale switching functional via dropdown
- [ ] Date/currency formatting correct per locale
- [ ] RTL support tested (not required for launch but architecture ready)
- [ ] No hardcoded strings in UI code
- [ ] Translation keys match en.json structure

**Verification**: Switch locales, verify all strings translated

**Status**: ✅ **PASSED** (2026-03-08)

---

### Gate P1-11: Accessibility

**Epic**: 9 (i18n/a11y)  
**Stories**: ACA-09-013 through ACA-09-021

**Acceptance Criteria**:
- [ ] WCAG 2.1 AA compliant (axe-core audit passes)
- [ ] Keyboard navigation functional (all interactive elements reachable via Tab)
- [ ] Screen reader tested with NVDA/JAWS (critical flows)
- [ ] Color contrast ratio ≥4.5:1 for text, ≥3:1 for large text
- [ ] Focus indicators visible on all interactive elements
- [ ] ARIA labels present on all icons and complex widgets
- [ ] Form validation announces errors to screen readers

**Verification**: Run axe-core CI gate, manual screen reader test

**Status**: ✅ **PASSED** (2026-03-10)

---

### Gate P1-12: Veritas MTI Score

**Epic**: 12 (Data Model)  
**Stories**: ACA-12-023 through ACA-12-028

**Acceptance Criteria**:
- [ ] All 281 stories seeded to Data Model WBS layer
- [ ] Evidence records linked to completed stories
- [ ] Veritas audit score ≥60 (acceptable for post-regeneration baseline)
- [ ] H2→Feature, H3→Story format validated by parser
- [ ] No orphan evidence, duplicate IDs, or missing parent links
- [ ] WBS hierarchy consistent: epic → feature → user_story

**Verification**: Run `eva audit_repo` and verify MTI score

**Status**: ⏳ **PENDING** (awaiting audit post-regeneration)

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
