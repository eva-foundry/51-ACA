"""MSAL client factory for multi-tenant Azure authentication"""
import os
from msal import PublicClientApplication

def create_msal_app():
    """
    Creates MSAL PublicClientApplication with authority=common
    Enables any Microsoft tenant sign-in (personal + work accounts)
    """
    client_id = os.getenv("ACA_CLIENT_ID")
    authority = "https://login.microsoftonline.com/common"
    
    app = PublicClientApplication(
        client_id=client_id,
        authority=authority,
    )
    return app

def get_authorization_request_url(msal_app, scopes):
    """Generate authorization URL for delegated flow"""
    auth_url = msal_app.get_authorization_request_url(
        scopes=scopes,
        redirect_uri=os.getenv("REDIRECT_URI", "http://localhost:3000/auth-callback"),
    )
    return auth_url

def get_tokens_by_auth_code(msal_app, code, scopes):
    """Exchange authorization code for access + refresh tokens"""
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=scopes,
        redirect_uri=os.getenv("REDIRECT_URI", "http://localhost:3000/auth-callback"),
    )
    return result

def get_tokens_by_refresh_token(msal_app, refresh_token, scopes):
    """Acquire new access token using refresh token"""
    result = msal_app.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
    return result

def get_resource_token(msal_app, refresh_token, resource_scope):
    """Get token for specific Azure resource (e.g., management.azure.com)"""
    result = msal_app.acquire_token_by_refresh_token(
        refresh_token,
        scopes=[resource_scope],
    )
    return result.get("access_token") if result and "access_token" in result else None
