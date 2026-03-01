# EVA-STORY: ACA-03-001
"""
Rule 03: Reserved Instances
Identifies opportunities to save costs by using reserved instances for virtual machines.
"""
def rule_03_reserved_instances(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("cost-data")
    query = """
    SELECT * FROM c WHERE c.type = 'VM' AND c.billingType = 'PayAsYouGo'
    """
    parameters = []
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)