param(
  [string]$ProjectId = "51-ACA",
  [string]$Sprint = "SPRINT-048",
  [string]$Assignee = "copilot"
)

$base = "https://msub-eva-data-model.victoriousgrass-30debbd3.canadacentral.azurecontainerapps.io"
$repo = "C:\eva-foundry\51-ACA"
$adoMapPath = Join-Path $repo ".eva\ado-id-map.json"
$adoMap = @{}

if (Test-Path $adoMapPath) {
  $adoMap = Get-Content $adoMapPath -Raw | ConvertFrom-Json -AsHashtable
}

$rows = (Invoke-RestMethod "$base/model/wbs/?limit=5000").data |
  Where-Object { $_.project_id -eq $ProjectId -and $_.level -in @("user_story", "story") }

$updated = 0
$skipped = 0
$failed = 0
$errors = @()

foreach ($rec in $rows) {
  $needs = [string]::IsNullOrWhiteSpace([string]$rec.sprint) -or
           [string]::IsNullOrWhiteSpace([string]$rec.assignee) -or
           [string]::IsNullOrWhiteSpace([string]$rec.ado_id)

  if (-not $needs) {
    $skipped++
    continue
  }

  $storyId = [string]$rec.original_story_id
  $adoVal = if ($storyId -and $adoMap.ContainsKey($storyId)) { [string]$adoMap[$storyId] } else { "PENDING" }

  $rec | Add-Member -NotePropertyName sprint -NotePropertyValue $Sprint -Force
  $rec | Add-Member -NotePropertyName assignee -NotePropertyValue $Assignee -Force
  $rec | Add-Member -NotePropertyName ado_id -NotePropertyValue $adoVal -Force

  $payload = $rec | ConvertTo-Json -Depth 12

  try {
    Invoke-RestMethod "$base/model/wbs/$($rec.id)" -Method Put -ContentType "application/json" -Body $payload | Out-Null
    $updated++
  } catch {
    $failed++
    $errors += [pscustomobject]@{
      id = $rec.id
      original_story_id = $storyId
      error = $_.Exception.Message
    }
  }
}

$result = [pscustomobject]@{
  generated_at = (Get-Date).ToString("s")
  project_id = $ProjectId
  total_story_records = $rows.Count
  updated = $updated
  skipped = $skipped
  failed = $failed
}

$out = [pscustomobject]@{
  summary = $result
  errors = $errors
}

$outPath = Join-Path $repo ".eva\nested-dpdca-metadata-update.json"
$out | ConvertTo-Json -Depth 8 | Set-Content $outPath

Write-Host "updated=$updated skipped=$skipped failed=$failed"
Write-Host "report=$outPath"
