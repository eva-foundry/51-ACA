# Cloud Agent Quick Start

**Date**: March 11, 2026  
**Project**: 51-ACA (Azure Cost Advisor)  
**Automation Potential**: 62% of 8-week work (108 stories, ~425 FP)  

---

## 🚀 Quick Commands

### Test with Batch 1 (Recommended First Step)
```powershell
cd C:\eva-foundry\51-ACA

# Preview
.\scripts\create-cloud-agent-issues-8week.ps1 -DryRun -Batch 1

# Create issue (triggers cloud agent automatically)
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 1

# Watch execution
gh run watch --repo eva-foundry/51-ACA
```

### High-Priority Automation (Weeks 1-5, 9 batches, ~265 FP)
```powershell
# Preview
.\scripts\create-cloud-agent-issues-8week.ps1 -DryRun -Priority

# Create all 9 high-priority issues
.\scripts\create-cloud-agent-issues-8week.ps1 -Priority

# Monitor
gh issue list --repo eva-foundry/51-ACA --label "sprint-task"
```

### Full Automation (All 16 batches)
```powershell
# Preview
.\scripts\create-cloud-agent-issues-8week.ps1 -DryRun

# Create all issues
.\scripts\create-cloud-agent-issues-8week.ps1

# Monitor
gh run list --repo eva-foundry/51-ACA --workflow "Sprint Agent"
```

---

## 📊 What Gets Automated

| Week | Batches | Stories | FP | Time Saved |
|------|---------|---------|-----|-----------|
| 1 | 1 (Analysis rules) | 4 | 10 | 3 hours |
| 2 | 2-5 (API + tests) | 24 | 70 | 23 hours |
| 3 | 6-8 (Frontend) | 24 | 55 | 18 hours |
| 5 | 9 (IaC templates) | 4 | 25 | 8 hours |
| **TOTAL** | **9** | **56** | **160** | **52 hours** |

**Cloud Execution**: ~10 hours  
**Human Review**: ~5 hours  
**Total Time**: 15 hours (vs 52 hours manual)  
**Savings**: **71% faster**

---

## 🎯 Recommended Workflow

### Day 1: Test Pattern
```powershell
# Create Batch 1 (Analysis Rules R-09 to R-12)
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 1

# Wait ~45 min for cloud execution
# Review PR, merge if quality gates pass
```

### Day 2-3: Week 1-2 Automation
```powershell
# Create Batches 2-5 (API endpoints + rule tests)
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 2
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 3
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 4
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 5

# Wait ~4 hours for parallel execution
# Review 4 PRs, merge if pass
# Run MTI audit (expect MTI ~65)
```

### Day 4-5: Week 3 Automation
```powershell
# Create Batches 6-8 (Frontend)
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 6
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 7
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 8

# Wait ~3 hours for parallel execution
# Review 3 PRs, merge if pass
# Run MTI audit (expect MTI ~68)
```

### Day 6-7: Week 4 MANUAL (MANDATORY GATE)
```
⚠️ MANUAL IMPLEMENTATION REQUIRED
- Admin pages (ACA-05-021..025)
- i18n foundation (ACA-09-001..006)
- Consent + a11y (partial)

🚫 DO NOT PROCEED PAST WEEK 4 WITHOUT MTI >= 72
```

### Day 8-9: Week 5 Automation
```powershell
# Create Batch 9 (IaC templates)
.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 9

# Wait ~75 min
# Manual: Delivery pipeline + Observability
# Run MTI audit (expect MTI ~75)
```

---

## 🔍 Monitor Progress

### Check Issue Status
```powershell
gh issue list --repo eva-foundry/51-ACA --label "sprint-task" --state all
```

### Watch Workflow
```powershell
gh run watch --repo eva-foundry/51-ACA
```

### Review PR
```powershell
gh pr list --repo eva-foundry/51-ACA --author "@copilot"
gh pr view <pr-number>
gh pr checks <pr-number>  # Quality gates
```

### MTI Validation (After Each Merge)
```powershell
cd C:\eva-foundry\48-eva-veritas
node src/cli.js audit --repo C:\eva-foundry\51-ACA
```

---

## ✅ Quality Gates (Automated in Every PR)

- ✅ `ruff lint`: 0 errors
- ✅ `mypy`: 0 unresolved types
- ✅ `pytest`: all pass, coverage >= 95%
- ✅ `axe-core`: 0 critical/serious (frontend)
- ✅ Evidence receipt generated
- ✅ Story acceptance criteria met

---

## 🛡️ Safety Guardrails

**What's Safe to Automate** (✅):
- Well-defined CRUD endpoints
- Tests following existing patterns
- Frontend components with Fluent UI
- IaC templates from documented patterns
- API client wiring

**What Requires Human Oversight** (⚠️):
- Security controls (RBAC, CSP, tenant isolation)
- Privacy compliance (GDPR, data retention)
- UX polish (design, accessibility validation)
- Acceptance gates (P1-01 through P1-12)
- Architectural decisions

**MANDATORY Human Gates**:
- **Week 4**: MTI >= 72 (must pass before Week 5)
- **Week 8**: MTI >= 87 (must pass for go-live)

---

## 📚 Full Documentation

1. [CLOUD-AGENT-AUTOMATION-ANALYSIS.md](CLOUD-AGENT-AUTOMATION-ANALYSIS.md) -- Detailed 62% automation analysis
2. [CLOUD-AGENT-EXECUTION-GUIDE.md](CLOUD-AGENT-EXECUTION-GUIDE.md) -- Complete execution guide
3. [8-WEEK-BUILD-PLAN-20260311.md](8-WEEK-BUILD-PLAN-20260311.md) -- Source plan with nested DPDCA
4. [../scripts/create-cloud-agent-issues-8week.ps1](../scripts/create-cloud-agent-issues-8week.ps1) -- Issue creation script

---

## 🆘 Troubleshooting

### Issue: PR fails quality gates
```powershell
# View failure details
gh pr checks <pr-number>

# Comment on issue to request fixes
gh issue comment <issue-number> --body "@copilot please fix: [describe issue]"
```

### Issue: Cloud agent creates wrong code
```
1. Close PR without merging
2. Edit issue: clarify acceptance criteria
3. Re-label with "sprint-task" to re-trigger
```

### Issue: Workflow times out
```
Split batch into smaller issues (3 stories max)
Create sub-issues: Batch 4a, Batch 4b
```

---

## 🎉 Expected Outcomes

### After Batch 1 (Day 1)
- ✅ 4 analysis rules complete (R-09 to R-12)
- ✅ 8 files created (4 rules + 4 tests)
- ✅ MTI: 57 → ~60

### After Batches 1-5 (Day 3)
- ✅ 28 stories complete
- ✅ All 12 analysis rules tested (95%+ coverage)
- ✅ 25+ API endpoints live
- ✅ Admin API operational
- ✅ MTI: 57 → ~65

### After Batches 1-8 (Day 5)
- ✅ 52 stories complete
- ✅ Frontend auth/router/layouts complete
- ✅ API client + shared components
- ✅ MTI: 57 → ~68

### After Batch 9 (Day 9)
- ✅ 56 stories complete (20% of total)
- ✅ 12 IaC templates ready
- ✅ MTI: 57 → ~75

---

**Ready?** Run: `.\scripts\create-cloud-agent-issues-8week.ps1 -Batch 1`

**Questions?** See [CLOUD-AGENT-EXECUTION-GUIDE.md](CLOUD-AGENT-EXECUTION-GUIDE.md)

---

*Cloud agents are powerful tools, but they work best with human oversight. Use them to accelerate, not replace, human judgment on security, privacy, and UX decisions.*
