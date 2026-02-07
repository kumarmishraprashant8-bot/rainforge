"""
Audit Logging Service
Complete audit trail for compliance
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Audit action types."""
    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    PASSWORD_CHANGE = "auth.password_change"
    TOKEN_REFRESH = "auth.token_refresh"
    
    # User Management
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    ROLE_CHANGE = "user.role_change"
    
    # Project Actions
    PROJECT_CREATE = "project.create"
    PROJECT_UPDATE = "project.update"
    PROJECT_DELETE = "project.delete"
    
    # Assessment Actions
    ASSESSMENT_CREATE = "assessment.create"
    ASSESSMENT_UPDATE = "assessment.update"
    
    # Verification
    VERIFICATION_SUBMIT = "verification.submit"
    VERIFICATION_APPROVE = "verification.approve"
    VERIFICATION_REJECT = "verification.reject"
    PHOTO_UPLOAD = "verification.photo_upload"
    
    # Payments
    PAYMENT_INITIATE = "payment.initiate"
    PAYMENT_COMPLETE = "payment.complete"
    PAYMENT_FAIL = "payment.fail"
    REFUND_INITIATE = "payment.refund"
    
    # Marketplace
    BID_CREATE = "marketplace.bid_create"
    BID_UPDATE = "marketplace.bid_update"
    BID_AWARD = "marketplace.bid_award"
    INSTALLER_VERIFY = "marketplace.installer_verify"
    
    # Admin
    CONFIG_CHANGE = "admin.config_change"
    EXPORT_DATA = "admin.export_data"
    BULK_OPERATION = "admin.bulk_operation"
    
    # Security
    SUSPICIOUS_ACTIVITY = "security.suspicious"
    ACCESS_DENIED = "security.access_denied"
    RATE_LIMIT_HIT = "security.rate_limit"


class AuditLevel(str, Enum):
    """Audit log severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """Audit log entry."""
    id: str
    timestamp: datetime
    action: AuditAction
    level: AuditLevel
    user_id: Optional[str]
    user_email: Optional[str]
    user_role: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    changes: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    request_id: Optional[str]


class AuditLogService:
    """
    Comprehensive audit logging for compliance.
    
    Features:
    - Complete action trail
    - Change tracking (before/after)
    - User context
    - IP and user agent tracking
    - Searchable logs
    - Export capabilities
    """
    
    def __init__(self):
        self._logs: List[AuditEntry] = []
        self._max_memory_logs = 10000  # Keep in memory
    
    async def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO,
        request_id: Optional[str] = None,
        **metadata
    ) -> AuditEntry:
        """Create audit log entry."""
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            level=level,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            metadata=metadata,
            request_id=request_id
        )
        
        # Store in memory (in production, would persist to database)
        self._logs.append(entry)
        
        # Trim if too many
        if len(self._logs) > self._max_memory_logs:
            self._logs = self._logs[-self._max_memory_logs:]
        
        # Also log to standard logger
        log_msg = f"[AUDIT] {action.value} | User: {user_email or user_id or 'anonymous'}"
        if resource_type:
            log_msg += f" | Resource: {resource_type}/{resource_id}"
        
        if level == AuditLevel.CRITICAL:
            logger.critical(log_msg)
        elif level == AuditLevel.ERROR:
            logger.error(log_msg)
        elif level == AuditLevel.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        return entry
    
    async def log_change(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        before: Dict[str, Any],
        after: Dict[str, Any],
        user_id: str,
        **kwargs
    ) -> AuditEntry:
        """Log a change with before/after values."""
        # Calculate diff
        changes = {
            "before": {},
            "after": {}
        }
        
        all_keys = set(before.keys()) | set(after.keys())
        for key in all_keys:
            before_val = before.get(key)
            after_val = after.get(key)
            
            if before_val != after_val:
                changes["before"][key] = before_val
                changes["after"][key] = after_val
        
        return await self.log(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            **kwargs
        )
    
    async def search(
        self,
        action: Optional[AuditAction] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[AuditLevel] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEntry]:
        """Search audit logs."""
        results = self._logs
        
        if action:
            results = [e for e in results if e.action == action]
        
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        
        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]
        
        if resource_id:
            results = [e for e in results if e.resource_id == resource_id]
        
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
        
        if level:
            results = [e for e in results if e.level == level]
        
        # Sort by timestamp descending
        results.sort(key=lambda e: e.timestamp, reverse=True)
        
        return results[offset:offset + limit]
    
    async def get_user_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get user activity summary."""
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        user_logs = [e for e in self._logs if e.user_id == user_id and e.timestamp >= cutoff]
        
        # Count by action type
        action_counts = {}
        for entry in user_logs:
            action = entry.action.value
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_actions": len(user_logs),
            "action_breakdown": action_counts,
            "last_activity": max((e.timestamp for e in user_logs), default=None),
            "suspicious_count": len([e for e in user_logs if e.level == AuditLevel.WARNING])
        }
    
    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str
    ) -> List[Dict]:
        """Get complete history for a resource."""
        history = [
            e for e in self._logs
            if e.resource_type == resource_type and e.resource_id == resource_id
        ]
        
        history.sort(key=lambda e: e.timestamp)
        
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "action": e.action.value,
                "user": e.user_email or e.user_id,
                "changes": e.changes
            }
            for e in history
        ]
    
    async def export(
        self,
        start_time: datetime,
        end_time: datetime,
        format: str = "json"
    ) -> str:
        """Export audit logs."""
        entries = await self.search(start_time=start_time, end_time=end_time, limit=10000)
        
        if format == "json":
            return json.dumps([
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat(),
                    "action": e.action.value,
                    "level": e.level.value,
                    "user_id": e.user_id,
                    "user_email": e.user_email,
                    "resource": f"{e.resource_type}/{e.resource_id}" if e.resource_type else None,
                    "changes": e.changes,
                    "ip": e.ip_address
                }
                for e in entries
            ], indent=2)
        
        elif format == "csv":
            lines = ["timestamp,action,level,user,resource,ip"]
            for e in entries:
                lines.append(
                    f"{e.timestamp.isoformat()},{e.action.value},{e.level.value},"
                    f"{e.user_email or e.user_id},{e.resource_type}/{e.resource_id},{e.ip_address}"
                )
            return "\n".join(lines)
        
        return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit log statistics."""
        if not self._logs:
            return {"total": 0}
        
        return {
            "total_entries": len(self._logs),
            "earliest": min(e.timestamp for e in self._logs).isoformat(),
            "latest": max(e.timestamp for e in self._logs).isoformat(),
            "by_level": {
                level.value: len([e for e in self._logs if e.level == level])
                for level in AuditLevel
            },
            "unique_users": len(set(e.user_id for e in self._logs if e.user_id))
        }


# Singleton
_audit_service: Optional[AuditLogService] = None

def get_audit_service() -> AuditLogService:
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditLogService()
    return _audit_service


# ==================== MIDDLEWARE FOR AUTOMATIC AUDITING ====================

class AuditMiddleware:
    """FastAPI middleware for automatic audit logging."""
    
    def __init__(self, app, audit_service: AuditLogService):
        self.app = app
        self.audit = audit_service
        
        # Endpoints to audit
        self.audit_patterns = [
            ("/auth/", [AuditAction.LOGIN, AuditAction.LOGOUT]),
            ("/payments/", [AuditAction.PAYMENT_INITIATE, AuditAction.PAYMENT_COMPLETE]),
            ("/verification/", [AuditAction.VERIFICATION_SUBMIT]),
            ("/admin/", [AuditAction.CONFIG_CHANGE])
        ]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Process request
        await self.app(scope, receive, send)
