# EVA-STORY: ACA-17-004
# ACA-17-004: Invoke-SyncAdvisor PowerShell Module
# Integration wrapper for Sync Orchestration Job
# Called on critical failure to get AI-driven recovery recommendations

param()

# Constants
$ADVISOR_ENDPOINT = $env:ADVISOR_AGENT_ENDPOINT ?? "http://localhost:8004"
$ADVISOR_TIMEOUT_MS = 500

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

function Invoke-SyncAdvisor {
    <#
    .SYNOPSIS
    Get AI-driven advisor recommendation for sync orchestration failure.
    
    .PARAMETER SubscriptionSize
    Size of subscription: "small" | "medium" | "large" (affects parallelism recommendations)
    
    .PARAMETER FailedStoryCount
    Number of failed stories (0-21)
    
    .PARAMETER TotalStories
    Total story count (default: 21)
    
    .PARAMETER CircuitBreakerState
    CB state: "open" | "half-open" | "closed"
    
    .PARAMETER LastErrorPattern
    Error pattern detected: "rate-limit" | "quota-exceeded" | "auth-failure"
    
    .PARAMETER ElapsedMs
    Elapsed time in milliseconds
    
    .PARAMETER RetryCount
    Number of retries attempted so far
    
    .EXAMPLE
    $rec = Invoke-SyncAdvisor -SubscriptionSize "medium" -FailedStoryCount 21 -CircuitBreakerState "closed"
    Write-Host "Action: $($rec.recommended_action)"
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("small", "medium", "large")]
        [string] $SubscriptionSize,
        
        [Parameter(Mandatory=$true)]
        [int] $FailedStoryCount,
        
        [int] $TotalStories = 21,
        
        [ValidateSet("open", "half-open", "closed")]
        [string] $CircuitBreakerState = "closed",
        
        [ValidateSet("rate-limit", "quota-exceeded", "auth-failure", $null)]
        [string] $LastErrorPattern = $null,
        
        [int] $ElapsedMs = 0,
        
        [int] $RetryCount = 0
    )
    
    Write-Host "[ADVISOR] Requesting recommendation: failed=$FailedStoryCount/$TotalStories, CB=$CircuitBreakerState, pattern=$LastErrorPattern" -ForegroundColor Cyan
    
    try {
        # Build request body
        $requestBody = @{
            subscription_size = $SubscriptionSize
            failed_story_count = $FailedStoryCount
            total_stories = $TotalStories
            cb_state = $CircuitBreakerState
            last_error_pattern = $LastErrorPattern
            elapsed_ms = $ElapsedMs
            retry_count = $RetryCount
        } | ConvertTo-Json
        
        # Call advisor endpoint
        $params = @{
            Uri = "$ADVISOR_ENDPOINT/v1/sync-advisor"
            Method = "POST"
            ContentType = "application/json"
            Body = $requestBody
            TimeoutSec = [math]::Ceiling($ADVISOR_TIMEOUT_MS / 1000)
            ErrorAction = "Stop"
        }
        
        $response = Invoke-RestMethod @params
        
        Write-Host "[ADVISOR] Recommendation received in $(if($response.advisor_latency_ms) { "$($response.advisor_latency_ms)ms" } else { "unknown" }) with confidence $($response.confidence)" -ForegroundColor Green
        
        return [PSCustomObject] $response
        
    } catch {
        Write-Warning "[ADVISOR] Failed to get recommendation: $($_.Exception.Message)"
        Write-Host "[ADVISOR] Falling back to default safe recommendation" -ForegroundColor Yellow
        
        return Invoke-FallbackSyncAdvisor -SubscriptionSize $SubscriptionSize -FailedStoryCount $FailedStoryCount
    }
}


function Invoke-FallbackSyncAdvisor {
    <#
    .SYNOPSIS
    Fallback rules-based advisor when agent is unavailable.
    
    Returns safe default recommendations based on failure pattern.
    #>
    
    [CmdletBinding()]
    param(
        [string] $SubscriptionSize = "medium",
        [int] $FailedStoryCount = 0
    )
    
    $failurePercent = ($FailedStoryCount / 21) * 100
    
    # Rule 1: All failed -> likely transient
    if ($FailedStoryCount -eq 21) {
        return [PSCustomObject] @{
            recommended_action = "retry_all"
            parallelism_level = 1
            guidance = "All stories failed - likely transient issue. Retry with parallelism=1 first."
            confidence = 0.95
            rationale = "100% failure rate suggests service unavailability rather than permissions."
        }
    }
    
    # Rule 2: Partial failures -> retry only failed
    if ($FailedStoryCount -le 3) {
        return [PSCustomObject] @{
            recommended_action = "retry_failed_only"
            parallelism_level = 3
            guidance = "Retry $FailedStoryCount failed stories only, skip $([21 - $FailedStoryCount]) completed."
            confidence = 0.90
            rationale = "Partial failures suggest isolated issues. Use checkpoint to resume."
        }
    }
    
    # Rule 3: Many failed -> pause and increase resources
    if ($failurePercent -gt 50) {
        return [PSCustomObject] @{
            recommended_action = "pause+increase"
            parallelism_level = 1
            guidance = "Pause sync. Increase Cosmos RUs by 25%. Wait 60s before retry."
            confidence = 0.88
            rationale = "High failure rate indicates rate-limit or quota exceeded."
        }
    }
    
    # Default: safe retry
    return [PSCustomObject] @{
        recommended_action = "retry_failed_only"
        parallelism_level = 2
        guidance = "Retry failed stories with reduced parallelism. Monitor for 429 errors."
        confidence = 0.75
        rationale = "Conservative approach for moderate failures."
    }
}


function Emit-AdvisorRecommendationEvent {
    <#
    .SYNOPSIS
    Emit AdvisorRecommendation event to Application Insights.
    
    .PARAMETER Recommendation
    AdvisorRecommendation object from Invoke-SyncAdvisor
    
    .PARAMETER CorrelationId
    Correlation ID for linking to orchestration
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [PSCustomObject] $Recommendation,
        
        [string] $CorrelationId = [Guid]::NewGuid().ToString()
    )
    
    # Non-blocking background event emission
    $job = Start-Job -ScriptBlock {
        param($rec, $cid, $endpoint)
        
        try {
            $eventBody = @{
                event_type = "AdvisorRecommendation"
                action = $rec.recommended_action
                parallelism_level = $rec.parallelism_level
                confidence = $rec.confidence
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
    } -ArgumentList $Recommendation, $CorrelationId, $ADVISOR_ENDPOINT
    
    # Don't wait for result - this is non-blocking
    $null = Remove-Job $job -Force
}


# ============================================================================
# EXPORTS
# ============================================================================

Export-ModuleMember -Function @(
    'Invoke-SyncAdvisor',
    'Invoke-FallbackSyncAdvisor',
    'Emit-AdvisorRecommendationEvent'
)
