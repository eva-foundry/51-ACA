"""Rule 07: Cognitive Search SKU Oversize -- Source: 14-az-finops #7"""
RULE_ID = "rule-07-search-sku-oversize"

def rule_07_search_sku_oversize(data: dict) -> dict | None:
    cost_rows = data.get("cost_rows", [])
    search_rows = [r for r in cost_rows if "cognitive search" in str(r.get("MeterCategory", "")).lower()
                   or "azure ai search" in str(r.get("MeterCategory", "")).lower()]
    if not search_rows:
        return None
    annual = sum(float(r.get("Cost", 0)) for r in search_rows) / len(search_rows) * 365
    if annual < 2000:
        return None
    return {
        "id": RULE_ID, "category": "sku-right-sizing",
        "title": "Azure AI Search instances may be running on oversized SKUs",
        "estimated_saving_low": round(annual * 0.32), "estimated_saving_high": round(annual * 0.48),
        "effort_class": "medium", "risk_class": "medium",
        "heuristic_source": RULE_ID,
        "narrative": "Search costs are elevated relative to typical dev workloads. S1 instances at ~$259/month vs Basic at ~$73/month represent a 72% per-instance saving where index and replica counts permit.",
        "deliverable_template_id": "tmpl-search-sku",
    }
