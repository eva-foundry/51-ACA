# deploy-metrics-to-dashboard.ps1
# Deploy regenerated .eva/ files from 51-ACA to 31-eva-faces (production dashboard)
# Verify MTI score and ADO board sync

param(
    [switch]$DryRun,
    [switch]$VerifyOnly
)

# Configuration
$PROJECT_DIR = "C:\eva-foundry\51-ACA"
$DASHBOARD_DIR = "C:\eva-foundry\31-eva-faces"
$DATA_MODEL_DIR = "C:\eva-foundry\37-data-model"

$FILES_TO_DEPLOY = @(
    "veritas-plan.json",
    "discovery.json",
    "reconciliation.json",
    "trust.json",
    "ado-id-map.json"
)

function Log-Status {
    param([string]$Message, [string]$Status = "INFO")
    $color = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        default { "Cyan" }
    }
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Status] $Message" -ForegroundColor $color
}

function Verify-Files {
    Log-Status "Verifying regenerated .eva/ files in 51-ACA" "INFO"
    
    $all_exist = $true
    foreach ($file in $FILES_TO_DEPLOY) {
        $path = Join-Path $PROJECT_DIR ".eva" $file
        if (Test-Path $path) {
            $size = [math]::Round((Get-Item $path).Length / 1KB, 1)
            Log-Status "[OK] $file ($($size) KB)" "PASS"
        } else {
            Log-Status "[MISSING] $file NOT FOUND" "FAIL"
            $all_exist = $false
        }
    }
    
    return $all_exist
}

function Check-MTI-Score {
    Log-Status "Checking MTI Score" "INFO"
    
    $trust_path = Join-Path $PROJECT_DIR ".eva" "trust.json"
    $trust = Get-Content $trust_path | ConvertFrom-Json
    
    $mti = $trust.mti_score.percent
    $status = $trust.mti_score.status
    
    if ($mti -eq 99 -and $status -eq "READY-TO-MERGE") {
        Log-Status "[OK] MTI Score: $mti/100 - Status: $status" "PASS"
        return $true
    } else {
        Log-Status "[FAIL] MTI Score: $mti/100 - Status: $status (Expected 99/100, READY-TO-MERGE)" "FAIL"
        return $false
    }
}

function Check-Story-Count-Consistency {
    Log-Status "Verifying story count consistency (281 stories)" "INFO"
    
    $vp = Get-Content (Join-Path $PROJECT_DIR ".eva" "veritas-plan.json") | ConvertFrom-Json
    $disc = Get-Content (Join-Path $PROJECT_DIR ".eva" "discovery.json") | ConvertFrom-Json
    $recon = Get-Content (Join-Path $PROJECT_DIR ".eva" "reconciliation.json") | ConvertFrom-Json
    $ado = Get-Content (Join-Path $PROJECT_DIR ".eva" "ado-id-map.json") | ConvertFrom-Json
    
    $vp_count = ($vp.features | ForEach-Object { $_.stories.Count } | Measure-Object -Sum).Sum
    $disc_count = $disc.summary.total_stories
    $recon_count = $recon.summary.total_stories
    $ado_count = $ado.PSObject.Properties.Count
    
    Log-Status "  veritas-plan.json: $vp_count stories" "INFO"
    Log-Status "  discovery.json: $disc_count stories" "INFO"
    Log-Status "  reconciliation.json: $recon_count stories" "INFO"
    Log-Status "  ado-id-map.json: $ado_count stories" "INFO"
    
    if ($vp_count -eq 281 -and $disc_count -eq 281 -and $recon_count -eq 281 -and $ado_count -eq 281) {
        Log-Status "[OK] All sources aligned: 281/281/281/281 (100 percent consistency)" "PASS"
        return $true
    } else {
        Log-Status "[FAIL] Inconsistency detected" "FAIL"
        return $false
    }
}

function Deploy-Files {
    Log-Status "Deploying .eva/ files to production dashboard (31-eva-faces)" "INFO"
    
    $source_eva = Join-Path $PROJECT_DIR ".eva"
    $target_eva = Join-Path $DASHBOARD_DIR ".eva" "projects" "51-ACA"
    
    # Create target directory if it doesn't exist
    if (-not (Test-Path $target_eva)) {
        New-Item -ItemType Directory -Path $target_eva -Force | Out-Null
        Log-Status "Created directory: $target_eva" "INFO"
    }
    
    $deploy_count = 0
    foreach ($file in $FILES_TO_DEPLOY) {
        $source_file = Join-Path $source_eva $file
        $target_file = Join-Path $target_eva $file
        
        if ($DryRun) {
            Log-Status "[DRY-RUN] Would copy: $file → $target_eva" "WARN"
            $deploy_count++
        } else {
            try {
                Copy-Item $source_file $target_file -Force
                Log-Status "[OK] Deployed: $file" "PASS"
                $deploy_count++
            } catch {
                Log-Status "[FAIL] Failed to deploy $file : $_" "FAIL"
            }
        }
    }
    
    return $deploy_count -eq $FILES_TO_DEPLOY.Count
}

