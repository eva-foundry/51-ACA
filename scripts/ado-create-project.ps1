# ado-create-project.ps1 -- one-time: create dev.azure.com/marcopresta/51-aca
# Usage: pwsh .\scripts\ado-create-project.ps1
# Reads PAT from KV marcosandkv20260203 / ADO-PAT

param([switch]$SkipCreate)

$org = "https://dev.azure.com/marcopresta"
$projectName = "51-aca"

Write-Host "[INFO] Loading PAT from KV..."
$pat = az keyvault secret show --vault-name marcosandkv20260203 --name ADO-PAT --query value -o tsv 2>&1
if (-not $pat -or $pat.Length -lt 10) { Write-Error "PAT load failed: $pat"; exit 1 }
$env:ADO_PAT = $pat
Write-Host "[INFO] PAT loaded len=$($pat.Length)"

$b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
$headers = @{ Authorization = "Basic $b64"; "Content-Type" = "application/json" }

# -- Check if project already exists
Write-Host "[INFO] Checking if project exists..."
try {
    $existing = Invoke-RestMethod "$org/_apis/projects/$projectName`?api-version=7.1" -Headers $headers -ErrorAction Stop
    Write-Host "[PASS] Project already exists: id=$($existing.id) state=$($existing.state)"
    exit 0
} catch {
    Write-Host "[INFO] Project does not exist -- will create."
}

if ($SkipCreate) { Write-Host "[INFO] -SkipCreate flag set -- done."; exit 0 }

# -- Scrum process template id (default enabled on marcopresta org)
$scrumTemplateId = "6b724908-ef14-45cf-84f8-768b5384da45"

$body = @{
    name         = $projectName
    description  = "Azure Cost Advisor -- Phase 1 commercial SaaS"
    visibility   = "private"
    capabilities = @{
        versioncontrol  = @{ sourceControlType = "Git" }
        processTemplate = @{ templateTypeId = $scrumTemplateId }
    }
} | ConvertTo-Json -Depth 5

Write-Host "[INFO] Creating project $projectName..."
$r = Invoke-RestMethod "$org/_apis/projects?api-version=7.1" -Method POST -Headers $headers -Body $body
Write-Host "[INFO] Response: status=$($r.status) id=$($r.id)"

# -- Poll until wellFormed (project creation is async)
$maxWait = 30; $waited = 0
do {
    Start-Sleep 3; $waited += 3
    $check = Invoke-RestMethod "$org/_apis/projects/$projectName`?api-version=7.1" -Headers $headers -ErrorAction SilentlyContinue
    Write-Host "[INFO] state=$($check.state) waited=${waited}s"
} while ($check.state -ne "wellFormed" -and $waited -lt $maxWait)

if ($check.state -eq "wellFormed") {
    Write-Host "[PASS] Project created: id=$($check.id)"
    Write-Host "[NEXT] Run: `$env:ADO_PAT = '<pat>'; .\ado-import.ps1 -DryRun"
} else {
    Write-Host "[WARN] state=$($check.state) after ${waited}s -- may still be provisioning"
}
