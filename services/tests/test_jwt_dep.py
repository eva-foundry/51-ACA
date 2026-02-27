# EVA-STORY: ACA-04-002
import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from unittest.mock import patch
from services.api.app.deps.auth import verify_token

def test_valid_token_returns_payload():
    mock_payload = {"sub": "test", "oid": "oid-123"}

    with patch("services.api.app.deps.auth.JWTValidator.decode_token", return_value=mock_payload):
        result = verify_token(token="valid_token")
        assert result == mock_payload

def test_invalid_token_raises_401():
    with patch("services.api.app.deps.auth.JWTValidator.decode_token", side_effect=HTTPException(status_code=401, detail="Invalid or expired token")):
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token="invalid_token")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid or expired token"

def test_no_token_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        verify_token(token=None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "No token provided"
