# Fix 51-ACA ado_project in cloud Cosmos model
# Change from "eva-poc" to "51-aca" to match reality

$cloudUrl = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"

Write-Host "[INFO] Fetching 51-ACA project from cloud model..."

try {
    $project = Invoke-RestMethod "$cloudUrl/model/projects/51-ACA"
    $prevRowVersion = $project.row_version
    
    Write-Host "[INFO] Current state:"
    Write-Host "  ID: $($project.id)"
    Write-Host "  Label: $($project.label)"
    Write-Host "  ado_project: $($project.ado_project) <- WRONG, should be '51-aca'"
    Write-Host "  row_version: $prevRowVersion"
    Write-Host ""
    
    # Update the field
    $project.ado_project = "51-aca"
    
    # Strip audit columns
    $projectClean = $project | Select-Object * -ExcludeProperty `
        layer, modified_by, modified_at, created_by, created_at, row_version, source_file
    
    $body = $projectClean | ConvertTo-Json -Depth 10
    
    Write-Host "[INFO] Updating cloud model..."
    $updated = Invoke-RestMethod "$cloudUrl/model/projects/51-ACA" `
        -Method PUT `
        -ContentType "application/json" `
        -Body $body `
        -Headers @{"X-Actor"="agent:copilot"}
    
    Write-Host "[PASS] Updated successfully"
    Write-Host "  row_version: $prevRowVersion -> $($updated.row_version)"
    Write-Host "  modified_by: $($updated.modified_by)"
    Write-Host "  ado_project: $($updated.ado_project)"
    Write-Host ""
    
    # Verify
    $verify = Invoke-RestMethod "$cloudUrl/model/projects/51-ACA"
    if ($verify.ado_project -eq "51-aca" -and $verify.row_version -eq ($prevRowVersion + 1)) {
        Write-Host "[PASS] Verification successful"
        Write-Host "  51-ACA now correctly points to ado_project: 51-aca"
    } else {
        Write-Host "[FAIL] Verification failed"
        Write-Host "  Expected ado_project: 51-aca, got: $($verify.ado_project)"
        Write-Host "  Expected row_version: $($prevRowVersion + 1), got: $($verify.row_version)"
    }
    
} catch {
    Write-Host "[FAIL] Error updating cloud model: $_"
    Write-Host $_.Exception.Message
    exit 1
}
