# EVA-STORY: ACA-12-007
"""
Populate request_schema + response_schema on every endpoint in the data model.
Source: 05-technical.md
Run: python scripts/put-schemas.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data-model"))
import db  # noqa: E402

SCHEMAS = {
    "POST /v1/auth/connect": {
        "request_schema": {
            "subscriptionId": "str",
            "tenantId": "str",
            "mode": "delegated | service_principal",
            "servicePrincipal": {
                "clientId": "str (mode=service_principal only)",
                "clientSecret": "str (stored in KV -- never logged)",
            },
        },
        "response_schema": {
            "subscriptionId": "str",
            "tenantId": "str",
            "status": "connected | disconnected",
            "connectedAt": "ISO8601",
        },
    },
    "POST /v1/auth/preflight": {
        "request_schema": {
            "subscriptionId": "str",
            "features": {
                "enableLogAnalyticsSignals": "bool",
                "enableNetworkSignals": "bool",
                "policyInsightsMandatory": "bool",
            },
        },
        "response_schema": {
            "preflightId": "str",
            "subscriptionId": "str",
            "overallStatus": "pass | fail",
            "checks": [
                {
                    "probe": "str",
                    "status": "pass | fail | skip",
                    "message": "str",
                }
            ],
            "completedAt": "ISO8601",
        },
    },
    "POST /v1/auth/disconnect": {
        "request_schema": {},
        "response_schema": {"status": "disconnected"},
    },
    "POST /v1/collect/start": {
        "request_schema": {
            "subscriptionId": "str",
            "preflightId": "str",
            "windowDays": "int (default 91)",
            "force": "bool (default false)",
        },
        "response_schema": {
            "scanId": "str",
            "statusUrl": "str -- /v1/collect/status?scanId={scanId}",
        },
    },
    "GET /v1/collect/status": {
        "request_schema": {"scanId": "str (query param)"},
        "response_schema": {
            "scanId": "str",
            "subscriptionId": "str",
            "status": "queued | running | succeeded | failed",
            "startedAt": "ISO8601",
            "completedAt": "ISO8601 | null",
            "resourceCount": "int",
            "errorMessage": "str | null",
        },
    },
    "GET /v1/scans/": {
        "request_schema": {"subscriptionId": "str (query param)", "limit": "int (default 20)"},
        "response_schema": {"scans": [{"scanId": "str", "status": "str", "startedAt": "ISO8601"}]},
    },
    "GET /v1/scans/{scan_id}": {
        "request_schema": {},
        "response_schema": {
            "scanId": "str",
            "subscriptionId": "str",
            "preflightId": "str",
            "status": "queued | running | succeeded | failed",
            "windowDays": "int",
            "startedAt": "ISO8601",
            "completedAt": "ISO8601 | null",
            "resourceCount": "int",
        },
    },
    "POST /v1/scans/": {
        "request_schema": {
            "subscriptionId": "str",
            "preflightId": "str",
            "windowDays": "int (default 91)",
            "force": "bool (default false)",
        },
        "response_schema": {
            "scanId": "str",
            "statusUrl": "str",
        },
    },
    "GET /v1/findings/{scan_id}": {
        "request_schema": {"tier": "1 | 2 | 3 (query param, default 1)"},
        "response_schema": {
            "tier": "int",
            "findings": [
                {
                    "id": "str",
                    "category": "str",
                    "title": "str",
                    "estimated_saving_low": "int (CAD/yr)",
                    "estimated_saving_high": "int (CAD/yr)",
                    "effort_class": "trivial | easy | medium | involved | strategic",
                    "risk_class": "none | low | medium | high",
                    "narrative": "str (tier2+ only)",
                    "deliverable_template_id": "str (tier3 only)",
                },
            ],
        },
    },
    "GET /v1/reports/tier1": {
        "request_schema": {"scan_id": "str (query param)"},
        "response_schema": {
            "tier": 1,
            "scanId": "str",
            "subscriptionId": "str",
            "generatedAt": "ISO8601",
            "findingCount": "int",
            "totalSavingLow": "int (CAD/yr)",
            "totalSavingHigh": "int (CAD/yr)",
            "findings": [
                {
                    "id": "str",
                    "title": "str",
                    "category": "str",
                    "estimated_saving_low": "int",
                    "estimated_saving_high": "int",
                    "effort_class": "str",
                    "risk_class": "str",
                },
            ],
        },
    },
    "GET /v1/checkout/entitlements": {
        "request_schema": {"subscriptionId": "str (query param)"},
        "response_schema": {
            "subscriptionId": "str",
            "tier": "tier1 | tier2 | tier3",
            "features": ["str"],
            "validUntil": "ISO8601 | null",
        },
    },
    "GET /v1/entitlements": {
        "request_schema": {"subscriptionId": "str (query param or X-Subscription-Id header)"},
        "response_schema": {
            "subscriptionId": "str",
            "tier": "tier1 | tier2 | tier3",
            "features": ["str"],
            "validUntil": "ISO8601 | null",
        },
    },
    "POST /v1/checkout/tier2": {
        "request_schema": {"subscriptionId": "str", "analysisId": "str"},
        "response_schema": {
            "checkoutSessionId": "str",
            "redirectUrl": "str -- https://checkout.stripe.com/...",
        },
    },
    "POST /v1/checkout/tier3": {
        "request_schema": {"subscriptionId": "str", "analysisId": "str"},
        "response_schema": {
            "checkoutSessionId": "str",
            "redirectUrl": "str -- https://checkout.stripe.com/...",
        },
    },
    "POST /v1/checkout/webhook": {
        "request_schema": {"_raw_body": "bytes -- Stripe event JSON (signature validated via Stripe-Signature header)"},
        "response_schema": {"received": "bool"},
    },
    "POST /v1/billing/checkout": {
        "request_schema": {
            "subscriptionId": "str",
            "analysisId": "str",
            "tier": "tier2 | tier3",
        },
        "response_schema": {
            "checkoutSessionId": "str",
            "redirectUrl": "str -- https://checkout.stripe.com/...",
        },
    },
    "GET /v1/billing/portal": {
        "request_schema": {"subscriptionId": "str (query param)"},
        "response_schema": {"portalUrl": "str -- Stripe customer portal URL"},
    },
    "POST /v1/webhooks/stripe": {
        "request_schema": {"_raw_body": "bytes -- Stripe event JSON (Stripe-Signature header required)"},
        "response_schema": {"received": "bool"},
    },
    "GET /v1/admin/kpis": {
        "request_schema": {},
        "response_schema": {
            "totalCustomers": "int",
            "activeScans": "int",
            "tier1Customers": "int",
            "tier2Customers": "int",
            "tier3Customers": "int",
            "totalSavingsIdentifiedCAD": "int",
            "mrr": "float (CAD)",
        },
    },
    "GET /v1/admin/customers": {
        "request_schema": {"query": "str (optional search term)", "limit": "int (default 50)"},
        "response_schema": {
            "customers": [
                {
                    "subscriptionId": "str",
                    "tenantId": "str",
                    "tier": "tier1 | tier2 | tier3",
                    "connectedAt": "ISO8601",
                    "lastScanAt": "ISO8601 | null",
                },
            ]
        },
    },
    "GET /v1/admin/runs": {
        "request_schema": {"type": "scan | analysis | delivery (optional)", "limit": "int (default 50)"},
        "response_schema": {
            "runs": [
                {
                    "runId": "str",
                    "type": "scan | analysis | delivery",
                    "subscriptionId": "str",
                    "status": "queued | running | succeeded | failed",
                    "startedAt": "ISO8601",
                    "completedAt": "ISO8601 | null",
                },
            ]
        },
    },
    "GET /v1/admin/stats": {
        "request_schema": {},
        "response_schema": {
            "totalScans": "int",
            "totalFindings": "int",
            "totalSavingsCAD": "int",
            "scansByStatus": {"queued": "int", "running": "int", "succeeded": "int", "failed": "int"},
        },
    },
    "POST /v1/admin/entitlements/grant": {
        "request_schema": {"subscriptionId": "str", "tier": "tier2 | tier3", "reason": "str"},
        "response_schema": {
            "subscriptionId": "str",
            "tier": "str",
            "grantedAt": "ISO8601",
            "grantedBy": "str (actor)",
        },
    },
    "POST /v1/admin/stripe/reconcile": {
        "request_schema": {},
        "response_schema": {"reconciled": "int", "mismatches": "int", "errors": ["str"]},
    },
    "POST /v1/admin/subscriptions/{subscriptionId}/lock": {
        "request_schema": {"reason": "str"},
        "response_schema": {"subscriptionId": "str", "locked": True, "lockedAt": "ISO8601"},
    },
    "DELETE /v1/admin/scans/{scan_id}": {
        "request_schema": {},
        "response_schema": {"deleted": "bool", "scanId": "str"},
    },
    "GET /health": {
        "request_schema": {},
        "response_schema": {"status": "ok", "version": "str", "store": "sqlite | cosmos"},
    },
}

AUDIT_COLS = {
    "layer", "modified_by", "modified_at", "created_by", "created_at",
    "row_version", "source_file",
}


def main():
    eps = db.list_layer("endpoints")
    ep_map = {e["id"]: e for e in eps}

    updated = 0
    skipped = 0
    missing = []

    for ep_id, schemas in SCHEMAS.items():
        if ep_id not in ep_map:
            missing.append(ep_id)
            continue
        obj = {k: v for k, v in ep_map[ep_id].items() if k not in AUDIT_COLS}
        obj["request_schema"] = schemas["request_schema"]
        obj["response_schema"] = schemas["response_schema"]
        try:
            db.upsert_object("endpoints", obj, actor="agent:copilot")
            print(f"[PASS] {ep_id}")
            updated += 1
        except Exception as exc:
            print(f"[FAIL] {ep_id} -- {exc}")
            skipped += 1

    print(f"\n[INFO] updated={updated} skipped={skipped} missing={len(missing)}")
    if missing:
        for m in missing:
            print(f"  [WARN] not in model: {m}")


if __name__ == "__main__":
    main()
