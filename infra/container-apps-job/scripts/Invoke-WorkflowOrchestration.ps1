# EVA-STORY: ACA-17-005
# ACA-17-005: Invoke-WorkflowOrchestration PowerShell Module
# Integration wrapper for Sync Orchestration Job
# Coordinates Classifier, Tuner, and Advisor agents via HTTP endpoints

param()

# Constants
$ORCHESTRATION_ENDPOINT = $env:ORCHESTRATION_ENDPOINT ?? "http://localhost:8005"
$ORCHESTRATION_TIMEOUT_MS = 400

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

function Invoke-SyncWorkflowOrchestration {
    <#
    .SYNOPSIS
    Invoke the multi-agent orchestration workflow.
    
    .PARAMETER ErrorMessage
    Error message that triggered this invocation
    
    .PARAMETER ErrorCode
    Error code (e.g., "429" for rate-limit, "403" for permission, "500" for transient)
    
    .PARAMETER RetryCount
    Number of retry attempts so far (0+)
    
    .PARAMETER ElapsedMs
    Elapsed time since sync started (milliseconds)
    
    .PARAMETER Context
    Hashtable with additional context: {failed_story_count, cb_state, subscription_size}
    
    .EXAMPLE
    $result = Invoke-SyncWorkflowOrchestration `
        -ErrorMessage "Cosmos 429 rate-limit" `
        -ErrorCode "429" `
        -RetryCount 2 `
        -Context @{failed_story_count = 5; cb_state = "open"}
    
    Write-Host "Action: $($result.final_action)"
    Write-Host "Delay: $($result.delay_ms)ms"
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $ErrorMessage,
        
        [Parameter(Mandatory=$true)]
        [string] $ErrorCode,
        
        [int] $RetryCount = 0,
        
        [int] $ElapsedMs = 0,
        
        [hashtable] $Context = $null
    )
    
    Write-Host "[ORCHESTRATION] Invoking multi-agent workflow: error=$ErrorCode, retry=$RetryCount" -ForegroundColor Cyan
    
    try {
        # Build request body
        $requestBody = @{
            error_message = $ErrorMessage
            error_code = $ErrorCode
            retry_count = $RetryCount
            elapsed_ms = $ElapsedMs
            context = $Context
        } | ConvertTo-Json
        
        # Call orchestration endpoint
        $params = @{
            Uri = "$ORCHESTRATION_ENDPOINT/v1/orchestrate"
            Method = "POST"
            ContentType = "application/json"
            Body = $requestBody
            TimeoutSec = [math]::Ceiling($ORCHESTRATION_TIMEOUT_MS / 1000)
            ErrorAction = "Stop"
        }
        
        $response = Invoke-RestMethod @params
        
        Write-Host "[ORCHESTRATION] Decision received in $($response.workflow_duration_ms)ms: $($response.final_action)" -ForegroundColor Green
        
        return [PSCustomObject] $response
        
    } catch {
        Write-Warning "[ORCHESTRATION] Failed to get orchestration decision: $($_.Exception.Message)"
        Write-Host "[ORCHESTRATION] Falling back to static fallback rules" -ForegroundColor Yellow
        
        return Invoke-WorkflowFallback -ErrorCode $ErrorCode -RetryCount $RetryCount
    }
}


function Invoke-WorkflowFallback {
    <#
    .SYNOPSIS
    Fallback orchestration when workflow is unavailable.
    
    Returns static decision based on error type and retry count.
    #>
    
    [CmdletBinding()]
    param(
        [string] $ErrorCode = "500",
        [int] $RetryCount = 0
    )
    
    # Permanent errors: 403 (forbidden), 401 (auth), 404 (not found)
    if ($ErrorCode -in @("403", "401", "404")) {
        return [PSCustomObject] @{
            final_action = "skip"
            delay_ms = 0
            guidance = "Error $ErrorCode is permanent - skipping story"
            workflow_duration_ms = 0
            agents_executed = @()
            confidence = 0.80
            timestamp = (Get-Date -AsUTC -Format "o")
        }
    }
    
    # Transient errors: use exponential backoff
    $delayMs = 1000 * [math]::Pow(2, [math]::Min($RetryCount, 3))
    
    return [PSCustomObject] @{
        final_action = "retry"
        delay_ms = [int] $delayMs
        guidance = "Fallback backoff: retry after $([int]$delayMs)ms"
        workflow_duration_ms = 0
        agents_executed = @()
        confidence = 0.65
        timestamp = (Get-Date -AsUTC -Format "o")
    }
}


function Emit-OrchestrationEvent {
    <#
    .SYNOPSIS
    Emit OrchestrationWorkflowComplete event to Application Insights (non-blocking).
    
    .PARAMETER Result
    OrchestrationResult object from Invoke-SyncWorkflowOrchestration
    
    .PARAMETER CorrelationId
    Correlation ID for linking to broader orchestration context
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [PSCustomObject] $Result,
        
        [string] $CorrelationId = [Guid]::NewGuid().ToString()
    )
    
    # Non-blocking background event emission
    $job = Start-Job -ScriptBlock {
        param($res, $cid, $endpoint)
        
        try {
            $eventBody = @{
                event_type = "OrchestrationWorkflowComplete"
                final_action = $res.final_action
                agents_executed = $res.agents_executed -join ","
                workflow_duration_ms = $res.workflow_duration_ms
                confidence = $res.confidence
                correlation_id = $cid
                timestamp = (Get-Date -AsUTC -Format "o")
            } | ConvertTo-Json
            
            $params = @{
                Uri = "$endpoint/v1/telemetry"
                Method = "POST"
                ContentType = "application/json"
                Body = $eventBody
                TimeoutSec = 2
                ErrorAction = "SilentlyContinue"
            }
            
            Invoke-RestMethod @params | Out-Null
            
        } catch {
            # Silent fail - telemetry is non-blocking
        }
    } -ArgumentList $Result, $CorrelationId, $ORCHESTRATION_ENDPOINT
    
    # Don't wait for result - this is non-blocking
    $null = Remove-Job $job -Force
}


# ============================================================================
# EXPORTS
# ============================================================================

Export-ModuleMember -Function @(
    'Invoke-SyncWorkflowOrchestration',
    'Invoke-WorkflowFallback',
    'Emit-OrchestrationEvent'
)
