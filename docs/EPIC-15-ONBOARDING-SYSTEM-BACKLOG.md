# BACKLOG UPDATE: Project 51 (ACA) Onboarding System Implementation

**Version**: 2.0.0 (Gap Closure Complete)  
**Created**: 2026-03-02  
**Updated**: 2026-03-02 (Critical gaps fixed, revised estimates)  
**Status**: Ready for Sprint 14 Planning (production-ready architecture)

---

## BACKLOG PRIORITY ITEMS

### CRITICAL (Block all other work)

**[BACKLOG-1] Retire 51-ACA project-management data model (port 8055)**
- **Status**: PLANNED
- **Priority**: P0 (high)
- **Dependency**: Must move project governance to 37-data-model (central source of truth)
- **Effort**: 3 FP
- **Description**:
  - Current state: SQLite on port 8055 (project sprints, stories, WBS, evidence)
  - Target state: Use 37-data-model (port 8010, Cosmos) for all project management
  - Rationale: Separation of concerns (project mgmt ≠ app runtime data)
  - Action items:
    1. Export all Sprint 1-13 evidence receipts from port 8055
    2. Import into 37-data-model /model/evidence layer
    3. Validate no loss of data
    4. Update copilot-instructions.md: bootstrap now points to port 8010 only
    5. Update .github/sprints/ to pull from 37-data-model API
    6. Test: sprint-advance.py, veritas-expert skill use 37-data-model

**[BACKLOG-2] Create 51-ACA Onboarding Service (new Epic 15)**
- **Status**: PLANNED (use Architecture document as specification)
- **Priority**: P0
- **Effort**: 52 FP (5.2 sprints @ 10 FP/sprint)
- **Revised from**: 50 FP (gap analysis identified underestimations)
- **Description**: Full onboarding system per ARCHITECTURE-ONBOARDING-SYSTEM.md (v2.0.0 with security/performance/crypto improvements)

---
2 FP, Week 1)

### Story ACA-15-000: Infrastructure Provisioning (Bicep + RBAC)
- **Effort**: 2 FP
- **NEW**: Added during gap analysis (missing from original plan)
- **Files**:
  - `infra/cosmos.bicep` (Cosmos DB with 9 containers, TTL, indexes)
  - `infra/keyvault.bicep` (Key Vault for HMAC signing key)
  - `infra/rbac.bicep` (ACA Managed Identity role assignments)
- **Acceptance**:
  - [ ] Bicep deploys 9 Cosmos containers with correct TTL policies (Section 1.3)
  - [ ] Indexes configured per Section 1.3 (engagementId, subscriptionId, currentGate, status)
  - [ ] Key Vault secret `ACA-HMAC-SigningKey` created (256-bit random)
  - [ ] ACA Managed Identity assigned Reader + Cost Management Reader roles
  - [ ] Test: Deploy to marco-sandbox, verify all resources created

### Story ACA-15-001: Cosmos DB Schema for Onboarding
- **Effort**: 3 FP
- **UPDATED**: Now includes operational config (TTL, indexes, RU/s allocation)
- **Acceptance**:
  - [ ] 9 containers created in marcosandcosmos20260203 (NOT 7): onboarding-sessions, role-assessments, extraction-manifests, inventories, cost-data, advisor-recommendations, findings, extraction-logs, evidence-receipts
  - [ ] All containers have correct partition key (/subscriptionId)
  - [ ] TTL policies applied per Section 1.3 (90 days for operational, 365 for findings, NEVER for evidence)
  - [ ] Indexes defined for queries (Section 1.3 indexing strategy)
  - [ ] RU/s allocation: 400 RU/s provisioned (shared, MVP)
  - [ ] Schema document (ARCHITECTURE-ONBOARDING-SYSTEM.md Section 1) validates against actual containers
  - [ ] Test: Insert test document in each container, verify partition isolation and TTL expiration (wait 1 day for TTL test)

### Story ACA-15-002: Gate State Machine Core (with Timeout/Retry)
- **Effort**: 3 FP
- **UPDATED**: Now includes timeout and retry logic per gap analysis
- **Files**:
  - `services/aca-onboarding/state_machine.py` (200 lines, increased from 150)
  - `services/aca-onboarding/models.py` (gate enums, state transitions, timeout configs)
- **Acceptance**:
  - [ ] Enum: Gate (1-7), GateStatus (PASSED, FAILED, TIMEOUT, RETRY_REQUESTED, etc)
  - [ ] State machine class with transition rules + timeout handling
  - [ ] GATE_2 (client decision) timeout: 4 FP, Week 2-3)

### Story ACA-15-004: Azure SDK Wrappers (with Pagination/Retry)
- **Effort**: 6 FP (increased from 4 FP due to pagination/retry complexity)
- **Files**:
  - `services/aca-onboarding/azure_sdk.py` (600 lines, increased from 400)
