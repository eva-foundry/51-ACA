# Epic 15 Verification & Evidence Cycle: Quick Start Guide
# EVA-STORY: ACA-15-013

**Date**: March 2, 2026  
**Commit**: 77da220  
**Framework**: Complete zero-tolerance verification, evidence, and traceability system

---

## What We've Built

A comprehensive 5-phase verification and evidence framework that ensures:

✅ **Nothing is unsurveilled**: Every operation traced with correlation ID + timestamp  
✅ **Explainability**: Why (narrative) + What (payload) + When (timestamp) + How (phase) + Proof (hash)  
✅ **Deterministic behavior**: Idempotent, reproducible, operator-independent  
✅ **Traceability**: All 23 story syncs cross-linked by single correlation ID  
✅ **Immutable evidence**: An evidence receipt generated per story, cryptographically signed  

---

## Three Core Documents (Just Committed)

### 1. `scripts/epic15-update-cycle-with-evidence.ps1`

**Purpose**: Complete orchestration script that manages the entire Epic 15 data model synchronization with comprehensive instrumentation.

**What it does**:
- **Phase 1 (Pre-Audit)**: Runs 4 readiness gates (G01-G04)
  - G01: Data model health check
  - G02: PLAN.md contains 22 stories (regex validation)
  - G03: ADO ID map exists and is valid JSON
  - G04: No Epic 15 stories yet in ADO map (idempotency)

- **Phase 2 (Sync)**: For each of 23 stories:
  - PUT to data model `/wbs/{story_id}` endpoint
  - Update `.eva/ado-id-map.json` with story ID → ADO ID mapping
  - Trace every operation with correlation ID

- **Phase 3 (Post-Audit)**: Runs 3 verification gates (PA01-PA03)
  - PA01: All 23 stories now in ADO map
  - PA02: ADO IDs are sequential 3193-3215 (no gaps)
  - PA03: PLAN.md unchanged (deterministic verification)

- **Phase 4 (Evidence)**: Generate immutable evidence receipt for each of 23 stories
  - Stored in `.eva/evidence/{story_id}-update-receipt.json`
  - Contains: inputs, outputs, validation results, cryptographic fingerprint

- **Phase 5 (Trace)**: Generate master traceability report
  - Stored in `.eva/traces/epic15-sync-trace-{correlation_id}.json`
  - Contains: all 7+ phases, every operation, all errors/warnings, verification status

**Usage**:
```powershell
# Dry-run (no changes, full validation)
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -DryRun -VerboseTrace

# Real execution (modifies ADO map and data model)
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -VerboseTrace

# Other modes
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode audit     # Pre-audit only
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode sync      # Sync only (skip verify)
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode verify    # Post-audit only
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode report    # Generate trace only
```

---

### 2. `docs/EPIC-15-VERIFICATION-AND-EVIDENCE-FRAMEWORK.md`

**Purpose**: Complete specification of the verification and evidence framework.

**Sections**:
1. **Pre-Audit Gates (G01-G04)**: What each gate checks, how to verify, failure modes, recovery procedures
2. **During-Sync Instrumentation**: Tracing fields for every operation (witness format)
3. **Post-Audit Gates (PA01-PA03)**: Cross-reference verification checks
4. **Deterministic Behavior**: Idempotency, sequential ID assignment, operator independence, consistency
5. **Evidence Receipt Schema**: JSON structure for immutable proofs (per story)
6. **Traceability Report Schema**: Master trace structure with all phases, all operations
7. **Deterministic Checklist**: 14-item verification checklist to confirm sync correctness
8. **Explainability Narrative**: How the trace explains why, what, when, how, proof
9. **Running the Cycle**: All 4 usage modes explained
10. **Failure Recovery**: How to diagnose and fix issues

**Key Concepts**:
- **Idempotency**: Running script 2x with clean ADO map produces identical results
- **Deterministic ID Assignment**: ACA-15-000 always → ADO ID 3193, ACA-15-001 always → 3194, etc. (no randomness)
- **Operator Independence**: Output identical whether run by agent or human (only correlation ID / actor differ)
- **Consistency**: PLAN.md, data model, and ADO map all agree on 23 stories

---

### 3. `docs/EPIC-15-DATA-MODEL-SCHEMA-EXTENSION.md`

**Purpose**: Exact JSON schema for all 23 WBS layer entries.

**Contains**:
- Schema definition (field types, required/optional, examples)
- Complete payload examples (3 stories shown in detail)
- PUT operation format (exact endpoint, headers, body)
- Expected response format
- Validation rules (POST /model/admin/validate checklist)
- ADO ID mapping (complete 23-entry table: story ID → ADO ID 3193-3215)
- Deterministic verification checklist

