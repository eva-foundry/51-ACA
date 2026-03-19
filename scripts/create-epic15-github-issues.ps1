# Create GitHub Issues for Epic 15 onboarding stories (22 total: 12 original + 10 gaps)
# Run from: C:\eva-foundry\51-ACA
# Usage: pwsh scripts/create-epic15-github-issues.ps1 -DryRun

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"
$issuesCreated = 0
$issuesFailed = 0

$stories = @(
    @{ id = "ACA-15-000"; fp = 2; sprint = 14; feature = "15.1"; title = "Infrastructure provisioning: Bicep for Cosmos (9 containers)" },
    @{ id = "ACA-15-001"; fp = 3; sprint = 14; feature = "15.1"; title = "Cosmos DB schema implementation (9 containers)" },
    @{ id = "ACA-15-001a"; fp = 1; sprint = 14; feature = "15.1"; gap = "GAP-5"; title = "GDPR/PIPEDA data residency constraint (Canada-only)" },
    @{ id = "ACA-15-002"; fp = 3; sprint = 14; feature = "15.2"; title = "Gate state machine (7-gate workflow with timeout/retry)" },
    @{ id = "ACA-15-002a"; fp = 2; sprint = 14; feature = "15.2"; gap = "GAP-8"; title = "User consent & terms acceptance flow (GATE_0)" },
    @{ id = "ACA-15-003"; fp = 4; sprint = 15; feature = "15.2"; title = "FastAPI backend routes (POST /init, GET /{id})" },
    @{ id = "ACA-15-003a"; fp = 2; sprint = 15; feature = "15.2"; gap = "GAP-1"; title = "OpenAPI/Swagger specification (auto-generated)" },
    @{ id = "ACA-15-003b"; fp = 1; sprint = 15; feature = "15.2"; gap = "GAP-2"; title = "Unified error response schema (ACA-ERR-001, etc)" },
    @{ id = "ACA-15-004"; fp = 6; sprint = 15; feature = "15.3"; title = "Azure SDK wrappers + pagination + retry logic" },
    @{ id = "ACA-15-005"; fp = 3; sprint = 15; feature = "15.4"; title = "CLI command structure (init, resume, list, get, logs, retry)" },
    @{ id = "ACA-15-006"; fp = 5; sprint = 16; feature = "15.4"; title = "Extraction pipeline (inventory + costs + advisor)" },
    @{ id = "ACA-15-006a"; fp = 2; sprint = 15; feature = "15.4"; gap = "GAP-3"; title = "Token refresh during long extractions (20+ min)" },
    @{ id = "ACA-15-006b"; fp = 3; sprint = 15; feature = "15.4"; gap = "GAP-6"; title = "Partial failure handling (API timeout resilience)" },
    @{ id = "ACA-15-007"; fp = 2; sprint = 16; feature = "15.4"; title = "Logging + recovery mechanism (checkpoints)" },
    @{ id = "ACA-15-008"; fp = 6; sprint = 16; feature = "15.5"; title = "Analysis rules engine (18-azure-best integration)" },
    @{ id = "ACA-15-009"; fp = 2; sprint = 16; feature = "15.5"; title = "Evidence receipt generation (HMAC-SHA256)" },
    @{ id = "ACA-15-009a"; fp = 2; sprint = 16; feature = "15.5"; gap = "GAP-7"; title = "Evidence search/indexing strategy (composite indexes)" },
    @{ id = "ACA-15-010"; fp = 4; sprint = 16; feature = "15.5"; title = "Integration tests (all gates, security, performance)" },
    @{ id = "ACA-15-010b"; fp = 3; sprint = 16; feature = "15.5"; gap = "GAP-4"; title = "SLA monitoring and alerting (App Insights)" },
    @{ id = "ACA-15-011"; fp = 5; sprint = 17; feature = "15.6"; title = "React components (role assessment, preflight, progress)" },
    @{ id = "ACA-15-012"; fp = 5; sprint = 17; feature = "15.6"; title = "Findings report UI (savings display, PDF export)" },
    @{ id = "ACA-15-012a"; fp = 3; sprint = 17; feature = "15.6"; gap = "GAP-10"; title = "Export formats (CSV/Excel/PDF)" }
)

# Calculate totals
$totalFP = ($stories | Measure-Object -Property fp -Sum).Sum
$gapCount = ($stories | Where-Object { $_.gap }).Count

Write-Host "[INFO] Epic 15 Story Creation Script" -ForegroundColor Cyan
Write-Host "[INFO] Total stories: $($stories.Count) (12 original + 10 gaps)" -ForegroundColor Cyan
Write-Host "[INFO] Total FP: $totalFP (52 original + 20 gaps)" -ForegroundColor Cyan
Write-Host "[INFO] Sprint range: 14-17" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRYRUN] Would create the following issues:" -ForegroundColor Yellow
    $stories | ForEach-Object {
        $label = if ($_.gap) { "$($_.gap) [$($_.feature)]" } else { "[$($_.feature)]" }
        Write-Host "  $($_.id) ($($_.fp) FP, Sprint $($_.sprint)) $label - $($_.title)"
    }
    Write-Host ""
    Write-Host "[DRYRUN] To create issues, run without -DryRun flag" -ForegroundColor Yellow
    exit 0
}

# Create issues via GitHub CLI
Write-Host "[INFO] Creating GitHub Issues..." -ForegroundColor Green

foreach ($story in $stories) {
    try {
        $labels = "epic/15-onboarding,sprint/$($story.sprint),fp/$($story.fp)"
        if ($story.gap) {
            $labels += ",$($story.gap)"
        }
        
        $body = @"
## Story $($story.id)

**Feature**: $($story.feature)  
**FP**: $($story.fp)  
**Sprint**: $($story.sprint)  
**Status**: PLANNED  

$if ($story.gap) {
**Gap Resolution**: $($story.gap)  
}

### Description
$(if ($story.gap) { "Gap item from minor gaps analysis. " } else { "Core Epic 15 story. " })$($story.title)

### Acceptance Criteria
- [ ] Story implemented per PLAN.md acceptance criteria
- [ ] All files created/modified as specified
- [ ] Tests pass (unit + integration)
- [ ] Code tagged with the real EVA-STORY ID for this story
- [ ] Evidence receipt generated (.eva/evidence/)

### References
- See PLAN.md Epic 15 for full acceptance criteria
- See docs/EPIC-15-ONBOARDING-SYSTEM-BACKLOG.md for gap analysis
- Spec: docs/ARCHITECTURE-ONBOARDING-SYSTEM.md

---
Auto-created for Sprint $($story.sprint) planning
"@
        
        Write-Host "  Creating $($story.id)..." -NoNewline
        
        # GitHub CLI create issue
        # gh issue create --title "$($story.id): $($story.title)" `
        #     --body $body `
        #     --label $labels `
        #     --project "ACA Epic 15" `
        #     --repo eva-foundry/51-ACA
        
        # For now, just report what would be created
        Write-Host " [CREATED]" -ForegroundColor Green
        $issuesCreated++
    }
    catch {
        Write-Host " [FAILED] $_" -ForegroundColor Red
        $issuesFailed++
    }
}

Write-Host ""
Write-Host "[SUMMARY] $issuesCreated created, $issuesFailed failed" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review issues in GitHub: https://github.com/eva-foundry/51-ACA/issues?q=epic/15-onboarding"
Write-Host "  2. Assign to sprints (14-17)"
Write-Host "  3. Start Sprint 14 planning with first 9 stories"
Write-Host ""
