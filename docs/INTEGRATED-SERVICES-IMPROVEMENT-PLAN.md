# Integrated Services Improvement Plan

**Version**: 1.0.0
**Date**: 2026-02-28
**Context**: Based on Sprint 2 execution and ADO sync session
**Target Services**: Data Model (37), Veritas (48), ADO Integration

---

## Executive Summary

Sprint 2 execution revealed integration gaps between the three core services that support project workflow:
- **Data Model API** (port 8010/8055) -- technical entity management
- **Veritas MCP** (port 8030) -- requirements traceability and trust scoring
- **ADO Integration** -- work item lifecycle management

This document proposes 23 specific improvements to create a seamless, single-source-of-truth workflow.

---

## 1. Data Model API Improvements (37-data-model)

### Current State
- HTTP API at `https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io`
- 27 entity layers (screens, endpoints, services, containers, etc.)
- Manual JSON file editing required for bulk operations
- PUT workflow requires audit field stripping

### Proposed Improvements

#### 1.1 Sprint Management Endpoints (HIGH PRIORITY)

**Current Pain Point**: Sprint stories must be created via direct JSON file editing or local scripts. No API to seed a sprint from PLAN.md.

**Proposed**:
```
POST /model/sprints/
Body: {
  "sprint_id": "51-ACA-sprint-03",
  "label": "Sprint 3",
  "epic_id": "epic-04",
  "start_date": "2026-03-01",
  "stories": [
    {
      "id": "ACA-04-001",
      "title": "GET /v1/findings endpoint",
      "ado_id": 3001,
      "files_to_create": ["services/api/app/routes/findings.py"],
      "acceptance": ["Returns paginated findings list"]
    }
  ]
}

Returns: {
  "sprint_id": "51-ACA-sprint-03",
  "stories_created": 15,
  "sprint_url": "/model/sprints/51-ACA-sprint-03"
}
```

**Benefit**: Single API call replaces 15+ individual story PUTs

#### 1.2 Batch Operations (HIGH PRIORITY)

**Current Pain Point**: Creating 15 sprint stories requires 15 separate PUT calls with manual row_version handling.

**Proposed**:
```
POST /model/batch
Body: {
  "operations": [
    {"method": "PUT", "path": "/model/stories/ACA-03-001", "data": {...}},
    {"method": "PUT", "path": "/model/stories/ACA-03-002", "data": {...}}
  ],
  "actor": "agent:copilot",
  "atomic": true
}

Returns: {
  "success": 15,
  "failed": 0,
  "results": [...]
}
```

**Benefit**: Atomic sprint setup, single transaction

#### 1.3 ADO Integration Layer (HIGH PRIORITY)

**Current Pain Point**: No data model representation of ADO work items. Scripts must use `az boards` CLI directly, requiring PAT token management outside the model.

**Proposed**: Add `ado_work_items` layer:
```
GET /model/ado/work-items/{ado_id}
Returns: {
  "ado_id": 2978,
  "story_id": "ACA-03-001",
  "state": "Active",
  "iteration": "51-aca\\Sprint 2",
  "assigned_to": null,
  "area_path": "51-aca"
}

PUT /model/ado/work-items/{ado_id}
Body: {
  "state": "Done",
  "iteration": "51-aca\\Sprint 2"
}
```

**Credential Management**:
```
POST /model/admin/config/ado
Body: {
  "organization": "https://dev.azure.com/marcopresta",
  "pat_token_env_var": "AZURE_DEVOPS_EXT_PAT"
}
```

**Benefit**: Single source of truth for ADO state, no external CLI calls needed

#### 1.4 Smart PUT Simplification (MEDIUM PRIORITY)

**Current Pain Point**: PUT requires:
1. GET to capture row_version
2. Strip audit fields (layer, modified_by, modified_at, created_by, created_at, row_version, source_file)
3. Convert to JSON with `-Depth 10`
4. POST with X-Actor header

**Proposed**: Accept partial updates
```
PATCH /model/stories/ACA-03-001
Body: {
  "status": "implemented",
  "implemented_in": "services/analysis/app/rules/rule_01.py"
}
Headers: {
  "X-Actor": "agent:copilot"
}

(No need to GET first, no need for full object, audit fields auto-managed)
```

