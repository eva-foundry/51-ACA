# ACA IaC Template Library
# EVA-STORY: ACA-12-002

Version: 1.0.0
Updated: 2026-02-27
Status: AUTHORITATIVE -- agents must read this before implementing any delivery or template story.

Note: This document specifies the IaC template library consumed by services/delivery/.
For the infrastructure bootstrap script (Phase 1/2 ACA provisioning), see the root
12-IaCscript.md file at the project root. These are separate concerns.

---

## 1. Overview

The Tier 3 deliverable is a ZIP file containing:
1. A set of IaC templates (Bicep Phase 1 / Terraform Phase 2) parametrized for the customer subscription
2. A FINDINGS.json summary of all findings for the subscription
3. A README.md with instructions
4. A manifest.json with SHA-256 hashes of all files in the ZIP

The delivery packager (services/delivery/app/) renders templates using Jinja2,
assembles the ZIP, uploads it to Azure Blob Storage, and returns a 7-day SAS URL.

---

## 2. Template Directory Structure

Each template category lives in its own folder under services/delivery/app/templates/.
Each folder contains exactly: main.bicep (or main.tf), README.md, variables.json.

```
services/delivery/app/templates/
  tmpl-devbox-autostop/
    main.bicep
    README.md
    variables.json
  tmpl-log-retention/
    main.bicep
    README.md
    variables.json
  tmpl-defender-plan/
    main.bicep
    README.md
    variables.json
  tmpl-compute-schedule/
    main.bicep
    README.md
    variables.json
  tmpl-anomaly-alert/
    main.bicep
    README.md
    variables.json
  tmpl-stale-envs/
    main.bicep
    README.md
    variables.json
  tmpl-search-sku/
    main.bicep
    README.md
    variables.json
  tmpl-acr-consolidation/
    main.bicep
    README.md
    variables.json
  tmpl-dns-consolidation/
    main.bicep
    README.md
    variables.json
  tmpl-savings-plan/
    main.bicep
    README.md
    variables.json
  tmpl-apim-token-budget/
    main.bicep
    README.md
    variables.json
  tmpl-chargeback-policy/
    main.bicep
    README.md
    variables.json
```

CURRENT STATE: All 12 folders are MISSING (0 of 12 exist). Templates directory is empty.
This is tracked as finding C-09 (delivery templates absent). Sprint 2 story ACA-07-005.

---

## 3. Template Catalogue (12 categories)

| Template ID | Rule | Category | Description |
|---|---|---|---|
| tmpl-devbox-autostop | rule_01 | compute-scheduling | Bicep policy to enable autostop on Dev Box at 18:00 local time |
| tmpl-log-retention | rule_02 | log-retention | Bicep to set Log Analytics workspace retention to 30 days |
| tmpl-defender-plan | rule_03 | defender-optimization | Bicep to scope Defender for Cloud plans to production workloads only |
| tmpl-compute-schedule | rule_04 | compute-scheduling | Bicep / Azure Automation runbook to schedule VM shutdown + startup |
| tmpl-anomaly-alert | rule_05 | cost-anomaly | Bicep to deploy Azure Monitor cost anomaly alert rule |
| tmpl-stale-envs | rule_06 | stale-resource | Bicep policy to tag and lock idle dev/test environments after 14 days |
| tmpl-search-sku | rule_07 | search-optimization | Bicep to downscale Azure AI Search from Standard to Basic tier |
| tmpl-acr-consolidation | rule_08 | registry-consolidation | Bicep to consolidate multiple ACR registries into one with geo-replication |
| tmpl-dns-consolidation | rule_09 | dns-consolidation | Bicep to merge overlapping DNS zones into a single zone hierarchy |
| tmpl-savings-plan | rule_10 | commitment-discount | Bicep + ARM to purchase 1-year compute savings plan |
| tmpl-apim-token-budget | rule_11 | api-cost-control | Bicep to add token budget policy to APIM AI Gateway product |
| tmpl-chargeback-policy | rule_12 | cost-allocation | Bicep Azure Policy to enforce mandatory cost-center tags on all resources |

---

## 4. Template File Contracts

### main.bicep (Jinja2 template, rendered before delivery)

Bicep file parametrized with Jinja2 variables. The generator replaces {{ var }}
tokens with values from the customer inventory before including in the ZIP.

Required Jinja2 variables:
- {{ subscription_id }} -- Azure subscription GUID
- {{ resource_group }} -- target resource group name
- {{ location }} -- Azure region (default: canadacentral)
- {{ resource_name }} -- affected Azure resource name (from finding.resource_ids)

