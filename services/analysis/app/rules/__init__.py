"""
# EVA-STORY: ACA-03-001
Rule registry -- imports and exports all 12 analysis rules.
"""
from app.rules.rule_01_devbox_autostop import rule_01_devbox_autostop
from app.rules.rule_02_log_retention import rule_02_log_retention
from app.rules.rule_03_defender_mismatch import rule_03_defender_mismatch
from app.rules.rule_04_compute_scheduling import rule_04_compute_scheduling
from app.rules.rule_05_anomaly_detection import rule_05_anomaly_detection
from app.rules.rule_06_stale_environments import rule_06_stale_environments
from app.rules.rule_07_search_sku_oversize import rule_07_search_sku_oversize
from app.rules.rule_08_acr_consolidation import rule_08_acr_consolidation
from app.rules.rule_09_dns_sprawl import rule_09_dns_sprawl
from app.rules.rule_10_savings_plan_coverage import rule_10_savings_plan_coverage
from app.rules.rule_11_apim_token_budget import rule_11_apim_token_budget
from app.rules.rule_12_chargeback_gap import rule_12_chargeback_gap

ALL_RULES = [
    rule_01_devbox_autostop,
    rule_02_log_retention,
    rule_03_defender_mismatch,
    rule_04_compute_scheduling,
    rule_05_anomaly_detection,
    rule_06_stale_environments,
    rule_07_search_sku_oversize,
    rule_08_acr_consolidation,
    rule_09_dns_sprawl,
    rule_10_savings_plan_coverage,
    rule_11_apim_token_budget,
    rule_12_chargeback_gap,
]
