# EVA-STORY: ACA-03-033
import pytest
import inspect
from services.delivery.app.packager import SAS_HOURS, Packager

def test_sas_hours_constant():
    assert SAS_HOURS == 168

def test_generate_sas_url_method():
    source = inspect.getsource(Packager.generate_sas_url)
    assert "account_key" not in source
    assert "user_delegation_key" in source
