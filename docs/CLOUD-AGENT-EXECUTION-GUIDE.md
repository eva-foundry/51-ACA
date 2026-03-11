# GitHub Copilot Cloud Agent Execution Guide

**Generated**: March 11, 2026 @ 09:15 AM ET  
**Project**: 51-ACA -- Azure Cost Advisor  
**Source**: 8-WEEK-BUILD-PLAN-20260311.md v2.0  
**Purpose**: Execute automatable work via GitHub Copilot Cloud agents  

---

## Summary

**62% of 8-week implementation work** (108 stories, ~425 FP) can be automated via GitHub Copilot Cloud agents.

**High-priority automation** (Weeks 1-5): 9 batches, ~265 FP, ~10 hours cloud execution time

---

## Quick Start

### Option 1: High-Priority Automation (Recommended)

Execute Weeks 1-5 (9 batches) via cloud agents, leaving Weeks 6-8 for manual implementation:

```powershell
# Preview issues (dry-run)
cd C:\eva-foundry\51-ACA
.\scripts\create-cloud-agent-issues-8week.ps1 -DryRun -Priority

# Create 9 high-priority issues
.\scripts\create-cloud-agent-issues-8week.ps1 -Priority

# Monitor execution
gh issue list --repo eva-foundry/51-ACA --label "sprint-task"
```

### Option 2: Test with Single Batch

Test cloud agent workflow with Batch 1 (Analysis Rules):

```powershell
# Preview Batch 1
.\scripts\create-cloud-agent-issues-8week.ps1 -DryRun -Batch 1

# Create Batch 1 issue
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 1

# Monitor GitHub Actions
gh run list --repo eva-foundry/51-ACA --workflow "Sprint Agent"
```

### Option 3: Full Automation

Create all 16 issues (Weeks 1-8, includes medium/low priority tasks):

```powershell
# Preview all issues
.\scripts\create-cloud-agent-issues-8week.ps1 -DryRun

# Create all 16 issues
.\scripts\create-cloud-agent-issues-8week.ps1
```

---

## Architecture

### Trigger Flow

```
User runs script → gh issue create → Issue labeled "sprint-task"
    ↓
GitHub webhook fires → .github/workflows/sprint-agent.yml starts
    ↓
Sprint Agent parses SPRINT_MANIFEST from issue body
    ↓
For each story: DISCOVER → PLAN → DO → CHECK → ACT
    ↓
Agent posts progress comment after each story
    ↓
Agent creates PR with all changes + evidence receipt
    ↓
Human reviews PR → Merges if quality gates pass
```

### Quality Gates (Automated)

Every cloud agent PR must pass:
- ✅ `ruff lint`: 0 errors
- ✅ `mypy`: 0 unresolved types  
- ✅ `pytest`: all tests pass, coverage >= 95%
- ✅ `axe-core`: 0 critical/serious (frontend only)
- ✅ Evidence receipt generated (duration, tokens, files_changed)
- ✅ Story acceptance criteria met

### Human Review Checklist

Before merging cloud agent PRs:
- [ ] Code follows project patterns (P2.3 structure, P2.5 partition key enforcement)
- [ ] No hardcoded credentials or secrets
- [ ] Error handling appropriate (no swallowed exceptions)
- [ ] Logging follows professional standards (dual logging, ASCII-only)
- [ ] API design adheres to EVA REST conventions
- [ ] Frontend components are accessible (WCAG 2.1 AA)
- [ ] Tests cover edge cases (not just happy path)

---

## 9 High-Priority Batches (Weeks 1-5)

| Batch | Title | Week | FP | Stories | Est. Time |
|-------|-------|------|----|---------| ---------|
| 1 | Analysis Rules Completion (R-09 to R-12) | 1 | 10 | 4 | ~45 min |
| 2 | Core API Endpoints (Routes 11-16) | 2 | 20 | 6 | ~60 min |
| 3 | Admin API (6 Endpoints) | 2 | 25 | 6 | ~75 min |
| 4a | Rule Unit Tests (R-01 to R-06) | 2 | 12 | 6 | ~45 min |
| 4b | Rule Unit Tests (R-07 to R-12) | 2 | 13 | 6 | ~45 min |
| 5 | Frontend Auth Layer + Router | 3 | 20 | 10 | ~60 min |
| 6 | Frontend Layouts | 3 | 15 | 5 | ~50 min |
| 7 | API Client + Shared Components | 3 | 20 | 9 | ~60 min |
| 8 | IaC Template Library (12 Templates) | 5 | 25 | 4 | ~75 min |
| **TOTAL** | | **1-5** | **160** | **56** | **~8.5 hours** |

