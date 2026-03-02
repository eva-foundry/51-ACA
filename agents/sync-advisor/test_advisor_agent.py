"""
# EVA-STORY: ACA-17-004

ACA-17-004: Sync Advisor Agent Test Suite

4 test scenarios covering acceptance criteria:
1. All 21 stories failed -> "retry_all"
2. 3 stories failed -> "retry_failed_only"
3. CB.OPEN + 15 failed -> "pause+increase" + parallelism=1
4. Rate-limit pattern -> increase RUs guidance + reduced parallelism
"""

import asyncio
import pytest
from advisor_agent import (
    AdvisorContext,
    AdvisorRecommendation,
    fallback_sync_advisor,
    get_advisor_recommendation
)


class TestSyncAdvisor:
    """Sync Advisor Agent test suite."""
    
    def test_scenario_all_stories_failed(self):
        """
        Scenario 1: All 21 stories failed -> "retry_all"
        
        Input:
        - subscription_size: medium
        - failed_story_count: 21
        - total_stories: 21
        - cb_state: closed
        
        Expected:
        - action: retry_all
        - parallelism_level: 1 (start serial)
        - confidence >= 0.9
        - Contains "transient"
        """
        
        context = AdvisorContext(
            subscription_size="medium",
            failed_story_count=21,
            total_stories=21,
            cb_state="closed"
        )
        
        recommendation = fallback_sync_advisor(context)
        
        assert recommendation.recommended_action == "retry_all"
        assert recommendation.parallelism_level == 1
        assert recommendation.confidence >= 0.9
        assert "transient" in recommendation.rationale.lower()
        assert recommendation.advisor_latency_ms is not None
        
        print(f"[PASS] Scenario 1: All failed -> {recommendation.recommended_action}")
        print(f"       Confidence: {recommendation.confidence}, Parallelism: {recommendation.parallelism_level}")
    
    
    def test_scenario_partial_failure_retry_failed_only(self):
        """
        Scenario 2: 3 stories failed -> "retry_failed_only"
        
        Input:
        - failed_story_count: 3
        - total_stories: 21
        - cb_state: closed
        
        Expected:
        - action: retry_failed_only
        - parallelism_level: 3 (can safely parallelize)
        - confidence >= 0.85
        - guidance mentions checkpoint/skip completed
        """
        
        context = AdvisorContext(
            subscription_size="medium",
            failed_story_count=3,
            total_stories=21,
            cb_state="closed"
        )
        
        recommendation = fallback_sync_advisor(context)
        
        assert recommendation.recommended_action == "retry_failed_only"
        assert recommendation.parallelism_level == 3
        assert recommendation.confidence >= 0.85
        assert "checkpoint" in recommendation.guidance.lower() or "skip" in recommendation.guidance.lower()
        assert "18 completed" in recommendation.guidance or "18" in recommendation.guidance
        
        print(f"[PASS] Scenario 2: Partial failure -> {recommendation.recommended_action}")
        print(f"       Parallelism: {recommendation.parallelism_level}, Confidence: {recommendation.confidence}")
    
    
    def test_scenario_circuit_breaker_open_many_failed(self):
        """
        Scenario 3: CB.OPEN + >50% failed (15 out of 21) -> "pause+increase"
        
        Input:
        - failed_story_count: 15
        - total_stories: 21
        - cb_state: open
        
        Expected:
        - action: pause+increase
        - parallelism_level: 1 (serial)
        - confidence >= 0.88
        - guidance mentions RUs, pause, wait
        """
        
        context = AdvisorContext(
            subscription_size="large",
            failed_story_count=15,
            total_stories=21,
            cb_state="open"
        )
        
        recommendation = fallback_sync_advisor(context)
        
        assert recommendation.recommended_action == "pause+increase"
        assert recommendation.parallelism_level == 1
        assert recommendation.confidence >= 0.88
        assert "pause" in recommendation.guidance.lower()
        assert ("ru" in recommendation.guidance.lower() or "provisioned throughput" in recommendation.guidance.lower())
        
        print(f"[PASS] Scenario 3: CB.OPEN + >50% failed -> {recommendation.recommended_action}")
        print(f"       Parallelism: {recommendation.parallelism_level}, Guidance: '{recommendation.guidance[:60]}...'")
    
    
    def test_scenario_rate_limit_pattern(self):
        """
        Scenario 4: Rate-limit (429) pattern detected -> "pause+increase"
        
        Input:
        - last_error_pattern: "rate-limit"
        - failed_story_count: 10
        
        Expected:
        - action: pause+increase
        - parallelism_level: 1
        - guidance mentions RUs, rate-limit/429, parallelism
        - confidence >= 0.85
        """
        
        context = AdvisorContext(
            subscription_size="medium",
            failed_story_count=10,
            total_stories=21,
            cb_state="closed",
            last_error_pattern="rate-limit"
        )
        
        recommendation = fallback_sync_advisor(context)
        
        assert recommendation.recommended_action == "pause+increase"
        assert recommendation.parallelism_level == 1
        assert recommendation.confidence >= 0.85
        assert ("rate-limit" in recommendation.guidance.lower() or "429" in recommendation.guidance or "ru" in recommendation.guidance.lower())
        
        print(f"[PASS] Scenario 4: Rate-limit pattern -> {recommendation.recommended_action}")
        print(f"       Guidance: '{recommendation.guidance[:60]}...'")


