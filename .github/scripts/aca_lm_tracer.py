#!/usr/bin/env python3
# EVA-STORY: ACA-14-001
# aca_lm_tracer.py -- ACA-specific LLM interaction logging with OpenAI direct pricing
#
# Adapted from 37-data-model lm_tracer.py for BYOK (Bring Your Own Key) model.
# Uses OpenAI direct pricing instead of GitHub Models pricing.
#
# Captures: timestamp, model, tokens, cost, latency, prompt hash, response hash
# Stores to .eva/traces/ for audit trail and cost analysis
#
# Usage:
#   tracer = ACALMTracer(correlation_id="ACA-S11-20260301-a1b2c3d4")
#   call = tracer.record_call(model="gpt-4o-mini", tokens_in=1000, tokens_out=500, phase="D1")
#   tracer.save()  # Writes .eva/traces/ACA-S11-20260301-a1b2c3d4-lm-calls.json

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List


# OpenAI Direct Pricing (BYOK model - user brings their own API key)
# Pricing as of 2026-03-01 (https://openai.com/pricing)
OPENAI_MODELS = {
    "gpt-4o": {
        "provider": "OpenAI",
        "input_price_per_mtok": 2.50,      # $2.50 per 1M input tokens
        "output_price_per_mtok": 10.00,    # $10.00 per 1M output tokens
        "max_tokens": 128000,
        "use_for": "Critical infrastructure: auth, security, complex state management"
    },
    "gpt-4o-mini": {
        "provider": "OpenAI",
        "input_price_per_mtok": 0.15,      # $0.15 per 1M input tokens
        "output_price_per_mtok": 0.60,     # $0.60 per 1M output tokens
        "max_tokens": 128000,
        "use_for": "Routine work: 95% of sprint tasks (helper functions, refactoring, docs)"
    }
}


class ACALMCall:
    """Single LLM API call with full tracing (ACA-specific)."""
    
    def __init__(self, model: str, phase: str):
        self.model = model
        self.phase = phase
        
        self.timestamp_start = datetime.now(timezone.utc)
        self.timestamp_end: Optional[datetime] = None
        
        self.tokens_in = 0
        self.tokens_out = 0
        self.response_text = ""
        self.error: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Export as JSON-serializable dict."""
        cost_usd = self._calculate_cost()
        latency_ms = self._calculate_latency()
        
        return {
            "model": self.model,
            "phase": self.phase,
            "timestamp_start": self.timestamp_start.isoformat(),
            "timestamp_end": self.timestamp_end.isoformat() if self.timestamp_end else None,
            "latency_ms": latency_ms,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost_usd": round(cost_usd, 8),
            "error": self.error
        }
    
    def _calculate_cost(self) -> float:
        """Calculate cost in USD based on OpenAI direct pricing."""
        if self.model not in OPENAI_MODELS:
            return 0.0
        
        config = OPENAI_MODELS[self.model]
        input_cost = (self.tokens_in / 1_000_000) * config["input_price_per_mtok"]
        output_cost = (self.tokens_out / 1_000_000) * config["output_price_per_mtok"]
        return input_cost + output_cost
    
    def _calculate_latency(self) -> int:
        """Calculate latency in milliseconds."""
        if not self.timestamp_end:
            return 0
        delta = self.timestamp_end - self.timestamp_start
        return int(delta.total_seconds() * 1000)


class ACALMTracer:
    """Unified LLM tracing across sprint execution (ACA-specific)."""
    
    def __init__(self, correlation_id: str, repo_root: Optional[str] = None):
        self.correlation_id = correlation_id
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
        self.lm_calls: List[ACALMCall] = []
        self.created_at = datetime.now(timezone.utc)
        
    def record_call(self, model: str, tokens_in: int, tokens_out: int, 
                   phase: str, response_text: str = "", 
                   error: Optional[str] = None) -> ACALMCall:
        """
        Record an LM call.
        
        Args:
            model: "gpt-4o" or "gpt-4o-mini"
            tokens_in: input tokens consumed
            tokens_out: output tokens generated
            phase: DPDCA phase ("D1", "P", "D2", "Check", "Act")
            response_text: (optional) response content
            error: (optional) error message if call failed
        
        Returns:
            ACALMCall object with cost calculated
        """
        call = ACALMCall(model, phase)
        call.timestamp_end = datetime.now(timezone.utc)
        call.response_text = response_text
        call.tokens_in = tokens_in
        call.tokens_out = tokens_out
        call.error = error
        
        self.lm_calls.append(call)
        return call
    
    def save(self) -> Path:
        """Write trace to .eva/traces/{correlation_id}-lm-calls.json"""
        eva_dir = self.repo_root / ".eva" / "traces"
        eva_dir.mkdir(parents=True, exist_ok=True)
        
        trace_file = eva_dir / f"{self.correlation_id}-lm-calls.json"
        
        data = {
            "correlation_id": self.correlation_id,
            "created_at": self.created_at.isoformat(),
            "lm_calls": [call.to_dict() for call in self.lm_calls],
            "summary": {
                "total_calls": len(self.lm_calls),
                "total_tokens_in": sum(c.tokens_in for c in self.lm_calls),
                "total_tokens_out": sum(c.tokens_out for c in self.lm_calls),
                "total_cost_usd": round(sum(c._calculate_cost() for c in self.lm_calls), 8),
                "total_latency_ms": sum(c._calculate_latency() for c in self.lm_calls),
            }
        }
        
        trace_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"[INFO] Trace written: {trace_file}")
        return trace_file
    
    def get_summary(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        return {
            "total_calls": len(self.lm_calls),
            "total_tokens_in": sum(c.tokens_in for c in self.lm_calls),
            "total_tokens_out": sum(c.tokens_out for c in self.lm_calls),
            "total_cost_usd": round(sum(c._calculate_cost() for c in self.lm_calls), 8),
            "total_latency_ms": sum(c._calculate_latency() for c in self.lm_calls),
        }

    def cost_per_phase(self, phase: str) -> float:
        """Get total cost for a specific DPDCA phase."""
        return round(sum(
            call._calculate_cost() 
            for call in self.lm_calls 
            if call.phase == phase
        ), 8)

    def models_used(self) -> List[str]:
        """Get list of unique models used in this sprint."""
        return sorted(list(set(call.model for call in self.lm_calls)))


if __name__ == "__main__":
    # Example usage
    tracer = ACALMTracer("ACA-S11-20260301-a1b2c3d4")
    
    # Simulate Phase D1 (Discover) calls
    tracer.record_call(
        model="gpt-4o-mini",
        tokens_in=2840,
        tokens_out=450,
        phase="D1",
        response_text="Analysis complete..."
    )
    
    # Simulate Phase P (Plan) critical call
    tracer.record_call(
        model="gpt-4o",
        tokens_in=3200,
        tokens_out=712,
        phase="P",
        response_text="Sprint plan generated..."
    )
    
    tracer.save()
    print(json.dumps(tracer.get_summary(), indent=2))
