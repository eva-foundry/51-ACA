# Application-Insights-Logger.ps1 -- APM telemetry and observability
# Purpose: Emit metrics, events, traces to Application Insights
# Enables dashboards, alerts, and operational visibility

class AppInsightsEvent {
    [string]$Name                           # Event name (e.g., "SyncStart", "SyncComplete")
    [DateTime]$Timestamp
    [hashtable]$Properties = @{}            # Custom properties (string)
    [hashtable]$Measurements = @{}          # Numeric metrics (double)
    [string]$InstrumentationKey
    [string]$AppInsightsEndpoint = "https://dc.applicationinsights.azure.com/v2/track"
    
    AppInsightsEvent([string]$name, [string]$key) {
        $this.Name = $name
        $this.Timestamp = Get-Date -AsUTC
        $this.InstrumentationKey = $key
    }
    
    [void]AddProperty([string]$name, [string]$value) {
        $this.Properties[$name] = $value
    }
    
    [void]AddMeasurement([string]$name, [double]$value) {
        $this.Measurements[$name] = $value
    }
    
    [hashtable]ToJSON() {
        return @{
            name = "Microsoft.ApplicationInsights.$(($this.InstrumentationKey -split '-')[0]).Event"
            time = $this.Timestamp.ToString("o")
            iKey = $this.InstrumentationKey
            data = @{
                baseType = "EventData"
                baseData = @{
                    ver = 2
                    name = $this.Name
                    properties = $this.Properties
                    measurements = $this.Measurements
                }
            }
        }
    }
}

function Test-AppInsightsConnection {
    <#
    .SYNOPSIS
    Test connection to Application Insights
    
    .DESCRIPTION
    Verifies that telemetry endpoint is reachable and instrumentation key is valid.
    
    .PARAMETER InstrumentationKey
    Application Insights instrumentation key (from Key Vault)
    
    .PARAMETER LogFunction
    Optional log function (if provided, logs are emitted; else silent)
    
    .EXAMPLE
    Test-AppInsightsConnection -InstrumentationKey "12345678-1234-1234-1234-123456789012"
    
    Returns: @{ success=$true; status="healthy"; latency=$ms }
    #>
    param(
        [string]$InstrumentationKey,
        [scriptblock]$LogFunction
    )
    
    try {
        if (-not $InstrumentationKey -or $InstrumentationKey -eq "") {
            return @{ success = $false; error = "Instrumentation key not provided" }
        }
        
        # Test a simple ping event
        $event = [AppInsightsEvent]::new("HealthCheck", $InstrumentationKey)
        $event.AddProperty("component", "sync-orchestrator")
        $event.AddProperty("test", "true")
        $event.AddMeasurement("latency_ms", 0)
        
        $timer = [System.Diagnostics.Stopwatch]::StartNew()
        $payload = $event.ToJSON() | ConvertTo-Json -Depth 10 -Compress
        
        # Attempt to send (non-blocking, timeout 5s)
        $response = $null
        try {
            $response = Invoke-RestMethod -Uri $event.AppInsightsEndpoint `
                -Method POST `
                -ContentType "application/json" `
                -Body $payload `
                -Headers @{ "Content-Encoding" = "gzip"; } `
                -TimeoutSec 5 `
                -ErrorAction SilentlyContinue
            $timer.Stop()
        } catch {
            $timer.Stop()
            # Connection attempt failed, but not a critical error
            & $LogFunction "AppInsights endpoint unreachable (non-blocking): $($_.Exception.Message)" "WARN" -ErrorAction SilentlyContinue
            return @{ success = $false; error = "Endpoint unreachable"; latency = $timer.ElapsedMilliseconds }
        }
        
        & $LogFunction "AppInsights connection test: OK (latency: $($timer.ElapsedMilliseconds)ms)" "PASS" -ErrorAction SilentlyContinue
        
        return @{
            success = $true
            status = "healthy"
            latency = $timer.ElapsedMilliseconds
            endpoint = $event.AppInsightsEndpoint
        }
    } catch {
        & $LogFunction "AppInsights connection test failed: $($_.Exception.Message)" "FAIL" -ErrorAction SilentlyContinue
        return @{ success = $false; error = $_.Exception.Message }
    }
}

