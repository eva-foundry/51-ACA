"""
ACA-17-001: Failure Classifier Agent
Real-time classification of sync orchestration errors (transient vs permanent).

This agent uses Microsoft Agent Framework with Azure AI Foundry to classify errors
from the sync orchestration process into actionable categories.

System Prompt: Trained on 20+ error patterns from Azure best practices (18-azure-best).
Output: Classification with confidence, rationale, and recommended action.
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
class ErrorContext:
    """Input context for classification."""
    error_message: str
    error_code: Optional[str] = None
    retry_count: int = 0
    elapsed_ms: int = 0
    last_error_time: Optional[str] = None
    context: Optional[dict] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "error_message": self.error_message,
            "error_code": self.error_code,
            "retry_count": self.retry_count,
            "elapsed_ms": self.elapsed_ms,
            "last_error_time": self.last_error_time,
            "context": self.context,
        }


@dataclass
class Classification:
    """Output classification result."""
    error_id: str
    error_message: str
    classification: str  # "transient" | "permanent"
    confidence: float  # 0.0-1.0
    recommended_action: str  # "retry" | "skip" | "escalate"
    rationale: str
    classification_latency_ms: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "error_id": self.error_id,
            "error_message": self.error_message,
            "classification": self.classification,
            "confidence": self.confidence,
            "recommended_action": self.recommended_action,
            "rationale": self.rationale,
            "classification_latency_ms": self.classification_latency_ms,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ============================================================================
# FALLBACK CLASSIFIER (Rules-Based)
# ============================================================================


def fallback_classifier(context: ErrorContext) -> Classification:
    """
    Rules-based fallback classifier for when the agent is unavailable.
    Used if agent times out, fails, or is unreachable.
    
    Based on error patterns from 18-azure-best + Sprint-001 telemetry.
    """
    error_msg = context.error_message.lower() if context.error_message else ""
    error_code = context.error_code or ""

    # Transient patterns (retry-able)
    transient_patterns = [
        ("timeout", 0.95),
        ("timed out", 0.95),
        ("429", 0.98),  # Rate limit
        ("rate limit", 0.98),
        ("temporarily unavailable", 0.90),
        ("try again", 0.85),
        ("dns", 0.85),  # DNS errors often transient
        ("connection reset", 0.80),
        ("connection refused", 0.75),  # Could be service restart
        ("503", 0.90),  # Service unavailable (transient)
        ("502", 0.80),  # Bad gateway (usually transient)
        ("504", 0.90),  # Gateway timeout
    ]

    # Permanent patterns (skip / escalate)
    permanent_patterns = [
        ("403", 0.99),  # Forbidden (auth issue)
        ("unauthorized", 0.98),
        ("not authorized", 0.98),
        ("access denied", 0.98),
        ("invalid credentials", 0.98),
        ("401", 0.99),  # Unauthorized
        ("404", 0.95),  # Not found
        ("partition key", 0.98),  # Cosmos partition mismatch
        ("invalid partition", 0.98),
        ("400", 0.90),  # Bad request
    ]

    # Check transient patterns
    for pattern, confidence in transient_patterns:
        if pattern in error_msg or pattern in error_code:
            return Classification(
                error_id=f"transient-{error_code or 'unknown'}",
                error_message=context.error_message,
                classification="transient",
                confidence=confidence,
                recommended_action="retry",
                rationale=f"Pattern '{pattern}' detected in error message.",
                classification_latency_ms=5,  # Fast fallback
            )

    # Check permanent patterns
    for pattern, confidence in permanent_patterns:
        if pattern in error_msg or pattern in error_code:
            return Classification(
                error_id=f"permanent-{error_code or 'unknown'}",
                error_message=context.error_message,
                classification="permanent",
                confidence=confidence,
                recommended_action="escalate",
                rationale=f"Pattern '{pattern}' detected in error message.",
                classification_latency_ms=5,  # Fast fallback
            )

    # Default: assume transient (safe to retry once)
    return Classification(
        error_id=f"unknown-{error_code or 'unknown'}",
        error_message=context.error_message,
        classification="transient",
        confidence=0.50,  # Low confidence
        recommended_action="retry",
        rationale="Unknown error pattern. Assuming transient (safe retry).",
        classification_latency_ms=5,  # Fast fallback
    )


# ============================================================================
# TOOLS FOR AGENT
# ============================================================================


def query_error_pattern_history(
    error_code: Annotated[str, "Error code to look up (e.g., '429', '403')."]
) -> str:
    """
    Query the error_pattern history from Cosmos DB.
    Returns success probability for this error type based on historical data.
    
    In production, this would query:
      SELECT successful_recovery_count, total_attempts FROM error_pattern WHERE error_code = @code
    
    For now, returns a simulated response.
    """
    # Simulated historical data (would come from Cosmos DB)
    history = {
        "429": {"successful_recovery_count": 95, "total_attempts": 100, "success_rate": 0.95},
        "503": {"successful_recovery_count": 88, "total_attempts": 100, "success_rate": 0.88},
        "timeout": {"successful_recovery_count": 92, "total_attempts": 100, "success_rate": 0.92},
        "403": {"successful_recovery_count": 5, "total_attempts": 100, "success_rate": 0.05},
        "404": {"successful_recovery_count": 15, "total_attempts": 100, "success_rate": 0.15},
    }
    
    data = history.get(error_code, {"successful_recovery_count": 0, "total_attempts": 0, "success_rate": 0})
    return json.dumps(data)


def check_circuit_breaker_state(
    breaker_name: Annotated[str, "Circuit breaker name (e.g., 'health-check', 'cosmos-sync')."]
) -> str:
    """
    Check the current state of a circuit breaker.
    Returns state (CLOSED, OPEN, HALF_OPEN) and metadata.
    
    In production, this would query the circuit breaker state from the orchestrator.
    """
    # Simulated CB state (would come from orchestrator state file)
    cb_states = {
        "health-check": {"state": "CLOSED", "failure_count": 0, "last_open_time": None},
        "cosmos-sync": {"state": "CLOSED", "failure_count": 1, "last_open_time": None},
    }
    
    state = cb_states.get(breaker_name, {"state": "UNKNOWN"})
    return json.dumps(state)


def get_azure_best_practice(
    topic: Annotated[str, "Topic to search (e.g., 'transient errors', 'rate limiting', 'Cosmos throttling')."]
) -> str:
    """
    Retrieve relevant Azure best practice guidance from 18-azure-best library.
    
    In production, this would load from MCP Cosmos server.
    """
    guidance = {
        "transient errors": "Transient errors (timeouts, DNS, 503) should be retried with exponential backoff.",
        "rate limiting": "Rate-limit errors (429) indicate Cosmos RU exhaustion. Increase RUs or reduce request rate.",
        "Cosmos throttling": "Cosmos throttling (429) can be resolved by: 1) Increase RU, 2) Use partition key correctly, 3) Retry with backoff.",
        "authorization": "Authorization errors (401, 403) are permanent. Do not retry. Check credentials and RBAC assignments.",
    }
    
    return guidance.get(topic, "No guidance found for this topic.")


# ============================================================================
# FAILURE CLASSIFIER AGENT
# ============================================================================


async def create_classifier_agent():
    """
    Create and configure the Failure Classifier Agent.
    Uses Microsoft Agent Framework with Azure AI Foundry (Foundry gpt-4o model).
    """
    
    # Load configuration from environment
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "https://marco-sandbox-foundry.services.ai.azure.com/api/projects/marco-sandbox-fdry-project")
    model_deployment = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    
    logger.info(f"Initializing Failure Classifier Agent")
    logger.info(f"  Project Endpoint: {project_endpoint}")
    logger.info(f"  Model Deployment: {model_deployment}")
    
    # System prompt trained on 20+ error patterns
    system_prompt = """You are a Failure Classifier AI agent. Your role is to quickly classify error messages 
