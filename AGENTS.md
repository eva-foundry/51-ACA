AGENTS.md -- ACA Azure Cost Advisor
====================================

Version  : 2.0.0
Updated  : 2026-02-27
Audience : GitHub Copilot coding agents (cloud), Claude (Opus/Sonnet), GPT-5 mini,
           and any other AI coding agent that works autonomously on GitHub Issues,
           Codespaces, or cloud agent infrastructure in this repository.

This file is the machine-readable contract between this codebase and every AI
agent. Read AGENTS.md FIRST, then .github/copilot-instructions.md in full.
Follow every rule. No deviations.

Model selection, Veritas audit, EVA-STORY tags, and sprint governance rules
are all mandatory -- not optional -- for every agent session.

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
MODEL SELECTION -- REASONING DEPTH, NOT STORY SIZE
-----------------------------------------------------------------------------

Choose model based on how much context, cross-file reasoning, and judgment
the task requires. Not by lines of code or FP number.

  Claude Opus 4.6
    Use for: full repo review, architecture decisions, cross-service refactors,
    security audit, test strategy design, any task requiring judgment across
    5+ files simultaneously.
    One-shot tasks only. Do not waste Opus on boilerplate.

  Claude Sonnet 4.6
    Use for: implementing L/M stories (cross-service integration, auth flows,
    analysis rule sets, Stripe webhook logic, multi-file features with tests).
    Default model for most real work.

  GPT-5.1 or GPT-5 mini
    Use for: S/XS stories (single route, config change, simple model, one file).
    Fast and cheap. Good for boilerplate, i18n strings, env var wiring.

  Do NOT use Gemini Flash or Grok for any story in this repo.
  Do NOT use a fast model for security-sensitive code (auth, Stripe, Cosmos).

-----------------------------------------------------------------------------
CLOUD AGENT BOOTSTRAP (run in this order, every session)
-----------------------------------------------------------------------------

1. Read these files in order before writing any code:
   AGENTS.md (this file)
   .github/copilot-instructions.md
   PLAN.md  (find the story assigned; read its Feature block)
   STATUS.md  (check for open blockers on this story)
   docs/<relevant-spec>.md  (see SPEC DOCUMENTS section below)

2. Query the data model for endpoint/container/screen details:
   GET https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io/model/endpoints/
   Filter to the endpoint(s) this story implements.
   Read .implemented_in and .repo_line to find existing stubs.
   Never grep for something the model already knows.

3. Check Veritas BEFORE starting work:
   node /path/to/48-eva-veritas/src/cli.js audit --repo . 2>&1
   If trust.json has "no-deploy" in actions array -> STOP, report to human.
   MTI must be >= 70 to proceed.

4. Produce a one-paragraph plan before writing code:
   - What files change
   - What the acceptance criteria check
   - What the test command is
   Never start coding before the plan is written.

-----------------------------------------------------------------------------
ISSUE ASSIGNMENT PROTOCOL
-----------------------------------------------------------------------------

When assigned a GitHub Issue with label "agent-task":

1. Read the issue body. It contains:
   - Story ID (ACA-NN-NNN format)
   - WBS ID (N.N.N format)
   - Spec doc reference
   - Inputs, Outputs, Acceptance criteria (all testable)
   - Files to modify (explicit repo-relative paths)

2. Branch: create from main with name agent/{story-id-lowercase}-{YYYYMMDD}
   Example: agent/aca-04-001-20260227

3. Add EVA-STORY tag to every file you modify:
   Python:  # EVA-STORY: ACA-NN-NNN
   TS/JS:   // EVA-STORY: ACA-NN-NNN
   Bicep:   // EVA-STORY: ACA-NN-NNN
   YAML:    # EVA-STORY: ACA-NN-NNN
   The tag goes on the first functional line of the file, not in comments at EOF.

4. Implement ONLY the acceptance criteria listed. Do not scope-creep.

5. Run the test command:
   pytest services/ -x -q --tb=short
   All tests must pass. Fix failures before committing.

6. Run Veritas audit AFTER implementing:
   MTI must still be >= 70. If it drops, you introduced a regression -- fix it.

7. Commit with Story ID on the subject line:
   feat(scope): ACA-NN-NNN short description
   The Story ID on the subject line is mandatory -- Veritas mines commits for evidence.

8. Open a PR using the pull_request_template.md checklist.
   PR title: feat(aca): ACA-NN-NNN -- short description

-----------------------------------------------------------------------------
SPRINT GOVERNANCE -- WHEN TO PROCEED VS WHEN TO ESCALATE
-----------------------------------------------------------------------------

PROCEED autonomously when:
  - Story has clear acceptance criteria, all files listed, no blocked dependency
  - Veritas MTI >= 70 before and after
  - pytest exits 0
  - No secret or Key Vault change required (those need human)

ESCALATE to human (comment on the issue, do not commit) when:
  - A listed dependency story (Depends On field) is not merged yet
  - The spec doc contradicts the issue body -- which one wins?
  - The fix requires a new Cosmos container or new Key Vault secret
  - Veritas MTI drops below 70 and you cannot find the root cause
  - Any acceptance criterion is ambiguous (cannot write a test for it)
  - pytest has failures you cannot resolve after 2 attempts

SPRINT BOUNDARY -- when all sprint stories are merged:
  1. Run: node cli.js audit --repo . -> confirm MTI >= 70
  2. Run: pytest services/ -v -> confirm 0 failures
  3. Post a sprint summary comment on the sprint planning issue:
     Stories merged, FP delivered, MTI score, test count, next sprint recommendation
  4. Do NOT start next sprint stories without human confirmation

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
- Do not select a fast model (GPT-5 mini) for auth, Stripe, or Cosmos code.
- Do not skip the EVA-STORY tag on any file you create or modify.
- Do not open a PR if Veritas MTI dropped below 70.
- Do not start a new story if the current one has unresolved escalation.
- Do not run git push without a passing pytest run on record.

-----------------------------------------------------------------------------
EVA-STORY TAG REFERENCE
-----------------------------------------------------------------------------

All 22 shipped story IDs (Sprint 0-1):
  ACA-01-001 through ACA-13-008 (see PLAN.md Story ID Roster for full list)

Next sprint stories (Sprint 2, not yet implemented):
  ACA-03-001 POST /connect full MSAL delegated auth
  ACA-04-001 POST /preflight RBAC probe
  ACA-05-001 POST /disconnect tenant offboarding
  ACA-10-001 GET /findings tier-gated response (full implementation)
  ACA-10-002 GET /inventory tenant-scoped
  ACA-02-001 DELETE /scans/{scan_id} with isolation

When implementing one of these, the EVA-STORY tag goes into the implementation
file, not just a comment file. Example:
  # EVA-STORY: ACA-04-001
  async def preflight(request: Request, ...) -> dict:

-----------------------------------------------------------------------------
AGENT ESCALATION COMMENT FORMAT
-----------------------------------------------------------------------------

When you need to escalate, post this exact format as a comment on the issue:

  [AGENT-ESCALATION]
  Story: ACA-NN-NNN
  Reason: <one sentence>
  Blocker type: DEPENDENCY | AMBIGUOUS_SPEC | SECRET_NEEDED | TEST_FAILURE | MTI_REGRESSION
  Attempted: <what you tried>
  Human action needed: <exact question or action to unblock>
  [/AGENT-ESCALATION]