function Verify-Dashboard-Sync {
    Log-Status "Verifying dashboard data (31-eva-faces)" "INFO"
    
    $target_eva = Join-Path $DASHBOARD_DIR ".eva" "projects" "51-ACA"
    
    $all_exist = $true
    foreach ($file in $FILES_TO_DEPLOY) {
        $target_file = Join-Path $target_eva $file
        if (Test-Path $target_file) {
            $size = [math]::Round((Get-Item $target_file).Length / 1KB, 1)
            Log-Status "[OK] Found in dashboard: $file ($($size) KB)" "PASS"
        } else {
            Log-Status "[MISSING] Not found in dashboard: $file" "FAIL"
            $all_exist = $false
        }
    }
    
    return $all_exist
}

function Verify-ADO-Sync {
    Log-Status "Verifying ADO board sync with 281-story baseline" "INFO"
    
    $ado_map_path = Join-Path $PROJECT_DIR ".eva" "ado-id-map.json"
    $ado_map = Get-Content $ado_map_path | ConvertFrom-Json
    
    $story_count = $ado_map.PSObject.Properties.Count
    Log-Status "ADO story mappings: $story_count stories in ado-id-map.json" "INFO"
    
    if ($story_count -eq 281) {
        Log-Status "[OK] ADO baseline verified: 281 stories mapped correctly" "PASS"
        return $true
    } else {
        Log-Status "[FAIL] ADO baseline mismatch: Expected 281, found $story_count" "FAIL"
        return $false
    }
}

function Verify-MetricsAPI {
    Log-Status "Checking metrics API availability (37-data-model)" "INFO"
    
    # Try to reach the data model API
    $api_url = "http://localhost:8010/model/projects/51-ACA"
    
    try {
        $response = Invoke-RestMethod $api_url -ErrorAction Stop -TimeoutSec 2
        Log-Status "[OK] Metrics API reachable at $api_url" "PASS"
        
        if ($response.mti_score) {
            Log-Status "  MTI Score from API: $($response.mti_score.percent)/100" "INFO"
        }
        return $true
    } catch {
        Log-Status "[WARN] Metrics API not available at $api_url (service may not be running)" "WARN"
        return $false
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      DEPLOYMENT & VERIFICATION - .EVA/ FILES TO DASHBOARD      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Phase 1: Pre-deployment validation
Log-Status "PHASE 1: PRE-DEPLOYMENT VALIDATION" "INFO"

$files_ok = Verify-Files
$mti_ok = Check-MTI-Score
$story_ok = Check-Story-Count-Consistency

Write-Host ""

if (-not ($files_ok -and $mti_ok -and $story_ok)) {
    Log-Status "Pre-deployment validation FAILED. Aborting deployment." "FAIL"
    exit 1
}

Log-Status "[OK] Pre-deployment validation PASSED" "PASS"
Write-Host ""

# Phase 2: Deploy files
if ($VerifyOnly) {
    Log-Status "Running in VERIFY-ONLY mode. Skipping file deployment." "WARN"
} else {
    Log-Status "PHASE 2: DEPLOYING FILES" "INFO"
    $deploy_ok = Deploy-Files
    
    if ($deploy_ok) {
        Log-Status "[OK] File deployment PASSED" "PASS"
    } else {
        Log-Status "[FAIL] File deployment FAILED" "FAIL"
    }
    Write-Host ""
}

# Phase 3: Post-deployment verification
Log-Status "PHASE 3: POST-DEPLOYMENT VERIFICATION" "INFO"

$dashboard_ok = Verify-Dashboard-Sync
$ado_ok = Verify-ADO-Sync
$api_ok = Verify-MetricsAPI

Write-Host ""

if ($dashboard_ok -and $ado_ok) {
    Log-Status "[OK] POST-DEPLOYMENT VERIFICATION PASSED" "PASS"
} else {
    Log-Status "[PARTIAL] POST-DEPLOYMENT VERIFICATION PARTIAL" "WARN"
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    DEPLOYMENT SUMMARY                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[INFO] DRY-RUN Mode: All checks passed, ready for deployment" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To execute deployment, run:" -ForegroundColor Cyan
    Write-Host "  .\deploy-metrics-to-dashboard.ps1" -ForegroundColor Cyan
} else {
    if ($dashboard_ok -and $ado_ok) {
        Write-Host "[SUCCESS] DEPLOYMENT COMPLETE AND VERIFIED" -ForegroundColor Green
        Write-Host ""
        Write-Host "Deployed files:" -ForegroundColor Cyan
        $FILES_TO_DEPLOY | ForEach-Object {
            Write-Host "  [OK] $_"
        }
        Write-Host ""
        Write-Host "Verification results:" -ForegroundColor Cyan
        Write-Host "  [OK] MTI Score: 99/100 (READY-TO-MERGE)"
        Write-Host "  [OK] Story count consistency: 281/281/281/281"
        Write-Host "  [OK] ADO baseline: 281 stories mapped"
        Write-Host "  [OK] Dashboard sync: All files deployed"
        
        if ($api_ok) {
            Write-Host "  [OK] Metrics API: Available"
        } else {
            Write-Host "  [WARN] Metrics API: Not available (service may not be running)"
        }
        
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Verify dashboard displays MTI Score: 99/100"
        Write-Host "  2. Confirm ADO board sync with 281 stories"
        Write-Host "  3. Monitor metrics dashboard for 24 hours"
    } else {
        Write-Host "[WARN] DEPLOYMENT PARTIAL - See above for details" -ForegroundColor Yellow
    }
}

Write-Host ""
