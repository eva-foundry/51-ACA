# EVA-STORY: ACA-03-007
"""
Findings tier-gating logic -- pure business rules, no I/O dependencies.
Extracted so unit tests can import without pulling in Cosmos/settings chain.
"""
from typing import Any

TIER1_FIELDS = frozenset({
    "id", "category", "title",
    "estimated_saving_low", "estimated_saving_high",
    "effort_class", "risk_class",
})

TIER2_FIELDS = TIER1_FIELDS | frozenset({"narrative", "heuristic_source"})
# Tier 3: all fields including deliverable_template_id


def gate_findings(findings: list[dict[str, Any]], tier: str) -> list[dict[str, Any]]:
    """
    Strip findings to tier-appropriate fields.
    NEVER expose narrative or deliverable_template_id to Tier 1.
    """
    if tier == "tier1":
        return [{k: v for k, v in f.items() if k in TIER1_FIELDS} for f in findings]
    if tier == "tier2":
        return [{k: v for k, v in f.items() if k in TIER2_FIELDS} for f in findings]
    return list(findings)  # tier3: full object
