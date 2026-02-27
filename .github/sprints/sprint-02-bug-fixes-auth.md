<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-02",
  "sprint_title": "bug-fixes-auth",
  "target_branch": "sprint/02-bug-fixes-auth",
  "epic": "ACA-04",
  "stories": [
    {
      "id": "ACA-03-021",
      "title": "Fix FindingsAssembler missing cosmos_client argument",
      "wbs": "ACA-03-021",
      "size": "XS",
      "model": "gpt-4o-mini",
      "model_rationale": "Single-file tag + unit test. No cross-service reasoning needed.",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/analysis/app/main.py",
        "services/tests/test_analysis_main.py"
      ],
      "acceptance": [
        "services/analysis/app/main.py has # EVA-STORY: ACA-03-021 tag",
        "FindingsAssembler instantiated with cosmos_client=get_cosmos_client() in main.py",
        "services/tests/test_analysis_main.py: test_findings_assembler_construction passes with mock cosmos_client",
        "pytest services/tests/test_analysis_main.py exits 0"
      ],
      "implementation_notes": "The fix is already in place: analysis/main.py line 30 passes cosmos_client=get_cosmos_client(). This story needs: (1) Add # EVA-STORY: ACA-03-021 tag to services/analysis/app/main.py. (2) Create services/tests/test_analysis_main.py with a unit test that mocks get_cosmos_client() and confirms FindingsAssembler instantiates without error. Use unittest.mock.patch to mock app.cosmos.get_cosmos_client. Import path from repo root: from services.analysis.app.findings import FindingsAssembler. Test must not require real Cosmos env vars."
    },
    {
      "id": "ACA-07-021",
      "title": "Fix generate_blob_sas call and SAS_HOURS constant",
      "wbs": "ACA-07-021",
      "size": "XS",
      "model": "gpt-4o-mini",
      "model_rationale": "Single-file tag + unit test. Fix is already in code.",
      "epic": "Epic 07 -- Delivery",
      "files_to_create": [
        "services/delivery/app/packager.py",
        "services/tests/test_packager_sas.py"
      ],
      "acceptance": [
        "services/delivery/app/packager.py has # EVA-STORY: ACA-07-021 tag",
        "SAS_HOURS = 168 in packager.py (already correct -- just confirm and tag)",
        "generate_blob_sas called with account_key= parameter (not credential=)",
        "services/tests/test_packager_sas.py: test_sas_uses_account_key passes",
        "services/tests/test_packager_sas.py: test_sas_expiry_7_days passes",
        "pytest services/tests/test_packager_sas.py exits 0"
      ],
      "implementation_notes": "The fix is already in place: packager.py has SAS_HOURS=168 and generate_blob_sas with account_key. This story needs: (1) Add # EVA-STORY: ACA-07-021 tag to services/delivery/app/packager.py. (2) Create services/tests/test_packager_sas.py. Mock azure.storage.blob.BlobServiceClient and azure.storage.blob.generate_blob_sas. Test 1: confirm generate_blob_sas is called with account_key kwarg (not credential). Test 2: confirm expiry = timedelta(hours=168). Import: from services.delivery.app.packager import DeliverablePackager, SAS_HOURS. Use unittest.mock.patch for the azure SDK calls."
    },
    {
      "id": "ACA-04-006",
      "title": "auth.py MSAL rework: multi-tenant authority=common, token_service.py",
      "wbs": "4.1.6",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "MSAL auth requires cross-file reasoning: settings.py, new token_service.py, auth.py router all change together.",
      "epic": "Epic 04 -- API",
      "files_to_create": [
        "services/api/app/services/token_service.py",
        "services/api/app/routers/auth.py",
        "services/api/app/settings.py"
      ],
      "acceptance": [
        "services/api/app/services/token_service.py created with TokenService class",
        "TokenService.initiate_device_code(subscription_id) returns {device_code, verification_uri, expires_in, user_code}",
        "TokenService.exchange_device_code(device_code) returns {access_token, refresh_token, subscription_id}",
        "MSAL PublicClientApplication uses authority=https://login.microsoftonline.com/common",
        "settings.py has ACA_CLIENT_ID field (str, from env ACA_CLIENT_ID)",
        "auth.py POST /connect calls TokenService.initiate_device_code, returns device_code + verification_uri",
        "auth.py has # EVA-STORY: ACA-04-006 tag",
        "token_service.py has # EVA-STORY: ACA-04-006 tag",
        "pytest: test for TokenService initiation with mock msal.PublicClientApplication passes"
      ],
      "implementation_notes": "Create services/api/app/services/token_service.py. Class TokenService: __init__(self, client_id=None) -- uses get_settings().ACA_CLIENT_ID if not injected (DI pattern from AGENTS.md). Use msal.PublicClientApplication(client_id, authority='https://login.microsoftonline.com/common'). Method initiate_device_code(subscription_id: str): calls app.initiate_device_flow(scopes=['https://management.azure.com/.default']). Returns dict with device_code, verification_uri, expires_in, user_code. Method exchange_device_code(device_code: str): calls app.acquire_token_by_device_flow(flow). Returns access_token, refresh_token. Add to settings.py: ACA_CLIENT_ID: str = Field(default='', description='MSAL app client ID'). Update auth.py POST /connect: call TokenService().initiate_device_code(req.subscription_id), return the flow dict. Remove the 501 raise. Keep the existing EVA-STORY tags on auth.py, add ACA-04-006 tag. Add # EVA-STORY: ACA-04-006 to token_service.py."
    },
    {
      "id": "ACA-04-002",
      "title": "JWT validation dependency: verify_token() FastAPI dep for authenticated routes",
      "wbs": "4.1.2",
      "size": "S",
      "model": "gpt-4o",
      "model_rationale": "Auth middleware touches security-critical token validation. gpt-4o for correctness.",
      "epic": "Epic 04 -- API",
      "files_to_create": [
        "services/api/app/deps/auth.py",
        "services/tests/test_jwt_dep.py"
      ],
      "acceptance": [
        "services/api/app/deps/auth.py created",
        "verify_token(token: str = Depends(oauth2_scheme)) validates JWT using JWKS from https://login.microsoftonline.com/common/discovery/v2.0/keys",
        "verify_token returns decoded payload dict on valid token",
        "verify_token raises HTTPException(status_code=401) on invalid / expired token",
        "services/api/app/deps/auth.py has # EVA-STORY: ACA-04-002 tag",
        "services/tests/test_jwt_dep.py: test_invalid_token_raises_401 passes",
        "pytest services/tests/test_jwt_dep.py exits 0"
      ],
      "implementation_notes": "Create services/api/app/deps/__init__.py and services/api/app/deps/auth.py. Use PyJWT (pip install PyJWT[cryptography] -- add to services/api/requirements.txt if not present). oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/token', auto_error=False). Dependency: async def verify_token(token: str = Depends(oauth2_scheme)) -> dict. If token is None: raise HTTPException(401, 'No token'). Decode using jwt.decode with options={'verify_signature': False} for audience-agnostic validation in dev. In production: fetch JWKS and verify with PyJWT JWTError -> 401. Return decoded payload. DI pattern: accept optional jwks_url for testing. Test: monkeypatch jwt.decode to return {'sub': 'test', 'oid': 'oid-123'} -- verify dep returns the dict. Test invalid: monkeypatch raises jwt.InvalidTokenError -- verify HTTPException(401) raised. Import path for tests: from services.api.app.deps.auth import verify_token."
    },
    {
      "id": "ACA-04-008",
      "title": "POST /v1/auth/connect: initiate MSAL device-code, store session in Cosmos",
      "wbs": "4.2.1",
      "size": "M",
      "model": "gpt-4o",
      "model_rationale": "Cross-service: uses TokenService + Cosmos clients_repo + auth.py. Security-critical.",
      "epic": "Epic 04 -- API",
      "files_to_create": [
        "services/api/app/routers/auth.py",
        "services/api/app/db/repos/clients_repo.py",
        "services/tests/test_auth_connect.py"
      ],
      "acceptance": [
        "POST /v1/auth/connect body: {subscription_id, connection_mode} returns {device_code, verification_uri, user_code, expires_in, subscription_id}",
        "POST /v1/auth/connect stores a pending connection record in Cosmos clients container with status=pending",
        "connection_mode=delegated triggers TokenService.initiate_device_code(subscription_id)",
        "connection_mode=service_principal returns 501 (not yet implemented) -- do not implement SP mode this sprint",
        "auth.py has # EVA-STORY: ACA-04-008 tag",
        "clients_repo.py has # EVA-STORY: ACA-04-008 tag and upsert_client(sub_id, doc) method using partition_key=sub_id",
        "services/tests/test_auth_connect.py: test_connect_delegated_returns_device_code passes with mock TokenService",
        "services/tests/test_auth_connect.py: test_connect_sp_returns_501 passes",
        "pytest services/tests/test_auth_connect.py exits 0"
      ],
      "implementation_notes": "Update auth.py POST /connect: (1) Remove 501 stub. (2) If req.connection_mode == 'service_principal': raise HTTPException(501, 'SP mode coming soon'). (3) Inject TokenService (DI -- accept token_svc=None param for testability). (4) Call token_svc.initiate_device_code(req.subscription_id). (5) Call ClientsRepo().upsert_client(req.subscription_id, {'subscriptionId': req.subscription_id, 'status': 'pending', 'connectionMode': 'delegated'}). (6) Return the device flow dict with subscription_id added. Create services/api/app/db/repos/clients_repo.py: class ClientsRepo with upsert_client(sub_id, doc) that calls upsert_item('clients', doc, partition_key=sub_id) from app.db.cosmos. Follow the DI + Cosmos pattern from services/api/AGENTS.md section 2. Test: mock TokenService.initiate_device_code to return {'device_code': 'dc123', 'verification_uri': 'https://aka.ms/devicelogin', 'user_code': 'ABCDEFGH', 'expires_in': 900}. Mock ClientsRepo.upsert_client. Call POST /v1/auth/connect via TestClient. Assert response has verification_uri."
    }
  ]
}
-->