**Key ADO ID Mapping**:
```
ACA-15-000 → 3193
ACA-15-001 → 3194
ACA-15-001a → 3195
... (sequential) ...
ACA-15-012a → 3215
```

Total: 23 stories → 23 sequential ADO IDs (3193-3215)

---

## How to Execute

### Step 1: Pre-Flight (Dry-Run)

```powershell
cd C:\eva-foundry\51-ACA

# Run dry-run to validate everything without making changes
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -DryRun -VerboseTrace

# Review output:
# - All 4 pre-audit gates should PASS
# - All 23 sync operations should SKIPPED (dry-run)
# - All 3 post-audit gates should PASS (paths validated)
# - Evidence generation shown as SKIPPED
# - Correlation ID logged for reference
```

**Expected Output snippet**:
```
=================================================================
  Epic 15 Data Model Synchronization with Comprehensive Evidence
=================================================================
  Correlation ID: ACA-EPIC15-20260302-xxxxxx
  Timestamp: 2026-03-02T...
  Mode: full
  DryRun: True
  VerboseTrace: True
=================================================================

=== PHASE 1: PRE-AUDIT (Readiness gates) ===
[1] G01 DataModel-Health => VERIFIED
[2] G02 PlanContainsEpic15 => VERIFIED
[3] G03 ADO-IdMapExists => VERIFIED
[4] G04 NoEpic15InADOMap => VERIFIED

[SUMMARY] PASS=4 WARN=0 FAIL=0

=== PHASE 2: SYNCHRONIZATION ===
[DRY-RUN] No changes will be made
[ACA-15-000] Syncing to ADO ID 3193...
  [DRY-RUN] Would sync to data model
  [DRY-RUN] Would update ADO map
...
[SUMMARY] Data Model Syncs: 0 | ADO Map Updates: 0

=== PHASE 3: POST-AUDIT (Verification) ===
(Output matches PHASE 1)

[SUMMARY] PASS=3 FAIL=0

=== PHASE 4: EVIDENCE RECEIPT GENERATION ===
(Skipped in dry-run)

=== PHASE 5: TRACEABILITY REPORT ===
(Shows summary of all operations traced)

=== CONCLUSION ===
[PASS] Full synchronization cycle complete. All gates passed.
Correlation ID: ACA-EPIC15-20260302-xxxxxx
```

### Step 2: Real Execution

```powershell
# When dry-run passes, execute for real
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -VerboseTrace

# This will:
# 1. Run Phase 1 (pre-audit gates)
# 2. PUT each of 23 stories to data model
# 3. Update .eva/ado-id-map.json with 23 new entries
# 4. Run Phase 3 (post-audit gates)
# 5. Generate 23 evidence receipts in .eva/evidence/
# 6. Generate master trace in .eva/traces/
```

### Step 3: Verification

```powershell
# Confirm all 23 evidence receipts were created
Get-ChildItem ".eva/evidence/ACA-15-*-update-receipt.json" | Measure-Object
# Should return: Count = 23

# View the master trace
$trace = Get-Content ".eva/traces/epic15-sync-trace-*.json" | ConvertFrom-Json
$trace.execution_summary

# Should show:
# total_stories = 23
# data_model_operations = 23
# ado_map_updates = 23
# evidence_receipts_generated = 23
# errors = 0
# warnings = 0
```

### Step 4: Deterministic Verification

```powershell
# Confirm idempotency: run again with clean ADO map
# 1. Manually delete ADO entries for ACA-15-* from .eva/ado-id-map.json
# 2. Re-run: pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full
# 3. Compare: Same correlation trace elements should repeat (same checksums, counts)
# 4. Result: G04 gate should show "already present, will skip updates" on second run
```

---

## Evidence Artifacts Generated

### Evidence Receipts (23 files)
```
.eva/evidence/ACA-15-000-update-receipt.json
.eva/evidence/ACA-15-001-update-receipt.json
.eva/evidence/ACA-15-001a-update-receipt.json
... (21 more) ...
.eva/evidence/ACA-15-012a-update-receipt.json
```

**Breakdown of receipt**:
- `story_id`: Which story this proves
- `correlation_id`: Links to master trace
- `timestamp`: When the operation occurred
- `inputs`: What was sent to data model
- `outputs`: What was stored (actual IDs, versions)
- `validation`: Which gates passed (pre-, post-, consistency)
- `fingerprint`: Cryptographic SHA256 signature for tampering detection

### Master Trace Report (1 file)
```
.eva/traces/epic15-sync-trace-ACA-EPIC15-20260302-xxxxxx.json
```

**Contains**:
- Execution summary (story counts, operation counts, error counts)
- Audit gate results (pre and post)
- Detailed phases: All 7+ operation sequences with timestamps
- Errors and warnings log
- Verification status (determinism, idempotency, traceability)

---

## Guarantees Provided

