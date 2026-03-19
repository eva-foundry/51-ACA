# PLAN-01: Foundation, Collection, and Analysis (Epics 1-3)

**Module**: PLAN-01  
**Epics**: 1 (Foundation), 2 (Collection), 3 (Analysis)  
**Stories**: 71 total (21 + 17 + 33)  
**Function Points**: 290 (65 + 70 + 155)

---

## Epic 1: Foundation and Infrastructure

**Goal**: All four services boot cleanly. Local dev stack works. Phase 1 infra wired.  
**Status**: DONE  
**Stories**: 21  
**Function Points**: 65

---

## Feature 1.1: Local dev environment

### Story ACA-01-001: Docker Compose startup
As a developer I can run `docker-compose up` and all services start without error

**Acceptance**: All 4 services (api, collector, analysis, delivery) show "ready" in logs

### Story ACA-01-002: Test suite execution
As a developer I can run `pytest services/ -x -q` and all tests pass

**Acceptance**: Exit code 0, no test failures, coverage report generated

### Story ACA-01-003: Health endpoint verification
As a developer I can hit http://localhost:8080/health and get status=ok

**Acceptance**: HTTP 200, JSON response with status and version fields

### Story ACA-01-004: Data model API connectivity
As a developer I can query the central data model (port 8010, managed by project 37)

**Acceptance**: `GET /model/projects/51-ACA` returns project metadata

### Story ACA-01-005: Environment template completeness
As a developer I can use the .env.example as a complete checklist

**Acceptance**: All required env vars documented with examples and descriptions

---

## Feature 1.2: CI pipeline

### Story ACA-01-006: Lint enforcement
As a developer, every PR triggers ruff lint. Zero lint errors = green.

**Acceptance**: GitHub Actions workflow runs ruff, blocks merge on violations

### Story ACA-01-007: Type checking
As a developer, every PR triggers mypy type check. No unresolved types.

**Acceptance**: mypy --strict passes on all Python files

### Story ACA-01-008: Test execution gate
As a developer, every PR triggers pytest. No test failures = merge allowed.

**Acceptance**: pytest runs all tests, coverage > 80%, blocks merge on failure

### Story ACA-01-009: Accessibility check
As a developer, main branch push triggers axe-core a11y check on frontend.

**Acceptance**: Playwright + axe-core runs, zero critical/serious violations

---

## Feature 1.3: Phase 1 marco* infra wiring

### Story ACA-01-010: Cosmos containers provisioning
As an operator I can run infra/phase1-marco/main.bicep and get 11 Cosmos containers

**Acceptance**: All 11 containers exist: scans, inventories, cost-data, advisor, findings, clients, deliverables, entitlements, payments, stripe_customer_map, admin_audit_events

### Story ACA-01-011: Key Vault secrets configuration
As an operator all secrets are in msubsandkv202603031449 (no .env in production)

**Acceptance**: 10+ secrets stored: COSMOS_KEY, STRIPE_SECRET_KEY, admin-token, etc.

### Story ACA-01-012: Managed identity approval
As an operator the API Container App has managed identity approved on KV

**Acceptance**: API can read secrets via managed identity, no access key in config

### Story ACA-01-013: Collector job identity
As an operator the collector job has managed identity with Cosmos read/write

**Acceptance**: Collector can write to all 11 containers without connection string

### Story ACA-01-014: OIDC configuration
As an operator OIDC is configured on the GitHub Actions workflow for EsDAICoE-Sandbox

**Acceptance**: deploy-phase1.yml authenticates via federated credential, no PAT

### Story ACA-01-015: Bootstrap script completeness
As an operator infra/phase1-marco/bootstrap.sh exists and provisions all marco* ACA resources in sequence (Cosmos containers, KV secrets, ACA env, Container App + 3 jobs, APIM product) using az CLI with DO_* toggle flags (DO_CONTAINERAPPS, DO_APIM) for partial re-runs

**Acceptance**: Script runs idempotently, supports --dry-run, logs all operations

---

## Feature 1.4: Container build and push

### Story ACA-01-016: Dockerfile build verification
As a developer all 4 Dockerfiles build without error on ubuntu-latest

