# Quick ADO Sprint 2 Check
# Purpose: Verify if work items are assigned to Sprint 2
# Run from: C:\eva-foundry\51-ACA

Write-Host "=== ADO SPRINT 2 QUICK CHECK ===" -ForegroundColor Cyan
Write-Host ""

$samples = @(2978, 2980, 2985, 2993)
$pass = 0

foreach ($id in $samples) {
    try {
        $iter = az boards work-item show --id $id `
            --org https://dev.azure.com/marcopresta `
            --query "fields.``System.IterationPath``" -o tsv
        
        if ($iter -eq "51-aca\Sprint 2") {
            Write-Host "[PASS] WI $id -> Sprint 2" -ForegroundColor Green
            $pass++
        } else {
            Write-Host "[FAIL] WI $id -> $iter" -ForegroundColor Red
        }
    } catch {
        Write-Host "[ERROR] WI $id -> $_" -ForegroundColor Red
    }
}

Write-Host ""
if ($pass -eq $samples.Count) {
    Write-Host "RESULT: All work items in Sprint 2" -ForegroundColor Green
} else {
    Write-Host "RESULT: $pass / $($samples.Count) in Sprint 2" -ForegroundColor Yellow
    Write-Host "ACTION: Run sync-ado-sprint2-improved.ps1" -ForegroundColor Yellow
}
