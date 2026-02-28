# ACA -- Security Architecture

Version: 1.0.0
Updated: 2026-02-28
Status: Active
Audience: Security Engineers, Compliance Officers, Architects

---

## PURPOSE

This document defines the security architecture for Azure Cost Advisor (ACA), covering
threat modeling, security zones, identity and access management, data protection,
compliance controls, and incident response procedures.

Read this document when: conducting security reviews, responding to incidents, preparing
for audits (SOC 2, ISO 27001), or implementing new security controls.

---

## SECURITY PRINCIPLES

### 1. Least Privilege by Default
ACA requires ONLY Reader role on customer subscriptions. No write permissions. API services
use managed identities with minimal RBAC grants. Cosmos queries scoped to partition key only.

### 2. Zero Trust Model
No implicit trust. Every request authenticated (MSAL token validation). Every Cosmos query
partition-filtered. No cross-tenant data access possible at code or database level.

### 3. Defense in Depth
Multiple security layers: Entra auth + APIM gateway + API middleware + Cosmos RBAC + 
Network Security Groups (Phase 2). Compromise of one layer does not expose tenant data.

### 4. Fail Secure
Authentication failure -> 401 response (no fallback). Partition key missing -> 403 (no query). 
Stripe webhook signature invalid -> 400 (payment not processed). Redteam agent flags risk -> 
IaC template rejected (no delivery).

### 5. Audit Everything
All API requests logged (Application Insights). All Cosmos writes include audit columns
(created_by, modified_by). All Key Vault access logged (diagnostics). All payment events
logged (Stripe webhook payload + signature).

### 6. Data Minimization
NO customer workload data collected (only Azure resource metadata). NO PII in Cosmos
(only subscriptionId, email for billing stored in Stripe, not ACA database).

---

## THREAT MODEL

### Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│  INTERNET (Trust Boundary 0)                                    │
│                                                                 │
│  ┌──────────────┐          ┌──────────────┐                    │
│  │  Malicious   │          │  Legitimate  │                    │
│  │  Actor       │          │  Customer    │                    │
│  └──────┬───────┘          └──────┬───────┘                    │
│         │                         │                            │
└─────────┼─────────────────────────┼────────────────────────────┘
          │                         │
          └────────┬────────────────┘
                   │ HTTPS (TLS 1.2+)
                   v
┌─────────────────────────────────────────────────────────────────┐
│  GATEWAY LAYER (Trust Boundary 1)                              │
│                                                                 │
│  ┌───────────────────────────────────────────────┐             │
│  │  Azure Front Door (Phase 2) or APIM (Phase 1)│             │
│  │  - Rate limiting (10 req/sec per sub)         │             │
│  │  - WAF (OWASP Top 10)                        │             │
│  │  - TLS termination                           │             │
│  │  - DDoS protection                           │             │
│  └─────────────────────┬─────────────────────────┘             │
└───────────────────────┼─────────────────────────────────────────┘
                        │ Authenticated (Bearer token)
                        v
┌─────────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER (Trust Boundary 2)                          │
│                                                                 │
│  ┌───────────────────────────────────────────────┐             │
│  │  ACA API (FastAPI)                           │             │
│  │  - MSAL token validation (Entra OIDC)        │             │
│  │  - Tenant middleware (subscriptionId extract)│             │
│  │  - Tier gate middleware (feature flags)      │             │
│  │  - Structured logging (every request)        │             │
│  └─────────────────────┬─────────────────────────┘             │
└───────────────────────┼─────────────────────────────────────────┘
                        │ Authorized (partition key injected)
                        v
┌─────────────────────────────────────────────────────────────────┐
│  DATA LAYER (Trust Boundary 3)                                 │
│                                                                 │
│  ┌───────────────────────────────────────────────┐             │
│  │  Cosmos DB                                   │             │
│  │  - Partition key filter (mandatory)          │             │
│  │  - RBAC (managed identity only)              │             │
│  │  - Encryption at rest (default)              │             │
│  │  - Audit logs (create/modify/delete)         │             │
│  └───────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Attack Scenarios and Mitigations

#### AS-01: Cross-Tenant Data Leakage

**Threat:** Attacker with valid credentials for Subscription A attempts to access 
Subscription B's findings.

