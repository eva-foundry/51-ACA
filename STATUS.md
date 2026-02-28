ACA -- Azure Cost Advisor -- STATUS
====================================

Version: 1.8.0
Updated: 2026-02-28 (Full ADO import: 257 stories as individual PBIs in dev.azure.com/marcopresta/51-aca)
Phase: Phase 1 -- Core Services Bootstrap
Active Epic: Epic 3 (analysis rules), Epic 4 (API endpoints), Epic 5 (frontend), Epic 12 (data model)

=============================================================================
SESSION SUMMARY -- 2026-02-28 (FULL ADO IMPORT + ADO-ID-MAP)
=============================================================================

Completed:
  TimingMiddleware (services/api/app/middleware/timing.py) -- ASGI, all 27 routes
  parse-agent-log.py (scripts/) -- git log + ACA-METRICS trailer -> ADO + data model
  CA.5 extended with duration_ms, tokens_used, test counts, files_changed, ACA-METRICS trailer
  Full ADO import: 14 Features + 257 PBIs into dev.azure.com/marcopresta/51-aca
  ado-artifacts-full.json: 257 story-level PBIs generated from veritas-plan.json (73 Done / 184 New)
  ado-artifacts.json: updated to match full version (import default target)
  .eva/ado-id-map.json: rebuilt with 256 individual ACA-NN-NNN -> ADO PBI ID mappings
  Note: ACA-03-021 is a duplicate in veritas-plan.json; 256 unique story IDs map to 256 ADO PBIs

Commits this session:
  a1a659e -- feat(ACA-12-022): timing middleware + parse-agent-log + evidence receipt extensions
  4a07520 -- feat(ACA-12-022): full ADO import -- 256 unique story PBIs in 51-aca, ado-id-map story-level

Test count: 24/24 passing (unchanged)

Open blockers:
  ACA-03-021 duplicate in veritas-plan.json -- minor, covered by single ADO PBI 3193
  ACA-03-021 should be investigated and de-duped in a future PLAN.md / seed run

Next:
  Run pytest to confirm 24/24 still passing after timing middleware
  Begin Epic 3 analysis rule implementation (ACA-03-xxx stubs)
  Epic 4 API endpoint stubs -> implemented

=============================================================================
SESSION SUMMARY -- 2026-02-27 (DATA MODEL WIRING)
=============================================================================

Problem identified: seed script seeded object IDs only -- no edges.
All 27 endpoints had empty cosmos_reads/cosmos_writes.
All 11 containers had no fields.
All 10 screens had no personas.
Hooks, feature_flags, infrastructure layers: 0 objects.
Veritas consistency score was passing vacuously (nothing to cross-check).

Fix applied:
  ENDPOINT_DEFS:      all 27 endpoints now carry cosmos_reads + cosmos_writes
  CONTAINER_DEFS:     all 11 containers now carry fields array
  SCREEN_DEFS:        all 10 screens now carry personas array
  HOOK_DEFS:          3 hooks (useFindings, useScanStatus, useCheckout)
  FEATURE_FLAG_DEFS:  4 flags (tier1/tier2/tier3/admin)
  INFRASTRUCTURE_DEFS: 10 marco* Phase 1 resources
  model_reseed():     seeds all 10 layers (was 7) on every --reseed-model run

New spec doc:
  docs/spec-wiring.md -- authoritative cross-layer wiring reference (ACA-12-021)
  Sections: Kanban evidence chain, endpoint->container map, container field registry,
            screen->persona map, feature flag gates, hook->endpoint wiring, infra layer

New bootstrap template:
  07-foundation-layer: data-model-seed-template.py
  Lesson: start every project with fully-wired DEFS before sprint 1. Never retrofit.

Veritas after wiring:
  MTI: 100 (deploy|merge|release)
  Gaps: 0 (ACA-12-021 closed)
  Test count: 24/24 passing (unchanged)
  Model objects: 349 (was 331; +18 hooks/flags/infra)

Commits:
  53a2653 feat(ACA-12-021): wire all cross-layer refs in seed script + spec-wiring.md
  da7f324 feat(ACA-04-008): Sprint-02 complete -- 5 stories, 24 tests, MTI 100

=============================================================================
SPRINT-03 READINESS
=============================================================================

Evidence chain is now fully wired. Every sprint story that implements an endpoint
will close a veritas gap and extend the cross-layer graph.

Sprint-03 candidates (in priority order):
  1. ACA-04-009  POST /v1/auth/preflight -- run pre-flight permission probes
  2. ACA-04-010  POST /v1/auth/disconnect -- revoke + KV cleanup
  3. ACA-04-002  Upgrade verify_token to use real JWKS signature verification
  4. ACA-04-003  POST /v1/scans/ -- trigger collection job + poll status
  5. ACA-05-001  Frontend scaffold: React 19 + Fluent UI v9 base
  6. ACA-03-001  Analysis rule 01: Dev Box autostop (trivial, establishes rule pattern)

Pre-Sprint-03 NOTE:
  JWT signature verification deferred -- needs JWKS URL from Entra app registration.
  ACA_CLIENT_ID must be provisioned in Key Vault before preflight tests run live.

