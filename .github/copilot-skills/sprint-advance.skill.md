# Skill: sprint-advance
# EVA-STORY: ACA-14-007

**Version**: 1.0.0
**Project**: 51-ACA
**Triggers**: sprint 2, sprint 3, next sprint, deliver next sprint, advance sprint, sprint planning,
  sprint handoff, close sprint, begin sprint, plan next sprint, sprint NNN

---

## PURPOSE

This skill owns the complete sprint-advance workflow. It runs every time a completed sprint
needs to be closed and the next sprint needs to be planned and issued.

The workflow has five phases run in strict order:

```
PHASE 1 -- Validate prior sprint evidence (veritas + pytest)
PHASE 2 -- Audit repo and data model (coverage, consistency, WBS integrity)
PHASE 3 -- Update data model + ADO board (mark done stories, create ADO items)
PHASE 4 -- Determine next sprint story set (archaeology + undone dump + sizing)
PHASE 5 -- Deliver sprint manifest and GitHub issue
```

Never skip a phase. Never start Phase 4 before Phase 2 is clean.

---

## PHASE 1 -- VALIDATE PRIOR SPRINT EVIDENCE

### 1.1 Run pytest gate

```powershell
Set-Location C:\eva-foundry\51-ACA
C:\eva-foundry\.venv\Scripts\python.exe -m pytest services/ -x -q --tb=short 2>&1
# REQUIRED: exits 0.  If non-zero: fix failures BEFORE advancing.
```

Record the test count. Write to STATUS.md under "Test count: N passing."

### 1.2 Run veritas full audit

```powershell
$repo = "C:\eva-foundry\51-ACA"
node C:\eva-foundry\48-eva-veritas\src\cli.js audit --repo $repo --warn-only 2>&1 |
    Tee-Object "$repo\veritas-audit-out.txt" | Select-Object -Last 30
Write-Host AUDIT_DONE
```

Read the gap list from the output. For each `missing_implementation` or
`missing_evidence` gap tied to a story claimed done in PLAN.md:

| Gap type on a DONE story | Mandatory fix |
|---|---|
| `missing_implementation` | Add `# EVA-STORY: ACA-NN-NNN` to the relevant source file |
| `missing_evidence` | Add `# EVA-STORY: ACA-NN-NNN` to a file under `tests/` for that story |
| `orphan_artifact` | The tag in source does NOT match any plan story -- remove or fix the ID |

Fix all gaps tied to stories that are marked `Status: DONE` in PLAN.md before
continuing. Gaps for NOT-YET-STARTED stories are acceptable at this stage.

### 1.3 Check MTI is at or above gate threshold

```powershell
$t = Get-Content "$repo\.eva\trust.json" | ConvertFrom-Json
Write-Host "MTI: $($t.mti)   Actions: $($t.actions -join '|')"
# Gate: MTI >= 30 (Sprint 2); raise to 70 at Sprint 3 boundary (10+ passing tests)
# If MTI < gate: fix tags/evidence before Phase 2
```

Record MTI in STATUS.md.

---

## PHASE 2 -- AUDIT REPO AND DATA MODEL

### 2.1 Verify data model server is running

```powershell
$base = "http://localhost:8055"
$h = Invoke-RestMethod "$base/health" -ErrorAction SilentlyContinue
if (-not $h) {
    pwsh -File "C:\eva-foundry\51-ACA\data-model\start.ps1"
    Start-Sleep 4
    $h = Invoke-RestMethod "$base/health" -ErrorAction SilentlyContinue
}
Write-Host "store=$($h.store)  version=$($h.version)"
```

### 2.2 Check total objects in model matches expectations

```powershell
$s = Invoke-RestMethod "$base/model/agent-summary"
Write-Host "total=$($s.total)"
# If total is lower than last known baseline (see STATUS.md): reseed before continuing
C:\eva-foundry\.venv\Scripts\python.exe scripts/seed-from-plan.py --reseed-model
```

### 2.3 Run veritas-plan story dump -- find all undone stories

