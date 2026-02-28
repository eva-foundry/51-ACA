# EVA-STORY: ACA-03-009
"""
Analysis Rule: Search SKU Oversize
Purpose: Identify findings where the cost exceeds $2000.
"""
from app.db.cosmos import query_items

def search_sku_oversize(subscription_id: str) -> list[dict]:
    """
    Fetch findings where the cost exceeds $2000 for the given subscription.

    Args:
        subscription_id (str): Tenant subscription ID.

    Returns:
        list[dict]: Findings exceeding $2000.
    """
    query = """
    SELECT * FROM c
    WHERE c.cost > @cost_threshold
    """
    parameters = [{"name": "@cost_threshold", "value": 2000}]

    findings = query_items(
        container_name="findings",
        query=query,
        parameters=parameters,
        partition_key=subscription_id
    )

    return findings