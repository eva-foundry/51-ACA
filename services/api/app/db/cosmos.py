"""
Cosmos DB client -- tenant-isolated helpers.

RULE: every query MUST include partition_key=subscription_id.
No cross-tenant queries are permitted.
"""
from functools import lru_cache

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.settings import get_settings

CONTAINERS = {
    "scans": "/subscriptionId",
    "inventories": "/subscriptionId",
    "cost-data": "/subscriptionId",
    "advisor": "/subscriptionId",
    "findings": "/subscriptionId",
    "clients": "/subscriptionId",
    "deliverables": "/subscriptionId",
    "entitlements": "/subscriptionId",
    "payments": "/subscriptionId",
    "stripe_customer_map": "/stripeCustomerId",
    "admin_audit_events": "/subscriptionId",
}


@lru_cache
def get_cosmos_client() -> CosmosClient:
    s = get_settings()
    return CosmosClient(url=s.ACA_COSMOS_URL, credential=s.ACA_COSMOS_KEY)


def get_container(name: str):
    s = get_settings()
    client = get_cosmos_client()
    db = client.get_database_client(s.ACA_COSMOS_DB)
    return db.get_container_client(name)


def upsert_item(container_name: str, item: dict) -> dict:
    """Upsert a single item. Item MUST contain the partition key field."""
    container = get_container(container_name)
    return container.upsert_item(item)


def get_item(container_name: str, item_id: str, partition_key: str) -> dict | None:
    """Fetch a single item by id and partition key."""
    try:
        container = get_container(container_name)
        return container.read_item(item=item_id, partition_key=partition_key)
    except CosmosResourceNotFoundError:
        return None


def query_items(container_name: str, query: str,
                parameters: list[dict], partition_key: str) -> list[dict]:
    """
    Execute a parameterized query SCOPED to partition_key.
    Never call without partition_key -- enforces tenant isolation.
    """
    container = get_container(container_name)
    return list(container.query_items(
        query=query,
        parameters=parameters,
        partition_key=partition_key,
    ))


def ensure_containers() -> None:
    """Create Cosmos containers if they do not exist (idempotent)."""
    s = get_settings()
    client = get_cosmos_client()
    db = client.get_database_client(s.ACA_COSMOS_DB)
    for name, pk_path in CONTAINERS.items():
        db.create_container_if_not_exists(
            id=name,
            partition_key=PartitionKey(path=pk_path),
        )
        print(f"[INFO] Container ready: {name}")
