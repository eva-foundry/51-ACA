# Cloud Agent Automation Analysis -- 8-Week Build Plan

**Generated**: March 11, 2026 @ 09:00 AM ET  
**Source**: 8-WEEK-BUILD-PLAN-20260311.md v2.0  
**Purpose**: Identify tasks suitable for GitHub Copilot Cloud agent automation  

---

## Cloud Agent Capabilities (From GitHub Docs)

GitHub Copilot Cloud agents can:
- ✅ Read/write files autonomously
- ✅ Execute tests and verify results
- ✅ Follow detailed acceptance criteria
- ✅ Create pull requests with evidence
- ✅ Implement well-defined patterns
- ✅ Generate code following templates

**NOT suitable for cloud agents**:
- ❌ Architectural decisions
- ❌ Ambiguous requirements
- ❌ Tasks requiring human judgment
- ❌ Security-sensitive credential management
- ❌ Cross-repository coordination

**51-ACA Existing Infrastructure**:
- `.github/workflows/sprint-agent.yml` -- Trigger on `sprint-task` label
- `.github/SPRINT_ISSUE_TEMPLATE.md` -- Machine-readable manifest format
- Proven pattern: Sprints 13-19 executed via cloud agents successfully

---

## Automation Suitability Analysis

### Week 1 / Sprint-004: Analysis Rules + Auth (14 stories, ~80 FP)

| Story | Automatable? | Rationale | Priority |
|-------|--------------|-----------|----------|
| **ACA-03-019** (R-09 DNS Sprawl) | ✅ YES | Clear pattern from R-01 through R-08, acceptance criteria complete | HIGH |
| **ACA-03-020** (R-10 Savings Plan) | ✅ YES | Rule pattern established, savings plan logic documented | HIGH |
| **ACA-03-021** (R-11 APIM Token Budget) | ✅ YES | APIM + OpenAI co-existence detection, risk-only (no saving) | HIGH |
| **ACA-03-022** (R-12 Chargeback Gap) | ✅ YES | Tagging analysis pattern, effort_class=strategic | HIGH |
| **ACA-04-001** (Multi-Tenant Sign-In) | ⚠️ PARTIAL | Auth configuration, needs manual MSAL verification | MEDIUM |
| **ACA-04-003** (SubscriptionId from Session) | ✅ YES | Session management pattern exists, Cosmos mock available | HIGH |
| **ACA-04-004** (Connect Modes A/B/C) | ⚠️ PARTIAL | Requires understanding of 3 auth modes (delegated/SP/Lighthouse) | MEDIUM |
| **ACA-04-005** (Disconnect) | ✅ YES | Hard-delete pattern defined, acceptance criteria clear | HIGH |
| **ACA-04-007** (Frontend LoginPage MSAL) | ⚠️ PARTIAL | Frontend MSAL.js integration, needs UI testing | LOW |
| **ACA-04-009** (Preflight API) | ✅ YES | 5 probes defined, structured PASS/WARN/FAIL response | HIGH |
| **ACA-04-010** (Disconnect API) | ✅ YES | Router registration, extends ACA-04-005 | HIGH |

**Week 1 Automation**: 7/11 stories (64%), ~50 FP  
**Recommended Batch**: 4 analysis rules (ACA-03-019..022) = 1 sprint issue

---

### Week 2 / Sprint-005: API Completion + Rule Tests (30 stories, ~95 FP)

| Story | Automatable? | Rationale | Priority |
|-------|--------------|-----------|----------|
| **ACA-04-011..016** (Core API) | ✅ YES | Endpoint wiring follows existing router patterns | HIGH |
| **ACA-04-017..021** (APIM Policies) | ⚠️ PARTIAL | Policy XML patterns defined, but infra deployment needs manual validation | MEDIUM |
| **ACA-04-022..027** (Admin API) | ✅ YES | 6 endpoints with clear DTOs, RBAC patterns established | HIGH |
| **ACA-03-020..032** (Rule Unit Tests) | ✅ YES | Test pattern established (fixtures, positive/negative, 95% coverage) | HIGH |
| **ACA-12-001..004** (Data Model Sync) | ❌ NO | Requires Data Model API sync, complex state management | N/A |

**Week 2 Automation**: ~25/30 stories (83%), ~80 FP  
**Recommended Batches**:
1. Core API endpoints (ACA-04-011..016) = 1 sprint issue
2. Admin API (ACA-04-022..027) = 1 sprint issue
3. Rule unit tests (ACA-03-020..032 -- 14 tests) = 2-3 sprint issues

