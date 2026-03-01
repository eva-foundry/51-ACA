# EVA-STORY: ACA-03-001
"""
Rule 11: RBAC Hygiene
Identifies overly permissive roles and suggests tightening access controls.
"""
def rule_11_rbac_hygiene(subscription_id: str, cosmos_client) -> list[dict]:
    container = cosmos_client.get_container("inventories")
    query = """
    SELECT * FROM c WHERE c.type = 'RoleAssignment' AND c.permissions = 'Owner'
    """
    parameters = []
    return container.query_items(query=query, parameters=parameters, partition_key=subscription_id)