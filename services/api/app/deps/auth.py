# EVA-STORY: ACA-04-002
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError, PyJWTError
import requests

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/token', auto_error=False)

class JWTValidator:
    def __init__(self, jwks_url: str = "https://login.microsoftonline.com/common/discovery/v2.0/keys"):
        self.jwks_url = jwks_url

    def fetch_jwks(self) -> dict:
        response = requests.get(self.jwks_url)
        response.raise_for_status()
        return response.json()

    def decode_token(self, token: str, jwks: dict) -> dict:
        try:
            return jwt.decode(
                token,
                options={"verify_signature": True},
                key=jwks,
                algorithms=["RS256"],
            )
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

async def verify_token(token: str = Depends(oauth2_scheme), jwks_url: str = None) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    validator = JWTValidator(jwks_url=jwks_url or "https://login.microsoftonline.com/common/discovery/v2.0/keys")
    jwks = validator.fetch_jwks()

    try:
        decoded_payload = validator.decode_token(token, jwks)
        return decoded_payload
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
