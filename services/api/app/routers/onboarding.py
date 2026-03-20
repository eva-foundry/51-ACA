# EVA-STORY: ACA-15-004
"""Onboarding session routes: init, read state, and decisions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.onboarding_runtime import build_onboarding_schema, provision_phase2_cosmos_containers

router = APIRouter(tags=["onboarding"])

_SESSION_STORE: dict[str, dict[str, Any]] = {}


class OnboardingInitRequest(BaseModel):
    subscription_id: str = Field(..., min_length=2)
    tenant_id: str | None = None


class DecisionRequest(BaseModel):
    gate: str = Field(..., min_length=2)
    decision: str = Field(..., pattern="^(approve|reject|retry)$")


@router.post("/init")
def init_onboarding(payload: OnboardingInitRequest) -> dict[str, Any]:
    session_id = f"onb_{uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    _SESSION_STORE[session_id] = {
        "session_id": session_id,
        "subscription_id": payload.subscription_id,
        "tenant_id": payload.tenant_id,
        "created_at": now,
        "updated_at": now,
        "state": "initialized",
        "decisions": [],
        "schema": build_onboarding_schema(),
        "provisioning_plan": provision_phase2_cosmos_containers(payload.subscription_id),
    }
    return _SESSION_STORE[session_id]


@router.get("/{session_id}")
def get_onboarding(session_id: str) -> dict[str, Any]:
    session = _SESSION_STORE.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="onboarding session not found")
    return session


@router.post("/{session_id}/decision")
def apply_decision(session_id: str, payload: DecisionRequest) -> dict[str, Any]:
    session = _SESSION_STORE.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="onboarding session not found")

    decision = {
        "gate": payload.gate,
        "decision": payload.decision,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    session["decisions"].append(decision)
    session["updated_at"] = decision["timestamp"]
    session["state"] = "in_review" if payload.decision == "retry" else "approved" if payload.decision == "approve" else "rejected"
    return session