```powershell
$vp = Get-Content C:\eva-foundry\51-ACA\.eva\veritas-plan.json | ConvertFrom-Json
foreach ($feat in $vp.features) {
    $undone = $feat.stories | Where-Object { -not $_.done }
    if ($undone) {
        Write-Host "=== $($feat.id) $($feat.title) -- $($undone.Count) undone"
        foreach ($s in $undone | Select-Object -First 8) {
            Write-Host "  [ ] $($s.id)  $($s.title)"
        }
    }
}
Write-Host UNDONE_DUMP_DONE
```

Save this output -- it is the candidate pool for Phase 4.

### 2.4 Code archaeology on prior-sprint fixes

For every story that was due in the prior sprint but is not yet marked `done=True`
in veritas-plan.json, check whether the code fix actually already exists (common
after multi-session coding):

```powershell
# Example -- check if FindingsAssembler fix already present
Select-String -Path services\analysis\app\main.py -Pattern "cosmos_client"
# Example -- check if SAS expiry fix present
Select-String -Path services\delivery\app\packager.py -Pattern "SAS_HOURS|account_key"
```

If the code is already correct: the story needs only a tag + unit test + `Status: DONE`
in PLAN.md. Mark these as XS stories in the next sprint. Do NOT reimplement them.

### 2.5 Run model violation check

```powershell
$c = Invoke-RestMethod "$base/model/admin/validate" -Headers @{"Authorization"="Bearer dev-admin"}
Write-Host "violations=$($c.count)"
# ACA target: 0 violations. Fix any before committing model changes.
```

---

## PHASE 3 -- UPDATE DATA MODEL AND ADO BOARD

### 3.1 Mark completed stories done=True in PLAN.md

For every story confirmed done (code + tag + test):

```
Find the PLAN.md story block (search for the story title or WBS number).
Add "Status: DONE" on the line after the story title block header.
```

Then reseed:

```powershell
C:\eva-foundry\.venv\Scripts\python.exe scripts/seed-from-plan.py --reseed-model
C:\eva-foundry\.venv\Scripts\python.exe scripts/reflect-ids.py
```

Verify the count increased:

```powershell
$vp = Get-Content .eva\veritas-plan.json | ConvertFrom-Json
$done = ($vp.features.stories | Where-Object { $_.done }).Count
Write-Host "done=$done  total=$($vp.features.stories.Count)"
```

### 3.2 Update data model endpoint/hook records for completed stories

For each completed story that touches an API endpoint or hook (check story title):

```powershell
# Write a temp script -- NEVER inline PUT (Rule 6 from copilot-instructions)
$script = @'
$base = "http://localhost:8055"
$ep = Invoke-RestMethod "$base/model/endpoints/POST /v1/auth/connect"
$prev_rv = $ep.row_version
$ep.status = "implemented"
$ep.implemented_in = "services/api/app/routers/auth.py"
$ep.repo_line = 42
$body = $ep |
    Select-Object * -ExcludeProperty layer,modified_by,modified_at,created_by,created_at,row_version,source_file |
    ConvertTo-Json -Depth 10
$p = @{ Method="PUT"; ContentType="application/json"; Body=$body; Headers=@{"X-Actor"="agent:copilot"} }
Invoke-RestMethod "$base/model/endpoints/POST /v1/auth/connect" @p
$w = Invoke-RestMethod "$base/model/endpoints/POST /v1/auth/connect"
Write-Host "rv=$($w.row_version) expected=$($prev_rv+1) status=$($w.status)"
'@
$script | Set-Content "$env:TEMP\put-ep.ps1" -Encoding UTF8
pwsh -NoProfile -File "$env:TEMP\put-ep.ps1"
```

### 3.3 Commit data model changes

```powershell
$c = Invoke-RestMethod "http://localhost:8055/model/admin/commit" `
    -Method POST -Headers @{"Authorization"="Bearer dev-admin"}
