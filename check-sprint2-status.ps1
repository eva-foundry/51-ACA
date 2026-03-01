# Sprint 2 Status Summary
# Quick readiness check for all systems

Write-Host "=== 51-ACA SPRINT 2 STATUS ===" -ForegroundColor Cyan
Write-Host ""

# 1. LOCAL DB Check
Write-Host "[1] LOCAL DB" -ForegroundColor Yellow
try {
    $s2Count = & C:\AICOE\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'data-model'); import db; s2 = [s for s in db.list_layer('wbs') if s.get('sprint_id') == 'Sprint-02']; print(len(s2))"
    
    if ($s2Count -eq "15") {
        Write-Host "  Stories: 15/15 [PASS]" -ForegroundColor Green
    } else {
        Write-Host "  Stories: $s2Count/15 [FAIL]" -ForegroundColor Red
    }
} catch {
    Write-Host "  [ERROR] Cannot query LOCAL db" -ForegroundColor Red
}

# 2. Cloud Model Check
Write-Host ""
Write-Host "[2] CLOUD MODEL" -ForegroundColor Yellow
try {
    $proj = Invoke-RestMethod "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io/model/projects/51-ACA" -ErrorAction Stop
    
    if ($proj.ado_project -eq "51-aca") {
        Write-Host "  ado_project: 51-aca [PASS]" -ForegroundColor Green
    } else {
        Write-Host "  ado_project: $($proj.ado_project) [FAIL]" -ForegroundColor Red
    }
} catch {
    Write-Host "  [ERROR] Cannot reach cloud model" -ForegroundColor Red
}

# 3. Workflow Check
Write-Host ""
Write-Host "[3] GITHUB WORKFLOW" -ForegroundColor Yellow
if (Test-Path ".github/workflows/sprint-agent.yml") {
    Write-Host "  sprint-agent.yml: [PASS]" -ForegroundColor Green
} else {
    Write-Host "  sprint-agent.yml: [MISSING]" -ForegroundColor Red
}

if (Test-Path ".github/scripts/sprint_agent.py") {
    Write-Host "  sprint_agent.py: [PASS]" -ForegroundColor Green
} else {
    Write-Host "  sprint_agent.py: [MISSING]" -ForegroundColor Red
}

# 4. ADO Status (Manual Verification Required)
Write-Host ""
Write-Host "[4] ADO SPRINT 2" -ForegroundColor Yellow
Write-Host "  Status: MANUAL CHECK REQUIRED"
Write-Host "  Action: Run verify-ado-sprint2.ps1"
Write-Host "  Board:  https://dev.azure.com/marcopresta/51-aca/_sprints/taskboard/51-aca/51-aca/Sprint%202"

Write-Host ""
Write-Host "=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "1. Verify ADO: pwsh verify-ado-sprint2.ps1"
Write-Host "2. If ADO needs sync: pwsh sync-ado-sprint2-improved.ps1"
Write-Host "3. Run baseline tests: pytest services/ -x -q"
Write-Host "4. Ready to execute Sprint 2!"
