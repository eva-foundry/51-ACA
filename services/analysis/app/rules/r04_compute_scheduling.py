# EVA-STORY: ACA-03-014
from typing import List, Dict

def evaluate_r04_compute_scheduling(subscription_id: str, client_tier: int, compute_cost_data: List[Dict] = None):
    """
    Evaluate R-04 rule: Returns finding when annual schedulable compute > $5,000.

    Args:
        subscription_id (str): The subscription ID for tenant isolation.
        client_tier (int): The tier of the client for field gating.

    Returns:
        list[dict]: List of findings after applying tier gating.
    """
    if compute_cost_data is None:
        compute_cost_data = []

    total_cost = sum(item.get("totalAnnualCost", 0) for item in compute_cost_data)

    if total_cost > 5000:
        finding = {
            "id": f"r04-{subscription_id}",
            "subscriptionId": subscription_id,
            "category": "compute-cost-optimization",
            "title": "Annual schedulable compute cost exceeds $5,000",
            "estimated_saving_low": 500,
            "estimated_saving_high": 1500,
            "effort_class": "medium",
            "risk_class": "low"
        }
        return [finding]

    return []