---

### Week 3 / Sprint-006: Frontend Customer Pages (34 stories, ~90 FP)

| Story | Automatable? | Rationale | Priority |
|-------|--------------|-----------|----------|
| **ACA-05-001..005** (Auth Layer) | ✅ YES | roles.ts, useAuth.ts, GuardComponents follow React patterns | HIGH |
| **ACA-05-006..010** (Layouts) | ✅ YES | Fluent UI v9 layouts, navigation components, AppShell pattern | HIGH |
| **ACA-05-011..015** (Router) | ✅ YES | React Router v6 with lazy loading, auth guards | HIGH |
| **ACA-05-016..020** (Customer Pages) | ⚠️ PARTIAL | Pages require UI polish, a11y validation (axe-core), UX review | MEDIUM |
| **ACA-05-026..029** (API Client) | ✅ YES | TypeScript DTOs, http client wrapper, appApi/adminApi | HIGH |
| **ACA-05-030..034** (Shared Components) | ✅ YES | Fluent UI primitives, MoneyRangeBar, EffortBadge patterns | HIGH |

**Week 3 Automation**: ~29/34 stories (85%), ~75 FP  
**Recommended Batches**:
1. Auth layer + Router (ACA-05-001..015) = 1 sprint issue
2. API client + Shared components (ACA-05-026..034) = 1 sprint issue
3. Layouts (ACA-05-006..010) = 1 sprint issue

---

### Week 4 / Sprint-007: Admin + i18n + Consent (26 stories, ~85 FP)

| Story | Automatable? | Rationale | Priority |
|-------|--------------|-----------|----------|
| **ACA-05-021..025** (Admin Pages) | ✅ YES | 5 admin pages follow AdminListPage pattern from P31 | HIGH |
| **ACA-05-035..038** (Consent + Telemetry) | ⚠️ PARTIAL | GTM/Clarity integration, consent logic clear but needs privacy review | MEDIUM |
| **ACA-05-039..042** (Accessibility) | ⚠️ PARTIAL | Skip-to-content, keyboard nav, labels -- needs manual axe-core validation | MEDIUM |
| **ACA-09-001..006** (i18n Foundation) | ✅ YES | react-i18next config, 5 locale namespaces, LanguageSelector | HIGH |

**Week 4 Automation**: ~16/26 stories (62%), ~50 FP  
**Recommended Batches**:
1. Admin pages (ACA-05-021..025) = 1 sprint issue
2. i18n foundation (ACA-09-001..006) = 1 sprint issue

**GATE**: Week 4 has MANDATORY MTI >= 72 gate -- cloud agents should NOT proceed past this without human verification

---

### Week 5 / Sprint-008: Delivery Packager + Observability (14 stories, ~95 FP)

| Story | Automatable? | Rationale | Priority |
|-------|--------------|-----------|----------|
| **ACA-07-001..004** (IaC Templates) | ✅ YES | 12 Jinja2 Bicep templates from 12-IaCscript.md patterns | HIGH |
| **ACA-07-005..007** (ZIP + Blob) | ✅ YES | ZIP assembly, SHA-256, Blob upload with SAS URL generation | HIGH |
| **ACA-07-008..009** (Deliverable Record) | ✅ YES | Cosmos write, SAS URL endpoint, 168h TTL | HIGH |
| **ACA-08-007..011** (Backend Observability) | ✅ YES | App Insights connection, structured logging, custom metrics | HIGH |

**Week 5 Automation**: 14/14 stories (100%), ~95 FP  
**Recommended Batches**:
1. IaC templates (ACA-07-001..004) = 1 sprint issue
2. Delivery pipeline (ACA-07-005..009) = 1 sprint issue
3. Observability (ACA-08-007..011) = 1 sprint issue

---

### Week 6 / Sprint-009: Observability + i18n/a11y Completion (21 stories, ~90 FP)

| Story | Automatable? | Rationale | Priority |
|-------|--------------|-----------|----------|
| **ACA-08-001..006** (Frontend Telemetry) | ⚠️ PARTIAL | GTM/GA4/Clarity tags, consent gating -- needs privacy validation | MEDIUM |
| **ACA-08-012..014** (Alerting) | ✅ YES | Azure Monitor alerts: 5xx rate, collector failure, anomaly | HIGH |
| **ACA-09-007..009** (i18n Translations) | ⚠️ PARTIAL | Machine translation for 4 locales (fr, pt-BR, es, de) -- needs review | LOW |
| **ACA-09-010..018** (a11y) | ⚠️ PARTIAL | axe-core CI, aria-labels, keyboard tests -- needs manual validation | MEDIUM |

