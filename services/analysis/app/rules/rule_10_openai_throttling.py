# EVA-STORY: ACA-03-001
"""
Rule 10: OpenAI Throttling
Detects excessive usage of OpenAI services and suggests throttling configurations.
"""
def rule_10_openai_throttling(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("cost-data")
    query = """
    SELECT * FROM c WHERE c.type = 'OpenAI' AND c.usage > @threshold
    """
    parameters = [{"name": "@threshold", "value": 100000}]
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)