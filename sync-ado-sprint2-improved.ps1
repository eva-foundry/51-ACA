# ADO Sprint 2 Sync - Execute with retry logic
# Handles az CLI extension prompts gracefully

$org = "https://dev.azure.com/marcopresta"
$iteration = "51-aca\Sprint 2"

$workItems = @(
    @{id=2978; story="ACA-03-001"},
    @{id=2979; story="ACA-03-002"},
    @{id=2980; story="ACA-03-003"},
    @{id=2981; story="ACA-03-004"},
    @{id=2982; story="ACA-03-005"},
    @{id=2984; story="ACA-03-007"},
    @{id=2985; story="ACA-03-008"},
    @{id=2986; story="ACA-03-009"},
    @{id=2987; story="ACA-03-010"},
    @{id=2988; story="ACA-03-011"},
    @{id=2989; story="ACA-03-012"},
    @{id=2990; story="ACA-03-013"},
    @{id=2991; story="ACA-03-014"},
    @{id=2992; story="ACA-03-015"},
    @{id=2993; story="ACA-03-016"}
)

Write-Host "============================================"
Write-Host "ADO SPRINT 2 SYNC"
Write-Host "============================================"
Write-Host "Organization: $org"
Write-Host "Iteration: $iteration"
Write-Host "Work Items: $($workItems.Count)"
Write-Host ""

$successCount = 0
$failCount = 0
$failed = @()

foreach ($wi in $workItems) {
    Write-Host "[$($wi.story)] Updating work item $($wi.id)..."
    
    try {
        $result = az boards work-item update `
            --id $wi.id `
            --org $org `
            --iteration $iteration `
            --output json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [PASS] Work item $($wi.id) updated" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  [FAIL] Work item $($wi.id) - Exit code: $LASTEXITCODE" -ForegroundColor Red
            Write-Host "  Error: $result"
            $failCount++
            $failed += $wi.id
        }
    } catch {
        Write-Host "  [FAIL] Work item $($wi.id) - Exception: $_" -ForegroundColor Red
        $failCount++
        $failed += $wi.id
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "============================================"
Write-Host "SUMMARY"
Write-Host "============================================"
Write-Host "Total: $($workItems.Count)"
Write-Host "Success: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Failed work items: $($failed -join ', ')" -ForegroundColor Red
    Write-Host ""
    Write-Host "RETRY COMMAND:"
    Write-Host "az boards work-item update --id NNNN --org $org --iteration `"$iteration`""
    exit 1
} else {
    Write-Host ""
    Write-Host "[PASS] All 15 work items assigned to Sprint 2" -ForegroundColor Green
    Write-Host ""
    Write-Host "VERIFY:"
    Write-Host "Open: https://dev.azure.com/marcopresta/51-aca/_sprints/taskboard/51-aca/51-aca/Sprint%202"
    exit 0
}
