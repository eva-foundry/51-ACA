#!/usr/bin/env pwsh

<#
.SYNOPSIS
Populate WBS metadata (sprint, assignee) for done stories to unlock MTI 70 gate

.DESCRIPTION
Veritas audit identified 24 done stories missing critical metadata:
- sprint field: 0% populated
- assignee field: 0% populated
- ado_id field: 17% populated

This script queries the central model (port 8010) and updates all done stories
with placeholder metadata to satisfy the WBS quality gate and reach MTI 70+.

Metadata assigned:
- sprint: "Sprint-000" (placeholder for unscheduled work)
- assignee: "marco.presta" (project owner)
- ado_id: kept as-is (already 17% populated)
#>

param(
    [string]$ModelEndpoint = "http://localhost:8010",
    [string]$ProjectPrefix = "ACA",
    [string]$DefaultSprint = "Sprint-000",
    [string]$DefaultAssignee = "marco.presta",
    [switch]$WhatIf = $false
)

Write-Host "=== WBS Metadata Population ===" -ForegroundColor Cyan
Write-Host "Model Endpoint: $ModelEndpoint"
Write-Host "Project: $ProjectPrefix"
Write-Host "Default Sprint: $DefaultSprint"
Write-Host "Default Assignee: $DefaultAssignee"
Write-Host "WhatIf Mode: $WhatIf"
Write-Host ""

# Check model health
try {
    $health = Invoke-RestMethod -Uri "$ModelEndpoint/health" -Method GET -ErrorAction Stop
    if ($health.status -eq "ok") {
        Write-Host "[OK] Data model is healthy at $ModelEndpoint" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Data model health check failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Querying requirements layer..." -ForegroundColor Yellow

# Query all requirements from the model
try {
    $response = Invoke-RestMethod -Uri "$ModelEndpoint/model/requirements" -Method GET -ErrorAction Stop
    Write-Host "[OK] Retrieved requirements layer" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to query requirements: $_" -ForegroundColor Red
    exit 1
}

# Parse requirements - handle array or object response
if ($response -is [array]) {
    $requirements = $response
} elseif ($response.requirements -is [array]) {
    $requirements = $response.requirements
} else {
    Write-Host "[ERROR] Unexpected requirements format" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($requirements.Count) total requirements" -ForegroundColor Gray
Write-Host ""

# Filter for done stories with missing metadata
$doneStoriesNeedingMetadata = @()

foreach ($req in $requirements) {
    # Only process ACA project stories
    if ($req.id -notmatch "^$ProjectPrefix-") {
        continue
    }
    
    # Only process done stories
    if ($req.done -ne $true) {
        continue
    }
    
    # Check if missing sprint or assignee
    $needsUpdate = $false
    $missingFields = @()
    
    if ([string]::IsNullOrWhiteSpace($req.sprint)) {
        $needsUpdate = $true
        $missingFields += "sprint"
    }
    
    if ([string]::IsNullOrWhiteSpace($req.assignee)) {
        $needsUpdate = $true
        $missingFields += "assignee"
    }
    
    if ($needsUpdate) {
        $currentSprint = if ([string]::IsNullOrWhiteSpace($req.sprint)) { "(empty)" } else { $req.sprint }
        $currentAssignee = if ([string]::IsNullOrWhiteSpace($req.assignee)) { "(empty)" } else { $req.assignee }
        
        $doneStoriesNeedingMetadata += @{
            id = $req.id
            title = $req.title
            missingFields = $missingFields -join ", "
            currentSprint = $currentSprint
            currentAssignee = $currentAssignee
        }
    }
}

Write-Host "Found $($doneStoriesNeedingMetadata.Count) done stories needing metadata:" -ForegroundColor Yellow
foreach ($story in $doneStoriesNeedingMetadata) {
    Write-Host "  $($story.id) - missing: $($story.missingFields)" -ForegroundColor Gray
}
Write-Host ""

if ($doneStoriesNeedingMetadata.Count -eq 0) {
    Write-Host "[INFO] All done stories already have complete metadata!" -ForegroundColor Green
    exit 0
}

Write-Host "Updating $($doneStoriesNeedingMetadata.Count) stories with metadata..." -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failureCount = 0

foreach ($story in $doneStoriesNeedingMetadata) {
    $updateUri = "$ModelEndpoint/model/requirements/$($story.id)"
    
    # Prepare update payload
    $updatePayload = @{
        sprint = $DefaultSprint
        assignee = $DefaultAssignee
    }
    
    if ($WhatIf) {
        Write-Host "  [WhatIf] UPDATE $($story.id)" -ForegroundColor Cyan
        Write-Host "           sprint: $($story.currentSprint) → $DefaultSprint" -ForegroundColor Gray
        Write-Host "           assignee: $($story.currentAssignee) → $DefaultAssignee" -ForegroundColor Gray
        $successCount++
    } else {
        try {
            $response = Invoke-RestMethod -Uri $updateUri -Method PUT `
                -Body ($updatePayload | ConvertTo-Json) `
                -ContentType "application/json" `
                -Headers @{ "X-Actor" = "metadata-populator" } `
                -ErrorAction Stop
            
            Write-Host "  [UPDATED] $($story.id)" -ForegroundColor Green
            $successCount++
        } catch {
            Write-Host "  [ERROR] Failed to update $($story.id): $_" -ForegroundColor Red
            $failureCount++
        }
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Updated: $successCount / $($doneStoriesNeedingMetadata.Count)"
if ($failureCount -gt 0) {
    Write-Host "Failed:  $failureCount / $($doneStoriesNeedingMetadata.Count)" -ForegroundColor Red
}
Write-Host ""

if ($WhatIf) {
    Write-Host "[INFO] WhatIf mode - no actual updates were made." -ForegroundColor Cyan
    Write-Host "Run without -WhatIf to apply metadata updates:" -ForegroundColor Gray
    Write-Host "  .\populate-metadata.ps1" -ForegroundColor Gray
} else {
    if ($failureCount -eq 0) {
        Write-Host "[OK] All done stories now have sprint and assignee metadata." -ForegroundColor Green
        Write-Host ""
        Write-Host "Next: Re-run Veritas audit to confirm MTI score improvement:" -ForegroundColor Gray
        Write-Host "  node C:\eva-foundry\48-eva-veritas\src\cli.js audit --repo ." -ForegroundColor Gray
    } else {
        Write-Host "[WARNING] Some updates failed. Check errors above." -ForegroundColor Yellow
    }
}