**Attack vector:**
1. Attacker authenticates as legitimate user (Subscription A)
2. Modifies API request: `GET /v1/findings?subscriptionId=B`
3. Attempts to retrieve Subscription B's data

**Mitigation:**
- Tenant middleware extracts subscriptionId from JWT claims, NOT from query params
- Cosmos query uses partition_key=subscription_id (cannot be overridden)
- API validates JWT subscription claim matches requested subscription
- Authorization failure -> 403 Forbidden

**Verification:**
```python
# Unit test: test_cross_tenant_blocked()
def test_cross_tenant_blocked(client, auth_token_sub_a):
    response = client.get(
        "/v1/findings?subscriptionId=sub-b",
        headers={"Authorization": f"Bearer {auth_token_sub_a}"}
    )
    assert response.status_code == 403
    assert "Unauthorized subscription access" in response.json()["detail"]
```

**Risk rating:** CRITICAL -> Mitigated to LOW (code-enforced partition isolation)

---

#### AS-02: Authentication Bypass

**Threat:** Attacker bypasses Entra OIDC authentication to access API without valid token.

**Attack vector:**
1. Attacker sends `GET /v1/findings` without Authorization header
2. Attempts to access protected endpoint

**Mitigation:**
- FastAPI `Depends(get_current_user)` on ALL protected routes
- MSAL token validation: signature, expiration, issuer, audience
- No fallback to API key or cookie-based auth
- Invalid token -> 401 Unauthorized

**Verification:**
```python
# Unit test: test_no_auth_header_blocked()
def test_no_auth_header_blocked(client):
    response = client.get("/v1/findings")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
```

**Risk rating:** CRITICAL -> Mitigated to LOW (MSAL enforced on all routes)

---

#### AS-03: API Abuse (DDoS / Rate Limit Exhaustion)

**Threat:** Attacker floods API with valid requests to exhaust resources or inflate costs.

**Attack vector:**
1. Attacker authenticates with valid credentials
2. Sends 10,000 requests/second to `/v1/scans` (trigger collection jobs)
3. Exhausts Container App CPU quota or Cosmos RU/s

**Mitigation:**
- APIM rate limit: 10 requests/second per subscription (sliding window)
- Container Apps autoscale: max 50 replicas (cost cap)
- Cosmos provisioned throughput: 400 RU/s Phase 1, 4,000 autoscale Phase 2
- Service Bus job queue: max 50 concurrent jobs (Phase 2)
- Rate limit exceeded -> 429 Too Many Requests (Retry-After header)

**Verification:**
```bash
# Load test: 100 concurrent requests (expect 90% to be 429)
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" https://aca-api.../v1/scans
# Expected: 10 successful (200), 90 rate-limited (429)
```

**Risk rating:** HIGH -> Mitigated to MEDIUM (rate limiting + cost caps)

---

#### AS-04: Payment Fraud (Stripe Webhook Spoofing)

**Threat:** Attacker sends fake Stripe webhook to unlock Tier 2/3 without payment.

**Attack vector:**
1. Attacker crafts fake POST /v1/webhooks/stripe with payload:
   ```json
   {"event": "checkout.session.completed", "subscription_id": "attacker-sub"}
   ```
2. Attempts to unlock Tier 3 entitlements

**Mitigation:**
- Stripe webhook signature validation (HMAC-SHA256)
- Signature header: `Stripe-Signature`
- Invalid signature -> 400 Bad Request (no entitlement change)
- Webhook secret stored in Key Vault (STRIPE-WEBHOOK-SECRET)

**Verification:**
```python
# Unit test: test_invalid_stripe_signature_blocked()
def test_invalid_stripe_signature_blocked(client):
    payload = '{"event":"checkout.session.completed"}'
    fake_signature = "t=123456,v1=fakesig"
    response = client.post(
        "/v1/webhooks/stripe",
        data=payload,
        headers={"Stripe-Signature": fake_signature}
    )
    assert response.status_code == 400
    assert "Invalid signature" in response.json()["detail"]
```

**Risk rating:** CRITICAL -> Mitigated to LOW (signature validation enforced)

---

#### AS-05: Malicious IaC Templates (Tier 3)

