# EVA-STORY: ACA-03-011
"""
Rule R-09: DNS Sprawl Analysis

This rule identifies DNS records with associated costs exceeding $1000.
"""
from app.db.cosmos import query_items

def analyze_dns_sprawl(subscription_id: str) -> list[dict]:
    """
    Analyze DNS sprawl for a given subscription.

    Returns findings where cost exceeds $1000.
    """
    query = """
    SELECT c.id, c.title, c.category, c.estimated_saving_low, c.estimated_saving_high, c.effort_class
    FROM c
    WHERE c.category = @category AND c.estimated_saving_high > @cost_threshold
    """
    parameters = [
        {"name": "@category", "value": "DNS"},
        {"name": "@cost_threshold", "value": 1000},
    ]

    findings = query_items(
        container_name="findings",
        query=query,
        parameters=parameters,
        partition_key=subscription_id,
    )

    return findings
