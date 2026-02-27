### Story ID

ACA-14-008

### WBS ID

14.3.1

### Epic

Epic 10 -- DPDCA Cloud Agent

### Function Point Size

S (3 FP) -- single route or component, no new schema

### Sprint

4

### User story

As the DPDCA agent, I need the Plan step to successfully reach the
GitHub Models API (models.inference.ai.azure.com) using the automatic
GITHUB_TOKEN so that the LLM can generate a concrete implementation
plan for each sprint story without requiring a separately managed API key.

### Inputs

- GITHUB_TOKEN (auto-provided by Actions runtime)
- agent-context.txt (loaded in D1 phase -- contains PLAN.md excerpt + decisions)
- Issue body text (story description, acceptance criteria)

### Outputs

- agent-plan.md written to workspace root (uploaded as artifact)
- .eva/evidence/ACA-14-008-YYYYMMDD.json receipt updated with plan char count

### Acceptance criteria

- [ ] Plan step exits 0 (no Python exception)
- [ ] agent-plan.md exists in workflow artifacts and contains at least 3 numbered steps
- [ ] Evidence receipt exists at .eva/evidence/ACA-14-008-YYYYMMDD.json
- [ ] If GitHub Models API is unreachable, fallback message appears in plan (not a crash)
- [ ] EVA-STORY tag present: # EVA-STORY: ACA-14-008

### Spec references

- PLAN.md: Epic 14, Feature 14.3, Story ACA-14-008
- .github/workflows/dpdca-agent.yml: P -- Generate implementation plan step
- copilot-instructions.md P2.5 Pattern 3 (MSAL token) for context

### Files to modify

- .github/workflows/dpdca-agent.yml (verify GitHub Models endpoint + GITHUB_TOKEN header)
- services/api/app/routers/admin.py (add EVA-STORY: ACA-14-008 tag as comment)
- .eva/evidence/ (new receipt file)

### Constraints

- Do NOT hardcode any API keys in workflow YAML
- GITHUB_TOKEN is the only auth mechanism for the GitHub Models endpoint
- Fallback message on LLM failure must be ASCII-only (no emoji)

### Depends on

ACA-14-003 (D1 context loading -- must be done first)

### Agent pre-flight checklist

- [x] Story ID matches ACA-NN-NNN format: ACA-14-008
- [x] All acceptance criteria are testable (pass/fail)
- [x] Files to modify are repo-relative paths
- [x] Inputs and outputs are explicit
- [x] EVA-STORY tag format confirmed: # EVA-STORY: ACA-14-008
- [ ] Evidence receipt will be written by D2 phase
- [ ] Veritas MTI >= 70 after this story merges
