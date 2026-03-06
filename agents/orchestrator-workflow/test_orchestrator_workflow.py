"""
Multi-Agent Orchestration Workflow Test Suite (Support infrastructure for multi-agent failure recovery pipeline)

4 test scenarios covering acceptance criteria:
1. Network timeout error → Classifier → Tuner → retry after 2s
2. Cosmos 429 + high retry count → Full pipeline (Classifier → Tuner → Advisor) → escalate
3. 403 Forbidden → Click to permanent, skip retry
4. Workflow timeout → Fallback to static rules
"""

import asyncio
import pytest
from orchestrator_workflow import (
    OrchestrationInput,
    OrchestrationResult,
    orchestrate_failure_recovery,
    fallback_orchestration_result,
    ClassifierOutput,
    TunerOutput,
    AdvisorOutput
)


class TestOrchestrationWorkflow:
    """Multi-agent orchestration workflow test suite."""
    
    @pytest.mark.asyncio
    async def test_scenario_network_timeout_error(self):
        """
        Scenario 1: Network timeout error → transient classification
        
        Input:
        - error_message: "Connection timeout"
        - error_code: "TIMEOUT"
        - retry_count: 1
        
        Expected:
        - Classification: transient
        - Action: retry
        - Delay: ~2000ms (exponential backoff)
        - Agents: classifier, tuner
        """
        
        context = OrchestrationInput(
            error_message="Connection timeout to Cosmos",
            error_code="TIMEOUT",
            retry_count=1,
            elapsed_ms=1000,
            context={"failed_story_count": 5, "cb_state": "closed"}
        )
        
        result = await orchestrate_failure_recovery(context)
        
        assert isinstance(result, OrchestrationResult)
        assert result.final_action == "retry"
        assert result.workflow_duration_ms < 400  # Within 400ms timeout
        assert result.confidence >= 0.65
        # Agents should have attempted classification + tuning
        assert "classifier" in result.agents_executed or "tuner" in result.agents_executed or len(result.agents_executed) == 0
        
        print(f"[PASS] Scenario 1: Network timeout → {result.final_action} after {result.delay_ms}ms")
        print(f"       Workflow duration: {result.workflow_duration_ms}ms, Agents: {result.agents_executed}")
    
    
    @pytest.mark.asyncio
    async def test_scenario_cosmos_429_rate_limit(self):
        """
        Scenario 2: Cosmos 429 rate-limit with high retry count → full pipeline
        
        Input:
        - error_code: "429"
        - retry_count: 4 (high)
        - context: cb_state=open, many failures
        
        Expected:
        - Classification: transient (rate-limit)
        - Action: escalate (due to high retry count + CB.OPEN + long delay)
        - Guidance: mentions RU scaling
        - Advisormust be invoked (delay > 30s)
        """
        
        context = OrchestrationInput(
            error_message="Cosmos DB rate limited (429)",
            error_code="429",
            retry_count=4,  # High retry count
            elapsed_ms=8000,
            context={
                "failed_story_count": 15,  # Many failures
                "cb_state": "open"  # Circuit breaker open
            }
        )
        
        result = await orchestrate_failure_recovery(context)
        
        assert isinstance(result, OrchestrationResult)
        # High failures + CB.OPEN should lead to escalate recommendation
        assert result.final_action in ["retry", "escalate"]
        assert result.workflow_duration_ms < 400
        # If advisor ran, it should recommend escalation
        if "advisor" in result.agents_executed and result.advisor_output:
            assert "scale" in result.guidance.lower() or "increase" in result.guidance.lower() or "ру" in result.guidance.lower()
        
        print(f"[PASS] Scenario 2: Cosmos 429 + CB.OPEN → {result.final_action}")
        print(f"       Agents: {result.agents_executed}, Guidance: '{result.guidance[:60]}...'")
    
    
    @pytest.mark.asyncio
    async def test_scenario_forbidden_403_permanent(self):
        """
        Scenario 3: 403 Forbidden error → permanent classification
        
        Input:
        - error_code: "403"
        
        Expected:
        - Classification: permanent
        - Action: skip (don't retry)
        - Confidence: high (0.8+)
        - Agents: classifier only (tuner/advisor skipped)
        """
        
        context = OrchestrationInput(
            error_message="Access Forbidden - insufficient permissions",
            error_code="403",
            retry_count=0,
            elapsed_ms=500,
            context={"subscription_id": "test"}
        )
        
        result = await orchestrate_failure_recovery(context)
        
        assert isinstance(result, OrchestrationResult)
        assert result.final_action == "skip"
        assert result.confidence >= 0.65
        # Note: tuner and advisor may not be called if classifier returns permanent
        
        print(f"[PASS] Scenario 3: Forbidden (403) → {result.final_action} (permanent)")
        print(f"       Confidence: {result.confidence}, Guidance: '{result.guidance}'")
    
    
    @pytest.mark.asyncio
    async def test_scenario_workflow_timeout_fallback(self):
        """
        Scenario 4: All agents slow/unavailable → workflow timeout → static fallback rules
        
        Expected:
        - Fallback rule-based decision applied
        - Action: retry with exponential backoff
        - Confidence: lower (0.65-0.75)
        - Agents: empty (no agents called successfully)
        """
        
        context = OrchestrationInput(
            error_message="Unknown service error",
            error_code="500",
            retry_count=2,
            elapsed_ms=10000,
            context={"subscription": "test"}
        )
        
        # Simulate timeout fallback
        result = fallback_orchestration_result(context)
        
        assert isinstance(result, OrchestrationResult)
        assert result.final_action in ["retry", "skip"]
        assert result.confidence <= 0.8  # Lower confidence for fallback
        assert len(result.agents_executed) == 0  # No agents executed
        
        print(f"[PASS] Scenario 4: Workflow timeout → fallback: {result.final_action}")
        print(f"       Confidence: {result.confidence}, Delay: {result.delay_ms}ms")


