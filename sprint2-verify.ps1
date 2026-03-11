#!/usr/bin/env pwsh
# Sprint 2 Comprehensive Verification - Simplified (No Wrapper)
# Location: 51-ACA/sprint2-verify.ps1

Write-Host ""
Write-Host "=== SPRINT 2 READINESS VERIFICATION ===" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$gates = @{pass=0; fail=0}

# GATE 1: LOCAL DB
Write-Host "[GATE 1] LOCAL DB Sprint 2 Linkage" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Gray

$dbCmd = @'
import sys
sys.path.insert(0, 'data-model')
import db
s2 = [s for s in db.list_layer("wbs") if s.get("sprint_id") == "Sprint-02"]
print(f"Count: {len(s2)}")
if s2: print(f"Sample IDs: {', '.join([s.get('id', 'N/A')[:15] for s in s2[:3]])}")
'@

Write-Host "Checking LOCAL db for sprint_id='Sprint-02'..." -ForegroundColor Gray
try {
    $dbOut = C:\eva-foundry\.venv\Scripts\python.exe -c $dbCmd 2>&1 | Out-String
    Write-Host $dbOut -ForegroundColor Gray
    
    if ($dbOut -match "Count: 15") {
        Write-Host "Result: PASS (15 stories found)" -ForegroundColor Green
        $gates.pass++
    } else {
        Write-Host "Result: FAIL (Expected 15 stories)" -ForegroundColor Red
        $gates.fail++
    }
} catch {
    Write-Host "Result: FAIL (Error: $_)" -ForegroundColor Red
    $gates.fail++
}
Write-Host ""

# GATE 2: ADO Sprint 2 Assignment (3 samples)
Write-Host "[GATE 2] ADO Sprint 2 Assignment (3 samples)" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Gray

$samples = @(2978, 2985, 2993)
$adoPass = 0

foreach ($id in $samples) {
    try {
        $iteration = az boards work-item show --id $id --org https://dev.azure.com/marcopresta --query "fields.`"System.IterationPath`"" -o tsv 2>$null
        $match = ($iteration -eq "51-aca\Sprint 2")
        
        if ($match) {
            Write-Host "  WI $id -> $iteration [PASS]" -ForegroundColor Green
            $adoPass++
        } else {
            Write-Host "  WI $id -> $iteration [FAIL - Expected: 51-aca\Sprint 2]" -ForegroundColor Red
        }
    } catch {
        Write-Host "  WI $id -> Error: $_ [FAIL]" -ForegroundColor Red
    }
}

if ($adoPass -eq 3) {
    Write-Host "Result: PASS (3/3 correct)" -ForegroundColor Green
    $gates.pass++
} else {
    Write-Host "Result: FAIL ($adoPass/3 correct)" -ForegroundColor Red
    Write-Host "Action: Run sync-ado-sprint2-improved.ps1" -ForegroundColor Yellow
    $gates.fail++
}
Write-Host ""

# GATE 3: Baseline Tests
Write-Host "[GATE 3] Baseline Test Suite" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Gray
Write-Host "Running: pytest services/ -x -q --tb=line" -ForegroundColor Gray

try {
    $testOut = C:\eva-foundry\.venv\Scripts\python.exe -m pytest services/ -x -q --tb=line 2>&1 | Out-String
    $testExitCode = $LASTEXITCODE
    
    Write-Host $testOut -ForegroundColor Gray
    Write-Host "Exit Code: $testExitCode" -ForegroundColor Gray
    
    if ($testExitCode -eq 0) {
        Write-Host "Result: PASS" -ForegroundColor Green
        $gates.pass++
    } else {
        Write-Host "Result: FAIL" -ForegroundColor Red
        $gates.fail++
    }
} catch {
    Write-Host "Result: FAIL (Error: $_)" -ForegroundColor Red
    $gates.fail++
}
Write-Host ""

# SUMMARY
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "FINAL RESULT" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "PASS: $($gates.pass) / 3" -ForegroundColor Green
Write-Host "FAIL: $($gates.fail) / 3" -ForegroundColor Red
Write-Host ""

if ($gates.fail -eq 0) {
    Write-Host "STATUS: READY FOR SPRINT 2 EXECUTION" -ForegroundColor Green -BackgroundColor Black
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Create GitHub issue: https://github.com/eva-foundry/51-ACA/issues/new" -ForegroundColor White
    Write-Host "2. Title: Sprint 2 - Analysis Rules (15 stories)" -ForegroundColor White
    Write-Host "3. Add label: sprint-task" -ForegroundColor White
    Write-Host "4. Monitor: https://github.com/eva-foundry/51-ACA/actions" -ForegroundColor White
} else {
    Write-Host "STATUS: NOT READY - FIX FAILURES ABOVE" -ForegroundColor Red -BackgroundColor Black
    Write-Host ""
    Write-Host "Actions Required:" -ForegroundColor Cyan
    Write-Host "- Fix failed gates and re-run this script" -ForegroundColor White
    Write-Host "- For GATE 2 (ADO): Run sync-ado-sprint2-improved.ps1" -ForegroundColor White
    Write-Host "- For GATE 3 (Tests): Fix failing tests in services/" -ForegroundColor White
}

Write-Host ""
