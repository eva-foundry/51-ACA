# EVA-STORY: ACA-03-001
"""
Rule 09: Network Optimization
Analyzes network usage and suggests optimizations to reduce costs.
"""
def rule_09_network_optimization(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("cost-data")
    query = """
    SELECT * FROM c WHERE c.type = 'Network' AND c.bandwidthUsage < @threshold
    """
    parameters = [{"name": "@threshold", "value": 100}]
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)