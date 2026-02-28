# EVA-STORY: ACA-03-016
import requests
from typing import Optional, Dict, Any

class ResourceGraphClient:
    def __init__(self, endpoint: str, token: str) -> None:
        self.endpoint = endpoint
        self.token = token

    def query(self, query: str, subscription_id: str, skip_token: Optional[str] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "subscriptions": [subscription_id],
        }

        if skip_token:
            payload["skipToken"] = skip_token

        response = requests.post(self.endpoint, json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    def paginate_query(self, query: str, subscription_id: str) -> list[Dict[str, Any]]:
        all_results = []
        skip_token = None

        while True:
            result = self.query(query, subscription_id, skip_token)
            all_results.extend(result.get("data", []))

            skip_token = result.get("skipToken")
            if not skip_token:
                break

        return all_results
