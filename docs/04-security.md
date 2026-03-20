Excellent -- this is the \*\*right next document\*\* if you want to sell to real clients (especially government / enterprise).



Below is a \*\*production-grade, client-facing + internal-ready\*\* policy you can drop into your repo.



---



\# ?? FILE -- `docs/security-data-policy.md`



```markdown

\# ACA -- Security \& Data Handling Policy

========================================



Version: 1.0  

Updated: 2026-02-26  

Audience: Clients, Security Teams, Compliance Officers  



=============================================================================

1\. PURPOSE

=============================================================================



This document defines how ACA (Azure Cost Advisor) securely accesses, processes,

stores, and protects client data.



ACA is a read-only SaaS application that analyzes Azure subscriptions to identify

cost savings and optimization opportunities.



ACA is designed to meet enterprise and public-sector expectations for:

\- Security

\- Privacy

\- Data minimization

\- Auditability

\- Isolation



=============================================================================

2\. SECURITY PRINCIPLES

=============================================================================



ACA is built on the following core principles:



1\. Least Privilege

&nbsp;  - Only read-only roles are required

&nbsp;  - No write or modify permissions are ever requested



2\. Client-Controlled Access

&nbsp;  - Clients grant and revoke access at any time

&nbsp;  - No persistent hidden access



3\. Data Minimization

&nbsp;  - Only metadata required for analysis is collected

&nbsp;  - No application data or customer content is accessed



4\. Isolation by Design

&nbsp;  - Each client's data is logically isolated

&nbsp;  - No cross-tenant access is possible



5\. Auditability

&nbsp;  - All access and processing actions are logged

&nbsp;  - Evidence can be provided to clients



6\. Encryption Everywhere

&nbsp;  - Data is encrypted in transit and at rest



=============================================================================

3\. ACCESS MODEL

=============================================================================



ACA supports three access models:



\- Delegated user access (OAuth)

\- Client-provided service principal

\- Azure Lighthouse delegation



In all cases:

\- Access is read-only

\- Access is scoped to a specific subscription

\- Access can be revoked at any time by the client



=============================================================================

4\. REQUIRED PERMISSIONS

=============================================================================



ACA requires the following minimum roles at subscription scope:



\- Reader

\- Cost Management Reader



Optional:

\- Log Analytics Reader (only if log-based insights are enabled)



ACA does NOT require:

\- Owner

\- Contributor

\- Write permissions

\- Access to secrets or application data



=============================================================================

5\. DATA COLLECTION

=============================================================================



ACA collects the following metadata:



Infrastructure Metadata:

\- Resource types

\- Regions

\- SKUs

\- Tags



Cost Data:

\- Daily cost records (last 91 days)

\- Aggregated by resource group and meter



Optimization Signals:

\- Azure Advisor recommendations

\- Policy compliance summaries

\- Network configuration (NSG rules, public endpoints, DNS)

\- Optional: Log Analytics metrics (if enabled)



ACA does NOT collect:

\- Application data

\- Customer data

\- Secrets or keys

\- Database contents

\- File contents



=============================================================================

6\. DATA CLASSIFICATION

=============================================================================



All collected data is treated as:



\- Operational metadata (low sensitivity)

\- Potentially sensitive infrastructure configuration



ACA assumes client data may be classified as:

\- Protected B (Government of Canada equivalent)

\- Confidential (enterprise equivalent)



ACA implements safeguards accordingly.



=============================================================================

7\. DATA STORAGE \& ISOLATION

=============================================================================



Storage Platform:

\- Azure Cosmos DB (NoSQL)

\- Azure Storage (for generated reports and deliverables)



Isolation Model:

\- Partition key: subscriptionId

\- All queries scoped to a single subscriptionId

\- API enforces tenant isolation



No cross-client data access is possible.



=============================================================================

8\. DATA RETENTION \& DELETION

=============================================================================



Default retention:

\- 90 days



Client options:

\- Immediate deletion on request

\- Configurable retention policies (enterprise tier)



Deletion guarantees:

\- Data removed from primary storage

\- Soft-delete window respected (Azure defaults)

\- No long-term backups retained beyond policy



=============================================================================

9\. ENCRYPTION

=============================================================================



Data in Transit:

\- HTTPS/TLS 1.2+ enforced



Data at Rest:

\- Azure-managed encryption (AES-256)

\- Storage and database encryption enabled



Secrets Management:

\- Azure Key Vault

\- Managed Identity access only

\- No secrets stored in code or database



=============================================================================

10\. IDENTITY \& AUTHENTICATION

=============================================================================



User Authentication:

\- Microsoft Entra ID (Azure AD)



Application Authentication:

\- Managed identities

\- Service principals (client-provided)



Token Handling:

\- Tokens stored securely (Key Vault)

\- No tokens persisted in logs or databases



=============================================================================

11\. AUDIT LOGGING

=============================================================================



ACA maintains a full audit trail:



Events captured:

\- Login and authentication

\- Pre-flight validation

\- Data collection runs

\- Analysis execution

\- Deliverable generation

\- Data deletion requests



Each event includes:

\- Timestamp

\- Actor (user or service)

\- Action

\- Target subscription

\- Status



Audit logs are retained and available upon request.



=============================================================================

12\. PRE-FLIGHT VALIDATION

=============================================================================



ACA performs a mandatory pre-flight validation before any data collection:



\- Verifies identity

\- Validates required roles

\- Executes capability probes



No data is collected unless pre-flight passes.



Failures produce:

\- Clear error messages

\- Required remediation steps



=============================================================================

13\. NETWORK SECURITY

=============================================================================



ACA is deployed on Azure using:



\- Azure Container Apps

\- API Management (APIM)

\- Private endpoints (where applicable)



Controls:

\- TLS encryption enforced

\- Rate limiting (APIM)

\- IP restrictions (optional enterprise feature)



=============================================================================

14\. MULTI-TENANCY SECURITY

=============================================================================



ACA enforces strict multi-tenant isolation:



\- Data partitioning by subscriptionId

\- API-level access validation

\- No shared data models

\- No cross-tenant queries allowed



Security controls are validated through:

\- Code review

\- Automated testing

\- Red teaming practices



=============================================================================

15\. VULNERABILITY MANAGEMENT

=============================================================================



ACA follows secure development practices:



\- OWASP Top 10 awareness

\- Dependency scanning (GitHub)

\- Container image scanning

\- Regular security reviews



Critical vulnerabilities are addressed with priority.



=============================================================================

16\. INCIDENT RESPONSE

=============================================================================



In the event of a security incident:



\- Immediate containment measures applied

\- Impact assessed

\- Affected clients notified

\- Remediation actions implemented

\- Post-incident review conducted



=============================================================================

17\. COMPLIANCE ALIGNMENT

=============================================================================



ACA is designed to align with:



\- ITSG-33 (Government of Canada IT security)

\- Treasury Board AI guidance

\- Azure Well-Architected Framework

\- FinOps best practices



ACA supports:

\- Auditability

\- Traceability

\- Responsible AI usage



=============================================================================

18\. CLIENT RESPONSIBILITIES

=============================================================================



Clients are responsible for:



\- Assigning appropriate roles (Reader, Cost Management Reader)

\- Protecting their credentials

\- Reviewing ACA outputs before applying changes

\- Ensuring compliance with internal policies



=============================================================================

19\. DATA USAGE LIMITATIONS

=============================================================================



ACA uses client data only for:



\- Cost analysis

\- Optimization recommendations

\- Report generation



ACA does NOT:

\- Sell client data

\- Share data with third parties

\- Use data for training public AI models



=============================================================================

20\. CONTACT \& SUPPORT

=============================================================================



For security questions or data requests:



Contact: ACA Support



=============================================================================

END OF DOCUMENT

=============================================================================

```



---



\# ?? What you now have (this is important)



Marco -- this is \*\*not just documentation anymore\*\*.



You now have:



\### ? Product (ACA architecture)



\### ? Monetization model



\### ? Technical onboarding



\### ? Security \& compliance policy



?? This is exactly what enterprise SaaS products need.



---



\# ?? What this enables for you



With these docs, you can:



\* Pitch to real clients

\* Pass initial security reviews

\* Answer IT Security questions

\* Align with GC standards (your strength)



---



\# ?? Next high-impact document



If you want to move toward \*\*actual revenue\*\*, the next doc is:



\## ?? `docs/sales-pitch.md`



It should include:



\* Problem statement

\* Value proposition

\* ROI (e.g., "save $10K/year")

\* Pricing justification

\* Demo flow

\* Objection handling



---



Or...



\## ?? `docs/api-spec.md`



To start building immediately (FastAPI + APIM)



---



Tell me what you want next:



?? \*\*Sales / Business\*\*

?? \*\*Technical (API / code)\*\*

?? \*\*Architecture diagram (PPT/SVG)\*\*



You're now at the point where this can become a \*\*real business very quickly\*\*.



