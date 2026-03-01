# EVA-STORY: ACA-03-017
from datetime import datetime, timedelta
from app.db.cosmos import query_items
from app.findings import persist_finding

def analyze_search_costs(scan_id: str, subscription_id: str) -> None:
    """
    Analyze cost data for Azure AI Search services and generate findings
    if annualized cost exceeds $2,000.

    Args:
        scan_id (str): The scan ID.
        subscription_id (str): The subscription ID.
    """
    container_name = "cost-data"
    query = (
        "SELECT c.rows FROM c WHERE c.scanId = @scan_id AND c.subscriptionId = @sub_id"
    )
    parameters = [
        {"name": "@scan_id", "value": scan_id},
        {"name": "@sub_id", "value": subscription_id},
    ]

    cost_data = query_items(container_name, query, parameters, partition_key=subscription_id)

    if not cost_data:
        print("[INFO] No cost data found for scan_id:", scan_id)
        return

    rows = cost_data[0].get("rows", [])
    total_cost = 0

    for row in rows:
        service_name = row.get("serviceName", "")
        meter_category = row.get("meterCategory", "")
        cost = row.get("cost", 0)

        if "Azure AI Search" in service_name or "Search" in meter_category:
            total_cost += cost

    # Annualize the cost (assuming 91 days of data)
    annual_cost = total_cost * (365 / 91)

    if annual_cost > 2000:
        finding = {
            "id": f"{scan_id}-search-cost-oversize",
            "subscriptionId": subscription_id,
            "scanId": scan_id,
            "category": "search-optimization",
            "title": "High Azure AI Search Costs",
            "description": (
                f"The annualized cost for Azure AI Search services exceeds $2,000. "
                f"Consider optimizing your usage to reduce costs."
            ),
            "estimated_saving_low": 500,
            "estimated_saving_high": 1500,
            "effort_class": "medium",
            "risk_class": "low",
            "detectedUtc": datetime.utcnow().isoformat(),
        }

        persist_finding(None, finding)
        print("[INFO] Finding persisted for high Azure AI Search costs.")
    else:
        print("[INFO] No findings generated for Azure AI Search costs.")
