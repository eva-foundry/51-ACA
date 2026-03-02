# SPRINT-PLAN-ACA-17: Tier 3 Execution (Sprint-002)

**Date**: 2026-03-02
**Sprint**: Sprint-002 (Tier 3: AI Agent Enhancement)
**Duration**: 4 weeks (estimated Oct-Nov 2026, but can execute immediately)
**Velocity Target**: 34 story points / 5 stories (same as ACA-16 Sprint-001)
**Baseline**: ACA-16 Sprint-001 COMPLETE (Tier 2: 25 points, 4.5 stories/hour)
**Acceleration Target**: Deliver all 5 ACA-17 stories by EOW 3 (accelerate via parallel story work)

---

## SPRINT OVERVIEW

| Week | Stories | Points | Focus | Deliverable |
|------|---------|--------|-------|-------------|
| W1 | ACA-17-001 | 8 | Failure Classifier Agent | Classify transient vs permanent errors (95%+ accuracy) |
| W1-W2 | ACA-17-002 | 5 | Retry Tuning Agent | Adaptive backoff (30% fewer retries on permanent) |
| W2 | ACA-17-003 | 8 | Async Orchestration | Parallel story syncs (3x speedup) |
| W3 | ACA-17-004 | 5 | Advisor Agent | Recovery recommendations + RAG context |
| W3-W4 | ACA-17-005 | 8 | Multi-Agent Orchestrator | Coordinate all 4 agents via 29-Foundry Workflow |
| **TOTAL** | **5 stories** | **34 points** | **Tier 3 Foundation** | **Reliability 8.0 → 9.5** |

---

## STORY EXECUTION SEQUENCE

### Story 1: ACA-17-001 (Failure Classifier Agent)
**Points**: 8 (L) | **Assign**: Agent Expert | **Duration**: 4-5 hours (EOD Day 1)

**Pre-Work** (30 min):
1. Set up Python venv in 51-ACA/agents/
2. Install: agent-framework-azure-ai==1.0.0b260107, agent-framework-core, python-dotenv
3. Configure .env with FOUNDRY_PROJECT_ENDPOINT + FOUNDRY_MODEL_DEPLOYMENT_NAME (gpt-4o)

**Implementation** (3 hours):
1. Create agents/failure-classifier/classifier_agent.py
   - AgentClient(model=gpt-4o, system_prompt="Classify errors into transient/permanent categories...")
   - Input schema: ErrorContext (message, code, context, retry_count)
   - Output schema: Classification (error_id, classification, confidence, recommended_action)
2. Create agents/failure-classifier/system_prompt.md
   - Training data: 20+ error patterns from 18-azure-best
   - Examples: timeout→transient, 403→permanent, 429→transient
3. Create infra/container-apps-job/scripts/Failure-Classifier-Agent.ps1 (wrapper)
   - Test-ClassifierConnection function
   - Invoke-ClassifierAgent function (calls Python gRPC/HTTP wrapper)
   - Fallback-To-RuleClassifier function (hardcoded patterns)
4. Integrate with sync-orchestration-job.ps1:
   - Line 36: Import Failure-Classifier-Agent.ps1
   - Line 205: Call Test-ClassifierConnection at startup
   - Line 255: Call Invoke-ClassifierAgent on caught exception
   - Line 265: Log Emit-FailureClassifiedEvent

**Testing** (1 hour):
1. Test classifier on 5 error patterns:
   - Timeout (500ms delay) → transient, retry ✓
   - 403 Forbidden → permanent, skip ✓
   - Cosmos 429 (rate-limit) → transient, backoff ✓
   - DNS error → transient, wait 30s ✓
   - Partition key mismatch → permanent, escalate ✓
2. Performance: latency <100ms p99 ✓
3. Fallback: if agent down, rules-based classifier works ✓

**Commit**: `feat(ACA-17-001): failure classifier agent - 95%+ accuracy transient/permanent detection`

---

### Story 2: ACA-17-002 (Retry Tuning Agent)
**Points**: 5 (M) | **Assign**: Agent Expert | **Duration**: 2-3 hours (EOD Day 2)

