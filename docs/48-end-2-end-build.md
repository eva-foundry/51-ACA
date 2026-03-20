\## ACA SaaS — Copilot-Ready Context Pack (End-to-End Build)



> \*\*Purpose:\*\* Paste this into GitHub Copilot Chat / Agents / VS Code as system context to generate consistent code, architecture, infra, and docs for the ACA (Azure Cloud Auditor) SaaS.



---



\# 🧠 SYSTEM CONTEXT — ACA SaaS



\## 1. Product Overview



\*\*Name:\*\* ACA — Azure Cloud Auditor

\*\*Type:\*\* Multi-tenant commercial SaaS

\*\*Domain:\*\* FinOps + Security + Reliability auditing for Azure subscriptions

\*\*Core Principle:\*\* Read-only, safe, explainable cloud analysis



ACA connects to customer Azure subscriptions using least-privilege access and produces actionable optimization reports.



\### Primary Outcomes



\* Cost savings identification

\* Security posture insights

\* Reliability best-practice checks

\* Governance hygiene assessment

\* Evidence-backed recommendations



---



\## 2. Ideal Customer Profile (ICP)



\* Dev teams managing Azure subscriptions

\* SMBs lacking FinOps capability

\* Public sector orgs needing low-risk audits

\* Enterprises wanting external validation



---



\## 3. Service Tiers



\### Free Tier



\* Manual scan

\* Limited rules

\* Basic report

\* Strict quotas



\### Tier 2 (Professional)



\* Weekly scans

\* Expanded rule set

\* Historical tracking

\* Standard support



\### Tier 3 (Enterprise)



\* Daily scans

\* Full rule catalog

\* Priority processing

\* Advanced reports

\* Dedicated support



---



\## 4. Core User Journey



1\. Register account

2\. Create organization

3\. Select plan

4\. Connect Azure subscription

5\. Preflight validation

6\. Accept permissions \& terms

7\. Provision workspace

8\. Launch scan

9\. Receive report

10\. Manage subscription \& settings



---



\## 5. System Architecture (Logical)



```

\[ React Web App ]

&nbsp;       |

&nbsp;    \[ API ]

&nbsp;       |

&nbsp;  ┌───────────────┐

&nbsp;  | Core Services |

&nbsp;  └───────────────┘

&nbsp;       |

&nbsp;┌───────────────┐

&nbsp;| Job Orchestr. |

&nbsp;└───────────────┘

&nbsp;       |

&nbsp;┌───────────────┐

&nbsp;| Scan Engine   |

&nbsp;└───────────────┘

&nbsp;       |

&nbsp;┌───────────────┐

&nbsp;| Azure APIs    |

&nbsp;└───────────────┘



Storage:

\- Cosmos DB (tenant + results)

\- Blob Storage (artifacts)

\- Telemetry (logs/metrics)

```



---



\## 6. Technology Stack



\### Frontend



\* React + TypeScript

\* Component library (Fluent UI or similar)

\* Auth via Entra ID / OAuth provider



\### Backend



\* FastAPI (Python)

\* REST APIs

\* Async job processing



\### Cloud (Azure)



\* App Service / Container Apps

\* Azure API Management

\* Cosmos DB (NoSQL)

\* Blob Storage

\* Key Vault

\* Application Insights

\* Service Bus / Queue



---



\## 7. Multi-Tenancy Model



\*\*Logical isolation per tenant\*\*



Tenant entity contains:



\* Organization info

\* Subscription connections

\* Plan \& quotas

\* Scan history

\* Billing metadata



Partitioning:



\* Cosmos DB partition key = tenant\_id



---



\## 8. Security Principles



\* Read-only Azure access

\* Least-privilege role validation

\* No credential storage beyond tokens

\* Encryption at rest \& in transit

\* Audit logging of all actions

\* Tenant data isolation



---



\## 9. Onboarding Requirements



Copilot should generate features for:



\* Account registration

\* Org creation

\* Plan selection

\* Payment integration (Stripe)

\* Azure subscription linking

\* Permission validation

\* Terms acceptance

\* Workspace provisioning



---



\## 10. Scan Engine Responsibilities



Copilot should implement:



