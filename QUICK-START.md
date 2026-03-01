# Sprint 2 Quick Start - With Universal Wrapper

## Current State (Confirmed)

✅ LOCAL DB: 15 stories → Sprint-02  
❌ ADO Sprint 2: Empty (your screenshot)  
⏳ Tests: Unknown  
❌ Cloud: ado_project = "eva-poc" (should be "51-aca")  

---

## 3 Commands to Run

### 1. Verify Current State (Uses NEW Wrapper)

```powershell
cd C:\AICOE\eva-foundry\51-ACA
pwsh -NoProfile -File sprint2-verify.ps1
```

**What it does**: 3 gates (DB, ADO, tests) with FULL output visible  
**Expected**: GATE 1 PASS, GATE 2 FAIL, GATE 3 unknown  
**Logs**: `$env:TEMP\eva-command-logs\gate*.log`

---

### 2. Sync ADO Sprint 2 (Fix GATE 2)

```powershell
pwsh -File sync-ado-sprint2-improved.ps1
```

**What it does**: Assigns 15 work items to Sprint 2 iteration  
**Duration**: 30 seconds  
**Verify**: Refresh ADO board → should show 15 items

---

### 3. Re-Verify (Should Be All PASS)

```powershell
pwsh -File sprint2-verify.ps1
```

**Expected**: All 3 gates PASS  
**Then**: Create GitHub issue → label: sprint-task → Sprint 2 executes

---

## What I Created (Foundation Layer)

**07-foundation-layer** (Global for ALL agents):
- `scripts/Invoke-CommandWithLog.ps1` - PowerShell wrapper
- `scripts/invoke_command_with_log.py` - Python wrapper
- `.github/copilot-skills/universal-command-wrapper.skill.md` - Documentation

**51-ACA** (Immediate use):
- `sprint2-verify.ps1` - 3-gate verification WITH wrapper
- `test-wrapper.ps1` - Wrapper test
- `WRAPPER-IMPLEMENTATION.md` - Full guide

---

## The Wrapper Pattern

**Your Ask**: "take the command and what you are looking for, run inside logger, know exact log file, echo back"

**Delivered**:

```powershell
# Load
. C:\AICOE\eva-foundry\07-foundation-layer\scripts\Invoke-CommandWithLog.ps1

# Use
$result = Invoke-CommandWithLog `
    -Command "pytest services/" `
    -SearchPattern "passed"

# Result
Write-Host $result.Output      # What you asked for
Write-Host $result.LogFile     # Exact log location
Write-Host $result.ExitCode    # Command success
```

**Solves**: Terminal output capture bug (no more blank results)  
**Location**: Foundation layer (all agents can use)  
**Pattern**: Skill documented for reuse across EVA

---

## ADO Sprint 2 Board

**Your Screenshot**: Sprint 1 empty  
**Need**: Sprint 2 → https://dev.azure.com/marcopresta/51-aca/_sprints/taskboard/51-aca%20Team/51-aca/Sprint%202

**After sync**: 15 work items visible  
**Story IDs**: ACA-03-001 through ACA-03-016 (skip done 006)  
**Work Items**: 2978-2993

---

## Next Message

After running `sprint2-verify.ps1`, tell me:

1. GATE 1 result: ____
2. GATE 2 result: ____  
3. GATE 3 result: ____

Then we proceed to Sprint 2 execution or fix failures.
