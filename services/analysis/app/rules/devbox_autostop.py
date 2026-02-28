# EVA-STORY: ACA-03-002
"""
Rule: Dev Box Autostop
Purpose: Identify Dev Boxes with costs exceeding $1000 and recommend autostop.
"""
from app.db.cosmos import query_items

def evaluate_devbox_autostop(subscription_id: str) -> list[dict]:
    """
    Evaluate Dev Boxes for autostop recommendation based on cost threshold.

    Args:
        subscription_id (str): Tenant subscription ID for isolation.

    Returns:
        list[dict]: Findings for Dev Boxes exceeding $1000 cost.
    """
    query = """
    SELECT c.id, c.title, c.category, c.estimated_saving_low, c.estimated_saving_high, c.effort_class
    FROM c
    WHERE c.type = 'DevBox' AND c.cost > @cost_threshold
    """
    parameters = [{"name": "@cost_threshold", "value": 1000}]

    findings = query_items(
        container_name="findings",
        query=query,
        parameters=parameters,
        partition_key=subscription_id
    )

    return findings