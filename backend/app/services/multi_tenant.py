"""
Multi-Tenant Architecture
Support for multiple municipalities/organizations
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TenantType(str, Enum):
    MUNICIPAL = "municipal"
    STATE = "state"
    ENTERPRISE = "enterprise"
    NGO = "ngo"
    DEMO = "demo"


class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


@dataclass
class TenantConfig:
    """Tenant-specific configuration."""
    # Branding
    name: str
    display_name: str
    logo_url: Optional[str] = None
    primary_color: str = "#0ea5e9"
    secondary_color: str = "#7c3aed"
    
    # Features
    features: List[str] = field(default_factory=lambda: [
        "assessment", "marketplace", "verification", "monitoring"
    ])
    max_users: int = 100
    max_projects: int = 1000
    max_installers: int = 50
    
    # Customization
    currency: str = "INR"
    language: str = "en"
    timezone: str = "Asia/Kolkata"
    
    # API limits
    api_rate_limit: int = 1000  # requests per minute
    storage_limit_gb: int = 10


@dataclass
class Tenant:
    """Tenant entity."""
    id: str
    slug: str  # URL-friendly identifier
    type: TenantType
    status: TenantStatus
    config: TenantConfig
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    user_count: int = 0
    project_count: int = 0


class MultiTenantService:
    """
    Multi-tenant management for RainForge.
    
    Features:
    - Tenant isolation
    - Custom branding per tenant
    - Feature flags
    - Resource quotas
    - Billing integration
    """
    
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}
        self._slug_index: Dict[str, str] = {}  # slug -> tenant_id
        self._user_tenant_map: Dict[str, str] = {}  # user_id -> tenant_id
        
        # Create default tenant
        self._create_default_tenant()
    
    def _create_default_tenant(self):
        """Create default system tenant."""
        default = Tenant(
            id="default",
            slug="rainforge",
            type=TenantType.STATE,
            status=TenantStatus.ACTIVE,
            config=TenantConfig(
                name="RainForge",
                display_name="RainForge India",
                features=["assessment", "marketplace", "verification", "monitoring", "analytics", "iot", "chatbot"],
                max_users=10000,
                max_projects=100000
            ),
            created_at=datetime.utcnow()
        )
        self._tenants["default"] = default
        self._slug_index["rainforge"] = "default"
    
    async def create_tenant(
        self,
        name: str,
        slug: str,
        tenant_type: TenantType,
        config: Optional[Dict] = None,
        admin_email: Optional[str] = None
    ) -> Tenant:
        """Create a new tenant."""
        # Validate slug
        if slug in self._slug_index:
            raise ValueError(f"Slug '{slug}' already exists")
        
        tenant_id = str(uuid.uuid4())
        
        # Merge config
        tenant_config = TenantConfig(name=name, display_name=name)
        if config:
            for key, value in config.items():
                if hasattr(tenant_config, key):
                    setattr(tenant_config, key, value)
        
        tenant = Tenant(
            id=tenant_id,
            slug=slug,
            type=tenant_type,
            status=TenantStatus.TRIAL,
            config=tenant_config,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30) if tenant_type != TenantType.DEMO else None,
            metadata={"admin_email": admin_email}
        )
        
        self._tenants[tenant_id] = tenant
        self._slug_index[slug] = tenant_id
        
        logger.info(f"Created tenant: {name} ({slug})")
        
        return tenant
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self._tenants.get(tenant_id)
    
    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        tenant_id = self._slug_index.get(slug)
        if tenant_id:
            return self._tenants.get(tenant_id)
        return None
    
    async def get_user_tenant(self, user_id: str) -> Optional[Tenant]:
        """Get tenant for a user."""
        tenant_id = self._user_tenant_map.get(user_id, "default")
        return self._tenants.get(tenant_id)
    
    async def assign_user_to_tenant(
        self,
        user_id: str,
        tenant_id: str
    ) -> bool:
        """Assign a user to a tenant."""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        
        # Check user limit
        if tenant.user_count >= tenant.config.max_users:
            raise ValueError("Tenant user limit reached")
        
        self._user_tenant_map[user_id] = tenant_id
        tenant.user_count += 1
        
        return True
    
    async def update_tenant_config(
        self,
        tenant_id: str,
        updates: Dict[str, Any]
    ) -> Tenant:
        """Update tenant configuration."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            raise ValueError("Tenant not found")
        
        for key, value in updates.items():
            if hasattr(tenant.config, key):
                setattr(tenant.config, key, value)
        
        return tenant
    
    async def check_feature_enabled(
        self,
        tenant_id: str,
        feature: str
    ) -> bool:
        """Check if feature is enabled for tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        
        return feature in tenant.config.features
    
    async def check_quota(
        self,
        tenant_id: str,
        resource: str
    ) -> Dict[str, Any]:
        """Check resource quota for tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return {"allowed": False, "reason": "Tenant not found"}
        
        if tenant.status != TenantStatus.ACTIVE:
            return {"allowed": False, "reason": f"Tenant is {tenant.status.value}"}
        
        if resource == "users":
            remaining = tenant.config.max_users - tenant.user_count
            return {
                "allowed": remaining > 0,
                "used": tenant.user_count,
                "limit": tenant.config.max_users,
                "remaining": remaining
            }
        
        elif resource == "projects":
            remaining = tenant.config.max_projects - tenant.project_count
            return {
                "allowed": remaining > 0,
                "used": tenant.project_count,
                "limit": tenant.config.max_projects,
                "remaining": remaining
            }
        
        return {"allowed": True}
    
    async def get_tenant_branding(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get branding configuration for tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            tenant = self._tenants.get("default")
        
        return {
            "name": tenant.config.display_name,
            "logo_url": tenant.config.logo_url,
            "primary_color": tenant.config.primary_color,
            "secondary_color": tenant.config.secondary_color,
            "currency": tenant.config.currency,
            "language": tenant.config.language
        }
    
    async def list_tenants(
        self,
        tenant_type: Optional[TenantType] = None,
        status: Optional[TenantStatus] = None
    ) -> List[Dict]:
        """List all tenants."""
        tenants = list(self._tenants.values())
        
        if tenant_type:
            tenants = [t for t in tenants if t.type == tenant_type]
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        
        return [
            {
                "id": t.id,
                "slug": t.slug,
                "name": t.config.display_name,
                "type": t.type.value,
                "status": t.status.value,
                "user_count": t.user_count,
                "project_count": t.project_count,
                "created_at": t.created_at.isoformat()
            }
            for t in tenants
        ]
    
    async def suspend_tenant(self, tenant_id: str, reason: str) -> bool:
        """Suspend a tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.SUSPENDED
        tenant.metadata["suspension_reason"] = reason
        tenant.metadata["suspended_at"] = datetime.utcnow().isoformat()
        
        logger.warning(f"Tenant {tenant.slug} suspended: {reason}")
        
        return True
    
    async def activate_tenant(self, tenant_id: str) -> bool:
        """Activate a tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.ACTIVE
        tenant.metadata.pop("suspension_reason", None)
        
        return True


# Need timedelta
from datetime import timedelta

# Singleton
_tenant_service: Optional[MultiTenantService] = None

def get_tenant_service() -> MultiTenantService:
    global _tenant_service
    if _tenant_service is None:
        _tenant_service = MultiTenantService()
    return _tenant_service


# ==================== TENANT CONTEXT MIDDLEWARE ====================

class TenantContext:
    """Thread-local tenant context."""
    
    _current_tenant: Optional[str] = None
    
    @classmethod
    def set(cls, tenant_id: str):
        cls._current_tenant = tenant_id
    
    @classmethod
    def get(cls) -> Optional[str]:
        return cls._current_tenant
    
    @classmethod
    def clear(cls):
        cls._current_tenant = None
