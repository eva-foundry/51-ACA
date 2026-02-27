"""
services/api/app/scan_pipeline.py
==================================
6-phase scan state machine for ACA.

States (in order):
    queued -> collecting -> collected -> analysing -> complete -> delivered
    Any state can transition to: failed

Adapted from 29-foundry/server/phase_orchestrator.py pattern.
Uses the app-local Cosmos client (app/db/cosmos.py, pydantic-Settings-backed)
rather than the standalone tools/cosmos_client.py (which is for agent job contexts).

This module is imported by routers/scans.py to:
  1. Create a new scan record (create_scan)
  2. Advance scan state (advance_scan)
  3. Read current state (get_scan)
  4. Trigger the background pipeline fan-out (trigger_pipeline)
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.db.cosmos import get_item, upsert_item, query_items

__all__ = [
    "ScanState",
    "ScanRecord",
    "ScanPipeline",
    "ScanStateError",
]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State definitions
# ---------------------------------------------------------------------------

class ScanState:
    QUEUED = "queued"
    COLLECTING = "collecting"
    COLLECTED = "collected"
    ANALYSING = "analysing"
    COMPLETE = "complete"
    DELIVERED = "delivered"
    FAILED = "failed"

    # Valid forward transitions (any state may also go to FAILED)
    _TRANSITIONS: dict[str, list[str]] = {
        QUEUED:     [COLLECTING, FAILED],
        COLLECTING: [COLLECTED,  FAILED],
        COLLECTED:  [ANALYSING,  FAILED],
        ANALYSING:  [COMPLETE,   FAILED],
        COMPLETE:   [DELIVERED,  FAILED],
        DELIVERED:  [],          # terminal
        FAILED:     [],          # terminal
    }

    @classmethod
    def is_valid_transition(cls, current: str, next_state: str) -> bool:
        allowed = cls._TRANSITIONS.get(current, [])
        return next_state in allowed

    @classmethod
    def is_terminal(cls, state: str) -> bool:
        return state in {cls.DELIVERED, cls.FAILED}


class ScanStateError(Exception):
    """Raised when an invalid state transition is attempted."""


# ---------------------------------------------------------------------------
# Record shape
# ---------------------------------------------------------------------------

class ScanRecord:
    """Thin wrapper around the Cosmos dict for type-safe access."""

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def scan_id(self) -> str:
        return self._data["id"]

    @property
    def subscription_id(self) -> str:
        return self._data["subscriptionId"]

    @property
    def status(self) -> str:
        return self._data.get("status", ScanState.QUEUED)

    @property
    def row_version(self) -> int:
        return self._data.get("row_version", 0)

    @property
    def error(self) -> Optional[str]:
        return self._data.get("error")

    def as_dict(self) -> dict:
        return dict(self._data)

    @classmethod
    def create(cls, subscription_id: str) -> "ScanRecord":
        """Build a new scan record in QUEUED state (not yet persisted)."""
        now = datetime.now(timezone.utc).isoformat()
        return cls({
            "id": str(uuid.uuid4()),
            "subscriptionId": subscription_id,
            "status": ScanState.QUEUED,
            "created_utc": now,
            "updated_utc": now,
            "row_version": 1,
        })


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class ScanPipeline:
    """
    Manages scan lifecycle state transitions in Cosmos.

    Usage:
        pipeline = ScanPipeline()

        # Create and persist a new scan
        record = pipeline.create_scan(subscription_id)

        # Advance state (called by background jobs or polling endpoint)
        pipeline.advance_scan(record.scan_id, record.subscription_id, ScanState.COLLECTING)

        # Read current state
        record = pipeline.get_scan(scan_id, subscription_id)

        # Trigger the background fan-out (non-blocking -- fires and returns)
        pipeline.trigger_pipeline(record.scan_id, record.subscription_id)
    """

    def create_scan(self, subscription_id: str) -> ScanRecord:
        """
        Create a new scan record in QUEUED state and persist to Cosmos.

        Returns:
            ScanRecord with scan_id and status=queued.
        """
        record = ScanRecord.create(subscription_id)
        upsert_item("scans", record.as_dict())
        logger.info(
            "scan_pipeline.create_scan: scan_id=%s subscription=%s",
            record.scan_id, subscription_id,
        )
        return record

    def get_scan(self, scan_id: str, subscription_id: str) -> Optional[ScanRecord]:
        """Read a scan record from Cosmos. Returns None if not found."""
        data = get_item("scans", scan_id, partition_key=subscription_id)
        return ScanRecord(data) if data else None

    def advance_scan(
        self,
        scan_id: str,
        subscription_id: str,
        new_status: str,
        error: Optional[str] = None,
        **extra_fields,
    ) -> ScanRecord:
        """
        Transition a scan to a new state.

        Validates the transition is legal, reads current record, applies update,
        increments row_version, and upserts back to Cosmos.

        Args:
            scan_id:         The scan UUID.
            subscription_id: Client subscription ID (partition key).
            new_status:      Target state (use ScanState constants).
            error:           Required when new_status == ScanState.FAILED.
            **extra_fields:  Additional fields to write (e.g. findings_count=12).

        Raises:
            ScanStateError: if the transition from current state is not allowed.
            LookupError:    if scan_id is not found.
        """
        record = self.get_scan(scan_id, subscription_id)
        if record is None:
            raise LookupError(f"Scan {scan_id!r} not found for subscription {subscription_id!r}")

        if not ScanState.is_valid_transition(record.status, new_status):
            raise ScanStateError(
                f"Cannot transition scan {scan_id!r} from {record.status!r} to {new_status!r}. "
                f"Allowed: {ScanState._TRANSITIONS.get(record.status, [])}"
            )

        now = datetime.now(timezone.utc).isoformat()
        data = record.as_dict()
        data["status"] = new_status
        data["updated_utc"] = now
        data["row_version"] = record.row_version + 1

        if error:
            data["error"] = error
        if extra_fields:
            data.update(extra_fields)

        upsert_item("scans", data)
        logger.info(
            "scan_pipeline.advance_scan: scan_id=%s %s -> %s rv=%d",
            scan_id, record.status, new_status, data["row_version"],
        )
        return ScanRecord(data)

    def list_scans(self, subscription_id: str, limit: int = 10) -> list[ScanRecord]:
        """
        Return the most recent scans for a subscription, ordered by created_utc desc.
        Scoped to partition key (tenant isolation enforced by Cosmos query helper).
        """
        rows = query_items(
            container_name="scans",
            query=(
                "SELECT TOP @limit * FROM c "
                "WHERE c.subscriptionId = @sub "
                "ORDER BY c.created_utc DESC"
            ),
            parameters=[
                {"name": "@limit", "value": limit},
                {"name": "@sub", "value": subscription_id},
            ],
            partition_key=subscription_id,
        )
        return [ScanRecord(r) for r in rows]

    def trigger_pipeline(self, scan_id: str, subscription_id: str) -> None:
        """
        Fire-and-forget: kick off the collector Container App Job.

        The job runs asynchronously. Status is polled via GET /v1/scans/{scan_id}.
        This method does not block -- it returns immediately after triggering.

        Requires:
            AZURE_SUBSCRIPTION_ID, ACA_RESOURCE_GROUP, ACA_ACA_ENVIRONMENT env vars.
            Falls back to dry-run mode (logged only) when not set -- safe for local dev.
        """
        from tools.trigger_aca_job import trigger_aca_job
        from tools.update_data_model import update_scan

        result = trigger_aca_job(
            job_name="aca-51-collector",
            env_args=[
                "--scan-id", scan_id,
                "--subscription-id", subscription_id,
            ],
        )

        if result.ok:
            # Advance to COLLECTING and store the execution ID
            self.advance_scan(
                scan_id,
                subscription_id,
                ScanState.COLLECTING,
                execution_id=result.execution_id,
                dry_run=result.dry_run,
            )
        else:
            self.advance_scan(
                scan_id,
                subscription_id,
                ScanState.FAILED,
                error=f"trigger_aca_job failed: {result.error}",
            )
