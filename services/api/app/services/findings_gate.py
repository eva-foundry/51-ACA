# EVA-STORY: ACA-03-008

TIER1_FIELDS = {
    "id", "category", "title", "estimated_saving_low", "estimated_saving_high",
    "effort_class", "risk_class"
}

TIER2_FIELDS = {
    "id", "category", "title", "estimated_saving_low", "estimated_saving_high",
    "effort_class", "risk_class", "narrative", "evidence_refs"
}

TIER3_FIELDS = None  # Placeholder for full pass-through fields

def gate_findings(findings: list[dict], tier: str) -> list[dict]:
    """
    Gate findings based on client tier.

    Args:
        findings: List of raw findings.
        tier: Client tier ("tier1", "tier2", "tier3").

    Returns:
        List of gated findings.
    """
    if tier == "tier1":
        return [{k: v for k, v in finding.items() if k in TIER1_FIELDS} for finding in findings]
    elif tier == "tier2":
        return [{k: v for k, v in finding.items() if k in TIER2_FIELDS} for finding in findings]
    elif tier == "tier3":
        return findings  # Full pass-through
    else:
        raise ValueError(f"Unsupported tier: {tier}")