# [SPRINT-02] bug-fixes-auth

Sprint-02 for ACA: 2 pre-flight bug verifications + 3 auth implementation stories.

**Branch**: `sprint/02-bug-fixes-auth`
**Stories**: 5 (2 XS + 1 S + 2 M = 8 FP)
**Veritas gate**: MTI >= 30, actions must include `merge`

---

<!-- STORY: ACA-03-021 -->
## ACA-03-021 -- Verify FindingsAssembler fix + add tag + unit test

**Size**: XS | **Model**: gpt-4o-mini | **Epic**: 3 (Analysis)

**Context**: The cosmos_client bug (C-04) was fixed in commit 4816baf. This story adds the EVA-STORY tag and the missing unit test to close the veritas gap.

**Files**:
- `services/analysis/app/main.py` (add EVA-STORY tag)
- `services/tests/test_analysis_main.py` (create)

**Acceptance**:
- `services/analysis/app/main.py` has `# EVA-STORY: ACA-03-021` tag
- `FindingsAssembler` instantiated with `cosmos_client=get_cosmos_client()` (already present -- confirm)
- `test_analysis_main.py`: `test_findings_assembler_construction` mocks `get_cosmos_client` and confirms no TypeError
- `pytest services/tests/test_analysis_main.py` exits 0

