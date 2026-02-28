# EVA-STORY: ACA-03-004
"""
Rule 03: Defender mismatch analysis.

This rule identifies cost discrepancies in Azure Defender subscriptions
where the cost exceeds $2000.
"""
from app.db.cosmos import query_items

def analyze_defender_mismatch(subscription_id: str) -> list[dict]:
    """
    Analyze Defender cost mismatches for a given subscription.

    Args:
        subscription_id (str): The subscription ID to analyze.

    Returns:
        list[dict]: Findings where Defender cost exceeds $2000.
    """
    query = (
        "SELECT * FROM c WHERE c.category = 'Defender' AND c.cost > @threshold"
    )
    parameters = [
        {"name": "@threshold", "value": 2000}
    ]

    findings = query_items(
        container_name="findings",
        query=query,
        parameters=parameters,
        partition_key=subscription_id
    )

    return findings