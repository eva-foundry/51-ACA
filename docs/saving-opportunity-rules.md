# ACA Saving Opportunity Rules Reference
# EVA-STORY: ACA-12-002

Version: 1.0.0
Updated: 2026-02-27
Status: AUTHORITATIVE -- agents must read this before implementing any analysis rule story.

---

## 1. Overview

The ACA analysis engine executes 12 rules against collected Azure inventory, cost data,
and Advisor recommendations. Each rule produces zero or more FINDING records.

Rules are independent Python modules under services/analysis/app/rules/.
Each module exposes a single function: `run(inventory: dict, cost_data: list, advisor: list) -> list[dict]`.

---

## 2. FINDING Schema

Every rule MUST return a list of dicts conforming to this shape exactly.
Do not invent new fields. Extensions go in the `extra` dict only.

```python
FINDING = {
    # Required -- all tiers
    "id": str,                        # kebab-case, globally unique, stable: e.g. "aca-rule-01-devbox-001"
    "rule_id": str,                   # parent rule ID: "rule_01" through "rule_12"
    "category": str,                  # see category list below
    "title": str,                     # plain English, no how-to, no PII: max 80 chars
    "estimated_saving_low": int,      # CAD/year integer, conservative estimate
    "estimated_saving_high": int,     # CAD/year integer, optimistic estimate
    "effort_class": str,              # trivial | easy | medium | involved | strategic
    "risk_class": str,                # none | low | medium | high
    "heuristic_source": str,          # rule ID string, e.g. "rule_01"

    # Required -- Tier 2+ only (strip from Tier 1 gate)
    "narrative": str,                 # plain English explanation, 2-4 sentences

    # Required -- Tier 3 only (strip from Tier 1 and Tier 2 gates)
    "deliverable_template_id": str,   # exact template ID from column 4 below

    # Optional
    "resource_ids": list[str],        # affected Azure resource IDs
    "extra": dict,                    # rule-specific metadata
}
```

Valid category values:
- compute-scheduling
- log-retention
- defender-optimization
- cost-anomaly
- stale-resource
- search-optimization
- registry-consolidation
- dns-consolidation
- commitment-discount
- api-cost-control
- cost-allocation
- security-hardening

---

## 3. Rules Reference (12 rules)

| Rule ID | Category | Title | Low Saving (CAD/yr) | High Saving (CAD/yr) | Effort | Risk | Template ID |
|---|---|---|---|---|---|---|---|
| rule_01 | compute-scheduling | Dev Box instances run nights and weekends | 5548 | 7902 | trivial | none | tmpl-devbox-autostop |
| rule_02 | log-retention | Log Analytics workspaces retain data beyond 30 days | 1200 | 3600 | trivial | none | tmpl-log-retention |
| rule_03 | defender-optimization | Defender for Cloud plans enabled on non-production resources | 2400 | 4800 | easy | low | tmpl-defender-plan |
| rule_04 | compute-scheduling | VMs running 24x7 with no scheduled shutdown | 8000 | 15000 | easy | low | tmpl-compute-schedule |
| rule_05 | cost-anomaly | Unexpected cost spike exceeds 20% week-over-week | varies | varies | medium | medium | tmpl-anomaly-alert |
| rule_06 | stale-resource | Dev/test environments idle for 14+ days | 3000 | 9000 | trivial | none | tmpl-stale-envs |
| rule_07 | search-optimization | Azure AI Search on Standard tier with low query volume | 2100 | 5400 | involved | medium | tmpl-search-sku |
| rule_08 | registry-consolidation | Multiple Container Registries with overlapping content | 1200 | 2400 | involved | low | tmpl-acr-consolidation |
| rule_09 | dns-consolidation | Multiple Azure DNS zones covering same domain hierarchy | 600 | 1200 | medium | low | tmpl-dns-consolidation |
| rule_10 | commitment-discount | Pay-as-you-go compute eligible for 1-year savings plan | 12000 | 28000 | strategic | low | tmpl-savings-plan |
| rule_11 | api-cost-control | APIM without token budget policy on AI-backed products | 4000 | 18000 | easy | none | tmpl-apim-token-budget |
| rule_12 | cost-allocation | Resources missing mandatory cost-center tags | 0 | 0 | easy | none | tmpl-chargeback-policy |

