# Skill: gap-report
# EVA-STORY: ACA-12-024

**Version**: 1.0.0
**Project**: 51-ACA
**Triggers**: gap report, what's missing, blockers, critical path, missing evidence, orphan tags

---

## PURPOSE

Identify gaps blocking next sprint or milestone. This skill produces a prioritized list of:
1. Critical blockers (stories blocking milestone with status != done)
2. Missing evidence (stories marked done with no evidence receipt)
3. Orphan tags (EVA-STORY tags not in veritas-plan.json)
4. Dependency chains (story -> blocking stories -> transitive closure)
5. Estimate to milestone (sum FP of all undone stories on critical path)

---

## CAPABILITIES

### 1. Critical Blockers Analysis
Query WBS for stories with status != "done" that appear in other stories' `blockers` field.
Build blocking graph: story A blocks story B if A appears in B's blockers array.

### 2. Missing Evidence Detection
Cross-reference WBS (status="done") with veritas gaps (missing_evidence, missing_implementation).
Any story marked done without >= 1 EVA-STORY tag = RED FLAG.

### 3. Orphan Tag Detection
Compare veritas artifact scan (all EVA-STORY tags found in repo) with veritas-plan.json (all valid story IDs).
Tags referencing non-existent stories = technical debt (remove or fix ID).

### 4. Dependency Chain Tracing
Given a target story, find all stories it depends on (transitive closure via blockers field).
Calculate aggregate FP to unblock target (sum story_points of all dependencies).

### 5. Estimate to Milestone
Given milestone ID (e.g. M1.0 = Phase 1 MVP), find all stories with milestone=M1.0 and status != done.
Sum story_points to get remaining effort (FP) to complete milestone.

---

## DATA SOURCES

| Source | API Endpoint | Fields Used |
|---|---|---|
| WBS layer | `/model/wbs/` | id, status, blockers, milestone, story_points |
| Veritas gaps | `.eva/reconciliation.json` | gaps[].type, gaps[].story_id, gaps[].count |
| Veritas artifacts | `.eva/artifacts.json` | artifacts[].story_id, artifacts[].file_path |
| Veritas plan | `.eva/veritas-plan.json` | features[].stories[].id |

---

## EXECUTION WORKFLOW

### Step 1: Query WBS for undone stories with blockers

```powershell
$base = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"
$wbs = Invoke-RestMethod "$base/model/wbs/" |
    Where-Object { $_.project_id -eq "51-ACA" -and $_.level -eq "story" }

# Find all stories that are blocking others
$all_blockers = $wbs | Where-Object { $_.blockers.Count -gt 0 } |
    ForEach-Object { $_.blockers } | Select-Object -Unique

# Filter to blockers that are NOT yet done
$critical_blockers = $wbs | Where-Object { $_.id -in $all_blockers -and $_.status -ne "done" }

Write-Host "[INFO] Critical blockers found: $($critical_blockers.Count)"
$critical_blockers | ForEach-Object {
    $blocking_count = ($wbs | Where-Object { $_.blockers -contains $_.id }).Count
    Write-Host "  $($_.id) -- $($_.label) (blocks $blocking_count stories, status=$($_.status))"
}
```

### Step 2: Check for missing evidence on done stories

```powershell
$repo = "C:\AICOE\eva-foundry\51-ACA"
node C:\AICOE\eva-foundry\48-eva-veritas\src\cli.js reconcile --repo $repo 2>&1 | Out-Null

$reconciliation = Get-Content "$repo\.eva\reconciliation.json" | ConvertFrom-Json
$missing_evidence_gaps = $reconciliation.gaps | Where-Object { $_.type -eq "missing_evidence" }

if ($missing_evidence_gaps) {
    Write-Host "`n[WARN] Missing evidence gaps: $($missing_evidence_gaps.Count)"
    $missing_evidence_gaps | ForEach-Object {
        Write-Host "  $($_.story_id) -- marked done but no evidence receipt"
    }
} else {
    Write-Host "`n[PASS] No missing evidence gaps"
}
```

### Step 3: Detect orphan tags

```powershell
$artifacts = Get-Content "$repo\.eva\artifacts.json" | ConvertFrom-Json
$plan = Get-Content "$repo\.eva\veritas-plan.json" | ConvertFrom-Json