function Emit-SyncStartEvent {
    <#
    .SYNOPSIS
    Emit telemetry event: Sync orchestration started
    
    .PARAMETER CorrelationId
    Correlation ID for tracing entire sync run
    
    .PARAMETER TotalStories
    Total number of stories to sync
    
    .PARAMETER ResumeFromIndex
    0-based index if resuming from checkpoint
    
    .PARAMETER InstrumentationKey
    AppInsights instrumentation key
    
    .PARAMETER LogFunction
    Optional log function
    #>
    param(
        [string]$CorrelationId,
        [int]$TotalStories,
        [int]$ResumeFromIndex = 0,
        [string]$InstrumentationKey,
        [scriptblock]$LogFunction
    )
    
    try {
        if (-not $InstrumentationKey) {
            & $LogFunction "AppInsights key not configured, skipping telemetry" "DEBUG" -ErrorAction SilentlyContinue
            return @{ success = $false; error = "No instrumentation key" }
        }
        
        $event = [AppInsightsEvent]::new("SyncOrchestrationStart", $InstrumentationKey)
        $event.AddProperty("correlationId", $CorrelationId)
        $event.AddProperty("resumeMode", $(if ($ResumeFromIndex -gt 0) { "true" } else { "false" }))
        $event.AddProperty("environment", $env:ENVIRONMENT ?? "dev")
        $event.AddMeasurement("totalStories", $TotalStories)
        $event.AddMeasurement("resumeFromIndex", $ResumeFromIndex)
        
        $payload = $event.ToJSON() | ConvertTo-Json -Depth 10 -Compress
        
        # Non-blocking send (background job to avoid delaying orchestration)
        Start-Job -ScriptBlock {
            param($uri, $body)
            try {
                Invoke-RestMethod -Uri $using:event.AppInsightsEndpoint `
                    -Method POST `
                    -ContentType "application/json" `
                    -Body $body `
                    -TimeoutSec 5 `
                    -ErrorAction SilentlyContinue | Out-Null
            } catch { }
        } -ArgumentList @($event.AppInsightsEndpoint, $payload) | Out-Null
        
        & $LogFunction "Emitted: SyncOrchestrationStart (correlationId=$CorrelationId)" "DEBUG" -ErrorAction SilentlyContinue
        return @{ success = $true }
    } catch {
        return @{ success = $false; error = $_.Exception.Message }
    }
}

function Emit-SyncCompleteEvent {
    <#
    .SYNOPSIS
    Emit telemetry event: Sync orchestration completed
    
    .PARAMETER CorrelationId
    Correlation ID for tracing
    
    .PARAMETER SuccessCount
    Number of stories successfully synced
    
    .PARAMETER FailureCount
    Number of stories that failed
    
    .PARAMETER DurationMs
    Total duration in milliseconds
    
    .PARAMETER RetryStats
    Hashtable with retry metrics (totalRetries, successAfterRetry, failedAfterRetries)
    
    .PARAMETER CircuitBreakerState
    Current circuit breaker state (CLOSED/OPEN/HALF_OPEN)
    
    .PARAMETER InstrumentationKey
    AppInsights instrumentation key
    #>
    param(
        [string]$CorrelationId,
        [int]$SuccessCount,
        [int]$FailureCount,
        [int]$DurationMs,
        [hashtable]$RetryStats,
        [string]$CircuitBreakerState,
        [string]$InstrumentationKey,
        [scriptblock]$LogFunction
    )
    
    try {
        if (-not $InstrumentationKey) { return @{ success = $false } }
        
        $event = [AppInsightsEvent]::new("SyncOrchestrationComplete", $InstrumentationKey)
        $event.AddProperty("correlationId", $CorrelationId)
        $event.AddProperty("circuitBreakerState", $CircuitBreakerState)
        $event.AddProperty("environment", $env:ENVIRONMENT ?? "dev")
        $event.AddMeasurement("successCount", $SuccessCount)
        $event.AddMeasurement("failureCount", $FailureCount)
        $event.AddMeasurement("durationMs", $DurationMs)
        $event.AddMeasurement("totalRetries", $RetryStats.totalRetries ?? 0)
        $event.AddMeasurement("successAfterRetry", $RetryStats.successAfterRetry ?? 0)
        $event.AddMeasurement("failedAfterRetries", $RetryStats.failedAfterRetries ?? 0)
        $event.AddMeasurement("successRate", $([math]::Round(($SuccessCount / ($SuccessCount + $FailureCount)) * 100, 2)))
        
        $payload = $event.ToJSON() | ConvertTo-Json -Depth 10 -Compress
        
        # Non-blocking send
        Start-Job -ScriptBlock {
            param($uri, $body)
            try {
                Invoke-RestMethod -Uri $using:event.AppInsightsEndpoint `
                    -Method POST -ContentType "application/json" -Body $body `
                    -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
            } catch { }
        } -ArgumentList @($event.AppInsightsEndpoint, $payload) | Out-Null
        
        & $LogFunction "Emitted: SyncOrchestrationComplete (success=$SuccessCount, failed=$FailureCount, duration=${DurationMs}ms)" "DEBUG" -ErrorAction SilentlyContinue
        return @{ success = $true }
    } catch {
        return @{ success = $false }
    }
}

function Emit-CircuitBreakerStateChange {
    <#
    .SYNOPSIS
    Emit telemetry event: Circuit breaker state transitioned
    
    .PARAMETER CircuitBreakerName
    Name of circuit breaker (e.g., "cosmos-sync", "health-check")
    
    .PARAMETER PreviousState
    State before change (CLOSED, OPEN, or HALF_OPEN)
    
    .PARAMETER NewState
    State after change
    
    .PARAMETER FailureCount
    Current failure count (for FAIL thresholds)
    
    .PARAMETER CorrelationId
    Correlation ID for tracing
    #>
    param(
        [string]$CircuitBreakerName,
        [string]$PreviousState,
        [string]$NewState,
        [int]$FailureCount,
        [string]$CorrelationId,
        [string]$InstrumentationKey,
        [scriptblock]$LogFunction
    )
    
    try {
        if (-not $InstrumentationKey) { return @{ success = $false } }
        
        $event = [AppInsightsEvent]::new("CircuitBreakerStateChange", $InstrumentationKey)
        $event.AddProperty("circuitBreakerName", $CircuitBreakerName)
        $event.AddProperty("previousState", $PreviousState)
        $event.AddProperty("newState", $NewState)
        $event.AddProperty("correlationId", $CorrelationId)
        $event.AddProperty("transition", "$PreviousState->$NewState")
        $event.AddMeasurement("failureCount", $FailureCount)
        
        $payload = $event.ToJSON() | ConvertTo-Json -Depth 10 -Compress
        Start-Job -ScriptBlock {
            try { Invoke-RestMethod -Uri $using:event.AppInsightsEndpoint `
                -Method POST -ContentType "application/json" -Body $body `
                -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
            } catch { }
        } | Out-Null
        
        & $LogFunction "Emitted: CircuitBreakerStateChange ($CircuitBreakerName: $PreviousState->$NewState)" "DEBUG" -ErrorAction SilentlyContinue
        return @{ success = $true }
    } catch {
        return @{ success = $false }
    }
}

function Emit-CheckpointEvent {
    <#
    .SYNOPSIS
    Emit telemetry event: Checkpoint saved or loaded
    
    .PARAMETER EventType
    "saved" or "loaded"
    
    .PARAMETER StoryId
    Last successful story ID
    
    .PARAMETER CompletedCount
    Stories completed so far
    
    .PARAMETER TotalExpected
    Total expected stories
    
    .PARAMETER CorrelationId
    Correlation ID
    #>
    param(
        [string]$EventType,
        [string]$StoryId,
        [int]$CompletedCount,
        [int]$TotalExpected,
        [string]$CorrelationId,
        [string]$InstrumentationKey,
        [scriptblock]$LogFunction
    )
    
    try {
        if (-not $InstrumentationKey) { return @{ success = $false } }
        
        $event = [AppInsightsEvent]::new("CheckpointEvent", $InstrumentationKey)
        $event.AddProperty("eventType", $EventType)
        $event.AddProperty("storyId", $StoryId)
        $event.AddProperty("correlationId", $CorrelationId)
        $event.AddMeasurement("completedCount", $CompletedCount)
        $event.AddMeasurement("totalExpected", $TotalExpected)
        $event.AddMeasurement("progressPercent", [math]::Round(($CompletedCount / $TotalExpected) * 100, 2))
        
        $payload = $event.ToJSON() | ConvertTo-Json -Depth 10 -Compress
        Start-Job -ScriptBlock {
            try { Invoke-RestMethod -Uri $using:event.AppInsightsEndpoint `
                -Method POST -ContentType "application/json" -Body $body `
                -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
            } catch { }
        } | Out-Null
        
        & $LogFunction "Emitted: CheckpointEvent ($EventType, $CompletedCount/$TotalExpected)" "DEBUG" -ErrorAction SilentlyContinue
        return @{ success = $true }
    } catch {
        return @{ success = $false }
    }
}

function Emit-FailureClassifiedEvent {
    <#
    .SYNOPSIS
    Emit error classification event to Application Insights (ACA-17-001)
    
    .DESCRIPTION
    Logs when Failure Classifier Agent has classified an error as transient or permanent.
    
    .EXAMPLE
    Emit-FailureClassifiedEvent -ErrorCode "429" -Classification "transient" -Confidence 0.98 `
        -RecommendedAction "retry" -CorrelationId "..." -InstrumentationKey "..."
    #>
    param(
        [string]$ErrorCode,
        [string]$Classification,            # "transient" | "permanent"
        [double]$Confidence,                # 0.0-1.0
        [string]$RecommendedAction,         # "retry" | "skip" | "escalate"
        [string]$CorrelationId,
        [string]$InstrumentationKey,
        [scriptblock]$LogFunction
    )
    
    try {
        if ([string]::IsNullOrEmpty($InstrumentationKey)) {
            return @{ success = $false }
        }
        
        $event = [AppInsightsEvent]::new("FailureClassified", $InstrumentationKey)
        $event.AddProperty("errorCode", $ErrorCode)
        $event.AddProperty("classification", $Classification)
        $event.AddProperty("recommendedAction", $RecommendedAction)
        $event.AddProperty("correlationId", $CorrelationId)
        $event.AddMeasurement("confidence", $Confidence)
        
        $body = $event.ToJSON() | ConvertTo-Json -Depth 10 -Compress
        Start-Job -ScriptBlock {
            try {
                Invoke-RestMethod -Uri $using:event.AppInsightsEndpoint `
                    -Method POST -ContentType "application/json" -Body $body `
                    -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
            } catch { }
        } | Out-Null
        
        & $LogFunction "Emitted: FailureClassifiedEvent ($Classification, action: $RecommendedAction, confidence: $Confidence)" "DEBUG" -ErrorAction SilentlyContinue
        return @{ success = $true }
    } catch {
        return @{ success = $false }
    }
}

function Get-AppInsightsStatus {
    <#
    .SYNOPSIS
    Get Application Insights telemetry health status
    
    .DESCRIPTION
    Returns count of failed sends, pending jobs, last event sent.
    
    .EXAMPLE
    Get-AppInsightsStatus
    
    Returns: @{ pendingJobs=$count; configured=$bool; lastEvent=$timestamp }
    #>
    param([string]$InstrumentationKey)
    
    try {
        $pendingJobs = @(Get-Job -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Running" }).Count
        
        return @{
            configured = (-not [string]::IsNullOrEmpty($InstrumentationKey))
            pendingJobs = $pendingJobs
            status = if ($pendingJobs -eq 0) { "idle" } else { "busy" }
        }
    } catch {
        return @{ error = $_.Exception.Message }
    }
}
