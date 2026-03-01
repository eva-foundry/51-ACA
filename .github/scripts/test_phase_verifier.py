# EVA-STORY: ACA-14-003
import pytest
from .phase_verifier import verify_d1_evidence, verify_d2_repo_audit, verify_p_plan_update, verify_d3_story_selection, verify_a_manifest_creation

def test_verify_d1_evidence(tmp_path):
    sprint_id = "SPRINT-10"
    evidence_dir = tmp_path / f".eva/evidence/{sprint_id}"
    evidence_dir.mkdir(parents=True)

    for i in range(6):
        (evidence_dir / f"ACA-{i}-receipt.json").write_text("{}")

    assert verify_d1_evidence(sprint_id, 6) is True

def test_verify_d2_repo_audit():
    ctx = {"pytest_output": {"test_count": 5}}
    assert verify_d2_repo_audit(ctx) is True

def test_verify_p_plan_update(tmp_path):
    sprint_id = "SPRINT-10"
    plan_file = tmp_path / f"docs/PLAN-{sprint_id}.md"
    plan_file.write_text("[x] Task 1\n[x] Task 2\n[x] Task 3\n[x] Task 4")

    ctx = {}
    assert verify_p_plan_update(ctx, sprint_id, 4) is True

def test_verify_d3_story_selection(tmp_path):
    sprint_id = "SPRINT-11"
    manifest_file = tmp_path / f"docs/{sprint_id}-MANIFEST.md"
    manifest_file.write_text("Sprint 11 manifest content")

    ctx = {}
    assert verify_d3_story_selection(ctx, sprint_id) is True

def test_verify_a_manifest_creation(tmp_path):
    sprint_id = "SPRINT-11"
    manifest_file = tmp_path / f"docs/{sprint_id}-MANIFEST.md"
    manifest_file.write_text("Sprint 11 manifest content")

    ctx = {}
    assert verify_a_manifest_creation(ctx, sprint_id) is True
