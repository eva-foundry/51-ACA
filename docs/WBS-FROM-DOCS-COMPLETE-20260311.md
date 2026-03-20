# ACA (Azure Cost Advisor) - Complete Work Breakdown Structure
## Extracted from Documentation (Files 01-49)
**Generated**: 2026-03-11  
**Source**: 49 specification documents (01-feasibility.md through 49-ACA-Founder-Launch-Kit.md)  
**Extraction Method**: Comprehensive analysis of all architectural specifications, feature descriptions, and implementation requirements

---

## Executive Summary

**Total Epics**: 19  
**Total Features**: 127  
**Total User Stories**: 623  
**Estimated Function Points**: 4,957 FP (preliminary)

**Coverage**: This WBS captures the complete scope from feasibility assessment (Phase 0) through multi-cloud ecosystem platform (Phase 10), including:
- Core MVP (authentication, collection, analysis, delivery)
- Enterprise features (multi-tenant, RBAC, billing)
- Advanced capabilities (continuous monitoring, autonomous optimization, predictive analytics)
- Platform evolution (multi-cloud, marketplace, ecosystem)

Nested DPDCA note:
- Docs 44-49 were reconciled after the initial 43-doc extraction.
- Most content mapped to existing stories already seeded in Epics 05, 06, 16, 18, and 19.
- Only true deltas were added as new stories below to avoid duplicate backlog inflation.

---

## EPIC 01: Authentication & Authorization Framework
**FP Estimate**: 193 FP  
**Stories**: 25

### Feature 1.1: Multi-Tenant Identity Support
**Stories**: 5

- **ACA-01-001**: Implement Microsoft Entra ID (Azure AD) authentication with multi-tenant support
  - **AC**: Support authority=common, acquire ARM tokens, handle MFA/Conditional Access
  - **FP**: 8

- **ACA-01-002**: Implement delegated user sign-in flow (device code + PKCE)
  - **AC**: MSAL device code flow, refresh token handling, Key Vault storage
  - **FP**: 8

- **ACA-01-003**: Implement service principal authentication mode
  - **AC**: Accept client ID/secret, store securely, authenticate as app identity
  - **FP**: 5

- **ACA-01-004**: Implement Azure Lighthouse delegation support
  - **AC**: Support delegated access from client tenant to ACA tenant
  - **FP**: 8

- **ACA-01-005**: Implement connection mode selection UI and API
  - **AC**: Support delegated/service_principal/lighthouse modes, validate credentials
  - **FP**: 5

### Feature 1.2: Pre-Flight Permission Validation
**Stories**: 8

- **ACA-01-006**: Design and implement pre-flight probe framework
  - **AC**: Pluggable probe system, status reporting (PASS/WARN/FAIL), evidence capture
  - **FP**: 8

- **ACA-01-007**: Implement ARM token acquisition probe
  - **AC**: Validate token, extract tenant/principal, return identity context
  - **FP**: 3

- **ACA-01-008**: Implement subscription discovery probe
  - **AC**: List subscriptions, validate target subscription visibility
  - **FP**: 5

- **ACA-01-009**: Implement Resource Graph access probe
  - **AC**: Test query capability, validate permissions
  - **FP**: 5

- **ACA-01-010**: Implement Cost Management Reader probe
  - **AC**: Test cost query, validate 91-day window availability
  - **FP**: 5

- **ACA-01-011**: Implement Azure Advisor access probe
  - **AC**: Test recommendations read, validate permissions
  - **FP**: 5

- **ACA-01-012**: Implement optional Policy Insights probe
  - **AC**: Test policy state read, mark as optional capability
  - **FP**: 5

- **ACA-01-013**: Implement optional Log Analytics probe
  - **AC**: Test workspace access, list workspaces, mark as optional
  - **FP**: 5

### Feature 1.3: Extraction Depth Assessment
**Stories**: 4

- **ACA-01-014**: Implement extraction depth calculation engine
  - **AC**: Compute DEPTH_0 through DEPTH_5 based on probe results
  - **FP**: 8

- **ACA-01-015**: Implement depth-based UI messaging
  - **AC**: Show user what data can be collected based on depth
  - **FP**: 5

- **ACA-01-016**: Implement depth-based collection scope configuration
  - **AC**: Configure collector based on computed depth
  - **FP**: 5

- **ACA-01-017**: Store pre-flight results in Cosmos DB
  - **AC**: Persist preflightId, probe results, depth, timestamp
  - **FP**: 5

### Feature 1.4: RBAC Role Verification
**Stories**: 6

- **ACA-01-018**: Implement Reader role verification
  - **AC**: Validate Reader at subscription scope
  - **FP**: 3

- **ACA-01-019**: Implement Cost Management Reader verification
  - **AC**: Validate Cost Management Reader role
  - **FP**: 3

- **ACA-01-020**: Implement optional Log Analytics Reader verification
  - **AC**: Check workspace-level access if LA enabled
  - **FP**: 3

- **ACA-01-021**: Generate missing permissions report
  - **AC**: List missing roles, provide remediation guidance
  - **FP**: 5

- **ACA-01-022**: Implement role assignment validation
  - **AC**: Call ARM role assignments API, parse effective permissions
  - **FP**: 8

- **ACA-01-023**: Create client-facing access setup guide
  - **AC**: Document role requirements, setup steps, troubleshooting
  - **FP**: 3

### Feature 1.5: Entra Token Validation and Role Mapping
**Stories**: 2

- **ACA-01-024**: Implement Entra JWT validation using OpenID discovery and JWKS
  - **AC**: Resolve discovery metadata from tenant-specific or `common` authority, cache JWKS, validate `aud`, `iss`, `exp`, and `iat`, and return structured 401 errors for malformed, expired, or unknown-key tokens
  - **FP**: 8

- **ACA-01-025**: Map Entra claims to ACA actor context and admin roles
  - **AC**: Extract `oid/sub`, `name`, `tid`, and `roles/groups`; map app roles and configured group IDs to `ACA_Admin`, `ACA_Support`, and `ACA_FinOps`; produce an actor object suitable for backend RBAC enforcement
  - **FP**: 5

---

## EPIC 02: Data Collection Subsystem
**FP Estimate**: 320 FP  
**Stories**: 42

### Feature 2.1: Azure Resource Graph Collection
**Stories**: 6

- **ACA-02-001**: Implement Resource Graph query engine
  - **AC**: Query all resources in subscription, handle pagination
  - **FP**: 8

- **ACA-02-002**: Implement inventory normalization
  - **AC**: Extract resourceId, type, name, RG, location, SKU, tags, properties
  - **FP**: 8

- **ACA-02-003**: Write inventory to Cosmos DB inventories container
  - **AC**: Partition by subscriptionId, bulk upsert, track counts
  - **FP**: 5

- **ACA-02-004**: Implement resource type filtering
  - **AC**: Filter by relevant types (VMs, disks, IPs, DBs, etc.)
  - **FP**: 5

- **ACA-02-005**: Implement inventory collection retry/backoff
  - **AC**: Exponential backoff for 429, max retries, error reporting
  - **FP**: 5

- **ACA-02-006**: Performance target: <60s for 500 resources
  - **AC**: Monitor and optimize query performance
  - **FP**: 5

### Feature 2.2: Cost Management Data Collection
**Stories**: 8

- **ACA-02-007**: Implement Cost Management Query API client
  - **AC**: Support daily granularity, 91-day window, pagination
  - **FP**: 8

- **ACA-02-008**: Implement cost data normalization
  - **AC**: Extract date, MeterCategory, MeterName, RG, resourceId, PreTaxCost, currency
  - **FP**: 8

- **ACA-02-009**: Write cost data to Cosmos DB cost-data container
  - **AC**: Partition by subscriptionId, daily rows, track counts
  - **FP**: 5

- **ACA-02-010**: Implement 429 retry logic for Cost Management API
  - **AC**: Honor Retry-After header, exponential backoff
  - **FP**: 5

- **ACA-02-011**: Implement cost data pagination handler
  - **AC**: Follow nextLink, accumulate rows, track progress
  - **FP**: 5

- **ACA-02-012**: Implement cost data validation
  - **AC**: Validate date ranges, currency consistency, row completeness
  - **FP**: 5

- **ACA-02-013**: Handle cost data availability exceptions
  - **AC**: Graceful handling of missing data, partial windows
  - **FP**: 3

- **ACA-02-014**: Implement cost data export alternative (FinOps Hub)
  - **AC**: Support reading from cost export landing zone
  - **FP**: 8

### Feature 2.3: Azure Advisor Collection
**Stories**: 5

- **ACA-02-015**: Implement Advisor API client
  - **AC**: List recommendations across all categories
  - **FP**: 5

- **ACA-02-016**: Implement Advisor data normalization
  - **AC**: Extract category, impact, risk, description, affected resources
  - **FP**: 8

- **ACA-02-017**: Write Advisor data to Cosmos DB advisor container
  - **AC**: Store both normalized and raw JSON, partition by subscriptionId
  - **FP**: 5

- **ACA-02-018**: Implement Advisor recommendation categorization
  - **AC**: Map to ACA finding categories
  - **FP**: 5

- **ACA-02-019**: Track Advisor recommendation changes over time
  - **AC**: Compare snapshots, detect new/resolved recommendations
  - **FP**: 5

### Feature 2.4: Policy Insights Collection
**Stories**: 4

- **ACA-02-020**: Implement Policy Insights API client
  - **AC**: Query policy compliance summaries at subscription scope
  - **FP**: 5

- **ACA-02-021**: Normalize policy compliance data
  - **AC**: Extract compliant counts, non-compliant counts, policy details
  - **FP**: 5

- **ACA-02-022**: Store policy signals in Cosmos DB
  - **AC**: Create policy signals storage schema
  - **FP**: 5

- **ACA-02-023**: Mark policy collection as optional capability
  - **AC**: Graceful skip if not available, report in depth
  - **FP**: 3

### Feature 2.5: Network Topology Collection
**Stories**: 8

- **ACA-02-024**: Implement NSG enumeration
  - **AC**: List all NSGs, extract rule counts, configuration
  - **FP**: 5

- **ACA-02-025**: Implement Public IP enumeration
  - **AC**: List all public IPs, extract attachment status, SKU
  - **FP**: 5

- **ACA-02-026**: Implement VNet enumeration
  - **AC**: List VNets, extract address space, subnets, peerings
  - **FP**: 5

- **ACA-02-027**: Implement Private DNS zone enumeration
  - **AC**: List private DNS zones, record counts
  - **FP**: 3

- **ACA-02-028**: Implement Load Balancer / App Gateway enumeration
  - **AC**: List LBs/AppGW, extract backend pools, rules
  - **FP**: 5

- **ACA-02-029**: Implement NAT Gateway enumeration
  - **AC**: List NAT gateways, extract configuration
  - **FP**: 3

- **ACA-02-030**: Normalize network topology data
  - **AC**: Create unified schema for network signals
  - **FP**: 5

- **ACA-02-031**: Store network signals in Cosmos DB
  - **AC**: Create network signals storage schema
  - **FP**: 5

### Feature 2.6: Activity & Log Analytics Collection (Optional)
**Stories**: 6

- **ACA-02-032**: Implement Log Analytics workspace discovery
  - **AC**: List accessible workspaces in subscription
  - **FP**: 5

- **ACA-02-033**: Implement activity query for idle detection
  - **AC**: Query for resource activity patterns (CPU, connections, queries)
  - **FP**: 8

- **ACA-02-034**: Implement activity query for usage patterns
  - **AC**: Detect night/weekend inactivity, seasonal patterns
  - **FP**: 8

