# EVA-STORY: ACA-03-011
from app.db.cosmos import query_items

def rule_01_dev_box_autostop(subscription_id: str) -> list[dict]:
    """
    Evaluate Dev Box resources and return a finding if annual cost exceeds $1,000.

    Args:
        subscription_id (str): Tenant subscription ID for isolation.

    Returns:
        list[dict]: List containing one finding if applicable, otherwise empty list.
    """
    # Query inventory for Dev Box resources
    query = (
        "SELECT c.resourceId, c.monthlyCost "
        "FROM c WHERE c.resourceType IN (@devcenters, @devboxes)"
    )
    parameters = [
        {"name": "@devcenters", "value": "Microsoft.DevBox/devcenters"},
        {"name": "@devboxes", "value": "Microsoft.DevBox/devboxes"}
    ]

    inventory_data = query_items(
        container_name="inventories",
        query=query,
        parameters=parameters,
        partition_key=subscription_id
    )

    # Calculate total annual cost
    total_annual_cost = sum(item["monthlyCost"] * 12 for item in inventory_data)

    # Return finding if annual cost exceeds $1,000
    if total_annual_cost > 1000:
        finding = {
            "category": "compute-scheduling",
            "title": "Dev Box instances run nights and weekends",
            "estimated_saving_low": total_annual_cost * 0.3,
            "estimated_saving_high": total_annual_cost * 0.5,
            "effort_class": "trivial",
            "risk_class": "none",
            "narrative": (
                "Auto-stop schedules can reduce costs by stopping Dev Box instances "
                "during nights and weekends when they are not in use."
            ),
            "deliverable_template_id": "tmpl-dev-box-autostop"
        }
        return [finding]

    return []