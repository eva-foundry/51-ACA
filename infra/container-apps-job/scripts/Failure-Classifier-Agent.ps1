# Failure-Classifier-Agent.ps1
# PowerShell wrapper for ACA-17-001 Failure Classifier Agent
# Provides functions to test connection, invoke classification, and fallback to rules-based classifier

param()

# ============================================================================
# CONFIGURATION
# ============================================================================

$FailureClassifierAgentModule = @{
    PythonScript = "C:\eva-foundry\51-ACA\agents\failure-classifier\classifier_agent.py"
    VenvPython   = "C:\eva-foundry\.venv\Scripts\python.exe"
    TimeoutMs    = 100
    MaxRetries   = 2
}

# ============================================================================
# FALLBACK CLASSIFIER (Rules-Based)
# ============================================================================

function Invoke-RuleBasedClassifier {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ErrorMessage,
        
        [Parameter(Mandatory = $false)]
        [string]$ErrorCode,
        
        [Parameter(Mandatory = $false)]
        [int]$RetryCount = 0,
        
        [Parameter(Mandatory = $false)]
        [int]$ElapsedMs = 0
    )

    $errorMsg = $ErrorMessage.ToLower()
    $errorCode = $ErrorCode.ToLower()

    # Transient patterns
    $transientPatterns = @(
        @{ regex = "timeout|timed out"; confidence = 0.95 },
        @{ regex = "429"; confidence = 0.98 },
        @{ regex = "rate limit"; confidence = 0.98 },
        @{ regex = "503"; confidence = 0.90 },
        @{ regex = "504"; confidence = 0.90 },
        @{ regex = "502"; confidence = 0.80 },
        @{ regex = "dns"; confidence = 0.85 },
        @{ regex = "connection reset|connection refused"; confidence = 0.80 },
        @{ regex = "temporarily unavailable"; confidence = 0.90 },
    )

    # Permanent patterns
    $permanentPatterns = @(
        @{ regex = "403"; confidence = 0.99 },
        @{ regex = "401|unauthorized|not authorized"; confidence = 0.98 },
        @{ regex = "access denied"; confidence = 0.98 },
        @{ regex = "404"; confidence = 0.95 },
        @{ regex = "partition key|invalid partition"; confidence = 0.98 },
        @{ regex = "400"; confidence = 0.90 },
        @{ regex = "invalid credentials"; confidence = 0.98 },
    )

    # Check transient patterns
    foreach ($pattern in $transientPatterns) {
        if ($errorMsg -match $pattern.regex -or $errorCode -match $pattern.regex) {
            return @{
                classification = "transient"
                confidence     = $pattern.confidence
                action         = "retry"
                rationale      = "Pattern '$($pattern.regex)' detected. Transient error."
                latency_ms     = 5
                source         = "rules-based fallback"
            }
        }
    }

    # Check permanent patterns
    foreach ($pattern in $permanentPatterns) {
        if ($errorMsg -match $pattern.regex -or $errorCode -match $pattern.regex) {
            return @{
                classification = "permanent"
                confidence     = $pattern.confidence
                action         = "escalate"
                rationale      = "Pattern '$($pattern.regex)' detected. Permanent error."
                latency_ms     = 5
                source         = "rules-based fallback"
            }
        }
    }

    # Default: assume transient (safe to retry once)
    return @{
        classification = "transient"
        confidence     = 0.50
        action         = "retry"
        rationale      = "Unknown pattern. Assuming transient (safe default)."
        latency_ms     = 5
        source         = "rules-based fallback"
    }
}

# ============================================================================
# TEST CONNECTION
# ============================================================================

function Test-ClassifierConnection {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [int]$TimeoutSeconds = 5
    )

    Write-Host "[INFO] Testing Failure Classifier Agent connection..."

    # Test 1: Check if Python venv exists
    if (-not (Test-Path $FailureClassifierAgentModule.VenvPython)) {
        Write-Warning "Python venv not found at $($FailureClassifierAgentModule.VenvPython)"
        Write-Host "[WARN] Fallback: Rules-based classifier will be used"
        return $false
    }

    # Test 2: Check if classifier script exists
    if (-not (Test-Path $FailureClassifierAgentModule.PythonScript)) {
        Write-Warning "Classifier agent script not found at $($FailureClassifierAgentModule.PythonScript)"
        Write-Host "[WARN] Fallback: Rules-based classifier will be used"
        return $false
    }

    # Test 3: Try to import the agent module (basic syntax check)
    try {
        $testResult = & $FailureClassifierAgentModule.VenvPython `
            -c "import sys; sys.path.insert(0, 'C:\eva-foundry\51-ACA\agents\failure-classifier'); import classifier_agent; print('OK')" `
            2>&1

        if ($testResult -like "*OK*") {
            Write-Host "[INFO] Failure Classifier Agent is ready"
            return $true
        }
    }
    catch {
        Write-Warning "Failed to load classifier agent: $_"
    }

    Write-Host "[WARN] Fallback: Rules-based classifier will be used"
    return $false
}

