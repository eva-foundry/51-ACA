<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-17",
  "sprint_title": "api-auth-routes-batch-1",
  "target_branch": "sprint/17-api-auth-routes-batch-1",
  "epic": "ACA-04",
  "stories": [
    {
      "id": "ACA-04-001",
      "title": "Sign in via Microsoft Identity (multi-tenant mode)",
      "wbs": "4.1.1",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "Auth flow requires careful MSAL configuration and token handling. gpt-4o for complex logic.",
      "epic": "Epic 4 -- API and Auth Layer",
      "files_to_create": [
        "services/api/app/auth/msal_client.py (MSAL app factory, authority=common)",
        "services/api/app/routers/auth.py (sign-in route stub -> implementation)"
      ],
      "files_to_modify": [],
      "acceptance": [
        "MSAL PublicClientApplication created with authority=https://login.microsoftonline.com/common",
        "Sign-in flow on frontend calls MSAL.js with same authority",
        "Token acquired contains delegated permissions (Reader, Cost Management Reader)",
        "Refresh token persisted in sessionStorage (frontend) or secure cookie (API)",
        "Test: multiple tenant sign-ins work (personal + work accounts)"
      ],
      "implementation_notes": "Multi-tenant mode (authority=common) allows ANY Microsoft account. NOT EsDAICoE-specific. Store refreshToken in secure location per-scan (KV, not per-user)."
    },
    {
      "id": "ACA-04-003",
      "title": "Extract subscriptionId from session + read tier from Cosmos",
      "wbs": "4.1.3",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Session extraction and Cosmos lookup. Straightforward data retrieval.",
      "epic": "Epic 4 -- API and Auth Layer",
      "files_to_create": [
        "services/api/app/auth/session.py (extract_subscription_id, validate_tier)"
      ],
      "files_to_modify": [
        "services/api/app/middleware/auth.py (add tier extraction after JWT validation)"
      ],
      "acceptance": [
        "extract_subscription_id(token) returns subscriptionId from token claims or session",
        "validate_tier(subscriptionId) queries Cosmos clients container, returns tier string",
        "Middleware stores tier in request.state.tier for downstream use",
        "Test: tier='TIER1' correctly fetched from Cosmos for test subscriptionId"
      ],
      "implementation_notes": "Tier is NOT stored in JWT. Always read from Cosmos to allow admin overrides. Cosmos query use partition key = subscriptionId for performance."
    },
    {
      "id": "ACA-04-004",
      "title": "Connect Azure subscription (POST /v1/auth/connect) - Mode A delegated auth",
      "wbs": "4.1.4",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "Complex multi-step: validate token, call preflight probes, write to Cosmos + KV. Requires gpt-4o.",
      "epic": "Epic 4 -- API and Auth Layer",
      "files_to_create": [
        "services/api/app/routers/auth.py >> POST /v1/auth/connect (implementation)"
      ],
      "files_to_modify": [
        "services/api/app/auth/msal_client.py (add get_resource_token method)",
        "services/api/app/db/cosmos.py (add upsert_client method)"
      ],
      "acceptance": [
        "POST /v1/auth/connect accepts { delegatedToken, desiredTier? }",
        "Extract subscriptionId from token claims",
        "Validate token has Reader + Cost Management Reader scopes on subscriptionId",
        "Write to Cosmos clients container: { subscriptionId, tier='TIER1', connectedAt=utc }",
        "Store refreshToken in Key Vault under aca-connect-{subscriptionId}",
        "Return { subscriptionId, tier, connectedAt, preflight_passcode? }",
        "Test: connect with valid token, verify Cosmos + KV write"
      ],
      "implementation_notes": "Mode A only (delegated). Modes B/C deferred. Preflight probes called separately (future story). Refresh token rotation handled by MSAL automatically."
    },
    {
      "id": "ACA-04-005",
      "title": "Disconnect subscription (POST /v1/auth/disconnect) - revoke all tokens",
      "wbs": "4.1.5",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "Straightforward cleanup: delete from Cosmos, delete from KV, revoke token.",
      "epic": "Epic 4 -- API and Auth Layer",
      "files_to_create": [
        "services/api/app/routers/auth.py >> POST /v1/auth/disconnect (implementation)"
      ],
      "files_to_modify": [
        "services/api/app/db/cosmos.py (add delete_client_tokens method)",
        "services/api/app/auth/msal_client.py (add revoke_refresh_token method)"
      ],
      "acceptance": [
        "POST /v1/auth/disconnect requires authenticated request (subscriptionId in request.state)",
        "Delete client record from Cosmos (subscriptionId as partition key)",
        "Delete all refresh tokens from Key Vault matching aca-connect-{subscriptionId}",
        "Return { status='disconnected', subscriptionId, revokedAt=utc }",
        "Test: disconnect, verify subsequent API calls return 401 Unauthorized"
      ],
      "implementation_notes": "All access tokens become invalid after disconnect because Cosmos lookup (validate_tier) will fail. Cleanup is best-effort (KV delete errors don't block response)."
    },
    {
      "id": "ACA-04-009",
      "title": "Preflight probes (POST /v1/auth/preflight) - validate RBAC + capabilities",
      "wbs": "4.2.2",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "Multi-probe validation (RBAC, quotas, region). Complex error handling. gpt-4o required.",
      "epic": "Epic 4 -- API and Auth Layer",
      "files_to_create": [
        "services/api/app/routers/auth.py >> POST /v1/auth/preflight (implementation)",
        "services/api/app/auth/probes.py (5 probe functions: rbac, cosmosdb, keyvault, storage, appinsights)"
      ],
      "files_to_modify": [
        "services/api/app/auth/msal_client.py (add get_management_token method for ARM calls)"
      ],
      "acceptance": [
        "POST /v1/auth/preflight requires authenticated token",
        "Probe 1: RBAC -- User has Reader + Cost Management Reader on subscriptionId",
        "Probe 2: Cosmos -- Client has network access + valid connection string",
        "Probe 3: Key Vault -- KV exists + client has get/list permissions",
        "Probe 4: Storage -- Blob container accessible for result downloads",
        "Probe 5: App Insights -- InstrumentationKey valid + writable",
        "Return { passcode: '12345', probes: [ { name, status, message } ], warnings: [] }",
        "Test: run preflight, verify all 5 probes pass for sandbox subscription"
      ],
      "implementation_notes": "Passcode is 5-digit code shown to user (optional, for support). Probes are non-blocking (1 probe failure doesn't stop others). Errors are collected in warnings array, not exceptions."
    },
    {
      "id": "ACA-04-007",
      "title": "Frontend LoginPage: MSAL.js sign-in with authority=common",
      "wbs": "4.1.7",
      "size": "S",
      "model": "gpt-4o-mini",
      "model_rationale": "React component using MSAL.js. Straightforward UI implementation.",
      "epic": "Epic 4 -- API and Auth Layer",
      "files_to_create": [
        "frontend/src/pages/LoginPage.tsx (MSAL sign-in button + redirect handler)"
      ],
      "files_to_modify": [
        "frontend/src/auth/msal-config.ts (authority=common, replyUrls=[http://localhost:3000/auth-callback, https://aca.prod/auth-callback])"
      ],
      "acceptance": [
        "LoginPage renders MSAL sign-in button (Fluent UI PrimaryButton)",
        "Clicking button calls useMsal().login() with authority=https://login.microsoftonline.com/common",
        "Pop-up shows account selector (personal + work accounts from all tenants)",
        "After sign-in, redirects to /connect-subscription page",
        "Access token stored in sessionStorage, refresh token in secure cookie",
        "Test: sign-in with multiple account types (personal @outlook.com, work @company.com)"
      ],
      "implementation_notes": "Use @azure/msal-react (v2.14+). Authority=common enables multi-tenant. Don't restrict to specific organizations. Refresh token rotation automatic."
    }
  ]
}
-->

