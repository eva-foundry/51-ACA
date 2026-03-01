# EVA-STORY: ACA-03-001
"""
Rule 07: Idle App Services
Detects app services with low traffic and suggests scaling down or stopping.
"""
def rule_07_idle_app_services(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("cost-data")
    query = """
    SELECT * FROM c WHERE c.type = 'AppService' AND c.requestCount < @threshold
    """
    parameters = [{"name": "@threshold", "value": 100}]
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)