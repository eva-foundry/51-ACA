# EVA-STORY: ACA-03-022
from app.db.cosmos import query_items

def identify_chargeback_gap(subscription_id: str, threshold: float = 5000.0) -> list[dict]:
    """
    Identify chargeback cost allocation gaps where the total cost exceeds the threshold.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.
        threshold (float): The cost threshold to identify gaps. Default is $5000.

    Returns:
        list[dict]: List of findings with chargeback gaps.
    """
    query = (
        "SELECT c.id, c.category, c.title, c.estimated_saving_low, "
        "c.estimated_saving_high, c.effort_class, c.risk_class "
        "FROM c WHERE c.subscriptionId = @sub AND c.totalCost > @threshold"
    )

    parameters = [
        {"name": "@sub", "value": subscription_id},
        {"name": "@threshold", "value": threshold},
    ]

    findings = query_items(
        container_name="cost-data",
        query=query,
        parameters=parameters,
        partition_key=subscription_id,
    )

    return findings
