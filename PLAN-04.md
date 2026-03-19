# PLAN-04: Hardening, Phase 2 Infrastructure, and Data Model (Epics 10-12)

**Module**: PLAN-04  
**Epics**: 10 (Commercial Hardening), 11 (Phase 2 Infra), 12 (Data Model Support)  
**Stories**: 58 total (15 + 9 + 34)  
**Function Points**: 265 (90 + 100 + 75)

---

## Epic 10: Commercial Hardening

**Goal**: Security review passed, privacy compliance ready, support tooling live.  
**Status**: NOT STARTED  
**Stories**: 15  
**Function Points**: 90

---

## Feature 10.1: Security

### Story ACA-10-001: Red-team tier bypass testing
Red-team agent runs Tier 1 token against findings API and asserts no narrative or deliverable_template_id in response

**Acceptance**: Automated test verifies Tier 1 data isolation

### Story ACA-10-002: Tenant isolation verification
All endpoints validated: no tenant A can access tenant B data (partition key enforcement verified in integration tests)

**Acceptance**: Integration tests confirm partition key isolation works

### Story ACA-10-003: Stripe webhook signature verification
Stripe webhook signature verified on every event (whsec_ secret)

**Acceptance**: Webhook handler rejects unsigned or tampered events

### Story ACA-10-004: Admin token rotation
Admin endpoints protected by bearer token rotation schedule

**Acceptance**: Admin tokens rotate every 90 days, old tokens invalidated

### Story ACA-10-005: SQL injection prevention
All Cosmos queries parameterized (no string concatenation in queries)

**Acceptance**: Code review confirms no SQL injection vulnerabilities

### Story ACA-10-006: CSP header enforcement
CSP header enforced: scripts from GTM/Stripe/Clarity only, no inline

**Acceptance**: CSP header blocks unauthorized script sources

---

## Feature 10.2: Privacy compliance

### Story ACA-10-007: Privacy policy publication
Privacy policy published at /privacy in all 5 locales

**Acceptance**: Privacy page accessible, covers GDPR/PIPEDA/LGPD requirements

### Story ACA-10-008: Terms of service publication
Terms of service published at /terms in all 5 locales

**Acceptance**: TOS page accessible, legally reviewed

### Story ACA-10-009: Data retention policy
Data retention policy: collected Azure data purged after 90 days (Cosmos container TTL = 7,776,000 seconds on scans, inventories, cost-data)

**Acceptance**: TTL configured on containers, data auto-purges after 90 days

### Story ACA-10-010: Data deletion on disconnect
Client can request data deletion via DELETE /v1/auth/disconnect which hard-deletes all Cosmos documents for that subscriptionId

**Acceptance**: Disconnect endpoint deletes all tenant data, logs deletion event

### Story ACA-10-011: GA4 data retention configuration
GA4 data retention set to 14 months. IP anonymization enabled.

**Acceptance**: GA4 property configured for 14-month retention, IP anonymization on

### Story ACA-10-012: Clarity GDPR compliance
Clarity data retention respects GDPR right-to-be-forgotten via Clarity API

**Acceptance**: Clarity recordings deletable on request

---

## Feature 10.3: Support and documentation

### Story ACA-10-013: Client access guide publication
docs/client-access-guide.md published at /docs/access-guide in all 5 locales

**Acceptance**: Guide accessible, covers all 3 connection modes

### Story ACA-10-014: FAQ page
FAQ page covers top 10 support questions (from preflight failure analysis)

**Acceptance**: FAQ addresses common issues: missing roles, Conditional Access, etc.

### Story ACA-10-015: Status page integration
Status page (uptime) linked from footer

**Acceptance**: Footer link to status.aca.example.com (or status page provider)

---

## Epic 11: Phase 2 Infrastructure

**Goal**: Private subscription provisioned, CI pointing to Phase 2, custom domain live.  
**Status**: NOT STARTED  
**Stories**: 9  
**Function Points**: 100

---

## Feature 11.1: Terraform provisioning

### Story ACA-11-001: Terraform infrastructure deployment
`terraform apply` on infra/phase2-private completes without error

**Acceptance**: All resources provisioned: Cosmos, Container Apps, APIM, Storage, KV

### Story ACA-11-002: APIM instance provisioning
ACA-specific APIM instance is deployed with Tier enforcement policies

**Acceptance**: APIM instance dedicated to ACA, policies migrated from Phase 1

### Story ACA-11-003: GitHub Actions OIDC configuration
GitHub Actions deploy-phase2.yml is wired to private subscription via OIDC

