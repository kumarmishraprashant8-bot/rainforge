"""
SSO/OAuth Integration
Support for government and enterprise SSO
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import base64
import hashlib
import secrets
import urllib.parse

logger = logging.getLogger(__name__)

# Try importing JWT library
try:
    from jose import jwt, JWTError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


class OAuthProvider:
    """OAuth provider configurations."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    DIGILOCKER = "digilocker"  # Indian Govt
    PARICHAY = "parichay"  # NIC SSO
    GITHUB = "github"


@dataclass
class OAuthConfig:
    """OAuth provider configuration."""
    provider: str
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scopes: list
    redirect_uri: str


@dataclass
class OAuthUser:
    """User info from OAuth provider."""
    provider: str
    provider_id: str
    email: str
    name: str
    picture_url: Optional[str] = None
    raw_data: Dict[str, Any] = None


class SSOService:
    """
    SSO/OAuth authentication service.
    
    Supports:
    - Google OAuth
    - Microsoft Azure AD
    - DigiLocker (Indian Govt)
    - Parichay (NIC SSO)
    - Custom SAML
    """
    
    # Provider configurations
    PROVIDERS = {
        OAuthProvider.GOOGLE: {
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
            "scopes": ["openid", "email", "profile"]
        },
        OAuthProvider.MICROSOFT: {
            "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "userinfo_url": "https://graph.microsoft.com/v1.0/me",
            "scopes": ["openid", "email", "profile", "User.Read"]
        },
        OAuthProvider.DIGILOCKER: {
            "authorize_url": "https://api.digitallocker.gov.in/public/oauth2/1/authorize",
            "token_url": "https://api.digitallocker.gov.in/public/oauth2/1/token",
            "userinfo_url": "https://api.digitallocker.gov.in/public/oauth2/1/userinfo",
            "scopes": ["openid", "email", "profile", "address"]
        },
        OAuthProvider.PARICHAY: {
            "authorize_url": "https://parichay.nic.in/oauth2/authorize",
            "token_url": "https://parichay.nic.in/oauth2/token",
            "userinfo_url": "https://parichay.nic.in/oauth2/userinfo",
            "scopes": ["openid", "profile"]
        },
        OAuthProvider.GITHUB: {
            "authorize_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scopes": ["read:user", "user:email"]
        }
    }
    
    def __init__(self):
        from app.core.config import settings
        
        self._configs: Dict[str, OAuthConfig] = {}
        self._states: Dict[str, Dict] = {}  # CSRF state tracking
        self._nonces: Dict[str, str] = {}  # OIDC nonce tracking
        
        # Load provider configs from settings
        self._load_provider_configs(settings)
    
    def _load_provider_configs(self, settings):
        """Load OAuth configurations from settings."""
        providers = {
            OAuthProvider.GOOGLE: ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
            OAuthProvider.MICROSOFT: ("AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"),
            OAuthProvider.GITHUB: ("GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"),
        }
        
        base_url = getattr(settings, 'APP_BASE_URL', 'http://localhost:5173')
        
        for provider, (id_key, secret_key) in providers.items():
            client_id = getattr(settings, id_key, None)
            client_secret = getattr(settings, secret_key, None)
            
            if client_id and client_secret:
                provider_info = self.PROVIDERS[provider]
                self._configs[provider] = OAuthConfig(
                    provider=provider,
                    client_id=client_id,
                    client_secret=client_secret,
                    authorize_url=provider_info["authorize_url"],
                    token_url=provider_info["token_url"],
                    userinfo_url=provider_info["userinfo_url"],
                    scopes=provider_info["scopes"],
                    redirect_uri=f"{base_url}/auth/callback/{provider}"
                )
    
    def get_available_providers(self) -> list:
        """Get list of configured providers."""
        return list(self._configs.keys())
    
    def get_authorization_url(
        self,
        provider: str,
        redirect_uri: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate OAuth authorization URL."""
        if provider not in self._configs:
            raise ValueError(f"Provider '{provider}' not configured")
        
        config = self._configs[provider]
        
        # Generate CSRF state
        state = secrets.token_urlsafe(32)
        self._states[state] = {
            "provider": provider,
            "created_at": datetime.utcnow(),
            "redirect_uri": redirect_uri
        }
        
        # Generate OIDC nonce
        nonce = secrets.token_urlsafe(16)
        self._nonces[state] = nonce
        
        # Build URL params
        params = {
            "client_id": config.client_id,
            "redirect_uri": redirect_uri or config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(config.scopes),
            "state": state,
            "nonce": nonce
        }
        
        # Provider-specific params
        if provider == OAuthProvider.GOOGLE:
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        elif provider == OAuthProvider.MICROSOFT:
            params["response_mode"] = "query"
        
        auth_url = f"{config.authorize_url}?{urllib.parse.urlencode(params)}"
        
        return {
            "url": auth_url,
            "state": state,
            "provider": provider
        }
    
    async def handle_callback(
        self,
        provider: str,
        code: str,
        state: str
    ) -> OAuthUser:
        """Handle OAuth callback and get user info."""
        import httpx
        
        # Validate state
        if state not in self._states:
            raise ValueError("Invalid state parameter")
        
        state_data = self._states.pop(state)
        if state_data["provider"] != provider:
            raise ValueError("Provider mismatch")
        
        # Check state expiry (10 minutes)
        if datetime.utcnow() - state_data["created_at"] > timedelta(minutes=10):
            raise ValueError("State expired")
        
        config = self._configs[provider]
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                config.token_url,
                data={
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "code": code,
                    "redirect_uri": config.redirect_uri,
                    "grant_type": "authorization_code"
                },
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                raise ValueError(f"Token exchange failed: {token_response.text}")
            
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            # Get user info
            userinfo_response = await client.get(
                config.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if userinfo_response.status_code != 200:
                raise ValueError("Failed to get user info")
            
            userinfo = userinfo_response.json()
        
        # Parse user info based on provider
        return self._parse_user_info(provider, userinfo)
    
    def _parse_user_info(self, provider: str, data: Dict) -> OAuthUser:
        """Parse user info from provider response."""
        if provider == OAuthProvider.GOOGLE:
            return OAuthUser(
                provider=provider,
                provider_id=data.get("sub"),
                email=data.get("email"),
                name=data.get("name"),
                picture_url=data.get("picture"),
                raw_data=data
            )
        
        elif provider == OAuthProvider.MICROSOFT:
            return OAuthUser(
                provider=provider,
                provider_id=data.get("id"),
                email=data.get("mail") or data.get("userPrincipalName"),
                name=data.get("displayName"),
                picture_url=None,
                raw_data=data
            )
        
        elif provider == OAuthProvider.GITHUB:
            return OAuthUser(
                provider=provider,
                provider_id=str(data.get("id")),
                email=data.get("email"),
                name=data.get("name") or data.get("login"),
                picture_url=data.get("avatar_url"),
                raw_data=data
            )
        
        elif provider == OAuthProvider.DIGILOCKER:
            return OAuthUser(
                provider=provider,
                provider_id=data.get("sub"),
                email=data.get("email"),
                name=data.get("given_name", "") + " " + data.get("family_name", ""),
                picture_url=data.get("picture"),
                raw_data=data
            )
        
        else:
            return OAuthUser(
                provider=provider,
                provider_id=data.get("sub") or data.get("id"),
                email=data.get("email"),
                name=data.get("name"),
                raw_data=data
            )
    
    async def link_account(
        self,
        user_id: str,
        oauth_user: OAuthUser
    ) -> bool:
        """Link OAuth account to existing user."""
        # In production, would save to database
        logger.info(f"Linked {oauth_user.provider} account to user {user_id}")
        return True
    
    def generate_pkce(self) -> Dict[str, str]:
        """Generate PKCE code verifier and challenge."""
        code_verifier = secrets.token_urlsafe(64)[:128]
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        
        return {
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }


# Singleton
_sso_service: Optional[SSOService] = None

def get_sso_service() -> SSOService:
    global _sso_service
    if _sso_service is None:
        _sso_service = SSOService()
    return _sso_service
