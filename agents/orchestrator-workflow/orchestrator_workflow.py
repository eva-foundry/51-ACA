"""
Multi-Agent Orchestration Workflow (Support infrastructure for multi-agent failure recovery pipeline)
Coordinates Failure Classifier + Retry Tuner + Advisor agents via 29-Foundry.

This module implements the orchestration logic for the following pipeline:
1. Failure Classifier (50ms) - classify error (transient vs permanent)
2. Retry Tuner (100ms) - determine optimal retry delay
3. [Conditional] Advisor Agent (200ms, if delay > 30s) - recommend recovery action

The orchestrator uses 29-Foundry Workflow for agent coordination, with fallback
rules-based decision logic if any agent times out.

Total latency target: ~350ms (< 400ms timeout)
Reliability target: 9.5/10 (99.5% success rate)
"""

import os
import json
import asyncio
import httpx
import logging
from typing import Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from enum import Enum

# FastAPI imports
from fastapi import FastAPI, HTTPException
import uvicorn

# Logging setup
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Agent endpoints (from individual agent deployments)
CLASSIFIER_ENDPOINT = os.getenv("CLASSIFIER_AGENT_ENDPOINT", "http://localhost:8001")
TUNER_ENDPOINT = os.getenv("TUNER_AGENT_ENDPOINT", "http://localhost:8002")
ADVISOR_ENDPOINT = os.getenv("ADVISOR_AGENT_ENDPOINT", "http://localhost:8004")

# Timeouts (milliseconds)
CLASSIFIER_TIMEOUT_MS = 50
TUNER_TIMEOUT_MS = 100
ADVISOR_TIMEOUT_MS = 200
ADVISOR_DELAY_THRESHOLD_MS = 30000  # 30s - if tuner delay exceeds this, run advisor

# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class OrchestrationInput:
    """Input to the orchestration workflow."""
    error_message: str
    error_code: Optional[str] = None
    retry_count: int = 0
    elapsed_ms: int = 0
    context: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "error_message": self.error_message,
            "error_code": self.error_code,
            "retry_count": self.retry_count,
            "elapsed_ms": self.elapsed_ms,
            "context": self.context,
        }


@dataclass
class ClassifierOutput:
    """Output from Failure Classifier agent."""
    classification: str  # "transient" | "permanent"
    confidence: float
    recommended_action: str
    rationale: str


@dataclass
class TunerOutput:
    """Output from Retry Tuner agent."""
    next_delay_ms: int
    estimated_success_probability: float
    recommended_action: str  # "retry" | "skip" | "wait"
    strategy: str


@dataclass
class AdvisorOutput:
    """Output from Advisor agent."""
    recommended_action: str
    parallelism_level: int
    guidance: str
    confidence: float


@dataclass
class OrchestrationResult:
    """Final orchestration decision combining all agents."""
    final_action: Literal["retry", "skip", "escalate"]
    delay_ms: int
    guidance: str
    workflow_duration_ms: int
    agents_executed: list = field(default_factory=list)  # ["classifier", "tuner", "advisor"]
    confidence: float = 0.75
    classifier_output: Optional[ClassifierOutput] = None
    tuner_output: Optional[TunerOutput] = None
    advisor_output: Optional[AdvisorOutput] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "final_action": self.final_action,
            "delay_ms": self.delay_ms,
            "guidance": self.guidance,
            "workflow_duration_ms": self.workflow_duration_ms,
            "agents_executed": self.agents_executed,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ============================================================================
# AGENT CALLERS (with timeout + fallback)
# ============================================================================


async def call_classifier(
    context: OrchestrationInput,
    timeout_ms: int = CLASSIFIER_TIMEOUT_MS
) -> tuple[Optional[ClassifierOutput], bool]:
    """
    Call Failure Classifier agent.
    Returns: (ClassifierOutput, success: bool)
    """
    
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await asyncio.wait_for(
                client.post(
                    f"{CLASSIFIER_ENDPOINT}/v1/classify",
                    json=context.to_dict(),
                    timeout=timeout_ms / 1000
                ),
                timeout=timeout_ms / 1000
            )
            
            if response.status_code == 200:
                data = response.json()
                output = ClassifierOutput(
                    classification=data.get("classification"),
                    confidence=data.get("confidence"),
                    recommended_action=data.get("recommended_action"),
                    rationale=data.get("rationale")
                )
                elapsed_ms = int((time.time() - start_time) * 1000)
                logger.info(f"[CLASSIFIER] Success: {output.classification} (latency: {elapsed_ms}ms)")
                return output, True
            else:
                logger.warning(f"[CLASSIFIER] HTTP {response.status_code}")
                return None, False
    
    except asyncio.TimeoutError:
        logger.warning(f"[CLASSIFIER] Timeout exceeded {timeout_ms}ms")
        return None, False
    except Exception as e:
        logger.error(f"[CLASSIFIER] Error: {e}")
        return None, False


