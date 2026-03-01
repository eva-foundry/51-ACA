# EVA-STORY: ACA-03-020
from app.db.cosmos import query_items
from app.services.findings_gate import gate_findings

def analyze_savings_plan_coverage(subscription_id: str, tier: int) -> list[dict]:
    """
    Analyze savings plan coverage for a given subscription.

    Args:
        subscription_id (str): The subscription ID to analyze.
        tier (int): The tier of the client.

    Returns:
        list[dict]: Tier-gated findings.
    """
    container_name = "cost-data"
    query = "SELECT * FROM c WHERE c.subscriptionId = @sub AND c.type = 'savings_plan'"
    parameters = [{"name": "@sub", "value": subscription_id}]

    # Fetch savings plan data scoped to the subscription
    savings_plan_data = query_items(container_name, query, parameters, partition_key=subscription_id)

    findings = []

    for plan in savings_plan_data:
        if plan.get("coverage") < 80:  # Example threshold for insufficient coverage
            findings.append({
                "id": plan["id"],
                "title": "Low Savings Plan Coverage",
                "category": "Savings Plan",
                "estimated_saving_low": plan.get("estimatedSavingLow", 0),
                "estimated_saving_high": plan.get("estimatedSavingHigh", 0),
                "effort_class": "low",
                "risk_class": "low",
                "narrative": plan.get("narrative", "Savings plan coverage is below recommended levels."),
                "heuristic_source": "r10_savings_plan_coverage"
            })

    # Apply tier gating to findings
    return gate_findings(findings, tier)
