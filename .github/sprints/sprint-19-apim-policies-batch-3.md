# Sprint 19 Manifest -- Feature 4.3: APIM Policies (Gateway Integration)

**Sprint**: 19  
**Feature**: 4.3 -- APIM Policies / Gateway Security & Enforcement  
**Stories**: 5 (ACA-04-018 through ACA-04-022 or adjusted per scope)  
**Est. FP**: 15-18 (3 FP per policy + testing)  
**Execution Model**: GitHub Cloud Agents  
**Date Created**: March 2, 2026, 8:55 AM ET  

---

## Overview

APIM (Azure API Management) acts as the public gateway. This sprint implements 5 critical policies:
1. JWT signature validation (on all /v1/* routes)
2. Entitlements caching (60s per subscriptionId)
3. Tier-based access control (403 if tier insufficient)
4. Rate limiting (100 req/min default)
5. Request/response header management (X-Subscription-Id forwarding)

All policies are **policy-as-code** (XML files in Azure) + **policy bindings** defined in terraform/bicep.

---

## Story 1: ACA-04-018 -- JWT Signature Validation Policy

**Feature**: 4.3 APIM Policies -- Validate JWT on all /v1/* routes  
**Acceptance**:
- [ ] APIM policy validates JWT signature using JWKS from https://login.microsoftonline.com/common/discovery/keys
- [ ] Policy set on all /v1/* routes (except /v1/auth/health + /v1/webhooks/stripe)
- [ ] Invalid JWT returns 401 Unauthorized
- [ ] Expired JWT returns 401 Unauthorized
- [ ] Valid JWT extracts subscriptionId claim and passes to backend via X-Subscription-Id header
- [ ] Policy XML is idempotent (terraform apply multiple times = same result)
- [ ] IaC (terraform or bicep) defines policy binding to product scope
- [ ] Story tested via newman (Postman collection) or curl against APIM gateway

**API Design** (APIM Policy Context):
```xml
<!-- aca-jwt-validate.policy.xml -->
<policy>
  <inbound>
    <validate-jwt header-name="Authorization" failed-validation-error-message="Unauthorized">
      <openid-config url="https://login.microsoftonline.com/common/.well-known/openid-configuration" />
      <audiences>
        <!-- ACA app registration client ID -->
        <audience>12345678-1234-1234-1234-123456789012</audience>
      </audiences>
      <issuers>
        <issuer>https://login.microsoftonline.com/common/v2.0</issuer>
      </issuers>
    </validate-jwt>
    <!-- Extract subscriptionId from JWT claims -->
    <set-header name="X-Subscription-Id" exists-action="override">
      <value>@(context.Request.Headers["Authorization"])</value>  <!-- stub: decode JWT in production -->
    </set-header>
  </inbound>
</policy>
```

**Files**:
- infra/phase1-marco/policies/aca-jwt-validate.policy.xml (NEW)
- infra/phase1-marco/main.tf (MODIFIED) -- policy binding on /v1/* routes
- services/api/tests/test_apim_policies.py (NEW) -- test invalid/expired JWT

---

## Story 2: ACA-04-019 -- Entitlements Caching Policy

**Feature**: 4.3 APIM Policies -- Cache /v1/entitlements for 60s  
**Acceptance**:
- [ ] APIM caches GET /v1/entitlements response for 60 seconds
- [ ] Cache key: entitlements::{subscriptionId} (extracted from X-Subscription-Id header)
- [ ] Cache header: Cache-Control: private, max-age=60
- [ ] Cache invalidation on subscription tier change (webhook from API backend)
- [ ] Policy XML is valid APIM policy
- [ ] Terraform applies policy binding without errors
- [ ] Story tested via repeated requests (expect 304 Not Modified or cached response)

**API Design** (APIM Policy Context):
```xml
<!-- aca-entitlements-cache.policy.xml -->
<policy>
  <inbound>
    <cache-lookup vary-by-header="X-Subscription-Id" vary-by-query-parameter="none">
      <vary-by-header>X-Subscription-Id</vary-by-header>
    </cache-lookup>
  </inbound>
  <backend>
    <!-- Call backend GET /v1/entitlements -->
  </backend>
  <outbound>
    <cache-store duration="60" cache-response="true">
      <vary-by-header>X-Subscription-Id</vary-by-header>
    </cache-store>
  </outbound>
</policy>
```

**Files**:
- infra/phase1-marco/policies/aca-entitlements-cache.policy.xml (NEW)
- infra/phase1-marco/main.tf (MODIFIED) -- policy binding on /v1/entitlements
- services/api/tests/test_apim_policies.py (MODIFIED) -- test cache hit/miss

---

## Story 3: ACA-04-020 -- Tier-Based Access Control Policy

**Feature**: 4.3 APIM Policies -- Return 403 if client tier insufficient  
**Acceptance**:
- [ ] APIM calls GET /v1/entitlements to fetch client tier
- [ ] If tier=TIER1 but endpoint requires TIER2+, return 403 Forbidden (custom error: TIER_REQUIRED)
- [ ] Tier requirements defined per endpoint (metadata: tier-required=TIER2)
- [ ] Policy checks tier against endpoint requirement
- [ ] Policy caches entitlements call (reuses story 2 cache)
- [ ] Error response includes reason + upgrade link
- [ ] Terraform applies policy binding without errors
- [ ] Story tested via testing Tier 1 client against Tier 2 endpoint

**API Design** (APIM Policy Context):
```xml
<!-- aca-tier-gating.policy.xml -->
<policy>
  <inbound>
    <set-variable name="required-tier" value="@(context.Operation.Name)" />  <!-- stub -->
    <!-- Call entitlements (cached) -->
    <!-- Compare tier from response vs required tier -->
    <!-- If tier insufficient, return 403 -->
    <choose>
      <when condition="@(context.Variables["user-tier"] != 'TIER2')">
        <return-response>
          <set-status code="403" reason="Forbidden" />
          <set-body>{ "error": "TIER_REQUIRED", "requiredTier": "TIER2", "upgradUrl": "..." }</set-body>
        </return-response>
      </when>
    </choose>
  </inbound>
</policy>
```

**Files**:
- infra/phase1-marco/policies/aca-tier-gating.policy.xml (NEW)
- infra/phase1-marco/main.tf (MODIFIED) -- policy binding on tier2+ endpoints
- services/api/tests/test_apim_policies.py (MODIFIED) -- test tier gating (403 for TIER1)

---

## Story 4: ACA-04-021 -- Rate Limiting Policy

**Feature**: 4.3 APIM Policies -- Enforce 100 requests/minute default  
**Acceptance**:
- [ ] APIM rate-limits to 100 req/min per subscription (X-Subscription-Id header)
- [ ] Exceeding limit returns 429 Too Many Requests
- [ ] Rate limit is per-subscription (different subs have separate buckets)
- [ ] Admin can override per-subscription via APIM dashboard (not automated in this story)
- [ ] Retry-After header included in 429 response
- [ ] Policy XML is valid APIM policy
- [ ] Terraform applies policy binding without errors
- [ ] Story tested via load test (101 requests in 60s should return 1x 429)

**API Design** (APIM Policy Context):
```xml
<!-- aca-rate-limit.policy.xml -->
<policy>
  <inbound>
    <rate-limit-by-key calls="100" renewal-period="60" counter-key="@(context.Request.Headers.GetValueOrDefault("X-Subscription-Id"))" />
  </inbound>
  <outbound>
    <choose>
      <when condition="@(context.Response.StatusCode == 429)">
        <set-header name="Retry-After" exists-action="override">
          <value>@(context.Response.Headers.GetValueOrDefault("Retry-After-Ms"))</value>
        </set-header>
      </when>
    </choose>
  </outbound>
</policy>
```

**Files**:
- infra/phase1-marco/policies/aca-rate-limit.policy.xml (NEW)
- infra/phase1-marco/main.tf (MODIFIED) -- policy binding on all /v1/* routes
- services/api/tests/test_apim_policies.py (MODIFIED) -- test 429 after 100 requests

---

## Story 5: ACA-04-022 -- Request/Response Header Management Policy

**Feature**: 4.3 APIM Policies -- Manage X-Subscription-Id header forwarding  
**Acceptance**:
- [ ] APIM sets X-Subscription-Id header on all backend calls (extracted from JWT claims)
- [ ] If header already present from client, reject (401 Unauthorized) or override
- [ ] Response removes sensitive headers (Authorization, APIM-Subscription-Key)
- [ ] Adds response headers: X-RateLimit-Remaining, X-RateLimit-Reset
- [ ] Policy is applied uniformly across all /v1/* routes via product policy
- [ ] Terraform applies policy binding without errors
- [ ] Story tested via inspecting request/response headers

**API Design** (APIM Policy Context):
```xml
<!-- aca-header-management.policy.xml -->
<policy>
  <inbound>
    <!-- Extract subscriptionId from JWT and set header -->
    <set-header name="X-Subscription-Id" exists-action="override">
      <value>@(context.Request.Headers.GetValueOrDefault("X-SubId-From-JWT"))</value>
    </set-header>
    <!-- Remove sensitive inbound headers -->
    <set-header name="Authorization" exists-action="delete" />
  </inbound>
  <outbound>
    <!-- Remove sensitive outbound headers -->
    <set-header name="Server" exists-action="delete" />
    <!-- Add rate limit headers -->
    <set-header name="X-RateLimit-Remaining" exists-action="override">
      <value>@(context.Variables["rate-limit-remaining"])</value>
    </set-header>
  </outbound>
</policy>
```

**Files**:
- infra/phase1-marco/policies/aca-header-management.policy.xml (NEW)
- infra/phase1-marco/main.tf (MODIFIED) -- policy binding on all /v1/* routes
- services/api/tests/test_apim_policies.py (MODIFIED) -- test header presence/absence

---

## Integration Testing

**File**: services/api/tests/test_apim_integration.py (NEW)
**Tests** (5-10 assertions):
- [ ] test_jwt_validation_happy_path() -- Valid JWT passes, calls backend
- [ ] test_jwt_validation_invalid_signature() -- Invalid JWT returns 401
- [ ] test_jwt_validation_expired() -- Expired JWT returns 401
- [ ] test_caching_entitlements() -- Repeated calls return cached response
- [ ] test_tier_gating_tier1_tries_tier2_endpoint() -- TIER1 client gets 403
- [ ] test_rate_limiting_100_per_minute() -- 101st call returns 429
- [ ] test_headers_subscription_id_forwarded() -- X-Subscription-Id in backend request
- [ ] test_headers_sensitive_removed() -- Authorization not in response
- [ ] test_combined_flow() -- Full flow: JWT → cache → tier check → backend → headers

---

## IaC Deliverables

**Terraform/Bicep Files**:
- infra/phase1-marco/policies/ (new directory)
  - aca-jwt-validate.policy.xml
  - aca-entitlements-cache.policy.xml
  - aca-tier-gating.policy.xml
  - aca-rate-limit.policy.xml
  - aca-header-management.policy.xml

- infra/phase1-marco/main.tf (modified)
  - APIM resource definitions (if not already present)
  - Policy binding definitions (product + operations scope)
  - Rate limit counter definitions
  - Cache definitions

---

## Summary

| Story | Policy Type | Endpoint Scope | Dependencies |
|---|---|---|---|
| ACA-04-018 | JWT Validation | All /v1/* except health/stripe | APIM, JWKS endpoint |
| ACA-04-019 | Caching | GET /v1/entitlements | Backend entitlements endpoint |
| ACA-04-020 | Tier Gating | Tier2+ endpoints | ACA-04-019 (cache) |
| ACA-04-021 | Rate Limiting | All /v1/* | APIM counters |
| ACA-04-022 | Header Management | All /v1/* | JWT claims parsing |

**Total Stories**: 5  
**Total FP**: 15-18 (3 FP per story)  
**Total Tests**: 8-12  
**Files to Create**: 5 policy XMLs + 3 test files + main.tf modifications  

---

## Execution Guidelines for Cloud Agents

1. **IaC First**: Create all policy XML files and terraform bindings before writing tests
2. **Policy Testing**: Can test in APIM sandbox without deploying to production
3. **Header Injection**: Use TestClient middleware mocking or actual APIM test runner
4. **Token Format**: Use JWT test tokens (can be mocked in policy validation)
5. **Evidence**: Record execution metrics (policy deployment time, test execution time, tokens used)

---

**Ready for Cloud Agent Execution**: Yes. This manifest is complete, testable, and has no external blockers.

**Next Steps After Sprint 19**:
- Sprint 20: Admin Endpoints (Feature 4.4) -- KPIs, customer search, grants, locks
- Sprint 21: Frontend Integration -- Wire UI to all API endpoints
- Sprint 22: Data Integration -- Cosmos wiring, real tests with live data
