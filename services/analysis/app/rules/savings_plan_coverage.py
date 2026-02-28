# EVA-STORY: ACA-03-012
"""
Savings Plan Coverage Rule Implementation

This rule identifies savings opportunities for compute resources exceeding $20,000
monthly cost without a savings plan.
"""
from app.db.cosmos import query_items

def evaluate_savings_plan_coverage(subscription_id: str) -> list[dict]:
    """
    Evaluate savings plan coverage for compute resources.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.

    Returns:
        list[dict]: Findings for compute resources exceeding $20,000 monthly cost.
    """
    container_name = "cost-data"
    query = (
        "SELECT * FROM c WHERE c.subscriptionId = @sub AND c.resourceType = 'compute' "
        "AND c.monthlyCost > @threshold"
    )
    parameters = [
        {"name": "@sub", "value": subscription_id},
        {"name": "@threshold", "value": 20000},
    ]

    findings = query_items(container_name, query, parameters, partition_key=subscription_id)

    return findings

# Example usage
if __name__ == "__main__":
    subscription_id = "example-subscription-id"
    findings = evaluate_savings_plan_coverage(subscription_id)
    print(f"[INFO] Findings: {findings}")