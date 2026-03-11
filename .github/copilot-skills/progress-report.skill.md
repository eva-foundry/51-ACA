# Skill: progress-report
# EVA-STORY: ACA-12-025

**Version**: 1.0.0
**Project**: 51-ACA
**Triggers**: progress report, project status, where are we, epic status, test count, recent commits

---

## PURPOSE

Replace STATUS.md as queryable progress snapshot. This skill generates a comprehensive
project status report by querying:
1. Data model (WBS layer)
2. Veritas audit (MTI, test count)
3. Git log (recent commits with story IDs)

The report answers: "Where are we right now?"

---

## CAPABILITIES

### 1. Epic Completion Percentages
Calculate done stories / total stories per epic.
Display completion bar chart (ASCII art or HTML progress bar).

### 2. Phase 1 Readiness Score
Check if all stories with milestone="M1.0" are status="done".
Report: READY / BLOCKED / percentage complete.

### 3. Recent Commits with Story IDs
Parse last 10 commits, extract ACA-NN-NNN story IDs from commit messages.
Link commits to WBS records (show story label + epic).

### 4. Test Count Trend
Extract test count from veritas trust.json (components.testCoverage.value).
Show last 5 values from session history (if tracked in data model).

### 5. Open Blockers Table
All stories with non-empty `blockers` field, grouped by epic.

### 6. Next 5 Recommended Stories
Undone stories with:
- No blocking dependencies (blockers = [])
- Sized (story_points > 0)
- Sorted by priority (epic order + story sequence)

---

## DATA SOURCES

| Source | Location | Query |
|---|---|---|
| WBS records | `/model/wbs/` | Filter by project_id="51-ACA" |
| MTI score | `.eva/trust.json` | Parse JSON, read mti field |
| Test count | `.eva/trust.json` | Parse JSON, read components.testCoverage.value |
| Git commits | `git log` | Last 10 commits, grep for ACA-NN-NNN |
| Test history | git log + grep | Extract test count from commit messages |

---

## EXECUTION WORKFLOW

### Step 1: Query all WBS records for 51-ACA

```powershell
$base = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"
$wbs = Invoke-RestMethod "$base/model/wbs/" |
    Where-Object { $_.project_id -eq "51-ACA" }

$epics = $wbs | Where-Object { $_.level -eq "epic" }
$features = $wbs | Where-Object { $_.level -eq "feature" }
$stories = $wbs | Where-Object { $_.level -eq "story" }

Write-Host "Total WBS objects: $($wbs.Count)"
Write-Host "  Epics: $($epics.Count)"
Write-Host "  Features: $($features.Count)"
Write-Host "  Stories: $($stories.Count)"
```

### Step 2: Calculate epic completion percentages

```powershell
$epic_progress = @()
foreach ($epic in $epics) {
    $epic_stories = $stories | Where-Object { $_.parent_wbs_id -match "^$($epic.id)" }
    $done_count = ($epic_stories | Where-Object { $_.status -eq "done" }).Count
    $total_count = $epic_stories.Count
    $pct = if ($total_count -gt 0) { [math]::Round($done_count / $total_count * 100, 1) } else { 0 }
    
    $epic_progress += [PSCustomObject]@{
        Epic = $epic.label
        Done = $done_count
        Total = $total_count
        Percent = $pct
    }
}

$epic_progress | Format-Table -AutoSize
```

### Step 3: Check Phase 1 (M1.0) readiness