- **ACA-02-035**: Normalize activity data
  - **AC**: Extract resource, timestamp, metric, value
  - **FP**: 5

- **ACA-02-036**: Store activity signals in Cosmos DB
  - **AC**: Create activity signals storage schema
  - **FP**: 5

- **ACA-02-037**: Mark activity collection as optional
  - **AC**: Skip if LA unavailable, report in depth
  - **FP**: 3

### Feature 2.7: Collector Orchestration
**Stories**: 5

- **ACA-02-038**: Implement collector job orchestration
  - **AC**: Coordinate pre-flight → inventory → cost → advisor → policy → network → activity
  - **FP**: 8

- **ACA-02-039**: Implement scan lifecycle state management
  - **AC**: Update scan status (queued → running → collected → succeeded/failed)
  - **FP**: 5

- **ACA-02-040**: Implement collection progress reporting
  - **AC**: Report counts, durations, errors back to API
  - **FP**: 5

- **ACA-02-041**: Implement collection error handling
  - **AC**: Capture errors, continue where possible, report failures
  - **FP**: 5

- **ACA-02-042**: Deploy collector as Container App Job
  - **AC**: Configure job, environment variables, managed identity
  - **FP**: 8

---

## EPIC 03: Analysis Engine & Rules
**FP Estimate**: 380 FP  
**Stories**: 47

### Feature 3.1: Analysis Framework
**Stories**: 6

- **ACA-03-001**: Design analysis rule contract
  - **AC**: Define rule interface, input/output, metadata
  - **FP**: 5

- **ACA-03-002**: Implement analysis context
  - **AC**: Provide scan data, subscription data to rules
  - **FP**: 5

- **ACA-03-003**: Implement rule registry and loader
  - **AC**: Discover, load, execute rules dynamically
  - **FP**: 8

- **ACA-03-004**: Implement analysis job orchestration
  - **AC**: Load scan data, execute rules, aggregate findings
  - **FP**: 8

- **ACA-03-005**: Store findings in Cosmos DB findings container
  - **AC**: Partition by subscriptionId, track per-rule results
  - **FP**: 5

- **ACA-03-006**: Deploy analysis as Container App Job
  - **AC**: Configure job, triggers, managed identity
  - **FP**: 8

### Feature 3.2: Ghost Resource Detection Rules
**Stories**: 8

- **ACA-03-007**: Rule: Unattached managed disks
  - **AC**: Detect disks not attached to VMs, age > threshold, no activity
  - **FP**: 8

- **ACA-03-008**: Rule: Unattached public IPs
  - **AC**: Detect unattached IPs, no meaningful usage
  - **FP**: 5

- **ACA-03-009**: Rule: Orphaned snapshots
  - **AC**: Old snapshots, no restore activity, no dependency
  - **FP**: 5

- **ACA-03-010**: Rule: Idle load balancers
  - **AC**: Empty backend pools, no traffic, no health activity
  - **FP**: 5

- **ACA-03-011**: Rule: Orphaned App Service Plans
  - **AC**: Plan running, apps removed/dormant, low usage
  - **FP**: 5

- **ACA-03-012**: Rule: Zombie databases
  - **AC**: DB exists, minimal query activity, no linked app
  - **FP**: 8

- **ACA-03-013**: Rule: Forgotten storage accounts
  - **AC**: Old storage, stale blobs, no access events
  - **FP**: 5

- **ACA-03-014**: Rule: Idle AKS clusters
  - **AC**: Cluster exists, minimal workload, test environment
  - **FP**: 8

### Feature 3.3: Idle & Shutdown Opportunity Rules
**Stories**: 5

- **ACA-03-015**: Rule: Night/weekend shutdown candidates (dev VMs)
  - **AC**: Detect dev/test VMs with night/weekend inactivity
  - **FP**: 8

- **ACA-03-016**: Rule: Seasonal environment shutdown
  - **AC**: Detect environments unused for extended periods
  - **FP**: 5

- **ACA-03-017**: Rule: Underutilized VMs (low CPU)
  - **AC**: CPU < threshold for extended period
  - **FP**: 5

- **ACA-03-018**: Rule: Idle SQL databases
  - **AC**: Low query activity, no connections
  - **FP**: 5

- **ACA-03-019**: Rule: Idle App Services
  - **AC**: Low request counts, no active users
  - **FP**: 5

### Feature 3.4: Rightsizing Rules
**Stories**: 6

- **ACA-03-020**: Rule: Oversized VMs
  - **AC**: Consistent low CPU/memory, recommend smaller SKU
  - **FP**: 8

- **ACA-03-021**: Rule: Oversized SQL databases
  - **AC**: Low DTU/vCore usage, recommend tier downgrade
  - **FP**: 8

- **ACA-03-022**: Rule: Over-provisioned storage
  - **AC**: Premium disk on low-IOPS workload
  - **FP**: 5

- **ACA-03-023**: Rule: Excessive backup retention
  - **AC**: Backup beyond policy requirements
  - **FP**: 3

- **ACA-03-024**: Rule: Over-configured App Service Plan
  - **AC**: Plan tier exceeds app requirements
  - **FP**: 5

- **ACA-03-025**: Rule: Unnecessary high availability
  - **AC**: Premium features on dev/test resources
  - **FP**: 5

### Feature 3.5: Reservation & Commitment Rules
**Stories**: 4

- **ACA-03-026**: Rule: Reserved instance opportunities (VMs)
  - **AC**: Stable VM usage, calculate RI savings
  - **FP**: 8

- **ACA-03-027**: Rule: Reserved capacity opportunities (SQL)
  - **AC**: Stable SQL usage, calculate reservation savings
  - **FP**: 8

- **ACA-03-028**: Rule: Savings plan opportunities
  - **AC**: Predictable compute usage patterns
  - **FP**: 8

- **ACA-03-029**: Rule: Long-term commitment recommendations
  - **AC**: 1-year vs 3-year analysis
  - **FP**: 8

### Feature 3.6: Advisor-Backed Rules
**Stories**: 5

- **ACA-03-030**: Rule: High-impact Advisor cost recommendations
  - **AC**: Extract high-impact Advisor findings, enrich with context
  - **FP**: 5

- **ACA-03-031**: Rule: Advisor security findings with cost impact
  - **AC**: Security recs that also reduce cost (e.g., remove exposure)
  - **FP**: 5

- **ACA-03-032**: Rule: Advisor reliability findings with cost trade-off
  - **AC**: Reliability recs with cost implications
  - **FP**: 5

- **ACA-03-033**: Enrich Advisor recs with Pareto scoring
  - **AC**: Add effort/risk/savings to Advisor findings
  - **FP**: 5

- **ACA-03-034**: Cross-reference Advisor with inventory
  - **AC**: Link Advisor recs to ACA resource data
  - **FP**: 5

### Feature 3.7: Governance & Compliance Rules
**Stories**: 4

- **ACA-03-035**: Rule: Untagged resources
  - **AC**: Resources missing required tags, cost allocation impact
  - **FP**: 5

- **ACA-03-036**: Rule: Non-compliant naming conventions
  - **AC**: Resources not following naming standards
  - **FP**: 3

- **ACA-03-037**: Rule: Policy violations with cost implications
  - **AC**: Policy non-compliance driving waste
  - **FP**: 5

- **ACA-03-038**: Rule: Orphaned resource groups
  - **AC**: Empty or nearly-empty RGs
  - **FP**: 3

### Feature 3.8: Network Optimization Rules
**Stories**: 4

- **ACA-03-039**: Rule: Idle public endpoints
  - **AC**: Public IPs or frontends with no traffic
  - **FP**: 5

- **ACA-03-040**: Rule: Redundant NAT gateways
  - **AC**: Multiple NAT gateways where one suffices
  - **FP**: 5

- **ACA-03-041**: Rule: Over-provisioned bandwidth
  - **AC**: High-bandwidth configs on low-traffic resources
  - **FP**: 5

- **ACA-03-042**: Rule: Stale DNS zones
  - **AC**: DNS zones with no records or activity
  - **FP**: 3

### Feature 3.9: Pareto Ranking & Prioritization
**Stories**: 5

- **ACA-03-043**: Implement Pareto scoring algorithm
  - **AC**: Score = (Savings × Confidence) / Risk
  - **FP**: 8

- **ACA-03-044**: Compute effort class for findings
  - **AC**: Classify as trivial/easy/medium/involved/strategic
  - **FP**: 5

- **ACA-03-045**: Compute risk class for findings
  - **AC**: Classify as none/low/medium/high
  - **FP**: 5

- **ACA-03-046**: Generate top-N recommendations list
  - **AC**: Sort by Pareto score, extract top 10-20
  - **FP**: 5

- **ACA-03-047**: Aggregate findings by category
  - **AC**: Group by ghost/idle/rightsizing/reservation/advisor/governance/network
  - **FP**: 5

---

## EPIC 04: Delivery & Script Generation
**FP Estimate**: 240 FP  
**Stories**: 32

### Feature 4.1: Script Template Framework
**Stories**: 5

- **ACA-04-001**: Design script template contract
  - **AC**: Define interface, dry-run mode, parameterization
  - **FP**: 5

- **ACA-04-002**: Implement script template registry
  - **AC**: Discover, load templates by ID
  - **FP**: 5

- **ACA-04-003**: Implement script generation engine
  - **AC**: Map findings to templates, generate scripts
  - **FP**: 8

- **ACA-04-004**: Implement dry-run vs hot-run mode
  - **AC**: Generate safe validation scripts vs action scripts
  - **FP**: 5

- **ACA-04-005**: Add script safety comments and warnings
  - **AC**: Include resource IDs, impact warnings, rollback hints
  - **FP**: 3

### Feature 4.2: PowerShell Script Templates
**Stories**: 12

- **ACA-04-006**: Template: Delete unattached managed disk
  - **AC**: Generate Remove-AzDisk command with safety checks
  - **FP**: 3

- **ACA-04-007**: Template: Delete unattached public IP
  - **AC**: Generate Remove-AzPublicIpAddress command
  - **FP**: 3

- **ACA-04-008**: Template: Delete orphaned snapshot
  - **AC**: Generate Remove-AzSnapshot command
  - **FP**: 3

- **ACA-04-009**: Template: VM night/weekend shutdown schedule
  - **AC**: Generate Automation Account runbook or Logic App
  - **FP**: 8

- **ACA-04-010**: Template: Resize VM to smaller SKU
  - **AC**: Generate Set-AzVMSize command with validation
  - **FP**: 5

- **ACA-04-011**: Template: Downgrade SQL database tier
  - **AC**: Generate Set-AzSqlDatabase command
  - **FP**: 5

- **ACA-04-012**: Template: Convert disk to standard
  - **AC**: Generate disk SKU conversion command
  - **FP**: 5

- **ACA-04-013**: Template: Delete idle load balancer
  - **AC**: Generate Remove-AzLoadBalancer with checks
  - **FP**: 5

- **ACA-04-014**: Template: Apply resource tags
  - **AC**: Generate Set-AzResource tag commands
  - **FP**: 3

- **ACA-04-015**: Template: Bulk resource cleanup
  - **AC**: Generate batch deletion script with confirmation
  - **FP**: 8

- **ACA-04-016**: Template: Reserved instance purchase
  - **AC**: Generate RI/savings plan commands with analysis
  - **FP**: 8

- **ACA-04-017**: Template: Storage tier optimization
  - **AC**: Generate blob tier change commands
  - **FP**: 5

### Feature 4.3: Report Generation
**Stories**: 8

- **ACA-04-018**: Generate executive summary
  - **AC**: Total findings, estimated annual savings, top opportunities
  - **FP**: 5