- **CRITICAL ADDITIONS**:
  - Resource Graph pagination (max 1,000 items/response, 15 req/sec limit)
  - Cost Management API pagination (max 1,000 rows/response, 10 req/min limit, 30-day windows)
  - Advisor API pagination (max 100 items/response, 5 req/sec limit)
  - Retry logic: exponential backoff for 429 rate limits (tenacity library)
  - Worker pool sizing: 3 concurrent cost workers (respect 10 req/min limit)
  - Batch writing to Cosmos: 100 items/batch (Section 6.3)
- **Acceptance**:
  - [ ] Resource Graph query wrapper (paginated, handles 15 req/sec rate limit)
  - [ ] Cost Management API wrapper (91-day query, 30-day windows, pagination, 3 workers)
  - [ ] Advisor API wrapper (paginated, handles 403 missing-role gracefully)
  - [ ] Error handling: retry 429 with exponential backoff (4s, 8s, 16s, 32s, 64s)
  - [ ] Batch write helper: write_cost_data_batch (100 items/batch to Cosmos)
  - [ ] Integration test: queries against marco-sandbox subscription (500+ resources, 45K cost rows)
  - [ ] Integration test: simulate 429 rate limit, verify retry succeeds
  - [ ] Performance test: extract 45K cost rows in <10 minutes

### Story ACA-15-005: CLI Command Structure (with Auth Flow)
- **Effort**: 3 FP (increased from 2 FP due to auth flow documentation)
- **Files**:
  - `cli/aca_cli.py` (400 lines, increased from 300)
  - `cli/auth.py` (Azure CLI integration + device code fallback, 150 lines)
- **CRITICAL ADDITIONS**:
  - Azure CLI token acquisition: `az account get-access-token`
  - Device code flow fallback (if Azure CLI not installed)
  - Token refresh logic (tokens expire after 1 hour)
- **Acceptance**:
  - [ ] Commands: init, resume, list, get, extract-logs, retry-extraction
  - [ ] Auth: detect Azure CLI, get token via `az account get-access-token --resource https://management.azure.com`
  - [ ] Auth fallback: if Azure CLI missing, use device code flow (prompt user to visit aka.ms/devicelogin)
  - [ ] Token refresh: if token expires during long extraction, auto-refresh
  - [ ] Prompts: yes/no decisions, progress display
  - [ ] Output formatting: table, json, text
  - [ ] Test: CLI interactive flow end-to-end (no actual extraction)
  - [ ] Test: Auth flow on machine without Azure CLI (device code fallback works)

### Story ACA-15-006: Extraction Pipeline (Inventory + Costs + Advisor)
- **Effort**: 5 FP (increased from 4 FP due to Azure limits handling)
- **Files**:
  - `services/aca-onboarding/extraction.py` (700 lines, increased from 500)
- **CRITICAL ADDITIONS**:2 FP, Week 4)

### Story ACA-15-008: Analysis Rules Engine (with 18-azure-best Integration)
- **Effort**: 6 FP (increased from 4 FP due to 18-azure-best patterns integration)
- **Files**:
  - `services/aca-onboarding/analysis.py` (600 lines, increased from 400)
  - `services/aca-onboarding/heuristics/*.py` (7 pattern modules)
- **CRITICAL ADDITIONS**:
  - Integration with 18-azure-best patterns (cost-optimization.md, anti-patterns.md)
  - 7 heuristic modules: vm-rightsizing, reserved-capacity, storage-tiering, orphan-resources, unattached-disks, idle-resources, cost-anomalies
  - Narrative generation (explain WHY recommendation applies)
- **Acceptance**:
  - [ ] Heuristics for cost optimization: right-sizing (VM CPU <30%), reserved capacity (stable workloads), storage tiering (cool/archive)
  - [ ] Integration with 18-azure-best: load cost-optimization.md, apply Agent Checklist patterns
  - [ ] Anti-pattern detection: apply 18-azure-best anti-patterns.md (10 patterns: busy-database, chatty-io, extraneous-fetching, improper-instantiation, monolithic-persistence, no-caching, retry-storm, synchronous-io, etc.)
  - [ ] Findings generation algorithm: rank by annual savings (DESC), filter by effort (easy/medium/hard)
  - [ ] Narrative generation: explain recommendation with reference to 18-azure-best documentation URL
  - [ ] Test: Apply rules to 100-item test dataset (50 VMs, 20 storage accounts, 10 SQL DBs, 20 misc), verify outputs (12+ findings)
  - [ ] Test: Validate narratives reference 18-azure-best URLs