**Threat:** Attacker receives Tier 3 deliverable, modifies Bicep template to inject 
malicious resource (e.g. cryptominer VM), blames ACA for the template.

**Attack vector:**
1. Attacker upgrades to Tier 3, downloads IaC templates
2. Modifies rule-01-dev-box-autostop.bicep to add hidden VM deployment
3. Executes template, incurs Azure costs
4. Files complaint: "ACA template deployed unauthorized resources"

**Mitigation:**
- **Redteam agent validation**: All templates pre-validated before delivery
  - Check: no resource types beyond whitelist
  - Check: no external URLs in template (no remote module injection)
  - Check: no secrets in template (no hardcoded connection strings)
- **SHA-256 manifest**: manifest.json contains checksums for every file
  - Customer can verify: `sha256sum -c manifest.json`
  - Modified file detected immediately
- **README disclaimer**: "Verify checksums before deployment. ACA not liable for 
  modified templates."

**Verification:**
```python
# Redteam agent test: test_template_whitelist_enforcement()
def test_template_whitelist_enforcement():
    malicious_template = """
    resource vm 'Microsoft.Compute/virtualMachines@2023-03-01' = {
      name: 'cryptominer'
      location: 'westus'
    }
    """
    result = redteam_agent.validate(malicious_template)
    assert result["status"] == "FAIL"
    assert "Unauthorized resource type" in result["checks"][0]["note"]
```

**Risk rating:** HIGH -> Mitigated to LOW (redteam validation + SHA-256 manifest)

---

#### AS-06: Insider Threat (ACA Admin Access)

**Threat:** ACA operator with admin access to Cosmos DB extracts all tenant data.

**Attack vector:**
1. Operator has `Cosmos DB Data Contributor` role (required for admin operations)
2. Runs query: `SELECT * FROM c` (no partition key filter)
3. Exports all findings across all tenants

**Mitigation:**
- **Separation of duties**: Admin operations (tenant lock/unlock) via API endpoint with 
  bearer token, not direct Cosmos access
- **Audit logging**: All Cosmos queries logged (Azure diagnostics)
- **RBAC minimization**: Operators have `Cosmos DB Data Reader` only (Phase 2)
- **Customer-managed keys**: Phase 2 (customer controls encryption, ACA cannot decrypt 
  without customer key)
- **SOC 2 compliance**: Background checks, access reviews, audit trails

**Verification:**
- Quarterly access review: verify RBAC assignments
- Annual SOC 2 audit: verify separation of duties (Phase 2)

**Risk rating:** MEDIUM (Phase 1) -> Mitigated to LOW (Phase 2 with CMK + SOC 2)

---

### STRIDE Analysis Summary

| Threat Category | Example | Primary Mitigation | Residual Risk |
|---|---|---|---|
| **Spoofing** | Fake auth token | MSAL signature validation | LOW |
| **Tampering** | Modify findings in Cosmos | Cosmos RBAC (managed identity only) | LOW |
| **Repudiation** | "I didn't trigger that scan" | Structured logs (every request) | LOW |
| **Information Disclosure** | Cross-tenant data leak | Partition key enforcement | LOW |
| **Denial of Service** | API flood | APIM rate limiting | MEDIUM |
| **Elevation of Privilege** | Tier 1 -> Tier 3 unlock without payment | Stripe webhook signature | LOW |

---

## SECURITY ZONES

### Zone 1: Public Internet (Untrusted)

**Assets:**
- Frontend (React SPA, Static Web App)
- APIM public endpoint (Phase 1)
- Front Door public endpoint (Phase 2)

**Controls:**
- TLS 1.2+ enforced
- HTTPS-only (HSTS header)
- WAF enabled (Phase 2: OWASP Top 10 rules)
- DDoS protection (Azure default)

---

### Zone 2: DMZ (Gateway Layer)

**Assets:**
- Azure Front Door (Phase 2)
- API Management (both phases)

**Controls:**
- Rate limiting (10 req/sec per subscription)
- IP allow lists (optional, for enterprise customers)
- Geo-filtering (optional, block high-risk countries)
- Bot detection (Phase 2: Front Door Premium)

---

### Zone 3: Application Tier (Authenticated)

**Assets:**
- Container Apps (API, collector, analysis, delivery)
- Service Bus (Phase 2)