async def call_tuner(
    context: OrchestrationInput,
    classifier_output: ClassifierOutput,
    timeout_ms: int = TUNER_TIMEOUT_MS
) -> tuple[Optional[TunerOutput], bool]:
    """
    Call Retry Tuner agent.
    Returns: (TunerOutput, success: bool)
    """
    
    import time
    start_time = time.time()
    
    try:
        request_body = {
            **context.to_dict(),
            "error_classification": classifier_output.classification,
            "confidence": classifier_output.confidence
        }
        
        async with httpx.AsyncClient() as client:
            response = await asyncio.wait_for(
                client.post(
                    f"{TUNER_ENDPOINT}/v1/tune-retry",
                    json=request_body,
                    timeout=timeout_ms / 1000
                ),
                timeout=timeout_ms / 1000
            )
            
            if response.status_code == 200:
                data = response.json()
                output = TunerOutput(
                    next_delay_ms=data.get("next_delay_ms"),
                    estimated_success_probability=data.get("estimated_success_probability"),
                    recommended_action=data.get("recommended_action"),
                    strategy=data.get("strategy")
                )
                elapsed_ms = int((time.time() - start_time) * 1000)
                logger.info(f"[TUNER] Success: delay={output.next_delay_ms}ms (latency: {elapsed_ms}ms)")
                return output, True
            else:
                logger.warning(f"[TUNER] HTTP {response.status_code}")
                return None, False
    
    except asyncio.TimeoutError:
        logger.warning(f"[TUNER] Timeout exceeded {timeout_ms}ms")
        return None, False
    except Exception as e:
        logger.error(f"[TUNER] Error: {e}")
        return None, False


async def call_advisor(
    context: OrchestrationInput,
    classifier_output: ClassifierOutput,
    tuner_output: TunerOutput,
    timeout_ms: int = ADVISOR_TIMEOUT_MS
) -> tuple[Optional[AdvisorOutput], bool]:
    """
    Call Advisor agent (optional, only if delay > 30s).
    Returns: (AdvisorOutput, success: bool)
    """
    
    import time
    start_time = time.time()
    
    try:
        request_body = {
            "subscription_size": "medium",  # TODO: get from context
            "failed_story_count": context.context.get("failed_story_count", 0) if context.context else 0,
            "cb_state": context.context.get("cb_state", "closed") if context.context else "closed",
            "last_error_pattern": classifier_output.classification
        }
        
        async with httpx.AsyncClient() as client:
            response = await asyncio.wait_for(
                client.post(
                    f"{ADVISOR_ENDPOINT}/v1/sync-advisor",
                    json=request_body,
                    timeout=timeout_ms / 1000
                ),
                timeout=timeout_ms / 1000
            )
            
            if response.status_code == 200:
                data = response.json()
                output = AdvisorOutput(
                    recommended_action=data.get("recommended_action"),
                    parallelism_level=data.get("parallelism_level"),
                    guidance=data.get("guidance"),
                    confidence=data.get("confidence")
                )
                elapsed_ms = int((time.time() - start_time) * 1000)
                logger.info(f"[ADVISOR] Success: {output.recommended_action} (latency: {elapsed_ms}ms)")
                return output, True
            else:
                logger.warning(f"[ADVISOR] HTTP {response.status_code}")
                return None, False
    
    except asyncio.TimeoutError:
        logger.warning(f"[ADVISOR] Timeout exceeded {timeout_ms}ms")
        return None, False
    except Exception as e:
        logger.error(f"[ADVISOR] Error: {e}")
        return None, False


# ============================================================================
# ORCHESTRATION WORKFLOW
# ============================================================================


