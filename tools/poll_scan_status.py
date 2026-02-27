"""
tools/poll_scan_status.py
=========================
Implements the `poll_scan_status` tool used by:
  collection-agent.yaml  (target_status: collected, timeout_minutes: 30)
  analysis-agent.yaml    (target_status: complete,  timeout_minutes: 20)

Also used to implement `poll_deliverable_status` (generation-agent).

Polls the `scans` container in Cosmos every `interval_seconds` until the
scan record reaches `target_status` or the timeout elapses.

The polling is synchronous (blocking) -- suitable for Container App Job
workers. For async contexts (FastAPI), use the async variant in
services/api/app/scan_pipeline.py.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from tools.cosmos_client import CosmosResourceNotFoundError, get_aca_container

__all__ = ["poll_scan_status", "poll_deliverable_status", "PollResult"]

logger = logging.getLogger(__name__)

_TERMINAL_STATUSES = frozenset({"complete", "failed", "delivered"})


@dataclass
class PollResult:
    ok: bool
    scan_id: str
    final_status: str
    elapsed_seconds: float
    timed_out: bool = False
    error: str = ""


def poll_scan_status(
    scan_id: str,
    subscription_id: str,
    target_status: str,
    timeout_minutes: int = 30,
    interval_seconds: int = 15,
) -> PollResult:
    """
    Block until the scan reaches `target_status` or a terminal error state.

    Args:
        scan_id:          The scan UUID.
        subscription_id:  Client subscription ID (partition key).
        target_status:    Status to wait for, e.g. "collected" or "complete".
        timeout_minutes:  Maximum wall-clock time to wait.
        interval_seconds: How often to poll Cosmos.

    Returns:
        PollResult. ok=True only if final_status == target_status.
    """
    deadline = time.monotonic() + timeout_minutes * 60
    container = get_aca_container("scans")

    while time.monotonic() < deadline:
        try:
            record = container.read_item(
                item=scan_id,
                partition_key=subscription_id,
            )
        except CosmosResourceNotFoundError:
            logger.warning("poll_scan_status: scan %s not found yet -- retrying", scan_id)
            time.sleep(interval_seconds)
            continue

        status = record.get("status", "")
        logger.info("poll_scan_status: scan=%s status=%s target=%s", scan_id, status, target_status)

        if status == target_status:
            return PollResult(
                ok=True,
                scan_id=scan_id,
                final_status=status,
                elapsed_seconds=round(time.monotonic() - (deadline - timeout_minutes * 60), 1),
            )

        if status == "failed":
            return PollResult(
                ok=False,
                scan_id=scan_id,
                final_status=status,
                elapsed_seconds=0,
                error=record.get("error", "scan failed"),
            )

        if status in _TERMINAL_STATUSES and status != target_status:
            # Reached a terminal state that is not what we wanted
            return PollResult(
                ok=False,
                scan_id=scan_id,
                final_status=status,
                elapsed_seconds=0,
                error=f"Scan reached terminal status {status!r} before {target_status!r}",
            )

        time.sleep(interval_seconds)

    # Timeout
    return PollResult(
        ok=False,
        scan_id=scan_id,
        final_status="timeout",
        elapsed_seconds=timeout_minutes * 60,
        timed_out=True,
        error=f"Timed out after {timeout_minutes}m waiting for {target_status!r}",
    )


def poll_deliverable_status(
    scan_id: str,
    subscription_id: str,
    timeout_minutes: int = 15,
    interval_seconds: int = 10,
) -> PollResult:
    """
    Convenience wrapper: poll until status == 'delivered' or failure.
    Used by generation-agent.yaml.
    """
    return poll_scan_status(
        scan_id=scan_id,
        subscription_id=subscription_id,
        target_status="delivered",
        timeout_minutes=timeout_minutes,
        interval_seconds=interval_seconds,
    )