**Benefit**: 3-step workflow becomes 1-step

#### 1.5 Sprint State Query (HIGH PRIORITY)

**Current Pain Point**: No single endpoint to get "is sprint ready to execute?"

**Proposed**:
```
GET /model/sprints/{sprint_id}/readiness
Returns: {
  "sprint_id": "51-ACA-sprint-02",
  "ready": true,
  "gates": {
    "stories_defined": {"pass": true, "count": 15},
    "ado_work_items_exist": {"pass": true, "count": 15},
    "ado_sprint_assigned": {"pass": true, "count": 15, "iteration": "51-aca\\Sprint 2"},
    "files_writable": {"pass": true},
    "tests_baseline": {"pass": true, "test_count": 24}
  },
  "blockers": []
}
```

**Benefit**: Replace custom verification scripts with API call

#### 1.6 Commit Workflow Enhancement (MEDIUM PRIORITY)

**Current Pain Point**: `POST /model/admin/commit` returns generic status. On ACA (cloud), you must manually interpret `assemble.stderr` errors.

**Proposed**: Return structured validation results:
```
POST /model/admin/commit
Returns: {
  "status": "PASS",
  "violation_count": 0,
  "exported_total": 962,
  "violations": [],
  "warnings": [
    {"layer": "endpoints", "id": "POST /v1/chat", "field": "auth", "message": "No auth roles defined"}
  ],
  "commit_hash": "abc123",
  "export_location": "model/*.json"
}
```

**Benefit**: Clear validation feedback, no need to parse stderr

#### 1.7 Cross-Service Health Check (MEDIUM PRIORITY)

**Current Pain Point**: Each service (data model, veritas, control plane) has separate health endpoints. No unified status.

**Proposed**:
```
GET /model/ecosystem/health
Returns: {
  "data_model": {"status": "healthy", "store": "cosmos", "version": "2.5"},
  "veritas": {"status": "healthy", "port": 8030, "mcp_active": true},
  "control_plane": {"status": "degraded", "port": 8020, "last_seen": "2026-02-28T12:00:00Z"},
  "ado": {"status": "healthy", "pat_configured": true, "organization": "marcopresta"}
}
```

**Benefit**: Single endpoint for orchestration health checks

---

## 2. Veritas MCP Improvements (48-eva-veritas)

### Current State
- MCP server on port 8030 (stdio transport in VS Code)
- Tools: `audit_repo`, `get_trust_score`, `get_coverage`, `generate_ado_items`, `scan_portfolio`, `model_audit`
- Trust scoring via MTI (Model-Traceability Index)
- Not integrated into sprint workflow

### Proposed Improvements

#### 2.1 Sprint Readiness Gate (HIGH PRIORITY)

**Current Paint Point**: Trust scores exist but aren't used in verification gates. Sprint can execute with low trust scores.

**Proposed**: New tool `verify_sprint_readiness`
```json
{
  "name": "verify_sprint_readiness",
  "input": {
    "repo_path": "C:\\AICOE\\eva-foundry\\51-ACA",
    "sprint_id": "51-ACA-sprint-02",
    "min_trust_score": 0.7
  },
  "output": {
    "ready": true,
    "trust_score": 0.85,
    "gates": {
      "stories_traceable": {"pass": true, "count": 15},
      "acceptance_criteria_complete": {"pass": true, "count": 15},
      "plan_consistency": {"pass": true, "score": 0.92},
      "trust_threshold": {"pass": true, "score": 0.85, "min": 0.7}
    },
    "blockers": []
  }
}
```

**Integration**: Sprint verification scripts call this before ADO sync

#### 2.2 Real-Time Story Validation (HIGH PRIORITY)

**Current Pain Point**: Stories are created in data model without requirements validation. Veritas runs audit post-facto.