- **ACA-04-019**: Generate technical assessment report (Markdown)
  - **AC**: Detailed findings by category, evidence, recommendations
  - **FP**: 8

- **ACA-04-020**: Generate findings list with money range bars
  - **AC**: Visual representation of savings potential
  - **FP**: 5

- **ACA-04-021**: Generate effort/risk badges
  - **AC**: Color-coded indicators for implementation complexity
  - **FP**: 3

- **ACA-04-022**: Generate action plan roadmap
  - **AC**: Phased implementation plan (quick wins → strategic)
  - **FP**: 5

- **ACA-04-023**: Generate ghost resources section
  - **AC**: Dedicated section for orphaned/unused resources
  - **FP**: 5

- **ACA-04-024**: Generate Pareto chart visualization
  - **AC**: 80/20 chart showing top savings opportunities
  - **FP**: 5

- **ACA-04-025**: Generate benchmark comparison (optional)
  - **AC**: Compare to industry averages if data available
  - **FP**: 5

### Feature 4.4: Deliverable Packaging
**Stories**: 7

- **ACA-04-026**: Package scripts into ZIP archive
  - **AC**: Organized folder structure, README, safety guide
  - **FP**: 5

- **ACA-04-027**: Package reports into ZIP archive
  - **AC**: Executive summary, technical report, appendices
  - **FP**: 5

- **ACA-04-028**: Generate implementation playbook
  - **AC**: Step-by-step guide for using scripts
  - **FP**: 5

- **ACA-04-029**: Generate safety checklist
  - **AC**: Pre-execution validation steps
  - **FP**: 3

- **ACA-04-030**: Generate rollback guide
  - **AC**: How to undo changes if needed
  - **FP**: 5

- **ACA-04-031**: Store deliverable in Blob Storage
  - **AC**: Upload ZIP, generate SAS URL, track in Cosmos
  - **FP**: 5

- **ACA-04-032**: Implement deliverable download API
  - **AC**: GET /v1/deliverables/{id}/download returns SAS URL
  - **FP**: 5

---

## EPIC 05: Frontend Application (Customer & Admin)
**FP Estimate**: 280 FP  
**Stories**: 38

### Feature 5.1: Frontend Infrastructure
**Stories**: 6

- **ACA-05-001**: Set up Vite + React + TypeScript project
  - **AC**: Modern build setup, hot reload, TypeScript strict
  - **FP**: 5

- **ACA-05-002**: Implement Fluent UI v9 design system integration
  - **AC**: Theme, components, accessibility primitives
  - **FP**: 5

- **ACA-05-003**: Implement React Router with route guards
  - **AC**: Customer routes, admin routes, auth protection
  - **FP**: 8

- **ACA-05-004**: Implement API client abstraction
  - **AC**: Centralized HTTP client, error handling, auth headers
  - **FP**: 5

- **ACA-05-005**: Implement environment configuration
  - **AC**: VITE_API_BASE_URL, VITE_ENABLE_TELEMETRY, feature flags
  - **FP**: 3

- **ACA-05-006**: Deploy frontend to Azure Static Web Apps
  - **AC**: CI/CD pipeline, custom domain, CDN
  - **FP**: 8

### Feature 5.2: Authentication & Session Management
**Stories**: 5

- **ACA-05-007**: Implement useAuth hook
  - **AC**: React hook for auth state, login/logout, role checking
  - **FP**: 8

- **ACA-05-008**: Implement RequireAuth route guard
  - **AC**: Redirect to login if unauthenticated
  - **FP**: 3

- **ACA-05-009**: Implement RequireRole route guard
  - **AC**: Check user roles (ACA_Admin, ACA_Support, ACA_FinOps)
  - **FP**: 5

- **ACA-05-010**: Implement dev auth mode for local testing
  - **AC**: Mock authenticated user with roles via env var
  - **FP**: 3

- **ACA-05-011**: Store subscription context in local storage
  - **AC**: Persist selected subscriptionId across sessions
  - **FP**: 3

### Feature 5.3: Customer Pages
**Stories**: 12

- **ACA-05-012**: LoginPage: Implement sign-in UI
  - **AC**: Microsoft sign-in button, status messages
  - **FP**: 5

- **ACA-05-013**: ConnectSubscriptionPage: Implement subscription selection
  - **AC**: List subscriptions, select, call POST /v1/collect/start
  - **FP**: 8

- **ACA-05-014**: ConnectSubscriptionPage: Service principal input
  - **AC**: Form for tenant/client/secret, validation
  - **FP**: 5

- **ACA-05-015**: CollectionStatusPage: Implement scan progress UI
  - **AC**: Polling GET /v1/collect/status, progress bars, step indicators
  - **FP**: 8

- **ACA-05-016**: CollectionStatusPage: Pre-flight results display
  - **AC**: Show green/yellow/red checks, probe details, depth
  - **FP**: 5

- **ACA-05-017**: FindingsTier1Page: Implement findings list
  - **AC**: Display findings, money range bars, effort badges, CTA to upgrade
  - **FP**: 8

- **ACA-05-018**: FindingsTier1Page: Category filtering
  - **AC**: Filter by ghost/idle/rightsizing/advisor/governance
  - **FP**: 5

- **ACA-05-019**: FindingsTier1Page: Sort by savings/effort/risk
  - **AC**: Client-side sorting
  - **FP**: 3

- **ACA-05-020**: UpgradePage: Tier comparison table
  - **AC**: Show Tier 1/2/3 features, pricing
  - **FP**: 5

- **ACA-05-021**: UpgradePage: Checkout flow
  - **AC**: Call POST /v1/billing/checkout, redirect to Stripe
  - **FP**: 5

- **ACA-05-022**: UpgradePage: Billing portal link
  - **AC**: Link to GET /v1/billing/portal for subscription management
  - **FP**: 3

- **ACA-05-023**: Implement settings/profile page
  - **AC**: View entitlements, billing status, subscription list
  - **FP**: 5

### Feature 5.4: Admin Pages
**Stories**: 11

- **ACA-05-024**: AdminDashboardPage: KPI widgets
  - **AC**: Call GET /v1/admin/kpis, display MRR, scan counts, failure rates
  - **FP**: 8

- **ACA-05-025**: AdminDashboardPage: Revenue charts
  - **AC**: Stripe revenue, tier distribution, churn metrics
  - **FP**: 8

- **ACA-05-026**: AdminCustomersPage: Search and list customers
  - **AC**: Call GET /v1/admin/customers?query=, display tier/status/activity
  - **FP**: 8

- **ACA-05-027**: AdminCustomersPage: Grant entitlement action
  - **AC**: POST /v1/admin/entitlements/grant with tier/days/reason, confirmation modal
  - **FP**: 8

- **ACA-05-028**: AdminCustomersPage: Lock/unlock subscription action
  - **AC**: POST /v1/admin/subscriptions/{id}/lock with reason, confirmation
  - **FP**: 5

- **ACA-05-029**: AdminBillingPage: Stripe webhook health
  - **AC**: Display recent webhook events, success/fail counts
  - **FP**: 5

- **ACA-05-030**: AdminBillingPage: Reconcile Stripe action
  - **AC**: POST /v1/admin/stripe/reconcile, show progress
  - **FP**: 5

- **ACA-05-031**: AdminRunsPage: List scans/analyses/deliveries
  - **AC**: Call GET /v1/admin/runs?type=, filter by subscriptionId, display status/duration
  - **FP**: 8

- **ACA-05-032**: AdminControlsPage: Feature flag toggles
  - **AC**: Enable/disable features (Tier3 delivery, etc.)
  - **FP**: 5

- **ACA-05-033**: AdminControlsPage: Rate limit overrides
  - **AC**: Override scan frequency limits per subscription
  - **FP**: 5

- **ACA-05-039**: AdminAuditPage: View admin audit events
  - **AC**: Route `/admin/audit`, require `ACA_Admin`, call `GET /v1/admin/audit`, support filtering by subscriptionId, and avoid exposing raw Azure identifiers in the UI
  - **FP**: 5

### Feature 5.5: Shared Components
**Stories**: 5

- **ACA-05-034**: Implement Loading spinner component
  - **AC**: Reusable loading indicator, Fluent UI Spinner
  - **FP**: 2

- **ACA-05-035**: Implement ErrorState component
  - **AC**: Friendly error messages, retry button
  - **FP**: 3

- **ACA-05-036**: Implement DataTable component
  - **AC**: Reusable table with sorting, pagination
  - **FP**: 5

- **ACA-05-037**: Implement MoneyRangeBar component
  - **AC**: Visual bar for savings estimate range
  - **FP**: 3

- **ACA-05-038**: Implement EffortBadge and RiskBadge components
  - **AC**: Color-coded badges for effort/risk levels
  - **FP**: 2

---

## EPIC 06: API Service (FastAPI Backend)
**FP Estimate**: 323 FP  
**Stories**: 45

### Feature 6.1: API Infrastructure
**Stories**: 6

- **ACA-06-001**: Set up FastAPI application structure
  - **AC**: Main app, config, dependencies, routers
  - **FP**: 5

- **ACA-06-002**: Implement Cosmos DB connection factory
  - **AC**: Support key + managed identity auth
  - **FP**: 5

- **ACA-06-003**: Implement repository base classes
  - **AC**: Base repo for Cosmos operations, partition key enforcement
  - **FP**: 5

- **ACA-06-004**: Implement API error handling middleware
  - **AC**: Catch exceptions, return structured errors, log
  - **FP**: 5

- **ACA-06-005**: Implement CORS configuration
  - **AC**: Allow frontend origin, secure headers
  - **FP**: 3

- **ACA-06-006**: Deploy API as Azure Container App
  - **AC**: Dockerfile, CI/CD, managed identity wiring
  - **FP**: 8

- **ACA-06-046**: Wire FastAPI actor dependency for bearer-token auth
  - **AC**: Extract `Authorization: Bearer` token, validate via Entra helper, build actor context for downstream handlers, and return structured 401 responses for missing or malformed auth
  - **FP**: 5

### Feature 6.2: Health & Status Endpoints
**Stories**: 3

- **ACA-06-007**: Implement GET /v1/health
  - **AC**: Return status, version, timestamp
  - **FP**: 2

- **ACA-06-008**: Implement GET /v1/me (current user)
  - **AC**: Return clientId, tenantId, email, tier, allowedSubscriptions
  - **FP**: 5

- **ACA-06-009**: Implement GET /v1/status (system status)
  - **AC**: Check Cosmos, Key Vault, job health
  - **FP**: 5

### Feature 6.3: Pre-Flight Endpoints
**Stories**: 4

- **ACA-06-010**: Implement POST /v1/onboarding/preflight
  - **AC**: Execute pre-flight probes, return PreflightResponse
  - **FP**: 8

- **ACA-06-011**: Implement GET /v1/onboarding/preflight/{id}
  - **AC**: Retrieve stored pre-flight results
  - **FP**: 3

- **ACA-06-012**: Implement POST /v1/subscriptions/connect
  - **AC**: Store connection credentials, validate mode
  - **FP**: 8

- **ACA-06-013**: Implement POST /v1/subscriptions/{id}/disconnect
  - **AC**: Remove connection, mark as disconnected
  - **FP**: 5

### Feature 6.4: Collection Endpoints
**Stories**: 4

- **ACA-06-014**: Implement POST /v1/scans (start scan)
  - **AC**: Validate preflight, create scan record, trigger collector job
  - **FP**: 8

- **ACA-06-015**: Implement GET /v1/scans/{id}
  - **AC**: Return scan status, counts, errors
  - **FP**: 5

- **ACA-06-016**: Implement GET /v1/subscriptions/{id}/scans
  - **AC**: List scans for subscription, pagination
  - **FP**: 5

