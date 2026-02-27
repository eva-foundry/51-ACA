# EVA-STORY: ACA-04-006
"""
Tests for ACA-04-006: TokenService MSAL device-code flow.

Uses TokenService(client_id="test-client") to bypass env var requirement.
Mocks msal.PublicClientApplication to avoid real MSAL network calls.
"""
import pytest
from unittest.mock import MagicMock, patch

from services.api.app.services.token_service import TokenService


MOCK_FLOW = {
    "device_code": "dc-abc-123",
    "verification_uri": "https://aka.ms/devicelogin",
    "message": "ABCDEFGH",
    "expires_in": 900,
}


def test_initiate_device_code_returns_expected_keys():
    """ACA-04-006: initiate_device_code returns device_code, verification_uri, user_code, expires_in."""
    with patch("services.api.app.services.token_service.msal.PublicClientApplication") as MockApp:
        MockApp.return_value.initiate_device_flow.return_value = MOCK_FLOW
        svc = TokenService(client_id="test-client-id")
        result = svc.initiate_device_code("sub-test-123")

    assert result["device_code"] == "dc-abc-123"
    assert result["verification_uri"] == "https://aka.ms/devicelogin"
    assert result["user_code"] == "ABCDEFGH"
    assert result["expires_in"] == 900


def test_initiate_device_code_uses_common_authority():
    """ACA-04-006: MSAL app must use multi-tenant authority=common."""
    with patch("services.api.app.services.token_service.msal.PublicClientApplication") as MockApp:
        MockApp.return_value.initiate_device_flow.return_value = MOCK_FLOW
        svc = TokenService(client_id="test-client-id")
        svc.initiate_device_code("sub-test-123")

    init_kwargs = MockApp.call_args[1]
    assert "common" in init_kwargs.get("authority", ""), (
        "MSAL authority must contain 'common' for multi-tenant -- "
        f"got: {init_kwargs.get('authority')}"
    )


def test_initiate_device_code_raises_on_msal_error():
    """ACA-04-006: RuntimeError raised when MSAL returns an error dict."""
    with patch("services.api.app.services.token_service.msal.PublicClientApplication") as MockApp:
        MockApp.return_value.initiate_device_flow.return_value = {
            "error": "access_denied",
            "error_description": "User denied consent",
        }
        svc = TokenService(client_id="test-client-id")
        with pytest.raises(RuntimeError, match="MSAL device flow"):
            svc.initiate_device_code("sub-test-123")


def test_exchange_device_code_returns_tokens():
    """ACA-04-006: exchange_device_code returns access_token and refresh_token."""
    mock_result = {
        "access_token": "eyJaccesstoken",
        "refresh_token": "eyJrefreshtoken",
        "expires_in": 3600,
    }
    with patch("services.api.app.services.token_service.msal.PublicClientApplication") as MockApp:
        MockApp.return_value.acquire_token_by_device_flow.return_value = mock_result
        svc = TokenService(client_id="test-client-id")
        result = svc.exchange_device_code({"device_code": "dc-abc"})

    assert result["access_token"] == "eyJaccesstoken"
    assert result["refresh_token"] == "eyJrefreshtoken"