**Proposed**: New tool `validate_story_before_commit`
```json
{
  "name": "validate_story_before_commit",
  "input": {
    "repo_path": "C:\\AICOE\\eva-foundry\\51-ACA",
    "story": {
      "id": "ACA-04-001",
      "title": "GET /v1/findings endpoint",
      "acceptance": ["Returns paginated findings list"],
      "implementation_notes": "Use FastAPI + Cosmos"
    }
  },
  "output": {
    "valid": true,
    "issues": [],
    "suggestions": [
      "Add auth requirement to acceptance criteria",
      "Specify pagination limit in acceptance"
    ],
    "trust_impact": 0.02
  }
}
```

**Benefit**: Catch gaps before sprint execution

#### 2.3 ADO Work Item Trust Scores (MEDIUM PRIORITY)

**Current Pain Point**: ADO work items don't show trust scores. Project managers can't see which items have weak requirements.

**Proposed**: New tool `enrich_ado_items_with_trust`
```json
{
  "name": "enrich_ado_items_with_trust",
  "input": {
    "repo_path": "C:\\AICOE\\eva-foundry\\51-ACA",
    "ado_ids": [2978, 2979, 2980]
  },
  "output": {
    "enriched_count": 3,
    "items": [
      {
        "ado_id": 2978,
        "story_id": "ACA-03-001",
        "trust_score": 0.9,
        "has_acceptance": true,
        "has_evidence": false,
        "gaps": []
      }
    ]
  }
}
```

**Benefit**: Trust visibility in ADO board (could update work item tags/fields)

#### 2.4 Portfolio Sprint Health Dashboard (LOW PRIORITY)

**Current Pain Point**: `scan_portfolio` returns per-project MTI but doesn't aggregate sprint readiness across portfolio.

**Proposed**: Enhance `scan_portfolio` output
```json
{
  "portfolio_root": "C:\\AICOE\\eva-foundry",
  "portfolio_mti": 0.78,
  "sprint_readiness": {
    "51-ACA-sprint-02": {"ready": true, "mti": 0.85, "project": "51-ACA"},
    "33-brain-sprint-05": {"ready": false, "mti": 0.65, "project": "33-eva-brain-v2", "blockers": ["missing acceptance criteria"]}
  },
  "at_risk_projects": ["33-eva-brain-v2"],
  "ready_to_execute": ["51-ACA"]
}
```

**Benefit**: Portfolio-level sprint planning visibility

#### 2.5 Auto-Fix Suggestions (MEDIUM PRIORITY)

**Current Pain Point**: Veritas reports gaps but doesn't suggest fixes.

**Proposed**: Add `fix_plan` to audit output
```json
{
  "gaps": [
    {
      "type": "missing_acceptance",
      "story_id": "ACA-04-001",
      "fix_plan": {
        "action": "add_acceptance_criteria",
        "suggested_text": [
          "Returns 200 with findings array",
          "Supports pagination via skip/limit query params",
          "Returns 401 if not authenticated"
        ],
        "confidence": 0.8
      }
    }
  ]
}
```

**Benefit**: Faster gap resolution, agent-friendly format

---

## 3. ADO Integration Improvements

### Current State
- Direct `az boards` CLI calls with PAT token
- No unified ADO service in data model
- Custom scripts for sprint assignment (sync-ado-sprint2-improved.ps1)
- Verification requires separate tool (`sprint2-verify.ps1`)

### Proposed Improvements

#### 3.1 ADO Proxy Service (HIGH PRIORITY)

**Design**: Add ADO layer to data model API

**Endpoints**:
```
# Get work item
GET /model/ado/work-items/{ado_id}

# Update work item state
PATCH /model/ado/work-items/{ado_id}
Body: {"state": "Done", "comment": "Completed by sprint agent"}

# Bulk sprint assignment
POST /model/ado/sprints/{sprint_id}/assign
Body: {
  "iteration": "51-aca\\Sprint 2",
  "work_item_ids": [2978, 2979, 2980]
}

# Query sprint state
GET /model/ado/sprints/{iteration}
Returns: {
  "iteration": "51-aca\\Sprint 2",
  "work_items": [
    {"id": 2978, "state": "Active", "story_id": "ACA-03-001"},
    {"id": 2979, "state": "Done", "story_id": "ACA-03-002"}
  ],
  "completion": "13%"
}
```

