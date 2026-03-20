# ACA Entra JWT + Cosmos Wiring Pack

This add-on pack upgrades the admin scaffold with:

- Entra JWT validation helper using JWKS discovery
- FastAPI auth dependency that extracts `oid/sub`, `name`, and `roles/groups`
- Cosmos client helper
- Real Cosmos query implementations for:
  - admin audit events
  - customer search/detail
  - run listing
- Example settings additions

## Notes
- Replace `ENTRA_ALLOWED_ISSUERS`, `ENTRA_AUDIENCE`, and optionally `ENTRA_ADMIN_GROUP_IDS`
  with your tenant/app values.
- This implementation uses `PyJWT` and `requests`.
- Cosmos queries are written against the existing ACA container names you already defined.

## Install
```bash
pip install pyjwt cryptography requests azure-cosmos pydantic-settings
```

## Wire-in
- Replace your current `app/auth/dependencies.py` with the version in this pack
- Add `app/auth/entra_jwt.py`
- Replace the repo/service files as needed
