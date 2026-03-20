\## 1) Epic 15 — Onboarding System (Client Onboarding SaaS)



\*\*Goal:\*\* Convert an anonymous visitor into a verified, authorized, billable ACA tenant ready to run scans safely.



\### Features



\* Tenant creation \& workspace provisioning

\* Identity verification (org + user)

\* Subscription \& billing setup

\* Azure access delegation (least-privilege)

\* Pre-scan eligibility checks

\* Quota initialization

\* Compliance \& ToU acceptance

\* Notifications \& onboarding checklist

\* Self-service management portal



\### User Journey (Happy Path)



1\. Sign up → verify email

2\. Create organization / tenant

3\. Choose plan (Free / Tier 2 / Tier 3)

4\. Connect Azure subscription (Reader role or custom role)

5\. Automated preflight validation

6\. Accept terms \& data permissions

7\. System provisions workspace + quotas

8\. User launches first scan



\### Boundaries vs Existing Flows



| Area         | Epic 15 Scope                  | Out of Scope                |

| ------------ | ------------------------------ | --------------------------- |

| Auth         | Account creation \& org mapping | Core IdP mechanics          |

| Connect      | Subscription linking UX        | Low-level ARM auth          |

| Preflight    | Eligibility orchestration      | Deep technical probes       |

| Billing      | Plan selection \& payment       | Payment processor internals |

| Provisioning | Tenant resources               | Scan engine internals       |



---



\## 2) WBS for Epic 15 (22 Stories, ACA-style)



\*\*ID Format:\*\* `ACA-E15-S##`



\### Milestone M1 — Account \& Tenant Setup



\* S01 User registration

\* S02 Email verification

\* S03 Organization creation

\* S04 Role assignment (Owner/Admin)

\* S05 Tenant record provisioning



\### M2 — Plan \& Billing



\* S06 Plan selection UI

\* S07 Pricing display

\* S08 Payment integration

\* S09 Subscription activation

\* S10 Billing profile storage



\### M3 — Azure Connection



\* S11 Subscription discovery

\* S12 Role validation (Reader/custom)

\* S13 Consent capture

\* S14 Connection persistence

\* S15 Connection health check



\### M4 — Preflight \& Eligibility



\* S16 Permission preflight

\* S17 Resource visibility test

\* S18 Quota assignment

\* S19 Abuse screening

\* S20 Readiness confirmation



\### M5 — Activation



\* S21 Workspace provisioning

\* S22 Onboarding completion + first-scan CTA



\*\*Acceptance Criteria (example for S12)\*\*



\* Reject if insufficient role

\* Display remediation guidance

\* Log evidence of validation

\* Allow retry without data loss



---



\## 3) Scan Cadence \& Quota Policy (3-Tier)



| Tier   | Cadence     | Max Scans | Re-scan Rule    | Abuse Controls     |

| ------ | ----------- | --------- | --------------- | ------------------ |

| Free   | Manual only | 1/month   | After 30 days   | Cooldown + CAPTCHA |

| Tier 2 | Weekly      | 4/month   | 7-day minimum   | Throttling         |

| Tier 3 | Daily       | 30+/month | 24-hour minimum | Priority queue     |



Additional safeguards:



\* Incremental scans encouraged

\* Duplicate scan suppression

\* Cost guardrails for large tenants



---



\## 4) API Rate-Limit \& Fairness Matrix



| Tier   | Sustained (req/min) | Burst | Daily Cap | Notes             |

| ------ | ------------------- | ----- | --------- | ----------------- |

| Free   | 10                  | 20    | 5,000     | Strict throttling |

| Tier 2 | 60                  | 120   | 50,000    | Standard SaaS     |

| Tier 3 | 300                 | 600   | 300,000   | Priority          |



APIM Policies:



\* Token bucket

\* Per-tenant quotas

\* Backoff headers

\* Abuse detection triggers



---



\## 5) Expanded Analysis Scope (Azure Best Practices)



| Control Area   | Description                   | Tier    |

| -------------- | ----------------------------- | ------- |

| WAF            | Front-door protection posture | Tier 2+ |

| APRL           | Reliability recommendations   | Tier 2+ |

| RBAC Hygiene   | Excess privilege detection    | All     |

| Key Vault Mode | RBAC vs Access Policy         | All     |

| MCSB Alignment | Security benchmark mapping    | Tier 3  |



---



\## 6) Competitive Positioning



\*\*Against Azure Native Tools\*\*



\* Cross-subscription visibility

\* Cost + security + governance unified

\* Actionable remediation scripts

\* Evidence-backed reports



\*\*Against FinOps Platforms\*\*



\* Azure-deep specialization

\* Read-only, low-risk onboarding

\* Preflight permission validation

\* Government-grade governance patterns



