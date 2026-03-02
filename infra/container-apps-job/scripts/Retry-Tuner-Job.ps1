function Emit-RetryTunedEvent {
    <#
    .SYNOPSIS
    Emit retry tuning decision event to Application Insights (ACA-17-002)
    
    .DESCRIPTION
    Logs when Retry Tuning Agent has tuned a retry strategy (selected delay, strategy, etc).
    
    .EXAMPLE
    Emit-RetryTunedEvent -ErrorCode "429" -NextDelayMs 5000 -Strategy "rate-limit-backoff" `
        -SuccessProbability 0.95 -CorrelationId "..." -InstrumentationKey "..."
    #>
    param(
        [string]$ErrorCode,
        [int]$NextDelayMs,
        [string]$Strategy,                  # "exponential" | "rate-limit-backoff" | "maintenance-wait" | "permanent-skip"
        [double]$SuccessProbability,        # 0.0-1.0
        [string]$RecommendedAction,         # "retry" | "skip" | "escalate"
        [int]$RetryAttempt,
        [string]$CorrelationId,
        [string]$InstrumentationKey,
        [scriptblock]$LogFunction
    )
    
    try {
        if ([string]::IsNullOrEmpty($InstrumentationKey)) {
            return @{ success = $false }
        }
        
        $event = [AppInsightsEvent]::new("RetryTuned", $InstrumentationKey)
        $event.AddProperty("errorCode", $ErrorCode)
        $event.AddProperty("strategy", $Strategy)
        $event.AddProperty("recommendedAction", $RecommendedAction)
        $event.AddProperty("correlationId", $CorrelationId)
        $event.AddProperty("retryAttempt", $RetryAttempt)
        $event.AddMeasurement("nextDelayMs", $NextDelayMs)
        $event.AddMeasurement("successProbability", $SuccessProbability)
        
        $body = $event.ToJSON() | ConvertTo-Json -Depth 10 -Compress
        Start-Job -ScriptBlock {
            try {
                Invoke-RestMethod -Uri $using:event.AppInsightsEndpoint `
                    -Method POST -ContentType "application/json" -Body $body `
                    -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
            } catch { }
        } | Out-Null
        
        & $LogFunction "Emitted: RetryTunedEvent (strategy: $Strategy, delay: ${NextDelayMs}ms, action: $RecommendedAction)" "DEBUG" -ErrorAction SilentlyContinue
        return @{ success = $true }
    } catch {
        return @{ success = $false }
    }
}

function Invoke-RetryTuner {
    <#
    .SYNOPSIS
    Invoke the Retry Tuning Agent to get optimal retry delay
    
    .DESCRIPTION
    Sends error context to the Retry Tuner Agent (HTTP endpoint or Python agent).
    Returns tuned delay and strategy.
    
    .EXAMPLE
    $decision = Invoke-RetryTuner -ErrorCode "429" -Classification "transient" `
        -RetryCount 2 -CircuitBreakerState "CLOSED" -TimeoutMs 200
    
    # Returns: @{ 
    #     nextDelayMs = 10000
    #     strategy = "rate-limit-backoff"
    #     recommendedAction = "retry"
    #     successProbability = 0.95
    #     rationale = "..."
    # }
    #>
    param(
        [string]$ErrorCode,
        [string]$Classification,            # "transient" | "permanent"
        [int]$RetryCount = 0,
        [int]$LastDelayMs = 0,
        [int]$TotalElapsedMs = 0,
        [string]$CircuitBreakerState = "CLOSED",
        [string]$SubscriptionSize = "medium",
        [int]$TimeoutMs = 200,
        [string]$AgentEndpoint = "http://localhost:8081"  # Can override in tests
    )
    
    $context = @{
        error_code               = $ErrorCode
        error_classification     = $Classification
        retry_count              = $RetryCount
        last_delay_ms            = $LastDelayMs
        total_elapsed_ms         = $TotalElapsedMs
        circuit_breaker_state    = $CircuitBreakerState
        subscription_size        = $SubscriptionSize
    }
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$AgentEndpoint/v1/retry-tune" `
            -Method POST `
            -ContentType "application/json" `
            -Body ($context | ConvertTo-Json) `
            -TimeoutSec ($TimeoutMs / 1000) `
            -ErrorAction SilentlyContinue
        
        if ($response) {
            return @{
                nextDelayMs             = $response.next_delay_ms
                strategy                = $response.tuning_strategy
                recommendedAction       = $response.recommended_action
                successProbability      = $response.estimated_success_probability
                tuningConfidence        = $response.tuning_confidence
                rationale               = $response.rationale
                tuningLatencyMs         = $response.tuning_latency_ms
            }
        }
    } catch {
        # Fallback to rules-based tuning if agent unavailable
    }
    
    # Fallback: rules-based tuning (same logic as Python fallback)
    return Invoke-FallbackRetryTuner -ErrorCode $ErrorCode `
        -Classification $Classification `
        -RetryCount $RetryCount `
        -CircuitBreakerState $CircuitBreakerState
}

function Invoke-FallbackRetryTuner {
    <#
    .SYNOPSIS
    Rules-based fallback when Retry Tuning Agent is unavailable
    
    .DESCRIPTION
    Implements static backoff strategies without agent involvement.
    #>
    param(
        [string]$ErrorCode,
        [string]$Classification,
        [int]$RetryCount = 0,
        [string]$CircuitBreakerState = "CLOSED"
    )
    
    # Permanent failures: no retry
    if ($Classification -eq "permanent") {
        return @{
            nextDelayMs        = 0
            strategy           = "permanent-skip"
            recommendedAction  = "skip"
            successProbability = 0.05
            rationale          = "Permanent failure classification. Skipping remaining retries."
        }
    }
    
    # Circuit breaker OPEN: escalate
    if ($CircuitBreakerState -eq "OPEN") {
        return @{
            nextDelayMs        = 0
            strategy           = "exponential"
            recommendedAction  = "escalate"
            successProbability = 0.10
            rationale          = "Circuit breaker OPEN. System unhealthy. Escalate."
        }
    }
    
    # Rate limit (429): longer delays
    if ($ErrorCode -eq "429") {
        $delays = @(5000, 10000, 20000, 30000)
        $nextDelay = if ($RetryCount -lt $delays.Count) { $delays[$RetryCount] } else { $delays[-1] }
        
        return @{
            nextDelayMs        = $nextDelay
            strategy           = "rate-limit-backoff"
            recommendedAction  = "retry"
            successProbability = 0.90
            rationale          = "Rate-limit error. Using extended backoff: ${nextDelay}ms."
        }
    }
    
    # Default transient: exponential backoff
    $delays = @(500, 1000, 2000, 4000, 8000)
    $nextDelay = if ($RetryCount -lt $delays.Count) { $delays[$RetryCount] } else { $delays[-1] }
    $successProb = [Math]::Max(0.10, 0.95 - ($RetryCount * 0.05))
    
    return @{
        nextDelayMs        = $nextDelay
        strategy           = "exponential"
        recommendedAction  = "retry"
        successProbability = $successProb
        rationale          = "Transient error. Using exponential backoff: ${nextDelay}ms."
    }
}
