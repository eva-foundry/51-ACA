# EVA-STORY: ACA-03-016
from app.db.cosmos import query_items

def evaluate_r06_stale_environments(subscription_id: str, scan_id: str) -> list[dict]:
    """
    Evaluate R-06 rule: Returns a finding if there are 3 or more App Service sites.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.
        scan_id (str): The scan ID to filter inventory.

    Returns:
        list[dict]: Findings if the rule is triggered.
    """
    container_name = "inventories"
    query = "SELECT c.resources FROM c WHERE c.scanId = @scanId"
    parameters = [{"name": "@scanId", "value": scan_id}]

    inventory_items = query_items(container_name, query, parameters, partition_key=subscription_id)

    if not inventory_items:
        return []

    resources = inventory_items[0].get("resources", [])
    app_service_sites = [r for r in resources if r.get("resourceType") == "Microsoft.Web/sites"]

    if len(app_service_sites) >= 3:
        return [
            {
                "id": f"r06-{scan_id}",
                "title": "Consolidate App Service Sites",
                "category": "resource-consolidation",
                "estimated_saving_low": 100,
                "estimated_saving_high": 500,
                "effort_class": "medium",
                "risk_class": "low",
                "subscriptionId": subscription_id,
                "scanId": scan_id
            }
        ]

    return []