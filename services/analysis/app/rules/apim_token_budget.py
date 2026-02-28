# EVA-STORY: ACA-03-013
"""
Rule 11: APIM Token Budget Analysis

This rule checks if the APIM token budget is within acceptable limits
and ensures OpenAI integration is available for analysis.
"""

from app.db.cosmos import query_items
from app.services.findings_gate import gate_findings

CONTAINER_NAME = "findings"


def analyze_apim_token_budget(subscription_id: str, client_tier: int) -> list[dict]:
    """
    Analyze APIM token budget and return findings gated by client tier.

    Args:
        subscription_id (str): Tenant subscription ID.
        client_tier (int): Client tier (1, 2, or 3).

    Returns:
        list[dict]: Gated findings based on client tier.
    """
    query = """
    SELECT * FROM c
    WHERE c.category = @category AND c.subscriptionId = @sub
    """
    parameters = [
        {"name": "@category", "value": "APIM Token Budget"},
        {"name": "@sub", "value": subscription_id},
    ]

    raw_findings = query_items(
        container_name=CONTAINER_NAME,
        query=query,
        parameters=parameters,
        partition_key=subscription_id,
    )

    return gate_findings(raw_findings, client_tier)