**Implementation notes**: Add the EVA-STORY tag. For the test: `unittest.mock.patch('services.analysis.app.cosmos.get_cosmos_client')`. Import `FindingsAssembler` from `services.analysis.app.findings`. Instantiate with mock cosmos_client and confirm no exception. Do NOT call `main()` -- just test the constructor.

**Spec references**: `_opus_review_findings_20260227.md` (C-04 entry)

<!-- END STORY: ACA-03-021 -->

---

<!-- STORY: ACA-07-021 -->
## ACA-07-021 -- Verify packager SAS fix + add tag + unit tests

**Size**: XS | **Model**: gpt-4o-mini | **Epic**: 7 (Delivery)

**Context**: SAS_HOURS=168 and account_key-based SAS (C-07) were fixed in commit 4816baf. Add the EVA-STORY tag and unit tests.

**Files**:
- `services/delivery/app/packager.py` (add EVA-STORY tag)
- `services/tests/test_packager_sas.py` (create)

**Acceptance**:
- `services/delivery/app/packager.py` has `# EVA-STORY: ACA-07-021` tag
- `SAS_HOURS = 168` confirmed in packager.py
- `generate_blob_sas` called with `account_key=` parameter (not `credential=`)
- `test_packager_sas.py`: `test_sas_uses_account_key` -- mock `generate_blob_sas`, confirm `account_key` kwarg present
- `test_packager_sas.py`: `test_sas_expiry_7_days` -- confirm expiry delta is 168 hours
- `pytest services/tests/test_packager_sas.py` exits 0

