# EVA-STORY: ACA-03-002
from app.db.cosmos import upsert_item
from app.settings import get_settings
from app.services.findings_gate import gate_findings
import logging

logger = logging.getLogger("analysis")

class AnalysisRun:
    def __init__(self, run_id: str, subscription_id: str):
        self.run_id = run_id
        self.subscription_id = subscription_id
        self.failed_rules = []
        self.findings = []

    def record_failure(self, rule_id: str):
        self.failed_rules.append(rule_id)

    def add_findings(self, findings):
        self.findings.extend(findings)

    def persist(self):
        doc = {
            "id": self.run_id,
            "subscriptionId": self.subscription_id,
            "failed_rules": self.failed_rules,
            "findings": self.findings,
        }
        upsert_item("analysis_runs", doc, partition_key=self.subscription_id)

def run_analysis(run_id: str, subscription_id: str, rules: list):
    analysis_run = AnalysisRun(run_id, subscription_id)

    for rule in rules:
        try:
            findings = rule.execute(subscription_id)
            gated_findings = gate_findings(findings, rule.tier)
            analysis_run.add_findings(gated_findings)
        except Exception as e:
            logger.error(f"[FAIL] Rule execution failed: {rule.id} - {str(e)}")
            analysis_run.record_failure(rule.id)

    analysis_run.persist()
    logger.info(f"[INFO] Analysis run completed: {run_id}")