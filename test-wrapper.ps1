#!/usr/bin/env pwsh
# Test Universal Command Wrapper on 51-ACA Sprint 2 Verification
# Location: 51-ACA/test-wrapper.ps1

. C:\eva-foundry\07-foundation-layer\scripts\Invoke-CommandWithLog.ps1

Write-Host "=== TESTING UNIVERSAL COMMAND WRAPPER ===" -ForegroundColor Cyan
Write-Host ""

# TEST 1: LOCAL DB Sprint 2 Count
Write-Host "[TEST 1] LOCAL DB Sprint 2 Count" -ForegroundColor Yellow
$r1 = Invoke-CommandWithLog `
    -Command "C:\eva-foundry\.venv\Scripts\python.exe -c `"import sys; sys.path.insert(0, 'data-model'); import db; print('Stories:', len([s for s in db.list_layer('wbs') if s.get('sprint_id')=='Sprint-02'])))`"" `
    -SearchPattern "Stories:" `
    -Label "db-check"

Write-Host "  Result: $($r1.Output)" -ForegroundColor $(if ($r1.Success) { 'Green' } else { 'Red' })
Write-Host "  Log: $($r1.LogFile)" -ForegroundColor Gray
Write-Host ""

# TEST 2: ADO Work Item Query
Write-Host "[TEST 2] ADO Work Item 2978 Iteration" -ForegroundColor Yellow
$r2 = Invoke-CommandWithLog `
    -Command "az boards work-item show --id 2978 --org https://dev.azure.com/marcopresta --query `"fields.\`"System.IterationPath\`"`" -o tsv" `
    -Label "ado-2978"

Write-Host "  Iteration: $($r2.Output)" -ForegroundColor $(if ($r2.Success) { 'Green' } else { 'Red' })
Write-Host "  Log: $($r2.LogFile)" -ForegroundColor Gray
Write-Host ""

# TEST 3: Full Verification Script
Write-Host "[TEST 3] Run manual-verify.py with wrapper" -ForegroundColor Yellow
$r3 = Invoke-CommandWithLog `
    -Command "C:\eva-foundry\.venv\Scripts\python.exe manual-verify.py" `
    -ReturnFullLog `
    -Label "full-verify"

Write-Host "  Exit Code: $($r3.ExitCode)" -ForegroundColor $(if ($r3.Success) { 'Green' } else { 'Red' })
Write-Host "  Duration: $($r3.Duration)s" -ForegroundColor Gray
Write-Host "  Log: $($r3.LogFile)" -ForegroundColor Gray
Write-Host ""
Write-Host "  First 30 lines:" -ForegroundColor Gray
($r3.Output -split "`n") | Select-Object -First 30 | ForEach-Object {
    Write-Host "    $_" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== WRAPPER TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "All logs in: $env:TEMP\eva-command-logs\" -ForegroundColor Cyan
