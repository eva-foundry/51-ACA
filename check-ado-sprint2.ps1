# Check ADO Sprint 2 work items
# Requires az CLI with azure-devops extension

$org = "https://dev.azure.com/marcopresta"
$iterationPath = "51-aca\Sprint 2"

Write-Host "[INFO] Querying ADO Sprint 2 work items..."

try {
    $wiql = "SELECT [System.Id], [System.Title], [System.IterationPath] FROM WorkItems WHERE [System.IterationPath] = '$iterationPath'"
    $result = az boards query --wiql $wiql --org $org --output json 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        $json = $result | ConvertFrom-Json
        Write-Host "[PASS] Found $($json.Count) work items in Sprint 2"
        $json | Select-Object -First 15 | ForEach-Object {
            Write-Host "  ID: $($_.fields.'System.Id') - $($_.fields.'System.Title')"
        }
    } else {
        Write-Host "[WARN] az CLI returned error code $LASTEXITCODE"
        Write-Host $result
    }
} catch {
    Write-Host "[FAIL] Error querying ADO: $_"
}
