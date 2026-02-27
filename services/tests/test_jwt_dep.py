# EVA-STORY: ACA-04-002
"""
Tests for ACA-04-002: verify_token FastAPI JWT dependency.

Tests the dependency function directly (bypasses FastAPI DI overhead).
No env vars required -- jwt.decode is patched.
"""
import asyncio
import pytest
from unittest.mock import patch
from fastapi import HTTPException

from services.api.app.deps.auth import verify_token


def test_no_token_raises_401():
    """ACA-04-002: verify_token raises HTTP 401 when token is None."""
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(verify_token(token=None))
    assert exc_info.value.status_code == 401
    assert "Authentication required" in exc_info.value.detail


def test_invalid_token_raises_401():
    """ACA-04-002: verify_token raises HTTP 401 when JWT is malformed."""
    import jwt as pyjwt
    with patch("services.api.app.deps.auth.jwt.decode") as mock_decode:
        mock_decode.side_effect = pyjwt.InvalidTokenError("bad token")
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(verify_token(token="not.a.real.jwt"))
    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail


def test_valid_token_returns_payload():
    """ACA-04-002: verify_token returns decoded payload dict for a valid token."""
    mock_payload = {"sub": "user-oid-123", "oid": "oid-456", "tid": "tenant-789"}
    with patch("services.api.app.deps.auth.jwt.decode", return_value=mock_payload):
        result = asyncio.run(verify_token(token="eyJvalid.jwt.token"))
    assert result == mock_payload
    assert result["sub"] == "user-oid-123"