**Controls:**
- MSAL token validation (every request)
- Tenant middleware (partition key injection)
- Tier gate middleware (feature flags)
- No public endpoints (Phase 2: VNET-injected only)
- Managed identity for all Azure SDK calls

---

### Zone 4: Data Tier (Restricted)

**Assets:**
- Cosmos DB
- Blob Storage (deliverables)
- Key Vault

**Controls:**
- Private endpoints (Phase 2)
- Partition key mandatory (code-enforced)
- RBAC (managed identity only, no connection strings)
- Encryption at rest (Microsoft-managed keys Phase 1, customer-managed Phase 2)
- Soft-delete + purge protection (Key Vault, 90 days)
- Continuous backup (Cosmos, 7-day Phase 1, 35-day Phase 2)

---

### Zone 5: Identity & Secrets (High Security)

**Assets:**
- Entra ID tenant (Microsoft-managed)
- Key Vault (marcosandkv20260203 Phase 1, aca-kv-prod Phase 2)

**Controls:**
- MFA enforced for all admin accounts
- Conditional Access policies (trusted locations only)
- Key Vault RBAC mode (no access policies)
- Secret rotation (90-day cycle for PATs, on-demand for API keys)
- Audit logs (Azure AD sign-ins, Key Vault access)

---

## IDENTITY AND ACCESS MANAGEMENT

### User Authentication Flow (Entra OIDC + MSAL)

```
1. User clicks "Sign in with Microsoft"
   Frontend: window.location.href = "https://login.microsoftonline.com/..."

2. Entra ID displays Microsoft login page
   User enters email + password + MFA (if required)

3. User grants consent for ACA app registration
   Requested scopes:
   - openid (user identity)
   - profile (name, email)
   - offline_access (refresh token)
   - https://management.azure.com/user_impersonation (delegated Azure access)

4. Entra redirects back to frontend with auth code
   https://aca.example.com/callback?code=ABC123...

5. Frontend exchanges code for tokens (MSAL.js)
   POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
   Response: access_token, refresh_token, id_token

6. Frontend stores tokens in sessionStorage (NOT localStorage)
   Security note: sessionStorage cleared on tab close (XSS mitigation)

7. Frontend calls API with access token
   Authorization: Bearer {access_token}

8. API validates token (MSAL Python library)
   - Signature verification (RSA-256, Entra public keys)
   - Expiration check (exp claim)
   - Issuer validation (iss claim)
   - Audience validation (aud claim = ACA client ID)

9. API extracts subscription_id from JWT claims
   - Custom claim: subscription_id (set during Azure OAuth consent)
   - Injected into request.state.subscription_id by tenant middleware

10. API queries Cosmos with partition_key=subscription_id
    All data scoped to this subscription only
```

### Delegated Azure Access (Collector Service)

**Flow:**
```
1. API receives scan request: POST /v1/scans (user-initiated)

2. API extracts refresh_token from request (stored in Key Vault after consent)

3. API triggers collector job with refresh_token (environment variable)

4. Collector job acquires ARM access token via MSAL
   app = msal.PublicClientApplication(client_id, authority)
   result = app.acquire_token_by_refresh_token(
       refresh_token,
       scopes=["https://management.azure.com/.default"]
   )
   access_token = result["access_token"]

5. Collector uses access_token for Azure SDK calls
   credential = AccessTokenCredential(access_token)
   resource_client = ResourceManagementClient(credential, subscription_id)

6. Azure validates token (enforces Reader role on subscription)

7. Collector pulls inventory, cost data, Advisor recommendations

8. Collector writes to Cosmos (partition_key=subscription_id)

9. Job completes, refresh_token rotated (90-day expiry)
```

**Security notes:**
- Refresh token stored in Key Vault (encrypted at rest)
- Access token ephemeral (5-minute lifetime, not stored)
- Reader role sufficient (no write permissions)
- Token rotation automatic (MSAL handles)

---

### RBAC Model (Internal ACA Roles)

**Phase 1 (Proof of Concept):**
- No role-based access control (all authenticated users have full access to their subscription)
- Admin operations via bearer token (no web UI)

**Phase 2 (Production):**

