"""
Pre-flight permission validation.
Probes ARM, Cost Management, Advisor, Policy, Network APIs before collection.
Returns PASS | PASS_WITH_WARNINGS | FAIL with per-probe results.
See 02-preflight.md for full spec.
"""
import os
import requests
from azure.identity import ClientSecretCredential


REQUIRED_PROBES = [
    ("arm",             "https://management.azure.com/subscriptions/{sub}?api-version=2022-12-01",       True),
    ("cost_management", "https://management.azure.com/subscriptions/{sub}/providers/Microsoft.CostManagement/query?api-version=2023-11-01", True),
    ("advisor",         "https://management.azure.com/subscriptions/{sub}/providers/Microsoft.Advisor/recommendations?api-version=2023-01-01", True),
    ("policy",          "https://management.azure.com/subscriptions/{sub}/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults?api-version=2019-10-01", True),
    ("network",         "https://management.azure.com/subscriptions/{sub}/providers/Microsoft.Network/publicIPAddresses?api-version=2023-11-01", False),
]


def run_preflight(subscription_id: str) -> dict:
    cred = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )
    token = cred.get_token("https://management.azure.com/.default").token
    headers = {"Authorization": f"Bearer {token}"}

    results = []
    blockers = []
    warnings = []

    for name, url_template, mandatory in REQUIRED_PROBES:
        url = url_template.replace("{sub}", subscription_id)
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            ok = resp.status_code in (200, 201, 202, 204, 400)  # 400 may be query method issue
            status = "PASS" if ok else "FAIL"
            results.append({"name": name, "status": status, "http": resp.status_code})
            if not ok and mandatory:
                blockers.append(f"Probe '{name}' returned HTTP {resp.status_code}")
            elif not ok:
                warnings.append(f"Probe '{name}' returned HTTP {resp.status_code} (optional)")
        except Exception as e:
            results.append({"name": name, "status": "FAIL", "error": str(e)})
            if mandatory:
                blockers.append(f"Probe '{name}' failed: {e}")
            else:
                warnings.append(f"Probe '{name}' failed (optional): {e}")

    if blockers:
        verdict = "FAIL"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "probes": results,
        "blockers": blockers,
        "warnings": warnings,
    }
