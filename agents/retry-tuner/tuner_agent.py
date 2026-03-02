"""
ACA-17-002: Intelligent Retry Tuning Agent
Adaptive backoff strategy based on learned error patterns (vs static exponential).

This agent uses Microsoft Agent Framework with Azure AI Foundry to recommend optimal
retry delays based on historical error patterns, scheduled maintenance windows, and
current circuit breaker state.

System Prompt: Trained on retry patterns from 18-azure-best + Sprint-001 telemetry.
Output: Tuned backoff schedule with confidence and rationale.
"""

import os
import json
import asyncio
import logging
from typing import Optional, Annotated
from dataclasses import dataclass, field
from datetime import datetime

# Agent Framework imports
from agent_framework.azure import AzureAIClient
from azure.identity.aio import DefaultAzureCredential

# Logging setup
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class RetryTuneContext:
    """Input context for retry tuning."""
    error_code: str
    error_classification: str  # "transient" | "permanent"
    retry_count: int
    last_delay_ms: int = 0
    total_elapsed_ms: int = 0
    failure_count_in_batch: int = 0
    circuit_breaker_state: str = "CLOSED"  # CLOSED | OPEN | HALF_OPEN
    subscription_size: str = "medium"  # small | medium | large | xlarge
    timestamp: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "error_classification": self.error_classification,
            "retry_count": self.retry_count,
            "last_delay_ms": self.last_delay_ms,
            "total_elapsed_ms": self.total_elapsed_ms,
            "failure_count_in_batch": self.failure_count_in_batch,
            "circuit_breaker_state": self.circuit_breaker_state,
            "subscription_size": self.subscription_size,
            "timestamp": self.timestamp or datetime.utcnow().isoformat(),
        }


@dataclass
class RetryDecision:
    """Output retry tuning decision."""
    next_delay_ms: int
    estimated_success_probability: float  # 0.0-1.0
    recommended_action: str  # "retry" | "skip" | "escalate"
    rationale: str
    tuning_strategy: str  # "exponential" | "rate-limit-backoff" | "maintenance-wait" | "permanent-skip"
    tuning_confidence: float  # 0.0-1.0
    tuning_latency_ms: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "next_delay_ms": self.next_delay_ms,
            "estimated_success_probability": self.estimated_success_probability,
            "recommended_action": self.recommended_action,
            "rationale": self.rationale,
            "tuning_strategy": self.tuning_strategy,
            "tuning_confidence": self.tuning_confidence,
            "tuning_latency_ms": self.tuning_latency_ms,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ============================================================================
# FALLBACK RETRY TUNER (Rules-Based)
# ============================================================================


