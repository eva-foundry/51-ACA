# EVA-STORY: ACA-03-003
from app.db.cosmos import upsert_item
from app.models import Finding

def persist_finding(cosmos_client, finding_dict):
    """
    Persist a Finding to the Cosmos DB findings container.

    Args:
        cosmos_client: CosmosClient instance.
        finding_dict: Dictionary containing the finding data.

    Returns:
        dict: The persisted finding document.
    """
    container_name = "findings"
    partition_key = finding_dict["subscriptionId"]

    # Ensure the finding_dict matches the Finding model
    finding = Finding(**finding_dict)

    # Convert the Pydantic model to a dictionary for Cosmos DB
    finding_doc = finding.dict()

    # Upsert the finding document into the Cosmos DB container
    return upsert_item(container_name, finding_doc, partition_key=partition_key)
