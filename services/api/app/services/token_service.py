# EVA-STORY: ACA-04-006
# EVA-STORY: ACA-04-008
"""
TokenService -- MSAL device-code flow for delegated Azure subscription auth.

Multi-tenant authority: https://login.microsoftonline.com/common
Scopes: https://management.azure.com/.default

DI pattern: pass client_id= in __init__ to bypass settings (for tests).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import msal

from app.settings import get_settings


class TokenService:
    def __init__(self, client_id: Optional[str] = None) -> None:
        # Accept injected client_id for unit tests -- avoids env var requirement
        self.client_id = client_id or get_settings().ACA_CLIENT_ID

    def _build_app(self) -> msal.PublicClientApplication:
        return msal.PublicClientApplication(
            client_id=self.client_id,
            authority="https://login.microsoftonline.com/common",
        )

    def initiate_device_code(self, subscription_id: str) -> Dict[str, Any]:
        """
        Initiate MSAL device-code flow.

        Returns dict with device_code, verification_uri, user_code, expires_in.
        The caller must display verification_uri and user_code to the end-user,
        then poll exchange_device_code() until the user completes sign-in.
        """
        app = self._build_app()
        flow = app.initiate_device_flow(
            scopes=["https://management.azure.com/.default"]
        )
        if "error" in flow:
            raise RuntimeError(
                f"[FAIL] MSAL device flow: {flow['error']}: {flow.get('error_description', '')}"
            )
        return {
            "device_code": flow["device_code"],
            "verification_uri": flow["verification_uri"],
            "user_code": flow["message"],
            "expires_in": flow["expires_in"],
        }

    def exchange_device_code(self, flow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Poll for token after user completes device sign-in.

        Pass the original flow dict returned by initiate_device_code().
        Returns access_token + refresh_token on success.
        Raises RuntimeError if token acquisition fails.
        """
        app = self._build_app()
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            raise RuntimeError(
                f"[FAIL] MSAL token exchange: {result.get('error_description', 'unknown error')}"
            )
        return {
            "access_token": result["access_token"],
            "refresh_token": result.get("refresh_token", ""),
            "expires_in": result.get("expires_in", 3600),
        }
