# EVA-STORY: ACA-03-012
from typing import List, Dict

def evaluate_log_retention_costs(log_analytics_data: List[Dict], environment_tag: str = "non-prod") -> List[Dict]:
    """
    Evaluate log retention costs for non-production environments.

    Args:
        log_analytics_data (List[Dict]): List of daily cost data for Log Analytics.
        environment_tag (str): Environment tag to filter (default: "non-prod").

    Returns:
        List[Dict]: Findings if annual cost exceeds $500, otherwise an empty list.
    """
    findings = []

    # Filter data for non-production environments
    filtered_data = [entry for entry in log_analytics_data if entry.get("environment") == environment_tag]

    # Sum daily costs and calculate annualized cost
    annual_cost = sum(entry.get("daily_cost", 0) for entry in filtered_data) * 365

    if annual_cost > 500:
        findings.append({
            "id": "r02-log-retention",
            "title": "Optimize Log Analytics Retention",
            "category": "logging-optimization",
            "estimated_saving_low": 500,
            "estimated_saving_high": annual_cost,
            "effort_class": "medium",
            "risk_class": "low"
        })

    return findings
