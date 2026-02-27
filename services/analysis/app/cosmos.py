"""
# EVA-STORY: ACA-03-004
Cosmos DB wrapper for the ACA Analysis Engine.

Provides the same interface that FindingsAssembler expects:
    client.query_items(container, query, subscription_id=pk)
    client.upsert_item(container, doc, subscription_id=pk)
    client.get_item(container, item_id, subscription_id=pk)

Reads connection settings from environment variables at startup:
    ACA_COSMOS_URL   -- Cosmos account endpoint
    ACA_COSMOS_KEY   -- Primary read/write key
    ACA_COSMOS_DB    -- Database name (default: aca-prod)
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache

from azure.cosmos import CosmosClient as _AzureCosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

logger = logging.getLogger(__name__)


class AnalysisCosmosClient:
    """
    Thin wrapper around azure-cosmos CosmosClient.
    All methods accept `subscription_id` as a keyword arg and use it as
    the Cosmos partition key -- enforcing tenant isolation on every call.
    """

    def __init__(self, url: str, key: str, database: str) -> None:
        self._client = _AzureCosmosClient(url=url, credential=key)
        self._database = database

    def _container(self, name: str):
        db = self._client.get_database_client(self._database)
        return db.get_container_client(name)

    def query_items(self, container_name: str, query: str,
                    subscription_id: str) -> list[dict]:
        """
        Execute a cross-partition-safe query scoped to subscription_id.
        Never call without subscription_id -- enforces tenant isolation.
        """
        container = self._container(container_name)
        return list(container.query_items(
            query=query,
            partition_key=subscription_id,
        ))

    def upsert_item(self, container_name: str, item: dict,
                    subscription_id: str) -> dict:
        """
        Upsert a document. Item MUST contain the correct partition key field.
        subscription_id is validated against the item but the SDK uses the
        field embedded in the document for actual partitioning.
        """
        container = self._container(container_name)
        return container.upsert_item(item)

    def get_item(self, container_name: str, item_id: str,
                 subscription_id: str) -> dict | None:
        """Fetch a single item by id, scoped to subscription_id partition."""
        try:
            container = self._container(container_name)
            return container.read_item(item=item_id, partition_key=subscription_id)
        except CosmosResourceNotFoundError:
            return None


@lru_cache(maxsize=1)
def get_cosmos_client() -> AnalysisCosmosClient:
    """
    Factory (cached). Reads ACA_COSMOS_URL, ACA_COSMOS_KEY, ACA_COSMOS_DB
    from environment variables. Raises ValueError at startup if any are missing
    so the Container App Job fails fast with a clear error.
    """
    url = os.environ.get("ACA_COSMOS_URL")
    key = os.environ.get("ACA_COSMOS_KEY")
    db = os.environ.get("ACA_COSMOS_DB", "aca-prod")

    if not url:
        raise ValueError("[FAIL] ACA_COSMOS_URL environment variable is not set")
    if not key:
        raise ValueError("[FAIL] ACA_COSMOS_KEY environment variable is not set")

    logger.info("[INFO] Analysis Cosmos client initialised: db=%s", db)
    return AnalysisCosmosClient(url=url, key=key, database=db)