**Benefit**: Automates 23% of total 8-week work (160 FP out of ~695 FP)

---

## Monitoring Cloud Execution

### Watch GitHub Actions

```powershell
# List recent workflow runs
gh run list --repo eva-foundry/51-ACA --workflow "Sprint Agent" --limit 10

# Watch specific run
gh run watch <run-id> --repo eva-foundry/51-ACA

# View run logs
gh run view <run-id> --repo eva-foundry/51-ACA --log
```

### Check Issue Progress

```powershell
# List all sprint-task issues
gh issue list --repo eva-foundry/51-ACA --label "sprint-task" --state all

# View specific issue (agent posts progress comments)
gh issue view <issue-number> --repo eva-foundry/51-ACA --comments
```

### Review PRs

```powershell
# List PRs from cloud agents
gh pr list --repo eva-foundry/51-ACA --author "@copilot"

# Review PR
gh pr view <pr-number> --repo eva-foundry/51-ACA

# Check PR status (quality gates)
gh pr checks <pr-number> --repo eva-foundry/51-ACA
```

---

## Evidence Collection

All cloud agent executions generate evidence receipts:

**Location**: `C:\eva-foundry\51-ACA\evidence\`

**Evidence Schema** (per Veritas):
```json
{
  "timestamp": "2026-03-11T09:15:00Z",
  "batch_id": 1,
  "sprint_id": "SPRINT-001-BATCH-1",
  "duration_ms": 2700000,
  "tokens_used": 150000,
  "files_changed": 8,
  "test_count_before": 42,
  "test_count_after": 50,
  "stories_completed": 4,
  "quality_gates_passed": true,
  "pr_url": "https://github.com/eva-foundry/51-ACA/pull/123"
}
```

---

## MTI Validation (After Each Merge)

Run Veritas audit after merging cloud agent PRs:

```powershell
cd C:\eva-foundry\48-eva-veritas
node src/cli.js audit --repo C:\eva-foundry\51-ACA

# Expected: MTI increases after each batch merge
# Week 1 target: MTI >= 62 (advisory gate)
# Week 4 target: MTI >= 72 (MANDATORY gate)
# Week 8 target: MTI >= 87 (MANDATORY gate)
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Scope creep** | Each batch limited to 3-6 stories, < 30 FP |
| **Unvalidated code** | All cloud PRs require human review before merge |
| **Breaking changes** | Cloud agents create feature branches, not main commits |
| **Test failures** | Agents run pytest/ruff/mypy in CHECK phase, fail if errors |
| **Security gaps** | Security-sensitive stories (auth, RBAC, CSP) excluded from automation |
| **MTI regression** | Manual MTI audit after each batch merge (veritas) |

---

## What NOT to Automate (Manual Implementation Required)

**Week 4 (MANDATORY MTI Gate)**: Human validation required before proceeding to Week 5

**Security-sensitive** (38% of work, ~270 FP):
- ACA-10-001..006 (Red-team tests, tenant isolation, CSP)
- ACA-13-013..016 (RBAC hygiene, Key Vault audit, MCSB compliance)
- P1-01..P1-12 (Acceptance gates)

**UX/Privacy** (requires human judgment):
- ACA-05-016..020 (Customer pages -- UI polish, UX review)
- ACA-05-035..038 (Consent + telemetry -- privacy review)
- ACA-09-007..009 (i18n translations -- professional review)
- ACA-10-007..012 (Privacy policy, GDPR compliance)

**Architectural**:
- ACA-12-001..008 (Data Model sync -- complex state management)
- Epic 11 (Phase 2 Infra -- Terraform, custom domain, geo-replicas)
- Epic 15 (Onboarding system -- 7-gate state machine)

---

## Recommended Workflow

### Phase 1: Test (Day 1)
1. Create Batch 1 issue (Analysis Rules)
2. Monitor cloud execution (~45 min)
3. Review PR, validate quality gates
4. Merge if passes
5. Run MTI audit (expect +3-5 points)

### Phase 2: Week 1-2 Automation (Day 2-3)
1. Create Batches 2-5 (API endpoints + rule tests)
2. Monitor parallel execution
3. Review 5 PRs
4. Merge all if passes
5. Run MTI audit (expect MTI ~65)