**Implementation notes**: Import `from services.delivery.app.packager import DeliverablePackager, SAS_HOURS`. Assert `SAS_HOURS == 168`. Mock `azure.storage.blob.BlobServiceClient` and `azure.storage.blob.generate_blob_sas` via `unittest.mock.patch`. In test_sas_uses_account_key call `packager.package_and_upload(...)` with dummy data and assert `generate_blob_sas.call_args.kwargs['account_key']` is not None. For test_sas_expiry_7_days: capture `expiry` kwarg and assert `(expiry - datetime.now(timezone.utc)).total_seconds() > 167 * 3600`.

**Spec references**: `docs/12-IaCscript.md`, `_opus_review_findings_20260227.md` (C-07 entry)

<!-- END STORY: ACA-07-021 -->

---

<!-- STORY: ACA-04-006 -->
## ACA-04-006 -- auth.py MSAL rework: multi-tenant token_service.py

**Size**: M | **Model**: gpt-4o | **Epic**: 4 (API / Auth)

**Context**: auth.py /connect is a 501 stub. This story creates `token_service.py` with MSAL multi-tenant device-code flow, updates settings.py to add `ACA_CLIENT_ID`, and wires the connect endpoint.

**Files**:
- `services/api/app/services/token_service.py` (create)
- `services/api/app/settings.py` (add ACA_CLIENT_ID)
- `services/api/app/routers/auth.py` (add tag ACA-04-006, wire connect to TokenService)

**Acceptance**:
- `token_service.py` created with `TokenService` class (DI pattern: `__init__(self, client_id=None)`)
- `TokenService.initiate_device_code(subscription_id)` returns dict with `device_code`, `verification_uri`, `user_code`, `expires_in`
- MSAL: `PublicClientApplication(client_id, authority='https://login.microsoftonline.com/common')`
- `settings.py` has `ACA_CLIENT_ID: str = Field(default='')` (not required -- so tests work without env)
- `auth.py` POST /connect no longer raises 501; calls `TokenService().initiate_device_code()`
- `token_service.py` has `# EVA-STORY: ACA-04-006` tag
- `auth.py` has `# EVA-STORY: ACA-04-006` tag added
- Unit test in `services/tests/test_token_service.py`: mocks `msal.PublicClientApplication`, confirms `initiate_device_code` returns expected dict keys
- `pytest services/tests/test_token_service.py` exits 0

**Implementation notes**: `token_service.py`: `import msal`. DI: `__init__(self, client_id=None)` sets `self.client_id = client_id or get_settings().ACA_CLIENT_ID`. `initiate_device_code`: `app = msal.PublicClientApplication(self.client_id, authority='https://login.microsoftonline.com/common')`. `flow = app.initiate_device_flow(scopes=['https://management.azure.com/.default'])`. Return `{'device_code': flow['device_code'], 'verification_uri': flow['verification_uri'], 'user_code': flow['message'], 'expires_in': flow['expires_in']}`. For tests: `TokenService(client_id='test-client-id')` -- no env vars needed. Mock `msal.PublicClientApplication` with `return_value.initiate_device_flow.return_value = {'device_code': 'dc', 'verification_uri': 'https://aka.ms/devicelogin', 'message': 'ABC', 'expires_in': 900}`.

**Spec references**: `docs/02-preflight.md`, `.github/copilot-instructions.md` P2.5 Pattern 3

<!-- END STORY: ACA-04-006 -->

---

<!-- STORY: ACA-04-002 -->
## ACA-04-002 -- JWT validation FastAPI dependency

**Size**: S | **Model**: gpt-4o | **Epic**: 4 (API / Auth)

**Context**: All authenticated endpoints need a `Depends(verify_token)` guard. Create the dep now so Sprint-03 can wire it onto each route.

**Files**:
- `services/api/app/deps/__init__.py` (create empty)
- `services/api/app/deps/auth.py` (create)
- `services/tests/test_jwt_dep.py` (create)