def fallback_retry_tuner(context: RetryTuneContext) -> RetryDecision:
    """
    Rules-based fallback retry tuner for when the agent is unavailable.
    Uses static exponential backoff with rate-limit and permanent failure handling.
    """
    
    # Permanent failures: skip remaining retries
    if context.error_classification == "permanent":
        return RetryDecision(
            next_delay_ms=0,
            estimated_success_probability=0.05,
            recommended_action="skip",
            rationale="Permanent failure classification. Skipping remaining retries.",
            tuning_strategy="permanent-skip",
            tuning_confidence=0.98,
            tuning_latency_ms=3,
        )
    
    # Circuit breaker OPEN: escalate instead of retry
    if context.circuit_breaker_state == "OPEN":
        return RetryDecision(
            next_delay_ms=0,
            estimated_success_probability=0.10,
            recommended_action="escalate",
            rationale="Circuit breaker OPEN. System unhealthy. Escalate instead of retry.",
            tuning_strategy="exponential",
            tuning_confidence=0.95,
            tuning_latency_ms=3,
        )
    
    # Rate-limit (429) errors: longer backoff (vs default exponential)
    if context.error_code == "429":
        # Sequence: 5s, 10s, 20s, 30s (longer than default 500ms, 1s, 2s, 4s)
        delays = [5000, 10000, 20000, 30000]
        next_delay = delays[min(context.retry_count, len(delays) - 1)]
        
        return RetryDecision(
            next_delay_ms=next_delay,
            estimated_success_probability=0.90,  # 429 usually recovers with longer wait
            recommended_action="retry",
            rationale=f"Rate-limit error (429). Using extended backoff: {next_delay}ms.",
            tuning_strategy="rate-limit-backoff",
            tuning_confidence=0.95,
            tuning_latency_ms=3,
        )
    
    # Default transient: standard exponential backoff
    # Sequence: 500ms, 1s, 2s, 4s, 8s (from ACA-16-002)
    delays = [500, 1000, 2000, 4000, 8000]
    next_delay = delays[min(context.retry_count, len(delays) - 1)]
    
    # Adjust success probability based on retry count
    success_prob = 0.95 - (context.retry_count * 0.05)  # Decrease confidence as retries increase
    success_prob = max(success_prob, 0.10)  # Floor at 10%
    
    return RetryDecision(
        next_delay_ms=next_delay,
        estimated_success_probability=success_prob,
        recommended_action="retry",
        rationale=f"Transient error. Using exponential backoff: {next_delay}ms.",
        tuning_strategy="exponential",
        tuning_confidence=0.85,
        tuning_latency_ms=3,
    )


# ============================================================================
# TOOLS FOR AGENT
# ============================================================================


def query_error_pattern_success_rate(
    error_code: Annotated[str, "Error code (e.g., '429', '503', 'timeout')."]
) -> str:
    """
    Query historical success rate for this error type from Cosmos error_pattern table.
    Returns success probability after retry.
    
    In production, this would query Cosmos:
      SELECT successful_recovery_count / total_attempts AS success_rate
      FROM error_pattern WHERE error_code = @code
    """
    
    # Simulated historical data (production: query Cosmos db.error_pattern)
    history = {
        "429": {"success_rate": 0.95, "total_retries": 1450, "recovery_time_ms": 5000},
        "503": {"success_rate": 0.88, "total_retries": 320, "recovery_time_ms": 2000},
        "timeout": {"success_rate": 0.92, "total_retries": 890, "recovery_time_ms": 2000},
        "connection_reset": {"success_rate": 0.85, "total_retries": 450, "recovery_time_ms": 1000},
        "dns": {"success_rate": 0.80, "total_retries": 200, "recovery_time_ms": 3000},
    }
    
    data = history.get(
        error_code,
        {"success_rate": 0.70, "total_retries": 0, "recovery_time_ms": 1000},
    )
    return json.dumps(data)


def check_maintenance_window(
    error_code: Annotated[str, "Error code that triggered the failure."],
    subscription_id: Annotated[str, "Azure subscription ID (for context)."] = "unknown",
) -> str:
    """
    Check if there's a scheduled maintenance window in progress that explains the error.
    Returns maintenance window status if applicable.
    
    In production, this would query the runbooks layer via Cosmos.
    """
    
    # Simulated maintenance windows
    maintenance = {
        "active": False,
        "window_close_time": None,
        "affected_services": [],
    }
    
    return json.dumps(maintenance)


def estimate_retry_success(
    error_code: Annotated[str, "Error code."],
    retry_count: Annotated[int, "Current retry attempt number (0-based)."],
    elapsed_ms: Annotated[int, "Total elapsed time in milliseconds."],
) -> str:
    """
    Estimate probability of success on the next retry based on error type and context.
    Returns success probability (0.0-1.0).
    """
    
    # Base probabilities by error type
    base_probs = {
        "429": 0.95,      # Rate limits almost always recover
        "503": 0.88,      # Service unavailable usually temporary
        "timeout": 0.92,  # Timeouts often transient
        "connection_reset": 0.85,
        "dns": 0.80,
    }
    
    base_prob = base_probs.get(error_code, 0.70)
    
    # Decay probability with retry attempts (diminishing returns)
    decay = max(0.0, 1.0 - (retry_count * 0.1))
    estimated_prob = base_prob * decay
    
    return json.dumps({
        "estimated_success_probability": estimated_prob,
        "rationale": f"Base probability {base_prob:.2f} adjusted for {retry_count} retries.",
    })


