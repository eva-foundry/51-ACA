# EVA-STORY: ACA-03-005
import pytest
from unittest.mock import patch, MagicMock

@patch('services.analysis.app.main.upsert_item')
def test_findings_summary_aggregation(mock_upsert):
    from services.analysis.app.main import AnalysisRun
    
    mock_findings = [
        {"category": "compute", "estimated_saving_low": 100, "estimated_saving_high": 200},
        {"category": "storage", "estimated_saving_low": 50, "estimated_saving_high": 150},
        {"category": "compute", "estimated_saving_low": 200, "estimated_saving_high": 300}
    ]

    analysis_run = AnalysisRun(run_id="test-run", subscription_id="test-sub")
    analysis_run.add_findings(mock_findings)
    analysis_run.persist()

    # Get the last call to upsert_item (which should be from persist(), not persist_status())
    last_call = mock_upsert.call_args_list[-1]
    args, kwargs = last_call
    doc = args[1]

    assert "findingsSummary" in doc
    assert doc["findingsSummary"]["findingCount"] == 3
    assert doc["findingsSummary"]["totalSavingLow"] == 350
    assert doc["findingsSummary"]["totalSavingHigh"] == 650
    assert set(doc["findingsSummary"]["categories"]) == {"compute", "storage"}
