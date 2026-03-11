# Manual Verification Instructions

**Issue**: Terminal output capture is blocked in AI agent session  
**Solution**: Run verification scripts manually in your own terminal  
**Your Pattern**: Log file wrapper (implemented below)  

---

## Quick Start

### 1. Browser Check (2 minutes)

**Navigate to Sprint 2 board**:
```
https://dev.azure.com/marcopresta/51-aca/_sprints/taskboard/51-aca%20Team/51-aca/Sprint%202
```

**OR** in your current ADO tab:
- Click "**Sprint 1**" dropdown (top left)
- Select "**Sprint 2**"

**Expected**: 15 work items visible  
**If empty**: Continue to Step 2 to run sync

---

### 2. Run Verification (Python - Recommended)

```powershell
cd C:\eva-foundry\51-ACA
C:\eva-foundry\.venv\Scripts\python.exe manual-verify.py
```

**Output**: Creates `verify-YYYYMMDD-HHMMSS.log` with results  
**Read log**: `type verify-YYYYMMDD-HHMMSS.log`

**Checks**:
- ✅ LOCAL DB: 15 stories linked to Sprint-02
- ⏳ ADO: 3 sample work items in Sprint 2 iteration
- ⏳ Tests: pytest baseline passes

---

### 3. ADO Quick Check (PowerShell - Fast)

```powershell
cd C:\eva-foundry\51-ACA
pwsh -File quick-ado-check.ps1
```

**Output**: Immediate console results for 4 sample work items  
**Expected**: All 4 show "51-aca\Sprint 2"  
**If FAIL**: Continue to Step 4

---

### 4. Sync ADO (If Needed)

```powershell
cd C:\eva-foundry\51-ACA
pwsh -File sync-ado-sprint2-improved.ps1
```

**Duration**: ~30 seconds (15 work items)  
**Output**: Color-coded progress + summary  
**Verify**: Refresh ADO board in browser → should show 15 work items

---

## Verification States

### ✅ LOCAL DB (CONFIRMED)
- 15 stories assigned to Sprint-02
- Story IDs: ACA-03-001 through ACA-03-016 (skipping done 006)
- ADO mapping: Work items 2978-2993
- **Status**: READY

### ❌ Cloud Model (NEEDS FIX)
- Current: `ado_project = "eva-poc"`
- Expected: `ado_project = "51-aca"`
- **Fix**: Run command from VERIFICATION-REPORT.md CHECK 2
- **Impact**: Medium (breaks cloud tracking, does NOT block Sprint 2)

### ⏳ ADO Sprint 2 (UNCERTAIN)
- Expected: 15 work items in "51-aca\Sprint 2" iteration
- **Verification**: Browser check OR quick-ado-check.ps1
- **If FAIL**: sync-ado-sprint2-improved.ps1

### ⏳ Baseline Tests (NOT RUN)
- Expected: pytest exits 0
- **Run**: `C:\eva-foundry\.venv\Scripts\python.exe -m pytest services/ -x -q`

---

## Scripts Created

| Script | Purpose | Output |
|--------|---------|--------|
| `manual-verify.py` | Full 3-gate check (Python) | Log file: `verify-YYYYMMDD-HHMMSS.log` |
| `verify-with-log.ps1` | Full 3-gate check (PowerShell) | Log file: `verify-YYYYMMDD-HHMMSS.log` |
| `quick-ado-check.ps1` | Fast ADO-only check | Console only |
| `sync-ado-sprint2-improved.ps1` | ADO Sprint 2 sync (15 work items) | Console with retry logic |
| `manual-gate-check.ps1` | Alternative full check | Console only |

---

## After Verification Passes

### If All 3 Checks PASS

**Create Sprint 2 GitHub Issue**:
1. URL: https://github.com/eva-foundry/51-ACA/issues/new
2. Title: `Sprint 2 - Analysis Rules (15 stories)`
3. Body: Copy from `sprint-02-manifest.json`
4. Label: `sprint-task`
5. Workflow auto-triggers

**Monitor Execution**:
- URL: https://github.com/eva-foundry/51-ACA/actions
- Duration: 4-8 hours (15 stories)
- Check issue comments for progress updates

---

## Troubleshooting

### ADO "az CLI not authenticated"
```powershell
az login --use-device-code
az account show
```

### ADO Extension missing
```powershell
az extension add --name azure-devops
```

### Python import error
```powershell
cd C:\eva-foundry\51-ACA
C:\eva-foundry\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'data-model'); import db; print('OK')"
```

### Pytest not found
```powershell
C:\eva-foundry\.venv\Scripts\python.exe -m pip install pytest
```

---

## Terminal Output Capture Issue

**Symptom**: AI agent terminal commands return echo only, no output  
**Your Solution**: Log file wrapper pattern ✅ (implemented in scripts above)  
**Workaround**: Manual execution in your own PowerShell terminal  

**Root Cause**: Unknown (terminal state, buffer limit, or tool limitation)  
**Status**: Documented in VERIFICATION-REPORT.md

---

## Ready Criteria

Sprint 2 execution is ready when:

- ✅ LOCAL DB: 15 stories → Sprint-02 (CONFIRMED)
- ⏳ ADO: 15 work items → Sprint 2 iteration (CHECK via browser)
- ⏳ Tests: pytest exits 0 (RUN manually)
- 🟡 Cloud: ado_project = "51-aca" (optional - does not block)
- ✅ Workflow: Files present (CONFIRMED)

**Next**: See DPDCA-SUMMARY.md for Sprint 2 execution steps
