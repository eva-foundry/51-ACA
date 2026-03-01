# EVA-STORY: ACA-03-001
"""
Rule 01: Dev Box Autostop
Identifies development boxes that are running without activity and suggests auto-stop configurations.
"""
def rule_01_dev_box_autostop(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("inventories")
    query = """
    SELECT * FROM c WHERE c.type = 'DevBox' AND c.lastActivity < @threshold
    """
    parameters = [{"name": "@threshold", "value": "2026-02-01T00:00:00Z"}]
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)