**Week 6 Automation**: ~8/21 stories (38%), ~35 FP  
**Recommended Batch**: Alerting (ACA-08-012..014) = 1 sprint issue

---

### Week 7 / Sprint-010: Best Practices + Security (17 stories, ~90 FP)

| Story | Automatable? | Rationale | Priority |
|-------|--------------|-----------|----------|
| **ACA-13-009..012** (WAF + FinOps) | ⚠️ PARTIAL | WAF assessment logic complex, FinOps rules follow existing pattern | MEDIUM |
| **ACA-13-013..016** (Security Rules) | ⚠️ PARTIAL | RBAC hygiene, Key Vault audit, MCSB compliance -- needs security review | MEDIUM |
| **ACA-13-017..019** (IaC Quality) | ✅ YES | API design compliance, PSRule gate, tag enforcement | HIGH |
| **ACA-10-001..006** (Security Hardening) | ❌ NO | Red-team tests, tenant isolation, CSP -- requires security expertise | N/A |

**Week 7 Automation**: ~5/17 stories (29%), ~25 FP  
**Recommended Batch**: IaC quality (ACA-13-017..019) = 1 sprint issue

---

### Week 8 / Sprint-011: Privacy + Acceptance + Go-Live (20 stories, ~80 FP)

| Story | Automatable? | Rationale | Priority |
|-------|--------------|-----------|----------|
| **ACA-10-007..012** (Privacy) | ⚠️ PARTIAL | Policy pages (boilerplate), data retention logic clear, GDPR needs legal review | MEDIUM |
| **ACA-10-013..015** (Support Docs) | ✅ YES | Documentation generation, FAQ from failure analysis, status page | HIGH |
| **ACA-12-001..008** (Data Model Final Sync) | ❌ NO | Final state sync, requires human oversight | N/A |
| **P1-01..P1-12** (Acceptance Gates) | ❌ NO | Manual validation gates, evidence collection, human sign-off required | N/A |

**Week 8 Automation**: ~4/20 stories (20%), ~15 FP  
**Recommended Batch**: Support docs (ACA-10-013..015) = 1 sprint issue

---

## Automation Summary

| Week | Total Stories | Automatable | FP Automatable | Cloud Issues | Manual FP |
|------|---------------|-------------|----------------|--------------|-----------|
| 1 | 11 | 7 (64%) | ~50 | 1 | ~30 |
| 2 | 30 | 25 (83%) | ~80 | 4 | ~15 |
| 3 | 34 | 29 (85%) | ~75 | 3 | ~15 |
| 4 | 26 | 16 (62%) | ~50 | 2 | ~35 |
| 5 | 14 | 14 (100%) | ~95 | 3 | 0 |
| 6 | 21 | 8 (38%) | ~35 | 1 | ~55 |
| 7 | 17 | 5 (29%) | ~25 | 1 | ~65 |
| 8 | 20 | 4 (20%) | ~15 | 1 | ~65 |
| **TOTAL** | **173** | **108 (62%)** | **~425 FP** | **16 issues** | **~270 FP** |

**Key Insight**: 62% of implementation work (108 stories, ~425 FP) can be automated via cloud agents. Remaining 38% requires human oversight (security, privacy, UX, acceptance gates).

---

## High-Priority Cloud Agent Batches (Weeks 1-5)

### Batch 1: Analysis Rules Completion (Week 1)
**Stories**: ACA-03-019, ACA-03-020, ACA-03-021, ACA-03-022  
**FP**: 10  
**Files**: 4 rule modules + tests  
**Pattern**: Existing R-01 through R-08 implementations  
**Estimated Cloud Execution**: ~45 min

### Batch 2: Core API Endpoints (Week 2)
**Stories**: ACA-04-011..016  
**FP**: 20  
**Files**: 6 endpoint implementations in routers/  
**Pattern**: Existing collector, billing routers  
**Estimated Cloud Execution**: ~60 min

### Batch 3: Admin API (Week 2)
**Stories**: ACA-04-022..027  
**FP**: 25  
**Files**: 6 admin endpoints + DTOs  
**Pattern**: Admin audit events logging  
**Estimated Cloud Execution**: ~75 min

### Batch 4: Rule Unit Tests (Week 2)
**Stories**: ACA-03-020..032 (14 test files)  
**FP**: 25  
**Files**: 14 test_rNN_*.py files  
**Pattern**: Existing rule test structure  
**Estimated Cloud Execution**: ~90 min (split into 2 issues)