**Acceptance**: `docker build` succeeds for api, collector, analysis, delivery

### Story ACA-01-017: ACR image push
As an operator deploy-phase1.yml pushes 4 images to msubsandacr202603031449

**Acceptance**: Images tagged with git SHA, latest tag updated

### Story ACA-01-018: Scheduled collector trigger
As an operator collector-schedule.yml triggers nightly at 02:00 UTC

**Acceptance**: GitHub Actions cron schedule fires, job runs successfully

---

## Feature 1.5: Phase 1 deployment URLs

### Story ACA-01-019: Environment-driven URLs
As an operator PUBLIC_APP_URL and PUBLIC_API_URL are read from env vars; no URLs are hardcoded in source. Phase 1 = Azure free hostnames (*.{region}.azurecontainerapps.io). No custom domain required.

**Acceptance**: Grep source for hardcoded URLs returns zero matches

### Story ACA-01-020: URL documentation
As a developer .env.example documents the Azure free hostname pattern with a placeholder comment and instructions to update on first deploy.

**Acceptance**: .env.example has PUBLIC_APP_URL with example and instructions

### Story ACA-01-021: CORS origin injection
As an operator ACA_ALLOWED_ORIGINS is seeded from the Phase 1 free hostname on container startup via environment variable injection from KV.

**Acceptance**: API logs show allowed origins loaded from env, CORS headers present

---

## Epic 2: Data Collection Pipeline

**Goal**: Collector job runs against a real Azure subscription and saves data to Cosmos.  
**Status**: DONE  
**Stories**: 17  
**Function Points**: 70

---

## Feature 2.1: Pre-flight validation

### Story ACA-02-001: Capability probe status display
As a client using Mode A (delegated) I see a PASS/FAIL/WARN status for each of the 5 capability probes before collection starts

**Acceptance**: UI shows 5 probes: identity, RBAC, inventory, cost, advisor with color-coded status

### Story ACA-02-002: Missing role error messaging
As a client with missing Cost Management Reader role I see a clear error message naming the missing role and linking to the access guide

**Acceptance**: Error message includes role name, subscription ID, link to docs/client-access-guide.md

### Story ACA-02-003: Warning tolerance
As a client with PASS_WITH_WARNINGS I can still proceed with collection and the warnings are recorded in the scan record

**Acceptance**: Warnings stored in Cosmos scan record, collection proceeds

### Story ACA-02-004: Preflight-only mode
As an operator I can pass --preflight-only to the collector to validate without collecting

**Acceptance**: Collector exits after probes, no data written to Cosmos

---

## Feature 2.2: Resource inventory

### Story ACA-02-005: Resource Graph query performance
As the system I collect all Azure resources via Resource Graph in < 60s for a subscription with up to 500 resources

**Acceptance**: Query completes in < 60s, all resources returned

### Story ACA-02-006: Inventory persistence
As the system I save inventory to Cosmos with partition_key=subscriptionId

**Acceptance**: inventories container has documents partitioned by subscription

### Story ACA-02-007: Resource metadata capture
As the system I capture: resource type, name, SKU, region, resource group, tags

**Acceptance**: Inventory documents contain all 6 fields with correct types

---

## Feature 2.3: Cost data

### Story ACA-02-008: Cost history collection
As the system I collect 91 days of daily cost rows via Cost Management Query API

**Acceptance**: cost-data container has >= 91 documents per subscription

### Story ACA-02-009: Cost data schema
As the system I capture: date, MeterCategory, MeterName, resourceGroup, resourceId (hashed), PreTaxCost in subscription currency

**Acceptance**: Cost documents match schema, amounts are numeric

### Story ACA-02-010: Rate limiting resilience
As the system I handle rate limiting (429) with exponential backoff + retry

**Acceptance**: Collector logs show retry attempts, eventual success after 429

---

## Feature 2.4: Advisor, Policy, Network

### Story ACA-02-011: Advisor recommendations collection
As the system I collect all Advisor recommendations across all categories

**Acceptance**: advisor container has documents for all 5 categories (cost, security, reliability, performance, operational excellence)