class TestAsyncAdvisor:
    """Async advisor function tests."""
    
    @pytest.mark.asyncio
    async def test_async_get_recommendation(self):
        """Test async recommendation endpoint."""
        
        context = AdvisorContext(
            subscription_size="medium",
            failed_story_count=21,
            total_stories=21,
            cb_state="closed"
        )
        
        recommendation = await get_advisor_recommendation(context, timeout_ms=500)
        
        assert isinstance(recommendation, AdvisorRecommendation)
        assert recommendation.recommended_action in ["retry_all", "retry_failed_only", "pause+increase"]
        assert 1 <= recommendation.parallelism_level <= 5
        assert 0.65 <= recommendation.confidence <= 1.0
        assert recommendation.advisor_latency_ms >= 0  # May be 0 for very fast local calls
        
        print(f"[PASS] Async recommendation: {recommendation.recommended_action} in {recommendation.advisor_latency_ms}ms")
    
    
    @pytest.mark.asyncio
    async def test_async_timeout_fallback(self):
        """Test async function with timeout (should fallback gracefully)."""
        
        context = AdvisorContext(
            subscription_size="small",
            failed_story_count=5,
            total_stories=21
        )
        
        # Call with very short timeout
        recommendation = await get_advisor_recommendation(context, timeout_ms=1)
        
        # Should still return valid recommendation (fallback)
        assert recommendation.recommended_action is not None
        assert recommendation.confidence >= 0.65
        
        print(f"[PASS] Timeout fallback: {recommendation.recommended_action} (fallback logic engaged)")


class TestDataModels:
    """Test data model serialization."""
    
    def test_advisor_context_to_dict(self):
        """Test AdvisorContext serialization."""
        
        context = AdvisorContext(
            subscription_size="large",
            failed_story_count=5,
            total_stories=21,
            cb_state="open",
            last_error_pattern="rate-limit",
            elapsed_ms=3000,
            retry_count=2
        )
        
        ctx_dict = context.to_dict()
        
        assert ctx_dict["subscription_size"] == "large"
        assert ctx_dict["failed_story_count"] == 5
        assert ctx_dict["cb_state"] == "open"
        assert ctx_dict["last_error_pattern"] == "rate-limit"
        assert ctx_dict["retry_count"] == 2
        
        print(f"[PASS] AdvisorContext.to_dict() serialization OK")
    
    
    def test_recommendation_to_dict_and_json(self):
        """Test AdvisorRecommendation serialization."""
        
        rec = AdvisorRecommendation(
            recommended_action="retry_all",
            parallelism_level=1,
            guidance="Test guidance",
            confidence=0.95,
            rationale="Test rationale",
            best_practice_reference="18-azure-best: example"
        )
        
        # Test to_dict()
        rec_dict = rec.to_dict()
        assert rec_dict["recommended_action"] == "retry_all"
        assert rec_dict["parallelism_level"] == 1
        assert rec_dict["confidence"] == 0.95
        
        # Test to_json()
        rec_json = rec.to_json()
        assert isinstance(rec_json, str)
        assert "retry_all" in rec_json
        assert "0.95" in rec_json
        
        print(f"[PASS] AdvisorRecommendation serialization OK")
        print(f"       JSON: {rec_json[:80]}...")


# ============================================================================
# PYTEST RUNNER
# ============================================================================

if __name__ == "__main__":
    # Run all tests with pytest
    # Usage: pytest test_advisor_agent.py -v
    pytest.main([__file__, "-v", "-s"])