- **ACA-06-017**: Implement POST /v1/scans/{id}/cancel
  - **AC**: Cancel running scan if possible
  - **FP**: 5

### Feature 6.5: Analysis Endpoints
**Stories**: 4

- **ACA-06-018**: Implement POST /v1/analyses (start analysis)
  - **AC**: Validate scan completion, trigger analysis job
  - **FP**: 8

- **ACA-06-019**: Implement GET /v1/analyses/{id}
  - **AC**: Return analysis status, finding counts, summary
  - **FP**: 5

- **ACA-06-020**: Implement GET /v1/subscriptions/{id}/analyses
  - **AC**: List analyses for subscription
  - **FP**: 5

- **ACA-06-021**: Implement GET /v1/analyses/{id}/findings
  - **AC**: Return findings list with filters, pagination
  - **FP**: 8

### Feature 6.6: Report Endpoints
**Stories**: 5

- **ACA-06-022**: Implement GET /v1/reports/tier1
  - **AC**: Return Tier 1 findings (high-level only), enforce entitlement
  - **FP**: 8

- **ACA-06-023**: Implement GET /v1/reports/tier2
  - **AC**: Return Tier 2 findings (full details), enforce entitlement
  - **FP**: 8

- **ACA-06-024**: Implement GET /v1/reports/{id}/executive-summary
  - **AC**: Return executive summary JSON
  - **FP**: 5

- **ACA-06-025**: Implement GET /v1/reports/{id}/category/{category}
  - **AC**: Return findings filtered by category
  - **FP**: 5

- **ACA-06-026**: Implement GET /v1/reports/{id}/pareto
  - **AC**: Return top-N Pareto-ranked recommendations
  - **FP**: 5

### Feature 6.7: Deliverable Endpoints
**Stories**: 4

- **ACA-06-027**: Implement POST /v1/deliverables (generate Tier 3 package)
  - **AC**: Validate entitlement, trigger delivery job, return deliverableId
  - **FP**: 8

- **ACA-06-028**: Implement GET /v1/deliverables/{id}
  - **AC**: Return deliverable status (pending/generating/ready)
  - **FP**: 5

- **ACA-06-029**: Implement GET /v1/deliverables/{id}/download
  - **AC**: Return SAS URL for ZIP download, enforce entitlement
  - **FP**: 5

- **ACA-06-030**: Implement GET /v1/subscriptions/{id}/deliverables
  - **AC**: List deliverables for subscription
  - **FP**: 5

### Feature 6.8: Admin Endpoints
**Stories**: 12

- **ACA-06-031**: Implement GET /v1/admin/kpis
  - **AC**: Return MRR, scan counts, failure rates, churn
  - **FP**: 8

- **ACA-06-032**: Implement GET /v1/admin/customers
  - **AC**: Search/list customers, return tier/status/activity
  - **FP**: 8

- **ACA-06-033**: Implement POST /v1/admin/entitlements/grant
  - **AC**: Grant tier for days with reason, audit log
  - **FP**: 8

- **ACA-06-034**: Implement POST /v1/admin/subscriptions/{id}/lock
  - **AC**: Lock subscription with reason, prevent scans
  - **FP**: 5

- **ACA-06-035**: Implement POST /v1/admin/subscriptions/{id}/unlock
  - **AC**: Unlock subscription, resume access
  - **FP**: 5

- **ACA-06-036**: Implement POST /v1/admin/stripe/reconcile
  - **AC**: Sync Stripe subscriptions with entitlements
  - **FP**: 8

- **ACA-06-037**: Implement GET /v1/admin/runs
  - **AC**: List scans/analyses/deliveries across all subscriptions
  - **FP**: 8

- **ACA-06-038**: Implement GET /v1/admin/webhooks
  - **AC**: List recent webhook events, success/fail counts
  - **FP**: 5

- **ACA-06-039**: Implement POST /v1/admin/controls/feature-flags
  - **AC**: Set feature flags globally or per subscription
  - **FP**: 5

- **ACA-06-044**: Implement GET /v1/admin/customers/{subscriptionId}
  - **AC**: Return entitlement, stripeCustomerId, locked state, and latest scan/analysis/delivery timestamps for a single subscription; require `ACA_Admin` or `ACA_Support`
  - **FP**: 5

- **ACA-06-045**: Implement GET /v1/admin/audit
  - **AC**: List admin audit events with `subscriptionId` filter and bounded limit, require `ACA_Admin`, and return actor/action/timestamp payloads suitable for investigations
  - **FP**: 5

- **ACA-06-047**: Implement Cosmos-backed admin repositories for customers, runs, and audit
  - **AC**: Query existing entitlements, clients, scans, analyses, deliverables, and admin-audit containers using partition-aware queries where possible; support customer search/detail, run listing, and audit event listing with bounded limits
  - **FP**: 8

### Feature 6.9: Billing & Entitlements Endpoints
**Stories**: 4

- **ACA-06-040**: Implement GET /v1/entitlements
  - **AC**: Return subscription entitlements (tier, paymentStatus, canViewTier2, canGenerateTier3)
  - **FP**: 5

- **ACA-06-041**: Implement POST /v1/checkout/tier2
  - **AC**: Create Stripe checkout session for Tier 2
  - **FP**: 8

- **ACA-06-042**: Implement POST /v1/checkout/tier3
  - **AC**: Create Stripe checkout session for Tier 3
  - **FP**: 8

- **ACA-06-043**: Implement GET /v1/billing/portal
  - **AC**: Return Stripe customer portal URL
  - **FP**: 5

---

## EPIC 07: Billing & Payment Integration
**FP Estimate**: 180 FP  
**Stories**: 22

### Feature 7.1: Stripe Integration
**Stories**: 6

- **ACA-07-001**: Implement Stripe SDK client
  - **AC**: Initialize with secret key, support checkout/subscriptions/portal
  - **FP**: 5

- **ACA-07-002**: Create Stripe products and prices
  - **AC**: Tier 2 one-time, Tier 2 subscription, Tier 3 one-time
  - **FP**: 3

- **ACA-07-003**: Implement checkout session creation
  - **AC**: Create session with metadata (aca_tier, aca_subscription_id, aca_analysis_id)
  - **FP**: 8

- **ACA-07-004**: Implement billing portal session creation
  - **AC**: Create portal session for subscription management
  - **FP**: 5

- **ACA-07-005**: Implement webhook signature verification
  - **AC**: Verify Stripe-Signature header, parse event
  - **FP**: 5

- **ACA-07-006**: Store Stripe secrets in Key Vault
  - **AC**: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, price IDs
  - **FP**: 3

### Feature 7.2: Entitlements Management
**Stories**: 8

- **ACA-07-007**: Design entitlements Cosmos container
  - **AC**: Partition by subscriptionId, schema: tier, paymentStatus, stripeCustomerId
  - **FP**: 5

- **ACA-07-008**: Implement EntitlementsRepo
  - **AC**: Get, upsert entitlements by subscriptionId
  - **FP**: 5

- **ACA-07-009**: Implement grant_tier2 operation
  - **AC**: Upsert entitlement, set tier=2, paymentStatus=active
  - **FP**: 5

- **ACA-07-010**: Implement grant_tier3 operation
  - **AC**: Upsert entitlement, set tier=3, paymentStatus=active
  - **FP**: 5

- **ACA-07-011**: Implement entitlement expiry logic
  - **AC**: Support time-limited entitlements (trial, goodwill)
  - **FP**: 5

- **ACA-07-012**: Implement entitlement check middleware
  - **AC**: Enforce tier gating on endpoints
  - **FP**: 8

- **ACA-07-013**: Implement entitlement revocation
  - **AC**: Set paymentStatus=canceled, block access
  - **FP**: 5

- **ACA-07-014**: Implement entitlement audit trail
  - **AC**: Log all changes with timestamp, actor, reason
  - **FP**: 5

### Feature 7.3: Webhook Event Handling
**Stories**: 8

- **ACA-07-015**: Handle checkout.session.completed event
  - **AC**: Grant entitlement, trigger delivery for Tier 3
  - **FP**: 8

- **ACA-07-016**: Handle invoice.paid event
  - **AC**: Keep Tier 2 active for recurring subscription
  - **FP**: 5

- **ACA-07-017**: Handle customer.subscription.updated event
  - **AC**: Sync paymentStatus (active/past_due/canceled)
  - **FP**: 5

- **ACA-07-018**: Handle customer.subscription.deleted event
  - **AC**: Revoke Tier 2, set paymentStatus=canceled
  - **FP**: 5

- **ACA-07-019**: Handle invoice.payment_failed event
  - **AC**: Set paymentStatus=past_due, notify admin
  - **FP**: 5

- **ACA-07-020**: Implement webhook idempotency
  - **AC**: Store event IDs, skip duplicate events
  - **FP**: 5

- **ACA-07-021**: Implement webhook error handling
  - **AC**: Log errors, return 200 to Stripe, alert on failures
  - **FP**: 5

- **ACA-07-022**: Implement webhook replay for reconciliation
  - **AC**: Admin tool to replay missed webhooks
  - **FP**: 8

---

## EPIC 08: Infrastructure & Deployment
**FP Estimate**: 200 FP  
**Stories**: 28

### Feature 8.1: Cosmos DB Setup
**Stories**: 6

- **ACA-08-001**: Create Cosmos DB account
  - **AC**: Session consistency, backup enabled, free tier for dev
  - **FP**: 3

- **ACA-08-002**: Create ACA database
  - **AC**: Set throughput (400 RU/s default)
  - **FP**: 2

- **ACA-08-003**: Create scans container
  - **AC**: Partition key /subscriptionId, throughput 400 RU/s
  - **FP**: 2

- **ACA-08-004**: Create inventories container
  - **AC**: Partition key /subscriptionId
  - **FP**: 2

- **ACA-08-005**: Create cost-data container
  - **AC**: Partition key /subscriptionId
  - **FP**: 2

- **ACA-08-006**: Create advisor, findings, entitlements, payments, clients, stripe_customer_map containers
  - **AC**: Each with appropriate partition key strategy
  - **FP**: 3

### Feature 8.2: Key Vault Setup
**Stories**: 5

- **ACA-08-007**: Create Key Vault
  - **AC**: RBAC-enabled, soft delete, purge protection
  - **FP**: 3

- **ACA-08-008**: Store Cosmos connection secrets
  - **AC**: COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DB_NAME
  - **FP**: 2

- **ACA-08-009**: Store Stripe secrets
  - **AC**: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, price IDs
  - **FP**: 2

- **ACA-08-010**: Store Azure auth secrets
  - **AC**: ENTRA_TENANT_ID, ENTRA_AUDIENCE (if needed)
  - **FP**: 2

- **ACA-08-011**: Configure Key Vault RBAC for managed identities
  - **AC**: Grant Key Vault Secrets User to UAMI
  - **FP**: 3

### Feature 8.3: Container Registry
**Stories**: 3

- **ACA-08-012**: Create Azure Container Registry (ACR)
  - **AC**: Standard tier, admin disabled, managed identity access
  - **FP**: 3

- **ACA-08-013**: Build and push API image
  - **AC**: Dockerfile, tag with version, push to ACR
  - **FP**: 5

- **ACA-08-014**: Build and push collector/analysis/delivery job images
  - **AC**: Three separate images, push to ACR
  - **FP**: 5

### Feature 8.4: Container Apps Environment
**Stories**: 4

- **ACA-08-015**: Create Container Apps Environment
  - **AC**: Workload profiles, Log Analytics integration
  - **FP**: 5

