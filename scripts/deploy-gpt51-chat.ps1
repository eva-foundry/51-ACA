Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEPLOY GPT-5.1-CHAT TO MARCO-SANDBOX-FOUNDRY" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "📋 Deployment Details:" -ForegroundColor Yellow
Write-Host "   Model: gpt-5.1-chat" -ForegroundColor White
Write-Host "   Version: 2025-11-13" -ForegroundColor White
Write-Host "   Resource: marco-sandbox-foundry" -ForegroundColor White
Write-Host "   Region: Canada East" -ForegroundColor White
Write-Host "   API Support: ✅ Chat Completions API" -ForegroundColor Green
Write-Host "   VS Code Compatible: ✅ Yes!" -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "Deploy gpt-5.1-chat? (y/n)"

if ($confirm -eq "y") {
    Write-Host "`n🚀 Deploying gpt-5.1-chat..." -ForegroundColor Cyan
    
    try {
        az cognitiveservices account deployment create `
            --name marco-sandbox-foundry `
            --resource-group EsDAICoE-Sandbox `
            --deployment-name gpt-5.1-chat `
            --model-name gpt-5.1-chat `
            --model-version "2025-11-13" `
            --model-format OpenAI `
            --sku-capacity 10 `
            --sku-name "Standard"
        
        Write-Host "`n✅ Deployment initiated!" -ForegroundColor Green
        Write-Host "`nChecking deployment status..." -ForegroundColor Yellow
        
        Start-Sleep -Seconds 5
        
        $deployment = az cognitiveservices account deployment show `
            --name marco-sandbox-foundry `
            --resource-group EsDAICoE-Sandbox `
            --deployment-name gpt-5.1-chat `
            -o json | ConvertFrom-Json
        
        Write-Host "`n📊 Deployment Status: $($deployment.properties.provisioningState)" -ForegroundColor $(if ($deployment.properties.provisioningState -eq "Succeeded") { "Green" } else { "Yellow" })
        
        if ($deployment.properties.provisioningState -eq "Succeeded") {
            Write-Host "`n🎉 gpt-5.1-chat is ready to use!" -ForegroundColor Green
            Write-Host "`nNext steps:" -ForegroundColor Yellow
            Write-Host "  1. Reload VS Code window (Ctrl+Shift+P -> Developer: Reload Window)"
            Write-Host "  2. Open Chat (Ctrl+Alt+I)"
            Write-Host "  3. Select 'gpt-5.1-chat' from the model dropdown"
            Write-Host "  4. Enjoy the latest GPT-5.1 with full Chat API support!"
        } else {
            Write-Host "`n⏱️  Deployment in progress. Check status with:" -ForegroundColor Yellow
            Write-Host "   az cognitiveservices account deployment show --name marco-sandbox-foundry --resource-group EsDAICoE-Sandbox --deployment-name gpt-5.1-chat"
        }
        
    } catch {
        Write-Host "`n❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "`nNote: You may need to request quota increase for this model." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n❌ Deployment cancelled." -ForegroundColor Yellow
    Write-Host "`nYou can use gpt-4o in VS Code Chat instead (already deployed)." -ForegroundColor Gray
}

Write-Host "`n════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
