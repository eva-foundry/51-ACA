# EVA-STORY: ACA-03-021
"""
Tests for ACA-03-021: FindingsAssembler receives cosmos_client kwarg.

Verifies that services/analysis/app/main.py passes cosmos_client=get_cosmos_client()
to FindingsAssembler. Source-inspection tests -- no Cosmos env vars required.
"""
from pathlib import Path


MAIN_SOURCE = Path("services/analysis/app/main.py").read_text(encoding="utf-8")


def test_analysis_main_passes_cosmos_client():
    """ACA-03-021: main.py must pass cosmos_client=get_cosmos_client() to FindingsAssembler."""
    assert "cosmos_client=get_cosmos_client()" in MAIN_SOURCE, (
        "services/analysis/app/main.py must pass cosmos_client=get_cosmos_client() "
        "to FindingsAssembler -- missing kwarg means C-04 regression"
    )


def test_analysis_main_imports_get_cosmos_client():
    """ACA-03-021: main.py must import get_cosmos_client from app.cosmos."""
    assert "from app.cosmos import get_cosmos_client" in MAIN_SOURCE, (
        "services/analysis/app/main.py must import get_cosmos_client from app.cosmos"
    )


def test_analysis_main_eva_story_tag_present():
    """ACA-03-021: main.py must carry the EVA-STORY tag for this story."""
    assert "EVA-STORY: ACA-03-021" in MAIN_SOURCE, (
        "services/analysis/app/main.py is missing # EVA-STORY: ACA-03-021 tag"
    )