### Guarantee 1: Zero Tolerance for Unverified Changes
Every story sync generates an immutable evidence receipt. If receipt missing → sync failed or incomplete.

### Guarantee 2: Complete Traceability
Single correlation ID links all 23 story operations. Query by correlation ID to see everything.

### Guarantee 3: Deterministic Behavior
Same inputs (PLAN.md with 23 stories) → same outputs (ADO IDs 3193-3215) → same trace structure.

### Guarantee 4: Safe Re-execution
G04 idempotency gate prevents duplicate ID assignment. Re-running with clean ADO map is safe (will reassign same IDs).

### Guarantee 5: Explainability
For every story, trace explains: why (narrative), what (payload), when (timestamp), how (phase), proof (hash).

---

## Troubleshooting

### Scenario 1: Pre-Audit Gate Fails (G01-G04)

**Symptom**: 
```
[FAIL] G01 DataModel-Health: Health status is unreachable
```

**Root Cause**: Data model API not responding  
**Solution**: 
```powershell
# Restart data-model service
pwsh -File C:\eva-foundry\37-data-model\start.ps1
Start-Sleep 4

# Re-run dry-run
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -DryRun
```

### Scenario 2: Post-Audit Gate Fails (PA01-PA03)

**Symptom**:
```
[FAIL] PA01 AllStoriesInAdoMap: Expected 23, found 15
```

**Root Cause**: Sync got interrupted partway through (network, API timeout)  
**Solution**:
```powershell
# Check the trace to see where it failed
$trace = Get-Content ".eva/traces/epic15-sync-trace-*.json" | ConvertFrom-Json
$trace.detailed_phases | Where-Object { $_.status -eq "FAILED" }

# Fix the root cause (network issue, credentials, etc.)
# Then re-run - G04 gate will detect that some entries already exist
pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full

# Second run will skip the already-completed operations and continue
```

### Scenario 3: Deterministic Verification Fails

**Symptom**: Running script 2x produces different ADO ID assignments  
**Root Cause**: Bug in script (should not happen)  
**Solution**: 
```powershell
# Check trace checksums
$trace1 = Get-Content ".eva/traces/epic15-sync-trace-*.json" | ConvertFrom-Json | selected-first
$trace2 = Get-Content ".eva/traces/epic15-sync-trace-*.json" | ConvertFrom-Json | select-last

# Compare operation counts
$trace1.execution_summary.data_model_operations -eq $trace2.execution_summary.data_model_operations
# Should be true

# If false, file a bug with traces attached
```

---

## Files Changed

| File | Type | Size | Purpose |
|------|------|------|---------|
| `scripts/epic15-update-cycle-with-evidence.ps1` | PowerShell | ~850 lines | Main orchestration script with 5 phases |
| `docs/EPIC-15-VERIFICATION-AND-EVIDENCE-FRAMEWORK.md` | Markdown | ~550 lines | Complete spec (gates, determinism, evidence, traceability) |
| `docs/EPIC-15-DATA-MODEL-SCHEMA-EXTENSION.md` | Markdown | ~630 lines | WBS schema, payload examples, ADO ID mapping |

**Total**: 3 files, ~2030 lines, comprehensive zero-tolerance verification framework

---

## Next Steps

1. **Dry-run first**: `pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -DryRun -VerboseTrace`
2. **Review dry-run output**: Confirm all 4 pre-audit gates PASS
3. **Execute real sync**: `pwsh scripts/epic15-update-cycle-with-evidence.ps1 -Mode full -VerboseTrace`
4. **Verify artifacts**: Check `.eva/evidence/` (23 files) and `.eva/traces/` (1 file)
5. **Check ADO map**: Confirm `.eva/ado-id-map.json` has 23 new entries (ACA-15-000 through ACA-15-012a → IDs 3193-3215)
6. **Data model validation**: `Invoke-RestMethod "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io/model/admin/validate"` should return 0 violations
7. **Git commit evidence**: `git add .eva/evidence .eva/traces && git commit -m "evidence(ACA-15): Epic 15 synchronization complete, all gates passed, 23 receipts generated"`

---

## Summary

**What**: Complete verification, evidence, and traceability framework for Epic 15 data model synchronization  
**Why**: Nothing can be left unsurveilled. Retroactively enforce same-PR rule with comprehensive instrumentation  
**How**: 5-phase orchestration with pre/during/post-audit gates, immutable evidence receipts, deterministic behavior verification  
**Result**: 23 story syncs with immutable proof, complete traceability, and repeatable audits  
**Safety**: Idempotent (safe to re-run), deterministic (same inputs = same outputs), operator-independent  

---

**Commit**: 77da220  
**Correlation ID Pattern**: `ACA-EPIC15-YYYYMMDD-HHMMSS-{hash}`  
**Evidence Location**: `.eva/evidence/` and `.eva/traces/`  
