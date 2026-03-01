# EVA-STORY: ACA-03-001
"""
Rule 08: Oversized Cosmos DB
Identifies Cosmos DB containers with excessive RU/s allocation.
"""
def rule_08_oversized_cosmos(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("cost-data")
    query = """
    SELECT * FROM c WHERE c.type = 'CosmosDB' AND c.ruAllocation > @threshold
    """
    parameters = [{"name": "@threshold", "value": 10000}]
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)