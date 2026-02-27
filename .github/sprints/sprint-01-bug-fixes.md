<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-01",
  "sprint_title": "Bug fixes: findings wire + entitlement revoke + ingest trigger + tests",
  "target_branch": "sprint/01-bug-fixes",
  "epic": "ACA-03",
  "stories": [
    {
      "id": "ACA-03-006",
      "title": "Wire findings.py GET handler: Cosmos reads + gate_findings",
      "wbs": "3.2.1",
      "size": "M",
      "model": "claude-sonnet-4-6",
      "model_rationale": "Cross-service: reads entitlements container, reads findings container, calls gate_findings. Needs to reason about tenant isolation + tier gating together.",
      "epic": "Epic 03 -- Analysis + Epic 04 -- API",
      "files_to_create": [
        "services/api/app/routers/findings.py"
      ],
      "acceptance": [
        "GET /{scan_id} calls query_items('findings', query, params, partition_key=subscription_id)",
        "GET /{scan_id} reads client tier from Cosmos clients container using get_item",
        "GET /{scan_id} calls gate_findings(findings, tier) before returning",
        "Tier 1 response contains only: id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class",
        "Tier 2 response additionally contains: narrative, heuristic_source",
        "Tier 3 response contains all fields including deliverable_template_id",
        "Returns 404 if scan does not exist or status != complete",
        "Returns 403 if subscription_id in request does not match scan.subscriptionId",
        "No unconditional raise HTTPException 404 -- the TODO raise must be replaced with real Cosmos reads",
        "File imports without error"
      ],
      "implementation_notes": "The file services/api/app/routers/findings.py currently has a fully stubbed handler at @router.get('/{scan_id}'). The gate_findings() function is already correctly implemented (lines 22-33) -- DO NOT change it. The ONLY change needed is the handler body: replace the 4 TODO comments + unconditional raise HTTPException(404) with real implementation. Step 1: add imports for get_item and query_items from app.db.cosmos, and import get_settings. Step 2: the handler signature needs subscription_id. Extract it from request.state if using TenantMiddleware, or accept as query param. Look at how other routers in services/api/app/routers/ get subscription_id. Step 3: call get_item('scans', scan_id, partition_key=subscription_id) -- if None, raise 404. If scan['status'] != 'complete', raise 404 with detail='Scan not yet complete'. Step 4: load tier -- call get_item('clients', subscription_id, partition_key=subscription_id) -- default tier='tier1' if client record missing. Read tier from client['tier'] field, format as 'tier1'/'tier2'/'tier3'. Step 5: query findings -- call query_items('findings', 'SELECT * FROM c WHERE c.scanId = @s', [{'name': '@s', 'value': scan_id}], partition_key=subscription_id). Step 6: return gate_findings(raw_findings, tier). CRITICAL tenant isolation rule: always pass partition_key=subscription_id to every Cosmos call. Never query across tenants. The EVA-STORY tag ACA-04-013 is on line 1 -- keep it, do not replace it with ACA-03-006 (one tag per file is fine)."
    },
    {
      "id": "ACA-06-018",
      "title": "entitlement_service.py revoke() -- preserve Tier 3 on subscription.deleted",
      "wbs": "6.3.5",
      "size": "XS",
      "model": "claude-sonnet-4-6",
      "model_rationale": "Revenue safety bug -- wrong logic for Tier 3 permanent purchases.",
      "epic": "Epic 06 -- Billing",
      "files_to_create": [
        "services/api/app/services/entitlement_service.py"
      ],
      "acceptance": [
        "revoke() reads existing.tier before writing",
        "If existing.tier >= 3 and existing.payment_status is not 'canceled', tier stays 3 (Tier 3 one-time purchase survives subscription.deleted)",
        "If existing.tier < 3, tier is set to 1 as before",
        "payment_status is always set to 'canceled' regardless of tier",
        "grant_tier2() and grant_tier3() are unchanged",
        "File imports without error"
      ],
      "implementation_notes": "The file services/api/app/services/entitlement_service.py has a revoke() method (near the bottom, last method defined). The current code sets tier=1 unconditionally on every subscription.deleted event. This destroys a Tier 3 one-time purchase when a Tier 2 subscription is canceled separately. Fix: change the revoke() method body to read existing tier first: existing = self.get(subscription_id). Then determine new_tier: if existing is not None and existing.tier >= 3: new_tier = 3 (preserve permanent Tier 3 -- subscription.deleted only cancels recurring Tier 2 subscriptions, Tier 3 is a one-time buy). Else: new_tier = 1. Then call self._repo.upsert with tier=new_tier (not hardcoded 1). Keep payment_status='canceled' -- the payment IS canceled, but the access tier is preserved for Tier 3. Look at the existing revoke() implementation carefully: it currently has tier=1 hardcoded. Change that single line to use new_tier. Do NOT change any other method. The file is ~117 lines -- rewrite it in full with only this one-line change in revoke(). All other code must be identical to the current file. EVA-STORY tag is on line 1 or 2 -- keep it."
    },
    {
      "id": "ACA-04-028",
      "title": "cosmos.py upsert_item -- add partition_key parameter",
      "wbs": "4.5.1",
      "size": "XS",
      "model": "claude-sonnet-4-6",
      "model_rationale": "Tenant isolation critical path. Wrong fix here breaks every write across all services.",
      "epic": "Epic 03 -- Analysis, Epic 01 -- Foundation",
      "files_to_create": [
        "services/api/app/db/cosmos.py"
      ],
      "acceptance": [
        "upsert_item(container_name, item, partition_key) has partition_key as required parameter",
        "container.upsert_item(item, partition_key=partition_key) is called with the explicit partition_key kwarg",
        "All other functions (get_item, query_items, ensure_containers) are unchanged",
        "File imports without error"
      ],
      "implementation_notes": "The file services/api/app/db/cosmos.py has a upsert_item function (around line 44) with signature: def upsert_item(container_name: str, item: dict) -> dict. The function currently calls container.upsert_item(item) without a partition_key argument. This is a Cosmos SDK bug: without partition_key, the SDK infers it from the item dict but this is unreliable. Fix: add partition_key: str as a third required parameter. Change the call to: return container.upsert_item(item, partition_key=partition_key). Also add a comment: '# partition_key MUST be supplied -- enforces tenant isolation'. The change is 2 lines only. Rewrite the full file (83 lines) with only this change. All other code must be identical. Do NOT change get_item, query_items, ensure_containers, get_container, get_cosmos_client. EVA-STORY tag ACA-01-001 is on line 2 inside docstring -- keep it."
    },
    {
      "id": "ACA-02-017",
      "title": "ingest.py mark_collection_complete -- trigger analysis Container App Job",
      "wbs": "2.5.4",
      "size": "S",
      "model": "claude-sonnet-4-6",
      "model_rationale": "Involves Azure Container Apps Jobs API -- needs Azure SDK pattern knowledge.",
      "epic": "Epic 02 -- Data Collection, Epic 03 -- Analysis",
      "files_to_create": [
        "services/collector/app/ingest.py"
      ],
      "acceptance": [
        "mark_collection_complete() calls a trigger function after setting status='collected'",
        "_trigger_analysis_job() is implemented and calls the Azure Container Apps Jobs API",
        "ACA_ANALYSIS_JOB_NAME and ACA_RESOURCE_GROUP are read from os.environ",
        "If ACA_ANALYSIS_JOB_NAME is empty/missing, trigger is skipped with a warning log (graceful degradation for CI)",
        "Trigger uses DefaultAzureCredential from azure.identity",
        "Trigger uses ContainerAppsAPIClient from azure.mgmt.appcontainers if available, else falls back to subprocess az containerapp job start",
        "No crash if azure.mgmt.appcontainers is not installed (try/except ImportError -> subprocess fallback)",
        "File imports without error"
      ],
      "implementation_notes": "The file services/collector/app/ingest.py has mark_collection_complete() as the last method. It sets status='collected' in Cosmos but then does nothing -- the analysis job never runs. Fix: add a call to self._trigger_analysis_job(scan_id=self.scan_id, subscription_id=self.sub_id) AFTER the upsert_item call. Implement _trigger_analysis_job as a separate private method. Pattern: read ACA_ANALYSIS_JOB_NAME = os.environ.get('ACA_ANALYSIS_JOB_NAME', '') and ACA_SUBSCRIPTION_ID = os.environ.get('ACA_SUBSCRIPTION_ID', '') and ACA_RESOURCE_GROUP = os.environ.get('ACA_RESOURCE_GROUP', ''). If any are empty, log '[WARN] ACA_ANALYSIS_JOB_NAME not set -- skipping analysis trigger' and return. Then try to import ContainerAppsAPIClient from azure.mgmt.appcontainers. If import succeeds: use DefaultAzureCredential() + ContainerAppsAPIClient to call jobs.start(resource_group_name, job_name, properties={'template': {'containers': [{'name': 'analysis', 'env': [{'name': 'SCAN_ID', 'value': scan_id}, {'name': 'SUBSCRIPTION_ID', 'value': subscription_id}]}]}}). If import fails: use subprocess to call ['az', 'containerapp', 'job', 'start', '--name', job_name, '--resource-group', resource_group, '--environment-variables', f'SCAN_ID={scan_id} SUBSCRIPTION_ID={subscription_id}']. Wrap the trigger call in try/except and log any error without raising -- collection must not fail because of a trigger failure. Keep all other existing methods (save_resources, save_cost_data, save_advisor, save_policy, save_network) exactly as-is. Keep EVA-STORY tag."
    },
    {
      "id": "ACA-03-033",
      "title": "Minimum test suite: checkout router + findings gate + packager SAS",
      "wbs": "3.4.14",
      "note": "ACA-03-033 in veritas = FindingsAssembler unit test -- this sprint story covers the broader test suite including checkout/gate/packager/entitlement.",
      "size": "M",
      "model": "claude-sonnet-4-6",
      "model_rationale": "Needs to understand all 4 fixed services to write meaningful tests.",
      "epic": "Epic 03 -- Analysis, Epic 06 -- Billing, Epic 07 -- Delivery",
      "files_to_create": [
        "services/tests/__init__.py",
        "services/tests/test_checkout_router.py",
        "services/tests/test_findings_gate.py",
        "services/tests/test_packager_sas.py",
        "services/tests/test_entitlement_revoke.py"
      ],
      "acceptance": [
        "pytest services/tests/ -v exits 0",
        "test_checkout_router.py: imports checkout.router and asserts len(router.routes) == 5",
        "test_checkout_router.py: asserts route paths include /tier2, /tier3, /webhook, /portal, /entitlements",
        "test_checkout_router.py: asserts exactly one route has path /webhook",
        "test_findings_gate.py: asserts gate_findings(full_finding, 'tier1') contains only TIER1_FIELDS",
        "test_findings_gate.py: asserts 'narrative' NOT in tier1 result",
        "test_findings_gate.py: asserts 'deliverable_template_id' NOT in tier1 result",
        "test_findings_gate.py: asserts gate_findings(full_finding, 'tier2') contains narrative but not deliverable_template_id",
        "test_findings_gate.py: asserts gate_findings(full_finding, 'tier3') returns full finding unchanged",
        "test_packager_sas.py: asserts packager.SAS_HOURS == 168",
        "test_packager_sas.py: asserts 'account_key' not in inspect.getsource(Packager.generate_sas_url) (no account_key kwarg)",
        "test_packager_sas.py: asserts 'user_delegation_key' in inspect.getsource(Packager.generate_sas_url)",
        "test_entitlement_revoke.py: mock EntitlementRepo; call revoke() with existing.tier=3; assert tier stays 3 in upsert call",
        "test_entitlement_revoke.py: mock EntitlementRepo; call revoke() with existing.tier=2; assert tier becomes 1 in upsert call",
        "No test makes a real network call (all Cosmos / Stripe calls mocked with unittest.mock)"
      ],
      "implementation_notes": "Create services/tests/ as a new directory. All test files use pytest (not unittest). Each test file starts with '# EVA-STORY: ACA-03-033'. Use unittest.mock.patch and MagicMock for all external calls. test_checkout_router.py: 'from services.api.app.routers.checkout import router' -- note the sys.path insertion needed: 'import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), \"..\", \"api\"))' before the import so 'from app.routers.checkout import router' works. Then check router.routes count == 5 and check that [r.path for r in router.routes] contains the 5 expected paths. test_findings_gate.py: import gate_findings and TIER1_FIELDS and TIER2_FIELDS directly from the findings module (no Cosmos calls needed -- these are pure functions). Make a full_finding dict containing all fields: id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class, narrative, heuristic_source, deliverable_template_id, evidence_refs. Assert tier1 strips to only id/category/title/estimated_saving_low/estimated_saving_high/effort_class/risk_class. test_packager_sas.py: import SAS_HOURS constant and Packager class. Use inspect.getsource to check the source of the generate_sas_url method to confirm no account_key param and user_delegation_key is present. test_entitlement_revoke.py: mock the EntitlementRepo using MagicMock. Set mock_repo.get.return_value = MagicMock(tier=3, stripe_customer_id=None, stripe_subscription_id=None). Create EntitlementService(repo=mock_repo). Call revoke('sub-123'). Then check mock_repo.upsert.call_args to verify tier=3 was passed (not tier=1). Second test: mock with tier=2 and assert tier=1 in upsert call."
    }
  ]
}
-->