### Story ACA-15-009: Evidence Receipt Generation (with Cryptographic Signing)
- **Effort**: 2 FP (decreased from 3 FP, simpler with HMAC library)
- **Files**:
  - `services/aca-onboarding/evidence.py` (200 lines, decreased from 250)
- **CRITICAL ADDITIONS**:
  - HMAC-SHA256 signing (Section 7.1): prevent tampering
  - Key Vault integration: retrieve ACA-HMAC-SigningKey
  - Verification function: detect tampered receipts
- **Acceptance**:
  - [ ] Build immutable evidence-receipt per ARCHITECTURE Section 7.2
  - [ ] HMAC-SHA256 signature computed over canonical JSON (sorted keys, no whitespace)
  - [ ] Key Vault integration: retrieve signing key via DefaultAzureCredential
  - [ ] Signature fields added: signature, signedAt, signatureAlgorithm, keyVaultKeyId
  - [ ] Verification function: verify_evidence_receipt returns True/False
  - [ ] Cosmos write with no-update TTL (evidence-receipts container has no TTL = permanent retention)
  - [ ] GET /evidence returns full receipt + tamper_check (is_valid=True/False)
  - [ ] Test: Evidence receipt validates against schema
  - [ ] Test: Modify receipt manually, verify verification function returns False
  - [ ] Test: Rotate HMAC key, verify old receipts still verify (keyVaultKeyId includes version)

### Story ACA-15-010: Integration Tests (All Gates + Security)
- **Effort**: 4 FP (increased from 3 FP for comprehensive security/performance testing)
- **Files**:
  - `tests/test_onboarding_gates.py` (500 lines, increased from 400)
  - `tests/test_security.py` (200 lines, NEW)
  - `tests/test_performance.py` (150 lines, NEW)
- **CRITICAL ADDITIONS**:
  - Security tests: GDPR delete, token validation, RBAC enforcement
  - Performance tests: API latency (<2s), extraction time (<20min), RU/s consumption
- **Acceptance**:
  - [ ] End-to-end test: init → role assessment → decision → preflight → extraction → analysis → evidence
  - [ ] Test with marco-sandbox subscription
  - [ ] All 7 gates pass with no errors
  - [ ] Evidence receipt valid (signature verification passes)
  - [ ] Security test: GDPR delete removes PII (verify subscriptionId partition deleted from 8 containers)
  - [ ] Security test: Evidence receipt PII redacted (not deleted)
  - [ ] Security test: Invalid token returns 401
  - [ ] Security test: User cannot access other tenant's engagement (returns 403)
  - [ ] Performance test: POST /init latency <500ms
  - [ ] Performance test: Extract 500 resources in <2min
  - [ ] Performance test: Extract 45K cost rows in <10min
  - [ ] Performance test: Analysis completes in <5minons, progress display
  - [ ] Output formatting: table, json, text
  - [ ] Test: CLI interactive flow end-to-end (no actual extraction)

### Story ACA-15-006: Extraction Pipeline (Inventory + Costs)
- **Effort**: 4 FP
- **Files**:
  - `services/aca-onboarding/extraction.py` (500 lines)
- **Acceptance**:
  - [ ] extract_inventory() function (paginated, logs progress)
  - [ ] extract_cost_data() function (3 parallel workers, progress logs)
  - [ ] Recovery checkpoints (lastSuccessfulPage, lastSuccessfulWindow)
  - [ ] Integration test: extract from marco-sandbox, verify Cosmos write

### Story ACA-15-007: Logging + Recovery
- **Effort**: 2 FP
- **Files**:
  - `services/aca-onboarding/logging.py` (200 lines)
- **Acceptance**:
  - [ ] Every operation logs to extraction-logs container
  - [ ] Recovery checkpoint stored with each log
  - [ ] GET /extract-logs returns paginated logs with checkpoints
  - [ ] POST /extract/retry resumes from last checkpoint
  - [ ] Test: Simulate extraction failure, verify resume works
REVISED EFFORT SUMMARY (Gap Analysis Update)

**Original Epic 15 Estimate**: 50 FP (4 sprints @ 10 FP/sprint + 1 sprint @ 10 FP)

**Revised Epic 15 Estimate**: 52 FP (5.2 sprints @ 10 FP/sprint)