\### Collection Phase



\* Enumerate resources

\* Capture metadata

\* Respect API quotas

\* Handle pagination



\### Analysis Phase



\* Run rule catalog

\* Score findings

\* Generate recommendations



\### Output Phase



\* Create report artifacts

\* Store results

\* Notify user



---



\## 11. Rule Categories



Initial categories:



\### Cost Optimization



\* Idle resources

\* Oversized SKUs

\* Unattached disks

\* Non-reserved compute



\### Security



\* RBAC hygiene

\* Key Vault configuration

\* Public exposure risks

\* Benchmark alignment



\### Reliability



\* Backup configuration

\* Redundancy posture

\* APRL alignment



\### Governance



\* Tagging completeness

\* Policy compliance

\* Resource sprawl indicators



---



\## 12. API Design Principles



\* RESTful endpoints

\* Tenant-scoped access

\* Idempotent operations

\* Clear status reporting

\* Pagination support



\### Example Resource Domains



\* Users

\* Organizations

\* Subscriptions

\* Scans

\* Reports

\* Billing

\* Support tickets



---



\## 13. Job Orchestration Requirements



Copilot should implement:



\* Queue-based processing

\* Retry logic

\* Progress tracking

\* Cancellation support

\* Failure recovery

\* Idempotent execution



---



\## 14. Status Model (User-Visible)



```

Pending

Running

Partial

Completed

Failed

Cancelled

```



Each status must include:



\* Timestamp

\* Progress %

\* Diagnostic message

\* Retry guidance



---



\## 15. Rate Limiting \& Fairness



Implement per-tenant limits:



\* API rate limits by tier

\* Scan frequency limits

\* Burst control

\* Abuse detection



Expose headers indicating remaining quota.



---



\## 16. Reporting \& Artifacts



Reports should include:



\* Executive summary

\* Findings categorized by severity

\* Estimated savings / impact

\* Recommended actions

\* Evidence references



Artifacts stored in Blob Storage with secure access.



---



\## 17. Observability



Required telemetry:



\* API usage metrics

\* Scan performance

\* Failure rates

\* Resource consumption

\* Tenant activity

\* Audit events



---



\## 18. Backup \& Retention



Copilot should design for:



\* Daily backups

\* Geo-redundancy

\* Tier-based retention policies

\* Immutable audit logs



---



\## 19. Support Operations



Include capabilities for:



\* Ticket submission

\* Incident tracking

\* Status notifications

\* Escalation paths

\* Customer communication



---



\## 20. SLA Targets



Phase 1 baseline:



\* Availability ≥ 99.5%

\* Scan completion < 2 hours (typical tenant)

\* Report generation < 15 minutes



---



\## 21. Non-Goals (Do NOT Implement)



\* Write access to customer resources

\* Automated remediation inside customer tenant

\* Credential harvesting

\* Intrusive scanning techniques

\* Vendor lock-in features



---



\## 22. Code Generation Guidance for Copilot



When generating code:



\### Prefer



\* Clean architecture

\* Strong typing

\* Modular services

\* Testable components

\* Secure defaults

\* Cloud-native patterns



\### Avoid



\* Monolithic design

\* Hard-coded secrets

\* Tenant data mixing

\* Blocking operations in async flows



---



\## 23. Deliverables Copilot Should Be Able to Produce



Using this context, Copilot should generate:



\* Frontend application

\* Backend APIs

\* Infrastructure as Code

\* Database schemas

\* Job processing system

\* Authentication integration

\* Billing integration

\* Documentation

\* Deployment pipelines



---



\# ✅ END OF CONTEXT PACK



---



If you want, I can also provide a \*\*Phase-1 Founder Kit\*\*, including:



🔥 Exact MVP feature cut that can reach first revenue fastest

🔥 Pricing strategy that maximizes conversion

🔥 Azure cost model to avoid losing margin

🔥 Competitive kill-shots vs native Azure tools

🔥 Investor-grade pitch narrative

🔥 “Build vs Buy” guidance for each subsystem

🔥 A Copilot mega-prompt that scaffolds the entire repo



Just say:



👉 \*\*“Give me the ACA Founder Launch Kit.”\*\*