### Story ACA-02-012: Policy compliance collection
As the system I collect Policy compliance state (compliant / non-compliant counts)

**Acceptance**: Scan record includes policyCompliantCount and policyNonCompliantCount

### Story ACA-02-013: Network signals collection
As the system I collect network signals: NSG rule counts, private DNS zones, public IP count, VNet peering map

**Acceptance**: Scan record includes networkSignals object with 4 fields

---

## Feature 2.5: Collection lifecycle

### Story ACA-02-014: Scan status updates
As the system I update scan status in Cosmos: queued -> running -> succeeded/failed

**Acceptance**: Scan status transitions logged, timestamps recorded

### Story ACA-02-015: Collection statistics
As the system I write stats to the scan record (inventoryCount, costRows, advisorRecs)

**Acceptance**: Scan record has stats object with all counts

### Story ACA-02-016: Status polling endpoint
As the API I expose GET /v1/scans/:scanId so the frontend can poll status

**Acceptance**: Endpoint returns current status, progress percentage, stats

### Story ACA-02-017: Analysis trigger automation
As the system, after mark_collection_complete sets status=collected, the analysis Container App Job is triggered automatically (via azure.mgmt.appcontainers or az CLI fallback). If ACA_ANALYSIS_JOB_NAME is not set, the trigger is skipped with a warning and collection still succeeds (graceful degradation for CI). Without this trigger no findings are ever produced -- scans stay at status=collected.

**Acceptance**: Analysis job starts within 30s of collection complete, or warning logged if disabled

---

## Epic 3: Analysis Engine and Rules

**Goal**: Analysis engine runs all 12 rules and persists tiered findings to Cosmos.  
**Status**: PARTIAL  
**Stories**: 33  
**Function Points**: 155

---

## Feature 3.1: Rule engine

### Story ACA-03-001: Rule loading and execution
As the system I load all 12 rules from ALL_RULES and run each in sequence

