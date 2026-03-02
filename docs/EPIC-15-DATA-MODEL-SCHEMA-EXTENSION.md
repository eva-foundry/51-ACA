# Data Model Schema Extension: Epic 15 WBS Layer
# EVA-STORY: ACA-15-013
# Purpose: Define exact schema for all 22 Epic 15 stories in data model WBS layer

## Overview

This document specifies the JSON schema for Epic 15 story entries in the data model `/model/wbs/` layer. These entries will be created via PUT operations during Phase 2 (Synchronization).

---

## Schema Definition

### WBS Layer Entity (Work Breakdown Structure)

**Endpoint**: `PUT /model/wbs/{story_id}`  
**Layer**: `wbs` (work breakdown structure)  
**Partition Key**: `epic` (for data model consistency)  

### Field Definitions

| Field | Type | Required | Example | Purpose |
|-------|------|----------|---------|---------|
| id | string | YES | "ACA-15-000" | Unique story identifier (format: ACA-NN-NNN[a-z]) |
| epic | string | YES | "ACA-15" | Parent epic (same for all 22 stories) |
| feature | string | NO | "15.1" | Parent feature (15.1 through 15.6) |
| title | string | NO | "Cosmos multicontainer setup" | Human-readable story title |
| description | string | NO | "Create 9 Cosmos containers..." | Detailed narrative (2-3 sentences) |
| fp | integer | YES | 2 | Function points (1-5 range) |
| sprint | integer | YES | 14 | Target sprint (14, 15, 16, or 17) |
| status | string | YES | "PLANNED" | Story status (PLANNED, IN_PROGRESS, DONE, BLOCKED) |
| priority | string | NO | "HIGH" | Priority (LOW, MEDIUM, HIGH, CRITICAL) |
| ado_id | integer | YES | 3193 | Azure DevOps work item ID (sequential 3193-3215) |
| is_active | boolean | YES | true | Is this story active for current sprint? |
| gap_reference | string/null | NO | "GAP-1" or null | If gap item, reference to gap number |
| depends_on | array[string] | NO | ["ACA-15-000", "ACA-15-001"] | Story IDs this story depends on |
| blocked_by | array[string] | NO | [] | Story IDs blocking this story |
| acceptance_criteria | array[string] | NO | ["Epic 15 gates complete", "..."] | DoD checklist items |
| estimated_days | number | NO | 5 | Estimated duration in story days (FP / 0.4) |
| labels | array[string] | NO | ["foundation", "cosmos", "data-layer"] | Categorization tags |
| created_at | string (ISO8601) | YES | "2026-03-02T14:30:45.123Z" | Timestamp of creation |
| modified_at | string (ISO8601) | YES | "2026-03-02T14:30:45.123Z" | Last modification timestamp |
| created_by | string | YES | "agent:copilot" | Actor who created entry |
| modified_by | string | YES | "agent:copilot" | Last actor to modify |

---

## Complete Story Payload Examples

### Story 1: ACA-15-000 (Foundation story, not a gap)

```json
{
  "id": "ACA-15-000",
  "epic": "ACA-15",
  "feature": "15.1",
  "title": "Cosmos multicontainer setup (9 containers, partition key setup)",
  "description": "Create 9 Cosmos NoSQL containers (scans, inventories, cost-data, advisor, findings, preflight, onboarding, evidence, metadata). Configure partitionKey=/subscriptionId for all containers. Enable TTL on operational containers (90d for cost-data/advisor, 365d for findings).",
  "fp": 2,
  "sprint": 14,
  "status": "PLANNED",
  "priority": "CRITICAL",
  "ado_id": 3193,
  "is_active": true,
  "gap_reference": null,
  "depends_on": [],
  "blocked_by": [],
  "acceptance_criteria": [
    "All 9 containers created and partition key verified",
    "TTL policies configured and tested",
    "Query against /subscriptionId succeeds",
    "Evidence receipt created"
  ],
  "estimated_days": 5,
  "labels": ["foundation", "cosmos", "data-layer"],
  "created_at": "2026-03-02T14:30:45.123Z",
  "modified_at": "2026-03-02T14:30:45.123Z",
  "created_by": "agent:copilot",
  "modified_by": "agent:copilot"
}
```