# ACA PASS conditions: violation_count=0 AND export_errors.Count=0
Write-Host "violations=$($c.violation_count)  errors=$($c.export_errors.Count)"
```

### 3.4 Sync ADO board (optional -- only when ADO sprint is active)

```powershell
# Generate ADO items from the repo (eva-veritas generates Epic/Feature/Story/Task)
node C:\eva-foundry\48-eva-veritas\src\cli.js generate_ado_items `
    --repo C:\eva-foundry\51-ACA --include_gaps 2>&1 |
    Select-Object -Last 20
# Then use the 38-ado-poc ADO plane agent to push items to the board:
# C:\eva-foundry\.venv\Scripts\python.exe C:\eva-foundry\38-ado-poc\agents\ado_plane.py
```

---

## PHASE 4 -- DETERMINE NEXT SPRINT STORY SET

### 4.1 Selection criteria (apply in order)

1. **Blockers first**: any story with `depends_on` that is now unblocked by Phase 3 changes
2. **Bug fixes second**: stories representing code that is already written but not yet tagged,
   tested, or marked done -- always XS, highest value per effort
3. **Foundation third**: stories whose completion unblocks the most other stories
   (use `GET /model/graph/?node_id=ACA-NN-NNN&depth=2` to check impact)
4. **Size budget**: default sprint = 2 XS + 1 S + 2 M = 8 FP. Adjust based on sprint velocity.

### 4.2 Story sizing guide

| Size | FP | Criteria |
|---|---|---|
| XS | 1 | Tag + test only on already-fixed code; single-file config; evidence receipt |
| S | 2 | One new file; simple logic; no cross-service calls |
| M | 3 | 2-3 new files; DI wiring; unit tests required; auth or Cosmos involvement |
| L | 5 | Cross-service, auth middleware, Stripe webhook, multi-container Cosmos; full test suite |
| XL | 8 | Epic-level feature; full integration; not recommended for a single sprint |

### 4.3 Model rationale rules

| Story type | Model | Why |
|---|---|---|
| XS (tag/test only) | gpt-4o-mini | No cross-file reasoning |
| S (single file, simple) | gpt-4o-mini | Fast, sufficient |
| M (auth, DI, Cosmos) | gpt-4o | Cross-file reasoning required |
| L (security, Stripe) | gpt-4o | Never use fast model on auth or secret handling |

Never use gpt-4o-mini for: auth.py, any Cosmos query, any secret handling, Stripe code.

### 4.4 Run the manifest generator

```powershell
Set-Location C:\eva-foundry\51-ACA

# List undone stories to confirm final selection
C:\eva-foundry\.venv\Scripts\python.exe scripts/gen-sprint-manifest.py --list-undone

# Generate the manifest (replace with actual story IDs chosen in 4.1)
C:\eva-foundry\.venv\Scripts\python.exe scripts/gen-sprint-manifest.py `
    --sprint 03 `
    --name "brief-hyphenated-name" `
    --stories ACA-NN-NNN,ACA-NN-NNN,ACA-NN-NNN,ACA-NN-NNN,ACA-NN-NNN `
    --sizes ACA-NN-NNN=XS,ACA-NN-NNN=M
# Output: .github/sprints/sprint-03-brief-hyphenated-name.md  (with TODO placeholders)
```

---

## PHASE 5 -- DELIVER SPRINT MANIFEST AND GITHUB ISSUE

### 5.1 Fill the manifest TODO fields

Open `.github/sprints/sprint-NN-<name>.md`. For each story block, replace every
`TODO:` field with the content specified below.

#### `model_rationale` field
State which model and why in one sentence. Use the table in section 4.3.
Example: `"gpt-4o-mini: single-file tag addition with no cross-service reasoning."`

#### `files_to_create` field
List every file path that the sprint agent must create or modify:
- Exact repo-relative paths
- Include test files (`services/tests/test_ACA-NN-NNN_<name>.py`)
- Include any new `__init__.py` files needed

#### `acceptance` field
List 4-6 bullet points:
- Source file has `# EVA-STORY: ACA-NN-NNN` tag (always first)
- Functional behaviour assertion (what the code does)
- Test file name + specific test function name that must pass
- `pytest services/tests/test_<name>.py exits 0` (always last)

