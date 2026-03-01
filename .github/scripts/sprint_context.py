#!/usr/bin/env python3
# EVA-STORY: ACA-14-001
# sprint_context.py -- Unified SprintContext class merging correlation ID + LM tracer + timeline
#
# Per Opus recommendation (Deliverable 8, Change 1):
# "Merge components 1-3 into a single SprintContext object instead of three separate systems.
#  This eliminates propagation problem: context object is passed through all phases,
#  and every log line, LM call, and timeline mark goes through it.
#  One object, one file, zero propagation misses."
#
# Usage:
#   ctx = SprintContext("ACA-S11-20260301-a1b2c3d4")
#   ctx.log("D1", "Starting discovery phase")
#   call = ctx.record_lm_call(model="gpt-4o-mini", tokens_in=1000, tokens_out=500, phase="D1")
#   ctx.mark_timeline("response")
#   ctx.save()  # Writes .eva/sprints/SPRINT-11-context.json

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

# Import ACALMTracer from same directory
from aca_lm_tracer import ACALMTracer


class SprintContext:
    """
    Unified sprint execution context: correlation ID + LM tracing + timeline.
    
    This is the single point of truth for sprint state. Every operation that needs
    tracing, logging, or timeline marking goes through this class.
    
    Timeline Points (6 total):
      - created:   Sprint context initialized
      - submitted: First DPDCA phase submitted (D1)
      - response:  LM response received (end of thinking)
      - applied:   Code changes applied to filesystem
      - tested:    All tests pass
      - committed: Changes committed and pushed to git
    """
    
    def __init__(self, correlation_id: str, repo_root: Optional[str] = None):
        """
        Initialize SprintContext.
        
        Args:
            correlation_id: Full ID in format "ACA-S{NN}-{YYYYMMDD}-{uuid[:8]}"
            repo_root: Path to project root (defaults to current directory)
        """
        self.correlation_id = correlation_id
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
        # Extract sprint_id from correlation_id (ACA-S11-20260301-a1b2c3d4 -> SPRINT-11)
        # Format: ACA-S{NN}-YYYYMMDD-uuid8
        parts = correlation_id.split("-")
        if len(parts) >= 2 and parts[1].startswith("S"):
            sprint_num = parts[1][1:]  # "S11" -> "11"
            self.sprint_id = f"SPRINT-{sprint_num}"
        else:
            self.sprint_id = "SPRINT-UNKNOWN"
        
        # Initialize tracer
        self.tracer = ACALMTracer(correlation_id, repo_root=str(self.repo_root))
        
        # Timeline tracking (6 points)
        self.timeline: Dict[str, str] = {
            "created": datetime.now(timezone.utc).isoformat() + "Z"
        }
        
        # Log buffer (for audit trail)
        self.logs: list[str] = []
    
    def log(self, phase: str, message: str) -> str:
        """
        Log a message with automatic correlation ID propagation.
        
        Format: [TRACE:{correlation_id}] [{phase}] {message}
        
        Args:
            phase: DPDCA phase ("D1", "P", "D2", "Check", "Act") or any identifier
            message: Log message
        
        Returns:
            Formatted log line (for testing)
        """
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        log_line = f"[TRACE:{self.correlation_id}] [{phase}] [{timestamp}] {message}"
        
        self.logs.append(log_line)
        print(log_line)  # Also print to stdout for real-time visibility
        
        return log_line
    
    def record_lm_call(self, model: str, tokens_in: int, tokens_out: int, 
                      phase: str, response_text: str = "", 
                      error: Optional[str] = None):
        """
        Record an LM call and automatically track in tracer.
        
        Args:
            model: "gpt-4o" or "gpt-4o-mini"
            tokens_in: Input tokens
            tokens_out: Output tokens
            phase: DPDCA phase
            response_text: (optional) Response content
            error: (optional) Error message if call failed
        
        Returns:
            The LM call object
        """
        call = self.tracer.record_call(
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            phase=phase,
            response_text=response_text,
            error=error
        )
        
        cost = call._calculate_cost()
        # ASCII arrow for Windows console compatibility
        self.log(phase, f"LM call: {model} | tokens: {tokens_in}->{tokens_out} | cost: ${cost:.8f}")
        
        return call
    
    def mark_timeline(self, point: str) -> str:
        """
        Mark a timeline point with current timestamp.
        
        Valid points: created, submitted, response, applied, tested, committed
        Additional points allowed for custom tracking.
        
        Args:
            point: Timeline point name
        
        Returns:
            Timestamp string
        """
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        self.timeline[point] = timestamp
        
        self.log("timeline", f"Marked: {point} @ {timestamp}")
        
        return timestamp
    
    def get_summary(self) -> Dict[str, Any]:
        """Get current sprint context summary."""
        return {
            "correlation_id": self.correlation_id,
            "sprint_id": self.sprint_id,
            "timeline": self.timeline,
            "lm_summary": self.tracer.get_summary(),
            "models_used": self.tracer.models_used(),
            "log_lines": len(self.logs)
        }
    
    def save(self) -> Path:
        """
        Save full sprint context to .eva/sprints/{sprint_id}-context.json
        
        This is the single authoritative record for the sprint:
        - Correlation ID
        - All LM calls with tokens and costs
        - Complete timeline with timestamps
        - All log lines
        
        Returns:
            Path to saved file
        """
        # Ensure directory exists
        sprints_dir = self.repo_root / ".eva" / "sprints"
        sprints_dir.mkdir(parents=True, exist_ok=True)
        
        context_file = sprints_dir / f"{self.sprint_id}-context.json"
        
        # Build full context
        context = {
            "correlation_id": self.correlation_id,
            "sprint_id": self.sprint_id,
            "created_at": self.timeline.get("created"),
            "timeline": self.timeline,
            "lm_calls": [call.to_dict() for call in self.tracer.lm_calls],
            "lm_summary": self.tracer.get_summary(),
            "models_used": self.tracer.models_used(),
            "logs": self.logs
        }
        
        # Write to file
        context_file.write_text(json.dumps(context, indent=2), encoding="utf-8")
        
        self.log("saving", f"Context saved: {context_file}")
        print(f"[INFO] Sprint context written: {context_file}")
        
        return context_file
    
    def cost_summary(self) -> Dict[str, Any]:
        """Get cost breakdown by phase."""
        summary = self.tracer.get_summary()
        
        # Build per-phase breakdown
        phases_seen = set(call.phase for call in self.tracer.lm_calls)
        phase_costs = {
            phase: self.tracer.cost_per_phase(phase)
            for phase in sorted(phases_seen)
        }
        
        return {
            "total_cost_usd": summary["total_cost_usd"],
            "total_tokens": summary["total_tokens_in"] + summary["total_tokens_out"],
            "by_phase": phase_costs,
            "models_used": self.tracer.models_used()
        }


if __name__ == "__main__":
    # Example usage
    ctx = SprintContext("ACA-S11-20260301-a1b2c3d4")
    
    # Log some operations
    ctx.log("D1", "Starting discovery phase")
    ctx.mark_timeline("submitted")
    
    # Simulate an LM call
    ctx.record_lm_call(
        model="gpt-4o-mini",
        tokens_in=2840,
        tokens_out=450,
        phase="D1"
    )
    
    ctx.mark_timeline("response")
    
    # Additional phase
    ctx.log("P", "Planning sprint")
    ctx.record_lm_call(
        model="gpt-4o",
        tokens_in=3200,
        tokens_out=712,
        phase="P"
    )
    
    ctx.mark_timeline("applied")
    ctx.log("D2", "Executing")
    ctx.mark_timeline("tested")
    ctx.mark_timeline("committed")
    
    # Save and print summary
    ctx.save()
    print("\n[SUMMARY]")
    print(json.dumps(ctx.get_summary(), indent=2))
    print("\n[COST BREAKDOWN]")
    print(json.dumps(ctx.cost_summary(), indent=2))
