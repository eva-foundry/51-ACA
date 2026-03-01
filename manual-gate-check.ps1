# Quick Manual Verification for Sprint 2 Readiness
# Run this in a fresh PowerShell terminal
# Purpose: Confirm 3 critical gates before Sprint 2 execution

Write-Host ""
Write-Host "=== SPRINT 2 READINESS CHECK ===" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$pass = 0
$fail = 0

# Gate 1: LOCAL DB
Write-Host "[GATE 1] LOCAL DB Sprint 2 Linkage" -ForegroundColor Yellow
try {
    $count = & C:\AICOE\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'data-model'); import db; print(len([s for s in db.list_layer('wbs') if s.get('sprint_id') == 'Sprint-02']))"
    Write-Host "  Stories linked: $count / 15" -ForegroundColor Gray
    if ($count -eq "15") {
        Write-Host "  Result: PASS" -ForegroundColor Green
        $pass++
    } else {
        Write-Host "  Result: FAIL" -ForegroundColor Red
        $fail++
    }
} catch {
    Write-Host "  Result: ERROR - $_" -ForegroundColor Red
    $fail++
}
Write-Host ""

# Gate 2: ADO Sprint 2
Write-Host "[GATE 2] ADO Sprint 2 Assignment (3 samples)" -ForegroundColor Yellow
$samples = @(2978, 2985, 2993)
$ado_pass = 0
foreach ($id in $samples) {
    try {
        $iter = az boards work-item show --id $id --org https://dev.azure.com/marcopresta --query "fields.``System.IterationPath``" -o tsv 2>&1
        $match = $iter -eq "51-aca\Sprint 2"
        Write-Host "  WI $id`: $iter $(if ($match) { '[OK]' } else { '[FAIL]' })" -ForegroundColor $(if ($match) { 'Gray' } else { 'Red' })
        if ($match) { $ado_pass++ }
    } catch {
        Write-Host "  WI $id`: ERROR" -ForegroundColor Red
    }
}
if ($ado_pass -eq 3) {
    Write-Host "  Result: PASS (all 3 samples correct)" -ForegroundColor Green
    $pass++
} else {
    Write-Host "  Result: FAIL ($ado_pass/3 correct)" -ForegroundColor Red
    Write-Host "  Action: Run sync-ado-sprint2-improved.ps1" -ForegroundColor Yellow
    $fail++
}
Write-Host ""

# Gate 3: Baseline Tests
Write-Host "[GATE 3] Baseline Test Suite" -ForegroundColor Yellow
Write-Host "  Running: pytest services/ -x -q ..." -ForegroundColor Gray
try {
    $testOutput = & C:\AICOE\.venv\Scripts\python.exe -m pytest services/ -x -q --tb=line 2>&1
    $exitCode = $LASTEXITCODE
    $summary = $testOutput | Select-String "passed|failed|error" | Select-Object -Last 1
    Write-Host "  Exit Code: $exitCode" -ForegroundColor Gray
    Write-Host "  Summary: $summary" -ForegroundColor Gray
    if ($exitCode -eq 0) {
        Write-Host "  Result: PASS" -ForegroundColor Green
        $pass++
    } else {
        Write-Host "  Result: FAIL" -ForegroundColor Red
        Write-Host "  Last 3 lines:" -ForegroundColor Yellow
        $testOutput | Select-Object -Last 3 | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
        $fail++
    }
} catch {
    Write-Host "  Result: ERROR - $_" -ForegroundColor Red
    $fail++
}
Write-Host ""

# Summary
Write-Host "==================" -ForegroundColor Cyan
Write-Host "FINAL RESULT" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "PASS: $pass / 3" -ForegroundColor Green
Write-Host "FAIL: $fail / 3" -ForegroundColor Red
Write-Host ""

if ($fail -eq 0) {
    Write-Host "STATUS: READY FOR SPRINT 2 EXECUTION" -ForegroundColor Green -BackgroundColor Black
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Create GitHub issue: https://github.com/eva-foundry/51-ACA/issues/new" -ForegroundColor Gray
    Write-Host "2. Title: Sprint 2 - Analysis Rules (15 stories)" -ForegroundColor Gray
    Write-Host "3. Add label: sprint-task" -ForegroundColor Gray
    Write-Host "4. Monitor: https://github.com/eva-foundry/51-ACA/actions" -ForegroundColor Gray
} else {
    Write-Host "STATUS: NOT READY - FIX FAILURES ABOVE" -ForegroundColor Red -BackgroundColor Black
    Write-Host ""
    Write-Host "Actions Required:" -ForegroundColor Cyan
    if ($fail -gt 0) {
        Write-Host "- Check failed gates above" -ForegroundColor Yellow
        Write-Host "- Review: VERIFICATION-REPORT.md" -ForegroundColor Yellow
    }
}

Write-Host ""
