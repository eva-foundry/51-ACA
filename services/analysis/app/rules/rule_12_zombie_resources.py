# EVA-STORY: ACA-03-001
"""
Rule 12: Zombie Resources
Finds resources that are no longer in use but still incurring costs.
"""
def rule_12_zombie_resources(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("inventories")
    query = """
    SELECT * FROM c WHERE c.type IN ('VM', 'Disk', 'Snapshot') AND c.lastActivity IS NULL
    """
    parameters = []
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)