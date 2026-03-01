# North Star Dashboard -- Agent-Driven SaaS Delivery

**Date**: 2026-02-28 **Status**: Sprint 3 Complete, Sprint 4 Ready **MTI**: 70 (gate: 30) ✅ PASS

---

## Vision: Fully Automated Agile Scrum

```
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 GOAL: Deliver 51-ACA SaaS product via agent-driven sprints  │
│ 📊 PROGRESS: 73/256 stories (28.5%) → M1.0 target: 120 stories │
│ ⏱️  VELOCITY: Sprint 2 = 15 stories in 45 minutes = 480 st/day │
│ 🎖️  MTI: 70 → target: maintain >= 30 always, restore to 100   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Ecosystem Status

### Sprint Planning (Human + AI Scrum Master)
| Agent/Skill | Status | Function | Next Test |
|-------------|--------|----------|-----------|
| **progress-report** | ✅ VALIDATED | Epic completion, next stories | Re-run for Sprint 4 |
| **gap-report** | 🟡 DEFINED | Critical blockers, missing evidence | Manual trigger Day 2 |
| **sprint-report** | 🟡 DEFINED | Velocity, completion %, MTI trend | Manual trigger Day 2 |
| **sprint-advance** | 🟡 DEFINED | 5-phase sprint handoff | Manual trigger Day 6 |

### Sprint Execution (Cloud Agents)
| Component | Status | Function | Next Test |
|-----------|--------|----------|-----------|
| **sprint_agent.py** | ✅ READY | LLM code gen, pytest, evidence, ADO sync | GitHub Actions Day 4 |
| **GitHub Models API** | ✅ CONFIGURED | gpt-4o access via GITHUB_TOKEN | Validate LLM call Day 4 |
| **ADO Integration** | 🟡 READY | 4 integration points, needs ADO_PAT | Deploy secret Day 3 |
| **Data Model API** | ✅ OPERATIONAL | Story metadata, endpoint schemas | Validate updates Day 4 |

### Validation (Post-Sprint)
| Component | Status | Function | Next Test |
|-----------|--------|----------|-----------|
| **veritas-expert** | ✅ OPERATIONAL | MTI=70, gap detection, evidence audit | Daily monitoring |
| **Evidence Receipts** | 🟡 5/7 FIELDS | duration_ms ✅, tokens_used ⚠️ TODO | Complete TODOs Day 8 |
| **pytest Gate** | ✅ ENFORCED | Exit 0 required, 3 retry attempts | Validate Day 4 |
| **MTI Gate** | ✅ ENFORCED | >= 30 required by sprint-advance | Validate Day 6 |

---

## Test Execution Timeline (3 Weeks)

### Week 1: Component Validation
```
Day 1 ┬─ Test sprint_agent.py (single story local validation) ✅ DONE
      ├─ Test veritas audit (MTI=70, gaps=0) ✅ DONE
      └─ Validate evidence receipts (5/7 fields working) ✅ DONE

Day 2 ┬─ Deploy ADO_PAT secret to GitHub (enable ADO sync)
      ├─ Test gap-report skill (manual trigger)
      └─ Test sprint-report skill (manual trigger)

Day 3 ┬─ Test ADO sync (4 integration points)
      ├─ Validate work item state transitions
      └─ Test sprint-advance skill (manual trigger)
```

### Week 2: Integration Testing
```
Day 4 ┬─ 🎯 Test I1: Single story via GitHub Actions (ACA-03-001)
      ├─ Monitor execution (expected: 10-15 minutes)
      ├─ Validate outputs (code, tests, evidence, ADO, GitHub)
      └─ Check MTI (should remain >= 70)

Day 5 ┬─ Test I2: Full sprint (5 stories, ACA-03-001 → ACA-03-005)
      ├─ Monitor execution (expected: 30-60 minutes)
      ├─ Validate sprint summary metrics
      └─ Check velocity (target: 400+ stories/day)

Day 6 ┬─ Test I3: Sprint handoff (Sprint 4 → Sprint 5)
      ├─ Trigger sprint-advance skill
      ├─ Validate 5-phase workflow
      └─ Check end-to-end time (target: < 10 minutes)
