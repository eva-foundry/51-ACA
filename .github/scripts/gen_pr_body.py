"""
DPDCA Gen PR Body -- writes the PR body for gh pr create to stdout.
Called by dpdca-agent.yml A step.
Usage: python3 gen_pr_body.py > /tmp/pr-body.md
EVA-STORY: ACA-14-007
"""
import os
import sys

story_id = os.environ.get("STORY_ID", "UNKNOWN")
wbs_id = os.environ.get("WBS_ID", "UNKNOWN")
epic = os.environ.get("EPIC", "UNKNOWN")
issue_num = os.environ.get("ISSUE_NUM", "0")
branch = os.environ.get("BRANCH_NAME", "")
lint = "pass" if os.environ.get("LINT_STATUS", "1") == "0" else "warn"
test = "pass" if os.environ.get("TEST_STATUS", "1") == "0" else "warn"
lint_badge = "[PASS]" if lint == "pass" else "[WARN]"
test_badge = "[PASS]" if test == "pass" else "[WARN]"

plan_excerpt = ""
try:
    with open("agent-plan.md", errors="ignore") as f:
        plan_excerpt = "\n".join(f.readlines()[:30])
except FileNotFoundError:
    plan_excerpt = "Plan not generated"

body = f"""## DPDCA Agent: {story_id}

**Issue**: #{issue_num}  **WBS**: {wbs_id}
**Epic**: {epic}
**Branch**: `{branch}`  **Model**: gpt-4o-mini

### Gate Results
- Lint:  {lint_badge}
- Tests: {test_badge}

### Plan (first 30 lines)
```
{plan_excerpt}
```

### Reviewer Checklist
- [ ] Plan steps match acceptance criteria in issue
- [ ] No cross-tenant queries (partition_key=subscriptionId enforced)
- [ ] EVA-STORY tag present: `# EVA-STORY: {story_id}`
- [ ] `pytest services/ -x -q` exits 0 locally
- [ ] Data model updated if new endpoint or story shipped
"""

sys.stdout.write(body)