**Status**: DONE (Sprint-06, merged PR #24)  
**Acceptance**: Engine discovers 12 rule modules, executes each, logs results

### Story ACA-03-002: Rule isolation
As the system I handle a rule failure in isolation (one rule crash does not stop the engine; the error is logged and that rule is skipped)

**Status**: DONE (Sprint-04, merged PR #19)  
**Acceptance**: Engine continues after rule exception, final status = partial success

### Story ACA-03-003: Finding persistence
As the system I persist each Finding to Cosmos with full schema: id, category, title, estimated_saving_low, estimated_saving_high, effort_class, risk_class, heuristic_source, narrative, deliverable_template_id, evidence_refs

**Status**: DONE (Sprint-04, merged PR #19)  
**Acceptance**: findings container documents match schema, all fields present

### Story ACA-03-004: Analysis run status management
As the system I update AnalysisRun status: queued -> running -> succeeded/failed

**Status**: DONE (Sprint-05, merged PR #22)  
**Acceptance**: Status transitions logged, timestamps accurate

### Story ACA-03-005: Findings summary generation
As the system I write findingsSummary to the analysis run record (findingCount, totalSavingLow, totalSavingHigh, categories[])

**Status**: DONE (Sprint-05, merged PR #22)  
**Acceptance**: Summary object calculated correctly, matches finding aggregation

---

## Feature 3.2: Tier gating

### Story ACA-03-006: Tier 1 field filtering
As a Tier 1 client calling GET /v1/findings/:scanId I receive findings with category, title, estimated_saving_low, estimated_saving_high only

**Status**: DONE (Sprint-01, merged PR #11)  
**Acceptance**: Response excludes narrative, deliverable_template_id

### Story ACA-03-007: Tier 1 security enforcement
As a Tier 1 client I do not receive narrative or deliverable_template_id even if they are stored in Cosmos

**Status**: DONE (Sprint-05, merged PR #22)  
**Acceptance**: API filters fields before response, Cosmos documents unchanged

### Story ACA-03-008: Tier 2 narrative access
As a Tier 2 client I receive the full finding including narrative and evidence_refs but not deliverable_template_id

**Status**: DONE (Sprint-06, merged PR #24)  
**Acceptance**: Response includes narrative, excludes deliverables

### Story ACA-03-009: Tier 3 full access
As a Tier 3 client I receive the full finding including deliverable_template_id

**Status**: DONE (Sprint-06, merged PR #24)  
**Acceptance**: Response includes all fields, no filtering

### Story ACA-03-010: Red-team tier bypass prevention
As the red-team agent I can assert that Tier 1 tokens never leak narrative or deliverable_template_id fields (redteam-agent.yaml gate)

**Status**: DONE (Sprint-07, merged PR #29)  
**Acceptance**: Automated test fails if Tier 1 response contains restricted fields

---

## Feature 3.3: Individual rules (R-01 through R-12)

### Story ACA-03-011: R-01 Dev Box auto-stop
R-01 Dev Box auto-stop: returns finding when annual Dev Box cost > $1,000

**Status**: DONE (Sprint-04, merged PR #19)  
**Threshold**: Annual Dev Box cost > $1,000  
**Category**: Compute  
**Template**: tmpl-devbox-autostop

### Story ACA-03-012: R-02 Log retention
R-02 Log retention: returns finding when annual LA cost > $500 in non-prod

**Status**: DONE (Sprint-07, merged PR #29)  
**Threshold**: Annual Log Analytics cost > $500 (non-prod environments)  
**Category**: Observability  
**Template**: tmpl-log-retention

### Story ACA-03-013: R-03 Defender mismatch
R-03 Defender mismatch: returns finding when annual Defender cost > $2,000

**Status**: DONE (Sprint-07, merged PR #29)  
**Threshold**: Annual Defender cost > $2,000  
**Category**: Security  
**Template**: tmpl-defender-plan

### Story ACA-03-014: R-04 Compute scheduling
R-04 Compute scheduling: returns finding when annual schedulable compute > $5,000

**Status**: DONE (Sprint-07, merged PR #29)  
**Threshold**: Annual schedulable compute > $5,000  
**Category**: Compute  
**Template**: tmpl-compute-schedule

### Story ACA-03-015: R-05 Anomaly detection
R-05 Anomaly detection: returns finding for each category with z-score > 3.0

**Status**: DONE (Sprint-08, merged PR #31)  
**Threshold**: Category z-score > 3.0  
**Category**: FinOps  
**Template**: tmpl-anomaly-alert

### Story ACA-03-016: R-06 Stale environments
R-06 Stale environments: returns finding when >= 3 App Service sites exist

**Status**: DONE (Sprint-08, merged PR #31)  
**Threshold**: >= 3 App Service sites  
**Category**: Waste  
**Template**: tmpl-stale-envs

### Story ACA-03-017: R-07 Search SKU oversize
R-07 Search SKU oversize: returns finding when annual Search cost > $2,000

**Status**: DONE (Sprint-08, merged PR #31)  
**Threshold**: Annual Search cost > $2,000  
**Category**: Data  
**Template**: tmpl-search-sku

### Story ACA-03-018: R-08 ACR consolidation
R-08 ACR consolidation: returns finding when >= 3 registries exist

**Status**: DONE (Sprint-08, merged PR #31)  
**Threshold**: >= 3 ACR registries  
**Category**: Infrastructure  
**Template**: tmpl-acr-consolidation

### Story ACA-03-019: R-09 DNS sprawl
R-09 DNS sprawl: returns finding when annual DNS cost > $1,000

**Status**: DONE (Sprint-004-Batch-1, merged PR #43, Issue #39 closed)  
**Threshold**: Annual DNS cost > $1,000  
**Category**: Networking  
**Template**: tmpl-dns-consolidation

### Story ACA-03-020: R-10 Savings plan
R-10 Savings plan: returns finding when annual total compute > $20,000

**Status**: DONE (Sprint-004-Batch-1, merged PR #43, Issue #39 closed)  
**Threshold**: Annual compute > $20,000  
**Category**: Commitment  
**Template**: tmpl-savings-plan

### Story ACA-03-021: R-11 APIM token budget
R-11 APIM token budget: returns finding when APIM + OpenAI both present

**Status**: DONE (Sprint-004-Batch-1, merged PR #43, Issue #39 closed)  
**Threshold**: APIM + OpenAI both present  
**Category**: Risk  
**Template**: tmpl-apim-token-budget

### Story ACA-03-022: R-12 Chargeback gap
R-12 Chargeback gap: returns finding when total period cost > $5,000

**Status**: DONE (Sprint-004-Batch-1, merged PR #43, Issue #39 closed)  
**Threshold**: Total period cost > $5,000  
**Category**: Governance  
**Template**: tmpl-chargeback-policy

---

## Feature 3.4: Rule unit tests (95% coverage target)

### Story ACA-03-023: R-01 unit test
Unit test for R-01 devbox_autostop: fixture with Dev Box cost > $1,000 -> finding

**Status**: DONE (test_r01_devbox.py, 3 tests passing)  
**Acceptance**: Test file exists, 3+ test cases, 95%+ coverage

### Story ACA-03-024: R-02 unit test
Unit test for R-02 log_retention: fixture with LA cost > $500 -> finding

**Status**: DONE (test_r02_log_retention.py, 3 tests passing)

### Story ACA-03-025: R-03 unit test
Unit test for R-03 defender_mismatch: fixture with Defender cost > $2,000 -> finding

**Status**: DONE (test_r03_defender.py, 3 tests passing)

### Story ACA-03-026: R-04 unit test
Unit test for R-04 compute_scheduling: fixture with schedulable > $5,000 -> finding

**Status**: DONE (test_r04_compute.py, 3 tests passing)

### Story ACA-03-027: R-05 unit test
Unit test for R-05 anomaly_detection: fixture with z-score > 3.0 -> finding

**Status**: DONE (test_r05_anomaly.py, 3 tests passing)

### Story ACA-03-028: R-06 unit test
Unit test for R-06 stale_environments: fixture with >= 3 App Services -> finding

**Status**: DONE (test_r06_stale.py, 3 tests passing)

### Story ACA-03-029: R-07 unit test
Unit test for R-07 search_sku_oversize: fixture with Search cost > $2,000 -> finding

**Status**: DONE (test_r07_search.py, 3 tests passing)

### Story ACA-03-030: R-08 unit test
Unit test for R-08 acr_consolidation: fixture with >= 3 registries -> finding

**Status**: DONE (test_r08_acr.py, 3 tests passing)

### Story ACA-03-031: R-09 unit test
Unit test for R-09 dns_sprawl: fixture with DNS cost > $1,000 -> finding

**Status**: DONE (Sprint-004-Batch-1, 5 tests in test_r09_dns_sprawl.py, merged PR #43)

### Story ACA-03-032: R-10 unit test
Unit test for R-10 savings_plan_coverage: fixture with compute > $20,000 -> finding

**Status**: DONE (Sprint-004-Batch-1, 4 tests in test_r10_savings_plan.py, merged PR #43)

### Story ACA-03-033: R-11 unit test
Unit test for R-11 apim_token_budget: fixture with APIM + OpenAI -> finding

**Status**: DONE (Sprint-004-Batch-1, 5 tests in test_r11_apim_token.py, merged PR #43)

### Story ACA-03-034: R-12 unit test
Unit test for R-12 chargeback_gap: fixture with total cost > $5,000 -> finding

**Status**: DONE (Sprint-004-Batch-1, 5 tests in test_r12_chargeback.py, merged PR #43)

### Story ACA-03-035: Negative test coverage
Negative tests for each rule: below-threshold fixture -> no finding returned

**Status**: DONE (test_negative_batch_1.py + test_negative_batch_2.py, 12 tests, all 12 rules covered)  
**Acceptance**: Each rule has at least one negative test case

### Story ACA-03-036: FindingsAssembler unit test
FindingsAssembler unit test: mock rule list -> correct Cosmos upsert payload

**Status**: DONE (Sprint-01, merged PR #11)  
**Acceptance**: Test verifies payload structure, partition key, required fields

---

**End of PLAN-01** -- Continue to [PLAN-02.md](PLAN-02.md) for Epics 4-6
