"""Cosmos helper for delivery service -- thin wrapper around azure-cosmos SDK."""
from __future__ import annotations
from azure.cosmos import CosmosClient, PartitionKey


class CosmosHelper:
    def __init__(self, url: str, key: str, database: str) -> None:
        self._client = CosmosClient(url, credential=key)
        self._db = self._client.get_database_client(database)

    def _container(self, name: str):
        return self._db.get_container_client(name)

    def query_items(self, container: str, query: str, subscription_id: str):
        return self._container(container).query_items(
            query=query,
            partition_key=subscription_id,
        )

    def upsert_item(self, container: str, item: dict, subscription_id: str) -> None:
        self._container(container).upsert_item(
            item,
            partition_key=subscription_id,
        )

    def get_item(self, container: str, item_id: str, subscription_id: str) -> dict:
        return self._container(container).read_item(
            item=item_id,
            partition_key=subscription_id,
        )
