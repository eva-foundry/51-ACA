# EVA-STORY: ACA-03-021
"""
Tests for ACA-03-021: Analysis main.py Cosmos integration.

Verifies that services/analysis/app/main.py correctly integrates with Cosmos DB.
Post-Sprint-4: validates upsert_item() usage pattern.
Source-inspection tests -- no Cosmos env vars required.
"""
from pathlib import Path


MAIN_SOURCE = Path("services/analysis/app/main.py").read_text(encoding="utf-8")


def test_analysis_main_passes_cosmos_client():
    """ACA-03-021: main.py must use upsert_item from app.db.cosmos for persistence."""
    assert "from app.db.cosmos import upsert_item" in MAIN_SOURCE, (
        "services/analysis/app/main.py must import upsert_item from app.db.cosmos "
        "for Cosmos persistence (Sprint 4+ pattern)"
    )
    assert "upsert_item(" in MAIN_SOURCE, (
        "services/analysis/app/main.py must call upsert_item() to persist data"
    )


def test_analysis_main_imports_get_cosmos_client():
    """ACA-03-021: main.py must import Cosmos integration (upsert_item post-Sprint-4)."""
    assert "from app.db.cosmos import upsert_item" in MAIN_SOURCE, (
        "services/analysis/app/main.py must import upsert_item from app.db.cosmos"
    )


def test_analysis_main_eva_story_tag_present():
    """ACA-03-021: main.py must carry the EVA-STORY tag for Sprint 4 stories."""
    assert "EVA-STORY: ACA-03-021" in MAIN_SOURCE, (
        "services/analysis/app/main.py is missing # EVA-STORY: ACA-03-021 tag"
    )