## Sprint 01: Bug Fixes -- Findings Wire + Entitlement Revoke + Ingest Trigger + Tests

**Type**: Bug fix sprint -- 4 blocking defects + minimum test coverage
**Branch**: sprint/01-bug-fixes
**Trigger**: sprint-task label
**Date**: 2026-02-27

### Context

Sprint-00 fixed the 3 pre-flight bugs (checkout dup router, cosmos_client missing,
SAS_HOURS=24). This sprint fixes the next 4 bugs identified in the Opus review
plus adds the test suite that was at zero.

### Stories

| ID | File | Bug / Feature | Size |
|---|---|---|---|
| ACA-03-006 | services/api/app/routers/findings.py | Wire Cosmos reads + gate_findings into handler | M |
| ACA-06-018 | services/api/app/services/entitlement_service.py | revoke() must preserve Tier 3 on subscription.deleted | XS |
| ACA-04-028 | services/api/app/db/cosmos.py | upsert_item missing partition_key parameter | XS |
| ACA-02-017 | services/collector/app/ingest.py | mark_collection_complete must trigger analysis Container App Job | S |
| ACA-03-033 | services/tests/ (new dir) | Minimum test suite: checkout router + findings gate + packager + entitlement | M |

### Dependency Order

All 4 bug fixes are independent. Tests must run after all 4 fixes are applied.
Agent should execute in the order listed: ACA-03-006, ACA-06-018, ACA-04-028,
ACA-02-017, then ACA-03-033.