Example (tmpl-log-retention/main.bicep):
```bicep
// EVA-STORY: ACA-07-005
// ACA generated template -- Log Analytics retention reduction
// Generated for subscription: {{ subscription_id }}
// DO NOT commit with real subscription IDs

targetScope = 'resourceGroup'

param workspaceName string = '{{ resource_name }}'
param retentionInDays int = 30

resource workspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: workspaceName
}

resource retentionPolicy 'Microsoft.OperationalInsights/workspaces/retentionInDays@2022-10-01' = {
  parent: workspace
  name: 'default'
  properties: {
    retentionInDays: retentionInDays
  }
}
```

Phase 1 goal: stub Bicep templates are acceptable -- they must exist, render without error,
and include all required Jinja2 variables. Full production templates are Sprint 3+ work.

### README.md (per template)

Must contain:
1. What this template does (one sentence)
2. Prerequisites (roles needed to deploy)
3. Deployment command:
   ```
   az deployment group create \
     --resource-group <rg> \
     --template-file main.bicep \
     --parameters workspaceName=<name>
   ```
4. Estimated saving range (from rule reference)
5. Risk class and effort class

### variables.json (per template)

Machine-readable parameter schema for the generator:

```json
{
  "template_id": "tmpl-log-retention",
  "rule_id": "rule_02",
  "jinja2_vars": ["subscription_id", "resource_group", "location", "resource_name"],
  "bicep_params": [
    {"name": "workspaceName", "type": "string", "source": "resource_name"},
    {"name": "retentionInDays", "type": "int", "default": 30}
  ]
}
```

---

## 5. Generator Flow (services/delivery/app/generator.py)

```python
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

TEMPLATES_DIR = Path(__file__).parent / "templates"

def render_template(template_id: str, variables: dict) -> dict[str, str]:
    """
    Render all files in a template folder with Jinja2 substitution.
    Returns dict of filename -> rendered content.
    Raises TemplateNotFound if template_id folder does not exist.
    """
    template_dir = TEMPLATES_DIR / template_id
    if not template_dir.exists():
        raise TemplateNotFound(f"Template directory missing: {template_id}")

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    rendered = {}
    for filename in ("main.bicep", "README.md"):
        try:
            tmpl = env.get_template(filename)
            rendered[filename] = tmpl.render(**variables)
        except TemplateNotFound:
            raise TemplateNotFound(f"Missing file {filename} in {template_id}")
    return rendered
```

Note: The current generator.py swallows TemplateNotFound silently (bug C-09).
Fix: let the exception propagate so the packager records the failure and the scan
status is set to "partial_delivery" instead of crashing silently.

---

## 6. Packager SAS URL Rules (services/delivery/app/packager.py)

Phase 1 specs:
- SAS_HOURS = 168 (7 days). Do NOT use 24. See bug C-07.
- generate_blob_sas() must use the storage account KEY, not DefaultAzureCredential.
  DefaultAzureCredential() is NOT valid as the `credential` parameter for SAS generation.
- The ZIP must include a manifest.json at the root with SHA-256 hashes of all included files.

Correct SAS generation pattern:
```python
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import timedelta, timezone, datetime

sas_token = generate_blob_sas(
    account_name=account_name,
    container_name=container_name,
    blob_name=blob_name,
    account_key=account_key,          # NOT DefaultAzureCredential
    permission=BlobSasPermissions(read=True),
    expiry=datetime.now(timezone.utc) + timedelta(hours=SAS_HOURS),
)
```

---

## 7. ZIP Manifest Schema (manifest.json)

```json
{
  "generated_at": "2026-MM-DDTHH:MM:SSZ",
  "scan_id": "...",
  "subscription_id": "...",
  "templates": [
    {
      "template_id": "tmpl-devbox-autostop",
      "rule_id": "rule_01",
      "files": [
        {"name": "tmpl-devbox-autostop/main.bicep", "sha256": "..."},
        {"name": "tmpl-devbox-autostop/README.md", "sha256": "..."}
      ]
    }
  ],
  "findings_sha256": "...",
  "manifest_version": "1.0"
}
```

---

## 8. Phase 1 / Phase 2 Template Format

Phase 1: Bicep templates only (infra/phase1-marco/ patterns).
Phase 2: Terraform modules from 18-azure-best/04-terraform-modules become available.

For Phase 2, the generator must detect which format the customer prefers and render
accordingly. The template_format field in the delivery trigger request determines this:
- "bicep" (default, Phase 1)
- "terraform" (Phase 2+)

---

*See also: saving-opportunity-rules.md (12 rule reference + template IDs), 05-technical.md (delivery endpoint)*
