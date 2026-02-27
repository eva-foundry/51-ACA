AGENTS.md -- ACA Azure Cost Advisor
====================================

Version  : 1.0.0
Updated  : 2026-02-26
Audience : GitHub Copilot coding agents, Claude, Codex, and any other AI coding
           agent that works autonomously on issues in this repository.

This file is the machine-readable contract between this codebase and any AI
agent that works on it autonomously via GitHub Issues, Codespaces, or cloud
agent infrastructure.

Read this file FIRST. Follow every rule. Do not deviate.

-----------------------------------------------------------------------------
WHAT THIS PROJECT IS
-----------------------------------------------------------------------------

ACA (Azure Cost Advisor) is a commercial SaaS product.
A client connects their Azure subscription, receives a tiered cost optimization
report (Tier 1 free, Tier 2 advisory CAD $499, Tier 3 IaC deliverable CAD $1499),
and optionally downloads a zip of Terraform/Bicep templates pre-configured for
their subscription.

Four backend services + one React frontend:
  services/api/       FastAPI API (auth, tier gating, Stripe, admin)
  services/collector/ Azure SDK inventory + cost + advisor pull
  services/analysis/  12 deterministic rules -> findings JSON
  services/delivery/  Jinja2 template rendering + ZIP packager
  frontend/           React 19 + Fluent UI v9 (Vite, i18next)

-----------------------------------------------------------------------------
NON-NEGOTIABLE RULES
-----------------------------------------------------------------------------

1. TENANT ISOLATION
   Every Cosmos query MUST include partition_key=subscriptionId.
   Never call query_items() without partition_key. This is a billing data
   product -- cross-tenant leaks are a critical production defect.

2. TIER GATING
   GET /v1/findings/:scanId calls gate_findings(findings, tier) before returning.
   Tier 1 must NOT expose narrative or deliverable_template_id.
   Never bypass gate_findings() on any findings endpoint.

3. ENCODING
   ASCII only. No emoji, no Unicode arrows, no curly quotes, no non-ASCII
   characters in any file: .py, .ts, .md, .json, .yaml, .sh.
   Output tokens: [PASS] / [FAIL] / [WARN] / [INFO] only.

4. STRIPE WEBHOOK
   In checkout.py webhook handler: always call await request.body() BEFORE
   any JSON parsing. Never re-read the body after verification.
   Wrong body order = silent 400 in production.

5. PYTHON VENV
   Never use bare python or python3.
   In Codespaces: python (devcontainer sets path).
   Locally (Windows): C:\AICOE\.venv\Scripts\python.exe

6. NO PROMPT-AND-WAIT
   Agents must not ask for permission on a step they can determine themselves.
   Read the spec docs, implement the change, run tests, commit. Done.

-----------------------------------------------------------------------------
DEVELOPMENT LOOP (DPDCA)
-----------------------------------------------------------------------------

Every agent task follows this sequence:

  Discover  -- read the relevant spec doc from the docs/ list below
  Plan      -- identify the exact files to change; write a brief plan comment
  Do        -- implement the change (code + tests)
  Check     -- run: pytest services/ -x -q  (must exit 0)
  Act       -- commit with message format: feat(scope): short description

Always run tests before committing. A commit that breaks pytest is not valid.

-----------------------------------------------------------------------------
TEST COMMAND
-----------------------------------------------------------------------------

  pytest services/ -x -q --tb=short

Required: exit 0 before any commit.
Frontend: cd frontend && npm test (vitest, if tests exist)

-----------------------------------------------------------------------------
SPEC DOCUMENTS (read before implementing any feature)
-----------------------------------------------------------------------------

  02-preflight.md         Onboarding + permission validation
  05-technical.md         Full API spec + FastAPI patterns
  08-payment.md           Stripe backend flow
  12-IaCscript.md         Tier 3 template library (12 categories)
  16-stripe-backend.md    Stripe repo + service layer patterns
  18-customer-mapping.md  Customer + entitlement mapping spec

-----------------------------------------------------------------------------
ISSUE ASSIGNMENT PROTOCOL
-----------------------------------------------------------------------------

When assigned a GitHub Issue with label "agent-task":

1. Read the issue body. It contains:
   - Story ID (e.g. ACA-SCANS-001)
   - Spec doc reference
   - Acceptance criteria (testable conditions)
   - Files to modify (explicit list)

2. Branch: create from main with name feat/{story-id-lowercase}

3. Implement all acceptance criteria. Do not implement anything not listed.

4. Run: pytest services/ -x -q
   If any test fails, fix it before committing.

5. Open a PR using the pull_request_template.md checklist.

6. PR title format: feat(aca): {story-id} -- {short description}

-----------------------------------------------------------------------------
KEY FILE LOCATIONS
-----------------------------------------------------------------------------

API settings        services/api/app/settings.py
Cosmos containers   services/api/app/db/cosmos.py
Repos               services/api/app/db/repos/
Service layer       services/api/app/services/
Routers             services/api/app/routers/
Analysis rules      services/analysis/app/rules/
Delivery templates  services/delivery/app/templates/
Frontend pages      frontend/src/app/routes/
Frontend API client frontend/src/app/api/
Frontend types      frontend/src/app/types/models.ts
i18n strings        frontend/public/locales/en/translation.json

-----------------------------------------------------------------------------
COMMIT FORMAT
-----------------------------------------------------------------------------

  feat(scope): short description
  fix(scope):  short description
  chore(scope): short description

Scope examples: api, collector, analysis, delivery, frontend, infra, docs
Max subject line: 72 characters. Body is optional.

-----------------------------------------------------------------------------
WHAT AGENTS MUST NOT DO
-----------------------------------------------------------------------------

- Do not add .env files or secrets to any commit.
- Do not bypass tenant isolation (no partition-key-free Cosmos calls).
- Do not downgrade a client's tier (entitlement_service.py enforces this).
- Do not change STRIPE_WEBHOOK_SECRET handling (raw body before JSON).
- Do not add emoji or Unicode to any file (encoding rule 3 above).
- Do not open PRs that fail pytest.
- Do not modify PLAN.md or STATUS.md (human-edited governance docs).