from Azure sync orchestration into two categories: TRANSIENT (retry-able) or PERMANENT (escalate).

TRANSIENT errors (retry-able):
- Timeouts, DNS failures, connection resets
- 429 (Rate Limit), 503 (Service Unavailable), 504 (Gateway Timeout)
- Temporary network issues
- Scheduled maintenance windows

PERMANENT errors (do not retry, escalate):
- 403 (Forbidden), 401 (Unauthorized) - authentication/authorization issues
- 404 (Not Found) - resource doesn't exist
- Partition key mismatches - data model issues
- Security policy violations

Your output must be JSON with these fields:
{
    "classification": "transient" | "permanent",
    "confidence": 0.0-1.0,
    "recommended_action": "retry" | "skip" | "escalate",
    "rationale": "brief explanation"
}

Be precise, confident, and quick (<100ms). Use the provided tools to check historical patterns 
and best practices when needed, but prioritize speed."""

    try:
        # Create agent with tools
        async with (
            DefaultAzureCredential() as credential,
            AzureAIClient(
                project_endpoint=project_endpoint,
                model_deployment_name=model_deployment,
                credential=credential,
            ).create_agent(
                name="FailureClassifierAgent",
                instructions=system_prompt,
                tools=[
                    query_error_pattern_history,
                    check_circuit_breaker_state,
                    get_azure_best_practice,
                ],
            ) as agent,
        ):
            logger.info("Failure Classifier Agent created successfully")
            return agent
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise


async def classify_error(context: ErrorContext, timeout_ms: int = 100) -> Classification:
    """
    Classify an error using the Failure Classifier Agent.
    
    Args:
        context: ErrorContext with error details
        timeout_ms: Agent response timeout (default 100ms)
    
    Returns:
        Classification result (via agent or fallback)
    """
    
    start_time = datetime.utcnow()
    
    try:
        # Try to use the agent (with timeout)
        agent = await asyncio.wait_for(create_classifier_agent(), timeout=timeout_ms / 1000)
        
        # Create prompt for the agent
        prompt = f"""Classify this error and respond with ONLY the JSON object (no markdown, no explanation):