**Acceptance**:
- `services/api/app/deps/auth.py` created
- `verify_token` is an async FastAPI dependency: `async def verify_token(token: str = Depends(oauth2_scheme)) -> dict`
- Missing / None token raises `HTTPException(status_code=401, detail='Authentication required')`
- Invalid token (JWT decode error) raises `HTTPException(status_code=401, detail='Invalid token')`
- Valid token returns decoded payload dict
- `deps/auth.py` has `# EVA-STORY: ACA-04-002` tag
- `test_jwt_dep.py`: `test_no_token_raises_401` passes
- `test_jwt_dep.py`: `test_invalid_token_raises_401` passes
- `test_jwt_dep.py`: `test_valid_token_returns_payload` passes
- `pytest services/tests/test_jwt_dep.py` exits 0

**Implementation notes**: `deps/auth.py`: `from fastapi.security import OAuth2PasswordBearer`. `oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/token', auto_error=False)`. `import jwt` (PyJWT). Add `PyJWT[cryptography]` to `services/api/requirements.txt` if not present (check first). `verify_token`: if token is None: raise HTTPException(401). Try `payload = jwt.decode(token, options={'verify_signature': False})` -- signature verification deferred to Sprint-03 when JWKS URL is confirmed. Except `jwt.InvalidTokenError`: raise HTTPException(401, 'Invalid token'). Return payload. For DI testability accept optional `token` param: `async def verify_token(token: Optional[str] = Depends(oauth2_scheme)) -> dict`. Tests: use `pytest-asyncio` and `AsyncClient` from httpx or just call the coroutine directly with `asyncio.run`. Test valid: `asyncio.run(verify_token('eyJ...'))` -- mock jwt.decode to return `{'sub': 'test'}`. Test invalid: monkeypatch jwt.decode to raise `jwt.InvalidTokenError`. Test None: call with None.

**Spec references**: `docs/05-technical.md` (JWT validation section)

<!-- END STORY: ACA-04-002 -->

---

<!-- STORY: ACA-04-008 -->
## ACA-04-008 -- POST /v1/auth/connect: device-code + Cosmos clients write

**Size**: M | **Model**: gpt-4o | **Epic**: 4 (API / Auth)

**Context**: Wire the connect endpoint end-to-end: call TokenService, write a pending client record to Cosmos, return device flow to the frontend.

**Files**:
- `services/api/app/routers/auth.py` (implement connect endpoint)
- `services/api/app/db/repos/clients_repo.py` (create with upsert_client)
- `services/tests/test_auth_connect.py` (create)

**Acceptance**:
- `POST /v1/auth/connect` with `connection_mode=delegated` returns `{device_code, verification_uri, user_code, expires_in, subscription_id}` (HTTP 200)
- `POST /v1/auth/connect` with `connection_mode=service_principal` returns HTTP 501
- `clients_repo.py` created with `upsert_client(subscription_id, doc)` using `partition_key=subscription_id` (pattern from `services/api/AGENTS.md` section 2)
- `auth.py` has `# EVA-STORY: ACA-04-008` tag
- `clients_repo.py` has `# EVA-STORY: ACA-04-008` tag
- `test_auth_connect.py`: `test_connect_delegated_returns_device_code` passes
- `test_auth_connect.py`: `test_connect_sp_returns_501` passes
- `pytest services/tests/test_auth_connect.py` exits 0

**Implementation notes**: Update auth.py POST /connect: (1) Add `# EVA-STORY: ACA-04-008` tag. (2) Signature: `async def connect_subscription(req: ConnectRequest, token_svc: Optional[TokenService] = None, clients: Optional[ClientsRepo] = None)`. (3) If `req.connection_mode == 'service_principal'`: raise HTTPException(501, 'SP mode not yet implemented'). (4) `svc = token_svc or TokenService()`. `repo = clients or ClientsRepo()`. (5) `flow = svc.initiate_device_code(req.subscription_id)`. (6) `repo.upsert_client(req.subscription_id, {'subscriptionId': req.subscription_id, 'status': 'pending', 'connectionMode': 'delegated'})`. (7) Return `{**flow, 'subscription_id': req.subscription_id}`. Create `services/api/app/db/repos/clients_repo.py`: `from app.db.cosmos import upsert_item`. `class ClientsRepo: def upsert_client(self, sub_id, doc): upsert_item('clients', doc, partition_key=sub_id)`. Tests: use `fastapi.testclient.TestClient`. Mock `TokenService.initiate_device_code` and `ClientsRepo.upsert_client`. Assert response JSON has `verification_uri`.

**Spec references**: `docs/02-preflight.md`, `docs/05-technical.md`, `services/api/AGENTS.md`

<!-- END STORY: ACA-04-008 -->