### Batch 5: Frontend Auth + Router (Week 3)
**Stories**: ACA-05-001..015  
**FP**: 20  
**Files**: Auth layer, layouts, router config  
**Pattern**: React 19 + MSAL.js + React Router v6  
**Estimated Cloud Execution**: ~60 min

### Batch 6: API Client + Shared Components (Week 3)
**Stories**: ACA-05-026..034  
**FP**: 20  
**Files**: TypeScript DTOs, http client, Fluent UI components  
**Pattern**: Existing appApi structure  
**Estimated Cloud Execution**: ~60 min

### Batch 7: IaC Templates (Week 5)
**Stories**: ACA-07-001..004  
**FP**: 25  
**Files**: 12 Jinja2 template folders with Bicep  
**Pattern**: 12-IaCscript.md patterns  
**Estimated Cloud Execution**: ~75 min

### Batch 8: Delivery Pipeline (Week 5)
**Stories**: ACA-07-005..009  
**FP**: 30  
**Files**: ZIP assembly, Blob upload, SAS URL endpoint  
**Pattern**: Existing delivery service structure  
**Estimated Cloud Execution**: ~90 min

### Batch 9: Backend Observability (Week 5)
**Stories**: ACA-08-007..011  
**FP**: 20  
**Files**: App Insights integration, structured logging, metrics  
**Pattern**: Existing telemetry patterns from P50  
**Estimated Cloud Execution**: ~60 min

**Total High-Priority**: 9 batches, ~265 FP, Weeks 1-5, Est. 10 hours cloud execution time

---

## Cloud Agent Issue Creation Script

See: `scripts/create-cloud-agent-issues-8week.ps1`

**Usage**:
```powershell
# Dry-run (preview issues)
.\scripts\create-cloud-agent-issues-8week.ps1 -DryRun

# Create Batch 1 only (test)
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 1

# Create all 16 issues
.\scripts\create-cloud-agent-issues-8week.ps1

# Create high-priority batches (1-9, Weeks 1-5)
.\scripts\create-cloud-agent-issues-8week.ps1 -Priority
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Cloud agent scope creep | Each issue limited to 3-6 stories, < 30 FP |
| Unvalidated code merged | All cloud PRs require human review before merge |
| Breaking changes | Cloud agents create feature branches, not main commits |
| Test failures | Cloud agents run pytest/ruff/mypy in CHECK phase, fail if errors |
| Security gaps | Security-sensitive stories (auth, RBAC, CSP) excluded from automation |
| MTI regression | Manual MTI audit after each cloud sprint (veritas) |

---

## Quality Gates for Cloud Agent PRs

**Required Checks** (before human review):
- [ ] ruff lint: 0 errors
- [ ] mypy: 0 unresolved types
- [ ] pytest: all tests pass, coverage >= 95% for new code
- [ ] axe-core: 0 critical/serious (frontend only)
- [ ] Evidence receipt generated (duration, tokens, files_changed)
- [ ] Story acceptance criteria met (automated check in sprint-agent.yml)
- [ ] ADO work item status synced (if applicable)
- [ ] Data model story status updated (if applicable)

**Human Review Checklist**:
- [ ] Code follows project patterns (P2.3 structure, P2.5 partition key enforcement)
- [ ] No hardcoded credentials or secrets
- [ ] Error handling appropriate (no swallowed exceptions)
- [ ] Logging follows professional standards (dual logging, ASCII-only)
- [ ] API design adheres to EVA REST conventions
- [ ] Frontend components are accessible (WCAG 2.1 AA)
- [ ] Tests cover edge cases (not just happy path)

---

## Next Steps

1. **User Decision**: Review batches 1-9 (high-priority automation), approve for cloud execution
2. **Create Issues**: Run `.\scripts\create-cloud-agent-issues-8week.ps1 -Priority` to create 9 GitHub issues
3. **Monitor Execution**: Watch GitHub Actions output, collect evidence receipts
4. **Review PRs**: Human review of all cloud-generated PRs before merge
5. **MTI Validation**: Run `eva audit` after each batch merge
6. **Iterate**: Adjust subsequent batches based on Week 1-2 cloud agent performance

---

*Analysis complete. 62% of 8-week plan (108 stories, ~425 FP) suitable for cloud agent automation. Remaining 38% requires human expertise (security, privacy, UX, acceptance validation).*
