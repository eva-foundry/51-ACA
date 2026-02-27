"""
tools/update_data_model.py
==========================
Implements the `update_data_model` tool referenced by all four agent YAMLs:
  collection-agent.yaml, analysis-agent.yaml, generation-agent.yaml, redteam-agent.yaml

Writes partial updates to the `scans` container, keeping subscription_id as
partition key so every write is tenant-isolated.

Usage (agent YAML step):
    - id: mark_complete
      tool: update_data_model
      args:
        scan_id: "{{ inputs.scan_id }}"
        subscription_id: "{{ inputs.subscription_id }}"
        updates:
          status: collected
          collected_utc: "2026-02-26T19:17:00Z"

Python usage:
    from tools.update_data_model import update_scan
    record = update_scan(scan_id, subscription_id, status="analysing")
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from tools.cosmos_client import (
    CosmosResourceNotFoundError,
    get_aca_container,
)

__all__ = ["update_scan", "UpdateResult"]

logger = logging.getLogger(__name__)

# Valid scan status values (enforced to prevent typos cascading through system)
_VALID_STATUSES = frozenset({
    "queued", "collecting", "collected", "analysing", "complete", "failed", "delivered",
})

# Fields callers are NOT allowed to overwrite via this tool
_IMMUTABLE_FIELDS = frozenset({"id", "subscriptionId", "created_utc"})


class UpdateResult:
    """Return type from update_scan / update_finding."""
    __slots__ = ("ok", "scan_id", "row_version", "error")

    def __init__(
        self,
        ok: bool,
        scan_id: str = "",
        row_version: int = 0,
        error: str = "",
    ) -> None:
        self.ok = ok
        self.scan_id = scan_id
        self.row_version = row_version
        self.error = error

    def __repr__(self) -> str:
        return (
            f"UpdateResult(ok={self.ok}, scan_id={self.scan_id!r}, "
            f"row_version={self.row_version}, error={self.error!r})"
        )


def update_scan(
    scan_id: str,
    subscription_id: str,
    **fields: Any,
) -> UpdateResult:
    """
    Partially update a scan record in Cosmos.

    Reads the existing record, applies the field updates, increments row_version,
    sets updated_utc, then upserts back. Raises ValueError on bad status.

    Args:
        scan_id:         The scan UUID.
        subscription_id: Client subscription ID (partition key).
        **fields:        Fields to update, e.g. status="collecting", error=None.

    Returns:
        UpdateResult with ok=True and the new row_version on success.

    Raises:
        ValueError: if `status` value is not in _VALID_STATUSES.
        EnvironmentError: if ACA_COSMOS_URL is not set.
    """
    if "status" in fields and fields["status"] not in _VALID_STATUSES:
        raise ValueError(
            f"Invalid scan status {fields['status']!r}. "
            f"Valid values: {sorted(_VALID_STATUSES)}"
        )

    # Strip any attempt to overwrite immutable fields
    for immutable in _IMMUTABLE_FIELDS:
        if immutable in fields:
            logger.warning(
                "update_scan: field %r is immutable and will be ignored.", immutable
            )
            fields.pop(immutable, None)

    container = get_aca_container("scans")

    try:
        existing = container.read_item(
            item=scan_id,
            partition_key=subscription_id,
        )
    except CosmosResourceNotFoundError:
        return UpdateResult(
            ok=False,
            scan_id=scan_id,
            error=f"Scan {scan_id!r} not found for subscription {subscription_id!r}",
        )

    current_rv = existing.get("row_version", 0)
    existing.update(fields)
    existing["row_version"] = current_rv + 1
    existing["updated_utc"] = datetime.now(timezone.utc).isoformat()

    container.upsert_item(existing)
    logger.info(
        "update_scan: scan_id=%s subscription=%s rv=%d fields=%s",
        scan_id,
        subscription_id,
        existing["row_version"],
        list(fields.keys()),
    )
    return UpdateResult(ok=True, scan_id=scan_id, row_version=existing["row_version"])


def update_finding(
    scan_id: str,
    subscription_id: str,
    finding_id: str,
    **fields: Any,
) -> UpdateResult:
    """
    Partially update a finding record in the `findings` container.

    Same pattern as update_scan -- read, merge, increment rv, upsert.
    """
    container = get_aca_container("findings")

    try:
        existing = container.read_item(
            item=finding_id,
            partition_key=subscription_id,
        )
    except CosmosResourceNotFoundError:
        return UpdateResult(
            ok=False,
            scan_id=scan_id,
            error=f"Finding {finding_id!r} not found.",
        )

    current_rv = existing.get("row_version", 0)
    existing.update(fields)
    existing["row_version"] = current_rv + 1
    existing["updated_utc"] = datetime.now(timezone.utc).isoformat()

    container.upsert_item(existing)
    return UpdateResult(ok=True, scan_id=scan_id, row_version=existing["row_version"])
