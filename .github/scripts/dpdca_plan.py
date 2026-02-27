"""
DPDCA Plan Step -- calls LLM to generate a numbered implementation plan.
Called by dpdca-agent.yml P step.
EVA-STORY: ACA-14-004
"""
import os
import json
import urllib.request
import urllib.error

story_id = os.environ.get("STORY_ID", "UNKNOWN")
issue_body = os.environ.get("ISSUE_BODY", "")

try:
    with open("agent-context.txt", "r", errors="ignore") as f:
        context = f.read()[:8000]
except FileNotFoundError:
    context = "(context file not found)"

system_prompt = (
    "You are a senior Python/FastAPI engineer implementing a sprint story for ACA "
    "(Azure Cost Advisor). "
    "ACA rules: ASCII-only output. Tenant isolation via Cosmos partition_key=subscriptionId. "
    "Tier gating via gate_findings() in findings.py. MSAL multi-tenant authority=common. "
    "Follow patterns in services/api/app/. Tests go in services/api/tests/. "
    "Ruff clean. Mypy clean. "
    "Output format: numbered implementation plan (1-10 steps), each step: "
    "action + file + code snippet."
)

user_prompt = (
    f"Story: {story_id}\n\n"
    f"ISSUE BODY:\n{issue_body[:3000]}\n\n"
    f"PROJECT CONTEXT (excerpt):\n{context[:4000]}\n\n"
    "Generate a concrete numbered implementation plan for this story. Be specific about:\n"
    "- Which files to create or modify\n"
    "- What functions/classes to add\n"
    "- Test cases to write\n"
    f"- EVA-STORY tag to add: # EVA-STORY: {story_id}\n"
    "- Acceptance criteria verification"
)

az_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
az_key = os.environ.get("AZURE_OPENAI_KEY", "")
deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
gh_token = os.environ.get("GITHUB_TOKEN", "")

if az_endpoint and az_key:
    url = (
        f"{az_endpoint}/openai/deployments/{deployment}"
        "/chat/completions?api-version=2024-08-01-preview"
    )
    headers = {"Content-Type": "application/json", "api-key": az_key}
else:
    url = "https://models.inference.ai.azure.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {gh_token}",
    }

payload = {
    "model": deployment,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    "max_tokens": 2000,
    "temperature": 0.2,
}

try:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers=headers
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    plan_text = result["choices"][0]["message"]["content"]
    print(f"[INFO] LLM plan generated ({len(plan_text)} chars)")
except Exception as e:
    plan_text = (
        f"[WARN] LLM call failed: {e}\n\n"
        f"Fallback: Implement {story_id} per PLAN.md spec. "
        "See .github/copilot-instructions.md for patterns."
    )
    print(f"[WARN] LLM unavailable: {e}")

with open("agent-plan.md", "w", encoding="utf-8") as f:
    f.write(f"# Agent Implementation Plan: {story_id}\n\n")
    f.write(plan_text)

print("[INFO] Plan written to agent-plan.md")
print(plan_text[:500])
