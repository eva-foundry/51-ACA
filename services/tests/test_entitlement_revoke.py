# EVA-STORY: ACA-03-033
import pytest
from unittest.mock import MagicMock
from services.api.app.services.entitlement_service import EntitlementService

def test_revoke_tier3_preserved():
    mock_repo = MagicMock()
    # EntitlementService.get calls doc.get("tier", 1) -- must be a dict
    mock_repo.get.return_value = {
        "tier": 3, "paymentStatus": "active",
        "stripeCustomerId": None, "stripeSubscriptionId": None,
    }
    service = EntitlementService(repo=mock_repo)

    service.revoke("sub-123")

    _, kwargs = mock_repo.upsert.call_args
    assert kwargs["tier"] == 3
    assert kwargs["payment_status"] == "canceled"


def test_revoke_tier2_downgraded():
    mock_repo = MagicMock()
    mock_repo.get.return_value = {
        "tier": 2, "paymentStatus": "active",
        "stripeCustomerId": None, "stripeSubscriptionId": None,
    }
    service = EntitlementService(repo=mock_repo)

    service.revoke("sub-123")

    _, kwargs = mock_repo.upsert.call_args
    assert kwargs["tier"] == 1
    assert kwargs["payment_status"] == "canceled"