async def create_retry_tuner_agent(
    project_endpoint: str,
    model_deployment: str,
) -> object:
    """
    Create the Retry Tuning Agent using Agent Framework.
    
    Args:
        project_endpoint: Azure AI Foundry project endpoint
        model_deployment: Model deployment name (e.g., 'gpt-4o')
    
    Returns:
        Agent object for running async prompts
    """
    
    system_prompt = """You are a Retry Tuning AI agent. Your role is to recommend optimal retry delays
for failures in Azure sync orchestration. Instead of using static exponential backoff, you adapt delays
based on error patterns and historical success rates.

## Decision Framework

### For PERMANENT failures (e.g., 403, 404, auth errors):
- Recommend SKIP (do not retry)
- Set delay_ms = 0
- Return estimated success probability = 0.05

### For RATE LIMIT errors (429):
- Use LONGER backoff than standard exponential: 5s, 10s, 20s, 30s
- Check historical success rate (usually 95%+ after waiting)
- Recommend RETRY with long delay

### For TRANSIENT errors (timeout, 503, connection reset):
- Use standard exponential backoff: 500ms, 1s, 2s, 4s, 8s
- Check historical success rate to estimate next success probability
- Decay probability with each retry (diminishing returns)
- Recommend RETRY

### For CIRCUIT BREAKER OPEN:
- System is unhealthy, do not retry
- Recommend ESCALATE
- Return estimated success probability = 0.10

## Output Requirements

You MUST respond with ONLY a JSON object (no markdown, no explanation):
{
    "next_delay_ms": <integer>,
    "estimated_success_probability": <float 0.0-1.0>,
    "recommended_action": "retry" | "skip" | "escalate",
    "rationale": "<brief explanation>",
    "tuning_strategy": "exponential" | "rate-limit-backoff" | "maintenance-wait" | "permanent-skip"
}

Use provided tools to check historical success rates and maintenance windows.
Optimize for reducing unnecessary retries on permanent failures (30% fewer retries target)."""

    try:
        async with (
            DefaultAzureCredential() as credential,
            AzureAIClient(
                project_endpoint=project_endpoint,
                model_deployment_name=model_deployment,
                credential=credential,
            ).create_agent(
                name="RetryTunerAgent",
                instructions=system_prompt,
                tools=[
                    query_error_pattern_success_rate,
                    check_maintenance_window,
                    estimate_retry_success,
                ],
            ) as agent,
        ):
            logger.info("Retry Tuner Agent created successfully")
            return agent
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise


