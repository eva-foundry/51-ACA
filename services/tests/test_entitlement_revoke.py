# EVA-STORY: ACA-03-033
import pytest
from unittest.mock import MagicMock
from services.api.app.services.entitlement_service import EntitlementService

def test_revoke_tier3_preserved():
    mock_repo = MagicMock()
    mock_repo.get.return_value = MagicMock(tier=3, stripe_customer_id=None, stripe_subscription_id=None)
    service = EntitlementService()
    service._repo = mock_repo

    service.revoke("sub-123")

    args, kwargs = mock_repo.upsert.call_args
    assert kwargs["tier"] == 3

def test_revoke_tier2_downgraded():
    mock_repo = MagicMock()
    mock_repo.get.return_value = MagicMock(tier=2, stripe_customer_id=None, stripe_subscription_id=None)
    service = EntitlementService()
    service._repo = mock_repo

    service.revoke("sub-123")

    args, kwargs = mock_repo.upsert.call_args
    assert kwargs["tier"] == 1