- **ACA-08-016**: Create managed identity (UAMI)
  - **AC**: Single identity for all services
  - **FP**: 3

- **ACA-08-017**: Assign UAMI roles
  - **AC**: Key Vault Secrets User, Contributor (for job triggering)
  - **FP**: 3

- **ACA-08-018**: Configure environment variables
  - **AC**: Key Vault references for secrets
  - **FP**: 3

### Feature 8.5: Container Apps Deployment
**Stories**: 4

- **ACA-08-019**: Deploy API as Container App
  - **AC**: Ingress enabled (external), autoscaling, managed identity
  - **FP**: 8

- **ACA-08-020**: Deploy collector as Container App Job
  - **AC**: Manual trigger, retry policy, managed identity
  - **FP**: 8

- **ACA-08-021**: Deploy analysis as Container App Job
  - **AC**: Manual trigger, managed identity
  - **FP**: 5

- **ACA-08-022**: Deploy delivery as Container App Job
  - **AC**: Manual trigger, managed identity
  - **FP**: 5

### Feature 8.6: Azure API Management (Optional)
**Stories**: 6

- **ACA-08-023**: Create APIM instance
  - **AC**: Developer tier for Phase 1, Standard for Phase 2
  - **FP**: 5

- **ACA-08-024**: Import API definition (OpenAPI)
  - **AC**: Generate OpenAPI spec from FastAPI, import to APIM
  - **FP**: 5

- **ACA-08-025**: Implement APIM caching policy
  - **AC**: Cache entitlements lookups for 60s
  - **FP**: 5

- **ACA-08-026**: Implement APIM rate limiting policy
  - **AC**: Tier-based rate limits (Tier 1: 1 scan/30d, Tier 2: unlimited)
  - **FP**: 5

- **ACA-08-027**: Implement APIM tier gating policy
  - **AC**: Enforce Tier 2/3 entitlement checks
  - **FP**: 8

- **ACA-08-028**: Configure APIM custom domain and SSL
  - **AC**: api.aca.example.com, Let's Encrypt or custom cert
  - **FP**: 5

---

## EPIC 09: Analytics & Telemetry
**FP Estimate**: 90 FP  
**Stories**: 12

### Feature 9.1: Google Analytics 4 Integration
**Stories**: 4

- **ACA-09-001**: Implement Google Tag Manager (GTM) integration
  - **AC**: GTM script in index.html, dataLayer push
  - **FP**: 5

- **ACA-09-002**: Implement GA4 event tracking
  - **AC**: Track login_success, scan_started, findings_viewed_tier1, etc.
  - **FP**: 8

- **ACA-09-003**: Implement privacy-safe property mapping
  - **AC**: Never send subscriptionId/tenantId/email, use opaque IDs only
  - **FP**: 5

- **ACA-09-004**: Implement consent banner
  - **AC**: localStorage-based consent, block tracking until accepted
  - **FP**: 5

### Feature 9.2: Microsoft Clarity Integration
**Stories**: 3

- **ACA-09-005**: Implement Clarity script loading
  - **AC**: Load via GTM or direct script tag
  - **FP**: 3

- **ACA-09-006**: Implement Clarity custom events
  - **AC**: Mirror key events (preflight_fail, unlock_cta_clicked, checkout_started)
  - **FP**: 5

- **ACA-09-007**: Implement Clarity masking
  - **AC**: Mask sensitive input fields (service principal secret)
  - **FP**: 3

### Feature 9.3: Custom Event Taxonomy
**Stories**: 5

- **ACA-09-008**: Define onboarding events
  - **AC**: login_success, subscription_selected, preflight_started/pass/fail
  - **FP**: 3

- **ACA-09-009**: Define core usage events
  - **AC**: scan_started/completed, analysis_started/completed
  - **FP**: 3

- **ACA-09-010**: Define conversion funnel events
  - **AC**: findings_viewed_tier1, unlock_cta_clicked, checkout_started/completed
  - **FP**: 3

- **ACA-09-011**: Define deliverable events
  - **AC**: deliverable_ready, deliverable_downloaded
  - **FP**: 3

- **ACA-09-012**: Implement TelemetryProvider component
  - **AC**: Wrap app, enable/disable via env var, consent check
  - **FP**: 5

---

## EPIC 10: Phase 6 - Continuous Monitoring & Optimization
**FP Estimate**: 220 FP  
**Stories**: 28

### Feature 10.1: Scheduled Rescans
**Stories**: 5

- **ACA-10-001**: Implement scan scheduler service
  - **AC**: Cron-based scheduler, daily/weekly/monthly frequencies
  - **FP**: 8

- **ACA-10-002**: Implement subscription scan schedule configuration
  - **AC**: Per-subscription schedule settings
  - **FP**: 5

- **ACA-10-003**: Implement scheduled scan triggering
  - **AC**: Automatically trigger collector job on schedule
  - **FP**: 5

- **ACA-10-004**: Implement scan history tracking
  - **AC**: Maintain scan history with dates, results
  - **FP**: 5

- **ACA-10-005**: Implement scan failure alerting
  - **AC**: Notify admin on repeated scan failures
  - **FP**: 5

### Feature 10.2: Drift Detection
**Stories**: 6

- **ACA-10-006**: Implement scan comparison engine
  - **AC**: Compare current scan to baseline scan
  - **FP**: 8

- **ACA-10-007**: Detect new resources introduced
  - **AC**: Identify resources not in baseline
  - **FP**: 5

- **ACA-10-008**: Detect new waste introduced
  - **AC**: Identify new ghost/idle resources
  - **FP**: 5

- **ACA-10-009**: Detect savings actions not implemented
  - **AC**: Compare findings, identify still-open items
  - **FP**: 8

- **ACA-10-010**: Detect policy compliance regression
  - **AC**: Identify new policy violations
  - **FP**: 5

- **ACA-10-011**: Generate drift report
  - **AC**: Summary of changes (positive/negative)
  - **FP**: 5

### Feature 10.3: Savings Verification
**Stories**: 6

- **ACA-10-012**: Implement before/after cost comparison
  - **AC**: Compare cost trends pre/post recommendations
  - **FP**: 8

- **ACA-10-013**: Implement expected vs actual savings tracking
  - **AC**: Track projected savings vs realized savings
  - **FP**: 8

- **ACA-10-014**: Implement ROI calculation
  - **AC**: Calculate ROI for ACA service
  - **FP**: 5

- **ACA-10-015**: Implement savings verification report
  - **AC**: Generate report showing realized savings
  - **FP**: 5

- **ACA-10-016**: Implement finding closure tracking
  - **AC**: Mark findings as resolved, verify with data
  - **FP**: 5

- **ACA-10-017**: Implement pay-for-performance support
  - **AC**: Track verified savings for performance-based billing
  - **FP**: 8

### Feature 10.4: Subscription Health Scoring
**Stories**: 5

- **ACA-10-018**: Implement waste index calculation
  - **AC**: Waste as % of total spend
  - **FP**: 5

- **ACA-10-019**: Implement optimization maturity score
  - **AC**: Based on findings resolved, trends
  - **FP**: 8

- **ACA-10-020**: Implement governance posture score
  - **AC**: Based on policy compliance, tagging, naming
  - **FP**: 5

- **ACA-10-021**: Implement cost stability score
  - **AC**: Based on cost variance, anomalies
  - **FP**: 5

- **ACA-10-022**: Implement risk level score
  - **AC**: Based on high-risk misconfigurations
  - **FP**: 5

### Feature 10.5: Alerting & Insights
**Stories**: 6

- **ACA-10-023**: Implement new high-impact waste alerts
  - **AC**: Email/webhook alert on major new findings
  - **FP**: 5

- **ACA-10-024**: Implement budget threat alerts
  - **AC**: Alert on projected budget overruns
  - **FP**: 5

- **ACA-10-025**: Implement governance violation alerts
  - **AC**: Alert on new policy violations
  - **FP**: 5

- **ACA-10-026**: Implement performance regression alerts
  - **AC**: Alert on health score deterioration
  - **FP**: 5

- **ACA-10-027**: Implement alert routing configuration
  - **AC**: Per-subscription alert destinations (email, Teams, Slack)
  - **FP**: 5

- **ACA-10-028**: Implement alert dashboard
  - **AC**: View recent alerts, acknowledge, snooze
  - **FP**: 5

---

## EPIC 11: Phase 7 - Enterprise Multi-Tenant Platform
**FP Estimate**: 280 FP  
**Stories**: 35

### Feature 11.1: Multi-Tenant Isolation
**Stories**: 6

- **ACA-11-001**: Enforce partition key isolation in all queries
  - **AC**: All Cosmos queries must filter by subscriptionId
  - **FP**: 8

- **ACA-11-002**: Implement tenant isolation validation middleware
  - **AC**: Validate user can only access their subscriptions
  - **FP**: 8

- **ACA-11-003**: Implement cross-tenant query prevention
  - **AC**: Detect and block attempts to access other subscriptions
  - **FP**: 5

- **ACA-11-004**: Implement tenant-scoped encryption
  - **AC**: Customer-managed keys per tenant (for enterprise)
  - **FP**: 8

- **ACA-11-005**: Implement tenant audit trail
  - **AC**: Log all data access with tenant context
  - **FP**: 5

- **ACA-11-006**: Conduct tenant isolation security audit
  - **AC**: Penetration test, verify no cross-tenant leaks
  - **FP**: 8

### Feature 11.2: Organization Management
**Stories**: 7

- **ACA-11-007**: Design organizations Cosmos container
  - **AC**: Schema: orgId, name, subscriptions[], users[]
  - **FP**: 5

- **ACA-11-008**: Implement organization CRUD operations
  - **AC**: Create, read, update, delete organizations
  - **FP**: 8

- **ACA-11-009**: Implement subscription-to-organization mapping
  - **AC**: Many subscriptions per organization
  - **FP**: 5

- **ACA-11-010**: Implement organization-level reporting
  - **AC**: Aggregate findings/costs across org subscriptions
  - **FP**: 8

- **ACA-11-011**: Implement organization hierarchy support
  - **AC**: Parent-child organization relationships (business units)
  - **FP**: 8

- **ACA-11-012**: Implement organization billing aggregation
  - **AC**: Consolidated billing for organization
  - **FP**: 8

- **ACA-11-013**: Implement organization admin role
  - **AC**: Org admins can manage subscriptions/users within org
  - **FP**: 8

### Feature 11.3: Role-Based Access Control (RBAC)
**Stories**: 8

- **ACA-11-014**: Design RBAC model
  - **AC**: Roles: OrgAdmin, SubscriptionOwner, Viewer, Auditor, Consultant
  - **FP**: 5

- **ACA-11-015**: Implement role assignment API
  - **AC**: Assign roles to users at org/subscription scope
  - **FP**: 8

- **ACA-11-016**: Implement permission checking middleware
  - **AC**: Verify user role before allowing operations
  - **FP**: 8

- **ACA-11-017**: Implement OrgAdmin role enforcement
  - **AC**: Full access to org subscriptions/users/billing
  - **FP**: 5

- **ACA-11-018**: Implement SubscriptionOwner role enforcement
  - **AC**: Full access to single subscription
  - **FP**: 5

- **ACA-11-019**: Implement Viewer role enforcement
  - **AC**: Read-only access to reports
  - **FP**: 3

- **ACA-11-020**: Implement Auditor role enforcement
  - **AC**: Read-only access to all data including audit logs
  - **FP**: 5

- **ACA-11-021**: Implement Consultant role enforcement
  - **AC**: Access to multiple client subscriptions (MSP mode)
  - **FP**: 8

### Feature 11.4: Portfolio Management
**Stories**: 7

