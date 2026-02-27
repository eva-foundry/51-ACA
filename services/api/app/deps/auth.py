# EVA-STORY: ACA-04-002
"""
JWT validation dependency for FastAPI authenticated routes.

Usage:
    from app.deps.auth import verify_token

    @router.get("/protected")
    async def handler(payload: dict = Depends(verify_token)):
        sub_id = payload.get("oid") or payload.get("sub")
        ...

Signature verification: deferred to Sprint-03 when JWKS URL is confirmed.
JWKS endpoint: https://login.microsoftonline.com/common/discovery/v2.0/keys
"""
from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token", auto_error=False)


async def verify_token(
    token: Optional[str] = Depends(oauth2_scheme),
) -> dict:
    """
    Validate a JWT bearer token. Returns the decoded payload dict.

    Raises HTTP 401 if:
    - Token is absent (None)
    - Token cannot be decoded (malformed)

    Sprint-03 note: add verify_signature=True + JWKS once Entra app is registered.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return payload
