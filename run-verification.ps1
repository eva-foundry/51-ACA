# Sprint 2 Readiness Verification - Writes results to file
# Addresses: Terminal output truncation issue

$outputFile = "sprint2-verification-results.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Result {
    param($message)
    Write-Host $message
    Add-Content -Path $outputFile -Value $message
}

# Clear previous results
if (Test-Path $outputFile) { Remove-Item $outputFile }
Write-Result "=== SPRINT 2 VERIFICATION ==="
Write-Result "Time: $timestamp"
Write-Result ""

# CHECK 1: LOCAL DB
Write-Result "[CHECK 1] LOCAL DB Sprint 2 Linkage"
Write-Result "-----------------------------------"
try {
    $s2Count = & C:\AICOE\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'data-model'); import db; s2 = [s for s in db.list_layer('wbs') if s.get('sprint_id') == 'Sprint-02']; print(len(s2))"
    
    Write-Result "Stories linked to Sprint-02: $s2Count"
    Write-Result "Expected: 15"
    
    if ($s2Count -eq "15") {
        Write-Result "Status: PASS" 
    } else {
        Write-Result "Status: FAIL"
    }
} catch {
    Write-Result "Status: ERROR - $_"
}
Write-Result ""

# CHECK 2: Cloud Cosmos
Write-Result "[CHECK 2] Cloud Cosmos ado_project"
Write-Result "-----------------------------------"
try {
    $proj = Invoke-RestMethod "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io/model/projects/51-ACA"
    
    Write-Result "ado_project: $($proj.ado_project)"
    Write-Result "Expected: 51-aca"
    
    if ($proj.ado_project -eq "51-aca") {
        Write-Result "Status: PASS"
    } else {
        Write-Result "Status: FAIL"
    }
} catch {
    Write-Result "Status: ERROR - $_"
}
Write-Result ""

# CHECK 3: Workflow Files
Write-Result "[CHECK 3] GitHub Workflow Files"
Write-Result "-----------------------------------"
$wf = Test-Path ".github/workflows/sprint-agent.yml"
$sc = Test-Path ".github/scripts/sprint_agent.py"

Write-Result "sprint-agent.yml: $(if ($wf) { 'FOUND' } else { 'MISSING' })"
Write-Result "sprint_agent.py: $(if ($sc) { 'FOUND' } else { 'MISSING' })"

if ($wf -and $sc) {
    Write-Result "Status: PASS"
} else {
    Write-Result "Status: FAIL"
}
Write-Result ""

# CHECK 4: Baseline Tests
Write-Result "[CHECK 4] Baseline Test Suite"
Write-Result "-----------------------------------"
Write-Result "Running pytest services/ -x -q..."

try {
    $testOutput = & C:\AICOE\.venv\Scripts\python.exe -m pytest services/ -x -q --tb=line 2>&1
    $exitCode = $LASTEXITCODE
    
    # Get test count from output
    $summary = $testOutput | Select-String "passed|failed|error" | Select-Object -Last 1
    
    Write-Result "Exit Code: $exitCode"
    Write-Result "Summary: $summary"
    
    if ($exitCode -eq 0) {
        Write-Result "Status: PASS"
    } else {
        Write-Result "Status: FAIL"
        Write-Result "Last 5 lines of output:"
        $testOutput | Select-Object -Last 5 | ForEach-Object { Write-Result "  $_" }
    }
} catch {
    Write-Result "Status: ERROR - $_"
}
Write-Result ""

# CHECK 5: ADO Sprint 2 Assignment
Write-Result "[CHECK 5] ADO Sprint 2 Assignment"
Write-Result "-----------------------------------"
Write-Result "Querying work item 2978..."

try {
    # Check if az CLI is available
    $azVersion = az version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Result "Status: SKIP - az CLI not available or not logged in"
    } else {
        # Try to query work item
        $result = az boards work-item show --id 2978 --org https://dev.azure.com/marcopresta --output json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            try {
                $wi = $result | ConvertFrom-Json
                $iter = $wi.fields.'System.IterationPath'
                
                Write-Result "Work Item 2978 Iteration: $iter"
                Write-Result "Expected: 51-aca\Sprint 2"
                
                if ($iter -eq "51-aca\Sprint 2") {
                    Write-Result "Status: PASS"
                } else {
                    Write-Result "Status: FAIL - Needs sync"
                    Write-Result "Action: Run sync-ado-sprint2-improved.ps1"
                }
            } catch {
                Write-Result "Status: ERROR - Cannot parse JSON"
                Write-Result "Raw result: $($result | Select-Object -First 3)"
            }
        } else {
            Write-Result "Status: FAIL - az CLI returned error"
            Write-Result "Output: $($result | Select-Object -First 3)"
        }
    }
} catch {
    Write-Result "Status: ERROR - $_"
}
Write-Result ""

# SUMMARY
Write-Result "==================================="
Write-Result "SUMMARY"
Write-Result "==================================="

$content = Get-Content $outputFile
$passCount = ($content | Select-String "Status: PASS").Count
$failCount = ($content | Select-String "Status: FAIL").Count
$errorCount = ($content | Select-String "Status: ERROR").Count
$skipCount = ($content | Select-String "Status: SKIP").Count

Write-Result "PASS: $passCount"
Write-Result "FAIL: $failCount"
Write-Result "ERROR: $errorCount"
Write-Result "SKIP: $skipCount"
Write-Result ""

if ($failCount -eq 0 -and $errorCount -eq 0) {
    Write-Result "OVERALL: READY FOR SPRINT EXECUTION"
} else {
    Write-Result "OVERALL: ISSUES FOUND - FIX BEFORE EXECUTION"
}

Write-Result ""
Write-Result "Full results: $outputFile"
Write-Host ""
Write-Host "Results written to: $outputFile" -ForegroundColor Cyan
