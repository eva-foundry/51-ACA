# EVA-STORY: ACA-03-021
from app.db.cosmos import query_items

def r11_apim_token_budget(subscription_id: str) -> list[dict]:
    """
    Identify API Management instances with high token budgets.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.

    Returns:
        list[dict]: List of findings for API Management instances with high token budgets.
    """
    container_name = "cost-data"
    query = (
        "SELECT c.id, c.title, c.category, c.estimated_saving_low, "
        "c.estimated_saving_high, c.effort_class, c.subscriptionId "
        "FROM c WHERE c.category = 'API Management' AND c.tokenBudget > @threshold"
    )
    parameters = [{"name": "@threshold", "value": 100000}]

    findings = query_items(container_name, query, parameters, partition_key=subscription_id)
    return findings