| Role | Permissions | Use Case |
|---|---|---|
| **ACA_Admin** | Full CRUD on all tenants, lock/unlock, reconcile, tier overrides | Support escalations, billing disputes |
| **ACA_Support** | Read-only on scans, findings, entitlements | Customer support inquiries |
| **ACA_FinOps** | Read cost-data, update Stripe reconciliation status | Billing operations |
| **ACA_User** | Full access to own subscription only | Standard customer |

**Entra ID group mapping:**
- ACA_Admin -> Entra group: `sg-aca-admins`
- ACA_Support -> Entra group: `sg-aca-support`
- ACA_FinOps -> Entra group: `sg-aca-finops`

**Authorization check (API):**
```python
# app/middleware/rbac.py
def require_role(required_roles: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_groups = request.state.user_groups  # from JWT claims
            if not any(group in user_groups for group in required_roles):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage:
@router.post("/v1/admin/tenant/lock")
@require_role(["ACA_Admin"])
async def lock_tenant(subscription_id: str):
    ...
```

---

## DATA PROTECTION

### Encryption Standards

**At Rest:**
- Cosmos DB: AES-256 (Microsoft-managed keys Phase 1, customer-managed Phase 2)
- Blob Storage: AES-256 (same as Cosmos)
- Key Vault: FIPS 140-2 Level 2 (hardware security module)

**In Transit:**
- TLS 1.2+ (minimum, prefer TLS 1.3 Phase 2)
- Frontend -> APIM: HTTPS enforced (HSTS)
- APIM -> API: HTTPS (internal, VNET-only Phase 2)
- API -> Cosmos: HTTPS (Azure SDK default)

**In Use:**
- No processing of plaintext secrets (Key Vault integration)
- No logging of sensitive data (PII redacted in structlog)

---

### Data Classification

| Data Type | Classification | Storage | Retention | Disposal |
|---|---|---|---|---|
| **Customer Azure metadata** | INTERNAL | Cosmos (inventories) | 90 days | Cascade delete on subscription delete |
| **Cost data** | INTERNAL | Cosmos (cost-data) | 90 days | Cascade delete |
| **Findings** | INTERNAL | Cosmos (findings) | Permanent | Export available, delete on request |
| **Entitlements** | CONFIDENTIAL | Cosmos (entitlements) | Permanent | Delete on subscription cancel (30-day grace) |
| **Stripe customer ID** | CONFIDENTIAL | Cosmos (entitlements) | Permanent | Delete on subscription cancel |
| **Refresh tokens** | SECRET | Key Vault | 90 days | Auto-rotate (MSAL) |
| **IaC templates** | INTERNAL | Blob Storage | 30 days | Lifecycle policy -> Archive -> Delete |
| **Logs** | INTERNAL | App Insights | 30 days Phase 1, 90 days Phase 2 | Auto-purge |

**No PII collected:**
- No names, addresses, phone numbers
- Email stored in Stripe only (ACA does not store)
- subscriptionId is Azure technical identifier (not PII per GDPR)

---

### Backup and Recovery

**Cosmos DB:**
- Continuous backup enabled (automatic, no manual snapshots)
- Point-in-time restore (PITR): 7 days Phase 1, 35 days Phase 2
- Geo-redundancy: canadacentral (primary), canadaeast (secondary) Phase 2 only

**Recovery process:**
```bash
# Restore to a specific timestamp
az cosmosdb restore \
  --account-name aca-cosmos-prod \
  --target-database-account-name aca-cosmos-prod-restored \
  --resource-group aca-prod-canadacentral \
  --restore-timestamp "2026-03-01T14:00:00Z" \
  --databases-to-restore name=aca-db collections=findings

# Verify restored data (manual query)
# Swap accounts (manual cutover via DNS CNAME)
```

**Blob Storage:**
- No backup (IaC templates regenerable from findings)
- Lifecycle policy: Archive after 30 days, delete after 90 days

**Key Vault:**
- Soft-delete: 90 days (cannot permanently delete for 90 days)
- Purge protection: enabled (prevents accidental purge)

---

### Data Deletion (GDPR Right to Erasure)

