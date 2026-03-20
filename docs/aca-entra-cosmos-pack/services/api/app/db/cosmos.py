from azure.cosmos import CosmosClient
from app.settings import settings

_client = None

def get_cosmos_client() -> CosmosClient:
    global _client
    if _client is None:
        _client = CosmosClient(settings.COSMOS_ENDPOINT, credential=settings.COSMOS_KEY)
    return _client

def get_container(container_name: str):
    client = get_cosmos_client()
    db = client.get_database_client(settings.COSMOS_DB_NAME)
    return db.get_container_client(container_name)
