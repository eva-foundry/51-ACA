# EVA-STORY: ACA-03-009

TIER1_FIELDS = [
    "id", "category", "title", "estimated_saving_low", "estimated_saving_high",
    "effort_class", "risk_class"
]

TIER2_FIELDS = TIER1_FIELDS + ["narrative", "heuristic_source"]

TIER3_FIELDS = [
    "id", "category", "title", "estimated_saving_low", "estimated_saving_high",
    "effort_class", "risk_class", "narrative", "evidence_refs", "deliverable_template_id"
]

def gate_findings(findings: list[dict], tier: str) -> list[dict]:
    """
    Filters findings based on client tier.

    Args:
        findings: List of findings (dicts).
        tier: Client tier ("tier1", "tier2", "tier3").

    Returns:
        List of filtered findings.
    """
    if tier == "tier1":
        return [{key: finding[key] for key in TIER1_FIELDS if key in finding} for finding in findings]
    elif tier == "tier2":
        return [{key: finding[key] for key in TIER2_FIELDS if key in finding} for finding in findings]
    elif tier == "tier3":
        return findings  # Full pass-through for Tier 3
    else:
        raise ValueError(f"Unknown tier: {tier}")
