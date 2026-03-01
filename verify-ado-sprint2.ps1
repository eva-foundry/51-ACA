# Verify ADO Sprint 2 Assignment - Simple Check
# Queries a few sample work items to confirm iteration path

$org = "https://dev.azure.com/marcopresta"
$testIds = @(2978, 2985, 2993)  # First, middle, last

Write-Host "Verifying ADO Sprint 2 assignment..."
Write-Host ""

$allGood = $true

foreach ($id in $testIds) {
    try {
        $wi = az boards work-item show --id $id --org $org --query "fields.{id:``System.Id``,title:``System.Title``,iteration:``System.IterationPath``}" --output json 2>&1 | ConvertFrom-Json
        
        if ($wi.iteration -eq "51-aca\Sprint 2") {
            Write-Host "[PASS] WI $($wi.id): $($wi.iteration)" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] WI $($wi.id): $($wi.iteration) (expected: 51-aca\Sprint 2)" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "[ERROR] WI $id: $_" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
if ($allGood) {
    Write-Host "[PASS] Sample check successful - Sprint 2 appears to be assigned" -ForegroundColor Green
    Write-Host "View board: https://dev.azure.com/marcopresta/51-aca/_sprints/taskboard/51-aca/51-aca/Sprint%202"
} else {
    Write-Host "[FAIL] Some work items are not assigned to Sprint 2" -ForegroundColor Red
    Write-Host "Run: sync-ado-sprint2-improved.ps1 to complete assignment"
}
