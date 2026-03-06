"""
# EVA-STORY: ACA-17-004

ACA-17-004: Sync Orchestration Advisor Agent
AI-driven recommendations for failure recovery and parallelism tuning.

This agent analyzes sync orchestration failures and recommends:
1. Recovery action: retry_all, retry_failed_only, pause+increase resources
2. Optimal parallelism level: 1-5 based on subscription and circuit breaker state
3. Actionable guidance: e.g., "increase Cosmos RUs by 25%"

System Prompt: Trained on Cosmos best practices (18-azure-best) + ACA Tier 2 telemetry.
Output: Recommendation with confidence 0.65-1.0, wrapped in AdvisorRecommendation.
"""

import os
import json
import asyncio
import logging
from typing import Optional, Annotated
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus

# Logging setup (must be before imports that use logger)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# FastAPI imports
from fastapi import FastAPI, HTTPException
import uvicorn

# Agent Framework imports (lazy load to avoid dependency issues in tests)
# from agent_framework.azure import AzureAIClient
# from azure.identity.aio import DefaultAzureCredential

# For tests: use fallback advisor only
_AGENT_FRAMEWORK_AVAILABLE = False
try:
    from agent_framework.azure import AzureAIClient
    from azure.identity.aio import DefaultAzureCredential
    _AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    logger.warning("Agent Framework not available - using fallback advisor only")
    DefaultAzureCredential = None
    AzureAIClient = None

# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class AdvisorContext:
    """Input context for advisor recommendation."""
    subscription_size: str  # "small" | "medium" | "large" (affects parallelism)
    failed_story_count: int
    total_stories: int = 21
    cb_state: str = "closed"  # "open" | "half-open" | "closed"
    last_error_pattern: Optional[str] = None  # "rate-limit" | "quota-exceeded" | "auth-failure"
    elapsed_ms: int = 0
    retry_count: int = 0

    def to_dict(self) -> dict:
        return {
            "subscription_size": self.subscription_size,
            "failed_story_count": self.failed_story_count,
            "total_stories": self.total_stories,
            "cb_state": self.cb_state,
            "last_error_pattern": self.last_error_pattern,
            "elapsed_ms": self.elapsed_ms,
            "retry_count": self.retry_count,
        }


@dataclass
class AdvisorRecommendation:
    """Output advisor recommendation."""
    recommended_action: str  # "retry_all" | "retry_failed_only" | "pause+increase"
    parallelism_level: int  # 1-5, recommended based on subscription
    guidance: str  # actionable next steps
    confidence: float  # 0.65-1.0
    rationale: str
    best_practice_reference: Optional[str] = None  # e.g., "18-azure-best: Cosmos rate-limit handling"
    advisor_latency_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "recommended_action": self.recommended_action,
            "parallelism_level": self.parallelism_level,
            "guidance": self.guidance,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "best_practice_reference": self.best_practice_reference,
            "advisor_latency_ms": self.advisor_latency_ms,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ============================================================================
# FALLBACK ADVISOR (Rules-Based)
# ============================================================================


def fallback_sync_advisor(context: AdvisorContext) -> AdvisorRecommendation:
    """
    Rules-based fallback advisor when agent is unavailable.
    
    Decision tree:
    1. If all stories failed (21/21) -> likely transient issue, retry_all
    2. If partial failure (1-3) -> skip completed, retry failed only
    3. If CB.OPEN + >50% failed -> rate-limit detected, reduce parallelism + increase RUs
    4. If rate-limit pattern -> increase RUs, reduce parallelism
    5. Otherwise -> safe defaults
    """
    
    failed_pct = (context.failed_story_count / context.total_stories) * 100
    
    # Rule 1: All failed -> likely transient service issue
    if context.failed_story_count == context.total_stories:
        return AdvisorRecommendation(
            recommended_action="retry_all",
            parallelism_level=1,  # Start serial to avoid cascade
            guidance="All stories failed - likely transient service issue. Retry with parallelism 1 first. If succeeds, gradually increase to 3.",
            confidence=0.95,
            rationale="100% failure rate suggests transient (network, service unavailability) rather than permission/data issues.",
            best_practice_reference="18-azure-best: transient fault handling"
        )
    
    # Rule 2: Partial failure (1-3 stories) -> use checkpoint to skip completed
    if 1 <= context.failed_story_count <= 3:
        return AdvisorRecommendation(
            recommended_action="retry_failed_only",
            parallelism_level=3,  # Can safely parallelize partial
            guidance=f"Retry {context.failed_story_count} failed stories only, skip {context.total_stories - context.failed_story_count} completed stories. Use checkpoint to resume.",
            confidence=0.9,
            rationale="Partial failures suggest isolated issues (specific resource quota, permission). Completed stories don't need retry.",
            best_practice_reference="18-azure-best: idempotent sync patterns"
        )
    
    # Rule 3: CB.OPEN + significant failure -> rate-limit or quota issue
    if context.cb_state == "open" and failed_pct > 50:
        return AdvisorRecommendation(
            recommended_action="pause+increase",
            parallelism_level=1,
            guidance="Circuit breaker OPEN and >50% failure rate detected. Pause sync. Increase Cosmos RUs by 25-50%. Wait 60s before retry with parallelism=1.",
            confidence=0.92,
            rationale="Persistent failures + CB.OPEN indicate rate-limit or quota exceeded. Increasing provisioned throughput (RUs) is required.",
            best_practice_reference="18-azure-best: Cosmos rate-limit mitigation"
        )
    
    # Rule 4: Rate-limit pattern detected
    if context.last_error_pattern == "rate-limit":
        return AdvisorRecommendation(
            recommended_action="pause+increase",
            parallelism_level=1,
            guidance="Rate-limit (429) detected on Cosmos. Increase RUs incrementally (25% per retry). Reduce parallelism to 1 until throttling resolves.",
            confidence=0.88,
            rationale="Explicit rate-limit pattern requires provisioning adjustment. Serial execution prevents cascading 429 errors.",
            best_practice_reference="18-azure-best: Cosmos throughput throttling"
        )
    
    # Rule 5: CB.OPEN (any failure count) -> reduce parallelism
    if context.cb_state == "open":
        return AdvisorRecommendation(
            recommended_action="retry_failed_only",
            parallelism_level=1,
            guidance="Circuit breaker OPEN detected. Reduce parallelism to 1 (serial execution). Wait 30s between retries.",
            confidence=0.85,
            rationale="CB.OPEN signals persistent transient errors. Serial execution with backoff avoids cascade.",
            best_practice_reference="18-azure-best: circuit breaker pattern"
        )
    
    # Rule 6: Quota pattern
    if context.last_error_pattern == "quota-exceeded":
        return AdvisorRecommendation(
            recommended_action="pause+increase",
            parallelism_level=1,
            guidance="Subscription resource quota exceeded. Increase quotas (storage, compute) or split sync into smaller batches.",
            confidence=0.87,
            rationale="Quota limits are hard stops. Increasing limits is required before retry.",
            best_practice_reference="18-azure-best: Azure subscription quotas"
        )
    
    # Default: safe recommendation for small failures
    return AdvisorRecommendation(
        recommended_action="retry_failed_only",
        parallelism_level=2,  # Conservative default
        guidance=f"Retry {context.failed_story_count} failed stories with parallelism=2. Monitor for rate-limit (429) errors.",
        confidence=0.75,
        rationale="Moderate failure rate with no CB.OPEN indicates transient issues. Conservative parallelism reduces cascade risk.",
        best_practice_reference="18-azure-best: transient fault patterns"
    )