Error Message: {context.error_message}
Error Code: {context.error_code}
Retry Count: {context.retry_count}
Elapsed Time (ms): {context.elapsed_ms}

Use tools if necessary to check historical patterns or best practices.
Respond ONLY with valid JSON (no markdown formatting)."""

        # Run agent (streaming for best practice)
        response_text = ""
        async for chunk in agent.run_stream(prompt):
            if chunk.text:
                response_text += chunk.text

        # Parse agent response
        # Strip markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```"):
            response_text = response_text[response_text.find("{") : response_text.rfind("}") + 1]

        agent_output = json.loads(response_text)

        # Build classification from agent output
        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        classification = Classification(
            error_id=f"classified-{context.error_code or 'unknown'}",
            error_message=context.error_message,
            classification=agent_output.get("classification", "transient"),
            confidence=float(agent_output.get("confidence", 0.5)),
            recommended_action=agent_output.get("recommended_action", "retry"),
            rationale=agent_output.get("rationale", "Agent classification"),
            classification_latency_ms=int(elapsed),
        )
        
        logger.info(f"Agent classified error: {classification.classification} "
                   f"(confidence: {classification.confidence:.2f}, latency: {elapsed:.0f}ms)")
        return classification

    except asyncio.TimeoutError:
        logger.warning(f"Agent timeout (>{timeout_ms}ms). Using fallback classifier.")
        result = fallback_classifier(context)
        result.classification_latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return result

    except (json.JSONDecodeError, KeyError, Exception) as e:
        logger.warning(f"Agent error: {e}. Using fallback classifier.")
        result = fallback_classifier(context)
        result.classification_latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return result


async def main():
    """Test the classifier with sample errors."""
    
    test_cases = [
        ErrorContext(
            error_message="The operation timed out after 30 seconds",
            error_code="TIMEOUT",
            retry_count=1,
        ),
        ErrorContext(
            error_message="Http request returned status code 403 (Forbidden)",
            error_code="403",
            retry_count=0,
        ),
        ErrorContext(
            error_message="Http request returned status code 429 (Too Many Requests)",
            error_code="429",
            retry_count=2,
        ),
        ErrorContext(
            error_message="Partition key mismatch in Cosmos DB operation",
            error_code="PARTITION_ERROR",
            retry_count=0,
        ),
    ]
    
    logger.info("=" * 70)
    logger.info("FAILURE CLASSIFIER AGENT - TEST RUN")
    logger.info("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n[Test {i}] Error: {test_case.error_message}")
        logger.info(f"Error Code: {test_case.error_code}")
        
        classification = await classify_error(test_case)
        
        logger.info(f"Result: {classification.classification.upper()}")
        logger.info(f"Confidence: {classification.confidence:.2f}")
        logger.info(f"Action: {classification.recommended_action}")
        logger.info(f"Latency: {classification.classification_latency_ms}ms")
        logger.info(f"Rationale: {classification.rationale}")


if __name__ == "__main__":
    asyncio.run(main())