```

### Week 3: Production Readiness
```
Day 7 ┬─ Telemetry audit (all 4 categories)
      ├─ Evidence receipts (validate all fields)
      ├─ ADO integration (validate all 4 points)
      ├─ Data model updates (validate PUT operations)
      └─ Sprint metrics (validate dashboard)

Day 8 ┬─ Complete TODOs (2 critical)
      ├─ Implement tokens_used tracking
      └─ Implement test_count tracking

Day 9 ┬─ Production gates
      ├─ Test rollback strategy (inject failure)
      └─ Test monitoring workflow (alerts)

Day 10 ┬─ Go/No-Go Decision
       ├─ Review all test results
       ├─ Validate MTI >= 30
       └─ Approve Sprint 4 production execution
```

---

## Current Sprint Status (Sprint 3 Complete)

### Epic Completion
```
ACA-01: Foundation          ████████████████████  21/21 (100%) ✅
ACA-02: Data Collection     ████████████████████  17/17 (100%) ✅
ACA-03: Analysis Engine     █░░░░░░░░░░░░░░░░░░    2/32   (6%) ⏳ NEXT
ACA-04: API Layer           ███░░░░░░░░░░░░░░░░    4/28  (14%) ⏳
ACA-05: Frontend            ░░░░░░░░░░░░░░░░░░░    0/42   (0%)
ACA-06: Billing             ████████████████████  18/18 (100%) ✅
ACA-07: Delivery            ░░░░░░░░░░░░░░░░░░░    0/9    (0%)
ACA-08: Observability       ░░░░░░░░░░░░░░░░░░░    0/14   (0%)
ACA-09: i18n                ░░░░░░░░░░░░░░░░░░░    0/18   (0%)
ACA-10: Hardening           ░░░░░░░░░░░░░░░░░░░    0/15   (0%)
ACA-11: Phase 2 Infra       ░░░░░░░░░░░░░░░░░░░    0/9    (0%)
ACA-12: Data Model          ░░░░░░░░░░░░░░░░░░░    0/8    (0%)
ACA-13: Best Practices      ░░░░░░░░░░░░░░░░░░░    0/11   (0%)
ACA-14: DPDCA Agent         ███████████████░░░░   11/14  (79%) ⏳