**Customer-initiated deletion:**
1. Customer navigates to /settings -> "Delete My Account"
2. Confirmation dialog: "This will permanently delete all your data. Continue?"
3. Frontend calls: `DELETE /v1/entitlements/{subscription_id}`
4. API marks entitlement with `deletion_requested_at` timestamp
5. Background job (nightly):
   - Deletes Cosmos documents (partition_key=subscription_id)
   - Deletes Blob deliverables (prefix=subscription_id)
   - Cancels Stripe subscription (webhook triggers entitlement cleanup)
6. Deletion confirmed via email: "Your data has been deleted"

**Timeline:**
- Soft delete: immediate (marked for deletion)
- Hard delete: 30 days (grace period for accidental deletion)
- Backup purge: 35 days (PITR retention Phase 2)

---

## COMPLIANCE CONTROLS

### SOC 2 Type II Roadmap (Target: Q3 2026)

**Common Criteria:**
- CC6.1: Logical access controls (RBAC + MFA)
- CC6.2: New user provisioning (Entra + JML process)
- CC6.6: Encryption at rest and in transit
- CC6.7: Change management (ADO work items + GitHub PR approval)

**Trust Services Criteria:**
- A1.2: System availability (99.9% uptime SLA Phase 2)
- C1.2: Confidentiality (customer-managed keys)
- PI1.4: Data disposal (GDPR right to erasure)

**Phase 2 requirements:**
- [ ] Customer-managed keys (Key Vault)
- [ ] 90-day log retention (Log Analytics)
- [ ] Background checks for all operators
- [ ] Quarterly access reviews (RBAC audit)
- [ ] Incident response plan (runbooks)
- [ ] Penetration testing (annual)

---

### GDPR Compliance

**Legal basis:** Legitimate interest (cost optimization service)

**Data subject rights:**
- Right to access: `GET /v1/export` (Tier 2+, returns findings.json)
- Right to erasure: `DELETE /v1/entitlements/{subscription_id}` (30-day grace)
- Right to portability: `GET /v1/export` (JSON format)
- Right to rectification: Customer can re-run scan (data refreshes automatically)

**Data protection:**
- Data processor: ACA (Microsoft Azure is sub-processor)
- Data location: Canada (canadacentral) Phase 1, customer choice Phase 2
- Data transfer: No cross-border (within Azure Canada region)

**Breach notification:**
- Detection: Application Insights alerts (anomalous access patterns)
- Notification: 72 hours (GDPR requirement)
- Remediation: Key rotation, token revocation, Cosmos PITR restore

---

## INCIDENT RESPONSE

### Severity Classification

| Severity | Definition | Response Time | Examples |
|---|---|---|---|
| **S1 (Critical)** | Data breach, service down, payment fraud | 30 minutes | Cross-tenant data leak detected |
| **S2 (High)** | Degraded performance, partial outage | 2 hours | Cosmos throttling (429 errors) |
| **S3 (Medium)** | Non-critical bug, single-tenant issue | 8 hours | Collector job fails for one subscription |
| **S4 (Low)** | Cosmetic issue, documentation update | 48 hours | Typo in Tier 1 report |

---

### Incident Response Procedure (S1)

**Detection:**
- Automated alert: Application Insights (anomalous query: SELECT * FROM c without partition key)
- Manual report: Customer email: "I see another customer's findings in my account"

**Immediate actions (0-30 minutes):**
1. Page on-call engineer (PagerDuty)
2. Confirm incident (reproduce the issue)
3. Isolate affected systems:
   - Disable API endpoint: `az containerapp revision deactivate`
   - Rotate Cosmos keys (prevent further access)
4. Preserve evidence:
   - Export Application Insights logs (last 24 hours)
   - Export Cosmos audit logs (last 24 hours)
   - Screenshot of alert + reproduction steps

**Containment (30 minutes - 2 hours):**
5. Identify root cause (code review + log analysis)
   - Example: Tenant middleware bug (partition key not injected)
6. Deploy hotfix:
   - Rollback to previous revision (if regression)
   - OR deploy emergency fix (if zero-day)
7. Verify fix (integration test + manual QA)

**Eradication (2-4 hours):**
8. Confirm no ongoing breach (monitor logs for 2 hours)
9. Reset affected tokens (revoke + reissue)
10. Cosmos PITR restore (if data modified)

