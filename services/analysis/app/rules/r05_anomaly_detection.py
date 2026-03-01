# EVA-STORY: ACA-03-015
import numpy as np

def calculate_z_scores(cost_data):
    """
    Calculate z-scores for cost data grouped by category.

    Args:
        cost_data (list[dict]): List of cost data dictionaries with 'category' and 'cost'.

    Returns:
        dict: Dictionary with categories as keys and z-scores as values.
    """
    categories = {}
    for item in cost_data:
        category = item['category']
        cost = item['cost']
        if category not in categories:
            categories[category] = []
        categories[category].append(cost)

    z_scores = {}
    for category, costs in categories.items():
        mean = np.mean(costs)
        std_dev = np.std(costs)
        if std_dev > 0:
            z_scores[category] = [(cost - mean) / std_dev for cost in costs]
        else:
            z_scores[category] = [0 for cost in costs]

    return z_scores

def detect_anomalies(subscription_id, scan_id):
    """
    Detect anomalies in cost data based on z-scores.

    Args:
        subscription_id (str): Subscription ID for tenant isolation.
        scan_id (str): Scan ID for identifying the data.

    Returns:
        list[dict]: List of findings for categories with z-score >= 3.0.
    """
    container_name = "cost-data"
    query = "SELECT * FROM c WHERE c.scanId = @scanId"
    parameters = [{"name": "@scanId", "value": scan_id}]

    cost_data = query_items(container_name, query, parameters, partition_key=subscription_id)

    z_scores = calculate_z_scores(cost_data)

    findings = []
    for category, scores in z_scores.items():
        if any(score >= 3.0 for score in scores):
            finding = {
                "subscriptionId": subscription_id,
                "scanId": scan_id,
                "category": category,
                "title": f"Anomaly detected in {category} costs",
                "estimated_saving_low": 0,
                "estimated_saving_high": 0,
                "effort_class": "low",
                "risk_class": "high"
            }
            findings.append(finding)
            persist_finding(cosmos_client=None, finding_dict=finding)  # cosmos_client is injected in real usage

    return findings