- **ACA-11-022**: Implement portfolio dashboard
  - **AC**: View all subscriptions in org, aggregate KPIs
  - **FP**: 8

- **ACA-11-023**: Implement cross-subscription cost aggregation
  - **AC**: Total spend, total waste, trends across portfolio
  - **FP**: 8

- **ACA-11-024**: Implement cross-subscription findings rollup
  - **AC**: Top opportunities across all subscriptions
  - **FP**: 8

- **ACA-11-025**: Implement portfolio-level benchmarking
  - **AC**: Compare subscriptions within portfolio
  - **FP**: 8

- **ACA-11-026**: Implement portfolio filters and drill-down
  - **AC**: Filter by business unit, environment, region
  - **FP**: 5

- **ACA-11-027**: Implement portfolio export
  - **AC**: Export aggregate data to Excel/CSV
  - **FP**: 5

- **ACA-11-028**: Implement portfolio health score
  - **AC**: Aggregate health across subscriptions
  - **FP**: 5

### Feature 11.5: Usage Metering & Billing
**Stories**: 7

- **ACA-11-029**: Design usage metering model
  - **AC**: Meter by subscription count, scan frequency, data volume
  - **FP**: 8

- **ACA-11-030**: Implement usage tracking
  - **AC**: Record scans, analyses, deliverables, API calls
  - **FP**: 8

- **ACA-11-031**: Implement usage aggregation
  - **AC**: Roll up usage by organization, subscription
  - **FP**: 5

- **ACA-11-032**: Implement pricing model configuration
  - **AC**: Support per-subscription, per-scan, volume-based pricing
  - **FP**: 8

- **ACA-11-033**: Implement invoice generation
  - **AC**: Monthly invoice with usage breakdown
  - **FP**: 8

- **ACA-11-034**: Integrate with Stripe metered billing
  - **AC**: Report usage to Stripe for subscription billing
  - **FP**: 8

- **ACA-11-035**: Implement usage dashboard for customers
  - **AC**: View current usage, projected costs
  - **FP**: 5

---

## EPIC 12: Phase 8 - Autonomous Optimization & Action Platform
**FP Estimate**: 310 FP  
**Stories**: 38

### Feature 12.1: Action Planning Engine
**Stories**: 6

- **ACA-12-001**: Design action plan schema
  - **AC**: Plan contains steps, dependencies, rollback, risk
  - **FP**: 5

- **ACA-12-002**: Implement finding-to-action-plan mapper
  - **AC**: Map findings to executable action plans
  - **FP**: 8

- **ACA-12-003**: Implement dependency resolver
  - **AC**: Order actions by dependencies (e.g., stop VM before resize)
  - **FP**: 8

- **ACA-12-004**: Implement risk assessment
  - **AC**: Calculate risk score for each action
  - **FP**: 5

- **ACA-12-005**: Implement rollback strategy generator
  - **AC**: Generate undo commands for each action
  - **FP**: 8

- **ACA-12-006**: Store action plans in Cosmos DB
  - **AC**: Create action_plans container
  - **FP**: 5

### Feature 12.2: Impact Simulation
**Stories**: 7

- **ACA-12-007**: Implement cost impact simulator
  - **AC**: Predict cost change from action
  - **FP**: 8

- **ACA-12-008**: Implement availability impact simulator
  - **AC**: Assess downtime risk from action
  - **FP**: 8

- **ACA-12-009**: Implement performance impact simulator
  - **AC**: Predict performance change from action
  - **FP**: 8

- **ACA-12-010**: Implement compliance impact simulator
  - **AC**: Check if action maintains compliance
  - **FP**: 5

- **ACA-12-011**: Implement simulation confidence scoring
  - **AC**: Confidence level based on data quality
  - **FP**: 5

- **ACA-12-012**: Generate simulation report
  - **AC**: "What-if" report with predicted outcomes
  - **FP**: 5

- **ACA-12-013**: Implement multi-action simulation
  - **AC**: Simulate effect of multiple actions together
  - **FP**: 8

### Feature 12.3: Approval Workflows
**Stories**: 8

- **ACA-12-014**: Design approval workflow types
  - **AC**: Manual, scheduled, policy-based, autonomous
  - **FP**: 5

- **ACA-12-015**: Implement manual approval workflow
  - **AC**: Send notification, wait for approval, timeout
  - **FP**: 8

- **ACA-12-016**: Implement scheduled approval workflow
  - **AC**: Auto-approve at specified time (e.g., maintenance window)
  - **FP**: 5

- **ACA-12-017**: Implement policy-based approval
  - **AC**: Auto-approve if meets criteria (low-risk, small cost)
  - **FP**: 8

- **ACA-12-018**: Implement multi-level approval
  - **AC**: Require multiple approvals for high-risk actions
  - **FP**: 8

- **ACA-12-019**: Implement approval dashboard
  - **AC**: View pending approvals, approve/reject
  - **FP**: 8

- **ACA-12-020**: Implement approval audit trail
  - **AC**: Log all approvals with approver, timestamp, decision
  - **FP**: 5

- **ACA-12-021**: Implement approval expiration
  - **AC**: Auto-reject if not approved within timeout
  - **FP**: 5

### Feature 12.4: Execution Engine
**Stories**: 8

- **ACA-12-022**: Implement Azure ARM execution adapter
  - **AC**: Execute actions via ARM REST API
  - **FP**: 8

- **ACA-12-023**: Implement PowerShell execution adapter
  - **AC**: Execute generated PS scripts
  - **FP**: 8

- **ACA-12-024**: Implement Azure CLI execution adapter
  - **AC**: Execute actions via Azure CLI
  - **FP**: 5

- **ACA-12-025**: Implement Terraform execution adapter
  - **AC**: Generate and apply Terraform changes
  - **FP**: 8

- **ACA-12-026**: Implement execution retry logic
  - **AC**: Retry failed actions with backoff
  - **FP**: 5

- **ACA-12-027**: Implement execution progress tracking
  - **AC**: Track step-by-step progress, update status
  - **FP**: 5

- **ACA-12-028**: Implement execution rollback on failure
  - **AC**: Auto-rollback if execution fails
  - **FP**: 8

- **ACA-12-029**: Store execution results in Cosmos DB
  - **AC**: Create executions container with results, logs
  - **FP**: 5

### Feature 12.5: Verification Engine
**Stories**: 6

- **ACA-12-030**: Implement post-execution verification
  - **AC**: Re-scan resources after actions, verify changes
  - **FP**: 8

- **ACA-12-031**: Implement savings realization verification
  - **AC**: Compare costs before/after, calculate actual savings
  - **FP**: 8

- **ACA-12-032**: Implement system health verification
  - **AC**: Check for availability, performance regressions
  - **FP**: 8

- **ACA-12-033**: Implement compliance verification
  - **AC**: Verify actions maintained compliance
  - **FP**: 5

- **ACA-12-034**: Generate verification report
  - **AC**: Report on verification results
  - **FP**: 5

- **ACA-12-035**: Implement verification failure alerting
  - **AC**: Alert if verification detects issues
  - **FP**: 5

### Feature 12.6: Learning System
**Stories**: 3

- **ACA-12-036**: Implement outcome tracking
  - **AC**: Track success/failure of actions, save patterns
  - **FP**: 8

- **ACA-12-037**: Implement recommendation improvement
  - **AC**: Adjust confidence/risk based on historical outcomes
  - **FP**: 8

- **ACA-12-038**: Implement execution pattern recognition
  - **AC**: Identify successful patterns for automation
  - **FP**: 8

---

## EPIC 13: Phase 9 - Predictive & Strategic Optimization
**FP Estimate**: 260 FP  
**Stories**: 32

### Feature 13.1: Cost Forecasting
**Stories**: 6

- **ACA-13-001**: Implement historical trend analysis
  - **AC**: Analyze cost trends over time
  - **FP**: 8

- **ACA-13-002**: Implement time series forecasting model
  - **AC**: Predict future costs (e.g., Prophet, ARIMA)
  - **FP**: 13

- **ACA-13-003**: Implement growth pattern detection
  - **AC**: Identify linear, exponential, seasonal growth
  - **FP**: 8

- **ACA-13-004**: Implement seasonality modeling
  - **AC**: Account for seasonal variations
  - **FP**: 8

- **ACA-13-005**: Implement confidence intervals
  - **AC**: Provide prediction ranges (low/medium/high)
  - **FP**: 5

- **ACA-13-006**: Implement cost forecast dashboard
  - **AC**: Visualize forecast with historical data
  - **FP**: 8

### Feature 13.2: Waste Trajectory Modeling
**Stories**: 4

- **ACA-13-007**: Implement waste trend analysis
  - **AC**: Track waste % over time
  - **FP**: 5

- **ACA-13-008**: Classify waste trajectory
  - **AC**: Stable, improving, deteriorating, exploding
  - **FP**: 5

- **ACA-13-009**: Predict future waste levels
  - **AC**: Forecast waste for next 6-12 months
  - **FP**: 8

- **ACA-13-010**: Generate waste trajectory report
  - **AC**: Report on waste trends and predictions
  - **FP**: 5

### Feature 13.3: Scenario Simulation
**Stories**: 8

- **ACA-13-011**: Implement reservation adoption scenario
  - **AC**: Simulate effect of purchasing RIs/savings plans
  - **FP**: 8

- **ACA-13-012**: Implement PaaS refactoring scenario
  - **AC**: Simulate cost of migrating IaaS to PaaS
  - **FP**: 8

- **ACA-13-013**: Implement region consolidation scenario
  - **AC**: Simulate cost of consolidating to fewer regions
  - **FP**: 8

- **ACA-13-014**: Implement environment shutdown scenario
  - **AC**: Simulate cost reduction from shutting down envs
  - **FP**: 5

- **ACA-13-015**: Implement service migration scenario
  - **AC**: Simulate cost of migrating to different services
  - **FP**: 8

- **ACA-13-016**: Implement usage increase scenario
  - **AC**: Simulate cost of 2x, 3x, 5x usage growth
  - **FP**: 8

- **ACA-13-017**: Implement multi-cloud scenario
  - **AC**: Simulate cost of hybrid Azure + AWS/GCP
  - **FP**: 8

- **ACA-13-018**: Generate scenario comparison report
  - **AC**: Side-by-side comparison of scenarios
  - **FP**: 5

### Feature 13.4: Commitment Optimization
**Stories**: 6

- **ACA-13-019**: Analyze reservation opportunities
  - **AC**: Identify stable workloads for reservations
  - **FP**: 8

- **ACA-13-020**: Calculate optimal reservation term
  - **AC**: 1-year vs 3-year ROI analysis
  - **FP**: 8

- **ACA-13-021**: Calculate optimal reservation coverage
  - **AC**: % of compute to reserve
  - **FP**: 8

- **ACA-13-022**: Analyze savings plan opportunities
  - **AC**: Identify workloads suitable for savings plans
  - **FP**: 8

- **ACA-13-023**: Generate commitment recommendation report
  - **AC**: Recommend specific RIs/plans with ROI
  - **FP**: 5

- **ACA-13-024**: Implement commitment tracking
  - **AC**: Track existing commitments, utilization, savings
  - **FP**: 5

### Feature 13.5: Architecture Strategy Guidance
**Stories**: 5

- **ACA-13-025**: Assess serverless migration opportunities
  - **AC**: Identify workloads suitable for Functions/Logic Apps
  - **FP**: 8

- **ACA-13-026**: Assess containerization opportunities
  - **AC**: Identify workloads suitable for AKS/Container Apps
  - **FP**: 8

- **ACA-13-027**: Assess storage tiering opportunities
  - **AC**: Recommend blob/archive/cool tier strategies
  - **FP**: 5

