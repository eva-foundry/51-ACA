"""
# EVA-STORY: ACA-03-019
Rule R-09: DNS Sprawl Detection
Source: 14-az-finops saving-opportunities.md #9
Saving: 30% consolidation savings
Effort: easy | Risk: low
"""

RULE_ID = "r09-dns-sprawl"


def r09_dns_sprawl(data: dict) -> dict | None:
    """
    Detects when annual DNS cost exceeds $1,000, indicating private DNS zone sprawl.
    Aggregates cost WHERE service contains 'dns' across all cost rows.
    """
    cost_rows = data.get("cost_rows", [])
    dns_rows = [
        r for r in cost_rows
        if "dns" in str(r.get("MeterCategory", "")).lower()
        or "dns" in str(r.get("ServiceName", "")).lower()
        or "dnszones" in str(r.get("ResourceType", "")).lower()
    ]
    if not dns_rows:
        return None

    dns_zone_count = len({r.get("ResourceId", r.get("resourceId", i)) for i, r in enumerate(dns_rows)})
    annual_dns_cost = round(sum(float(r.get("Cost", 0)) for r in dns_rows) / max(len(dns_rows), 1) * 365, 2)

    if annual_dns_cost < 1000:
        return None

    return {
        "id": RULE_ID,
        "finding_type": "cost_optimization",
        "category": "network",
        "title": "DNS zone sprawl: per-environment private DNS zones create excess charges",
        "dns_zone_count": dns_zone_count,
        "annual_dns_cost": annual_dns_cost,
        "estimated_saving_low": round(annual_dns_cost * 0.30),
        "estimated_saving_high": round(annual_dns_cost * 0.30),
        "effort_class": "easy",
        "risk_class": "low",
        "heuristic_source": RULE_ID,
        "narrative": (
            f"Annual DNS spend of ${annual_dns_cost:.0f} across {dns_zone_count} zone(s) "
            "indicates per-environment private DNS zone sprawl. Consolidating to a hub-spoke "
            "DNS model typically yields 30% cost reduction with no service disruption."
        ),
        "deliverable_template_id": "tmpl-dns-consolidation",
    }
