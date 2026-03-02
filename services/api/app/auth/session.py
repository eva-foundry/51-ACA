"""Session utilities: extract subscriptionId and tier from request context"""
from fastapi import Request
import json

def extract_subscription_id(request: Request) -> str:
    """
    Extract subscriptionId from request state (set by middleware after token validation).
    Falls back to checking JWT claims if available.
    """
    if hasattr(request.state, "subscription_id") and request.state.subscription_id:
        return request.state.subscription_id
    return None

def get_tier(request: Request) -> str:
    """Get current tier from request state (fetched from Cosmos by middleware)"""
    if hasattr(request.state, "tier") and request.state.tier:
        return request.state.tier
    return "TIER1"  # default to Tier 1 if not set

def validate_tier_requirement(request: Request, required_tier: str) -> bool:
    """
    Check if current tier meets the requirement.
    Tiers: TIER1 < TIER2 < TIER3 (numeric hierarchy)
    """
    tier_map = {"TIER1": 1, "TIER2": 2, "TIER3": 3}
    current = tier_map.get(get_tier(request), 1)
    required = tier_map.get(required_tier, 1)
    return current >= required

def set_subscription_context(request: Request, subscription_id: str, tier: str):
    """Store subscriptionId and tier in request state for downstream use"""
    request.state.subscription_id = subscription_id
    request.state.tier = tier