# Extract all valid story IDs from plan
$valid_ids = $plan.features | ForEach-Object { $_.stories | ForEach-Object { $_.id } }

# Find artifacts with story IDs not in plan
$orphan_tags = $artifacts.artifacts | Where-Object { $_.story_id -notin $valid_ids }

if ($orphan_tags) {
    Write-Host "`n[WARN] Orphan tags found: $($orphan_tags.Count)"
    $orphan_tags | ForEach-Object {
        Write-Host "  $($_.file_path) -- references $($_.story_id) (not in plan)"
    }
} else {
    Write-Host "`n[PASS] No orphan tags"
}
```

### Step 4: Build dependency chain for target story

```powershell
function Get-DependencyChain {
    param([string]$StoryId, [array]$AllStories)
    
    $story = $AllStories | Where-Object { $_.id -eq $StoryId }
    if (-not $story) { return @() }
    
    $chain = @($story)
    foreach ($blocker_id in $story.blockers) {
        $blocker_chain = Get-DependencyChain -StoryId $blocker_id -AllStories $AllStories
        $chain += $blocker_chain
    }
    
    return $chain | Select-Object -Unique
}

$target_story = "ACA-04-009"
$dependency_chain = Get-DependencyChain -StoryId $target_story -AllStories $wbs

Write-Host "`nDependency chain for $target_story"
$dependency_chain | ForEach-Object {
    Write-Host "  $($_.id) -- $($_.label) (status=$($_.status), FP=$($_.story_points))"
}

$total_fp = ($dependency_chain | Measure-Object -Property story_points -Sum).Sum
Write-Host "Total FP to unblock $target_story $total_fp"
```

### Step 5: Calculate estimate to milestone

```powershell
$milestone = "M1.0"
$milestone_stories = $wbs | Where-Object { $_.milestone -eq $milestone }
$undone_milestone_stories = $milestone_stories | Where-Object { $_.status -ne "done" }

$remaining_fp = ($undone_milestone_stories | Measure-Object -Property story_points -Sum).Sum
$total_fp = ($milestone_stories | Measure-Object -Property story_points -Sum).Sum
$done_fp = $total_fp - $remaining_fp
$completion_pct = [math]::Round($done_fp / $total_fp * 100, 1)

Write-Host "`nMilestone: $milestone"
Write-Host "  Total FP: $total_fp"
Write-Host "  Done FP: $done_fp ($completion_pct%)"
Write-Host "  Remaining FP: $remaining_fp"
Write-Host "  Undone stories: $($undone_milestone_stories.Count)"
```

### Step 6: Generate gap report

```powershell
$report = @"
# Gap Report: 51-ACA

**Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')

## 1. Critical Blockers

$(if ($critical_blockers) {
    "| Story ID | Status | FP | Blocks Count |`n|----------|--------|----|----|`n" +
    (($critical_blockers | ForEach-Object {
        $blocking_count = ($wbs | Where-Object { $_.blockers -contains $_.id }).Count
        "| $($_.id) | $($_.status) | $($_.story_points) | $blocking_count |"
    }) -join "`n")
} else {
    "No critical blockers"
})

## 2. Missing Evidence

$(if ($missing_evidence_gaps) {
    (($missing_evidence_gaps | ForEach-Object { "- $($_.story_id) -- marked done but no evidence receipt" }) -join "`n")
} else {
    "No missing evidence"
})

## 3. Orphan Tags

$(if ($orphan_tags) {
    (($orphan_tags | ForEach-Object { "- $($_.file_path) -- references $($_.story_id) (not in plan)" }) -join "`n")
} else {
    "No orphan tags"
})