#### `implementation_notes` field
Write 5-8 sentences of precise technical guidance:
- Import paths the agent must use (relative to repo root or service root)
- Class/function signatures if introducing new files
- Mock patterns: which external calls to patch, what to return
- DI pattern reminder: accept optional injected deps for testability (see AGENTS.md)
- EVA-STORY tag placement: functional line, not blank comment block
- Any known pitfalls from prior sprint archaeology

### 5.2 Manifest content rules

The manifest HTML comment header must use this JSON schema. Never invent fields.

```json
{
  "sprint_id": "SPRINT-NN",
  "sprint_title": "hyphenated-name",
  "target_branch": "sprint/NN-hyphenated-name",
  "epic": "ACA-NN",
  "stories": [
    {
      "id": "ACA-NN-NNN",
      "title": "exact title from veritas-plan.json",
      "wbs": "N.N.N",
      "size": "XS|S|M|L",
      "model": "gpt-4o|gpt-4o-mini",
      "model_rationale": "one sentence",
      "epic": "Epic NN -- Title",
      "files_to_create": ["repo-relative/path.py"],
      "acceptance": ["criterion 1", "criterion 2"],
      "implementation_notes": "paragraph of technical guidance"
    }
  ]
}
```

### 5.3 Verify story IDs are canonical

All story IDs come from `.eva/veritas-plan.json`. Never invent an ID.

```powershell
$vp = Get-Content .eva\veritas-plan.json | ConvertFrom-Json
# Confirm each story ID in the manifest exists
foreach ($id in @("ACA-NN-NNN","ACA-NN-NNN")) {
    $found = $vp.features.stories | Where-Object { $_.id -eq $id }
    if (-not $found) { Write-Host "ERROR -- ID not in plan: $id" }
    else { Write-Host "OK: $id -- $($found.title)" }
}
```

### 5.4 Create the GitHub issue

```powershell
Set-Location C:\eva-foundry\51-ACA
gh issue create `
    --repo eva-foundry/51-ACA `
    --title "[SPRINT-NN] hyphenated-name" `
    --body-file .github/sprints/sprint-NN-hyphenated-name.md `
    --label "sprint-task"
# Record the issue number from the output URL
```

If the `sprint-task` label does not exist yet:

```powershell
gh label create "sprint-task" --repo eva-foundry/51-ACA --color "0075ca" `
    --description "Sprint execution issue for the sprint-agent workflow"
```

### 5.5 Trigger the sprint agent (optional)

```powershell
# sprint-agent.yml triggers on label "sprint-task", OR manually:
gh workflow run sprint-agent.yml `
    --repo eva-foundry/51-ACA `
    --field issue_number=<ISSUE_NUMBER>
```

---

## PHASE 5+ -- CLOSE THE LOOP (commit + STATUS.md + model commit)

### After issue is created, before any other work:

```powershell
Set-Location C:\eva-foundry\51-ACA

# 1. Commit the manifest file
git add .github/sprints/sprint-NN-<name>.md
git commit -m "chore(ACA-NN-NNN): Sprint-NN manifest fully filled -- N stories, issue #NN"
git push origin main

# 2. Update STATUS.md
#    - Version: 1.N.0
#    - Updated: date + "Sprint-NN issue #NN created"
#    - List all sprint stories with [PLANNED] prefix
#    - Record test count, MTI, veritas gap count

# 3. Commit STATUS.md
git add STATUS.md
git commit -m "chore(ACA-NN-NNN): STATUS.md vN.N.0 -- Sprint-NN issue #NN created"
git push origin main
```

---

## MANDATORY FORMAT REFERENCE

### Sprint manifest body section format

Each story in the issue body must use this Markdown structure:

```markdown
<!-- STORY: ACA-NN-NNN -->
## ACA-NN-NNN -- <Story title from plan>

**Size**: XS|S|M|L | **Model**: gpt-4o[-mini] | **Epic**: N (Epic title)

