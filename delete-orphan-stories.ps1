#!/usr/bin/env pwsh

<#
.SYNOPSIS
Delete orphan story tags (template placeholders) from central data model (port 8010)

.DESCRIPTION
Veritas audit identified 13 malformed story records that should not exist:
- ACA-16-001 through ACA-16-007 (out of range, ACA-16 epic does not exist)
- ACA-17-004, ACA-17-005 (out of range, ACA-17 epic does not exist)
- ACA-12-023 (out of range, ACA-12 only has 16 stories)
- ACA-XX-XXX, ACA-NN-NNN, ACA- (template placeholders)

This script queries and deletes them from port 8010.
#>

param(
    [string]$ModelEndpoint = "http://localhost:8010",
    [switch]$WhatIf = $false
)

# List of orphan story IDs to delete (from Veritas audit GAPS section)
$orphanStories = @(
    "ACA-16-001",
    "ACA-16-002", 
    "ACA-16-003",
    "ACA-16-004",
    "ACA-",
    "ACA-XX-XXX",
    "ACA-12-023",
    "ACA-NN-NNN",
    "ACA-17-005",
    "ACA-17-004",
    "ACA-16-005",
    "ACA-16-006",
    "ACA-16-007"
)

function Test-ModelHealth {
    try {
        $response = Invoke-RestMethod -Uri "$ModelEndpoint/health" -Method GET -ErrorAction Stop
        if ($response.status -eq "ok") {
            Write-Host "[OK] Data model is healthy at $ModelEndpoint" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "[ERROR] Data model health check failed: $_" -ForegroundColor Red
        return $false
    }
}

function Delete-OrphanStory {
    param(
        [string]$StoryId,
        [string]$Layer = "requirements"
    )
    
    # Story ID must be URL-encoded if it contains special chars
    $encodedId = [System.Uri]::EscapeDataString($StoryId)
    $deleteUri = "$ModelEndpoint/model/$layer/$encodedId"
    
    try {
        if ($WhatIf) {
            Write-Host "  [WhatIf] DELETE $deleteUri" -ForegroundColor Cyan
            return $true
        } else {
            Invoke-RestMethod -Uri $deleteUri -Method DELETE -ErrorAction Stop | Out-Null
            Write-Host "  [DELETED] $StoryId" -ForegroundColor Green
            return $true
        }
    } catch {
        # 404 is acceptable - record doesn't exist (maybe already deleted)
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "  [SKIP] $StoryId (not found / already deleted)" -ForegroundColor Yellow
            return $true
        } else {
            Write-Host "  [ERROR] Failed to delete $StoryId : $_" -ForegroundColor Red
            return $false
        }
    }
}

Write-Host "=== Orphan Story Tag Deletion ===" -ForegroundColor Cyan
Write-Host "Model Endpoint: $ModelEndpoint"
Write-Host "WhatIf Mode: $WhatIf"
Write-Host ""

# Check model health first
if (-not (Test-ModelHealth)) {
    Write-Host "[FATAL] Data model is unreachable. Start it with: npm start (in 37-data-model)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deleting $($orphanStories.Count) orphan stories..." -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failureCount = 0

foreach ($storyId in $orphanStories) {
    if (Delete-OrphanStory -StoryId $storyId -Layer "requirements") {
        $successCount++
    } else {
        $failureCount++
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Deleted: $successCount / $($orphanStories.Count)"
if ($failureCount -gt 0) {
    Write-Host "Failed:  $failureCount / $($orphanStories.Count)" -ForegroundColor Red
}
Write-Host ""

if ($WhatIf) {
    Write-Host "[INFO] WhatIf mode - no actual deletions performed." -ForegroundColor Cyan
    Write-Host "Run without -WhatIf to execute deletions:" -ForegroundColor Gray
    Write-Host "  .\delete-orphan-stories.ps1" -ForegroundColor Gray
} else {
    Write-Host "[OK] Orphan story tags deleted from data model." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Run Veritas audit to confirm cleanup:" -ForegroundColor Gray
    Write-Host "  node C:\eva-foundry\48-eva-veritas\src\cli.js audit --repo ." -ForegroundColor Gray
}