Note: rule_05 and rule_12 saving amounts are subscription-specific (depends on actual spend and
tagging gaps). The FINDING must populate estimated_saving_low and estimated_saving_high from
collected cost data, not hardcode them.

---

## 4. Rule Module Contract

```python
# services/analysis/app/rules/rule_01.py
# EVA-STORY: ACA-03-001

from typing import Any

RULE_ID = "rule_01"
DELIVERABLE_TEMPLATE_ID = "tmpl-devbox-autostop"

def run(
    inventory: dict[str, Any],
    cost_data: list[dict],
    advisor: list[dict],
) -> list[dict]:
    """
    Scan inventory for DevTest Labs / Dev Box resources without autostop policy.
    Returns list of FINDING records.
    """
    findings = []
    dev_resources = [
        r for r in inventory.get("resources", [])
        if r.get("type", "").lower() in (
            "microsoft.devtestlab/labs",
            "microsoft.devcenter/devboxdefinitions",
        )
    ]
    for resource in dev_resources:
        # Check for autostop policy
        if not _has_autostop(resource):
            findings.append({
                "id": f"aca-rule-01-{resource['id'][-8:]}",
                "rule_id": RULE_ID,
                "category": "compute-scheduling",
                "title": f"Dev resource lacks autostop: {resource['name']}",
                "estimated_saving_low": 5548,
                "estimated_saving_high": 7902,
                "effort_class": "trivial",
                "risk_class": "none",
                "heuristic_source": RULE_ID,
                "narrative": (
                    "Dev Box and DevTest Labs resources without autostop policies "
                    "continue running overnight and on weekends. Enabling autostop "
                    "at 18:00 local time typically reduces compute hours by 60-70%, "
                    "saving CAD 5,500-7,900 per resource annually."
                ),
                "deliverable_template_id": DELIVERABLE_TEMPLATE_ID,
                "resource_ids": [resource["id"]],
            })
    return findings

def _has_autostop(resource: dict) -> bool:
    props = resource.get("properties", {})
    return bool(props.get("shutdownTime") or props.get("autoShutdownProfile"))
```

---

## 5. FindingsAssembler (analysis/findings.py)

The analysis entry point (services/analysis/app/main.py) must instantiate FindingsAssembler
with THREE arguments. Missing cosmos_client causes TypeError at runtime (bug C-04).

```python
# CORRECT instantiation
from services.analysis.app.findings import FindingsAssembler

assembler = FindingsAssembler(
    scan_id=scan_id,
    subscription_id=sub_id,
    cosmos_client=cosmos_client,   # REQUIRED -- was missing, see C-04
)
```

FindingsAssembler.save_findings() upserts findings to Cosmos with partition key = subscriptionId.
FindingsAssembler.mark_analysis_complete() sets scan status = "complete" in scans container.

---

## 6. Rule Execution Order

Rules are independent and can run in any order or in parallel.
The analysis engine runs all 12 rules and aggregates findings.

Suggested execution sequence for serial mode:
1. rule_01 -- Dev Box autostop (fast, low API calls)
2. rule_02 -- Log retention (fast)
3. rule_03 -- Defender plans (moderate)
4. rule_04 -- VM scheduling (fast, large inventory)
5. rule_05 -- Cost anomaly (requires cost_data, may be slow)
6. rule_06 -- Stale environments (moderate)
7. rule_07 -- Search SKU (fast)
8. rule_08 -- ACR consolidation (moderate)
9. rule_09 -- DNS consolidation (fast)
10. rule_10 -- Savings plan eligibility (requires cost_data)
11. rule_11 -- APIM token budget (fast)
12. rule_12 -- Chargeback tags (fast, large inventory)

---

## 7. Tier Gating Summary

| Field | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| id | YES | YES | YES |
| title | YES | YES | YES |
| category | YES | YES | YES |
| estimated_saving_low | YES | YES | YES |
| estimated_saving_high | YES | YES | YES |
| effort_class | YES | YES | YES |
| risk_class | NO | YES | YES |
| heuristic_source | NO | YES | YES |
| narrative | NO | YES | YES |
| deliverable_template_id | NO | NO | YES |
| resource_ids | NO | YES | YES |

---

*See also: 05-technical.md (gate_findings pattern), 12-IaCscript.md (template library)*
