# rebuild-veritas-plan.ps1
# Rebuilds .eva/veritas-plan.json from .eva/model-export.json
# F12.4.4 fix: restore correct 15 epic / 281 story structure after bad generate-plan run

param(
    [string]$RepoPath = "C:\eva-foundry\51-ACA"
)

$exportPath = Join-Path $RepoPath ".eva\model-export.json"
$planPath   = Join-Path $RepoPath ".eva\veritas-plan.json"

$me = Get-Content $exportPath | ConvertFrom-Json
$features_raw = $me.wbs | Where-Object { $_.level -eq 'feature' }
$stories_raw  = $me.wbs | Where-Object { $_.level -eq 'user_story' }

Write-Host "[INFO] Loaded $($features_raw.Count) features, $($stories_raw.Count) stories"

$planFeatures = foreach ($f in $features_raw) {
    $fStories = $stories_raw | Where-Object { $_.parent_wbs_id -eq $f.id }
    $storyObjs = foreach ($s in $fStories) {
        [ordered]@{
            id         = if ($s.original_story_id) { $s.original_story_id } else { $s.id }
            wbs_id     = $s.id
            title      = $s.label
            feature_id = $f.id
            done       = ($s.status -eq 'done')
            source     = 'model-export'
            tasks      = @()
        }
    }
    [ordered]@{
        id             = $f.id
        title          = $f.label
        source_heading = "Feature: $($f.label) [$($f.id)]"
        stories        = @($storyObjs)
    }
}

$totalStories = ($planFeatures | ForEach-Object { $_.stories.Count } | Measure-Object -Sum).Sum

$plan = [ordered]@{
    schema          = 'eva.veritas-plan.v1'
    generated_at    = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
    generated_from  = @('model-export.json')
    format_detected = 'native-wbs'
    prefix          = 'ACA'
    features        = @($planFeatures)
}

$plan | ConvertTo-Json -Depth 10 | Set-Content $planPath -Encoding UTF8

Write-Host "[PASS] veritas-plan.json written: $($planFeatures.Count) features, $totalStories stories"

# Verify
$v = Get-Content $planPath | ConvertFrom-Json
foreach ($f in $v.features) {
    Write-Host "  $($f.id)  $($f.stories.Count)  $($f.title)"
}
Write-Host "[VERIFY] Total features: $($v.features.Count)"
$ts = ($v.features | ForEach-Object { $_.stories.Count } | Measure-Object -Sum).Sum
Write-Host "[VERIFY] Total stories:  $ts"
