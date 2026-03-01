# EVA-STORY: ACA-03-001
"""
Rule 05: Unattached Disks
Identifies unattached disks that can be deleted to save costs.
"""
def rule_05_unattached_disks(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("inventories")
    query = """
    SELECT * FROM c WHERE c.type = 'Disk' AND c.attachedTo = null
    """
    parameters = []
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)