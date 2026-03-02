# Epic 15 Data Model Synchronization: Verification Checklist & Evidence Framework
# EVA-STORY: ACA-15-013

## Executive Summary

This document specifies the complete verification and evidence collection framework for Epic 15 data model synchronization. **Mandatory principle: Nothing left unsurveilled.** Every operation is traced, stamped, and verified with immutable evidence.

---

## 1. Verification Framework: Pre-, During, and Post-Audit Gates

### Pre-Audit Gates (G-gates: G01-G04)

These gates verify the system is in a known, correct state BEFORE any changes.

#### G01: Data Model Reachability
- **What**: Health check on data model API endpoint
- **How**: `GET /health` with 5-second timeout
- **Expected**: `status: ok` + `store: cosmos`
- **Evidence**: Response timestamp, latency (ms), version
- **Failure Mode**: Cannot proceed. Root cause: Network, API down, credential issue
- **Recovery**: Restart data-model service (port 8010) or verify network connectivity

#### G02: PLAN.md Contains 22 Epic 15 Stories
- **What**: Verify source file has all story IDs before sync
- **How**: Regex search: `ACA-15-\d+` (count must = 22)
- **Expected**: 22 exact matches across file
- **Evidence**: Story IDs found, match timestamps
- **Failure Mode**: Source document incomplete. Root cause: Stories not added to PLAN.md
- **Recovery**: Re-run `seed-from-plan.py --reseed-model` from PLAN.md

#### G03: ADO ID Map Exists and Readable
- **What**: Verify configuration file is present and valid JSON
- **How**: File exists? Parse as JSON? Read succeeds?
- **Expected**: Valid JSON, parseable, last entry readable
- **Evidence**: File path, size (bytes), parse success, last entry ID
- **Failure Mode**: Configuration missing or corrupted. Root cause: File deleted or truncated
- **Recovery**: Restore `.eva/ado-id-map.json` from git history or previous backup

#### G04: No Epic 15 in ADO Map Yet (Idempotency Check)
- **What**: Verify no duplicate entries if re-running
- **How**: Grep ADO map for `ACA-15-\d+`
- **Expected**: 0 matches (clean slate) OR > 0 matches (safe to skip updates)
- **Evidence**: Count of Epic 15 entries found, idempotency decision
- **Failure Mode**: Partial updates detected. Root cause: Previous run incomplete
- **Recovery**: Complete or rollback the previous attempt

---

### During-Sync Instrumentation

Every operation is traced with correlation ID, timestamp, and request/response fingerprints.

#### Operation Type 1: PUT to Data Model `/wbs/{story_id}` Endpoint

**Tracing Fields**:
```json
{
  "sequence_number": 1,
  "phase": "PHASE-2",
  "operation": "ACA-15-000-PUT-WBS",
  "status": "CALL|RESPONSE|VERIFIED|FAILED",
  "timestamp": "2026-03-02T14:30:45.123Z",
  "correlation_id": "ACA-EPIC15-20260302-143000-a1b2c3d4",
  "request": {
    "method": "PUT",
    "url": "/model/wbs/ACA-15-000",
    "payload_hash": "sha256:...",
    "headers": {
      "X-Correlation-Id": "ACA-EPIC15-20260302-143000-a1b2c3d4",
      "X-Actor": "agent:copilot"
    }
  },
  "response": {
    "status_code": 200,
    "row_version": 1,
    "modified_at": "2026-03-02T14:30:45.123Z",
    "modified_by": "agent:copilot"
  }
}
```

**Assertions to Verify**:
- [ ] Status code = 200 (success)
- [ ] row_version incremented (0 → 1, or 1 → 2 on re-run)
- [ ] modified_by = "agent:copilot" (correct actor)
- [ ] modified_at matches request timestamp (+/- 1 second)
- [ ] id returned matches request ID (no corruption)

#### Operation Type 2: Update ADO ID Map