- **ACA-13-028**: Assess data architecture changes
  - **AC**: Recommend DB consolidation, caching strategies
  - **FP**: 8

- **ACA-13-029**: Generate architecture modernization roadmap
  - **AC**: Phased plan for architecture changes
  - **FP**: 8

### Feature 13.6: Portfolio Planning
**Stories**: 3

- **ACA-13-030**: Implement budget allocation recommendations
  - **AC**: Recommend budget by business unit based on trends
  - **FP**: 8

- **ACA-13-031**: Implement cost governance strategy recommendations
  - **AC**: Recommend policies, budgets, alerts
  - **FP**: 8

- **ACA-13-032**: Generate portfolio strategy report
  - **AC**: Executive report on portfolio optimization strategy
  - **FP**: 8

---

## EPIC 14: Phase 10 - Ecosystem & Intelligence Platform
**FP Estimate**: 320 FP  
**Stories**: 40

### Feature 14.1: Multi-Cloud Abstraction
**Stories**: 8

- **ACA-14-001**: Design multi-cloud data model
  - **AC**: Unified schema for Azure, AWS, GCP resources
  - **FP**: 13

- **ACA-14-002**: Implement AWS data collection
  - **AC**: Collect inventory, costs from AWS
  - **FP**: 13

- **ACA-14-003**: Implement GCP data collection
  - **AC**: Collect inventory, costs from GCP
  - **FP**: 13

- **ACA-14-004**: Implement private cloud data collection
  - **AC**: Collect data from on-prem VMware, OpenStack
  - **FP**: 13

- **ACA-14-005**: Implement unified cost aggregation
  - **AC**: Aggregate costs across all clouds
  - **FP**: 8

- **ACA-14-006**: Implement unified findings generation
  - **AC**: Apply rules across multi-cloud environment
  - **FP**: 13

- **ACA-14-007**: Implement cloud-specific rule adapters
  - **AC**: Translate rules for AWS/GCP specifics
  - **FP**: 8

- **ACA-14-008**: Implement multi-cloud dashboard
  - **AC**: Unified view of all cloud costs and waste
  - **FP**: 8

### Feature 14.2: Plugin & Extension Ecosystem
**Stories**: 8

- **ACA-14-009**: Design plugin API specification
  - **AC**: Define plugin contract, hooks, data access
  - **FP**: 8

- **ACA-14-010**: Implement plugin registry
  - **AC**: Discover, load, manage plugins
  - **FP**: 8

- **ACA-14-011**: Implement custom rule plugins
  - **AC**: Allow third parties to add analysis rules
  - **FP**: 8

- **ACA-14-012**: Implement industry module plugins
  - **AC**: Healthcare, finance, retail-specific modules
  - **FP**: 8

- **ACA-14-013**: Implement compliance pack plugins
  - **AC**: HIPAA, PCI-DSS, SOC2 compliance modules
  - **FP**: 8

- **ACA-14-014**: Implement integration plugins
  - **AC**: Integrate with ServiceNow, Jira, etc.
  - **FP**: 8

- **ACA-14-015]: Implement plugin sandboxing
  - **AC**: Isolate plugin execution for security
  - **FP**: 8

- **ACA-14-016**: Implement plugin marketplace UI
  - **AC**: Browse, install, manage plugins
  - **FP**: 8

### Feature 14.3: Benchmark Intelligence
**Stories**: 6

- **ACA-14-017**: Design anonymized data aggregation
  - **AC**: Collect anonymized waste patterns across customers
  - **FP**: 8

- **ACA-14-018**: Implement industry classification
  - **AC**: Categorize subscriptions by industry
  - **FP**: 5

- **ACA-14-019**: Implement peer comparison
  - **AC**: Compare subscription to industry peers
  - **FP**: 8

- **ACA-14-020**: Implement efficiency percentile ranking
  - **AC**: "You are in top 25% of efficiency"
  - **FP**: 5

- **ACA-14-021**: Generate benchmark report
  - **AC**: Report on peer comparison
  - **FP**: 5

- **ACA-14-022**: Implement benchmark dashboard
  - **AC**: Real-time benchmark visualization
  - **FP**: 8

### Feature 14.4: Marketplace
**Stories**: 6

- **ACA-14-023**: Implement marketplace backend
  - **AC**: Manage listings, purchases, payments
  - **FP**: 13

- **ACA-14-024**: Implement ISV onboarding
  - **AC**: ISVs can submit plugins/modules
  - **FP**: 8

- **ACA-14-025**: Implement revenue sharing
  - **AC**: Split revenue with ISVs (e.g., 70/30)
  - **FP**: 8

- **ACA-14-026**: Implement marketplace UI
  - **AC**: Browse, purchase, install marketplace items
  - **FP**: 8

- **ACA-14-027**: Implement reviews and ratings
  - **AC**: Users can review plugin/modules
  - **FP**: 5

- **ACA-14-028**: Implement marketplace analytics
  - **AC**: Track downloads, revenue, trending
  - **FP**: 5

### Feature 14.5: Data Intelligence Network
**Stories**: 6

- **ACA-14-029**: Implement anonymized data lake
  - **AC**: Store aggregated anonymous patterns
  - **FP**: 8

- **ACA-14-030**: Implement trend detection
  - **AC**: Detect industry-wide cost/waste trends
  - **FP**: 8

- **ACA-14-031**: Implement pattern recognition
  - **AC**: Identify common optimization patterns
  - **FP**: 8

- **ACA-14-032**: Implement risk indicator analysis
  - **AC**: Detect emerging risk patterns
  - **FP**: 8

- **ACA-14-033**: Generate industry intelligence reports
  - **AC**: Publish quarterly intelligence reports
  - **FP**: 5

- **ACA-14-034**: Implement intelligence API
  - **AC**: Expose intelligence data via API
  - **FP**: 5

### Feature 14.6: Partner Ecosystem
**Stories**: 6

- **ACA-14-035**: Implement partner onboarding
  - **AC**: Consultants, MSPs, SIs can join ecosystem
  - **FP**: 8

- **ACA-14-036**: Implement partner portal
  - **AC**: Manage clients, view aggregated data
  - **FP**: 8

- **ACA-14-037**: Implement partner commission tracking
  - **AC**: Track referrals, calculate commissions
  - **FP**: 8

- **ACA-14-038**: Implement co-branding support
  - **AC**: Partners can white-label frontend
  - **FP**: 8

- **ACA-14-039**: Implement partner certification program
  - **AC**: Train and certify partners on ACA
  - **FP**: 5

- **ACA-14-040**: Generate partner performance reports
  - **AC**: Track partner success metrics
  - **FP**: 5

---

## EPIC 15: Testing & Quality Assurance
**FP Estimate**: 180 FP  
**Stories**: 24

### Feature 15.1: Unit Testing
**Stories**: 6

- **ACA-15-001**: Implement Python unit test framework (pytest)
  - **AC**: Test coverage > 80% for all Python services
  - **FP**: 8

- **ACA-15-002**: Implement JavaScript/TypeScript unit tests (Vitest)
  - **AC**: Test coverage > 80% for frontend
  - **FP**: 8

- **ACA-15-003**: Write unit tests for analysis rules
  - **AC**: Test each rule with mock data
  - **FP**: 13

- **ACA-15-004**: Write unit tests for API endpoints
  - **AC**: Test all endpoints with mock dependencies
  - **FP**: 13

- **ACA-15-005**: Write unit tests for script generators
  - **AC**: Verify correct scripts generated
  - **FP**: 8

- **ACA-15-006**: Implement code coverage reporting
  - **AC**: Generate coverage reports in CI/CD
  - **FP**: 5

### Feature 15.2: Integration Testing
**Stories**: 6

- **ACA-15-007**: Implement Cosmos DB integration tests
  - **AC**: Test repo operations against real Cosmos emulator
  - **FP**: 8

- **ACA-15-008**: Implement Azure SDK integration tests
  - **AC**: Test Azure API clients with mock responses
  - **FP**: 8

- **ACA-15-009**: Implement Stripe integration tests
  - **AC**: Test with Stripe test mode
  - **FP**: 8

- **ACA-15-010**: Implement collector integration tests
  - **AC**: Test full collection flow with sample subscription
  - **FP**: 8

- **ACA-15-011**: Implement analysis integration tests
  - **AC**: Test analysis with sample scan data
  - **FP**: 8

- **ACA-15-012**: Implement delivery integration tests
  - **AC**: Test script generation with sample findings
  - **FP**: 8

### Feature 15.3: End-to-End Testing
**Stories**: 6

- **ACA-15-013**: Implement E2E test framework (Playwright)
  - **AC**: Set up Playwright for frontend E2E tests
  - **FP**: 5

- **ACA-15-014**: Write E2E test: onboarding flow
  - **AC**: Login → connect subscription → pre-flight → scan
  - **FP**: 8

- **ACA-15-015**: Write E2E test: findings flow
  - **AC**: View Tier 1 findings → upgrade → view Tier 2
  - **FP**: 8

- **ACA-15-016]: Write E2E test: checkout flow
  - **AC**: Select tier → checkout → webhook → access granted
  - **FP**: 8

- **ACA-15-017**: Write E2E test: admin flow
  - **AC**: Admin login → view customers → grant entitlement
  - **FP**: 8

- **ACA-15-018**: Implement E2E test CI/CD integration
  - **AC**: Run E2E tests in pipeline
  - **FP**: 5

### Feature 15.4: Performance Testing
**Stories**: 3

- **ACA-15-019**: Implement load testing for API
  - **AC**: Test 100 concurrent requests, <2s response time
  - **FP**: 8

- **ACA-15-020**: Implement collection performance tests
  - **AC**: Verify <60s for 500 resources
  - **FP**: 5

- **ACA-15-021**: Implement analysis performance tests
  - **AC**: Verify analysis completes in <5 minutes
  - **FP**: 5

### Feature 15.5: Security Testing
**Stories**: 3

- **ACA-15-022**: Implement tenant isolation penetration test
  - **AC**: Verify no cross-tenant data leaks
  - **FP**: 13

- **ACA-15-023**: Implement API security audit
  - **AC**: OWASP Top 10 compliance check
  - **FP**: 8

- **ACA-15-024**: Implement dependency vulnerability scanning
  - **AC**: Snyk/Dependabot for Python + npm dependencies
  - **FP**: 5

---

## EPIC 16: Documentation
**FP Estimate**: 120 FP  
**Stories**: 16

### Feature 16.1: Technical Documentation
**Stories**: 6

- **ACA-16-001**: Write API documentation (OpenAPI)
  - **AC**: Complete OpenAPI spec with examples
  - **FP**: 8

- **ACA-16-002**: Write architecture documentation
  - **AC**: System architecture, data flow, deployment diagrams
  - **FP**: 8

- **ACA-16-003**: Write developer setup guide
  - **AC**: Local dev environment setup instructions
  - **FP**: 5

- **ACA-16-004**: Write deployment guide
  - **AC**: Azure infrastructure deployment instructions
  - **FP**: 8

- **ACA-16-005**: Write rule development guide
  - **AC**: How to add new analysis rules
  - **FP**: 5

- **ACA-16-006**: Write plugin development guide
  - **AC**: How to develop plugins for ecosystem
  - **FP**: 8

### Feature 16.2: User Documentation
**Stories**: 6

- **ACA-16-007**: Write client access setup guide
  - **AC**: How to grant ACA access (3 modes)
  - **FP**: 5

- **ACA-16-008**: Write user onboarding guide
  - **AC**: Step-by-step first scan walkthrough
  - **FP**: 5