### Definition of Done

- [ ] pytest services/ -x -q exits 0
- [ ] ruff check services/ exits 0
- [ ] findings.py GET handler no longer raises 404 unconditionally
- [ ] entitlement_service.py revoke() preserves tier=3 if tier3_purchased
- [ ] cosmos.py upsert_item accepts partition_key parameter
- [ ] ingest.py mark_collection_complete calls _trigger_analysis_job
- [ ] services/tests/ directory exists with 4 test files
- [ ] All 4 test files pass with pytest

### Notes

ACA-03-006 is the highest business impact: without it, no findings are ever
returned to any client. The endpoint raises 404 on every request regardless of
scan state. gate_findings() is already correctly implemented -- only the handler
body needs to be wired.

ACA-06-018 is a revenue safety bug: a customer who paid CAD $1,499 one-time for
Tier 3 loses their access if their later Tier 2 subscription is canceled.

ACA-04-028 is a data integrity bug: without an explicit partition_key on upsert,
the Cosmos SDK infers it from the item dict. This works for well-structured items
but fails silently if the partition key field is missing or differently named.

ACA-02-017 closes the analysis pipeline gap: without the analysis job trigger,
scans sit at status=collected forever and no findings are ever produced.

### Spec References

- docs/05-technical.md -- full API spec for findings endpoint
- docs/08-payment.md -- Stripe tier unlock flow (Tier 3 permanence)
- copilot-instructions.md P2.5 Pattern 1 (tenant isolation)
- copilot-instructions.md P2.5 Pattern 2 (tier gating)
