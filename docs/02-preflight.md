# ACA Onboarding and Pre-flight Validation Spec
# EVA-STORY: ACA-12-002

Version: 1.0.0
Updated: 2026-02-27
Status: AUTHORITATIVE -- agents must read this before implementing any auth or collector preflight story.

---

## 1. Overview

Pre-flight is Step 1 of the ACA onboarding flow. Before the collector job runs
against a customer subscription, the system validates that the required Azure RBAC
permissions are present and the necessary APIs are reachable.

Pre-flight produces a structured result that is stored in the scan record and
displayed on the ConnectSubscription page before the user confirms collection.

---

## 2. Authentication Modes

ACA supports three onboarding modes. The mode is chosen at registration time.

| Mode | Credential | Use Case |
|---|---|---|
| A -- Delegated | MSAL PublicClientApplication + refresh token | End-customer (standard) |
| B -- Service Principal | ClientSecretCredential (ACA_CLIENT_ID + secret) | Automated / unattended |
| C -- Managed Identity | DefaultAzureCredential (ManagedIdentity chain) | ACA's own collector job |

For Phase 1, Mode B (Service Principal) is the only implemented mode because ACA-CLIENT-ID
is pending Entra app registration. Mode A implementation is gated on that credential.

### Mode A: Delegated Auth Flow (MSAL)

```
POST /v1/auth/connect
  <- { subscription_id, tenant_id }
  -> { auth_url, state_token }    # redirect client to auth_url
  <- redirect back with code
POST /v1/auth/preflight
  <- { code, state_token }
  -> { preflight_result }         # 5-probe PASS/WARN/FAIL
```

MSAL token acquisition:

```python
# services/collector/app/azure_client.py
import msal, os

def get_arm_token(client_id: str, tenant_id: str, refresh_token: str) -> str:
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )
    result = app.acquire_token_by_refresh_token(
        refresh_token,
        scopes=["https://management.azure.com/.default"],
    )
    if "access_token" not in result:
        raise RuntimeError(f"[FAIL] Token refresh: {result.get('error_description')}")
    return result["access_token"]
```

Refresh token is stored in Cosmos (scans container) encrypted at rest via Key Vault
managed encryption. Never stored in plaintext in any log or error message.

---

## 3. Pre-flight Probes (5 capability checks)

The collector runs 5 RBAC and connectivity probes. Each probe is independent.
Failure of probe 1 or 2 is blocking. Failure of probes 3-5 produces PASS_WITH_WARNINGS.

| Probe | Required Role | API Called | Blocking? |
|---|---|---|---|
| 1 -- ARM read | Reader | ARM /subscriptions/{id} GET | YES |
| 2 -- Cost Management | Cost Management Reader | /providers/Microsoft.CostManagement/query | YES |
| 3 -- Advisor | Reader (inherits) | /providers/Microsoft.Advisor/recommendations | NO (warn) |
| 4 -- Policy | Reader (inherits) | /providers/Microsoft.PolicyInsights/policyStates | NO (warn) |
| 5 -- Network Topology | Network Contributor | /providers/Microsoft.Network/virtualNetworks | NO (warn) |

### Probe Result States

- PASS: role present, API returned HTTP 200
- PASS_WITH_WARNINGS: one or more non-blocking probes failed; collection proceeds
- FAIL: one or more blocking probes failed; collection cannot proceed

### Pre-flight Result Schema

```python
PreflightResult = {
    "overall": "PASS" | "PASS_WITH_WARNINGS" | "FAIL",
    "all_clear": bool,            # True only when overall == "PASS"
    "missing_roles": list[str],   # role names missing, empty on PASS
    "probes": [
        {
            "name": str,          # "arm_read" | "cost_management" | "advisor" | "policy" | "network"
            "status": "PASS" | "FAIL",
            "blocking": bool,
            "detail": str,        # error message or "OK"
        }
    ],
    "collected_at": str,          # ISO 8601
}
```

---

## 4. Pre-flight API Endpoints

### POST /v1/auth/connect

Initiates delegated auth flow. Returns MSAL authorization URL.

Request:
```json
{
  "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

Response 200:
```json
{
  "auth_url": "https://login.microsoftonline.com/...",
  "state_token": "opaque-state-string",
  "expires_in": 300
}
```

Errors:
- 400: subscription_id or tenant_id missing or malformed
- 501: Mode A not yet supported (Phase 1 -- ACA-CLIENT-ID pending)
- 503: MSAL configuration unavailable

### POST /v1/auth/preflight

Exchanges auth code for token, runs 5 probes, returns result.
Also triggers scan record creation in Cosmos.

Request:
```json
{
  "code": "MSAL-auth-code",
  "state_token": "opaque-state-string",
  "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

Response 200:
```json
{
  "scan_id": "scan-uuid",
  "preflight_result": { ...PreflightResult... },
  "next": "POST /v1/collect/start"
}
```

Errors:
- 400: code or state_token missing
- 403: state_token mismatch (CSRF protection)
- 422: preflight FAIL (blocking role missing; details in preflight_result)

### DELETE /v1/auth/disconnect

Revokes stored refresh token and marks scan as disconnected.

Response 204: no content

---

## 5. ConnectSubscription Page Flow

```
1. User lands on /app/connect
2. User enters subscription_id + tenant_id
3. Frontend calls POST /v1/auth/connect -> gets auth_url
4. Frontend redirects user to auth_url (MSAL consent page)
5. MSAL redirects back to /app/preflight-callback?code=...&state=...
6. Frontend calls POST /v1/auth/preflight
7. Frontend shows PreflightResult:
   - PASS: "Ready to collect" -> green CTA -> POST /v1/collect/start
   - PASS_WITH_WARNINGS: amber banner + warning list -> user confirms
   - FAIL: red error + missing_roles list + link to access guide
```

---

## 6. Collector --preflight-only Flag

The collector job accepts a CLI flag for validation-only runs:

```bash
python -m collector --preflight-only --subscription-id <sub_id>
```

Runs all 5 probes, prints structured JSON to stdout, exits 0 (PASS/WARN) or 1 (FAIL).
Does not write to Cosmos. Used in CI RBAC validation workflows.

---

## 7. Phase 1 Limitations

- Mode A (delegated) blocked on ACA-CLIENT-ID Entra app registration
  (Application Developer role requested 2026-02-27)
- Phase 1 uses Mode B only: ClientSecretCredential with ACA service principal
- Refresh token storage in Key Vault: deferred to Mode A implementation
- Network probe (probe 5): VNet peering count missing from get_network_topology()
  (tracked in opus review findings C-08)

---

## 8. Error Messages (user-facing)

All error messages must be plain English with no implementation detail.

| Condition | User-facing message |
|---|---|
| Probe 1 FAIL | "The account does not have read access to this subscription. Please assign the Reader role and retry." |
| Probe 2 FAIL | "Cost Management Reader access is required to generate cost analysis. Please assign the role listed and retry." |
| State token mismatch | "The authentication session expired. Please start again." |
| Mode A not available | "Direct login is not yet available. Please use service principal mode." |

---

*See also: 05-technical.md (API skeleton), PLAN.md Feature 2.1 (pre-flight stories)*
