"""
Role Hierarchy & RBAC Service
Fine-grained access control
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """System permissions."""
    # Assessment
    ASSESSMENT_CREATE = "assessment:create"
    ASSESSMENT_READ = "assessment:read"
    ASSESSMENT_UPDATE = "assessment:update"
    ASSESSMENT_DELETE = "assessment:delete"
    
    # Projects
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_ASSIGN = "project:assign"
    
    # Verification
    VERIFICATION_SUBMIT = "verification:submit"
    VERIFICATION_REVIEW = "verification:review"
    VERIFICATION_APPROVE = "verification:approve"
    VERIFICATION_REJECT = "verification:reject"
    
    # Payments
    PAYMENT_VIEW = "payment:view"
    PAYMENT_RELEASE = "payment:release"
    PAYMENT_REFUND = "payment:refund"
    ESCROW_MANAGE = "escrow:manage"
    
    # Marketplace
    BID_CREATE = "bid:create"
    BID_VIEW = "bid:view"
    BID_AWARD = "bid:award"
    INSTALLER_VERIFY = "installer:verify"
    
    # Monitoring
    SENSOR_VIEW = "sensor:view"
    SENSOR_MANAGE = "sensor:manage"
    ALERT_CONFIGURE = "alert:configure"
    
    # Users
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    ROLE_ASSIGN = "role:assign"
    
    # Admin
    SYSTEM_CONFIG = "system:config"
    AUDIT_VIEW = "audit:view"
    REPORTS_VIEW = "reports:view"
    REPORTS_EXPORT = "reports:export"
    BULK_OPERATIONS = "bulk:operations"
    
    # Tenant
    TENANT_MANAGE = "tenant:manage"


class RoleLevel(int, Enum):
    """Role hierarchy levels."""
    SUPER_ADMIN = 100
    STATE_ADMIN = 90
    DISTRICT_ADMIN = 80
    WARD_ADMIN = 70
    VERIFIER = 60
    INSTALLER = 50
    USER = 10
    GUEST = 0


@dataclass
class Role:
    """Role definition."""
    id: str
    name: str
    display_name: str
    level: RoleLevel
    permissions: Set[Permission]
    inherits_from: Optional[str] = None  # Parent role ID
    description: str = ""


@dataclass
class UserRole:
    """User-role assignment."""
    user_id: str
    role_id: str
    scope: Optional[str] = None  # e.g., "district:pune" or "ward:123"
    granted_by: Optional[str] = None
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class RBACService:
    """
    Role-Based Access Control with hierarchy.
    
    Features:
    - Hierarchical roles
    - Permission inheritance
    - Scoped permissions (per district/ward)
    - Dynamic role assignment
    """
    
    def __init__(self):
        self._roles: Dict[str, Role] = {}
        self._user_roles: Dict[str, List[UserRole]] = {}
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default system roles."""
        # Super Admin - Full access
        self._roles["super_admin"] = Role(
            id="super_admin",
            name="super_admin",
            display_name="Super Administrator",
            level=RoleLevel.SUPER_ADMIN,
            permissions=set(Permission),  # All permissions
            description="Full system access"
        )
        
        # State Admin
        self._roles["state_admin"] = Role(
            id="state_admin",
            name="state_admin",
            display_name="State Administrator",
            level=RoleLevel.STATE_ADMIN,
            permissions={
                Permission.ASSESSMENT_READ, Permission.ASSESSMENT_UPDATE,
                Permission.PROJECT_READ, Permission.PROJECT_UPDATE, Permission.PROJECT_ASSIGN,
                Permission.VERIFICATION_REVIEW, Permission.VERIFICATION_APPROVE, Permission.VERIFICATION_REJECT,
                Permission.PAYMENT_VIEW, Permission.PAYMENT_RELEASE,
                Permission.BID_VIEW, Permission.BID_AWARD, Permission.INSTALLER_VERIFY,
                Permission.SENSOR_VIEW, Permission.ALERT_CONFIGURE,
                Permission.USER_READ, Permission.USER_UPDATE, Permission.ROLE_ASSIGN,
                Permission.AUDIT_VIEW, Permission.REPORTS_VIEW, Permission.REPORTS_EXPORT,
                Permission.BULK_OPERATIONS
            },
            inherits_from="district_admin",
            description="State-level administration"
        )
        
        # District Admin
        self._roles["district_admin"] = Role(
            id="district_admin",
            name="district_admin",
            display_name="District Administrator",
            level=RoleLevel.DISTRICT_ADMIN,
            permissions={
                Permission.ASSESSMENT_READ, Permission.ASSESSMENT_UPDATE,
                Permission.PROJECT_READ, Permission.PROJECT_UPDATE, Permission.PROJECT_ASSIGN,
                Permission.VERIFICATION_REVIEW, Permission.VERIFICATION_APPROVE, Permission.VERIFICATION_REJECT,
                Permission.PAYMENT_VIEW,
                Permission.BID_VIEW, Permission.BID_AWARD,
                Permission.SENSOR_VIEW,
                Permission.USER_READ,
                Permission.REPORTS_VIEW
            },
            inherits_from="ward_admin",
            description="District-level administration"
        )
        
        # Ward Admin
        self._roles["ward_admin"] = Role(
            id="ward_admin",
            name="ward_admin",
            display_name="Ward Administrator",
            level=RoleLevel.WARD_ADMIN,
            permissions={
                Permission.ASSESSMENT_READ,
                Permission.PROJECT_READ, Permission.PROJECT_UPDATE,
                Permission.VERIFICATION_REVIEW,
                Permission.BID_VIEW,
                Permission.SENSOR_VIEW,
                Permission.USER_READ
            },
            description="Ward-level administration"
        )
        
        # Verifier
        self._roles["verifier"] = Role(
            id="verifier",
            name="verifier",
            display_name="Field Verifier",
            level=RoleLevel.VERIFIER,
            permissions={
                Permission.ASSESSMENT_READ,
                Permission.PROJECT_READ,
                Permission.VERIFICATION_SUBMIT, Permission.VERIFICATION_REVIEW,
                Permission.SENSOR_VIEW
            },
            description="Field verification staff"
        )
        
        # Installer
        self._roles["installer"] = Role(
            id="installer",
            name="installer",
            display_name="Registered Installer",
            level=RoleLevel.INSTALLER,
            permissions={
                Permission.ASSESSMENT_CREATE, Permission.ASSESSMENT_READ,
                Permission.PROJECT_READ, Permission.PROJECT_UPDATE,
                Permission.VERIFICATION_SUBMIT,
                Permission.BID_CREATE, Permission.BID_VIEW,
                Permission.SENSOR_VIEW
            },
            description="Verified RWH installer"
        )
        
        # User
        self._roles["user"] = Role(
            id="user",
            name="user",
            display_name="Citizen User",
            level=RoleLevel.USER,
            permissions={
                Permission.ASSESSMENT_CREATE, Permission.ASSESSMENT_READ,
                Permission.PROJECT_CREATE, Permission.PROJECT_READ,
                Permission.VERIFICATION_SUBMIT,
                Permission.BID_VIEW,
                Permission.PAYMENT_VIEW,
                Permission.SENSOR_VIEW
            },
            description="Regular citizen user"
        )
        
        # Guest
        self._roles["guest"] = Role(
            id="guest",
            name="guest",
            display_name="Guest",
            level=RoleLevel.GUEST,
            permissions={
                Permission.ASSESSMENT_CREATE,
                Permission.REPORTS_VIEW
            },
            description="Unauthenticated guest"
        )
    
    async def assign_role(
        self,
        user_id: str,
        role_id: str,
        scope: Optional[str] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """Assign a role to a user."""
        if role_id not in self._roles:
            raise ValueError(f"Role '{role_id}' not found")
        
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            scope=scope,
            granted_by=granted_by,
            expires_at=expires_at
        )
        
        if user_id not in self._user_roles:
            self._user_roles[user_id] = []
        
        self._user_roles[user_id].append(user_role)
        
        logger.info(f"Assigned role {role_id} to user {user_id} (scope: {scope})")
        
        return user_role
    
    async def revoke_role(
        self,
        user_id: str,
        role_id: str,
        scope: Optional[str] = None
    ) -> bool:
        """Revoke a role from a user."""
        if user_id not in self._user_roles:
            return False
        
        initial_count = len(self._user_roles[user_id])
        self._user_roles[user_id] = [
            ur for ur in self._user_roles[user_id]
            if not (ur.role_id == role_id and ur.scope == scope)
        ]
        
        return len(self._user_roles[user_id]) < initial_count
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user."""
        user_roles = self._user_roles.get(user_id, [])
        
        # Filter expired roles
        now = datetime.utcnow()
        active_roles = [
            ur for ur in user_roles
            if not ur.expires_at or ur.expires_at > now
        ]
        
        return [self._roles[ur.role_id] for ur in active_roles if ur.role_id in self._roles]
    
    async def get_user_permissions(
        self,
        user_id: str,
        scope: Optional[str] = None
    ) -> Set[Permission]:
        """Get all permissions for a user, optionally within a scope."""
        roles = await self.get_user_roles(user_id)
        
        permissions = set()
        for role in roles:
            # Check scope if applicable
            user_role = next(
                (ur for ur in self._user_roles.get(user_id, []) if ur.role_id == role.id),
                None
            )
            
            if scope and user_role and user_role.scope:
                # Check if user's scope includes the requested scope
                if not self._scope_matches(user_role.scope, scope):
                    continue
            
            permissions.update(role.permissions)
            
            # Add inherited permissions
            inherited = self._get_inherited_permissions(role)
            permissions.update(inherited)
        
        return permissions
    
    async def check_permission(
        self,
        user_id: str,
        permission: Permission,
        scope: Optional[str] = None
    ) -> bool:
        """Check if user has a specific permission."""
        permissions = await self.get_user_permissions(user_id, scope)
        return permission in permissions
    
    async def get_highest_role(self, user_id: str) -> Optional[Role]:
        """Get user's highest level role."""
        roles = await self.get_user_roles(user_id)
        if not roles:
            return None
        
        return max(roles, key=lambda r: r.level.value)
    
    async def can_assign_role(
        self,
        assigner_user_id: str,
        target_role_id: str
    ) -> bool:
        """Check if user can assign a specific role."""
        assigner_role = await self.get_highest_role(assigner_user_id)
        if not assigner_role:
            return False
        
        target_role = self._roles.get(target_role_id)
        if not target_role:
            return False
        
        # Can only assign roles lower than your own
        return assigner_role.level.value > target_role.level.value
    
    def _get_inherited_permissions(self, role: Role) -> Set[Permission]:
        """Get permissions inherited from parent roles."""
        permissions = set()
        
        if role.inherits_from and role.inherits_from in self._roles:
            parent = self._roles[role.inherits_from]
            permissions.update(parent.permissions)
            # Recursive inheritance
            permissions.update(self._get_inherited_permissions(parent))
        
        return permissions
    
    def _scope_matches(self, user_scope: str, requested_scope: str) -> bool:
        """Check if user's scope includes the requested scope."""
        # e.g., "state:maharashtra" includes "district:pune"
        # e.g., "district:pune" includes "ward:123"
        
        user_parts = user_scope.split(":")
        req_parts = requested_scope.split(":")
        
        scope_hierarchy = ["state", "district", "ward", "project"]
        
        user_level = scope_hierarchy.index(user_parts[0]) if user_parts[0] in scope_hierarchy else -1
        req_level = scope_hierarchy.index(req_parts[0]) if req_parts[0] in scope_hierarchy else -1
        
        # User scope is broader or equal
        return user_level <= req_level
    
    async def get_role_hierarchy(self) -> List[Dict]:
        """Get role hierarchy for UI."""
        roles = sorted(self._roles.values(), key=lambda r: r.level.value, reverse=True)
        
        return [
            {
                "id": role.id,
                "name": role.display_name,
                "level": role.level.value,
                "permissions_count": len(role.permissions),
                "inherits_from": role.inherits_from,
                "description": role.description
            }
            for role in roles
        ]


# Singleton
_rbac: Optional[RBACService] = None

def get_rbac_service() -> RBACService:
    global _rbac
    if _rbac is None:
        _rbac = RBACService()
    return _rbac


# ==================== PERMISSION DECORATOR ====================

from functools import wraps
from fastapi import HTTPException, Depends

def require_permission(permission: Permission, scope_param: Optional[str] = None):
    """Decorator to check permission on endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (injected by dependency)
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            rbac = get_rbac_service()
            
            # Get scope from path params if specified
            scope = None
            if scope_param and scope_param in kwargs:
                scope = kwargs[scope_param]
            
            has_permission = await rbac.check_permission(
                current_user.id,
                permission,
                scope
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
