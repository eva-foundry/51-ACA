# EVA-STORY: ACA-04-008
"""
Tests for ACA-04-008: POST /v1/auth/connect device-code flow + Cosmos write.

Tests the route function directly (no TestClient startup overhead).
Patches TokenService and ClientsRepo so no env vars are required.
"""
import asyncio
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

MOCK_FLOW = {
    "device_code": "dc-xyz-456",
    "verification_uri": "https://aka.ms/devicelogin",
    "user_code": "XYZABC",
    "expires_in": 900,
}


def test_connect_delegated_returns_device_code():
    """ACA-04-008: delegated connect returns device_code + verification_uri + subscription_id."""
    with patch("services.api.app.routers.auth.TokenService") as MockTS, \
         patch("services.api.app.routers.auth.ClientsRepo") as MockCR:
        MockTS.return_value.initiate_device_code.return_value = MOCK_FLOW
        MockCR.return_value.upsert.return_value = {}

        from services.api.app.routers.auth import connect_subscription, ConnectRequest
        req = ConnectRequest(
            subscription_id="sub-test-abc",
            connection_mode="delegated",
        )
        result = asyncio.run(connect_subscription(req))

    assert result["verification_uri"] == "https://aka.ms/devicelogin"
    assert result["device_code"] == "dc-xyz-456"
    assert result["subscription_id"] == "sub-test-abc"
    assert result["expires_in"] == 900


def test_connect_delegated_writes_pending_client():
    """ACA-04-008: connect calls ClientsRepo.upsert with status=pending."""
    with patch("services.api.app.routers.auth.TokenService") as MockTS, \
         patch("services.api.app.routers.auth.ClientsRepo") as MockCR:
        MockTS.return_value.initiate_device_code.return_value = MOCK_FLOW
        mock_repo = MockCR.return_value

        from services.api.app.routers.auth import connect_subscription, ConnectRequest
        req = ConnectRequest(subscription_id="sub-test-abc", connection_mode="delegated")
        asyncio.run(connect_subscription(req))

    mock_repo.upsert.assert_called_once()
    call_kwargs = mock_repo.upsert.call_args[1]
    assert call_kwargs["subscription_id"] == "sub-test-abc"
    assert call_kwargs["auth_mode"] == "delegated"
    assert call_kwargs["status"] == "pending"


def test_connect_sp_returns_501():
    """ACA-04-008: service_principal connection_mode raises HTTP 501."""
    from services.api.app.routers.auth import connect_subscription, ConnectRequest
    req = ConnectRequest(subscription_id="sub-test-abc", connection_mode="service_principal")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(connect_subscription(req))
    assert exc_info.value.status_code == 501


def test_connect_propagates_msal_error_as_502():
    """ACA-04-008: RuntimeError from TokenService becomes HTTP 502."""
    with patch("services.api.app.routers.auth.TokenService") as MockTS, \
         patch("services.api.app.routers.auth.ClientsRepo"):
        MockTS.return_value.initiate_device_code.side_effect = RuntimeError("[FAIL] MSAL error")

        from services.api.app.routers.auth import connect_subscription, ConnectRequest
        req = ConnectRequest(subscription_id="sub-test-abc", connection_mode="delegated")
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(connect_subscription(req))

    assert exc_info.value.status_code == 502
