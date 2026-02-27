# EVA-STORY: ACA-07-021
"""
Tests for ACA-07-021: DeliverablePackager SAS URL uses account_key + 7-day expiry.

Source-inspection tests -- no Azure Storage env vars required.
Verifies that the C-07 fix (account_key SAS, SAS_HOURS=168) is present and tagged.
"""
from pathlib import Path

from services.delivery.app.packager import SAS_HOURS

PACKAGER_SOURCE = Path("services/delivery/app/packager.py").read_text(encoding="utf-8")


def test_sas_hours_is_168():
    """ACA-07-021: SAS_HOURS must equal 168 (7 days per spec)."""
    assert SAS_HOURS == 168, f"SAS_HOURS={SAS_HOURS} -- must be 168 (7 days)"


def test_sas_uses_account_key_not_credential():
    """ACA-07-021: generate_blob_sas must be called with account_key= parameter."""
    assert "account_key=self.account_key" in PACKAGER_SOURCE, (
        "services/delivery/app/packager.py must call generate_blob_sas with "
        "account_key=self.account_key -- managed identity cannot sign SAS tokens"
    )


def test_sas_expiry_uses_sas_hours():
    """ACA-07-021: SAS expiry must reference SAS_HOURS constant."""
    assert "timedelta(hours=SAS_HOURS)" in PACKAGER_SOURCE, (
        "services/delivery/app/packager.py must use timedelta(hours=SAS_HOURS) "
        "to set the SAS expiry -- hardcoded values are not acceptable"
    )


def test_packager_eva_story_tag_present():
    """ACA-07-021: packager.py must carry the EVA-STORY tag for this story."""
    assert "EVA-STORY: ACA-07-021" in PACKAGER_SOURCE, (
        "services/delivery/app/packager.py is missing # EVA-STORY: ACA-07-021 tag"
    )

