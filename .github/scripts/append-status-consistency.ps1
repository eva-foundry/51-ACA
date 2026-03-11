# Script: append-status-consistency.ps1
# Appends Veritas consistency declarations to STATUS.md

$statusPath = "C:\eva-foundry\51-ACA\STATUS.md"
$planPath   = "C:\eva-foundry\51-ACA\.eva\veritas-plan.json"

$plan = Get-Content $planPath | ConvertFrom-Json

$lines = @()
$lines += ""
$lines += "============================================================================="
$lines += "STORY STATUS (veritas consistency block -- generated 2026-02-27)"
$lines += "============================================================================="

foreach ($f in $plan.features) {
    $lines += ""
    $lines += "# Feature: $($f.id)"
    foreach ($s in $f.stories) {
        $state = if ($s.done) { "Done" } else { "Not Started" }
        $lines += "STORY $($s.id): $state"
    }
}

Add-Content -Path $statusPath -Value ($lines -join "`r`n") -Encoding UTF8
Write-Host "[PASS] STATUS.md consistency block appended"
$count = (Select-String "^STORY ACA-" $statusPath).Count
Write-Host "[INFO] Total STORY declarations in STATUS.md: $count"
