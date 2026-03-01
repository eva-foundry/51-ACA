# EVA-STORY: ACA-03-021
# EVA-STORY: ACA-03-004
# EVA-STORY: ACA-03-005
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
        self.status = "queued"
        self.persist_status()

    def record_failure(self, rule_id: str):
        self.failed_rules.append(rule_id)

    def add_findings(self, findings):
        self.findings.extend(findings)

    def persist(self):
        findings_summary = {
            "findingCount": len(self.findings),
            "totalSavingLow": sum(f["estimated_saving_low"] for f in self.findings),
            "totalSavingHigh": sum(f["estimated_saving_high"] for f in self.findings),
            "categories": list(set(f["category"] for f in self.findings))
        }

        doc = {
            "id": self.run_id,
            "subscriptionId": self.subscription_id,
            "failed_rules": self.failed_rules,
            "findings": self.findings,
            "status": self.status,
            "findingsSummary": findings_summary
        }
        upsert_item("analysis_runs", doc, partition_key=self.subscription_id)

    def update_status(self, status: str):
        self.status = status
        self.persist_status()

    def persist_status(self):
        doc = {
            "id": self.run_id,
            "subscriptionId": self.subscription_id,
            "status": self.status,
        }
        upsert_item("analysis_runs", doc, partition_key=self.subscription_id)

def run_analysis(run_id: str, subscription_id: str, rules: list):
    analysis_run = AnalysisRun(run_id, subscription_id)

    analysis_run.update_status("running")

    for rule in rules:
        try:
            findings = rule.execute(subscription_id)
            gated_findings = gate_findings(findings, rule.tier)
            analysis_run.add_findings(gated_findings)
        except Exception as e:
            logger.error(f"[FAIL] Rule execution failed: {rule.id} - {str(e)}")
            analysis_run.record_failure(rule.id)

    if analysis_run.failed_rules:
        analysis_run.update_status("failed")
    else:
        analysis_run.update_status("succeeded")

    analysis_run.persist()
    logger.info(f"[INFO] Analysis run completed: {run_id}")
