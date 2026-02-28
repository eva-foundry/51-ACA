# EVA-STORY: ACA-03-015
from app.db.cosmos import query_items, upsert_item
from app.settings import get_settings

def auto_trigger_analysis(subscription_id: str, scan_id: str) -> None:
    """
    Auto-trigger analysis upon collector completion.

    Args:
        subscription_id (str): Tenant subscription ID.
        scan_id (str): ID of the completed scan.

    """
    settings = get_settings()
    container_name = "scans"

    # Fetch the completed scan details
    query = "SELECT * FROM c WHERE c.id = @scan_id"
    parameters = [{"name": "@scan_id", "value": scan_id}]
    scan_details = query_items(container_name, query, parameters, partition_key=subscription_id)

    if not scan_details:
        print(f"[WARN] No scan found with ID: {scan_id} for subscription: {subscription_id}")
        return

    scan = scan_details[0]

    # Prepare analysis trigger document
    analysis_trigger = {
        "id": f"analysis-{scan_id}",
        "subscriptionId": subscription_id,
        "scanId": scan_id,
        "status": "pending",
        "createdAt": scan.get("completedAt"),
        "triggeredAt": settings.CURRENT_TIMESTAMP,
    }

    # Upsert the analysis trigger document
    upsert_item("advisor", analysis_trigger, partition_key=subscription_id)
    print(f"[INFO] Analysis trigger created for scan ID: {scan_id}, subscription: {subscription_id}")
