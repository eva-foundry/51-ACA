#!/usr/bin/env powershell

<#
.SYNOPSIS
Remove orphan story tags from source code and evidence files

.DESCRIPTION
Fixes source code files and evidence files that are tagged with out-of-range
story IDs (ACA-16-*, ACA-17-*, etc). These need to be re-tagged with correct
IDs from the planned epic range (ACA-01 through ACA-15).

This handles:
1. # EVA-STORY: ACA-16-* tags in PowerShell files -> delete or re-assign
2. Evidence files (ACA-16-001-STORY-COMPLETION.md, etc) -> delete
3. Comments in Python files with ACA-17-* -> update to valid ID or remove
#>

param(
    [string]$RepoRoot = "c:\eva-foundry\51-ACA",
    [switch]$WhatIf = $false
)

Write-Host "=== Orphan Story Tag Cleanup ===" -ForegroundColor Cyan
Write-Host "Repository: $RepoRoot"
Write-Host "WhatIf Mode: $WhatIf"
Write-Host ""

# Files and IDs to remove/clean
$orphanFiles = @(
    "evidence\ACA-16-001-STORY-COMPLETION.md",
    "evidence\ACA-16-002-STORY-COMPLETION.md",
    "evidence\ACA-16-003-STORY-COMPLETION.md",
    "evidence\ACA-16-004-STORY-COMPLETION.md"
)

# Source code files with incorrect story tags (to remove)
# Note: These files are tagged with out-of-range IDs (ACA-16-*, ACA-17-*)
# but need manual re-tagging to correct ACA-15-* story IDs after review
$filesToClean = @(
    "infra\container-apps-job\scripts\sync-orchestration-job.ps1",
    "infra\container-apps-job\scripts\Invoke-With-Retry.ps1",
    "infra\container-apps-job\scripts\Health-Diagnostics.ps1",
    "infra\container-apps-job\scripts\Circuit-Breaker.ps1",
    "infra\container-apps-job\scripts\Checkpoint-Resume.ps1",
    "infra\container-apps-job\scripts\Invoke-SyncAdvisor.ps1",
    "infra\container-apps-job\scripts\Invoke-WorkflowOrchestration.ps1",
    "agents\orchestrator-workflow\orchestrator_workflow.py",
    "agents\orchestrator-workflow\test_orchestrator_workflow.py",
    "agents\sync-advisor\advisor_agent.py",
    "agents\sync-advisor\test_advisor_agent.py"
)

$removedCount = 0
$fixedCount = 0
$failureCount = 0

# Step 1: Delete orphan evidence files
Write-Host "Deleting orphan evidence files..." -ForegroundColor Yellow
foreach ($orphanFile in $orphanFiles) {
    $fullPath = Join-Path $RepoRoot $orphanFile
    if (Test-Path $fullPath) {
        if ($WhatIf) {
            Write-Host "  [WhatIf] DELETE $orphanFile" -ForegroundColor Cyan
        } else {
            try {
                Remove-Item -Path $fullPath -Force
                Write-Host "  [DELETED] $orphanFile" -ForegroundColor Green
                $removedCount++
            } catch {
                Write-Host "  [ERROR] Failed to delete $orphanFile : $_" -ForegroundColor Red
                $failureCount++
            }
        }
    } else {
        Write-Host "  [SKIP] $orphanFile (not found)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Removing orphan story ID tags from source files..." -ForegroundColor Yellow
foreach ($file in $filesToClean) {
    $fullPath = Join-Path $RepoRoot $file
    if (Test-Path $fullPath) {
        $content = Get-Content -Path $fullPath -Raw
        # Remove any # EVA-STORY: ACA-16-* or ACA-17-* lines
        $pattern = '# EVA-STORY: ACA-(16|17)-[0-9a-z]+'
        
        if ($content -match $pattern) {
            if ($WhatIf) {
                Write-Host "  [WhatIf] REMOVE EVA-STORY tag from $file" -ForegroundColor Cyan
            } else {
                try {
                    $newContent = $content -replace "^.*$pattern.*`r?`n", ""
                    Set-Content -Path $fullPath -Value $newContent -Force
                    Write-Host "  [CLEANED] $file (orphan tag removed)" -ForegroundColor Green
                    $fixedCount++
                } catch {
                    Write-Host "  [ERROR] Failed to clean $file : $_" -ForegroundColor Red
                    $failureCount++
                }
            }
        } else {
            Write-Host "  [SKIP] $file (no orphan tag found)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [SKIP] $file (file not found)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Evidence files deleted: $removedCount"
Write-Host "Story tags updated: $fixedCount"
if ($failureCount -gt 0) {
    Write-Host "Failures: $failureCount" -ForegroundColor Red
}
Write-Host ""

if ($WhatIf) {
    Write-Host "[INFO] WhatIf mode - no actual changes made." -ForegroundColor Cyan
    Write-Host "Run without -WhatIf to execute cleanup:" -ForegroundColor Gray
    Write-Host "  .\cleanup-orphan-tags.ps1" -ForegroundColor Gray
} else {
    Write-Host "[OK] Orphan story tags cleaned up." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Run Veritas audit to confirm cleanup:" -ForegroundColor Gray
    Write-Host "  node C:\eva-foundry\48-eva-veritas\src\cli.js audit --repo ." -ForegroundColor Gray
}