**Benefit**: Replace all `az boards` calls with HTTP API

#### 3.2 Unified Sprint Sync Command (HIGH PRIORITY)

**Current Pain Point**: Sprint setup requires:
1. Seed data model with stories
2. Create ADO work items (if not exist)
3. Run `sync-ado-sprint2-improved.ps1`
4. Run `sprint2-verify.ps1`

**Proposed**: Single orchestration endpoint
```
POST /model/sprints/{sprint_id}/sync-ado
Body: {
  "iteration": "51-aca\\Sprint 3",
  "create_work_items_if_missing": true,
  "verify": true
}

Returns: {
  "status": "success",
  "stories_synced": 15,
  "work_items_created": 0,
  "work_items_updated": 15,
  "verification": {
    "gate_1_db_linkage": "PASS",
    "gate_2_ado_assignment": "PASS",
    "gate_3_tests": "PASS"
  }
}
```

**Benefit**: One command, guaranteed consistency

#### 3.3 PAT Token Management (HIGH PRIORITY)

**Current Pain Point**: PAT token must be:
1. Created manually in ADO portal
2. Set as environment variable `AZURE_DEVOPS_EXT_PAT`
3. Configured persistently for new sessions
4. Scripts spawned with `-NoProfile` don't inherit token

**Proposed**: Centralized credential store
```
POST /model/admin/config/credentials
Body: {
  "service": "ado",
  "credential_type": "pat",
  "value": "***",
  "organization": "https://dev.azure.com/marcopresta",
  "scope": ["work_items_read", "work_items_write"]
}

GET /model/admin/config/credentials/ado
Returns: {
  "configured": true,
  "organization": "https://dev.azure.com/marcopresta",
  "expires_at": "2026-03-28",
  "scopes": ["work_items_read", "work_items_write"]
}
```

**Security**: Store encrypted in Cosmos, decrypt server-side, never expose token in API responses

**Benefit**: Scripts don't need environment variable management

#### 3.4 Sprint Agent Callback Integration (MEDIUM PRIORITY)

**Current Pain Point**: Sprint Agent workflow commits stories but doesn't update ADO state. Manual step to mark work items "Done".

**Proposed**: Workflow callback endpoint
```
POST /model/ado/work-items/{ado_id}/complete
Body: {
  "commit_sha": "8113b32",
  "story_id": "ACA-03-016",
  "completion_evidence": {
    "files_written": ["services/collector/app/resource_graph.py"],
    "tests_passed": true,
    "lint_status": "WARN"
  }
}

(Automatically sets ADO state to "Done", adds comment with completion evidence)
```

**Integration**: Sprint Agent calls this after each story completes

**Benefit**: Zero-touch ADO state management

#### 3.5 ADO Field Mapping (LOW PRIORITY)

**Current Pain Point**: Data model story schema doesn't map to ADO fields. Custom code needed to translate.

**Proposed**: Configuration endpoint
```
POST /model/admin/config/ado-field-mapping
Body: {
  "story_id": "System.Tags",
  "title": "System.Title",
  "acceptance": "Microsoft.VSTS.Common.AcceptanceCriteria",
  "implementation_notes": "System.Description",
  "ado_id": "System.Id",
  "state": "System.State"
}

GET /model/stories/ACA-03-001?format=ado
Returns: ADO-compatible work item JSON
```

**Benefit**: Automatic schema translation

---

## 4. Cross-Service Integration Patterns

### 4.1 Unified Sprint Launch Workflow (HIGH PRIORITY)

**Goal**: Single command to go from PLAN.md to running Sprint Agent

**Proposed CLI**:
```powershell
# In 51-ACA project
pwsh -File $env:EVA_FOUNDATION/scripts/launch-sprint.ps1 `
  -SprintId "51-ACA-sprint-03" `
  -Epic "epic-04" `
  -Iteration "51-aca\Sprint 3"

