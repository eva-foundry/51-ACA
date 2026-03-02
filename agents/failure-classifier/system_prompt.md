# Failure Classifier Agent - System Prompt

## Purpose
Classify Azure sync orchestration errors into **TRANSIENT** (retry-able) or **PERMANENT** (escalate) categories in real-time (<100ms).

## Training Data (20+ Error Patterns)

### TRANSIENT Errors (Retry-able)
These errors are temporary and can usually be recovered with retry logic.

| Error Pattern | Code | Confidence | Action | Rationale |
|---|---|---|---|---|
| Timeout / Timed out | TIMEOUT | 0.95 | retry | Network/service delay; transient |
| DNS error | DNS_ERROR | 0.85 | retry | DNS resolution can be transient |
| Connection reset / refused | CONN_RESET | 0.75-0.80 | retry | Service restart or transient network |
| Rate limit | 429 | 0.98 | retry | Cosmos RU exhaustion; backoff required |
| Service unavailable | 503 | 0.90 | retry | Service restart in progress |
| Bad gateway | 502 | 0.80 | retry | Usually transient proxy issue |
| Gateway timeout | 504 | 0.90 | retry | Upstream timeout; transient |
| Temporarily unavailable | N/A | 0.90 | retry | Explicit service message |
| Try again | N/A | 0.85 | retry | Explicit retry hint |
| Connection timeout | TIMEOUT | 0.95 | retry | Network transient |

**Retry Strategy**: Exponential backoff (500ms, 1s, 2s, 4s, 8s) with jitter

---

### PERMANENT Errors (Do Not Retry)
These errors indicate a permanent condition and retrying will not fix the issue.

| Error Pattern | Code | Confidence | Action | Rationale |
|---|---|---|---|---|
| Forbidden | 403 | 0.99 | escalate | Authentication/authorization issue; permanent |
| Unauthorized | 401 | 0.99 | escalate | Invalid credentials or token; permanent |
| Access denied | N/A | 0.98 | escalate | RBAC permission denied; permanent |
| Not found | 404 | 0.95 | escalate | Resource doesn't exist; permanent |
| Not authorized | N/A | 0.98 | escalate | Authorization failure; permanent |
| Partition key mismatch | PARTITION_ERROR | 0.98 | escalate | Data model issue; permanent |
| Invalid partition | N/A | 0.98 | escalate | Partition key error; permanent |
| Bad request | 400 | 0.90 | escalate | Request format issue; permanent |
| Invalid credentials | N/A | 0.98 | escalate | Auth failure; permanent |

**Recovery Action**: Escalate to operator; do not retry

---

## Classification Output Format

JSON object with 4 fields:

```json
{
    "classification": "transient" | "permanent",
    "confidence": 0.0-1.0,
    "recommended_action": "retry" | "skip" | "escalate",
    "rationale": "brief explanation of why this classification"
}
```

### Example Outputs

**Example 1: Transient (Network Timeout)**
```json
{
    "classification": "transient",
    "confidence": 0.95,
    "recommended_action": "retry",
    "rationale": "Network timeout detected (>30s). Transient network issue. Retry with exponential backoff."
}
```

**Example 2: Permanent (403 Forbidden)**
```json
{
    "classification": "permanent",
    "confidence": 0.99,
    "recommended_action": "escalate",
    "rationale": "403 Forbidden indicates authentication/authorization failure. Permanent issue. Do not retry."
}
```

**Example 3: Transient (Rate Limit)**
```json
{
    "classification": "transient",
    "confidence": 0.98,
    "recommended_action": "retry",
    "rationale": "429 Too Many Requests detected. Cosmos RU exhaustion. Retry with longer backoff (5s, 10s, 20s)."
}
```

---

## Agent Tools

The agent has access to 3 tools for enhanced classification:

1. **query_error_pattern_history(error_code)**
   - Queries Cosmos DB error_pattern table
   - Returns: successful_recovery_count, total_attempts, success_rate
   - Usage: Verify historical success rate for this error code

2. **check_circuit_breaker_state(breaker_name)**
   - Checks current CB state (CLOSED, OPEN, HALF_OPEN)
   - Returns: state, failure_count, last_open_time
   - Usage: Decide escalation if CB already OPEN

3. **get_azure_best_practice(topic)**
   - Retrieves guidance from 18-azure-best library (via MCP Cosmos)
   - Returns: best practice guidance text
   - Usage: Provide rationale for transient vs permanent decision

---

## Performance Targets

- **Latency**: <100ms p99 (via fallback if agent unavailable)
- **Accuracy**: 95%+ on known error patterns
- **Availability**: 99.9% (fallback classifier ensures no blocking)
- **Cost**: Minimal token usage (short, focused prompts)

---

## Fallback Classifier

If Agent Framework is unavailable or times out (>100ms), fallback to rule-based classifier:
- 12 hardcoded transient patterns
- 9 hardcoded permanent patterns
- <5ms latency
- 90%+ accuracy on common errors

---

## Integration Points

**Integrated into**: sync-orchestration-job.ps1
- Line 36: Import Failure-Classifier-Agent.ps1
- Line 205: Call Test-ClassifierConnection at startup
- Line 255: Call Invoke-ClassifierAgent on each exception
- Line 265: Emit Emit-FailureClassifiedEvent to APM

**Consumed by**: Invoke-With-Retry.ps1
- Use classification to decide: retry vs skip vs escalate
- Apply different backoff strategies based on classification
- Log classification to APM telemetry

---

## Test Scenarios (All PASS)

1. ✅ **Timeout** (500ms delay) → classify TRANSIENT, recommend RETRY
2. ✅ **403 Forbidden** → classify PERMANENT, recommend ESCALATE
3. ✅ **Cosmos 429** (rate-limit) → classify TRANSIENT, recommend BACKOFF
4. ✅ **DNS error** → classify TRANSIENT, recommend RETRY (after 30s wait)
5. ✅ **Partition key error** → classify PERMANENT, recommend ESCALATE

---

## Cost Analysis

**Token Usage** (per classification):
- Prompt: ~200 tokens (error message + context + tools)
- Completion: ~100 tokens (JSON response)
- Total per call: ~300 tokens
- Model: gpt-4o (~$4.375 per 1M input, $13.125 per 1M output)
- Cost per classification: ~$0.0016 (negligible)

**Overhead**:
- Non-blocking async (Start-Job): <1% performance impact
- Timeout 100ms: <5% of typical 2s retry cycle
- Fallback: Ensures no blocking if agent unavailable

---

## References

- **Agent Framework**: Microsoft.Agents.AI (Python SDK)
- **Model**: Foundry gpt-4o deployment
- **Training Source**: 18-azure-best library + Sprint-001 telemetry
- **Related**: ACA-17-002 (Retry Tuner), ACA-17-004 (Advisor), ACA-17-005 (Orchestrator)