**Acceptance**: Workflow authenticates to private subscription, no PAT

### Story ACA-11-004: Custom domain configuration
Custom domain (app.aca.example.com / api.aca.example.com) configured with managed TLS via Azure Container Apps ingress

**Acceptance**: Custom domains resolve, TLS certificates valid

### Story ACA-11-005: Cosmos geo-replication
Phase 2 Cosmos has 3 geo-replicas (canadacentral primary + failover)

**Acceptance**: Cosmos configured with multi-region writes, automatic failover

---

## Feature 11.2: Cutover

### Story ACA-11-006: DNS TTL preparation
DNS TTL lowered 48h before cutover

**Acceptance**: DNS records have 300s TTL before cutover

### Story ACA-11-007: Phase 1 rollback readiness
Phase 1 marco* infra remains live as rollback for 30 days post-cutover

**Acceptance**: Phase 1 resources not deleted immediately, preserved for rollback

### Story ACA-11-008: Phase 2 smoke test
Phase 2 smoke test: full Tier 1 -> Tier 3 flow on Phase 2 infra

**Acceptance**: All flows tested on Phase 2 before DNS switch

### Story ACA-11-009: APIM configuration export
APIM configuration exported and version-controlled

**Acceptance**: APIM policies backed up to Git before cutover

---

## Epic 12: Data Model Support (app runtime)

**Goal**: EVA data model used as source of truth for build process and as app runtime API.  
**Status**: ONGOING  
**Stories**: 34  
**Function Points**: 75

---

## Feature 12.1: Build-time use

### Story ACA-12-001: WBS seeding
All epics, features, and stories from this PLAN are seeded into the data-model WBS layer with epic, feature, and user_story node types preserved

**Acceptance**: Cloud API has 281 stories in WBS layer with correct hierarchy

### Story ACA-12-002: Story status tracking
Each story has status: not-started / in-progress / done

**Acceptance**: WBS records include status field, updated by agents

### Story ACA-12-003: Agent story status updates
Story status is updated by the agent at start and end of each work item

**Acceptance**: Agents write status updates to cloud API during development

### Story ACA-12-004: Agent summary reporting
data-model agent-summary reflects current overall completion percentage

**Acceptance**: `/model/projects/51-ACA` includes completion metrics

---

## Feature 12.2: Runtime use

### Story ACA-12-005: Feature flags integration
API service reads feature_flags layer to gate unreleased features

**Acceptance**: API queries feature flags from data model, gates features dynamically

### Story ACA-12-006: Rules discovery
Analysis service reads the rules layer to discover enabled/disabled rules (data-model rules layer matches services/analysis/app/rules/ files)

**Acceptance**: Analysis engine loads rule list from data model

### Story ACA-12-007: Endpoints layer synchronization
Endpoints layer is kept in sync with every shipped route (PUT on ship)

**Acceptance**: Data model endpoints layer reflects live API surface

### Story ACA-12-008: Containers layer reflection
Containers layer reflects the actual Cosmos schema (fields, partition keys)

**Acceptance**: Data model documents Cosmos schema with accurate partition keys

---

## Feature 12.3: Phase 1 Core Infrastructure & Containers

### Story ACA-12-009: Scans container
Cosmos DB aca-db + scans container with 256-partition key on subscriptionId (Phase 1 marco* sandbox, infra/phase1-marco/main.bicep)

**Acceptance**: scans container has partition key /subscriptionId

### Story ACA-12-010: Inventories container
inventories container for Azure resource snapshots (partition key: subscriptionId)

**Acceptance**: inventories container partitioned by subscriptionId

### Story ACA-12-011: Cost-data container
cost-data container for monthly cost export and FinOps hub landing zone

**Acceptance**: cost-data container stores cost rows partitioned by subscriptionId

### Story ACA-12-012: Advisor container
advisor container for Azure Advisor recommendations + scores

**Acceptance**: advisor container stores recommendations partitioned by subscriptionId

### Story ACA-12-013: Findings container
findings container for analysis rule output (indexed on risk_class, effort_class)

**Acceptance**: findings container has composite indexes for filtering

### Story ACA-12-014: APIM product configuration
APIM ACA product + subscription key policy for tier-gated rate limiting

**Acceptance**: APIM product configured with tier-based rate limits

### Story ACA-12-015: Key Vault secrets wiring
Key Vault secrets wiring (ACA-CLIENT-ID, ACA-OPENAI-KEY, ACA-COSMOS-CONN)

**Acceptance**: All services reference secrets via KV, no hardcoded credentials

### Story ACA-12-016: Container App Job definitions
Container App Job definitions for collector, analysis, delivery workers

