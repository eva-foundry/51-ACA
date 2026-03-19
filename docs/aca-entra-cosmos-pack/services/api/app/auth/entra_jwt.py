from __future__ import annotations

import time
from typing import Any, Dict, List, Set

import jwt
import requests
from fastapi import HTTPException, status

from app.settings import settings
from app.auth.rbac import ROLE_ADMIN, ROLE_FINOPS, ROLE_SUPPORT

_JWKS_CACHE: Dict[str, Any] = {"expires_at": 0, "keys": {}}
_JWKS_TTL_SECONDS = 3600


def _discovery_url() -> str:
    tenant = settings.ENTRA_TENANT_ID or "common"
    return f"https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration"


def _load_jwks() -> Dict[str, Any]:
    now = int(time.time())
    if _JWKS_CACHE["keys"] and now < _JWKS_CACHE["expires_at"]:
        return _JWKS_CACHE["keys"]

    disco = requests.get(_discovery_url(), timeout=10)
    disco.raise_for_status()
    jwks_uri = disco.json()["jwks_uri"]

    jwks_resp = requests.get(jwks_uri, timeout=10)
    jwks_resp.raise_for_status()
    jwks = jwks_resp.json()

    keys = {k["kid"]: k for k in jwks.get("keys", [])}
    _JWKS_CACHE["keys"] = keys
    _JWKS_CACHE["expires_at"] = now + _JWKS_TTL_SECONDS
    return keys


def _allowed_issuers() -> List[str]:
    if settings.ENTRA_ALLOWED_ISSUERS:
        return settings.ENTRA_ALLOWED_ISSUERS
    if settings.ENTRA_TENANT_ID:
        tid = settings.ENTRA_TENANT_ID
        return [
            f"https://login.microsoftonline.com/{tid}/v2.0",
            f"https://sts.windows.net/{tid}/",
        ]
    return []


def validate_token(token: str) -> Dict[str, Any]:
    try:
        unverified = jwt.get_unverified_header(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "INVALID_TOKEN", "message": "Malformed token"}}) from e

    kid = unverified.get("kid")
    if not kid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "INVALID_TOKEN", "message": "Missing kid"}})

    jwks = _load_jwks()
    jwk = jwks.get(kid)
    if not jwk:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "INVALID_TOKEN", "message": "Unknown signing key"}})

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

    try:
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=settings.ENTRA_AUDIENCE,
            issuer=_allowed_issuers() or None,
            options={"require": ["exp", "iat"]},
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "TOKEN_EXPIRED", "message": "Expired token"}}) from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "INVALID_TOKEN", "message": "Token validation failed"}}) from e


def map_claims_to_roles(payload: Dict[str, Any]) -> Set[str]:
    roles: Set[str] = set()

    raw_roles = payload.get("roles") or []
    raw_groups = payload.get("groups") or []

    # direct app role names
    if ROLE_ADMIN in raw_roles:
        roles.add(ROLE_ADMIN)
    if ROLE_SUPPORT in raw_roles:
        roles.add(ROLE_SUPPORT)
    if ROLE_FINOPS in raw_roles:
        roles.add(ROLE_FINOPS)

    # group-id based mappings
    if set(raw_groups).intersection(set(settings.ENTRA_ADMIN_GROUP_IDS)):
        roles.add(ROLE_ADMIN)
    if set(raw_groups).intersection(set(settings.ENTRA_SUPPORT_GROUP_IDS)):
        roles.add(ROLE_SUPPORT)
    if set(raw_groups).intersection(set(settings.ENTRA_FINOPS_GROUP_IDS)):
        roles.add(ROLE_FINOPS)

    return roles
