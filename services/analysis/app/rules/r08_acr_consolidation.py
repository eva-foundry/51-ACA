# EVA-STORY: ACA-03-018
from app.db.cosmos import query_items

def evaluate_acr_consolidation(subscription_id: str, scan_id: str) -> list[dict]:
    """
    Evaluate Azure Container Registry consolidation rule.

    Args:
        subscription_id (str): Tenant subscription ID.
        scan_id (str): Scan ID for inventory lookup.

    Returns:
        list[dict]: Findings if rule conditions are met.
    """
    container_name = "inventories"
    query = "SELECT c.resources FROM c WHERE c.scanId = @scanId AND c.subscriptionId = @subId"
    parameters = [
        {"name": "@scanId", "value": scan_id},
        {"name": "@subId", "value": subscription_id},
    ]

    inventory_items = query_items(container_name, query, parameters, partition_key=subscription_id)

    if not inventory_items:
        return []

    resources = inventory_items[0].get("resources", [])
    acr_count = sum(1 for r in resources if r.get("resourceType") == "Microsoft.ContainerRegistry/registries")

    if acr_count >= 3:
        return [
            {
                "id": f"r08-acr-consolidation-{scan_id}",
                "subscriptionId": subscription_id,
                "scanId": scan_id,
                "category": "container-consolidation",
                "title": "Consider consolidating Azure Container Registries",
                "estimated_saving_low": 100,
                "estimated_saving_high": 500,
                "effort_class": "medium",
                "risk_class": "low",
            }
        ]

    return []