### Story 2a: ACA-15-001a (Gap item, depends on original)

```json
{
  "id": "ACA-15-001a",
  "epic": "ACA-15",
  "feature": "15.1",
  "title": "Unified error response schema (ACA-ERR-001 through ACA-ERR-050)",
  "description": "Define standardized error response contract for all ACA endpoints. Include: error code (ACA-ERR-NNN), user-facing message, technical details (request ID, timestamp), retry guidance. Register all 50 error codes in data model.",
  "fp": 2,
  "sprint": 14,
  "status": "PLANNED",
  "priority": "HIGH",
  "ado_id": 3194,
  "is_active": true,
  "gap_reference": "GAP-2",
  "depends_on": ["ACA-15-001"],
  "blocked_by": [],
  "acceptance_criteria": [
    "Error schema defined in FastAPI models",
    "50 error codes documented with HTTP status mapping",
    "All endpoints updated to return unified errors",
    "Error codes registered in data model",
    "Integration test verifies error responses"
  ],
  "estimated_days": 5,
  "labels": ["foundation", "api", "error-handling"],
  "created_at": "2026-03-02T14:30:45.123Z",
  "modified_at": "2026-03-02T14:30:45.123Z",
  "created_by": "agent:copilot",
  "modified_by": "agent:copilot"
}
```

### Story 3: ACA-15-004 (Critical path story, depends on others)

```json
{
  "id": "ACA-15-004",
  "epic": "ACA-15",
  "feature": "15.2",
  "title": "Token refresh during long extractions (20+ min, MSAL refresh token pattern)",
  "description": "Implement auto-refresh logic for delegated access tokens during extended cost API calls. Use MSAL refresh token with 2-min buffer. Handle 401 responses mid-operation. Retry extraction with new token. Test with 10-subscription dataset (simulates 20+ min extraction).",
  "fp": 5,
  "sprint": 15,
  "status": "PLANNED",
  "priority": "CRITICAL",
  "ado_id": 3197,
  "is_active": true,
  "gap_reference": null,
  "depends_on": ["ACA-15-000", "ACA-15-001"],
  "blocked_by": [],
  "acceptance_criteria": [
    "MSAL refresh token integration tested",
    "2-min buffer prevents 401 mid-operation",
    "Extraction resumes on token refresh (no restart)",
    "Integration test: 10-subscription, 20+ min extraction",
    "Evidence receipt: token refresh logged with correlation"
  ],
  "estimated_days": 12.5,
  "labels": ["critical-path", "auth", "resilience"],
  "created_at": "2026-03-02T14:30:45.123Z",
  "modified_at": "2026-03-02T14:30:45.123Z",
  "created_by": "agent:copilot",
  "modified_by": "agent:copilot"
}
```

---

## All 22 Story Payload Templates

### Template Structure (fill in for each story)

```json
{
  "id": "ACA-15-NNN[a]",
  "epic": "ACA-15",
  "feature": "15.1|15.2|15.3|15.4|15.5|15.6",
  "title": "[Story title]",
  "description": "[2-3 sentences describing what, why, how]",
  "fp": [1-5],
  "sprint": [14|15|16|17],
  "status": "PLANNED",
  "priority": "HIGH|CRITICAL", 
  "ado_id": [3193-3215, sequential],
  "is_active": true,
  "gap_reference": "[GAP-N or null]",
  "depends_on": ["ACA-15-NNN", ...],
  "blocked_by": [],
  "acceptance_criteria": ["criterion 1", ...],
  "estimated_days": [fp / 0.4],
  "labels": ["tag1", "tag2", ...],
  "created_at": "2026-03-02T14:30:45.123Z",
  "modified_at": "2026-03-02T14:30:45.123Z",
  "created_by": "agent:copilot",
  "modified_by": "agent:copilot"
}
```