**Recovery (4-8 hours):**
11. Re-enable API endpoint
12. Customer notification (affected tenants only):
    - Subject: "Security Incident Notification"
    - Body: "What happened, what we did, what data was affected, what you should do"
    - Timeline: "Incident detected at X, contained at Y, resolved at Z"
13. Status page update: "Resolved"

**Post-Incident Review (1 week):**
14. Root cause analysis (RCA document)
15. Code audit (peer review of affected code paths)
16. Control enhancement (e.g. add unit test for tenant isolation)
17. GDPR notification (if PII affected, within 72 hours)

---

### Security Monitoring Queries (Kusto)

**Anomalous access patterns:**
```kql
// Cross-tenant query attempts (should never happen)
traces
| where message contains "partition_key" and message contains "null"
| project timestamp, subscription_id=customDimensions.subscription_id, user_id=customDimensions.user_id
| order by timestamp desc

// Multiple failed auth attempts (brute force)
requests
| where resultCode == 401
| summarize FailedAttempts=count() by user_id=tostring(customDimensions.user_id), bin(timestamp, 5m)
| where FailedAttempts > 10
```

**High-privilege operations:**
```kql
// Admin actions (tenant lock/unlock)
traces
| where message contains "admin_action"
| project timestamp, action=customDimensions.action, subscription_id=customDimensions.subscription_id, actor=customDimensions.actor
| order by timestamp desc
```

**Stripe webhook anomalies:**
```kql
// Webhook signature failures
traces
| where message contains "stripe_webhook" and message contains "invalid_signature"
| project timestamp, remote_ip=customDimensions.remote_ip, payload_excerpt=substring(tostring(customDimensions.payload), 0, 100)
| order by timestamp desc
```

---

## SECURITY BEST PRACTICES (DEVELOPMENT)

### Secure Coding Guidelines

1. **Never trust user input**
   - Validate all request parameters (Pydantic models)
   - Sanitize string inputs (SQL injection prevention, though Cosmos uses parameterized queries)
   - Reject unexpected fields (Pydantic strict mode)

2. **Always use partition keys**
   - Every Cosmos query MUST include `partition_key=subscription_id`
   - Unit tests enforce this (test_partition_key_mandatory())

3. **No secrets in code**
   - All secrets in Key Vault
   - Environment variables for secret names only (e.g. `KV_NAME=marcosandkv20260203`)
   - DefaultAzureCredential() for authentication

4. **Structured logging (no sensitive data)**
   - Log subscriptionId (not PII)
   - DO NOT log: access_token, refresh_token, Stripe keys
   - Redact customer emails in logs

5. **Fail secure**
   - Auth failure -> 401 (never fallback to anonymous)
   - Partition key missing -> 403 (never query all partitions)
   - Stripe signature invalid -> 400 (never process payment)

6. **Least privilege RBAC**
   - API managed identity: `Cosmos DB Data Reader` only (no Contributor)
   - Jobs managed identity: `Cosmos DB Data Contributor` (write access needed)
   - Key Vault: `Key Vault Secrets User` (no Administrator)

---

### Security Testing Checklist

**Phase 1 (every PR):**
- [ ] Unit tests for tenant isolation (`test_cross_tenant_blocked()`)
- [ ] Unit tests for auth bypass (`test_no_auth_header_blocked()`)
- [ ] Unit tests for Stripe webhook signature (`test_invalid_signature_blocked()`)
- [ ] SAST scan (Bandit for Python, ESLint security plugin for TypeScript)
- [ ] Dependency scan (pip-audit, npm audit)

**Phase 2 (quarterly):**
- [ ] Penetration testing (external firm)
- [ ] DAST scan (OWASP ZAP)
- [ ] Threat model review (STRIDE analysis update)
- [ ] Access review (RBAC audit)
- [ ] Incident response drill (tabletop exercise)

---

## RELATED DOCUMENTS

- [Application Architecture](./application-architecture.md) -- component design
- [Solution Architecture](./solution-architecture.md) -- business context
- [Infrastructure Architecture](./infrastructure-architecture.md) -- deployment topology
- [04-security.md](../04-security.md) -- security policy (original spec)
- [PLAN.md](../../PLAN.md) -- Epic 10 (Hardening) tasks

---

END OF SECURITY ARCHITECTURE
