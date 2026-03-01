# EVA-STORY: ACA-03-013
from typing import List, Dict

def evaluate_defender_costs(defender_cost_data: List[Dict] = None, subscription_id: str = None, scan_id: str = None):
    """
    Evaluate Microsoft Defender for Cloud costs and generate findings
    if annual cost exceeds $2,000.

    Args:
        defender_cost_data (List[Dict]): List of daily cost data for Defender.
        subscription_id (str): The subscription ID for tenant isolation.
        scan_id (str): The scan ID for the current analysis.

    Returns:
        list[dict]: List of findings.
    """
    if defender_cost_data is None:
        defender_cost_data = []
    
    results = defender_cost_data

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