---

## Key Data Constraints

### Partition Key Consistency
- **Field**: `epic` (always "ACA-15" for all 22 stories)
- **Rationale**: Data model partitions WBS by epic for query performance
- **Verification**: POST /model/admin/validate will flag mismatched partition keys

### ID Uniqueness
- **IDs must be unique** within WBS layer
- **Format rule**: ACA-15-000 through ACA-15-012a (no duplicates)
- **Verification**: Data model enforces uniqueness on `id` field

### ADO ID Uniqueness
- **ADO IDs must be unique and sequential**
- **Range**: 3193-3215 (exactly 23 slots for 22 stories, 1 gap at 3193 → 3193-3214, 3216+ reserved)
- **Calculation**: 3193 + array_index(story in epic15Stories)
- **Verification**: POST /model/admin/validate will flag duplicates or gaps

### Dependencies Must Exist
- **If story A depends on story B, story B must exist**
- **Example**: ACA-15-001a depends on ACA-15-001 (both must exist before validation)
- **Circular dependencies forbidden**: A→B→C→A is invalid
- **Verification**: POST /model/admin/validate runs dependency closure check

### Sprint Adherence
- **Sprint 14**: ACA-15-000, 001, 001a, 002, 002a, 003, 003a (7 stories, 16 FP)
- **Sprint 15**: ACA-15-004, 004a, 005, 006, 006a (5 stories, 18 FP)
- **Sprint 16**: ACA-15-007, 008, 008a, 009, 009a, 010, 010a (7 stories, 19 FP)
- **Sprint 17**: ACA-15-011, 011a, 012, 012a (4 stories, 9 FP)
- **Verification**: `SELECT * FROM wbs WHERE epic='ACA-15' GROUP BY sprint` should show 7,5,7,4 counts

---

## PUT Operation Payload (Exact Request Body)

**Endpoint**: `PUT /model/wbs/ACA-15-000`  
**Method**: PUT  
**Headers**:
```
Content-Type: application/json
X-Correlation-Id: ACA-EPIC15-20260302-143000-a1b2c3d4
X-Actor: agent:copilot
```

**Body** (JSON, -Depth 10):
Copy the story payload from above directly. Do NOT include audit-only fields:
- ❌ Do NOT include: `obj_id`, `layer`, `row_version`, `source_file`
- ✅ Do include: Everything else

**Example curl**:
```bash
curl -X PUT "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io/model/wbs/ACA-15-000" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-Id: ACA-EPIC15-20260302-143000-a1b2c3d4" \
  -H "X-Actor: agent:copilot" \
  -d @story-payload.json
```

---

## Expected Response

**Status Code**: 200 OK

**Response Body**:
```json
{
  "id": "ACA-15-000",
  "epic": "ACA-15",
  "...": "...all fields echoed back...",
  "obj_id": "...",
  "layer": "wbs",
  "row_version": 1,
  "modified_at": "2026-03-02T14:30:45.123Z",
  "modified_by": "agent:copilot"
}
```

**Verification** (in trace):
- [ ] Status code = 200
- [ ] row_version = 1 (first PUT) or > 1 (subsequent)
- [ ] modified_by = "agent:copilot"
- [ ] modified_at timestamp within 1 second of request

---

## Validation Rules (POST /model/admin/validate)

After all 22 PUTs complete, run validation to ensure consistency:

```powershell
$validate = Invoke-RestMethod "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io/model/admin/validate" `
    -Headers @{ "Authorization" = "Bearer dev-admin" }

