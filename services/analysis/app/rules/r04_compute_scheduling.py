# EVA-STORY: ACA-03-014
from services.analysis.app.cosmos import query_items
from services.api.app.services.findings_gate import gate_findings
from services.analysis.app.models import Finding

def evaluate_r04_compute_scheduling(subscription_id: str, client_tier: int):
    """
    Evaluate R-04 rule: Returns finding when annual schedulable compute > $5,000.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.
        client_tier (int): The tier of the client for field gating.

    Returns:
        list[dict]: List of findings after applying tier gating.
    """
    container_name = "cost-data"
    query = (
        "SELECT c.serviceName, SUM(c.annualCost) AS totalAnnualCost "
        "FROM c WHERE c.subscriptionId = @sub AND c.serviceName IN (@vm, @app_service, @container_instances, @dedicated_hosts) "
        "AND NOT ARRAY_CONTAINS(c.tags, 'prod') AND NOT ARRAY_CONTAINS(c.tags, 'critical') "
        "GROUP BY c.serviceName"
    )
    parameters = [
        {"name": "@sub", "value": subscription_id},
        {"name": "@vm", "value": "Virtual Machines"},
        {"name": "@app_service", "value": "App Service"},
        {"name": "@container_instances", "value": "Container Instances"},
        {"name": "@dedicated_hosts", "value": "Dedicated Hosts"}
    ]

    results = query_items(container_name, query, parameters, partition_key=subscription_id)

    total_cost = sum(item["totalAnnualCost"] for item in results)

    if total_cost > 5000:
        finding = {
            "id": f"r04-{subscription_id}",
            "subscriptionId": subscription_id,
            "category": "compute-cost-optimization",
            "title": "Annual schedulable compute cost exceeds $5,000",
            "estimated_saving_low": 500,
            "estimated_saving_high": 1500,
            "effort_class": "medium",
            "risk_class": "low"
        }
        return gate_findings([finding], client_tier)

    return []