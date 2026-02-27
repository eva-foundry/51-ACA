"""
tools/observability.py
======================
Operation tracer and structured event logger for ACA.

Uses opencensus-ext-azure (already in requirements.txt) to send traces and
custom events to Application Insights via APPLICATIONINSIGHTS_CONNECTION_STRING.

Adapted from 29-foundry/tools/observability pattern -- stripped of EVA-specific
dependency on opentelemetry SDK; uses opencensus which is already in ACA deps.

Usage:
    from tools.observability import get_tracer, trace_operation, log_event

    tracer = get_tracer()

    with trace_operation(tracer, "collector.run", {"scan_id": scan_id}):
        # work here
        pass

    log_event("scan_started", {"scan_id": scan_id, "subscription_id": sub_id})
"""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

logger = logging.getLogger(__name__)

_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
_SERVICE_NAME = os.getenv("ACA_SERVICE_NAME", "aca-api")
_ENVIRONMENT = os.getenv("ACA_ENVIRONMENT", "local")

# ---------------------------------------------------------------------------
# Tracer factory -- lazy init so services that don't instrument don't crash
# ---------------------------------------------------------------------------

_tracer = None
_telemetry_client = None


def _init_telemetry():
    """Initialize opencensus Azure Monitor exporter. Idempotent."""
    global _tracer, _telemetry_client
    if _tracer is not None:
        return

    if not _CONNECTION_STRING:
        logger.warning(
            "observability: APPLICATIONINSIGHTS_CONNECTION_STRING not set -- "
            "traces will be logged locally only."
        )
        _tracer = _NoopTracer()
        return

    try:
        from opencensus.ext.azure.trace_exporter import AzureExporter
        from opencensus.ext.azure.log_exporter import AzureLogHandler
        from opencensus.trace.samplers import AlwaysOnSampler
        from opencensus.trace.tracer import Tracer

        _tracer = Tracer(
            exporter=AzureExporter(connection_string=_CONNECTION_STRING),
            sampler=AlwaysOnSampler(),
        )

        # Wire AzureLogHandler to root logger for log-based events
        root_logger = logging.getLogger()
        if not any(isinstance(h, AzureLogHandler) for h in root_logger.handlers):
            handler = AzureLogHandler(connection_string=_CONNECTION_STRING)
            handler.setLevel(logging.INFO)
            root_logger.addHandler(handler)

        logger.info(
            "observability: Application Insights connected. service=%s env=%s",
            _SERVICE_NAME,
            _ENVIRONMENT,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("observability: init failed -- noop mode. error=%s", exc)
        _tracer = _NoopTracer()


class _NoopTracer:
    """Silent no-op tracer used when AppInsights is not configured."""

    def span(self, name: str):
        return _NoopSpan()


class _NoopSpan:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def add_attribute(self, key: str, value: Any):
        pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_tracer():
    """Return the initialized tracer (opencensus Tracer or NoopTracer)."""
    _init_telemetry()
    return _tracer


@contextmanager
def trace_operation(
    operation_name: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> Generator[Any, None, None]:
    """
    Context manager that wraps a code block in a named trace span.

    Args:
        operation_name: Span name shown in Application Insights (e.g. "collector.run").
        attributes:     Extra key-value metadata attached to the span.

    Example:
        with trace_operation("analysis.run", {"scan_id": scan_id}):
            run_analysis(scan_id)
    """
    _init_telemetry()
    tracer = _tracer

    with tracer.span(name=operation_name) as span:
        if attributes:
            for k, v in attributes.items():
                try:
                    span.add_attribute(k, str(v))
                except Exception:  # noqa: BLE001
                    pass
        try:
            yield span
        except Exception as exc:
            try:
                span.add_attribute("error", str(exc))
                span.add_attribute("error.type", type(exc).__name__)
            except Exception:  # noqa: BLE001
                pass
            raise


def log_event(
    event_name: str,
    properties: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a named custom event visible in Application Insights customEvents table.

    Args:
        event_name:  Short camelCase or snake_case name (e.g. "scan_started").
        properties:  Dict of string key-value pairs (values are coerced to str).
    """
    props = {k: str(v) for k, v in (properties or {}).items()}
    props["service"] = _SERVICE_NAME
    props["environment"] = _ENVIRONMENT
    # opencensus AzureLogHandler picks up extra= dict as custom dimensions
    logger.info("EVENT:%s", event_name, extra={"custom_dimensions": props})