# Sprint 17: API Auth Routes Batch 1 -- 6 Stories (Auth Foundation)

**Sprint ID**: SPRINT-17
**Epic**: Epic 4 -- API and Auth Layer
**Target Branch**: sprint/17-api-auth-routes-batch-1
**Total FP**: 18 (2×M=10 FP + 3×S=9 FP, rounding to 18)
**Sprint Goal**: Complete Feature 4.1 authentication (sign-in, connect, disconnect, preflight, tier extraction)

---

## Stories

### Story ACA-04-001: Sign In via Microsoft Identity
- **WBS**: 4.1.1
- **Size**: M=3 FP
- **Model**: gpt-4o
- **Description**: MSAL client factory + sign-in flow (multi-tenant mode)
- **Files to Create**: msal_client.py, auth.py route
- **Acceptance**: MSAL authority=common, delegated tokens acquired, refresh persisted

### Story ACA-04-003: Extract subscriptionId + Read Tier from Cosmos
- **WBS**: 4.1.3  
- **Size**: S=2 FP
- **Model**: gpt-4o-mini
- **Description**: Session tier extraction, Cosmos lookup
- **Files to Create**: session.py
- **Acceptance**: subscriptionId extracted from token, tier fetched from Cosmos

### Story ACA-04-004: Connect Azure Subscription (POST /v1/auth/connect)
- **WBS**: 4.1.4
- **Size**: M=3 FP
- **Model**: gpt-4o
- **Description**: Multi-step connect flow with validation + Cosmos write + KV storage
- **Files to Create/Modify**: auth router implementation, Cosmos upsert
- **Acceptance**: Valid token -> Cosmos write + KV storage, return tier

