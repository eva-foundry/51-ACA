# EVA-STORY: ACA-03-005
"""
Compute Scheduling Rule Implementation.
This rule identifies schedulable compute resources with potential savings exceeding $5000.
"""
from app.db.cosmos import query_items

RULE_THRESHOLD = 5000  # Minimum savings threshold for schedulable compute resources


def compute_scheduling_rule(subscription_id: str) -> list[dict]:
    """
    Identify schedulable compute resources with potential savings exceeding the threshold.

    Args:
        subscription_id (str): Tenant subscription ID for Cosmos partition isolation.

    Returns:
        list[dict]: Findings matching the rule criteria.
    """
    query = (
        "SELECT c.id, c.title, c.category, c.estimated_saving_low, "
        "c.estimated_saving_high, c.effort_class, c.risk_class "
        "FROM c WHERE c.schedulable = true AND c.estimated_saving_high > @threshold"
    )
    parameters = [{"name": "@threshold", "value": RULE_THRESHOLD}]

    findings = query_items(
        container_name="findings",
        query=query,
        parameters=parameters,
        partition_key=subscription_id
    )

    return findings