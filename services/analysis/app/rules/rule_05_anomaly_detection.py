"""
# EVA-STORY: ACA-03-015
Rule 05: Anomaly Detection (z-score)
Source: 14-az-finops saving-opportunities.md #5
Saving: $156K+ per incident prevented
Effort: easy | Risk: none
"""
import statistics

RULE_ID = "rule-05-anomaly-detection"
Z_THRESHOLD = 3.0
HIGH_RISK_CATEGORIES = {"foundry tools", "azure openai", "container apps"}


def _z_scores(values: list[float]) -> list[float]:
    if len(values) < 5:
        return [0.0] * len(values)
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    if stdev == 0:
        return [0.0] * len(values)
    return [(v - mean) / stdev for v in values]


def rule_05_anomaly_detection(data: dict) -> list[dict]:
    """
    Detect z-score anomalies (z > 3.0) in daily cost series per MeterCategory.
    Flags categories with recent anomalies as high-risk runaway spend candidates.
    """
    cost_rows = data.get("cost_rows", [])
    if not cost_rows:
        return []

    from collections import defaultdict
    by_category: dict[str, list[float]] = defaultdict(list)
    for r in cost_rows:
        cat = str(r.get("MeterCategory", "unknown")).lower()
        try:
            by_category[cat].append(float(r.get("Cost", 0)))
        except (ValueError, TypeError):
            pass

    findings = []
    for cat, costs in by_category.items():
        zscores = _z_scores(costs)
        max_z = max(zscores) if zscores else 0
        if max_z >= Z_THRESHOLD:
            high_risk = any(h in cat for h in HIGH_RISK_CATEGORIES)
            findings.append({
                "id": f"{RULE_ID}-{cat.replace(' ', '-')[:30]}",
                "category": "anomaly-detection",
                "title": f"Potential runaway spend detected in '{cat}' (spike index: {max_z:.1f})",
                "estimated_saving_low": 0,
                "estimated_saving_high": 0,
                "effort_class": "easy",
                "risk_class": "high" if high_risk else "medium",
                "heuristic_source": RULE_ID,
                "narrative": (
                    f"Daily cost series for '{cat}' shows a statistical anomaly "
                    f"(spike index {max_z:.1f}). Historical incidents in similar patterns "
                    "have resulted in significant unplanned spend before detection."
                ),
                "deliverable_template_id": "tmpl-anomaly-alert",
            })
    return findings