- **ACA-16-009**: Write findings interpretation guide
  - **AC**: How to understand and act on findings
  - **FP**: 5

- **ACA-16-010**: Write script execution guide
  - **AC**: How to safely execute generated scripts
  - **FP**: 5

- **ACA-16-011**: Write admin user guide
  - **AC**: Admin portal operations
  - **FP**: 5

- **ACA-16-012]: Write FAQ documentation
  - **AC**: Common questions and troubleshooting
  - **FP**: 5

### Feature 16.3: Business Documentation
**Stories**: 4

- **ACA-16-013**: Write pricing documentation
  - **AC**: Tier comparison, pricing model
  - **FP**: 5

- **ACA-16-014**: Write security & data policy
  - **AC**: Security principles, data handling, compliance
  - **FP**: 8

- **ACA-16-015**: Write SLA documentation
  - **AC**: Service level agreements, uptime commitments
  - **FP**: 5

- **ACA-16-016**: Write terms of service
  - **AC**: Legal terms, acceptable use policy
  - **FP**: 5

---

## EPIC 17: DevOps & CI/CD
**FP Estimate**: 150 FP  
**Stories**: 18

### Feature 17.1: GitHub Actions Pipelines
**Stories**: 8

- **ACA-17-001**: Implement API build and test pipeline
  - **AC**: Build, test, lint, coverage on PR
  - **FP**: 5

- **ACA-17-002**: Implement collector build and test pipeline
  - **AC**: Build, test for collector service
  - **FP**: 5

- **ACA-17-003**: Implement analysis build and test pipeline
  - **AC**: Build, test for analysis service
  - **FP**: 5

- **ACA-17-004**: Implement delivery build and test pipeline
  - **AC**: Build, test for delivery service
  - **FP**: 5

- **ACA-17-005]: Implement frontend build and test pipeline
  - **AC**: Build, test, lint for React frontend
  - **FP**: 5

- **ACA-17-006**: Implement end-to-end test pipeline
  - **AC**: Run E2E tests on staging environment
  - **FP**: 8

- **ACA-17-007**: Implement security scanning pipeline
  - **AC**: Dependency scanning, SAST, container scanning
  - **FP**: 8

- **ACA-17-008**: Implement release pipeline
  - **AC**: Tag, build, push images, deploy to prod
  - **FP**: 8

### Feature 17.2: Infrastructure as Code
**Stories**: 6

- **ACA-17-009**: Implement Bicep templates for Cosmos DB
  - **AC**: Automate Cosmos account + containers provisioning
  - **FP**: 5

- **ACA-17-010]: Implement Bicep templates for Key Vault
  - **AC**: Automate Key Vault + RBAC provisioning
  - **FP**: 5

- **ACA-17-011**: Implement Bicep templates for Container Apps
  - **AC**: Automate Container App + jobs provisioning
  - **FP**: 8

- **ACA-17-012**: Implement Bicep templates for APIM
  - **AC**: Automate APIM + policies provisioning
  - **FP**: 8

- **ACA-17-013**: Implement Bicep parameters for environments
  - **AC**: Dev, staging, prod parameter files
  - **FP**: 5

- **ACA-17-014**: Implement IaC validation pipeline
  - **AC**: Lint, validate, preview in CI
  - **FP**: 5

### Feature 17.3: Monitoring & Observability
**Stories**: 4

- **ACA-17-015**: Implement Application Insights integration
  - **AC**: Track requests, exceptions, custom events
  - **FP**: 8

- **ACA-17-016**: Implement Log Analytics integration
  - **AC**: Container logs to Log Analytics workspace
  - **FP**: 5

- **ACA-17-017]: Implement custom dashboards
  - **AC**: Azure Monitor dashboards for KPIs
  - **FP**: 5

- **ACA-17-018**: Implement alerting rules
  - **AC**: Alerts on failures, high latency, errors
  - **FP**: 5

---

## EPIC 18: Marketing & Go-To-Market
**FP Estimate**: 100 FP  
**Stories**: 13

### Feature 18.1: Marketing Website
**Stories**: 5

- **ACA-18-001**: Design and build marketing website
  - **AC**: Homepage, features, pricing, contact
  - **FP**: 13

- **ACA-18-002]: Create marketing content
  - **AC**: Product descriptions, value propositions, case studies
  - **FP**: 8

- **ACA-18-003**: Implement lead capture forms
  - **AC**: Contact form, demo request, trial signup
  - **FP**: 5

- **ACA-18-004**: Implement SEO optimization
  - **AC**: Meta tags, schema markup, sitemap
  - **FP**: 5

- **ACA-18-005**: Deploy marketing site
  - **AC**: Host on Azure Static Web Apps or similar
  - **FP**: 5

### Feature 18.2: Lead Generation
**Stories**: 4

- **ACA-18-006**: Implement coupon system
  - **AC**: Generate free analysis coupons
  - **FP**: 8

- **ACA-18-007**: Create LinkedIn campaign assets
  - **AC**: Post templates, images, targeting
  - **FP**: 5

- **ACA-18-008]: Implement demo environment
  - **AC**: Pre-populated environment for demos
  - **FP**: 8

- **ACA-18-009]: Create sales enablement materials
  - **AC**: Pitch deck, one-pagers, ROI calculator
  - **FP**: 8

### Feature 18.3: Customer Success
**Stories**: 6

- **ACA-18-010**: Create onboarding checklist
  - **AC**: Step-by-step checklist for new customers
  - **FP**: 3

- **ACA-18-011]: Create training materials
  - **AC**: Video tutorials, documentation, webinars
  - **FP**: 8

- **ACA-18-012]: Implement in-app help
  - **AC**: Context-sensitive help, tooltips
  - **FP**: 5

- **ACA-18-013**: Implement customer feedback system
  - **AC**: In-app feedback form, NPS survey
  - **FP**: 5

- **ACA-18-014**: Publish founder launch playbook
  - **AC**: Define MVP cut, pricing hypotheses, margin guardrails, sales narrative, and launch-ready checklist for first revenue
  - **FP**: 8

- **ACA-18-015**: Define support operations for first 10 clients
  - **AC**: Document support channels, escalation levels, optional Tier 3 Slack/Teams path, and incident communication template
  - **FP**: 5

---

## EPIC 19: Compliance & Governance
**FP Estimate**: 120 FP  
**Stories**: 15

### Feature 19.1: Data Privacy
**Stories**: 5

- **ACA-19-001]: Implement GDPR compliance
  - **AC**: Data subject rights, consent, export, deletion
  - **FP**: 13

- **ACA-19-002**: Implement privacy policy
  - **AC**: Document privacy practices
  - **FP**: 5

- **ACA-19-003**: Implement data retention policies
  - **AC**: Auto-delete old data per policy
  - **FP**: 8

- **ACA-19-004]: Implement data export API
  - **AC**: Allow users to export their data
  - **FP**: 8

- **ACA-19-005]: Implement data deletion API
  - **AC**: Allow users to request data deletion
  - **FP**: 8

### Feature 19.2: Security Compliance
**Stories**: 5

- **ACA-19-006**: Implement SOC 2 Type II controls
  - **AC**: Security, availability, confidentiality controls
  - **FP**: 13

- **ACA-19-007]: Implement audit logging
  - **AC**: Immutable audit trail for all operations
  - **FP**: 8

- **ACA-19-008]: Implement security incident response plan
  - **AC**: Document incident response procedures
  - **FP**: 5

- **ACA-19-009]: Implement vulnerability management
  - **AC**: Regular scanning, patching process
  - **FP**: 8

- **ACA-19-010]: Implement security awareness training
  - **AC**: Train team on security best practices
  - **FP**: 5

### Feature 19.3: Operational Compliance
**Stories**: 7

- **ACA-19-011]: Implement backup and disaster recovery
  - **AC**: Automated backups, tested DR plan
  - **FP**: 8

- **ACA-19-012]: Implement business continuity plan
  - **AC**: Document BCP, test annually
  - **FP**: 5

- **ACA-19-013]: Implement change management
  - **AC**: Documented process for changes
  - **FP**: 5

- **ACA-19-014]: Implement SLA monitoring
  - **AC**: Track uptime, latency, alerting
  - **FP**: 8

- **ACA-19-015]: Conduct compliance audits
  - **AC**: Regular internal audits, external audit support
  - **FP**: 8

- **ACA-19-016**: Define tiered backup, retention, and disaster recovery policy
  - **AC**: Specify retention by data class and tier, backup cadence, geo-restore expectations, and immutable audit-log retention windows
  - **FP**: 5

- **ACA-19-017**: Define service quota and fairness policy
  - **AC**: Specify scan cadence by tier, API sustained and burst quotas, abuse controls, and customer-visible status/header behavior for throttling
  - **FP**: 8

---

## Summary Statistics by Epic

| Epic | Stories | FP Estimate |
|------|---------|-------------|
| 01: Authentication & Authorization | 25 | 193 |
| 02: Data Collection | 42 | 320 |
| 03: Analysis Engine & Rules | 47 | 380 |
| 04: Delivery & Script Generation | 32 | 240 |
| 05: Frontend (Customer & Admin) | 39 | 285 |
| 06: API Service | 47 | 333 |
| 07: Billing & Payment | 22 | 180 |
| 08: Infrastructure & Deployment | 28 | 200 |
| 09: Analytics & Telemetry | 12 | 90 |
| 10: Phase 6 - Continuous Monitoring | 28 | 220 |
| 11: Phase 7 - Enterprise Multi-Tenant | 35 | 280 |
| 12: Phase 8 - Autonomous Optimization | 38 | 310 |
| 13: Phase 9 - Predictive & Strategic | 32 | 260 |
| 14: Phase 10 - Ecosystem Platform | 40 | 320 |
| 15: Testing & QA | 24 | 180 |
| 16: Documentation | 16 | 120 |
| 17: DevOps & CI/CD | 18 | 150 |
| 18: Marketing & GTM | 15 | 113 |
| 19: Compliance & Governance | 17 | 133 |
| **TOTAL** | **623** | **4,957** |

---

## Implementation Phases

### Phase 1: MVP (Epics 01-04, 06-09)
**Stories**: 186  
**FP**: 1,536  
**Deliverable**: Working product with auth, collection, analysis, delivery, basic frontend, billing

### Phase 2: Production Hardening (Epics 05, 08, 15-17)
**Stories**: 119  
**FP**: 835  
**Deliverable**: Full frontend, infrastructure, testing, CI/CD

### Phase 3: Enterprise Features (Epics 10-11)
**Stories**: 63  
**FP**: 500  
**Deliverable**: Continuous monitoring, multi-tenant platform

### Phase 4: Advanced Capabilities (Epics 12-13)
**Stories**: 70  
**FP**: 570  
**Deliverable**: Autonomous optimization, predictive analytics

### Phase 5: Platform & Ecosystem (Epics 14, 18-19)
**Stories**: 72  
**FP**: 566  
**Deliverable**: Multi-cloud, marketplace, compliance

---

## Notes on Extraction Methodology

This WBS was extracted by:
1. Reading all 49 documentation files sequentially
2. Identifying architectural capabilities, features, and requirements
3. Breaking features into atomic user stories with acceptance criteria
4. Assigning story IDs in format ACA-NN-NNN
5. Estimating story points using standard Function Point methodology
6. Grouping stories into features and epics
7. Organizing into phases aligned with project PLAN

**Confidence Level**: High - based on comprehensive technical specifications
**Coverage**: Complete - all phases from feasibility through ecosystem, plus nested DPDCA reconciliation of docs 44-49 admin, onboarding, founder, operations, and Entra/Cosmos wiring packs
**Traceability**: Each story maps to specific documentation sections

---

**Document End**
