"""R-09: DNS sprawl detection"""

def evaluate_dns_sprawl(inventory, cost_data, advisor_data):
    """Returns finding if annual DNS cost > $1,000"""
    dns_cost = sum(
        float(row.get("MeterCost", 0))
        for row in cost_data
        if "DNS" in row.get("MeterName", "")
    )
    
    if dns_cost > 1000:
        return {
            "id": "rule-09-dns-sprawl",
            "category": "network",
            "title": "DNS zone consolidation opportunity",
            "estimated_saving_low": dns_cost * 0.15,
            "estimated_saving_high": dns_cost * 0.25,
            "effort_class": "easy",
            "risk_class": "low",
            "heuristic_source": "rule-09",
            "narrative": f"Annual DNS costs of ${dns_cost:.0f} suggest consolidation opportunity",
        }
    return None