### Story ACA-04-005: Disconnect Subscription (POST /v1/auth/disconnect)
- **WBS**: 4.1.5
- **Size**: S=2 FP
- **Model**: gpt-4o-mini
- **Description**: Cleanup: delete Cosmos record + revoke KV tokens
- **Files to Create/Modify**: auth router implementation, Cosmos delete
- **Acceptance**: Post-disconnect, API calls return 401

### Story ACA-04-009: Preflight Probes (POST /v1/auth/preflight)
- **WBS**: 4.2.2
- **Size**: M=3 FP
- **Model**: gpt-4o
- **Description**: 5-probe validation (RBAC, Cosmos, KV, Storage, AppInsights)
- **Files to Create**: probes.py, auth router endpoint
- **Acceptance**: All 5 probes run, return status + warnings

### Story ACA-04-007: Frontend LoginPage MSAL.js
- **WBS**: 4.1.7
- **Size**: S=2 FP
- **Model**: gpt-4o-mini
- **Description**: React LoginPage with MSAL sign-in button, authority=common
- **Files to Create/Modify**: LoginPage.tsx, msal-config.ts
- **Acceptance**: Multi-tenant sign-in works, redirects to connect-subscription

---

## Success Criteria

- **Feature 4.1 Complete**: Sign-in → Connect → Tier Extraction → Disconnect all working
- **Auth Flow End-to-End**: Frontend sign-in → backend token validation → Cosmos tier lookup → API access control
- **Test Coverage**: 10+ API tests (positive + edge cases)
- **Cosmos + KV Wired**: Client records + refresh tokens + tier management functional
- **Evidence Receipt**: Created for all 6 stories

---

## Scaling Progression

| Sprint | Epic | Stories | FP | Execution (Est) |
|--------|------|---------|----|-|
| 13 | 3 (Analysis) | 4 | 12 | 2.7 hours |
| 14 | 3 | 5 | 15 | 3.1 hours |
| 15 | 3 | 6 | 18 | 3.7 hours |
| 16 | 3 | 7 | 21 | 4.3 hours |
| **17** | **4** | **6** | **18** | **3.5 hours (est)** |

**Estimated Sprint 17 execution time: 25-35 minutes** (based on 6 API routes × 4 min each + tests)

---

## API Endpoint Summary (Sprint 17 Creates)

| Endpoint | Method | Feature | Status |
|----------|--------|---------|--------|
| /v1/auth/signin | - | Login UI | Story 4.1.1 (frontend via MSAL.js) |
| /v1/auth/connect | POST | Connect subscription | Story 4.1.4 |
| /v1/auth/disconnect | POST | Disconnect subscription | Story 4.1.5 |
| /v1/auth/preflight | POST | Validation probes | Story 4.1.9 |
| /v1/entitlements | GET | Tier lookup (middleware) | Story 4.1.3 |
| **/health** | GET | Health check (unauthenticated) | Story 4.2.11 (stub, no implementation needed) |

**Epic 4 Remaining** (Sprints 18-20):
- Core endpoints (collect, reports, billing): ACA-04-010 through ACA-04-016
- APIM policies: ACA-04-017 through ACA-04-021
- Admin endpoints: ACA-04-022 through ACA-04-026
- Total: 20+ stories, ~60 FP, 3-4 additional sprints
