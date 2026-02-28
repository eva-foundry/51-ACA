# Skill: sprint-report
# EVA-STORY: ACA-12-023

**Version**: 1.0.0
**Project**: 51-ACA
**Triggers**: sprint report, sprint summary, velocity, sprint metrics, sprint dashboard, show sprint

---

## PURPOSE

Generate comprehensive sprint summary reports from data model queries. This skill replaces
manual STATUS.md updates with queryable metrics from sprints layer + WBS layer + veritas audit.

---

## CAPABILITIES

1. **Sprint velocity chart** - Planned vs actual FP delivered
2. **Story completion table** - Done/in-progress/blocked breakdown
3. **MTI trend** - Current sprint vs prior 3 sprints
4. **Blocker list** - All stories with non-empty blockers field
5. **Test coverage delta** - Test count at sprint start vs close

---

## DATA SOURCES

| Source | Layer | Query |
|---|---|---|
| Sprint records | `/model/sprints/` | Filter by project_id="51-ACA" |
| Story status | `/model/wbs/` | Filter by sprint_id + level="story" |
| MTI scores | veritas audit output | `.eva/trust.json` per sprint |
| Test counts | git log + pytest | Parse from commit messages |

---

## EXECUTION WORKFLOW

### Step 1: Query sprint record

```powershell
$base = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"
$sprint_id = "51-ACA-sprint-02"
$sprint = Invoke-RestMethod "$base/model/sprints/$sprint_id"

Write-Host "Sprint: $($sprint.label)"
Write-Host "Status: $($sprint.status)"
Write-Host "Started: $($sprint.started_at)"
Write-Host "Completed: $($sprint.completed_at)"
```

### Step 2: Query all stories for this sprint

```powershell
$stories = Invoke-RestMethod "$base/model/wbs/" |
    Where-Object { $_.sprint_id -eq $sprint_id -and $_.level -eq "story" }

$total = $stories.Count
$done = ($stories | Where-Object { $_.status -eq "done" }).Count
$in_progress = ($stories | Where-Object { $_.status -eq "in_progress" }).Count
$blocked = ($stories | Where-Object { $_.blockers.Count -gt 0 }).Count

Write-Host "Stories: $done done / $total total ($([math]::Round($done/$total*100))%)"
Write-Host "In Progress: $in_progress"
Write-Host "Blocked: $blocked"
```

### Step 3: Calculate velocity

```powershell
$planned_fp = ($stories | Measure-Object -Property story_points -Sum).Sum
$delivered_fp = ($stories | Where-Object { $_.status -eq "done" } |
    Measure-Object -Property story_points -Sum).Sum

$velocity = if ($sprint.completed_at -and $sprint.started_at) {
    $start = [datetime]::Parse($sprint.started_at)
    $end = [datetime]::Parse($sprint.completed_at)
    $days = ($end - $start).TotalDays
    if ($days -gt 0) { $delivered_fp / $days } else { 0 }
} else { 0 }

Write-Host "Planned FP: $planned_fp"
Write-Host "Delivered FP: $delivered_fp"
Write-Host "Velocity: $([math]::Round($velocity, 2)) FP/day"
```

### Step 4: Get MTI trend (last 4 sprints)

```powershell
$all_sprints = Invoke-RestMethod "$base/model/sprints/" |
    Where-Object { $_.project_id -eq "51-ACA" -and $_.id -ne "51-ACA-sprint-backlog" } |
    Sort-Object id -Descending | Select-Object -First 4

$mti_trend = @()
foreach ($s in $all_sprints) {
    $mti = if ($s.mti_at_close) { $s.mti_at_close } else { "N/A" }
    $mti_trend += "$($s.label): MTI=$mti"
}

Write-Host "`nMTI Trend (last 4 sprints):"
$mti_trend | ForEach-Object { Write-Host "  $_" }
```

### Step 5: List blockers

```powershell
$blocked_stories = $stories | Where-Object { $_.blockers.Count -gt 0 }

if ($blocked_stories) {
    Write-Host "`nBlocked Stories:"
    $blocked_stories | ForEach-Object {
        Write-Host "  $($_.id) -- $($_.label)"
        Write-Host "    Blockers: $($_.blockers -join ', ')"
    }
} else {
    Write-Host "`nNo blocked stories"
}
```

### Step 6: Generate markdown report

```powershell
$report = @"
# Sprint Report: $($sprint.label)

