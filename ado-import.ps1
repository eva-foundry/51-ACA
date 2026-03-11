# ado-import.ps1 -- 51-ACA ADO project onboard
# Creates: 1 Epic + 12 Features + 16 PBIs in dev.azure.com/marcopresta/51-aca
#
# PRE-REQUISITE: ADO project must exist first.
#   Run: pwsh .\scripts\ado-create-project.ps1
#
# Usage:
#   $env:ADO_PAT = "<pat>"; .\ado-import.ps1
#   $env:ADO_PAT = "<pat>"; .\ado-import.ps1 -DryRun
param([switch]$DryRun)
$sharedScript   = "C:\eva-foundry\38-ado-poc\scripts\ado-import-project.ps1"
$artifactsFile  = Join-Path $PSScriptRoot "ado-artifacts.json"
if (-not (Test-Path $sharedScript))  { throw "Shared import script not found: $sharedScript" }
if (-not (Test-Path $artifactsFile)) { throw "Artifacts file not found: $artifactsFile" }
# Read ado_project from artifacts so this never silently targets eva-poc
$adoProject = (Get-Content $artifactsFile -Raw | ConvertFrom-Json).ado_project
if (-not $adoProject) { throw "ado_project not set in ado-artifacts.json" }
& $sharedScript -ArtifactsFile $artifactsFile -Project $adoProject -DryRun:$DryRun
