#!/usr/bin/env pwsh
# Generate Sprint 2 GitHub Issue Body
# Uses CLOUD data model only (no local db)

$base = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"

Write-Host "[INFO] Querying cloud data model for Sprint 2 stories..." -ForegroundColor Cyan

# Get all Sprint 2 stories from cloud
$stories = Invoke-RestMethod "$base/model/wbs/" | Where-Object { 
    $_.sprint_id -eq "Sprint-02" -and $_.is_active 
}

Write-Host "[PASS] Found $($stories.Count) stories" -ForegroundColor Green
Write-Host ""

# Build issue body
$issueBody = @"
## Sprint 2 -- Analysis Rules (15 Stories)

**Goal**: Implement Epic 3 analysis rules (12 saving opportunity detectors) + GB-02/GB-03 infrastructure fixes

**Duration**: 2026-02-28 to 2026-03-10 (11 days)

**Velocity**: 15 stories

**Critical Dependencies**:
- GB-02: Analysis auto-trigger
- GB-03: Resource Graph pagination for large subscriptions
- 12 rules from Epic 03

---

### Stories (15)

"@

# Add each story
foreach ($story in $stories | Sort-Object id) {
    $issueBody += @"

#### $($story.id) -- $($story.label)

- **ADO**: #$($story.ado_id)
- **Status**: $($story.status)
- **Points**: $($story.story_points)
- **Owner**: $($story.owner)

"@
}

$issueBody += @"

---

### Execution Notes

This sprint will be executed by the Sprint Agent workflow (`.github/workflows/sprint-agent.yml`). The workflow will:

1. Parse this issue body
2. Execute each story in sequence: D->P->D->C->A
3. Post progress comments after each story
4. Create PRs with AB#N tags linking to ADO work items
5. Post final sprint summary

**Monitor**: https://github.com/eva-foundry/51-ACA/actions

---

**Data Source**: Cloud data model (ACA 24x7)
**Linked Iteration**: 51-aca\Sprint 2

"@

# Write to file
$issueBody | Out-File -FilePath "sprint2-issue-body.md" -Encoding UTF8

Write-Host "[PASS] Issue body written to: sprint2-issue-body.md" -ForegroundColor Green
Write-Host ""
Write-Host "Next: gh issue create --repo eva-foundry/51-ACA --title 'Sprint 2 -- Analysis Rules' --body-file sprint2-issue-body.md --label sprint-task"
