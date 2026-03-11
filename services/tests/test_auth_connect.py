# EVA-STORY: ACA-04-008
"""Compatibility tests for current POST /v1/auth/connect contract.

Current router contract accepts:
- delegated_token (required)
- desired_tier (optional, default TIER1)
"""
import asyncio
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from services.api.app.routers.auth import connect_subscription, ConnectRequest


def _request() -> Request:
    return Request({"type": "http", "headers": []})


def test_connect_with_default_tier_returns_connected():
    req = ConnectRequest(delegated_token="fake-token")
    result = asyncio.run(connect_subscription(_request(), req))

    assert result["subscriptionId"] == "00000000-0000-0000-0000-000000000001"
    assert result["tier"] == "TIER1"
    assert result["status"] == "connected"


def test_connect_with_desired_tier_returns_requested_tier():
    req = ConnectRequest(delegated_token="fake-token", desired_tier="TIER2")
    result = asyncio.run(connect_subscription(_request(), req))

    assert result["tier"] == "TIER2"
    assert result["status"] == "connected"


def test_connect_rejects_empty_token():
    req = ConnectRequest(delegated_token="", desired_tier="TIER1")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(connect_subscription(_request(), req))
    assert exc_info.value.status_code == 400


def test_connect_returns_timestamp_with_z_suffix():
    req = ConnectRequest(delegated_token="fake-token")
    result = asyncio.run(connect_subscription(_request(), req))
    assert result["connectedAt"].endswith("Z")