**Breakdown of Changes**:
- **ACA-15-000**: Infrastructure provisioning (NEW): +2 FP
- **ACA-15-001**: Cosmos DB schema: 3 FP (unchanged, but scope expanded: operational config)
- **ACA-15-002**: Gate state machine: 3 FP (unchanged, but scope expanded: timeout/retry)
- **ACA-15-003**: FastAPI backend: 4 FP (unchanged, but scope expanded: security/health endpoints)
- **ACA-15-004**: Azure SDK wrappers: 4 → **6 FP** (+2 FP: pagination/retry complexity underestimated)
- **ACA-15-005**: CLI: 2 → **3 FP** (+1 FP: auth flow missing from original)
- **ACA-15-006**: Extraction pipeline: 4 → **5 FP** (+1 FP: Azure limits handling)
- **ACA-15-007**: Logging + recovery: 2 FP (unchanged)
- **ACA-15-008**: Analysis engine: 4 → **6 FP** (+2 FP: 18-azure-best patterns integration)
- **ACA-15-009**: Evidence receipts: 3 → **2 FP** (-1 FP: simpler with HMAC library)
- **ACA-15-010**: Integration tests: 3 → **4 FP** (+1 FP: security/performance testing)
- **ACA-15-011**: React components: 5 FP (unchanged)
- **ACA-15-012**: Findings report UI: 5 FP (unchanged)

**Total Effort Increase**: +7 FP (14% increase)

**Why the increase?**:
- Gap analysis identified 5 critical gaps (container count, Cosmos operational config, security/compliance, Azure API limits, crypto signing)
- Original estimates underestimated Azure SDK pagination/retry logic complexity (Resource Graph 1,000 items/query, Cost API 1,000 rows/response, 429 rate limits)
- Security requirements (RBAC, GDPR, rate limiting) not scoped in original plan
- Cryptographic signing (HMAC-SHA256) vs simple hashing adds Key Vault integration
- Performance optimization (caching, batch writes, worker pools) not in original scope

**Production-readiness trade-off**: +7 FP effort → Architecture grade B+ (85%) → A (production-ready)

---

## 
---

## PHASE 3: ANALYSIS + EVIDENCE (Sprint 16, 10 FP, Week 4)

### Story ACA-15-008: Analysis Rules Engine
- **Effort**: 4 FP
- **Files**:
  - `services/aca-onboarding/analysis.py` (400 lines)
- **Acceptance**:
  - [ ] Heuristics for cost optimization (right-sizing, reserved capacity, storage tiering)
  - [ ] Integration with 18-azure-best best practices
  - [ ] Findings generation algorithm
  - [ ] Test: Apply rules to 100-item test dataset, verify outputs

### Story ACA-15-009: Evidence Receipt Generation
- **Effort**: 3 FP
- **Files**:
  - `services/aca-onboarding/evidence.py` (250 lines)
- **Acceptance**:
  - [ ] Build immutable evidence-receipt per ARCHITECTURE Section 6
  - [ ] Content hash + timestamp
  - [ ] Cosmos write with no-update TTL
  - [ ] GET /evidence returns full receipt
  - [ ] Test: Evidence receipt validates against schema

### Story ACA-15-010: Integration Tests (All Gates)
- **Effort**: 3 FP
- **Files**:
  - `tests/test_onboarding_gates.py` (400 lines)
- **Acceptance**:
  - [ ] End-to-end test: init → role assessment → decision → preflight → extraction → analysis → evidence
  - [ ] Test with marco-sandbox subscription
  - [ ] All gates pass with no errors
  - [ ] Evidence receipt valid

---

## PHASE 4: WEB UI (Sprint 17, 10 FP, Week 5)

### Story ACA-15-011: React Components (Role Assessment + Preflight)
- **Effort**: 5 FP
- **Files**: `31-eva-faces/src/components/onboarding/*.tsx`
- **Acceptance**:
  - [ ] Role assessment report card (show discovered roles, recommendation)
  - [ ] Preflight manifest card (show extraction plan, sizes, duration)
  - [ ] Extraction progress card (real-time logs, progress bar)

### Story ACA-15-012: Findings Report UI
- **Effort**: 5 FP
- **Files**: `31-eva-faces/src/pages/findings.tsx`
- **Acceptance**:
  - [ ] Display savings opportunities (ranked, effort, risk)
  - [ ] PDF export (findings + evidence)
  - [ ] Service menu tier selector (Tier 1/2/3)

---

## NOTES FOR SPRINTS

**For all sprints**: 
- Use DPDCA (Discover → Plan → Do → Check → Act)
- Update PLAN.md + STATUS.md each session
- Generate evidence receipts per Sprint 11-13 pattern
- Reference ARCHITECTURE-ONBOARDING-SYSTEM.md as golden spec

**Testing strategy**:
- CLI: functional tests (yes/no prompts, output format)
- Backend: unit (state machine, Azure SDK wrappers) + integration (Cosmos CRUD, extraction)
- End-to-end: init → evidence receipt, using marco-sandbox subscription

**Performance targets**:
- POST /init: <500ms
- GET /manifest: <1s
- Extract inventory (500 items): <2min
- Extract costs (90 days): <10min
- Analysis: <5min

---

**Ready for Sprint 14 kickoff.**