**Pre-Work** (15 min):
1. Cosmos: seed error_pattern table (20 rows, columns: error_code, total_attempts, successful_recovery_count)

**Implementation** (1.5 hours):
1. Create agents/retry-tuner/tuner_agent.py
   - Input: ErrorClassification (from ACA-17-001), retry_count, elapsed_ms
   - Output: { next_delay_ms, confidence, reason }
   - System prompt: "Recommend optimal retry delays based on error type..."
2. Integration with Invoke-With-Retry.ps1:
   - Line 80: Call Invoke-TunerAgent (before retry attempt N)
   - Use agent-recommended delay instead of static formula
   - Log RetryTuned event
3. Cosmos integration:
   - Query error_pattern table for this error_code
   - Calculate success_probability = recovery_count / total
   - If probability < 0.5: longer backoff (vs default exponential)
4. Runbooks integration (optional):
   - Check scheduled maintenance windows
   - If maintenance window open: recommend wait until window closes
5. Fallback: use static exponential backoff if agent unavailable

**Testing** (30 min):
1. Test 4 scenarios:
   - Network timeout (retry count 2): recommend 8s (static exponential) ✓
   - Cosmos 429 (detected rate-limit, retry 1): recommend 5s (tuned longer) ✓
   - 403 Forbidden (permanent, confidence 0.99): recommend stop ✓
   - Maintenance window detected: recommend wait 2 hours ✓
2. Performance: latency <100ms with Cosmos lookup ✓
3. Effectiveness: 30% fewer retries on permanent failures ✓

**Commit**: `feat(ACA-17-002): retry tuning agent - 30% fewer retries adaptive backoff`

---

### Story 3: ACA-17-003 (Async Orchestration)
**Points**: 8 (L) | **Assign**: PowerShell Expert | **Duration**: 4-5 hours (EOD Day 3)

**Pre-Work** (30 min):
1. Review checkpoint logic from ACA-16-005
2. Review rollback logic from ACA-16-006

**Implementation** (3 hours):
1. Create infra/container-apps-job/scripts/Async-Orchestrator.ps1 (280 lines)
   - class ParallelJobBatch { StoryIndex[], Jobs[], CheckpointAfter }
   - function Start-AsyncOrchestration { $batchSize = 3; for each batch: Start-Job, Wait-Job }
   - function Get-JobResult { check exit code, capture stdout/stderr }
   - function Save-CheckpointAfterBatch { Save-Checkpoint after each story completes }
2. Integration with sync-orchestration-job.ps1:
   - Line 38: Import Async-Orchestrator.ps1
   - Line 225: Call Start-AsyncOrchestration (instead of sequential loop)
   - Pass: resumeStartIndex, totalStories, batchSize=3
   - Receive: completedCount, failureCount, finalCheckpoint
3. Rate-limit handling:
   - Monitor Circuit Breaker state during orchestration
   - If CB.OPEN: reduce batchSize to 1 (sequential fallback)
   - If CB.HALF_OPEN: reduce batchSize to 2 (conservative)
4. Rollback integration:
   - If any job fails (exit 1): Restore-RollbackSnapshot immediately
   - Stop orchestration
   - Emit RollbackTriggered event
5. Timeout per job: 30s (fail-fast)

**Testing** (1.5 hours):
1. Test 4 scenarios:
   - 21 stories, 3 parallel, all succeed: duration ~30s (3x speedup) ✓
   - Story 10 fails during job 7: Restore-RollbackSnapshot, all reverted ✓
   - Crash after story 8: resume from 16 (skip 0-15 already done) ✓
   - Cosmos rate-limit detected (CB.OPEN): parallelism drops to 1, continues ✓
2. Performance: measure actual duration vs expected 30s ✓

**Commit**: `feat(ACA-17-003): async orchestration - 3x speedup parallel story syncs`

---

### Story 4: ACA-17-004 (Advisor Agent)
**Points**: 5 (M) | **Assign**: Agent Expert | **Duration**: 2-3 hours (EOD Day 4)

**Pre-Work** (15 min):
1. Load 18-azure-best entries into Cosmos (via MCP Cosmos)
   - Cosmos rate-limit best practices
   - RU scaling guidance
   - Service troubleshooting patterns