# Executes:
# 1. Parse PLAN.md Epic 4 stories
# 2. POST /model/sprints/ (seed data model)
# 3. POST /model/ado/sprints/.../assign (sync ADO work items)
# 4. Invoke veritas:verify_sprint_readiness
# 5. If ready: create GitHub issue with SPRINT_MANIFEST
# 6. Monitor workflow execution
# 7. Return: GitHub Actions URL + ADO board URL
```

**Benefit**: Sprint launch time: 30 minutes -> 2 minutes

### 4.2 Unified Verification Gate (HIGH PRIORITY)

**Goal**: Single source of truth for "is sprint ready?"

**Proposed**: Multi-service aggregator
```
GET /model/sprints/{sprint_id}/gates
(Queries data model + veritas + ADO + runs tests)

Returns: {
  "sprint_id": "51-ACA-sprint-03",
  "ready": true,
  "gates": {
    "db_linkage": {"pass": true, "service": "data-model", "details": {...}},
    "ado_assignment": {"pass": true, "service": "ado-proxy", "details": {...}},
    "trust_score": {"pass": true, "service": "veritas", "score": 0.85},
    "baseline_tests": {"pass": true, "service": "pytest", "count": 24}
  }
}
```

**Benefit**: Replace 3 separate verification scripts with 1 API call

### 4.3 Event-Driven State Sync (MEDIUM PRIORITY)

**Goal**: Auto-sync state changes across services

**Design**: Webhook/event bus pattern
```
# When Sprint Agent completes story
1. Sprint Agent commits code -> webhook to Control Plane
2. Control Plane -> POST /model/stories/{id}/complete
3. Data Model -> emits event "story.completed"
4. ADO Proxy subscribes -> PATCH /model/ado/work-items/{id} (state=Done)
5. Veritas subscribes -> updates trust score cache
```

**Benefit**: Zero-latency state consistency

### 4.4 Federated Query API (MEDIUM PRIORITY)

**Goal**: Query across all services in one call

**Proposed**:
```
POST /model/query/federated
Body: {
  "query": {
    "sprint_id": "51-ACA-sprint-03",
    "include": ["stories", "ado_state", "trust_scores", "completion_evidence"]
  }
}

