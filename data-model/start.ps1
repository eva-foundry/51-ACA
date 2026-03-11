# ACA local data model server -- SQLite-backed, port 8055
# 51-ACA owns this server completely; no dependency on 37-data-model.
# DB persists across restarts at: data-model/aca-model.db
#
# Usage:
#   pwsh -File C:\eva-foundry\51-ACA\data-model\start.ps1
#   Then: Invoke-RestMethod http://localhost:8055/health
#   Docs: http://localhost:8055/docs

$SCRIPT_DIR = $PSScriptRoot
$VENV_PY    = "C:\eva-foundry\.venv\Scripts\python.exe"
$Port       = 8055

Write-Host "[INFO] Starting ACA data model on http://localhost:$Port"
Write-Host "[INFO] DB: $SCRIPT_DIR\aca-model.db"
Write-Host "[INFO] Store: SQLite (persistent)"
Write-Host "[INFO] Health: http://localhost:$Port/health"
Write-Host "[INFO] Agent summary: http://localhost:$Port/model/agent-summary"
Write-Host "[INFO] Docs: http://localhost:$Port/docs"
Write-Host "[INFO] Press Ctrl+C to stop"

Push-Location $SCRIPT_DIR
& $VENV_PY -m uvicorn server:app --port $Port --reload --log-level info
Pop-Location
