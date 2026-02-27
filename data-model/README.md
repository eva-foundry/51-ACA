ACA Data Model
==============

Isolated EVA Data Model instance for project 51-ACA (Azure Cost Advisor).
Port: 8011 (isolated from EVA POC shared instance on 8010).

=============================================================================
DUAL PURPOSE
=============================================================================

This data model serves TWO purposes:

1. BUILD-TIME: Source of truth for the WBS, epics, features, and user stories
   that drive the ACA development process. Every story in PLAN.md is seeded
   here. Agents read and update story status as work progresses.

2. RUNTIME: Source of truth for the ACA app itself at runtime -- feature
   flags, enabled/disabled analysis rules, endpoint metadata, Cosmos container
   schema, service health, and agent configuration.

=============================================================================
STRUCTURE
=============================================================================

data-model/
  model/               <- layer JSON files (source of truth, git-checked-in)
    services.json      <- 5 ACA services (api, collector, analysis, delivery, frontend)
    endpoints.json     <- 25+ API endpoints with auth, tier, and impl info
    containers.json    <- 10 Cosmos containers with partition keys and field schemas
    agents.json        <- 4 AI agents (collection, analysis, generation, redteam)
    screens.json       <- 10 frontend screens with route, auth, and API calls
    hooks.json         <- React hooks with endpoints they call
    rules.json         <- 12 analysis rules with status, threshold, category
    integrations.json  <- 6 third-party integrations (Stripe, GA4, Clarity, GTM, MSAL, Azure SDK)
    i18n.json          <- 5 locale definitions with translation completeness status
    epics.json         <- 12 epics from PLAN.md
    features.json      <- 50+ features (one story block per feature)
    stories.json       <- 100+ user stories with status and epic/feature refs
    currencies.json    <- 5 supported currencies with display format
    settings.json      <- runtime config keys (feature flags, thresholds, TTLs)
    ...                <- remaining 15 EVA standard layers (empty, grow as needed)
  start.ps1            <- launcher: runs on port 8011
  README.md            <- this file

=============================================================================
HOW TO START
=============================================================================

Start the data model server:

  pwsh C:\AICOE\eva-foundry\51-ACA\data-model\start.ps1