**Status**: $($sprint.status)
**Duration**: $(if ($sprint.started_at) { $sprint.started_at }) to $(if ($sprint.completed_at) { $sprint.completed_at } else { 'In Progress' })

## Metrics

| Metric | Value |
|--------|-------|
| Total Stories | $total |
| Done | $done ($([math]::Round($done/$total*100))%) |
| In Progress | $in_progress |
| Blocked | $blocked |
| Planned FP | $planned_fp |
| Delivered FP | $delivered_fp |
| Velocity | $([math]::Round($velocity, 2)) FP/day |

## MTI Trend

$($mti_trend -join "`n")

## Story Breakdown

| Story ID | Status | FP | Blockers |
|----------|--------|----|----|
$(($stories | ForEach-Object { "| $($_.id) | $($_.status) | $($_.story_points) | $($_.blockers -join ', ') |" }) -join "`n")

## Blockers

$(if ($blocked_stories) {
    ($blocked_stories | ForEach-Object { "- **$($_.id)**: $($_.blockers -join ', ')" }) -join "`n"
} else {
    "No blockers"
})

---
*Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')*
"@

$report_path = "C:\AICOE\eva-foundry\51-ACA\docs\sprint-report-$sprint_id.md"
$report | Set-Content $report_path -Encoding UTF8
Write-Host "`n[PASS] Sprint report written to: $report_path"
```

---

## OUTPUT FORMATS

### 1. Markdown Report (human-readable)
- Saved to: `docs/sprint-report-{sprint-id}.md`
- Contains: Metrics table, MTI trend, story breakdown, blockers

### 2. JSON Artifact (machine-readable)
```json
{
  "sprint_id": "51-ACA-sprint-02",
  "status": "completed",
  "metrics": {
    "total_stories": 15,
    "done": 15,
    "in_progress": 0,
    "blocked": 0,
    "planned_fp": 18,
    "delivered_fp": 18,
    "velocity": 1.36
  },
  "mti_trend": [
    {"sprint": "Sprint 3", "mti": 30},
    {"sprint": "Sprint 2", "mti": 100},
    {"sprint": "Sprint 1", "mti": null}
  ],
  "blockers": []
}
```

---

## INTEGRATION WITH SPRINT-ADVANCE

This skill is invoked automatically in sprint-advance.skill.md Phase 5:

```powershell
# After sprint manifest is created, generate report
node C:\AICOE\eva-foundry\48-eva-veritas\src\cli.js audit --repo . --warn-only

# Trigger: "sprint report" or "generate sprint summary"
# This skill runs and produces:
#   1. docs/sprint-report-51-ACA-sprint-NN.md
#   2. .eva/sprint-NN-summary.json (for ADO dashboard)
```

---

## EXAMPLE USAGE

**Copilot prompt:**
```
sprint report for sprint 2
```

**Expected output:**
1. Query data model for sprint-02 record
2. Query all stories with sprint_id="51-ACA-sprint-02"
3. Calculate metrics (velocity, completion %, blockers)
4. Query MTI from veritas audit
5. Generate markdown report at `docs/sprint-report-51-ACA-sprint-02.md`
6. Display summary in chat

---

## ERROR HANDLING

| Error | Cause | Recovery |
|---|---|---|
| 404 on sprint record | Sprint ID not in data model | List available sprints, prompt for correct ID |
| 0 stories returned | Wrong sprint_id filter | Check sprint_id format (must match "51-ACA-sprint-NN") |
| MTI unavailable | No .eva/trust.json | Show "N/A" in report, recommend running veritas audit |
| Velocity = 0 | Sprint not completed | Show planned metrics only, mark report as "in-progress" |

---

## DEPENDENCIES

- Data model API: `https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io`
- Veritas CLI: `C:\AICOE\eva-foundry\48-eva-veritas\src\cli.js`
- PowerShell 7+

---

## MAINTENANCE

Update this skill when:
- Sprint schema changes (new fields added to sprints layer)
- WBS schema changes (new status values, blockers format)
- Report format requirements change (new metrics, different layout)