```powershell
$m10_stories = $stories | Where-Object { $_.milestone -eq "M1.0" }
$m10_done = ($m10_stories | Where-Object { $_.status -eq "done" }).Count
$m10_total = $m10_stories.Count
$m10_pct = if ($m10_total -gt 0) { [math]::Round($m10_done / $m10_total * 100, 1) } else { 0 }

if ($m10_pct -eq 100) {
    Write-Host "[PASS] Phase 1 (M1.0) READY -- all stories done" -ForegroundColor Green
} else {
    Write-Host "[WARN] Phase 1 (M1.0) NOT READY -- $m10_pct% complete" -ForegroundColor Yellow
    $m10_undone = $m10_stories | Where-Object { $_.status -ne "done" }
    Write-Host "  Undone stories: $($m10_undone.Count)"
    $m10_undone | Select-Object -First 5 | ForEach-Object {
        Write-Host "    $($_.id) -- $($_.label) (status=$($_.status))"
    }
}
```

### Step 4: Parse recent commits for story IDs

```powershell
$repo = "C:\eva-foundry\51-ACA"
$recent_commits = git -C $repo log --oneline -10 2>&1

$story_commits = @()
$recent_commits | ForEach-Object {
    if ($_ -match '(ACA-\d{2}-\d{3})') {
        $story_id = $matches[1]
        $story = $stories | Where-Object { $_.id -eq $story_id }
        $story_commits += [PSCustomObject]@{
            Commit = $_.Substring(0, 8)
            StoryID = $story_id
            Label = if ($story) { $story.label } else { "(not in WBS)" }
            Epic = if ($story) { $story.parent_wbs_id.Substring(0, 9) } else { "N/A" }
        }
    }
}

Write-Host "`nRecent commits with story IDs:"
$story_commits | Format-Table -AutoSize
```

### Step 5: Get test count from veritas

```powershell
if (Test-Path "$repo\.eva\trust.json") {
    $trust = Get-Content "$repo\.eva\trust.json" | ConvertFrom-Json
    $test_count = $trust.components.testCoverage.value
    $mti = $trust.mti
    
    Write-Host "`nCurrent metrics:"
    Write-Host "  Test count: $test_count"
    Write-Host "  MTI score: $mti"
} else {
    Write-Host "`n[WARN] No trust.json found -- run veritas audit first"
}
```

### Step 6: List open blockers

```powershell
$blocked_stories = $stories | Where-Object { $_.blockers.Count -gt 0 }

if ($blocked_stories) {
    Write-Host "`nOpen blockers: $($blocked_stories.Count)"
    $blocked_stories | ForEach-Object {
        Write-Host "  $($_.id) -- $($_.label)"
        Write-Host "    Blocked by: $($_.blockers -join ', ')"
    }
} else {
    Write-Host "`n[PASS] No stories blocked"
}
```

### Step 7: Recommend next 5 stories

```powershell
$recommended = $stories |
    Where-Object { $_.status -ne "done" -and $_.blockers.Count -eq 0 -and $_.story_points -gt 0 } |
    Sort-Object { $_.id } |
    Select-Object -First 5

Write-Host "`nNext 5 recommended stories:"
$recommended | ForEach-Object {
    Write-Host "  $($_.id) -- $($_.label) (FP=$($_.story_points), epic=$($_.parent_wbs_id.Substring(0,9)))"
}
```

### Step 8: Generate progress report

```powershell
$report = @"
# Progress Report: 51-ACA

**Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
**Test Count**: $test_count
**MTI Score**: $mti

## Epic Completion

| Epic | Done | Total | Percent |
|------|------|-------|---------|
$(($epic_progress | ForEach-Object { "| $($_.Epic) | $($_.Done) | $($_.Total) | $($_.Percent)% |" }) -join "`n")

## Phase 1 (M1.0) Readiness

- **Status**: $(if ($m10_pct -eq 100) { "READY" } else { "NOT READY ($m10_pct% complete)" })
- **Done**: $m10_done / $m10_total stories

$(if ($m10_pct -lt 100) {
    "### Undone M1.0 Stories`n" +
    (($m10_undone | Select-Object -First 5 | ForEach-Object { "- $($_.id) -- $($_.label) (status=$($_.status))" }) -join "`n")
} else {
    ""
})

## Recent Commits (Last 10)