Returns: {
  "stories": [
    {
      "id": "ACA-04-001",
      "status": "implemented",
      "ado_state": "Done",
      "trust_score": 0.9,
      "evidence": {
        "commit": "abc123",
        "tests_passed": true
      }
    }
  ]
}
```

**Benefit**: Dashboard/reporting without N service calls

### 4.5 Service Dependency Graph (LOW PRIORITY)

**Goal**: Visualize service integration

**Proposed**:
```
GET /model/ecosystem/dependencies
Returns: {
  "services": [
    {"name": "data-model", "port": 8010, "deps": ["cosmos", "veritas"]},
    {"name": "veritas", "port": 8030, "deps": ["data-model"]},
    {"name": "ado-proxy", "port": null, "deps": ["data-model", "azure-devops"]},
    {"name": "control-plane", "port": 8020, "deps": ["data-model"]}
  ],
  "graph_url": "/model/ecosystem/dependencies/graph.svg"
}
```

**Benefit**: Debugging integration issues

---

## 5. Implementation Priority Matrix

### Phase 1 (Immediate -- Next Sprint)

**Critical Path**:
1. Data Model: Sprint management endpoints (`POST /model/sprints/`)
2. Data Model: ADO integration layer (`/model/ado/work-items/`)
3. ADO: PAT token centralized credential store
4. ADO: Unified sprint sync command
5. Veritas: Sprint readiness gate tool

**Benefit**: Sprint 3 launch with 80% less manual scripting

### Phase 2 (1-2 Weeks)

**Workflow Enhancement**:
6. Data Model: Batch operations endpoint
7. Data Model: Smart PUT/PATCH simplification
8. Veritas: Real-time story validation
9. ADO: Sprint Agent callback integration
10. Cross-service: Unified sprint launch workflow

**Benefit**: Zero-touch sprint execution

### Phase 3 (1 Month)

**Advanced Features**:
11. Data Model: Sprint state readiness query
12. Data Model: Cross-service health check
13. Veritas: ADO work item trust scores
14. ADO: Field mapping configuration
15. Cross-service: Unified verification gate API

**Benefit**: Production-grade observability

### Phase 4 (2+ Months)

**Ecosystem Maturity**:
16. Data Model: Commit workflow enhanced validation
17. Veritas: Portfolio sprint health dashboard
18. Veritas: Auto-fix suggestions
19. Cross-service: Event-driven state sync
20. Cross-service: Federated query API
21. Cross-service: Service dependency graph

**Benefit**: Enterprise-scale multi-project orchestration

---

## 6. Success Metrics

### Developer Experience

**Current State**:
- Sprint setup: 15+ manual steps, 30-45 minutes
- Verification: 3 separate scripts, must manually correlate results
- ADO sync: Custom PowerShell script, PAT token env var dance

**Target State (Phase 1)**:
- Sprint setup: 1 command, 2 minutes
- Verification: 1 API call, instant results
- ADO sync: Automatic via data model proxy

### Reliability

**Current State**:
- Sprint verification: 3 gates, manual execution, PAT token failures
- ADO sync: 100% success rate after fixing auth (this session)
- Cross-service consistency: Unknown (no unified health check)

**Target State (Phase 2)**:
- Sprint verification: 100% automated, pre-flight checks
- ADO sync: 100% success rate, automatic retry on transient failures
- Cross-service consistency: Real-time dashboard, <1 second staleness

### Traceability

**Current State**:
- Trust scores exist but not integrated into workflow gates
- ADO work items lack trust score visibility
- No automatic gap detection before sprint launch

**Target State (Phase 3)**:
- Trust scores gate sprint execution (min threshold)
- ADO board shows trust scores per work item
- Automatic gap detection with fix suggestions

---

## 7. Breaking Changes and Migration

### Data Model

**Breaking**:
- None (all additions are backwards-compatible endpoints)

**Migration**:
- Existing scripts continue to work
- New scripts use enhanced endpoints
- Gradual migration over Sprint 3-4

### Veritas

**Breaking**:
- None (new tools added, existing tools unchanged)

**Migration**:
- Existing `audit_repo` calls continue to work
- New `verify_sprint_readiness` opt-in

### ADO Integration

**Breaking**:
- PAT token from environment variable -> credential store (optional migration)

**Migration**:
- Phase 1: Support both env var and credential store
- Phase 2: Deprecate env var (warning in logs)
- Phase 3: Remove env var support (6+ months)

---

## 8. Open Questions

1. **Data Model hosting**: Should ADO proxy run in same ACA as data-model, or separate service?
2. **Credential encryption**: Use Azure Key Vault or Cosmos encrypted fields for PAT storage?
3. **Event bus**: Use Azure Event Grid, Service Bus, or custom HTTP webhooks?
4. **Veritas MCP protocol**: Keep stdio transport or add HTTP for cross-service calls?
5. **Rate limiting**: What's ADO API rate limit? Need caching layer?
6. **Multi-tenancy**: Single PAT per organization or per-user PAT delegation?
7. **Audit trail**: Where to log ADO state changes? Control Plane or Data Model?
8. **Error recovery**: What happens if ADO PATCH fails mid-sprint? Retry policy?

---

## 9. Next Steps

### Immediate (This Session)
- [x] Document improvement plan
- [ ] Create GitHub issue for Phase 1 implementation
- [ ] Update 37-data-model PLAN.md with ADO layer design
- [ ] Update 48-eva-veritas roadmap with sprint readiness gate

### Sprint 3 Preparation
- [ ] Implement Phase 1 critical path (5 items above)
- [ ] Test unified sprint launch workflow
- [ ] Verify Sprint 3 can launch with new endpoints
- [ ] Document migration guide for existing scripts

### Long Term
- [ ] Evangelize integrated workflow to other EVA projects (33, 31, 38, 44)
- [ ] Extract common patterns into 07-foundation-layer templates
- [ ] Create reference implementation in 51-ACA for other projects

---

**Document Owner**: 51-ACA project (Azure Cost Advisor)
**Review Cadence**: Weekly during Phase 1, bi-weekly Phase 2+
**Feedback Channel**: GitHub Discussions in 51-ACA repo
