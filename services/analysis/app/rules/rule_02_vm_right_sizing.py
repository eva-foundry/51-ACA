# EVA-STORY: ACA-03-001
"""
Rule 02: VM Right Sizing
Analyzes virtual machine usage and recommends resizing based on utilization metrics.
"""
def rule_02_vm_right_sizing(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("cost-data")
    query = """
    SELECT * FROM c WHERE c.type = 'VM' AND c.cpuUtilization < @threshold
    """
    parameters = [{"name": "@threshold", "value": 20}]
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)