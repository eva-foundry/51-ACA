# EVA-STORY: ACA-03-014
"""
Analysis Rule: Chargeback Gap

This rule identifies cost items where the chargeback exceeds $5000.
"""
from app.db.cosmos import query_items

def evaluate_chargeback_gap(subscription_id: str) -> list[dict]:
    """
    Evaluate chargeback gaps for a given subscription.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.

    Returns:
        list[dict]: Findings where chargeback exceeds $5000.
    """
    container_name = "cost-data"
    query = """
        SELECT * FROM c
        WHERE c.chargeback > @threshold
    """
    parameters = [{"name": "@threshold", "value": 5000}]

    findings = query_items(container_name, query, parameters, partition_key=subscription_id)
    return findings