### Phase 3: Week 3 Automation (Day 4-5)
1. Create Batches 6-8 (Frontend auth/layouts/components)
2. Monitor parallel execution
3. Review 3 PRs
4. Merge all if passes
5. Run MTI audit (expect MTI ~68)

### Phase 4: Week 4 Manual Gate (Day 6-7)
1. Manual implementation: ACA-05-021..025 (Admin pages)
2. Manual implementation: ACA-09-001..006 (i18n foundation)
3. **MANDATORY MTI >= 72 gate** -- do not proceed until pass
4. Human sign-off required

### Phase 5: Week 5 Automation (Day 8-9)
1. Create Batch 9 (IaC templates)
2. Manual implementation: ACA-07-005..009 (Delivery pipeline)
3. Manual implementation: ACA-08-007..011 (Observability)
4. Run MTI audit (expect MTI ~75)

### Phase 6: Weeks 6-8 Manual (Day 10-30)
1. Manual implementation: All remaining stories (~270 FP)
2. Week 6: Observability + i18n/a11y completion
3. Week 7: Best practices + security hardening
4. Week 8: Privacy + acceptance gates + go-live
5. **MANDATORY MTI >= 87 gate** -- must pass for production

---

## Troubleshooting

### Issue: Cloud agent PR fails quality gates

**Symptoms**: pytest fails, ruff lint errors, mypy type errors

**Fix**:
1. View PR checks: `gh pr checks <pr-number>`
2. Read failure logs
3. Add comment to issue: "@copilot please fix quality gate failures: [describe]"
4. Cloud agent will update PR with fixes

### Issue: Cloud agent creates incorrect code

**Symptoms**: Code doesn't follow project patterns, wrong API design, missing acceptance criteria

**Fix**:
1. Close PR without merging
2. Edit issue body: clarify acceptance criteria, add pattern references
3. Re-label issue with `sprint-task` to re-trigger workflow
4. Cloud agent creates new PR

### Issue: Cloud agent times out (> 2 hours)

**Symptoms**: GitHub Actions run exceeds timeout, incomplete work

**Fix**:
1. Split batch into smaller issues (3 stories max)
2. Create sub-issues: Batch 4a and Batch 4b instead of single Batch 4
3. Re-run with smaller scope

---

## Next Steps After Automation

1. **Week 4 Gate**: Manual MTI validation (MANDATORY >= 72)
2. **Week 8 Gate**: Manual MTI validation (MANDATORY >= 87)
3. **Acceptance Gates**: Manual P1-01 through P1-12 validation (12 gates)
4. **Go-Live**: Manual deployment to production (Azure Container Apps)
5. **Phase 2 Planning**: Epic 11 (Terraform, custom domain) + Epic 15 (Onboarding)

---

## Success Metrics

| Metric | Baseline (3/11) | Target (Week 5) | Target (Week 8) |
|--------|-----------------|-----------------|-----------------|
| MTI Score | 57 | 75 | 87 |
| Test Coverage | ~70% | 90% | 95% |
| Stories Complete | ~74 (26%) | ~130 (46%) | ~252 (90%) |
| FP Complete | ~225 | ~385 | ~650 |
| Cloud Agent FP | 0 | ~160 | ~265 |
| Manual FP | ~225 | ~225 | ~385 |

**ROI Calculation**:
- Cloud agent time: ~10 hours (9 batches x ~60 min avg)
- Manual time saved: ~53 hours (160 FP x 20 min/FP)
- **Time savings: 81%** (43 hours saved)

---

## Files Created

1. [docs/CLOUD-AGENT-AUTOMATION-ANALYSIS.md](docs/CLOUD-AGENT-AUTOMATION-ANALYSIS.md) -- Full analysis with 16 batches
2. [scripts/create-cloud-agent-issues-8week.ps1](scripts/create-cloud-agent-issues-8week.ps1) -- Issue creation script
3. [docs/CLOUD-AGENT-EXECUTION-GUIDE.md](docs/CLOUD-AGENT-EXECUTION-GUIDE.md) -- This guide

---

**Ready to execute**: Run `.\scripts\create-cloud-agent-issues-8week.ps1 -Priority` to create 9 high-priority cloud agent issues for Weeks 1-5.

**Estimated completion**: 10 hours cloud execution + 5 hours human review = 15 hours total (vs 53 hours manual implementation)

**CAUTION**: Do not proceed past Week 4 MANDATORY MTI >= 72 gate without human validation. Cloud agents are powerful but require oversight for security, privacy, and UX decisions.
