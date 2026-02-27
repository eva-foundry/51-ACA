"""
# EVA-STORY: ACA-01-001
tools/cosmos_client.py
======================
Standalone Cosmos DB auth helper for ACA agent tools.

Credential priority:
  1. ACA_COSMOS_KEY env var (account key) -- local dev + Phase 1 sandbox.
  2. DefaultAzureCredential (Managed Identity) -- Phase 2 production ACA subscription.

Separate from services/api/app/db/cosmos.py which is bound to pydantic Settings.
This module is used by tool implementations in tools/ that run in agent context.

Usage:
    from tools.cosmos_client import get_aca_container

    container = get_aca_container("scans")
    container.upsert_item(record)
"""
import os
from functools import lru_cache
from typing import Optional

from azure.cosmos import CosmosClient, exceptions as cosmos_exc
from azure.identity import DefaultAzureCredential

__all__ = [
    "get_aca_client",
    "get_aca_container",
    "ACA_COSMOS_URL",
    "ACA_COSMOS_DB",
    "CosmosResourceNotFoundError",
]

# Resolved at import -- surfaces missing-var errors early
ACA_COSMOS_URL: str = os.getenv("ACA_COSMOS_URL", "")
ACA_COSMOS_DB: str = os.getenv("ACA_COSMOS_DB", "aca-db")

CosmosResourceNotFoundError = cosmos_exc.CosmosResourceNotFoundError


def _get_credential(key: Optional[str] = None):
    """Return account key string or DefaultAzureCredential."""
    resolved = key or os.getenv("ACA_COSMOS_KEY", "")
    return resolved if resolved else DefaultAzureCredential()


@lru_cache(maxsize=1)
def get_aca_client() -> CosmosClient:
    """
    Return a cached synchronous CosmosClient.

    lru_cache makes this a singleton per process -- safe for Container App Jobs
    (each job is a fresh process) and for long-running API workers alike.
    """
    if not ACA_COSMOS_URL:
        raise EnvironmentError(
            "ACA_COSMOS_URL is not set. "
            "Add it to .env or set it as an environment variable."
        )
    return CosmosClient(url=ACA_COSMOS_URL, credential=_get_credential())


def get_aca_container(container_name: str):
    """
    Return a ContainerClient for the named container in ACA_COSMOS_DB.

    Args:
        container_name: One of: scans | inventories | cost-data | advisor |
                        findings | clients | deliverables

    Returns:
        azure.cosmos.ContainerProxy
    """
    client = get_aca_client()
    db = client.get_database_client(ACA_COSMOS_DB)
    return db.get_container_client(container_name)