**Tracing Fields**:
```json
{
  "sequence_number": 2,
  "phase": "PHASE-2",
  "operation": "ACA-15-000-UPDATE-ADO-MAP",
  "status": "CALL|RESPONSE|VERIFIED|FAILED",
  "timestamp": "2026-03-02T14:30:46.234Z",
  "file_operation": {
    "action": "JSON.add Property",
    "file": ".eva/ado-id-map.json",
    "key": "ACA-15-000",
    "value": 3193,
    "file_hash_before": "sha256:...",
    "file_hash_after": "sha256:..."
  }
}
```

**Assertions to Verify**:
- [ ] File write succeeded (no I/O errors)
- [ ] JSON remains valid (can re-parse)
- [ ] New entry present (can read back)
- [ ] File hash changed (mutation detected)
- [ ] No other entries modified (isolation)

---

### Post-Audit Gates (PA-gates: PA01-PA03)

These gates verify all changes were applied correctly and consistently.

#### PA01: All 22 Epic 15 Stories in ADO Map

**Verification**:
```powershell
$adoMap = Get-Content ".eva/ado-id-map.json" | ConvertFrom-Json
$epic15 = @($adoMap | Get-Member -MemberType NoteProperty | Where-Object { $_.Name -match "ACA-15-\d+" })
$epic15.Count # Must = 22
```

**Evidence**: Count of Epic 15 entries, story IDs present, values in expected range (3193-3215)

#### PA02: ADO IDs Sequential (3193-3215)

**Verification**:
```powershell
$adoIds = @($epic15Entries | ForEach-Object { $adoMap.($_.Name) } | Sort-Object)
$expected = 3193..3215
Compare-Object $adoIds $expected  # Must be empty (no diff)
```

**Evidence**: Actual ID range, any gaps detected, sorting verified

#### PA03: PLAN.md Unchanged (Deterministic)

**Verification**:
```powershell
$planBefore = Get-FileHash "PLAN.md" -Algorithm SHA256
# ... sync operations ...
$planAfter = Get-FileHash "PLAN.md" -Algorithm SHA256
$planBefore -eq $planAfter  # Must be true
```

**Evidence**: SHA256 hashes before/after, file size, line count

---

## 2. Deterministic Behavior Specification

### Principle 1: Idempotency

**Definition**: Running the script twice with identical inputs produces identical outputs (no side effects on second run).

**Verification Steps**:
1. Run: `pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode sync`
2. Verify: All ADO IDs 3193-3215 present
3. Delete ADO map entries for ACA-15-* manually
4. Run: `pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode sync`
5. Verify: Identical ADO IDs assigned, G04 gate shows "already present, will skip"
6. Evidence: Two runs produce identical correlation trace (same checksums, same operation counts)

### Principle 2: Deterministic ID Assignment

**Definition**: Story → ADO ID mapping is deterministic (same story always gets same ADO ID).

**Verification**:
- ACA-15-000 → always 3193
- ACA-15-001 → always 3194
- ... (sequential)
- ACA-15-012a → always 3215

**Math**: `ADO_ID = 3193 + array_index(story_id)`

**Evidence**: Input/output pairs documented in trace, no randomness or time-dependence

### Principle 3: Operator Independence

**Definition**: Output is identical regardless of who runs the script (agent, human, CI/CD).

**Verification**:
- Run by agent: Produces trace T1 with correlation ID C1
- Run by human: same command, produces trace T2 with different correlation ID C2
- Traces T1 and T2 differ ONLY in: correlation_id, timestamp, actor (agent:copilot vs user:...)
- All story IDs, ADO IDs, operation counts, checklist results are IDENTICAL

**Evidence**: Two runs from different actors, side-by-side comparison showing only correlation/actor differ

### Principle 4: Consistency Across Layers

**Definition**: Data model layer, ADO map layer, and PLAN.md layer remain consistent (no orphaned references).

**Verification**:
- For each story in PLAN.md:
  - [ ] Exists in data model `/wbs/{story_id}` (GET succeeds)
  - [ ] Exists in ADO map with valid integer ID
  - [ ] ADO ID is in expected range (3193-3215)
  - [ ] No duplicate IDs across stories

