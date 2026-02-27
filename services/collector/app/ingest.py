import os
from datetime import datetime, timezone

from azure.cosmos import CosmosClient

COSMOS_DB = os.environ.get("ACA_COSMOS_DB", "aca-db")

# EVA-STORY: ACA-02-017

def _client():
    return CosmosClient(
        url=os.environ["ACA_COSMOS_URL"],
        credential=os.environ["ACA_COSMOS_KEY"],
    )

class Ingestor:
    def __init__(self, scan_id: str, subscription_id: str):
        self.scan_id = scan_id
        self.sub_id = subscription_id
        self.db = _client().get_database_client(COSMOS_DB)
        self._now = datetime.now(timezone.utc).isoformat()

    def _container(self, name: str):
        return self.db.get_container_client(name)

    def _wrap(self, data: dict, item_id: str) -> dict:
        return {
            "id": item_id,
            "subscriptionId": self.sub_id,
            "scanId": self.scan_id,
            "collectedUtc": self._now,
            **data,
        }

    def save_inventory(self, resources: list[dict]) -> None:
        c = self._container("inventories")
        c.upsert_item(self._wrap(
            {"resources": resources, "count": len(resources)},
            f"{self.scan_id}-inventory",
        ))

    def save_cost_data(self, rows: list[dict]) -> None:
        c = self._container("cost-data")
        c.upsert_item(self._wrap(
            {"rows": rows, "row_count": len(rows)},
            f"{self.scan_id}-cost",
        ))

    def save_advisor(self, recommendations: list[dict]) -> None:
        c = self._container("advisor")
        c.upsert_item(self._wrap(
            {"recommendations": recommendations, "count": len(recommendations)},
            f"{self.scan_id}-advisor",
        ))

    def save_policy(self, policy_state: dict) -> None:
        c = self._container("inventories")
        c.upsert_item(self._wrap(
            {"policy_state": policy_state},
            f"{self.scan_id}-policy",
        ))

    def save_network(self, topology: dict) -> None:
        c = self._container("inventories")
        c.upsert_item(self._wrap(
            {"network_topology": topology},
            f"{self.scan_id}-network",
        ))

    def mark_collection_complete(self) -> None:
        c = self._container("scans")
        c.upsert_item({
            "id": self.scan_id,
            "subscriptionId": self.sub_id,
            "status": "collected",
            "collectionCompletedUtc": self._now,
        }, partition_key=self.sub_id)
        self._trigger_analysis_job(scan_id=self.scan_id, subscription_id=self.sub_id)

    def _trigger_analysis_job(self, scan_id: str, subscription_id: str) -> None:
        job_name = os.environ.get("ACA_ANALYSIS_JOB_NAME", "")
        resource_group = os.environ.get("ACA_RESOURCE_GROUP", "")

        if not job_name or not resource_group:
            print("[WARN] ACA_ANALYSIS_JOB_NAME or ACA_RESOURCE_GROUP not set -- skipping analysis trigger")
            return

        try:
            from azure.mgmt.appcontainers import ContainerAppsAPIClient
            from azure.identity import DefaultAzureCredential

            client = ContainerAppsAPIClient(credential=DefaultAzureCredential())
            client.jobs.start(
                resource_group_name=resource_group,
                job_name=job_name,
                properties={
                    "template": {
                        "containers": [
                            {
                                "name": "analysis",
                                "env": [
                                    {"name": "SCAN_ID", "value": scan_id},
                                    {"name": "SUBSCRIPTION_ID", "value": subscription_id},
                                ],
                            }
                        ]
                    }
                }
            )
        except ImportError:
            print("[WARN] azure.mgmt.appcontainers not installed -- falling back to subprocess")
            try:
                import subprocess
                subprocess.run([
                    "az", "containerapp", "job", "start",
                    "--name", job_name,
                    "--resource-group", resource_group,
                    "--environment-variables", f"SCAN_ID={scan_id} SUBSCRIPTION_ID={subscription_id}"
                ], check=True)
            except Exception as e:
                print(f"[FAIL] Failed to trigger analysis job via subprocess: {e}")
        except Exception as e:
            print(f"[FAIL] Failed to trigger analysis job via SDK: {e}")