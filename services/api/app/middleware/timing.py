# EVA-STORY: ACA-08-009
"""
services/api/app/middleware/timing.py
=====================================
ASGI request timing middleware.

Emits one structured JSON log line per request:

    {"event": "http_request", "method": "POST", "path": "/v1/collect/start",
     "status_code": 202, "duration_ms": 34, "subscription_id": "sub-xxx",
     "request_id": "uuid", "service": "aca-api", "environment": "local"}

Rules:
- /health is excluded (high-frequency noise).
- subscription_id extracted from X-Subscription-Id header (hashed, not raw).
- All log lines are ASCII-only, JSON-safe.
- duration_ms is wall-clock time in milliseconds (int).

This single middleware replaces the per-router trace_operation calls. It covers
every route automatically without per-endpoint instrumentation.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

_SERVICE = os.getenv("ACA_SERVICE_NAME", "aca-api")
_ENV = os.getenv("ACA_ENVIRONMENT", "local")
_EXCLUDE_PATHS = {"/health", "/docs", "/openapi.json", "/favicon.ico"}


def _hash_sub(sub_id: str) -> str:
    """One-way hash of subscriptionId for logs (privacy-safe)."""
    if not sub_id:
        return ""
    return hashlib.sha256(sub_id.encode()).hexdigest()[:12]


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Emit one structured JSON log line per HTTP request.

    Wired in main.py via:
        app.add_middleware(TimingMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in _EXCLUDE_PATHS:
            return await call_next(request)

        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())[:8]
        sub_id_raw = request.headers.get("X-Subscription-Id", "")

        t0 = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            logger.error(
                json.dumps({
                    "event": "http_error",
                    "method": request.method,
                    "path": request.url.path,
                    "error": type(exc).__name__,
                    "request_id": request_id,
                    "service": _SERVICE,
                    "environment": _ENV,
                }, ensure_ascii=True)
            )
            raise
        finally:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            record = {
                "event": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "subscription_id": _hash_sub(sub_id_raw),
                "request_id": request_id,
                "service": _SERVICE,
                "environment": _ENV,
            }
            if status_code >= 500:
                logger.error(json.dumps(record, ensure_ascii=True))
            elif status_code >= 400:
                logger.warning(json.dumps(record, ensure_ascii=True))
            else:
                logger.info(json.dumps(record, ensure_ascii=True))