**Evidence**: Cross-reference report showing zero orphans, zero duplicates

---

## 3. Evidence Receipt Schema

Every story update generates an immutable evidence receipt in `.eva/evidence/{story_id}-update-receipt.json`.

### Receipt Structure

```json
{
  "story_id": "ACA-15-000",
  "correlation_id": "ACA-EPIC15-20260302-143000-a1b2c3d4",
  "timestamp": "2026-03-02T14:30:45.123Z",
  "phase": "P",
  "operation": "epic15-data-model-sync",
  "status": "PASS",
  
  "inputs": {
    "sprint_number": 14,
    "function_points": 2,
    "gap_item": null,
    "ado_id_assigned": 3193
  },
  
  "outputs": {
    "data_model_entry": {
      "layer": "wbs",
      "id": "ACA-15-000",
      "status": "PLANNED",
      "row_version": 1
    },
    "ado_map_entry": {
      "story_id": "ACA-15-000",
      "ado_id": 3193
    }
  },
  
  "validation": {
    "pa01_all_in_map": true,
    "pa02_sequential_ids": true,
    "pa03_deterministic": true,
    "pre_audit": true,
    "post_audit": true
  },
  
  "fingerprint": {
    "correlation_id": "ACA-EPIC15-20260302-143000-a1b2c3d4",
    "sha256_payload": "a1b2c3d4e5f6...",
    "signature": "HMAC-SHA256(...)"
  }
}
```

### Immutability Guarantee

Each receipt is write-once-read-many:
1. Generated during Phase 4
2. Written to disk with UTF8 encoding
3. File hash recorded in trace
4. Not modified after creation
5. Can be verified against trace for tampering

---

## 4. Traceability Report Schema

Master trace document: `.eva/traces/epic15-sync-trace-{correlation_id}.json`

### Report Structure

```json
{
  "epic": "ACA-15",
  "title": "Epic 15 Data Model Synchronization Trace",
  "correlation_id": "ACA-EPIC15-20260302-143000-a1b2c3d4",
  "timestamp": "2026-03-02T14:30:45.123Z",
  "mode": "sync|audit|verify|report|full",
  "dry_run": false,
  
  "execution_summary": {
    "total_stories": 22,
    "data_model_operations": 22,
    "ado_map_updates": 22,
    "evidence_receipts_generated": 22,
    "errors": 0,
    "warnings": 0
  },
  
  "audit_gates": {
    "pre_audit_passed": true,
    "post_audit_passed": true
  },
  
  "detailed_phases": [
    {
      "seq": 1,
      "phase": "PHASE-1",
      "operation": "G01-DataModel-Health",
      "status": "VERIFIED",
      "timestamp": "2026-03-02T14:30:45.123Z",
      "data": { "status": "ok", "store": "cosmos" }
    },
    ...
  ],
  
  "errors_and_warnings": {
    "errors": [],
    "warnings": []
  },
  
  "verification_status": {
    "deterministic_behavior": "VERIFIED",
    "idempotency_safe": "VERIFIED",
    "all_operations_traced": "VERIFIED",
    "correlation_tracking": "ENABLED"
  }
}
```

### How to Query the Trace

```powershell
# Load the trace
$trace = Get-Content ".eva/traces/epic15-sync-trace-*.json" | ConvertFrom-Json

# Find all PUT operations
$trace.detailed_phases | Where-Object { $_.operation -match "PUT-WBS" } | Select-Object seq, status, timestamp

# Find all failures
$trace.detailed_phases | Where-Object { $_.status -eq "FAILED" }

# Get summary
$trace.execution_summary
```

---

## 5. Deterministic Behavior Checklist

Use this checklist to ensure the sync is deterministic, auditable, and reproducible.

