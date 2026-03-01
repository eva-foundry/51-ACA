# EVA-STORY: ACA-03-013
from app.db.cosmos import query_items
from app.findings import persist_finding

def evaluate_defender_costs(subscription_id: str, scan_id: str):
    """
    Evaluate Microsoft Defender for Cloud costs and generate findings
    if annual cost exceeds $2,000.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.
        scan_id (str): The scan ID for the current analysis.

    Returns:
        list[dict]: List of findings.
    """
    container_name = "cost-data"
    query = """
        SELECT c.serviceName, SUM(c.annualCost) AS totalAnnualCost
        FROM c
        WHERE c.subscriptionId = @sub AND c.serviceName = @serviceName
        GROUP BY c.serviceName
    """
    parameters = [
        {"name": "@sub", "value": subscription_id},
        {"name": "@serviceName", "value": "Microsoft Defender for Cloud"}
    ]

    results = query_items(container_name, query, parameters, partition_key=subscription_id)

    findings = []
    for result in results:
        total_cost = result.get("totalAnnualCost", 0)
        if total_cost > 2000:
            finding = {
                "id": f"{scan_id}-defender-cost-{result['serviceName']}",
                "subscriptionId": subscription_id,
                "scanId": scan_id,
                "category": "security-cost-optimization",
                "title": "High Microsoft Defender for Cloud Costs",
                "description": f"The annual cost for {result['serviceName']} exceeds $2,000.",
                "estimated_saving_low": 0,
                "estimated_saving_high": total_cost,
                "effort_class": "low",
                "risk_class": "low"
            }
            persist_finding(None, finding)  # Cosmos client is injected in persist_finding
            findings.append(finding)

    return findings