async def orchestrate_failure_recovery(
    context: OrchestrationInput,
    total_timeout_ms: int = 400
) -> OrchestrationResult:
    """
    Main orchestration workflow: Classifier → Tuner → [Optional] Advisor
    
    Returns final orchestration result with all agent outputs.
    """
    
    import time
    workflow_start = time.time()
    agents_executed = []
    classifier_output = None
    tuner_output = None
    advisor_output = None
    
    try:
        # STAGE 1: Classifier Agent (50ms)
        classifier_output, classifier_ok = await call_classifier(context, CLASSIFIER_TIMEOUT_MS)
        agents_executed.append("classifier")
        
        if not classifier_ok or not classifier_output:
            logger.warning("[ORCHESTRATION] Classifier failed, falling back to static rules")
            return fallback_orchestration_result(context)
        
        # STAGE 2: Retry Tuner Agent (100ms)
        tuner_output, tuner_ok = await call_tuner(context, classifier_output, TUNER_TIMEOUT_MS)
        agents_executed.append("tuner")
        
        if not tuner_ok or not tuner_output:
            logger.warning("[ORCHESTRATION] Tuner failed, using default strategy")
            # Use classifier result but fallback tuner
            return OrchestrationResult(
                final_action="retry",
                delay_ms=2000,  # default 2s delay
                guidance="Tuner unavailable, using default 2s retry delay",
                workflow_duration_ms=int((time.time() - workflow_start) * 1000),
                agents_executed=agents_executed,
                confidence=classifier_output.confidence * 0.8,
                classifier_output=classifier_output
            )
        
        # STAGE 3: [Conditional] Advisor Agent (if delay > 30s, 200ms)
        if tuner_output.next_delay_ms > ADVISOR_DELAY_THRESHOLD_MS:
            logger.info(f"[ORCHESTRATION] Delay {tuner_output.next_delay_ms}ms > {ADVISOR_DELAY_THRESHOLD_MS}ms, invoking Advisor")
            advisor_output, advisor_ok = await call_advisor(
                context, classifier_output, tuner_output, ADVISOR_TIMEOUT_MS
            )
            agents_executed.append("advisor")
            
            if not advisor_ok or not advisor_output:
                logger.warning("[ORCHESTRATION] Advisor failed, using Tuner recommendation")
                # Use tuner output since advisor failed
                advisor_output = None
        
        # FINAL: Synthesize orchestration result
        workflow_duration_ms = int((time.time() - workflow_start) * 1000)
        
        # Determine final action based on agent outputs
        final_action = "retry"  # default
        guidance = f"Retry after {tuner_output.next_delay_ms}ms"
        confidence = (classifier_output.confidence + tuner_output.estimated_success_probability) / 2
        
        if advisor_output:
            # Advisor provides ultimate recommendation
            if advisor_output.recommended_action == "pause+increase":
                final_action = "escalate"
                guidance = advisor_output.guidance
                confidence = min(advisor_output.confidence, confidence)
            elif advisor_output.recommended_action == "retry_all":
                final_action = "retry"
                guidance = advisor_output.guidance
        
        if classifier_output.classification == "permanent":
            final_action = "skip"
            guidance = f"Permanent error detected: {classifier_output.rationale}"
            confidence = classifier_output.confidence
        
        result = OrchestrationResult(
            final_action=final_action,
            delay_ms=tuner_output.next_delay_ms,
            guidance=guidance,
            workflow_duration_ms=workflow_duration_ms,
            agents_executed=agents_executed,
            confidence=confidence,
            classifier_output=classifier_output,
            tuner_output=tuner_output,
            advisor_output=advisor_output
        )
        
        logger.info(f"[ORCHESTRATION] Complete: {final_action} in {workflow_duration_ms}ms, confidence={confidence:.2f}")
        return result
    
    except Exception as e:
        logger.error(f"[ORCHESTRATION] Unexpected error: {e}, falling back")
        return fallback_orchestration_result(context)


def fallback_orchestration_result(context: OrchestrationInput) -> OrchestrationResult:
    """Fallback orchestration when all agents unavailable."""
    
    # Simple rules: if error_code is known permanent → skip, else retry with exponential backoff
    is_permanent = context.error_code in ["403", "401", "404"]  # Permission / not found errors
    
    if is_permanent:
        return OrchestrationResult(
            final_action="skip",
            delay_ms=0,
            guidance=f"Error {context.error_code} is permanent, skipping story",
            workflow_duration_ms=0,
            agents_executed=[],
            confidence=0.8
        )
    else:
        # Exponential backoff: 1s, 2s, 4s, 8s, ...
        delay_ms = 1000 * (2 ** min(context.retry_count, 3))
        return OrchestrationResult(
            final_action="retry",
            delay_ms=delay_ms,
            guidance=f"All agents unavailable, using exponential backoff: {delay_ms}ms",
            workflow_duration_ms=0,
            agents_executed=[],
            confidence=0.65
        )


# ============================================================================
# FASTAPI HTTP SERVER
# ============================================================================


app = FastAPI(
    title="ACA-17-005: Multi-Agent Orchestration Workflow",
    version="1.0.0",
    description="Coordinates Classifier, Tuner, and Advisor agents for failure recovery"
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "orchestration-workflow",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/v1/orchestrate")
async def orchestrate_endpoint(request_body: dict) -> dict:
    """
    Main orchestration endpoint.
    
    Input JSON:
    {
        "error_message": "Cosmos 429 - rate limit exceeded",
        "error_code": "429",
        "retry_count": 2,
        "elapsed_ms": 5000,
        "context": {"failed_story_count": 5, "cb_state": "open"}
    }
    
    Output JSON:
    {
        "final_action": "escalate",
        "delay_ms": 5000,
        "guidance": "...",
        "workflow_duration_ms": 342,
        "agents_executed": ["classifier", "tuner", "advisor"],
        "confidence": 0.89,
        "timestamp": "2026-03-02T23:00:00Z"
    }
    """
    
    try:
        # Parse input
        context = OrchestrationInput(
            error_message=request_body.get("error_message", ""),
            error_code=request_body.get("error_code"),
            retry_count=request_body.get("retry_count", 0),
            elapsed_ms=request_body.get("elapsed_ms", 0),
            context=request_body.get("context")
        )
        
        # Run orchestration
        result = await orchestrate_failure_recovery(context)
        
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))


# ============================================================================
# ENTRYPOINT
# ============================================================================


if __name__ == "__main__":
    # Run HTTP server
    # Usage: python orchestrator_workflow.py
    # Server: http://localhost:8005
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")

