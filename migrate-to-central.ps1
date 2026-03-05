#!/usr/bin/env pwsh
# Migrate 51-ACA data from port 8055 (local SQLite) to port 8010 (central Cosmos)

$base_local = "http://localhost:8055"
$base_central = "http://localhost:8010"

Write-Host "=== MIGRATING 51-ACA TO CENTRAL DATA MODEL ===" -ForegroundColor Green

# Get all layers from local
$layers = @("requirements", "endpoints", "services", "containers", "agents", "screens", "infrastructure", "hooks", "components")

$migrated = @{}

foreach ($layer in $layers) {
    Write-Host "`n[Exporting] $layer..." -ForegroundColor Cyan
    try {
        $objects = Invoke-RestMethod "$base_local/model/$layer/" -ErrorAction SilentlyContinue
        
        if ($objects -and $objects.Count -gt 0) {
            Write-Host "  Found: $($objects.Count) objects"
            
            # Push to central
            $success = 0
            $failed = 0
            
            foreach ($obj in $objects) {
                # Strip audit fields
                $clean = $obj | Select-Object * -ExcludeProperty obj_id, layer, modified_by, modified_at, created_by, created_at, row_version, source_file
                $body = $clean | ConvertTo-Json -Depth 10
                
                try {
                    $result = Invoke-RestMethod "$base_central/model/$layer/$($obj.id)" `
                        -Method PUT `
                        -ContentType "application/json" `
                        -Body $body `
                        -Headers @{"X-Actor" = "agent:copilot"} `
                        -ErrorAction SilentlyContinue
                    $success++
                } catch {
                    $failed++
                }
            }
            
            Write-Host "  Pushed to central: $success OK, $failed failed"
            $migrated[$layer] = @{ total = $objects.Count; success = $success; failed = $failed }
        } else {
            Write-Host "  (none to migrate)"
        }
    } catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
    }
}

Write-Host "`n=== MIGRATION SUMMARY ===" -ForegroundColor Green
$migrated.GetEnumerator() | ForEach-Object {
    if ($_.Value.total -gt 0) {
        Write-Host "$($_.Key): $($_.Value.success)/$($_.Value.total) pushed"
    }
}

Write-Host "`n[Verification] Comparing object counts..." -ForegroundColor Cyan
$local_summary = Invoke-RestMethod "$base_local/model/agent-summary"
$central_summary = Invoke-RestMethod "$base_central/model/agent-summary"

Write-Host "Port 8055 (local): $($local_summary.total) total objects"
Write-Host "Port 8010 (central): $($central_summary.total) total objects"
Write-Host "Central Cosmos is now primary data store for 51-ACA" -ForegroundColor Green
