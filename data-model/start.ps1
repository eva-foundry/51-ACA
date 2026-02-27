# ACA local data model server -- isolated instance on port 8011
# Shares code from 37-data-model but uses 51-ACA data only.
# Run from anywhere: pwsh start.ps1
#
# Usage:
#   pwsh C:\AICOE\eva-foundry\51-ACA\data-model\start.ps1
#   Then: Invoke-RestMethod http://localhost:8011/health
#
# Data lives in: C:\AICOE\eva-foundry\51-ACA\data-model\model\
# Code lives in: C:\AICOE\eva-foundry\37-data-model\

$SCRIPT_DIR = "C:\AICOE\eva-foundry\51-ACA\data-model"
$CODE_DIR   = "C:\AICOE\eva-foundry\37-data-model"
$VENV_PY    = "C:\AICOE\.venv\Scripts\python.exe"

# -- isolation: point server at ACA model data only
$env:MODEL_DIR   = "$SCRIPT_DIR\model"
$env:COSMOS_URL  = ""
$env:COSMOS_KEY  = ""
$env:MODEL_DB_NAME        = ""
$env:MODEL_CONTAINER_NAME = ""
$env:REDIS_URL            = ""
$env:CACHE_TTL_SECONDS    = "0"
$env:ADMIN_TOKEN          = "dev-admin"
$env:DEV_MODE             = "true"
$env:API_TITLE            = "ACA Model API"

Write-Host "[INFO] Starting ACA data model on port 8011"
Write-Host "[INFO] Model dir: $($env:MODEL_DIR)"
Write-Host "[INFO] Store: MemoryStore (in-process, no Cosmos)"
Write-Host "[INFO] Health: http://localhost:8011/health"
Write-Host "[INFO] Agent summary: http://localhost:8011/model/agent-summary"
Write-Host "[INFO] Press Ctrl+C to stop"

Push-Location $CODE_DIR
& $VENV_PY -m uvicorn api.server:app --port 8011 --reload --log-level info
Pop-Location
