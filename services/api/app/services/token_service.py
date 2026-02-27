# EVA-STORY: ACA-04-006
from msal import PublicClientApplication
from app.settings import get_settings

class TokenService:
    def __init__(self, client_id: str = None) -> None:
        settings = get_settings()
        self.client_id = client_id or settings.ACA_CLIENT_ID
        self.authority = "https://login.microsoftonline.com/common"
        self.app = PublicClientApplication(client_id=self.client_id, authority=self.authority)

    def initiate_device_code(self, subscription_id: str) -> dict:
        flow = self.app.initiate_device_flow(scopes=["https://management.azure.com/.default"])
        return {
            "device_code": flow["device_code"],
            "verification_uri": flow["verification_uri"],
            "expires_in": flow["expires_in"],
            "user_code": flow["user_code"]
        }

    def exchange_device_code(self, device_code: str) -> dict:
        flow = {"device_code": device_code}
        result = self.app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token"),
                "subscription_id": result.get("id_token_claims", {}).get("sub")
            }
        raise ValueError("Failed to exchange device code")