# ============================================================================
# INVOKE CLASSIFIER (Agent or Fallback)
# ============================================================================

function Invoke-ClassifierAgent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ErrorMessage,
        
        [Parameter(Mandatory = $false)]
        [string]$ErrorCode,
        
        [Parameter(Mandatory = $false)]
        [int]$RetryCount = 0,
        
        [Parameter(Mandatory = $false)]
        [int]$ElapsedMs = 0,
        
        [Parameter(Mandatory = $false)]
        [hashtable]$Context = @{},
        
        [Parameter(Mandatory = $false)]
        [int]$TimeoutMs = $FailureClassifierAgentModule.TimeoutMs
    )

    $startTime = Get-Date

    # If venv not available, use fallback immediately
    if (-not (Test-Path $FailureClassifierAgentModule.VenvPython)) {
        Write-Verbose "[DEBUG] Python venv not available. Using fallback classifier."
        return (Invoke-RuleBasedClassifier -ErrorMessage $ErrorMessage `
                                            -ErrorCode $ErrorCode `
                                            -RetryCount $RetryCount `
                                            -ElapsedMs $ElapsedMs)
    }

    # Try to invoke agent
    try {
        # Create a Python script to run async classify_error
        $pythonCmd = @"
            import sys
            import json
            import asyncio
            sys.path.insert(0, 'C:\eva-foundry\51-ACA\agents\failure-classifier')
            from classifier_agent import classify_error, ErrorContext
            
            # Prepare context
            context = ErrorContext(
                error_message='$ErrorMessage',
                error_code='$ErrorCode',
                retry_count=$RetryCount,
                elapsed_ms=$ElapsedMs,
                context=$([System.Text.Json.JsonSerializer]::Serialize($Context))
            )
            
            # Run classification
            result = asyncio.run(classify_error(context, timeout_ms=$TimeoutMs))
            print(json.dumps(result.to_dict()))
"@

        # Execute with timeout
        # Note: PowerShell Start-Process doesn't have native timeout, so we'll use job with timeout
        $job = Start-Job -ScriptBlock {
            param($python, $script)
            & $python -c $script
        } -ArgumentList $FailureClassifierAgentModule.VenvPython, $pythonCmd

        # Wait with timeout
        $result = Wait-Job -Job $job -Timeout ($TimeoutMs / 1000) -ErrorAction SilentlyContinue
        
        if ($null -eq $result) {
            # Timeout occurred
            Write-Verbose "[DEBUG] Classifier agent timeout (>${TimeoutMs}ms). Using fallback."
            Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
            return (Invoke-RuleBasedClassifier -ErrorMessage $ErrorMessage `
                                                -ErrorCode $ErrorCode `
                                                -RetryCount $RetryCount `
                                                -ElapsedMs $ElapsedMs)
        }

        # Get output
        $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue

        # Parse JSON response
        $classification = $output | ConvertFrom-Json -ErrorAction SilentlyContinue
        
        if ($null -ne $classification) {
            # Add latency measurement
            $elapsedMs = (Get-Date - $startTime).TotalMilliseconds
            $classification | Add-Member -NotePropertyName latency_ms -NotePropertyValue ([int]$elapsedMs) -Force
            $classification | Add-Member -NotePropertyName source -NotePropertyValue "agent-based" -Force
            
            Write-Verbose "[DEBUG] Agent classified: $($classification.classification) (latency: ${elapsedMs}ms)"
            return $classification
        }
    }
    catch {
        Write-Verbose "[DEBUG] Agent error: $_. Using fallback classifier."
    }

    # Fallback
    return (Invoke-RuleBasedClassifier -ErrorMessage $ErrorMessage `
                                        -ErrorCode $ErrorCode `
                                        -RetryCount $RetryCount `
                                        -ElapsedMs $ElapsedMs)
}

# ============================================================================
# GET CLASSIFIER STATUS
# ============================================================================

function Get-ClassifierStatus {
    [CmdletBinding()]
    param()

    $status = @{
        agent_available = Test-ClassifierConnection
        python_venv     = Test-Path $FailureClassifierAgentModule.VenvPython
        agent_script    = Test-Path $FailureClassifierAgentModule.PythonScript
        timeout_ms      = $FailureClassifierAgentModule.TimeoutMs
    }

    return $status
}

# ============================================================================
# EXPORTS
# ============================================================================

Export-ModuleMember -Function @(
    'Test-ClassifierConnection',
    'Invoke-ClassifierAgent',
    'Invoke-RuleBasedClassifier',
    'Get-ClassifierStatus'
)