async def tune_retry(
    context: RetryTuneContext, timeout_ms: int = 200
) -> RetryDecision:
    """
    Get optimal retry delay using the Retry Tuning Agent.
    
    Args:
        context: RetryTuneContext with error and retry info
        timeout_ms: Agent response timeout (default 200ms)
    
    Returns:
        RetryDecision with tuned delay and strategy
    """
    
    start_time = datetime.utcnow()
    
    try:
        # Load config from environment
        project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        model_deployment = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o")
        
        if not project_endpoint:
            logger.warning("FOUNDRY_PROJECT_ENDPOINT not set, using fallback classifier")
            return fallback_retry_tuner(context)
        
        # Create agent with timeout
        agent = await asyncio.wait_for(
            create_retry_tuner_agent(project_endpoint, model_deployment),
            timeout=timeout_ms / 1000,
        )
        
        # Create prompt for the agent
        prompt = f"""Tune retry delay for this error and respond with ONLY the JSON object (no markdown):

Error Code: {context.error_code}
Error Classification: {context.error_classification}
Retry Attempt: {context.retry_count}
Last Delay (ms): {context.last_delay_ms}
Total Elapsed (ms): {context.total_elapsed_ms}
Circuit Breaker State: {context.circuit_breaker_state}
Subscription Size: {context.subscription_size}

Use tools to check historical success rates and maintenance windows. Prioritize reducing retries on permanent failures.
Respond ONLY with valid JSON (no markdown formatting)."""

        # Run agent (streaming)
        response_text = ""
        async for chunk in agent.run_stream(prompt):
            if chunk.text:
                response_text += chunk.text

        # Parse agent response
        response_text = response_text.strip()
        if response_text.startswith("```"):
            response_text = response_text[response_text.find("{") : response_text.rfind("}") + 1]

        agent_output = json.loads(response_text)

        # Build decision from agent output
        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        decision = RetryDecision(
            next_delay_ms=agent_output.get("next_delay_ms", 1000),
            estimated_success_probability=agent_output.get("estimated_success_probability", 0.70),
            recommended_action=agent_output.get("recommended_action", "retry"),
            rationale=agent_output.get("rationale", ""),
            tuning_strategy=agent_output.get("tuning_strategy", "exponential"),
            tuning_confidence=0.90,  # Agent output confidence
            tuning_latency_ms=int(elapsed),
        )
        
        logger.info(
            f"Tuned retry: {context.error_code} (attempt {context.retry_count}) -> "
            f"delay={decision.next_delay_ms}ms, strategy={decision.tuning_strategy}"
        )
        
        return decision

    except asyncio.TimeoutError:
        logger.warning(f"Retry tuner agent timed out ({timeout_ms}ms), using fallback")
        return fallback_retry_tuner(context)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse agent response: {e}, using fallback")
        return fallback_retry_tuner(context)
    except Exception as e:
        logger.warning(f"Retry tuner agent error: {e}, using fallback")
        return fallback_retry_tuner(context)


# ============================================================================
# HTTP SERVER (Production Entry Point)
# ============================================================================


async def main():
    """
    HTTP server entry point for production deployment.
    Wraps the retry tuner agent as a FastAPI service.
    """
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI(
        title="ACA-17-002 Retry Tuner Agent",
        version="1.0.0",
        description="Intelligent retry tuning for adaptive backoff strategies",
    )

    class TuneRequest(BaseModel):
        error_code: str
        error_classification: str  # "transient" | "permanent"
        retry_count: int
        last_delay_ms: int = 0
        total_elapsed_ms: int = 0
        circuit_breaker_state: str = "CLOSED"
        subscription_size: str = "medium"

    class TuneResponse(BaseModel):
        next_delay_ms: int
        estimated_success_probability: float
        recommended_action: str
        rationale: str
        tuning_strategy: str
        tuning_confidence: float
        tuning_latency_ms: int

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "retry-tuner-agent"}

    @app.post("/v1/retry-tune", response_model=TuneResponse)
    async def tune_retry_endpoint(request: TuneRequest):
        """Tune a retry decision for the given error context."""
        context = RetryTuneContext(
            error_code=request.error_code,
            error_classification=request.error_classification,
            retry_count=request.retry_count,
            last_delay_ms=request.last_delay_ms,
            total_elapsed_ms=request.total_elapsed_ms,
            circuit_breaker_state=request.circuit_breaker_state,
            subscription_size=request.subscription_size,
        )

        decision = await tune_retry(context)
        return TuneResponse(
            next_delay_ms=decision.next_delay_ms,
            estimated_success_probability=decision.estimated_success_probability,
            recommended_action=decision.recommended_action,
            rationale=decision.rationale,
            tuning_strategy=decision.tuning_strategy,
            tuning_confidence=decision.tuning_confidence,
            tuning_latency_ms=decision.tuning_latency_ms,
        )

    import uvicorn

    port = int(os.getenv("RETRY_TUNER_PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    asyncio.run(main())