\*\*Core Differentiator:\*\*

👉 “Safe, explainable, low-friction cloud optimization audits.”



---



\## 7) SLA \& SLO Targets



\### Phase 1



\* Availability: 99.5%

\* Scan completion: < 2 hours (mid-size tenant)

\* Report generation: < 15 minutes

\* Support response: 1 business day



\### Phase 2



\* Availability: 99.9%

\* Scan completion: < 60 minutes

\* Tier 3 package delivery: < 48 hours

\* Critical support: < 2 hours



---



\## 8) Failure \& Retry Policy



\### Collection Jobs



\* Retry: exponential backoff (max 5)

\* Partial progress saved

\* Fail if permission revoked



\### Analysis Jobs



\* Deterministic re-run allowed

\* Idempotent processing



\### Delivery



\* Retry artifact generation

\* Fallback to download link



\### Customer-Visible Status



\* Pending → Running → Partial → Completed → Failed

\* Clear remediation guidance on failure



---



\## 9) Backup, DR, Retention Policy



| Data Type     | Retention                     | Backup            | DR               |

| ------------- | ----------------------------- | ----------------- | ---------------- |

| Tenant config | 1 year                        | Daily             | Cross-region     |

| Scan results  | 90 days (Free), 1 year (Paid) | Daily             | Geo-replication  |

| Artifacts     | 90 days                       | Versioned storage | Geo-restore      |

| Telemetry     | 30–180 days                   | Aggregated        | Secondary region |

| Audit logs    | 2+ years                      | Immutable         | Required         |



---



\## 10) Support Operations (First 10 Clients)



\### Channels



\* Email support

\* Ticket portal

\* Optional Slack/Teams (Tier 3)



\### Escalation



1\. Tier 1 — Customer success

2\. Tier 2 — Engineering

3\. Tier 3 — Founder / Architecture



\### Incident Communication Template



\* Issue summary

\* Impact

\* Workaround

\* ETA

\* Post-incident report



---



\## 11) Sprint Naming Rule



\*\*Standard:\*\* `Sprint-NNN`



Rules:



\* Always 3 digits (Sprint-001)

\* Never mix formats

\* Used across repos, reports, dashboards



---



\## 12) Data-Model Drift Remediation



Steps:



1\. Freeze schema changes

2\. Map legacy → canonical model

3\. Migration scripts + validation

4\. Update consumers

5\. Acceptance gate before new sprint execution



Gate Criteria:



\* No orphan fields

\* All stories mapped

\* Backward compatibility verified



---



\## 13) Objective README \& PLAN Completeness



\### Mandatory (README)



\* Product overview

\* Problem \& value proposition

\* Architecture summary

\* Quick start

\* Pricing / tiers

\* Security \& privacy

\* Support model



\### Mandatory (PLAN)



\* Scope \& roadmap

\* WBS / backlog mapping

\* Milestones

\* Risks \& mitigations

\* Operational model

\* Evidence links



Optional:



\* Marketing materials

\* Competitive analysis

\* Case studies



Evidence-Backed:



\* Test results

\* Performance metrics

\* Security validation

\* Deployment proof



---



\## 14) Executive Narrative (README Top Section)



\*\*ACA — Azure Cloud Auditor\*\*



Organizations overspend and operate cloud environments with hidden risk due to limited visibility and complex best practices. ACA provides a safe, read-only SaaS audit that analyzes Azure subscriptions for cost, reliability, security, and governance improvements. Designed for minimal permissions and rapid onboarding, ACA delivers evidence-based recommendations and remediation guidance within hours. The service targets development teams, SMBs, and public-sector organizations seeking quick savings and risk reduction without deploying new infrastructure or granting high privileges. ACA combines FinOps insights with security benchmarks and operational best practices into a single actionable report, backed by strict data controls and transparent processing.



---



\## 15) Final Investor-/Engineering-/Ops-Ready Checklist



\### Investor-Ready



\* Clear problem \& market

\* Differentiation

\* Pricing model

\* Scalability story

\* Risk controls

\* Early traction plan



\### Engineering-Ready



\* Architecture documented

\* Backlog prioritized

\* SLOs defined

\* Deployment model clear

\* Observability plan



\### Operations-Ready



\* Support model defined

\* Incident processes documented

\* Backup \& DR validated

\* Runbooks available

\* Compliance posture described



---



If you want, I can also produce:



✅ A \*\*single canonical ACA Product Spec (PRD)\*\*

✅ A \*\*Copilot-ready context pack\*\* for building the SaaS end-to-end

✅ A \*\*Phase-1 launch playbook\*\* (first revenue in 90 days)

✅ A \*\*technical architecture aligned to your Azure sandbox → production migration path\*\*



Just say the word.



