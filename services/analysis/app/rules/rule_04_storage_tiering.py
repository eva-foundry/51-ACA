# EVA-STORY: ACA-03-001
"""
Rule 04: Storage Tiering
Suggests moving storage accounts to a lower-cost tier based on usage patterns.
"""
def rule_04_storage_tiering(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("cost-data")
    query = """
    SELECT * FROM c WHERE c.type = 'StorageAccount' AND c.accessTier = 'Hot' AND c.accessFrequency < @threshold
    """
    parameters = [{"name": "@threshold", "value": 10}]
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)