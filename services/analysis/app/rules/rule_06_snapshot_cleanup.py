# EVA-STORY: ACA-03-001
"""
Rule 06: Snapshot Cleanup
Finds old snapshots that can be deleted to reduce storage costs.
"""
def rule_06_snapshot_cleanup(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("inventories")
    query = """
    SELECT * FROM c WHERE c.type = 'Snapshot' AND c.creationDate < @threshold
    """
    parameters = [{"name": "@threshold", "value": "2025-12-31T00:00:00Z"}]
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)