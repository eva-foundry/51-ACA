# Invoke-With-Retry.ps1
# Retry Logic with Exponential Backoff + Jitter
# Used by: sync-orchestration-job.ps1 for all Cosmos + HTTP operations
# EVA-STORY: ACA-16-002

<#
.SYNOPSIS
Invokes a script block with automatic retry on transient failures.

.DESCRIPTION
Implements exponential backoff retry logic with jitter to handle transient failures
(network timeouts, rate limits, temporary service unavailability).

Backoff formula:
  delay_ms = (baseDelay_ms * 2^(attempt-1)) + random_jitter(0-100ms)

Example progression (baseDelay=1000ms):
  Attempt 1 fails → wait 1000-1100ms → retry
  Attempt 2 fails → wait 2000-2100ms → retry
  Attempt 3 fails → wait 4000-4100ms → retry (or fail)

.PARAMETER ScriptBlock
The script block to invoke. Should throw on failure.

.PARAMETER MaxAttempts
Maximum number of attempts (default: 3, range: 1-5)

.PARAMETER BaseDelayMs
Base delay in milliseconds (default: 1000)

.PARAMETER OperationName
Human-readable operation name for logging.

.PARAMETER LogFunction
Optional logging function (receives $Level and $Message).
Default: Write-Host

.EXAMPLE
$result = Invoke-WithRetry -ScriptBlock {
    Invoke-RestMethod "https://api.example.com/data"
} -MaxAttempts 3 -BaseDelayMs 1000 -OperationName "FetchData"

.NOTES
- Circuit breaker should be checked BEFORE calling this function
- Does NOT log to APM (caller should emit telemetry for failures)
- Jitter prevents thundering herd problem
#>

param(
    [Parameter(Mandatory = $true)]
    [scriptblock]$ScriptBlock,
    
    [Parameter(Mandatory = $false)]
    [int]$MaxAttempts = 3,
    
    [Parameter(Mandatory = $false)]
    [int]$BaseDelayMs = 1000,
    
    [Parameter(Mandatory = $false)]
    [string]$OperationName = "Operation",
    
    [Parameter(Mandatory = $false)]
    [scriptblock]$LogFunction = $null
)

# Use Write-Host if no logger provided
if ($null -eq $LogFunction) {
    $LogFunction = { param($Level, $Message)
        $timestamp = Get-Date -Format "HH:mm:ss.fff"
        Write-Host "[$timestamp] [$Level] $Message"
    }
}

# Input validation
if ($MaxAttempts -lt 1 -or $MaxAttempts -gt 5) {
    & $LogFunction "WARN" "MaxAttempts=$MaxAttempts adjusted to valid range [1-5]"
    $MaxAttempts = [Math]::Max(1, [Math]::Min(5, $MaxAttempts))
}

if ($BaseDelayMs -lt 0) {
    & $LogFunction "WARN" "BaseDelayMs=$BaseDelayMs adjusted to 1000"
    $BaseDelayMs = 1000
}

$attempt = 0
$lastError = $null

while ($attempt -lt $MaxAttempts) {
    $attempt++
    
    try {
        & $LogFunction "DEBUG" "$OperationName : Attempt $attempt/$MaxAttempts"
        
        # Execute the operation
        $result = & $ScriptBlock
        
        # Success
        if ($attempt -gt 1) {
            & $LogFunction "INFO" "$OperationName : Succeeded after $attempt attempts"
        } else {
            & $LogFunction "DEBUG" "$OperationName : Succeeded on first attempt"
        }
        
        return $result
        
    } catch {
        $lastError = $_
        $errorMsg = $_.Exception.Message
        
        & $LogFunction "WARN" "$OperationName : Attempt $attempt failed: $errorMsg"
        
        if ($attempt -lt $MaxAttempts) {
            # Calculate backoff delay
            # Formula: baseDelay * 2^(attempt-1) + jitter
            $exponentialDelay = $BaseDelayMs * [Math]::Pow(2, $attempt - 1)
            $jitter = Get-Random -Minimum 0 -Maximum 100
            $totalDelay = [int]($exponentialDelay + $jitter)
            
            & $LogFunction "INFO" "$OperationName : Backing off ${totalDelay}ms before retry (exponential: ${exponentialDelay}ms + jitter: ${jitter}ms)"
            
            Start-Sleep -Milliseconds $totalDelay
            
            # Check circuit breaker (if available in caller's scope)
            # Note: Caller must implement circuit breaker check
            
        } else {
            & $LogFunction "ERROR" "$OperationName : Failed after $MaxAttempts attempts"
        }
    }
}

# All retries exhausted
& $LogFunction "FAIL" "$OperationName : Exhausted all $MaxAttempts attempts, giving up"
throw $lastError

# EOF
