# EVA-STORY: ACA-03-003

from app.db.cosmos import query_items

def log_retention_rule(subscription_id: str) -> list[dict]:
    """
    Rule R-02: Identify logs with retention costs exceeding $500.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.

    Returns:
        list[dict]: Findings where log retention costs exceed $500.
    """
    query = (
        "SELECT c.id, c.title, c.category, c.estimated_saving_low, "
        "c.estimated_saving_high, c.effort_class, c.risk_class "
        "FROM c WHERE c.type = 'log-retention' AND c.cost > @cost"
    )
    parameters = [{"name": "@cost", "value": 500}]

    findings = query_items(
        container_name="findings",
        query=query,
        parameters=parameters,
        partition_key=subscription_id
    )

    return findings
