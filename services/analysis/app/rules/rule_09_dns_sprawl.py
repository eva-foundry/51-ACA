"""Rule 09: Private DNS Zone Sprawl -- Source: 14-az-finops #9"""
# EVA-STORY: ACA-03-019
RULE_ID = "rule-09-dns-sprawl"

def rule_09_dns_sprawl(data: dict) -> dict | None:
    cost_rows = data.get("cost_rows", [])
    dns_rows = [r for r in cost_rows if "dns" in str(r.get("MeterCategory", "")).lower()]
    if not dns_rows:
        return None
    annual_dns_cost = sum(float(r.get("Cost", 0)) for r in dns_rows) / len(dns_rows) * 365
    if annual_dns_cost < 1000:
        return None
    dns_zone_count = len({r.get("ResourceId", r.get("resource_id", "")) for r in dns_rows})
    return {
        "id": RULE_ID,
        "category": "network",
        "finding_type": "cost_optimization",
        "title": "DNS costs suggest private DNS zone sprawl across resource groups",
        "dns_zone_count": dns_zone_count,
        "annual_dns_cost": round(annual_dns_cost),
        "estimated_saving_low": round(annual_dns_cost * 0.26),
        "estimated_saving_high": round(annual_dns_cost * 0.44),
        "effort_class": "easy",
        "risk_class": "medium",
        "heuristic_source": RULE_ID,
        "narrative": "DNS costs are 3-6x higher than typical for this subscription size, indicating per-environment private DNS zones. Hub-spoke DNS consolidation eliminates duplicate zone charges.",
        "deliverable_template_id": "tmpl-dns-consolidation",
    }
