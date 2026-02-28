# EVA-STORY: ACA-03-010
from app.db.cosmos import query_items

def acr_consolidation(subscription_id: str) -> dict:
    """
    Analyze Azure Container Registry (ACR) usage for consolidation opportunities.

    Returns a finding if there are 3 or more registries under the given subscription.
    """
    container_name = "inventories"
    query = "SELECT * FROM c WHERE c.type = @type"
    parameters = [{"name": "@type", "value": "acr"}]

    acr_items = query_items(container_name, query, parameters, partition_key=subscription_id)

    if len(acr_items) >= 3:
        return {
            "id": "acr-consolidation",
            "title": "ACR Consolidation Opportunity",
            "category": "Optimization",
            "estimated_saving_low": 100,
            "estimated_saving_high": 500,
            "effort_class": "medium",
            "risk_class": "low",
            "details": {
                "registry_count": len(acr_items),
                "registries": [item["name"] for item in acr_items],
            },
        }

    return {}