- [ ] **Pre-execution**: Data model health check passes (G01)
- [ ] **Pre-execution**: PLAN.md has exactly 22 Epic 15 stories (G02)
- [ ] **Pre-execution**: ADO map exists and is valid JSON (G03)
- [ ] **Pre-execution**: No Epic 15 stories already in ADO map (G04)
- [ ] **Sync Phase**: All 22 PUTs to data model complete
- [ ] **Sync Phase**: All 22 ADO map updates complete
- [ ] **Post-sync**: All 22 stories present in ADO map (PA01)
- [ ] **Post-sync**: ADO IDs are sequential 3193-3215 (PA02)
- [ ] **Post-sync**: PLAN.md hash unchanged (PA03)
- [ ] **Evidence**: 22 receipt files generated in `.eva/evidence/`
- [ ] **Trace**: Master trace file generated in `.eva/traces/`
- [ ] **Correlation**: All operations link to same correlation ID
- [ ] **Determinism**: Running script 2x with clean ADO map produces identical results
- [ ] **Consistency**: PLAN.md, data model, and ADO map all agree on 22 stories

---

## 6. Explainability Narrative

For every story update, the trace explains:

1. **Why**: "Adding ACA-15-000 data model entry for Cosmos containers setup task"
2. **What**: Exact payload sent to data model API, exact JSON added to ADO map
3. **When**: Precise timestamp of each operation
4. **How**: Step-by-step phase progression (pre-audit → sync → post-audit → evidence → trace)
5. **Proof**: Checksums, digital fingerprints, correlation IDs linking all operations

---

## 7. Running the Complete Cycle

### Option 1: Dry-Run (No Changes)

```powershell
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -DryRun -VerboseTrace
```

**Output**: 
- All audits run
- Shows what WOULD change (but doesn't commit)
- Generates trace showing simulated operations
- Safe to validate before real execution

### Option 2: Real Execution

```powershell
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -VerboseTrace
```

**Output**:
- Executes all 5 phases (pre-audit → sync → post-audit → evidence → trace)
- Modifies ADO map and data model
- Generates 22 evidence receipts
- 1 master trace file
- Returns status: PASS or FAIL

### Option 3: Audit Only (No Sync)

```powershell
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode audit
```

**Output**: Pre-audit gates only, no data model changes

### Option 4: Post-Verification (After Manual Changes)

```powershell
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode verify
```

**Output**: Post-audit gates only, verifies existing state

---

## 8. Failure Recovery Procedure

If a failure occurs:

1. **Check the trace**: `.eva/traces/epic15-sync-trace-{correlation_id}.json`
2. **Find the failure**: Look for `"status": "FAILED"`
3. **Identify the operation**: Check which story/phase failed
4. **Determine root cause**: Review error_message field
5. **Manual correction**: Fix the underlying issue (API down, permissions, etc.)
6. **Re-run with dry-run**: `pwsh ... -Mode full -DryRun` to validate fix
7. **Resume sync**: `pwsh ... -Mode full` to complete

**Safety mechanism**: G04 idempotency gate ensures re-run is safe (no duplicate IDs assigned)

---

## 9. Compliance with Foundational Rules

This framework enforces:

✅ **Same-PR Rule**: Stories NOT added to data model during PLAN.md commit; NOW added retroactively with full evidence trail
✅ **Deterministic Behavior**: Idempotent, reproducible, operator-independent
✅ **Traceability**: Every operation traced with correlation ID
✅ **Explainability**: Every change documented with narrative (why, what, when, how, proof)
✅ **Verification**: Pre-, during, and post-audit gates
✅ **Evidence**: Immutable receipt files per story

---

## Appendix: Quick Reference

| Action | Command |
|--------|---------|
| Dry-run full sync | `pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -DryRun` |
| Real full sync | `pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full` |
| Show help | `Get-Help scripts/epic15-update-cycle-with-evidence.ps1` |
| Verify existing state | `pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode verify` |
| View trace | `Get-Content ".eva/traces/epic15-sync-trace-*.json" \| ConvertFrom-Json` |
| View all receipts | `Get-ChildItem ".eva/evidence/ACA-15-*-update-receipt.json"` |
