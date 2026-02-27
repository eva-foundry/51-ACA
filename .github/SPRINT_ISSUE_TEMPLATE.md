# Sprint Issue Template

Use this format when creating a sprint issue. The `<!-- SPRINT_MANIFEST -->` block is
machine-readable. The narrative sections below it are for human review.

Label the issue with `sprint-task` to trigger the Sprint Agent workflow.
Label with `sonnet-review` AFTER the sprint completes to trigger architecture review.

---

## How to create a sprint issue

```powershell
# 1. Create the issue
gh issue create --repo eva-foundry/51-ACA \
  --title "[SPRINT-01] Foundation + API Core" \
  --body-file .github/sprints/sprint-01.md \
  --label "sprint-task"

# 2. The workflow fires automatically on the sprint-task label.
# 3. Monitor progress via issue comments (agent posts after each story).
# 4. After sprint completes, trigger review:
gh issue edit N --add-label "sonnet-review" --repo eva-foundry/51-ACA
```

---

## Sprint Issue Body Format

The issue body must contain exactly one `<!-- SPRINT_MANIFEST ... -->` block.
All other content is narrative for human readers and the review agent.

---

**PASTE BELOW THIS LINE into a new GitHub issue body:**

```
<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-01",
  "sprint_title": "Foundation + API Core",
  "target_branch": "sprint/01-foundation",
  "epic": "ACA-01",
  "stories": [
    {
      "id": "ACA-01-001",
      "title": "FastAPI project scaffold",
      "wbs": "1.1.1",
      "epic": "Epic 01 -- Foundation",
      "files_to_create": [
        "services/api/app/__init__.py",
        "services/api/app/main.py",
        "services/api/app/settings.py",
        "services/api/requirements.txt"
      ],
      "acceptance": [
        "services/api/app/main.py exists and imports without error",
        "FastAPI app instance is created with lifespan",
        "GET /health endpoint registered",
        "settings.py uses pydantic-settings BaseSettings"
      ],
      "implementation_notes": "Create the FastAPI application factory in main.py. Use lifespan context manager. Add CORS middleware allowing all origins for dev. Include the health router. Settings must include ACA_COSMOS_URL, ACA_OPENAI_KEY, STRIPE_SECRET_KEY as optional strings with defaults. Follow copilot-instructions P2.3 structure exactly."
    },
    {
      "id": "ACA-01-002",
      "title": "Tenant isolation middleware",
      "wbs": "1.1.2",
      "epic": "Epic 01 -- Foundation",
      "files_to_create": [
        "services/api/app/middleware/__init__.py",
        "services/api/app/middleware/tenant.py"
      ],
      "acceptance": [
        "TenantMiddleware class defined in tenant.py",
        "get_subscription_id() raises HTTP 403 if no subscription_id in request.state",
        "Middleware sets request.state.subscription_id from X-Subscription-Id header"
      ],
      "implementation_notes": "Implement exactly as in copilot-instructions P2.5 Pattern 1. Class-based Starlette middleware. Extract X-Subscription-Id header. If missing, raise HTTPException 403. Set request.state.subscription_id. Import in main.py."
    },
    {
      "id": "ACA-01-003",
      "title": "Cosmos DB client + partition helpers",
      "wbs": "1.1.3",
      "epic": "Epic 01 -- Foundation",
      "files_to_create": [
        "services/api/app/db/__init__.py",
        "services/api/app/db/cosmos.py"
      ],
      "acceptance": [
        "CosmosClient initialized from settings.ACA_COSMOS_URL",
        "query_findings(sub_id) always passes partition_key=sub_id",
        "Module imports without error when settings are absent"
      ],
      "implementation_notes": "Implement exactly as in copilot-instructions P2.5 Pattern 1. CosmosClient + DatabaseProxy + ContainerProxy lazy initialization. All query functions must include partition_key parameter. Never call query_items without partition_key. Wrap initialization in try/except so the module loads even without a real Cosmos connection (for CI)."
    }
  ]
}
-->

## Sprint SPRINT-01: Foundation + API Core

**Epic**: ACA-01 Foundation
**Branch**: sprint/01-foundation
**Triggered by**: sprint-task label

### Objectives

This sprint scaffolds the core FastAPI service with:
- Project structure matching copilot-instructions P2.3
- Tenant isolation middleware (copilot-instructions Pattern 1)
- Cosmos DB client with mandatory partition key (Pattern 1)

### Acceptance Gate

All stories must pass lint (ruff) and pytest --co before the sprint PR is opened.

### Stories

| ID | Title | WBS | Files |
|---|---|---|---|
| ACA-01-001 | FastAPI project scaffold | 1.1.1 | main.py, settings.py |
| ACA-01-002 | Tenant isolation middleware | 1.1.2 | middleware/tenant.py |
| ACA-01-003 | Cosmos DB client + partition helpers | 1.1.3 | db/cosmos.py |

### Definition of Done

- [ ] All files exist at specified paths
- [ ] `EVA-STORY: ACA-01-NNN` tag present in each file
- [ ] `ruff check services/` exits 0 (or only pre-existing warnings)
- [ ] `pytest services/ --co -q` exits 0
- [ ] Progress comment posted after each story by the sprint agent
- [ ] Sprint summary comment posted at end

### Dependencies

None -- this is Sprint 1.

### Notes for review agent

Missing docs referenced in copilot-instructions:
- `docs/05-technical.md` -- see copilot-instructions P2.5 for patterns
- `docs/02-preflight.md` -- see copilot-instructions P2.8 for troubleshooting
Fallback: use copilot-instructions.md P2.5 patterns as ground truth.
```

---

## Field Reference

| Field | Required | Description |
|---|---|---|
| `sprint_id` | yes | Unique sprint ID, e.g. `SPRINT-01` |
| `sprint_title` | yes | Human-readable sprint name |
| `target_branch` | yes | Branch the agent will create, e.g. `sprint/01-foundation` |
| `epic` | yes | Epic ID, e.g. `ACA-01` |
| `stories[].id` | yes | Story ID in `ACA-NN-NNN` format |
| `stories[].title` | yes | Short imperative title |
| `stories[].wbs` | yes | WBS code from PLAN.md |
| `stories[].files_to_create` | yes | List of repo-relative paths to write |
| `stories[].acceptance` | yes | Acceptance criteria (tested by agent) |
| `stories[].implementation_notes` | yes | Full implementation instructions for the LLM |

## Rules for Writing Sprint Issues

1. `implementation_notes` must be self-contained -- reference specific patterns by name.
2. File paths must be repo-relative (no leading slash).
3. `EVA-STORY` tag will be injected automatically by the agent.
4. Keep `acceptance` items testable (imports, file exists, function signature).
5. Max 8 stories per sprint -- agent runs synchronously.
6. `target_branch` must be unique per sprint.

## Creating Sprint Files

Store sprint manifests in `.github/sprints/`:
```
.github/sprints/
  sprint-01-foundation.md
  sprint-02-collector.md
  sprint-03-analysis.md
  ...
```

Create the issue from the manifest file:
```powershell
gh issue create --repo eva-foundry/51-ACA \
  --title "[SPRINT-02] Data Collection Service" \
  --body-file .github/sprints/sprint-02-collector.md \
  --label "sprint-task"
```