**Implementation** (1.5 hours):
1. Create agents/sync-advisor/advisor_agent.py
   - Input: { rollback_snapshot, failure_log, subscription_size, cb_state_history }
   - Output: { recommended_action, parallelism_level, guidance, confidence }
   - System prompt: "Recommend recovery actions based on failure patterns and Azure best practices..."
2. RAG integration (18-azure-best):
   - Create rag_context_loader.py
   - Load 3-5 relevant entries from Cosmos
   - Weave into system prompt
3. Integration with sync-orchestration-job.ps1:
   - Line 255: On critical failure, call Invoke-AdvisorAgent
   - Log AdvisorRecommendation event
   - Display guidance to operator (optional: write to /app/state/advisor-recommendation.json)
4. Recommendation logic:
   - If all 21 stories failed: "retry_all" (transient service issue)
   - If 1-3 stories failed: "retry_failed_only" (use checkpoint)
   - If >50% + CB.OPEN: "pause + increase RUs by 25%" (rate-limit)
   - If FinOps queries timing out: "increase Query RUs" (per 18-azure-best guidance)

**Testing** (30 min):
1. Test 4 scenarios:
   - All stories fail: recommend "retry_all" with confidence 0.9 ✓
   - Stories 15-21 fail: recommend "retry_failed_only" (skip 0-14) ✓
   - CB.OPEN + parallelism 3: recommend reduce to 1 + increase RUs ✓
   - Cosmos 429 detected: recommend "increase RUs by 25%" with best practice link ✓
2. RAG verification: guidance includes snippet from 18-azure-best ✓

**Commit**: `feat(ACA-17-004): sync advisor agent - recovery recommendations + RAG context`

---

### Story 5: ACA-17-005 (Multi-Agent Orchestrator)
**Points**: 8 (L) | **Assign**: Agent Framework Expert | **Duration**: 4-5 hours (EOD Day 5)

**Pre-Work** (30 min):
1. Review 29-Foundry multi-agent orchestrator patterns
2. Review Microsoft Agent Framework Workflow APIs

**Implementation** (3 hours):
1. Create agents/orchestration-workflow/orchestration_workflow.py (400+ lines)
   - Define Workflow class (async orchestration framework)
   - Node 1: FailureClassifierNode (calls ACA-17-001 agent, timeout 50ms)
   - Node 2: RetryTunerNode (calls ACA-17-002 agent, timeout 100ms, depends on Node 1)
   - Node 3: AdvisorNode (calls ACA-17-004 agent, timeout 200ms, conditional on delay > 30s)
   - Output node: DecisionNode (synthesize outputs into final action)
   - Routing: Sequential Classifier → Tuner → [conditional] Advisor → Decision
2. Workflow logic:
   - Input: { error_message, error_code, retry_count, elapsed_ms, context }
   - Run Node 1: get classification
   - Run Node 2: if classification=transient, get tuned delay
   - If delay > 30s: Run Node 3 (get advisor recommendation)
   - Synthesize: return { final_action, delay_ms, guidance }
3. Integration with Invoke-With-Retry.ps1:
   - Create Invoke-OrchestrationWorkflow function (PowerShell wrapper)
   - Call before each retry attempt
   - Use returned action (retry vs skip vs escalate)
   - Non-blocking: async call, timeout 400ms → fallback to static rules
4. Fault tolerance:
   - If Classifier unavailable: use rule-based, skip Tuner/Advisor
   - If Tuner unavailable: use static exponential, continue
   - If Advisor unavailable: skip guidance (still got action)
   - Log each fault event
5. Checkpointing:
   - Save orchestration decisions to checkpoint (which agents ran, which decisions)
   - Resume: can replay decisions if needed for audit

**Testing** (1.5 hours):
1. Test 4 scenarios:
   - Network timeout → Node 1(transient) → Node 2(2s backoff) → Output ✓
   - Cosmos 429 + retry_count=4 → Node 1(rate-limit) → Node 2(5s) → Node 3(increase RUs) → Output ✓
   - 403 Forbidden → Node 1(permanent) → skip Nodes 2/3 → Output: escalate ✓
   - Workflow timeout (all agents slow): fallback to static rules+log timeout ✓