## 4. Milestone Progress: M1.0

| Metric | Value |
|--------|-------|
| Total FP | $total_fp |
| Done FP | $done_fp ($completion_pct%) |
| Remaining FP | $remaining_fp |
| Undone Stories | $($undone_milestone_stories.Count) |

### Undone Stories for M1.0

$(($undone_milestone_stories | ForEach-Object { "- $($_.id) -- $($_.label) (FP=$($_.story_points), status=$($_.status))" }) -join "`n")

---
*Gap report complete. Fix critical blockers before advancing to next sprint.*
"@

$report_path = "C:\AICOE\eva-foundry\51-ACA\docs\gap-report.md"
$report | Set-Content $report_path -Encoding UTF8
Write-Host "`n[PASS] Gap report written to: $report_path"
```

---

## OUTPUT FORMATS

### 1. Markdown Report (human-readable)
- Saved to: `docs/gap-report.md`
- Contains: Critical blockers table, missing evidence list, orphan tags, milestone progress

### 2. JSON Artifact (machine-readable)
```json
{
  "critical_blockers": [
    {"story_id": "ACA-02-001", "status": "in_progress", "blocks_count": 3}
  ],
  "missing_evidence": [
    {"story_id": "ACA-03-007", "status": "done", "evidence_count": 0}
  ],
  "orphan_tags": [
    {"file": "services/api/app/main.py", "story_id": "ACA-99-999"}
  ],
  "milestone_progress": {
    "milestone": "M1.0",
    "total_fp": 120,
    "done_fp": 85,
    "remaining_fp": 35,
    "completion_pct": 70.8
  }
}
```

---

## INTEGRATION WITH SPRINT-ADVANCE

This skill is invoked in sprint-advance.skill.md Phase 2 (Audit):

```powershell
# After veritas reconcile completes:
# Trigger: "gap report" or "what's missing"
# This skill runs and produces:
#   1. docs/gap-report.md
#   2. .eva/gaps.json (for automated fix script)
```

---

## REMEDIATION STEPS

| Gap Type | Automated Fix | Manual Fix Required |
|---|---|---|
| Critical blocker | Cannot automate (requires implementing story) | Prioritize blocker in next sprint |
| Missing evidence | Add `# EVA-STORY: ACA-NN-NNN` to test file | Write evidence receipt in `.eva/evidence/` |
| Orphan tag | Remove tag or fix ID in source file | Code review + PR |
| Dependency chain | Cannot automate (requires story sequence) | Plan sprint with dependencies first |
| Milestone overage | Cannot automate (requires descoping) | Product owner decision |

---

## EXAMPLE USAGE

**Copilot prompt:**
```
gap report for milestone M1.0
```

**Expected output:**
1. Query WBS for critical blockers
2. Run veritas reconcile to find missing evidence
3. Scan artifacts for orphan tags
4. Calculate milestone M1.0 completion (70.8% done, 35 FP remaining)
5. Generate markdown report at `docs/gap-report.md`
6. Display summary in chat with top 3 action items

---

## ERROR HANDLING

| Error | Cause | Recovery |
|---|---|---|
| No WBS records | Data model not seeded | Run seed-from-plan.py first |
| Veritas files missing | Never ran veritas audit | Run `audit --repo .` before gap-report |
| Circular dependency | Story A blocks B, B blocks A | Manual fix required (break cycle) |
| Milestone not found | Invalid milestone ID | List available milestones from WBS |

---

## DEPENDENCIES

- Data model API: `https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io`
- Veritas CLI: `C:\AICOE\eva-foundry\48-eva-veritas\src\cli.js`
- PowerShell 7+ with ConvertFrom-Json support

---

## MAINTENANCE

Update this skill when:
- WBS schema changes (new blocker format, milestone field rename)
- Veritas gap types change (new gap categories added)
- Remediation workflows change (new automated fix scripts)
