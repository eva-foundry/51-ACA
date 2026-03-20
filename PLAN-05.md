# PLAN-05: Best Practices, DPDCA Agent, and Onboarding (Epics 13-15)

**Module**: PLAN-05  
**Epics**: 13 (Azure Best Practices), 14 (DPDCA Agent), 15 (Onboarding)  
**Stories**: 44 total (15 + 18 + 11)  
**Function Points**: 165 (60 + 75 + 30)

---

## Epic 13: Azure Best Practices Catalog

**Goal**: All 12 ACA rules mapped to specific Azure Well-Architected Framework (WAF) recommendations, public catalog published.  
**Status**: ONGOING  
**Stories**: 15  
**Function Points**: 60

---

## Feature 13.1: Rule-to-practice mapping

### Story ACA-13-001: R-01 WAF mapping
R-01 (unused resources) maps to Cost Optimization pillar: "Eliminate waste by identifying idle resources"

**Acceptance**: Mapping documented in catalog, links to WAF guidance

### Story ACA-13-002: R-02 WAF mapping
R-02 (orphan disks) maps to Cost Optimization + Reliability: "Delete unattached disks, avoid data loss from dangling dependencies"

**Acceptance**: Mapping includes links to deletion scripts

### Story ACA-13-003: R-03 WAF mapping
R-03 (snapshots without disk) maps to Cost Optimization: "Review snapshot retention, purge unnecessary backups"

**Acceptance**: Mapping includes snapshot lifecycle guidance

### Story ACA-13-004: R-04 WAF mapping
R-04 (over-provisioned VMs) maps to Cost Optimization: "Right-size VMs using Advisor metrics"

**Acceptance**: Mapping links to Advisor resize recommendations

### Story ACA-13-005: R-05 WAF mapping
R-05 (unused NICs) maps to Cost Optimization: "Identify and delete unassigned network interfaces"

**Acceptance**: Mapping includes NIC cleanup guidance

### Story ACA-13-006: R-06 WAF mapping
R-06 (empty resource groups) maps to Operational Excellence: "Remove unused resource groups for cleaner organization"

**Acceptance**: Mapping clarifies when empty RGs indicate cleanup opportunity

### Story ACA-13-007: R-07 WAF mapping
R-07 (NICs with no NSG) maps to Security: "Ensure all network interfaces have NSG protection"

**Acceptance**: Mapping links to NSG guidance

### Story ACA-13-008: R-08 WAF mapping
R-08 (NSG with 0.0.0.0/0 allow) maps to Security: "Restrict overly permissive rules, follow least-privilege"

**Acceptance**: Mapping includes NSG best practices, zero-trust principles

### Story ACA-13-009: R-09 WAF mapping
R-09 (public IPs with no DDoS) maps to Reliability + Security: "Enable DDoS protection for public endpoints"

**Acceptance**: Mapping links to Azure DDoS Standard guidance

### Story ACA-13-010: R-10 WAF mapping
R-10 (VMs without backup) maps to Reliability: "Enable Azure Backup for all production VMs"

**Acceptance**: Mapping includes backup vault setup

### Story ACA-13-011: R-11 WAF mapping
R-11 (single-instance deployments) maps to Reliability: "Use Availability Zones or Availability Sets for SLA"

**Acceptance**: Mapping clarifies 99.9% SLA for single instance vs 99.95%+ for multi-zone

### Story ACA-13-012: R-12 WAF mapping
R-12 (expired certificates) maps to Security: "Rotate TLS certificates before expiry, use managed certificates"

**Acceptance**: Mapping links to Key Vault certificate automation

---

## Feature 13.2: Catalog publication

### Story ACA-13-013: Catalog website deployment
Azure Best Practices catalog published at /catalog with search and filter by pillar, severity, rule ID

**Acceptance**: Catalog website live, all 12 rules searchable

### Story ACA-13-014: Narrative generation examples
Catalog includes narrative examples for all 12 rules (Tier 2 format)

**Acceptance**: Example narratives show tone, format, context

### Story ACA-13-015: IaC template examples
Catalog includes remediation IaC templates (Bicep) for all 12 rules (Tier 3 format)

**Acceptance**: Example Bicep templates downloadable from catalog

---

## Epic 14: DPDCA Cloud Agent

**Goal**: Data Model API agent (EVA-32) executes autonomous DPDCA cycle: Discover, Plan, Do, Check, Act.  
**Status**: NOT STARTED  
**Stories**: 18  
**Function Points**: 75

---

## Feature 14.1: Agent orchestration

### Story ACA-14-001: Agent definition
Define cloud agent EVA-32 with backstory, instructions, tools (Project 34 agent framework)

**Acceptance**: EVA-32 agent defined, registered in agent registry

### Story ACA-14-002: Nightly scan trigger
Nightly scan job triggers for all Tier 1+ subscriptions via Container App Job

**Acceptance**: Scheduled job runs at 02:00 UTC, processes all subscriptions

### Story ACA-14-003: Parallel scan execution
Scans run in parallel with concurrency limit (max 5 concurrent scans)

**Acceptance**: Concurrency enforced, no subscription scanned twice simultaneously

### Story ACA-14-004: Scan completion logging
Each scan logs start/end/duration/status to Cosmos audit table