TOTAL                       ███████░░░░░░░░░░░░   73/256 (28.5%)
```

### Next 5 Stories (recommended by progress-report)
1. **ACA-03-001** -- Load all 12 rules from ALL_RULES ⭐ TEST TARGET
2. ACA-03-002 -- Handle rule failure in isolation
3. ACA-03-003 -- Persist findings to Cosmos
4. ACA-03-004 -- Update AnalysisRun status
5. ACA-03-005 -- Write findingsSummary

### Sprint 3 Deliverables ✅
- [x] Veritas evidence receipts (+5 metrics)
- [x] ADO bidirectional sync (4 integration points)
- [x] Retry logic with exponential backoff (5s, 10s, 20s)
- [x] Enhanced sprint summary dashboard (metrics table, velocity)
- [x] Parallel execution infrastructure (ThreadPoolExecutor ready)
- [x] 5-skill system (veritas-expert, sprint-advance, sprint-report, gap-report, progress-report)
- [x] Data model seeded (256 stories, 14 epics, 73 done)
- [x] MTI: 70 (gate: 30) ✅ PASS

---

## Telemetry Status

### Evidence Receipts (7 fields)
| Field | Status | Source | Notes |
|-------|--------|--------|-------|
| story_id | ✅ WORKING | Manifest | ACA-NN-NNN format |
| phase | ✅ WORKING | Hardcoded | "A" (Audit/Complete) |
| timestamp | ✅ WORKING | datetime.now(utc) | ISO 8601 UTC |
| artifacts | ✅ WORKING | written_files | File paths array |
| test_result | ✅ WORKING | pytest exit code | PASS/FAIL |
| commit_sha | ✅ WORKING | git rev-parse HEAD | Git commit SHA |
| duration_ms | ✅ WORKING | story start → complete | Execution time |
| files_changed | ✅ WORKING | len(artifacts) | Artifact count |
| tokens_used | ⚠️ TODO | LLM API response | Not yet extracted |
| test_count_before | ⚠️ TODO | pytest --co | Not yet parsed |
| test_count_after | ⚠️ TODO | pytest --co | Not yet parsed |

**Working**: 5/7 fields (71%) | **TODO**: 2/7 fields (29%)

### ADO Integration (4 points)
| Point | Status | Trigger | Action |
|-------|--------|---------|--------|
| Story Start | ✅ READY | Line ~831 | PATCH state → Active + comment |
| Story Complete | ✅ READY | Line ~868 | PATCH state → Done + comment |
| Story Failure | ✅ READY | Line ~878 | POST comment with error |
| Sprint Complete | ✅ READY | Line ~1005 | POST summary to Feature WI |

**Blockers**: Requires ADO_PAT secret (deploy on Day 3)

### Data Model Updates
| Operation | Status | Endpoint | Notes |
|-----------|--------|----------|-------|
| Story status | ✅ READY | PUT /model/requirements/{id} | planned → done |
| Endpoint schemas | ✅ READY | Via put-schemas.py | After seed |
| Sprint records | 🟡 TODO | PUT /model/sprints/{id} | Need sprint layer |

### Sprint Metrics (5 metrics)
| Metric | Status | Calculation | Output |
|--------|--------|-------------|--------|
| Duration | ✅ WORKING | end_dt - start_dt | minutes |
| Velocity | ✅ WORKING | stories / duration_days | stories/day |
| Completion % | ✅ WORKING | done / total × 100 | percentage |
| Avg Story Time | ✅ WORKING | duration / story_count | minutes/story |
| Total Files | ✅ WORKING | sum(len(artifacts)) | file count |

---

## Immediate Next Actions (Today)

### Day 1 Validation ✅ COMPLETE
- [x] Test sprint agent locally (test-runner.py executed)
- [x] Validate manifest loading (ACA-03-001 loaded)
- [x] Validate spec reading (saving-opportunity-rules.md found)
- [x] Validate evidence stub (receipt written)
- [x] Commit Sprint 3 + 5-skill system (pushed to main)
- [x] Understand sprint agent architecture (GitHub Actions + LLM)

### Day 2 Actions (Deploy ADO Integration)
```powershell
# 1. Get ADO PAT from Key Vault
az keyvault secret show --vault-name marcosandkv20260203 --name ADO-PAT --query value -o tsv

# 2. Deploy to GitHub Secrets
gh secret set ADO_PAT --repo eva-foundry/51-ACA --body "<pat-value>"

# 3. Validate secret deployed
gh secret list --repo eva-foundry/51-ACA | grep ADO_PAT

# 4. Test gap-report skill
# User: "gap report" or "what's blocking us"

# 5. Test sprint-report skill
# User: "sprint 2 report" or "sprint metrics"
```

### Day 3-4 Actions (First GitHub Actions Test)
```bash
# 1. Create GitHub issue with test manifest
gh issue create \
  --title "Test Sprint: ACA-03-001 (Single Story E2E)" \
  --body "<!-- SPRINT_MANIFEST
$(cat test-manifest-ACA-03-001.json)
-->" \
  --label "sprint,test" \
  --repo eva-foundry/51-ACA

# 2. Trigger sprint-agent workflow
gh workflow run sprint-agent.yml \
  --field issue=<issue-number> \
  --repo eva-foundry/51-ACA

# 3. Monitor execution
gh run watch --repo eva-foundry/51-ACA

