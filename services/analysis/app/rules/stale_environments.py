# EVA-STORY: ACA-03-008
from app.db.cosmos import query_items

def detect_stale_environments(subscription_id: str) -> list[dict]:
    """
    Detect stale environments based on the rule:
    - Environments with >= 3 App Services are flagged as stale.

    Args:
        subscription_id (str): Tenant subscription ID for isolation.

    Returns:
        list[dict]: Findings for stale environments.
    """
    query = (
        "SELECT c.environmentId, COUNT(c.resourceId) AS appServiceCount "
        "FROM c WHERE c.subscriptionId = @sub AND c.resourceType = 'AppService' "
        "GROUP BY c.environmentId HAVING COUNT(c.resourceId) >= 3"
    )
    parameters = [{"name": "@sub", "value": subscription_id}]

    findings = query_items(
        container_name="inventories",
        query=query,
        parameters=parameters,
        partition_key=subscription_id,
    )

    return [
        {
            "id": f"stale-env-{finding['environmentId']}",
            "title": "Stale Environment Detected",
            "category": "Optimization",
            "estimated_saving_low": 100,
            "estimated_saving_high": 500,
            "effort_class": "low",
            "risk_class": "low",
            "environmentId": finding["environmentId"],
            "appServiceCount": finding["appServiceCount"],
        }
        for finding in findings
    ]