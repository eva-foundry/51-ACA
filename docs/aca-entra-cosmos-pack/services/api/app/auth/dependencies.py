from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from app.auth.rbac import Actor
from app.auth.entra_jwt import validate_token, map_claims_to_roles

def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "MISSING_AUTH", "message": "Missing Authorization header"}})
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "INVALID_AUTH", "message": "Expected Bearer token"}})
    return parts[1].strip()

def get_actor(authorization: str | None = Header(default=None, alias="Authorization")) -> Actor:
    token = _extract_bearer_token(authorization)
    payload = validate_token(token)
    roles = map_claims_to_roles(payload)

    actor_id = payload.get("oid") or payload.get("sub")
    if not actor_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "INVALID_TOKEN", "message": "Missing actor id claim"}})

    return Actor(
        actor_id=actor_id,
        roles=roles,
        display_name=payload.get("name") or payload.get("preferred_username"),
        tenant_id=payload.get("tid"),
    )