# 4. Validate outputs
# - Check code generated (13 files in services/analysis/app/rules/)
# - Check tests pass (pytest services/analysis/ -v)
# - Check evidence receipt (.eva/evidence/ACA-03-001-receipt.json)
# - Check ADO sync (work item state transitions)
# - Check GitHub updates (issue comments)
# - Check data model (story status = done)
# - Check MTI (should remain >= 70)
```

---

## Blockers & TODOs

### Critical Blockers (Must Fix Before Sprint 4)
1. ⚠️ **tokens_used tracking** (sprint_agent.py line ~891)
   - Extract from LLM API response
   - Add to evidence receipt
   - Estimated effort: 30 minutes

2. ⚠️ **test_count tracking** (sprint_agent.py line ~842)
   - Run pytest --co before/after
   - Parse output for test count
   - Estimated effort: 45 minutes

3. ⚠️ **ADO_PAT deployment** (GitHub Secrets)
   - Get PAT from Key Vault
   - Deploy to eva-foundry/51-ACA repo
   - Estimated effort: 15 minutes

### Nice-to-Have (Post-Sprint 4)
4. 🟡 **Sprints layer population** (data model)
   - Add sprint records to data model
   - Track sprint metrics over time
   - Estimated effort: 2 hours

5. 🟡 **Blockers field in model** (data model schema)
   - Add blockers array to story schema
   - Update seed-from-plan.py
   - Estimated effort: 1 hour

6. 🟡 **Milestone tracking** (data model)
   - Add milestone field to story schema
   - Track M1.0 readiness
   - Estimated effort: 1 hour

7. 🟡 **Rollback strategy** (sprint_agent.py)
   - Implement rollback_story()
   - Test with injected failure
   - Estimated effort: 3 hours

8. 🟡 **Monitoring workflow** (GitHub Actions)
   - Create sprint-agent-monitor.yml
   - Set up alerting (Teams/Slack)
   - Estimated effort: 2 hours

---

## Decision Points

### Go/No-Go Criteria (Day 10)

**GO Criteria** (all must be ✅):
- [ ] Single story executes without errors (Day 4)
- [ ] All 7 evidence fields captured (complete TODOs Day 8)
- [ ] ADO sync works (deploy secret Day 3)
- [ ] pytest gate enforced (validate Day 4)
- [ ] MTI gate enforced (validate Day 6)
- [ ] Data model updates successful (validate Day 4)
- [ ] Sprint metrics calculated (validate Day 5)
- [ ] sprint-advance executes 5 phases (validate Day 6)

**NO-GO Criteria** (any triggers halt):
- [ ] Sprint agent crashes (unhandled exception)
- [ ] pytest fails after 3 retries
- [ ] MTI drops below 30
- [ ] Evidence receipt missing fields
- [ ] ADO sync fails (> 10% error rate)
- [ ] Data model returns 409 conflict

---

## Key Resources

**Docs**:
- [AGENT-AUDIT-PLAN.md](AGENT-AUDIT-PLAN.md) -- Full audit plan (1000+ lines)
- [STATUS.md](STATUS.md) -- v1.14.0, Sprint 3 summary
- [PLAN.md](PLAN.md) -- 14 epics, 256 stories

**Code**:
- [.github/scripts/sprint_agent.py](.github/scripts/sprint_agent.py) -- 1054 lines
- [.github/workflows/sprint-agent.yml](.github/workflows/sprint-agent.yml) -- Workflow def
- [test-runner.py](test-runner.py) -- Local validation script

**Skills**:
- [.github/copilot-skills/veritas-expert.skill.md](.github/copilot-skills/veritas-expert.skill.md) -- 302 lines
- [.github/copilot-skills/sprint-advance.skill.md](.github/copilot-skills/sprint-advance.skill.md) -- 498 lines
- [.github/copilot-skills/progress-report.skill.md](.github/copilot-skills/progress-report.skill.md) -- ~350 lines
- [.github/copilot-skills/gap-report.skill.md](.github/copilot-skills/gap-report.skill.md) -- ~300 lines
- [.github/copilot-skills/sprint-report.skill.md](.github/copilot-skills/sprint-report.skill.md) -- ~300 lines

**Data**:
- [data-model/aca-model.db](data-model/aca-model.db) -- Local SQLite (348 objects)
- [.eva/trust.json](.eva/trust.json) -- MTI=70
- [test-manifest-ACA-03-001.json](test-manifest-ACA-03-001.json) -- Single story test

---

**NORTH STAR DASHBOARD** -- Updated 2026-02-28

**Next Milestone**: Day 4 (First GitHub Actions Test) -- ACA-03-001 E2E execution