**Acceptance**: audit_events container records all scan events

### Story ACA-14-005: Failure retry logic
Failed scans retry 3x with exponential backoff before marking failed

**Acceptance**: Retry logic tested, failures logged with correlation ID

### Story ACA-14-006: Agent summary generation
Agent generates summary after each DPDCA cycle and writes to data model

**Acceptance**: `/model/agents/EVA-32/summaries` includes cycle summaries

---

## Feature 14.2: DPDCA cycle implementation

### Story ACA-14-007: Discover phase
Discover: Fetch current subscription inventory, cost data, Advisor recommendations

**Acceptance**: Agent queries Azure APIs, writes to inventories, cost-data, advisor containers

### Story ACA-14-008: Plan phase
Plan: Analyze data with rule engine, generate findings, categorize by risk/effort

**Acceptance**: Findings written to findings container with risk_class, effort_class

### Story ACA-14-009: Do phase (Tier 1 Advisory)
Do (Tier 1): Generate summary report with top 5 recommendations

**Acceptance**: Tier 1 report generated, no sensitive data included

### Story ACA-14-010: Do phase (Tier 2 Narrative)
Do (Tier 2): Generate narrative with context for all findings

**Acceptance**: Narrative includes Azure WAF references, remediation steps

### Story ACA-14-011: Do phase (Tier 3 Deliverable)
Do (Tier 3): Generate ZIP with IaC templates for each finding

**Acceptance**: ZIP contains Bicep files, CSV index, SHA-256 verified

### Story ACA-14-012: Check phase
Check: Validate deliverable artifact count matches findings count, verify ZIP integrity

**Acceptance**: Artifact count verified, ZIP sha256 matches metadata

### Story ACA-14-013: Act phase
Act: Write results to data model WBS, update project status, publish evidence

**Acceptance**: Evidence records linked to stories, WBS updated

---

## Feature 14.3: Agent monitoring

### Story ACA-14-014: Agent execution history
All agent cycles logged to infrastructure_events layer (agent_execution_history node type)

**Acceptance**: Data model records agent start, end, duration, outcome

### Story ACA-14-015: Agent error tracing
Failures logged with full trace, correlation IDs, retry history

**Acceptance**: Error logs include stack trace, input parameters

### Story ACA-14-016: Agent metrics dashboard
App Insights dashboard tracks agent success rate, cycle duration, failure reasons

**Acceptance**: Dashboard shows agent health, alerting on failure spike

### Story ACA-14-017: Agent cost tracking
Each agent cycle logs estimated Azure API cost (ARM queries)

**Acceptance**: Cost per cycle estimated and logged

### Story ACA-14-018: Agent human-in-loop override
Admin can manually trigger scan for specific subscription outside of schedule

**Acceptance**: Admin page includes "Scan Now" button, respects concurrency limit

---

## Epic 15: Onboarding and Launch

**Goal**: Public launch, marketing site live, onboarding flow tested.  
**Status**: NOT STARTED  
**Stories**: 11  
**Function Points**: 30

---

## Feature 15.1: Launch readiness

### Story ACA-15-001: Phase 2 cutover complete
DNS switched to Phase 2 custom domain, rollback tested

**Acceptance**: app.aca.example.com resolves to Phase 2 infra

### Story ACA-15-002: Marketing site live
Public marketing site at aca.example.com with product tiers, pricing, demo video

**Acceptance**: Marketing site accessible, SEO optimized

### Story ACA-15-003: GA4 production property
GA4 production property configured with goals, funnels, conversion tracking

**Acceptance**: GA4 tracking code live, consent banner enforced

### Story ACA-15-004: Clarity production project
Clarity recording enabled for production traffic with privacy masking

**Acceptance**: Clarity recordings available, PII masked

### Story ACA-15-005: Status page integration
Status page integrated, reflects Phase 2 uptime and incident history

**Acceptance**: status.aca.example.com shows uptime metrics

---

## Feature 15.2: Onboarding flow optimization

### Story ACA-15-006: Onboarding wizard
New user onboarding wizard: connect subscription → preflight → view findings → upgrade prompt

**Acceptance**: Wizard guides users through 4 steps, tracks completion in GA4

### Story ACA-15-007: Demo subscription seed
Demo subscription pre-seeded for trial users (synthetic findings, no real Azure data)

**Acceptance**: Demo mode available, no Azure connection required

### Story ACA-15-008: First-scan notification
Email sent when first scan completes (via SendGrid or equivalent)

**Acceptance**: Email includes summary, link to findings, upgrade CTA

### Story ACA-15-009: Upgrade flow optimization
Upgrade flow A/B tested (inline vs modal checkout)

**Acceptance**: Conversion tracked in GA4, winner selected

### Story ACA-15-010: Referral program
Referral program implemented (Stripe referral metadata) with $10 credit for referrer

**Acceptance**: Referral links trackable, credits applied to Stripe accounts

### Story ACA-15-011: Launch announcement
Launch announcement published on Microsoft Tech Community, LinkedIn, Twitter

**Acceptance**: Announcement includes demo video, link to app

---

**End of PLAN-05** -- All 15 epics documented. Return to [PLAN.md](PLAN.md) for index.