**Context**: One sentence explaining WHY this story exists and what the prior state was.

**Files**:
- `services/path/to/file.py` (create|update -- one-line note)
- `services/tests/test_ACA-NN-NNN_name.py` (create)

**Acceptance**:
- `file.py` has `# EVA-STORY: ACA-NN-NNN` tag
- <functional assertion -- what the code does>
- `test_ACA-NN-NNN_name.py`: `test_function_name` passes with mock <X>
- `pytest services/tests/test_name.py` exits 0

**Implementation notes**: <5-8 sentences: import paths, class signatures, mock
patterns, DI pattern reminder, EVA-STORY tag placement, known pitfalls>

**Spec references**: `docs/NN-spec.md` (relevant section)

<!-- END STORY: ACA-NN-NNN -->
```

### Commit message format (agent PRs)

```
<type>(ACA-NN-NNN): <imperative description>
```

Types: `feat`, `fix`, `test`, `chore`, `docs`, `refactor`
Example: `feat(ACA-04-006): add token_service.py with MSAL multi-tenant device-code flow`

### Branch format (sprint-agent branch)

```
agent/ACA-NN-NNN-YYYYMMDD-HHMMSS
```

---

## COMMON PITFALLS

| Pitfall | Symptom | Fix |
|---|---|---|
| Story IDs invented from memory | Veritas returns orphan artifacts | Always read from .eva/veritas-plan.json |
| Tag on wrong file type | Coverage does not increase after tag | Check file extension is .py/.ts/.tsx/.yaml |
| `done=True` in plan without code artifact | MTI consistency penalty | Only mark done when code + tag + test all exist |
| Inline PowerShell PUT with JSON | 422 or silent wrong value | Always write to temp .ps1 file, run with -File (Rule 6) |
| Missing `account_key` in generate_blob_sas | SAS URL generated but unusable | Use `account_key=` not `credential=` |
| pytest fails because of missing env vars | Collection error or import error | Use `Field(default='')` pattern in settings.py for all optional fields |
| model.author set to `modified_by` mismatch | Commit validation fails | Use `Headers @{"X-Actor"="agent:copilot"}` on every PUT |
| Wrong branch name pushed | sprint-agent.yml does not trigger | Branch must start with `agent/` for auto-trigger |
| Missing `# EVA-STORY` tag on test file | Evidence gap not closed | Tag must be in the first 15 lines of the test file |
| Manifest TODO fields left unfilled | Agent generates nonsense implementation | Fill ALL TODO fields before `gh issue create` |

---

## QUICK COMMAND REFERENCE

```powershell
# Run full audit
node C:\eva-foundry\48-eva-veritas\src\cli.js audit --repo C:\eva-foundry\51-ACA --warn-only

# Check MTI
(Get-Content C:\eva-foundry\51-ACA\.eva\trust.json | ConvertFrom-Json).mti

# List undone stories grouped by epic
$vp = Get-Content C:\eva-foundry\51-ACA\.eva\veritas-plan.json | ConvertFrom-Json
foreach ($f in $vp.features) {
    $u = $f.stories | Where-Object { -not $_.done }
    if ($u) { Write-Host "$($f.id): $($u.Count) undone" }
}

# Reseed after PLAN.md change
C:\eva-foundry\.venv\Scripts\python.exe scripts/seed-from-plan.py --reseed-model

# Reflect IDs into PLAN.md
C:\eva-foundry\.venv\Scripts\python.exe scripts/reflect-ids.py

# Generate sprint manifest
C:\eva-foundry\.venv\Scripts\python.exe scripts/gen-sprint-manifest.py --sprint NN --name "name" `
    --stories ACA-NN-NNN,ACA-NN-NNN

# Create GitHub issue
gh issue create --repo eva-foundry/51-ACA --title "[SPRINT-NN] name" `
    --body-file .github/sprints/sprint-NN-name.md --label "sprint-task"

# Data model health
Invoke-RestMethod http://localhost:8055/health
Invoke-RestMethod http://localhost:8055/model/agent-summary | Select-Object total
```