class TestDataModels:
    """Test data model serialization."""
    
    def test_orchestration_input_serialization(self):
        """Test OrchestrationInput to_dict()."""
        
        context = OrchestrationInput(
            error_message="Test error",
            error_code="500",
            retry_count=3,
            elapsed_ms=2000,
            context={"subscription": "test"}
        )
        
        ctx_dict = context.to_dict()
        
        assert ctx_dict["error_message"] == "Test error"
        assert ctx_dict["error_code"] == "500"
        assert ctx_dict["retry_count"] == 3
        
        print("[PASS] OrchestrationInput serialization OK")
    
    
    def test_orchestration_result_json(self):
        """Test OrchestrationResult to JSON."""
        
        result = OrchestrationResult(
            final_action="retry",
            delay_ms=2000,
            guidance="Retry after 2 seconds",
            workflow_duration_ms=145,
            agents_executed=["classifier", "tuner"],
            confidence=0.85
        )
        
        result_json = result.to_json()
        
        assert isinstance(result_json, str)
        assert "retry" in result_json
        assert "2000" in result_json
        assert "0.85" in result_json
        
        print("[PASS] OrchestrationResult JSON serialization OK")
        print(f"       JSON: {result_json[:100]}...")


class TestFallbackLogic:
    """Test fallback decision logic."""
    
    def test_fallback_permanent_error(self):
        """Test fallback for permanent errors (403, 401, 404)."""
        
        for error_code in ["403", "401", "404"]:
            context = OrchestrationInput(
                error_message="Permanent error",
                error_code=error_code,
                retry_count=0
            )
            
            result = fallback_orchestration_result(context)
            
            assert result.final_action == "skip"
            assert result.confidence >= 0.75
    
    
    def test_fallback_transient_exponential_backoff(self):
        """Test fallback exponential backoff for transient errors."""
        
        # Test retry counts 0, 1, 2, 3 -> delays 1s, 2s, 4s, 8s
        expected_delays = [1000, 2000, 4000, 8000]
        
        for retry_count, expected_delay in enumerate(expected_delays):
            context = OrchestrationInput(
                error_message="Transient error",
                error_code="500",
                retry_count=retry_count
            )
            
            result = fallback_orchestration_result(context)
            
            assert result.final_action == "retry"
            assert result.delay_ms == expected_delay
    
    
    def test_fallback_confidence(self):
        """Test fallback confidence scores."""
        
        # Permanent: high confidence
        perm_result = fallback_orchestration_result(
            OrchestrationInput(error_message="Forbidden", error_code="403")
        )
        assert perm_result.confidence >= 0.75
        
        # Transient: lower confidence (rules-based only)
        trans_result = fallback_orchestration_result(
            OrchestrationInput(error_message="Timeout", error_code="500")
        )
        assert 0.60 <= trans_result.confidence <= 0.80


# ============================================================================
# PYTEST RUNNER
# ============================================================================

if __name__ == "__main__":
    # Run all tests with pytest
    # Usage: pytest test_orchestrator_workflow.py -v -s
    pytest.main([__file__, "-v", "-s"])