2. Performance: verify workflow duration <400ms ✓
3. Concurrency: MCP Cosmos lookups parallel with agent calls ✓

**Commit**: `feat(ACA-17-005): multi-agent orchestrator - coordinate 4 agents via 29-Foundry Workflow [SPRINT-002 COMPLETE]`

---

## DAILY STANDUP TEMPLATE

Each day, report:
- **Completed**: which acceptance criteria passed
- **In Progress**: current blockers
- **Next 24h**: next task
- **Metrics**: test count, code lines, integration points

Example (Day 1):
```
[DAY 1] ACA-17-001 Failure Classifier Agent
Completed:
  - Agent Framework agent created (gpt-4o model)
  - System prompt trained on 20+ error patterns
  - Fallback rule-based classifier working
  - 5 test scenarios PASS (timeout, 403, 429, DNS, partition-key)
  - Latency verified <100ms p99
In Progress:
  - Cosmos error_pattern table seeding (20 rows) - 80% done
Blockers:
  - FOUNDRY_MODEL_DEPLOYMENT_NAME needs gpt-4o available in Foundry (verify before D1 end)
Next 24h:
  - Complete Cosmos table seed
  - Integrate with sync-orchestration-job.ps1 (lines 36, 205, 255, 265)
  - Full acceptance criteria validation
Metrics:
  - Code: 180 lines Python (classifier_agent.py)
  - Integration: 4 touchpoints in sync-orchestration-job.ps1
  - Tests: 5/5 passing
```

---

## RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Agent Framework API breaking changes (beta SDK) | Medium | High | Pin versions: agent-framework==1.0.0b260107, test before upgrade |
| Foundry model unavailable | Low | High | Use gpt-4o-mini as fallback, test graceful degradation |
| Cosmos rate-limit during execution | Medium | Medium | Circuit Breaker (ACA-16-003) handles, Advisor recommends RU increase |
| Multi-agent orchestrator deadlock | Low | Medium | Add timeout every node, fallback to rules-based if timeout |
| Async job failures cascade | Low | High | Rollback Manager (ACA-16-006) handles all-or-nothing, no cascading |

---

## SUCCESS METRICS

**Reliability**: 8.0/10 (ACA-16) → 9.5/10 (ACA-17)
- Failure classification 95%+ accuracy
- Adaptive retry: 30% fewer retries on permanent failures
- Async speedup: 3x (21 stories: 90s → 30s)
- Agent coordination: 0 conflicts, all 4 agents routing correctly
- Fallback coverage: 100% (every agent has rule-based fallback)

**Code Quality**:
- Total lines: 1,200+ Python (agents) + 400+ PowerShell (wrappers + orchestration)
- Integration points: 20+ touchpoints with Sprint-001 modules
- Test coverage: 25+ test scenarios (all PASS)
- Acceptance criteria: 106 total (5 stories * avg 21 criteria)

**DPDCA Cycle**:
- **Discover**: ✅ Data model (4,174 objects, 13 agents), 29-Foundry patterns, Sprint-001 telemetry
- **Plan**: ✅ EPIC-17-WBS.md, SPRINT-PLAN-ACA-17.md (this document), 5 stories with 106 AC
- **Do**: → Execute stories ACA-17-001 through ACA-17-005 (sequence above)
- **Check**: → Acceptance criteria validation + performance baselines
- **Act**: → Update WBS, reflect IDs, commit with story tags, reseed data model

---

## READY TO EXECUTE?

**Blockers Before Starting**:
- [ ] Verify gpt-4o model available in Microsoft Foundry
- [ ] Verify 29-Foundry multi-agent orchestrator patterns (reference ado_plane, azure_plane agents)
- [ ] Verify 18-azure-best loaded into Cosmos (MCP Cosmos required)
- [ ] Verify agent-framework==1.0.0b260107 installable (pip)

**All Clear?** → Proceed to **DO Phase** (execute stories ACA-17-001 through ACA-17-005)

---

**Sprint Status**: READY FOR EXECUTION | Plan: COMPLETE | Next: DO PHASE