**Acceptance**: 3 jobs defined, triggerable via API or schedule

---

## Feature 12.4: Data Model Safe Cleanup and Ground-Up Restore

**Execution order**: snapshot -> scoped cleanup -> re-prime -> README/PLAN refresh -> WBS rebuild -> Veritas audit  
**Gate**: do not execute cleanup until the README scope refresh is merged and the snapshot evidence pack exists

### Story ACA-12-029: WBS evidence snapshot
Snapshot the live `projects/51-ACA`, WBS, evidence, and related governance rows before any delete so the restore can prove exactly what was removed and why

**Acceptance**: Evidence pack created with timestamp, includes all WBS records

### Story ACA-12-030: Scoped cleanup execution
Execute a scoped cleanup that deletes only 51-ACA WBS and evidence records, preserves the canonical project identity row, and records API correlation IDs for every delete

**Acceptance**: Cleanup deletes only 51-ACA WBS/evidence, preserves project record

### Story ACA-12-031: Foundation re-prime
Re-prime 51-ACA through Project 07 after cleanup and verify governance scaffolding, project registration, and PROJECT-ORGANIZATION continuity remain intact

**Acceptance**: Project 07 re-prime succeeds, project identity restored

### Story ACA-12-032: WBS hierarchy regeneration
Regenerate the project hierarchy from README + PLAN top-down into the data-model WBS layer, preserving epic -> feature -> user_story relationships

**Acceptance**: WBS regenerated from PLAN files, 281+ stories in cloud API

### Story ACA-12-033: Bottom-up reconciliation
Run a bottom-up reconciliation that flags missing user_story leaves, duplicate IDs, orphan evidence, and legacy `/model/stories` dependencies as explicit gaps

**Acceptance**: Reconciliation report identifies gaps, no silent data loss

### Story ACA-12-034: Restore evidence publication
Publish a restore evidence pack plus Veritas audit results and do not re-open cloud sprint execution until the rebuilt WBS counts and trust score are accepted

**Acceptance**: Evidence pack published, MTI score meets threshold (≥60)

---

## Feature 12.5: Additional containers (Epic 4/6 dependencies)

### Story ACA-12-017: Clients container
clients container for subscription connection records (partition key: subscriptionId)

**Acceptance**: clients container stores mode, stripeCustomerId, tier, isLocked

### Story ACA-12-018: Deliverables container
deliverables container for Tier 3 ZIP metadata (partition key: subscriptionId)

**Acceptance**: deliverables container stores sasUrl, sha256, artifactCount

### Story ACA-12-019: Entitlements container
entitlements container for tier access control (partition key: subscriptionId)

**Acceptance**: entitlements container stores tier, validUntil, features[]

### Story ACA-12-020: Payments container
payments container for Stripe webhook event audit trail (partition key: subscriptionId)

**Acceptance**: payments container stores all webhook events

### Story ACA-12-021: Stripe customer map container
stripe_customer_map container for bidirectional customer ID mapping (partition key: stripeCustomerId)

**Acceptance**: Container maps stripeCustomerId <-> subscriptionId

### Story ACA-12-022: Admin audit events container
admin_audit_events container for admin action logging (partition key: adminUserId)

**Acceptance**: Container logs all admin actions with reason, operator, timestamp

---

## Feature 12.6: Data model seeding and synchronization

### Story ACA-12-023: Epic metadata seeding
Seed epic records to WBS layer with title, status, milestone, FP totals

**Acceptance**: 15 epic records in cloud WBS with level=epic

### Story ACA-12-024: Feature metadata seeding
Seed feature records to WBS layer with parent_wbs_id linking to epics

**Acceptance**: ~60 feature records with level=feature, linked to epics

### Story ACA-12-025: Story metadata seeding
Seed user_story records to WBS layer with parent_wbs_id linking to features

**Acceptance**: 281 story records with level=user_story, linked to features

### Story ACA-12-026: Evidence layer seeding
Seed evidence records linking commits, tests, artifacts to stories

**Acceptance**: Evidence records reference story_id, include artifact_type

### Story ACA-12-027: Project metadata update
Update project metadata in `/model/projects/51-ACA` with sprint context

**Acceptance**: Project record includes active sprint, MTI score, story count

### Story ACA-12-028: Continuous synchronization
Implement continuous sync: agent commits update WBS status in real-time

**Acceptance**: Story status updates written to cloud within 5 minutes of commit

---

**End of PLAN-04** -- Continue to [PLAN-05.md](PLAN-05.md) for Epics 13-15