| Commit | Story ID | Label | Epic |
|--------|----------|-------|------|
$(($story_commits | ForEach-Object { "| $($_.Commit) | $($_.StoryID) | $($_.Label) | $($_.Epic) |" }) -join "`n")

## Open Blockers

$(if ($blocked_stories) {
    (($blocked_stories | ForEach-Object { "- **$($_.id)**: $($_.label)`n  Blocked by: $($_.blockers -join ', ')" }) -join "`n`n")
} else {
    "No stories blocked"
})

## Next 5 Recommended Stories

$(($recommended | ForEach-Object { "1. **$($_.id)** -- $($_.label) (FP=$($_.story_points))" }) -join "`n")

---
*Progress report updated. Use this instead of STATUS.md for current snapshot.*
"@

$report_path = "C:\eva-foundry\51-ACA\docs\progress-report.md"
$report | Set-Content $report_path -Encoding UTF8
Write-Host "`n[PASS] Progress report written to: $report_path"
```

---

## OUTPUT FORMATS

### 1. Markdown Report (human-readable)
- Saved to: `docs/progress-report.md`
- Contains: Epic completion table, M1.0 readiness, recent commits, blockers, next stories

### 2. JSON Artifact (machine-readable)
```json
{
  "generated": "2026-02-28T18:45:00Z",
  "test_count": 27,
  "mti": 30,
  "epic_progress": [
    {"epic": "Epic 1", "done": 12, "total": 15, "percent": 80.0}
  ],
  "m10_readiness": {
    "status": "NOT_READY",
    "done": 85,
    "total": 120,
    "percent": 70.8
  },
  "blockers": [
    {"story_id": "ACA-04-009", "blocked_by": ["ACA-02-003"]}
  ],
  "recommended": [
    {"story_id": "ACA-04-010", "fp": 3}
  ]
}
```

### 3. HTML Dashboard (optional)
- Served via GitHub Pages or local HTTP server
- Live charts: epic completion pie, MTI trend line, test count bar
- Auto-refresh every 5 minutes via JavaScript

---

## INTEGRATION WITH STATUS.MD

This skill **replaces** manual STATUS.md updates. Workflow:

1. Developer makes change (implements story)
2. Developer commits with story ID in message
3. Developer posts "progress report" to Copilot
4. This skill runs, generates `docs/progress-report.md`
5. Optional: Copy progress-report.md content to STATUS.md for legacy compatibility

---

## EXAMPLE USAGE

**Copilot prompt:**
```
progress report
```

**Expected output:**
1. Query WBS for 324 objects (14 epics, 54 features, 256 stories)
2. Calculate epic completion (Epic 1: 80%, Epic 2: 60%, Epic 3: 45%, ...)
3. Check M1.0 readiness (70.8% complete, 35 FP remaining)
4. Parse last 10 commits (find 7 with story IDs)
5. Get test count from veritas (27 tests, MTI=30)
6. List open blockers (2 stories blocked)
7. Recommend next 5 stories
8. Generate markdown report at `docs/progress-report.md`
9. Display summary in chat

---

## ERROR HANDLING

| Error | Cause | Recovery |
|---|---|---|
| No WBS records | Data model not seeded | Run seed-from-plan.py first |
| No trust.json | Never ran veritas audit | Show "N/A" for MTI/test count |
| Git log fails | Not in git repo | Skip recent commits section |
| Percentage overflow | Division by zero (epic with 0 stories) | Guard with `if ($total -gt 0)` |

---

## DEPENDENCIES

- Data model API: `https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io`
- Veritas trust.json: `.eva/trust.json` (optional)
- Git CLI: `git log` (optional)
- PowerShell 7+

---

## MAINTENANCE

Update this skill when:
- WBS schema changes (new fields, status values)
- Milestone definitions change (M1.0 -> Phase 1 MVP)
- Test count tracking moves from veritas to separate system
- Report format requirements change (new sections, different metrics)
