# Check cloud Cosmos data model for ADO project tracking

$cloudUrl = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"

Write-Host "[INFO] Checking cloud data model schema..."
Write-Host ""

# 1. Health check
try {
    $health = Invoke-RestMethod "$cloudUrl/health"
    Write-Host "[PASS] Cloud data model is UP"
    Write-Host "  Store: $($health.store)"
    Write-Host "  Version: $($health.version)"
    Write-Host "  Uptime: $($health.uptime_seconds) seconds"
    Write-Host ""
} catch {
    Write-Host "[FAIL] Cannot reach cloud data model: $_"
    exit 1
}

# 2. List all layers
try {
    $model = Invoke-RestMethod "$cloudUrl/model/"
    Write-Host "[INFO] Available layers ($($model.layers.Count) total):"
    $model.layers | ForEach-Object { Write-Host "  - $_" }
    Write-Host ""
} catch {
    Write-Host "[FAIL] Cannot query model layers: $_"
    exit 1
}

# 3. Check for ADO-related layers
$adoLayers = $model.layers | Where-Object { $_ -like "*ado*" -or $_ -like "*project*" -or $_ -like "*org*" }
if ($adoLayers) {
    Write-Host "[INFO] Found potential ADO-related layers:"
    $adoLayers | ForEach-Object { Write-Host "  - $_" }
    Write-Host ""
} else {
    Write-Host "[INFO] No obvious ADO-specific layers found"
    Write-Host ""
}

# 4. Check projects layer (most likely place for ADO tracking)
try {
    $projects = Invoke-RestMethod "$cloudUrl/model/projects/"
    Write-Host "[INFO] Projects layer: $($projects.Count) records"
    
    # Check if any project has ADO-related fields
    $sample = $projects | Select-Object -First 1
    if ($sample) {
        Write-Host "[INFO] Sample project fields:"
        $sample.PSObject.Properties | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Value)"
        }
        Write-Host ""
        
        # Look for marcopresta ADO projects
        $adoProjects = $projects | Where-Object { 
            $_.ado_org -like "*marcopresta*" -or 
            $_.ado_project -like "*marcopresta*" -or
            $_. id -like "*ado*" -or
            $_.label -like "*ADO*" -or
            $_.url -like "*dev.azure.com/marcopresta*"
        }
        
        if ($adoProjects) {
            Write-Host "[PASS] Found ADO projects in cloud model:"
            $adoProjects | ForEach-Object {
                Write-Host "  ID: $($_.id)"
                Write-Host "  Label: $($_.label)"
                if ($_.ado_org) { Write-Host "    ado_org: $($_.ado_org)" }
                if ($_.ado_project) { Write-Host "    ado_project: $($_.ado_project)" }
                if ($_.url) { Write-Host "    url: $($_.url)" }
                Write-Host ""
            }
        } else {
            Write-Host "[INFO] No marcopresta ADO projects found in projects layer"
        }
    }
} catch {
    Write-Host "[WARN] Cannot query projects layer: $_"
}

# 5. Summary
Write-Host ""
Write-Host "=== SUMMARY ==="
Write-Host "Cloud endpoint: $cloudUrl"
Write-Host "Store type: Cosmos DB"
Write-Host "Total layers: $($model.layers.Count)"
Write-Host "ADO-specific layers: $($adoLayers.Count)"
Write-Host ""