# ============================================================================
# AGENT CREATION & ADVISOR FUNCTION
# ============================================================================


async def create_sync_advisor_agent():
    """Create and configure the Sync Advisor Agent using Agent Framework.
    
    Returns None if Agent Framework is not available - fallback advisor will be used.
    """
    
    if not _AGENT_FRAMEWORK_AVAILABLE or DefaultAzureCredential is None:
        logger.info("[ADVISOR] Agent Framework not available - using fallback advisor")
        return None
    
    try:
        credential = DefaultAzureCredential()
        
        # For now, use fallback approach (no actual agent until Foundry is configured)
        # In production, this would:
        # client = AzureAIClient(
        #     credential=credential,
        #     project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        #     model_deployment=os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o")
        # )
        
        return None  # Return None signals use fallback
    
    except Exception as e:
        logger.warning(f"[ADVISOR] Agent Framework setup failed: {e} - using fallback")
        return None


async def get_advisor_recommendation(
    context: AdvisorContext,
    timeout_ms: int = 500
) -> AdvisorRecommendation:
    """
    Get advisor recommendation with timeout and fallback.
    
    Tries to call Agent Framework agent first (if available).
    Falls back to rules-based advisor if agent timeouts or fails.
    """
    
    import time
    start_time = time.time()
    
    try:
        # For now, always use fallback (agent integration can be added in phase 2)
        # TODO: Integrate with Foundry agent when endpoint is available
        
        recommendation = fallback_sync_advisor(context)
        elapsed_ms = int((time.time() - start_time) * 1000)
        recommendation.advisor_latency_ms = elapsed_ms
        
        logger.info(f"[ADVISOR] Recommendation: {recommendation.recommended_action} (latency: {elapsed_ms}ms)")
        return recommendation
        
    except asyncio.TimeoutError:
        logger.warning("[ADVISOR] Agent timeout, falling back to rules")
        recommendation = fallback_sync_advisor(context)
        recommendation.advisor_latency_ms = timeout_ms
        return recommendation
    except Exception as e:
        logger.error(f"[ADVISOR] Error: {e}, falling back to rules")
        recommendation = fallback_sync_advisor(context)
        recommendation.advisor_latency_ms = int((time.time() - start_time) * 1000)
        return recommendation


# ============================================================================
# FASTAPI HTTP SERVER
# ============================================================================


app = FastAPI(
    title="ACA-17-004: Sync Advisor Agent",
    version="1.0.0",
    description="AI-driven recommendations for sync orchestration recovery"
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "sync-advisor-agent",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/v1/sync-advisor")
async def sync_advisor_endpoint(request_body: dict) -> dict:
    """
    Main advisor endpoint.
    
    Input JSON:
    {
        "subscription_size": "medium",
        "failed_story_count": 21,
        "total_stories": 21,
        "cb_state": "open",
        "last_error_pattern": "rate-limit"
    }
    
    Output JSON:
    {
        "recommended_action": "pause+increase",
        "parallelism_level": 1,
        "guidance": "...",
        "confidence": 0.92,
        "rationale": "...",
        "advisor_latency_ms": 45
    }
    """
    
    try:
        # Parse input
        context = AdvisorContext(
            subscription_size=request_body.get("subscription_size", "medium"),
            failed_story_count=request_body.get("failed_story_count", 0),
            total_stories=request_body.get("total_stories", 21),
            cb_state=request_body.get("cb_state", "closed"),
            last_error_pattern=request_body.get("last_error_pattern"),
            elapsed_ms=request_body.get("elapsed_ms", 0),
            retry_count=request_body.get("retry_count", 0),
        )
        
        # Get recommendation
        recommendation = await get_advisor_recommendation(context)
        
        return recommendation.to_dict()
        
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))


# ============================================================================
# ENTRYPOINT
# ============================================================================


if __name__ == "__main__":
    # Run HTTP server
    # Usage: python advisor_agent.py
    # Server: http://localhost:8004
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")

