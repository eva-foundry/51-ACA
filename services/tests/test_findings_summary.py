# EVA-STORY: ACA-03-005
import pytest
from unittest.mock import MagicMock
from services.analysis.app.main import AnalysisRun

def test_findings_summary_aggregation():
    mock_findings = [
        {"category": "compute", "estimated_saving_low": 100, "estimated_saving_high": 200},
        {"category": "storage", "estimated_saving_low": 50, "estimated_saving_high": 150},
        {"category": "compute", "estimated_saving_low": 200, "estimated_saving_high": 300}
    ]

    mock_upsert_item = MagicMock()
    AnalysisRun.persist = lambda self: mock_upsert_item("analysis_runs", {
        "id": self.run_id,
        "subscriptionId": self.subscription_id,
        "failed_rules": self.failed_rules,
        "findings": self.findings,
        "status": self.status,
        "findingsSummary": {
            "findingCount": len(self.findings),
            "totalSavingLow": sum(f["estimated_saving_low"] for f in self.findings),
            "totalSavingHigh": sum(f["estimated_saving_high"] for f in self.findings),
            "categories": list(set(f["category"] for f in self.findings))
        }
    }, partition_key=self.subscription_id)

    analysis_run = AnalysisRun(run_id="test-run", subscription_id="test-sub")
    analysis_run.add_findings(mock_findings)
    analysis_run.persist()

    mock_upsert_item.assert_called_once()
    args, kwargs = mock_upsert_item.call_args
    doc = args[1]

    assert doc["findingsSummary"]["findingCount"] == 3
    assert doc["findingsSummary"]["totalSavingLow"] == 350
    assert doc["findingsSummary"]["totalSavingHigh"] == 650
    assert set(doc["findingsSummary"]["categories"]) == {"compute", "storage"}
