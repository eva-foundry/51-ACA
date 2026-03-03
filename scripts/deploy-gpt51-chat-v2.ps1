Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEPLOYING GPT-5.1-CHAT" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "Step 1: Checking if gpt-5.1-chat already exists..." -ForegroundColor Yellow

$existing = az cognitiveservices account deployment show `
    --name marco-sandbox-foundry `
    --resource-group EsDAICoE-Sandbox `
    --deployment-name gpt-5.1-chat `
    2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ gpt-5.1-chat is already deployed!" -ForegroundColor Green
    $deployment = $existing | ConvertFrom-Json
    Write-Host "`nDeployment Info:" -ForegroundColor Cyan
    Write-Host "  Model: $($deployment.properties.model.name)" -ForegroundColor White
    Write-Host "  Version: $($deployment.properties.model.version)" -ForegroundColor White
    Write-Host "  Status: $($deployment.properties.provisioningState)" -ForegroundColor Green
    Write-Host "  Capacity: $($deployment.sku.capacity * 1000) TPM" -ForegroundColor White
} else {
    Write-Host "❌ gpt-5.1-chat not found. Creating new deployment..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Step 2: Creating deployment..." -ForegroundColor Yellow
    
    $deployResult = az cognitiveservices account deployment create `
        --name marco-sandbox-foundry `
        --resource-group EsDAICoE-Sandbox `
        --deployment-name gpt-5.1-chat `
        --model-name gpt-5.1-chat `
        --model-version "2025-11-13" `
        --model-format OpenAI `
        --sku-capacity 10 `
        --sku-name "Standard" `
        2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Deployment created successfully!" -ForegroundColor Green
        $deployResult | ConvertFrom-Json | Select-Object name, @{Name='state';Expression={$_.properties.provisioningState}} | Format-List
    } else {
        Write-Host "❌ Deployment failed" -ForegroundColor Red
        Write-Host "Error:" -ForegroundColor Yellow
        $deployResult
        
        # Check if it's a quota issue
        if ($deployResult -like "*quota*" -or $deployResult -like "*capacity*") {
            Write-Host "`n💡 This might be a quota issue." -ForegroundColor Cyan
            Write-Host "   Try reducing capacity or request quota increase at:" -ForegroundColor Gray
            Write-Host "   https://aka.ms/oai/quotaincrease" -ForegroundColor White
        }
    }
}

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Step 3: Listing all current deployments..." -ForegroundColor Yellow
Write-Host ""

.\list-foundry-models.ps1

Write-Host "`n════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