Then seed from JSON files:

  $b = "http://localhost:8011"
  Invoke-RestMethod "$b/model/admin/seed" -Method POST `
    -Headers @{"Authorization"="Bearer dev-admin"}

Quick health check:

  Invoke-RestMethod "$b/health"
  Invoke-RestMethod "$b/model/agent-summary"

=============================================================================
LAYER REFERENCE -- ALL 27 LAYERS
=============================================================================

Layer             Description                              Priority   Count*
----------------  ---------------------------------------  ---------  ------
services          ACA microservices (api, collector, etc)  core       5
endpoints         All API endpoints with tier/auth/impl    core       25+
containers        Cosmos DB containers + partition keys    core       10
agents            29-foundry agent YAML definitions        core       4
screens           Frontend pages + routes + API calls      core       10
hooks             React hooks + endpoints they call        high       10+
rules             Analysis rules (12 heuristics)           core       12
integrations      Third-party integrations                 high       6
i18n              Locale definitions + completeness        high       5
epics             WBS epics from PLAN.md                   build      12
features          WBS features from PLAN.md                build      50+
stories           User stories with status tracking        build      100+
currencies        Supported currencies + formats           high       5
settings          Runtime feature flags + config keys      core       20+
(standard layers: functions, events, roles, permissions, tags, health,
                  schedules, jobs, alerts, policies, reports, templates,
                  workflows, pipelines, infrastructure)

* Count is seeded target. Use GET /model/agent-summary for live count.

=============================================================================
BUILD-TIME USAGE -- STORY STATUS TRACKING
=============================================================================

Every user story from PLAN.md has a record in the stories layer.
Format:

  {
    "id": "s-1-1-1",
    "epic_id": "epic-1",
    "feature_id": "feat-1-1",
    "title": "As a developer I can run docker-compose up and all services start",
    "status": "not-started",
    "acceptance": "docker-compose up exits 0. GET http://localhost:8080/health returns 200.",
    "is_active": true
  }

Status lifecycle: not-started -> in-progress -> done -> blocked

Copilot agents MUST update story status before and after each work item:

  # Before starting:
  $s = Invoke-RestMethod "http://localhost:8011/model/stories/s-1-1-1"
  $s.status = "in-progress"
  $body = $s | Select-Object * -ExcludeProperty layer, modified_by, modified_at, created_by, created_at, row_version, source_file | ConvertTo-Json -Depth 10
  Invoke-RestMethod "http://localhost:8011/model/stories/s-1-1-1" -Method PUT -ContentType "application/json" -Body $body -Headers @{"X-Actor"="agent:copilot"}

  # After completing:
  $s.status = "done"
  # PUT again

Sprint velocity query (all done stories this session):

  Invoke-RestMethod "http://localhost:8011/model/stories/" | Where-Object { $_.status -eq "done" } | Measure-Object | Select-Object Count

=============================================================================
RUNTIME USAGE -- FEATURE FLAGS
=============================================================================

The settings layer holds runtime feature flags read by the API service.
The API service reads them on startup (and can hot-reload on GET /admin/reload-settings).

Key flags:

  Flag key                    Default   Purpose
  --------------------------  -------   ----------------------------------
  FEATURE_TIER2_ENABLED       true      Gate Tier 2 checkout and access
  FEATURE_TIER3_ENABLED       true      Gate Tier 3 checkout and delivery
  FEATURE_MODE_B_ENABLED      true      Enable SP-based onboarding
  FEATURE_MODE_C_ENABLED      false     Enable Lighthouse onboarding (Phase 2)
  FEATURE_RECURRING_BILLING   true      Enable Stripe subscription mode
  FEATURE_ANOMALY_RULE        true      Enable R-05 anomaly detection rule
  FEATURE_DELIVERY_PACKAGER   true      Enable delivery service trigger on Tier 3
  FEATURE_ANALYTICS_GTM       true      Load GTM container (requires consent)
  ANALYSIS_RULE_R01_ENABLED   true      Toggle individual analysis rules
  ANALYSIS_RULE_R05_ENABLED   true      Anomaly detection (computationally heavier)
  FX_RATE_REFRESH_HOURS       24        How often to refresh currency rates
  SCAN_MAX_RESOURCES          1000      Resource Graph pagination limit
  COLLECTION_COST_DAYS        91        Days of cost data to collect

=============================================================================
RUNTIME USAGE -- RULES LAYER
=============================================================================

The rules layer mirrors services/analysis/app/rules/ and is the authoritative
list of enabled analysis rules. The analysis service can read this layer to
determine which rules to run without redeployment.

  Invoke-RestMethod "http://localhost:8011/model/rules/"

Each rule record:

  {
    "id": "rule-04-compute-scheduling",
    "label": "Compute Scheduling",
    "category": "compute-scheduling",
    "status": "implemented",
    "is_active": true,
    "min_annual_cost_threshold": 5000,
    "effort_class": "easy",
    "risk_class": "none",
    "implemented_in": "services/analysis/app/rules/rule_04_compute_scheduling.py",
    "estimated_saving_pct_low": 33,
    "estimated_saving_pct_high": 47
  }

Setting is_active=false on a rule record disables it without code change.

=============================================================================
RUNTIME USAGE -- ENDPOINTS LAYER
=============================================================================

Before generating any client code for an endpoint, read the endpoint record:

  Invoke-RestMethod "http://localhost:8011/model/endpoints/POST /v1/checkout/tier2"

Key fields to check:
  status           -- "implemented" | "stub" (do not call stubs)
  auth             -- required roles
  tier_required    -- minimum tier to call this endpoint
  implemented_in   -- file path to the route handler
  repo_line        -- line number of the handler

Do NOT call any endpoint with status=stub.
GET /model/endpoints/filter?status=implemented for all callable endpoints.

=============================================================================
ENDPOINTS -- INITIAL SEED LIST
=============================================================================

Method  Path                          Tier  Auth   Status
------  ----------------------------  ----  -----  ----------
GET     /health                       0     none   implemented
POST    /v1/auth/connect              0     jwt    stub
POST    /v1/auth/preflight            0     jwt    stub
POST    /v1/auth/disconnect           0     jwt    stub
POST    /v1/scans                     0     jwt    stub
GET     /v1/scans/:scanId             0     jwt    stub
GET     /v1/scans                     0     jwt    stub
GET     /v1/findings/:scanId          0     jwt    implemented
POST    /v1/checkout/tier2            0     jwt    stub
POST    /v1/checkout/tier3            0     jwt    stub
POST    /v1/webhooks/stripe           0     sig    stub
GET     /v1/billing/portal            0     jwt    stub
GET     /v1/entitlements              0     jwt    stub
GET     /v1/admin/stats               0     admin  stub
DELETE  /v1/admin/scans/:id           0     admin  stub

=============================================================================
CONTAINERS -- SCHEMA REFERENCE
=============================================================================

Container             PK                Fields (key)
--------------------  ----------------  --------------------------------------
scans                 /subscriptionId   scanId, status, startedUtc, completedUtc, stats, error
inventories           /subscriptionId   scanId, resources[], capturedUtc
cost-data             /subscriptionId   scanId, rows[], periodStart, periodEnd
advisor               /subscriptionId   scanId, recommendations[]
findings              /subscriptionId   scanId, analysisId, id, category, title,
                                        estimated_saving_low, estimated_saving_high,
                                        effort_class, risk_class, heuristic_source,
                                        narrative, deliverable_template_id, evidence_refs
clients               /subscriptionId   clientId, tenantId, primaryEmail, tier, paymentStatus,
                                        allowedSubscriptions[]
deliverables          /subscriptionId   deliverableId, analysisId, status, artifact{},
                                        download{sasUrl, expiresUtc}
entitlements          /subscriptionId   tier, validUntil, features[], grantedAt
payments              /subscriptionId   stripeEventId, eventType, amount, currency, createdUtc
stripe_customer_map   /stripeCustomerId id="cust::{stripeCustomerId}", subscriptionId, updatedUtc

=============================================================================
i18n -- LOCALE DEFINITIONS
=============================================================================

Locale   Language              Status (frontend)   Status (API errors)
-------  --------------------  ------------------  -------------------
en       English (en-CA)       target              target
fr       French (fr-CA)        Phase 1 required    Phase 1 required
pt-BR    Portuguese (Brazil)   Phase 2             Phase 2
es       Spanish               Phase 2             Phase 2
de       German                Phase 2             Phase 2

Translation files: frontend/src/i18n/locales/{locale}/

=============================================================================
INTEGRATION RECORDS
=============================================================================

ID           Type      Notes
-----------  --------  -------------------------------------------------------
stripe       payment   Checkout, webhook, billing portal, recurring billing
ga4          analytics Via GTM. Consent-gated. 16 events. Existing account.
clarity      analytics Via GTM. Session replay + heatmaps. Existing account.
gtm          infra     Single container script. Routes GA4 and Clarity tags.
msal         auth      Delegated flow (Mode A) and SP flow (Mode B).
azure-sdk    data      Resource Graph, Cost Management, Advisor, Policy, Network.

=============================================================================
PORTABILITY
=============================================================================

The data model code lives in 37-data-model (shared across EVA projects).
The DATA lives here in data-model/model/*.json.

To run a standalone ACA data model server:
1. Set MODEL_DIR=C:\AICOE\eva-foundry\51-ACA\data-model\model
2. Run the 37-data-model API server on port 8011
3. All model/ JSON files are loaded on seed (POST /model/admin/seed)

The ACA data model is ISOLATED from the EVA POC instance.
Never point ACA services at localhost:8010 (EVA POC). Use localhost:8011.

=============================================================================
VERITAS
=============================================================================

Veritas is initialized at the repo root (.eva/).

Audit command:
  node C:\AICOE\eva-foundry\48-eva-veritas\src\cli.js audit --repo C:\AICOE\eva-foundry\51-ACA

Trust score target: >= 0.80 before Phase 1 go-live.
Coverage expected: all 25+ endpoints have at least one story referencing them.

=============================================================================
QUICK REFERENCE
=============================================================================

  $b = "http://localhost:8011"

  # Health and summary
  Invoke-RestMethod "$b/health"
  Invoke-RestMethod "$b/model/agent-summary"

  # WBS progress
  Invoke-RestMethod "$b/model/stories/" | Where-Object { $_.status -eq "done" } | Measure-Object
  Invoke-RestMethod "$b/model/epics/"

  # Rule management
  Invoke-RestMethod "$b/model/rules/"
  Invoke-RestMethod "$b/model/rules/rule-04-compute-scheduling"

  # Endpoint discovery
  Invoke-RestMethod "$b/model/endpoints/filter?status=implemented"
  Invoke-RestMethod "$b/model/endpoints/filter?status=stub"

  # Feature flags
  Invoke-RestMethod "$b/model/settings/"

  # i18n status
  Invoke-RestMethod "$b/model/i18n/"
