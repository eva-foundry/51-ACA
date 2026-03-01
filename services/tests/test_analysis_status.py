# EVA-STORY: ACA-03-004
import pytest
from unittest.mock import MagicMock
from app.db.cosmos import upsert_item
from app.main import AnalysisRun

def test_analysis_status_lifecycle():
    mock_upsert_item = MagicMock()
    upsert_item = mock_upsert_item

    run_id = "test-run-001"
    subscription_id = "sub-123"

    analysis_run = AnalysisRun(run_id, subscription_id)

    # Initial status should be "queued"
    assert analysis_run.status == "queued"
    mock_upsert_item.assert_called_with("analysis_runs", {
        "id": run_id,
        "subscriptionId": subscription_id,
        "status": "queued",
    }, partition_key=subscription_id)

    # Update status to "running"
    analysis_run.update_status("running")
    assert analysis_run.status == "running"
    mock_upsert_item.assert_called_with("analysis_runs", {
        "id": run_id,
        "subscriptionId": subscription_id,
        "status": "running",
    }, partition_key=subscription_id)

    # Update status to "succeeded"
    analysis_run.update_status("succeeded")
    assert analysis_run.status == "succeeded"
    mock_upsert_item.assert_called_with("analysis_runs", {
        "id": run_id,
        "subscriptionId": subscription_id,
        "status": "succeeded",
    }, partition_key=subscription_id)

    # Update status to "failed"
    analysis_run.update_status("failed")
    assert analysis_run.status == "failed"
    mock_upsert_item.assert_called_with("analysis_runs", {
        "id": run_id,
        "subscriptionId": subscription_id,
        "status": "failed",
    }, partition_key=subscription_id)

    print("[PASS] test_analysis_status_lifecycle")