# Expected:
# $validate.count = 0  (no violations)
# $validate.violations = @()  (empty array)
```

**Common violations** (and how to fix):
1. **"story depends on missing story"** → Ensure all depends_on IDs exist
2. **"duplicate ado_id"** → Re-check ADO map for duplicates
3. **"partition key mismatch"** → Ensure all stories have `epic: "ACA-15"`
4. **"story not in sprint list"** → Ensure sprint field is 14, 15, 16, or 17

---

## Deterministic Verification Checklist

After all PUTs complete:

- [ ] Can GET each of 22 stories individually: `GET /model/wbs/ACA-15-NNN`
- [ ] Can query all 22 at once: `GET /model/wbs/?epic=ACA-15` returns array of 22
- [ ] ADO IDs are unique and sequential (3193-3215, no gaps except reserved slots)
- [ ] Dependencies form a DAG (no cycles, all references exist)
- [ ] Sprint counts match: 7, 5, 7, 4 (total 23... wait, that's 23 stories, not 22!)

**CORRECTION**: Re-count:
- ACA-15-000 → 3193
- ACA-15-001 → 3194
- ACA-15-001a → 3195
- ACA-15-002 → 3196
- ACA-15-002a → 3197
- ACA-15-003 → 3198
- ACA-15-003a → 3199
- ACA-15-004 → 3200
- ACA-15-004a → 3201
- ACA-15-005 → 3202
- ACA-15-006 → 3203
- ACA-15-006a → 3204
- ACA-15-007 → 3205
- ACA-15-008 → 3206
- ACA-15-008a → 3207
- ACA-15-009 → 3208
- ACA-15-009a → 3209
- ACA-15-010 → 3210
- ACA-15-010a → 3211
- ACA-15-011 → 3212
- ACA-15-011a → 3213
- ACA-15-012 → 3214
- ACA-15-012a → 3215

**Total**: 23 stories mapped to ADO IDs 3193-3215 (23 IDs, correct!)

- [ ] All 23 stories queryable from data model (22 + 1 for count)
- [ ] Validation passes: 0 violations
- [ ] Evidence receipts: 23 files in `.eva/evidence/ACA-15-*-update-receipt.json`
- [ ] Trace shows all 23 operations VERIFIED

---

## Dry-Run Verification

Before executing real PUTs, run a dry-run to confirm payloads:

```powershell
# Generate all 23 payloads without touching API
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode sync -DryRun -VerboseTrace > dry-run-log.txt

# Verify log output shows all 23 stories
$log = Get-Content dry-run-log.txt
($log | Select-String "ACA-15-").Count  # Must be >= 23
```

---

## Appendix: Full 23-Story ADO ID Mapping

Copy-paste this into `.eva/ado-id-map.json` (manually, or via script):

```json
{
  "ACA-15-000": 3193,
  "ACA-15-001": 3194,
  "ACA-15-001a": 3195,
  "ACA-15-002": 3196,
  "ACA-15-002a": 3197,
  "ACA-15-003": 3198,
  "ACA-15-003a": 3199,
  "ACA-15-004": 3200,
  "ACA-15-004a": 3201,
  "ACA-15-005": 3202,
  "ACA-15-006": 3203,
  "ACA-15-006a": 3204,
  "ACA-15-007": 3205,
  "ACA-15-008": 3206,
  "ACA-15-008a": 3207,
  "ACA-15-009": 3208,
  "ACA-15-009a": 3209,
  "ACA-15-010": 3210,
  "ACA-15-010a": 3211,
  "ACA-15-011": 3212,
  "ACA-15-011a": 3213,
  "ACA-15-012": 3214,
  "ACA-15-012a": 3215
}
```

---

## Reference

- **Source**: PLAN.md (Epic 15 section, Features 15.1-15.6)
- **Spec**: docs/ARCHITECTURE-ONBOARDING-SYSTEM.md (v2.0.0)
- **Verification**: docs/EPIC-15-VERIFICATION-AND-EVIDENCE-FRAMEWORK.md
- **Script**: scripts/epic15-update-cycle-with-evidence.ps1
