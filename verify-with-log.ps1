# Verification with Log File Pattern
# Addresses: Terminal output capture issue
# Pattern: Run commands -> write to unique log -> read log -> cleanup

$logFile = "verify-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Log {
    param($message, $color = "White")
    Write-Host $message -ForegroundColor $color
    Add-Content -Path $logFile -Value $message
}

try {
    Write-Log "=== SPRINT 2 VERIFICATION (Log Pattern) ===" "Cyan"
    Write-Log "Time: $timestamp" "Gray"
    Write-Log "Log: $logFile" "Gray"
    Write-Log ""

    # CHECK 1: LOCAL DB
    Write-Log "[CHECK 1] LOCAL DB Sprint 2 Linkage" "Yellow"
    Write-Log "-----------------------------------" "Gray"
    try {
        $dbCheck = & C:\eva-foundry\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'data-model'); import db; s2 = [s for s in db.list_layer('wbs') if s.get('sprint_id') == 'Sprint-02']; print(f'Count: {len(s2)}'); print(f'IDs: {[s.get(\"id\") for s in s2[:5]]}'); print(f'Status: {\"PASS\" if len(s2) == 15 else \"FAIL\"}')" 2>&1
        
        Write-Log "Output:" "Gray"
        $dbCheck | ForEach-Object { Write-Log "  $_" "Gray" }
        
        if ($dbCheck -match "Status: PASS") {
            Write-Log "Result: PASS" "Green"
            $script:check1 = $true
        } else {
            Write-Log "Result: FAIL" "Red"
            $script:check1 = $false
        }
    } catch {
        Write-Log "Result: ERROR - $_" "Red"
        $script:check1 = $false
    }
    Write-Log ""

    # CHECK 2: ADO Sprint 2 Assignment
    Write-Log "[CHECK 2] ADO Sprint 2 Assignment (3 samples)" "Yellow"
    Write-Log "-----------------------------------" "Gray"
    $samples = @(2978, 2985, 2993)
    $adoPass = 0
    
    foreach ($id in $samples) {
        try {
            $iter = az boards work-item show --id $id --org https://dev.azure.com/marcopresta --query "fields.``System.IterationPath``" -o tsv 2>&1
            $match = $iter -eq "51-aca\Sprint 2"
            
            if ($match) {
                Write-Log "  WI $id : $iter [PASS]" "Green"
                $adoPass++
            } else {
                Write-Log "  WI $id : $iter [FAIL - expected '51-aca\Sprint 2']" "Red"
            }
        } catch {
            Write-Log "  WI $id : ERROR - $_" "Red"
        }
    }
    
    if ($adoPass -eq 3) {
        Write-Log "Result: PASS (3/3 correct)" "Green"
        $script:check2 = $true
    } else {
        Write-Log "Result: FAIL ($adoPass/3 correct)" "Red"
        $script:check2 = $false
    }
    Write-Log ""

    # CHECK 3: Baseline Tests
    Write-Log "[CHECK 3] Baseline Test Suite" "Yellow"
    Write-Log "-----------------------------------" "Gray"
    Write-Log "Running: pytest services/ -x -q --tb=line" "Gray"
    
    try {
        $testOutput = & C:\eva-foundry\.venv\Scripts\python.exe -m pytest services/ -x -q --tb=line 2>&1
        $exitCode = $LASTEXITCODE
        
        Write-Log "Exit Code: $exitCode" "Gray"
        
        # Log last 10 lines of test output
        $testOutput | Select-Object -Last 10 | ForEach-Object {
            Write-Log "  $_" "Gray"
        }
        
        if ($exitCode -eq 0) {
            Write-Log "Result: PASS" "Green"
            $script:check3 = $true
        } else {
            Write-Log "Result: FAIL" "Red"
            $script:check3 = $false
        }
    } catch {
        Write-Log "Result: ERROR - $_" "Red"
        $script:check3 = $false
    }
    Write-Log ""

    # SUMMARY
    Write-Log "===================================" "Cyan"
    Write-Log "FINAL RESULT" "Cyan"
    Write-Log "===================================" "Cyan"
    
    $passCount = @($script:check1, $script:check2, $script:check3) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count
    $failCount = 3 - $passCount
    
    Write-Log "CHECK 1 (LOCAL DB): $(if ($script:check1) { 'PASS' } else { 'FAIL' })" "Gray"
    Write-Log "CHECK 2 (ADO):      $(if ($script:check2) { 'PASS' } else { 'FAIL' })" "Gray"
    Write-Log "CHECK 3 (TESTS):    $(if ($script:check3) { 'PASS' } else { 'FAIL' })" "Gray"
    Write-Log ""
    Write-Log "PASS: $passCount / 3" "Green"
    Write-Log "FAIL: $failCount / 3" "Red"
    Write-Log ""

    if ($failCount -eq 0) {
        Write-Log "STATUS: READY FOR SPRINT 2 EXECUTION" "Green"
    } else {
        Write-Log "STATUS: NOT READY - FIX FAILURES ABOVE" "Red"
    }

} finally {
    Write-Log ""
    Write-Log "Log file: $logFile" "Cyan"
    Write-Host ""
    Write-Host "To read results: Get-Content $logFile" -ForegroundColor Cyan
}
