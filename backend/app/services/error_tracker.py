"""
Error Tracking and Logging Service
Centralized error handling with context
"""

import logging
import traceback
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    INTERNAL = "internal"
    CLIENT = "client"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    CONFIGURATION = "configuration"


@dataclass
class ErrorContext:
    """Context information for an error."""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrackedError:
    """Tracked error with full context."""
    id: str
    fingerprint: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    exception_type: str
    stack_trace: str
    context: ErrorContext
    timestamp: datetime
    resolved: bool = False
    occurrence_count: int = 1
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


class ErrorTracker:
    """Central error tracking service."""
    
    def __init__(self, max_errors: int = 1000):
        self._errors: Dict[str, TrackedError] = {}
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._max_errors = max_errors
        self._hooks: List[callable] = []
    
    async def capture(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
        tags: Optional[List[str]] = None
    ) -> TrackedError:
        """Capture and track an exception."""
        import uuid
        
        context = context or ErrorContext()
        category = category or self._classify_error(error)
        severity = severity or self._determine_severity(error, category)
        
        # Generate fingerprint for deduplication
        fingerprint = self._generate_fingerprint(error)
        
        # Get stack trace
        stack_trace = ''.join(traceback.format_exception(
            type(error), error, error.__traceback__
        ))
        
        now = datetime.utcnow()
        
        # Check for existing error with same fingerprint
        if fingerprint in self._errors:
            existing = self._errors[fingerprint]
            existing.occurrence_count += 1
            existing.last_seen = now
            tracked_error = existing
        else:
            tracked_error = TrackedError(
                id=str(uuid.uuid4()),
                fingerprint=fingerprint,
                message=str(error),
                category=category,
                severity=severity,
                exception_type=type(error).__name__,
                stack_trace=stack_trace,
                context=context,
                timestamp=now,
                first_seen=now,
                last_seen=now,
                tags=tags or []
            )
            
            # Store error (with size limit)
            self._errors[fingerprint] = tracked_error
            if len(self._errors) > self._max_errors:
                # Remove oldest resolved errors first
                self._cleanup_old_errors()
        
        # Update counts
        self._error_counts[category] += 1
        
        # Log error
        self._log_error(tracked_error)
        
        # Run hooks
        await self._run_hooks(tracked_error)
        
        return tracked_error
    
    async def capture_message(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[ErrorContext] = None,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        tags: Optional[List[str]] = None
    ) -> TrackedError:
        """Capture an error message without exception."""
        import uuid
        
        context = context or ErrorContext()
        fingerprint = hashlib.md5(message.encode()).hexdigest()
        now = datetime.utcnow()
        
        tracked_error = TrackedError(
            id=str(uuid.uuid4()),
            fingerprint=fingerprint,
            message=message,
            category=category,
            severity=severity,
            exception_type="Message",
            stack_trace="",
            context=context,
            timestamp=now,
            first_seen=now,
            last_seen=now,
            tags=tags or []
        )
        
        self._errors[fingerprint] = tracked_error
        self._log_error(tracked_error)
        await self._run_hooks(tracked_error)
        
        return tracked_error
    
    def add_hook(self, hook: callable):
        """Add a hook to be called on error capture."""
        self._hooks.append(hook)
    
    def get_errors(
        self,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
        resolved: Optional[bool] = None,
        limit: int = 50
    ) -> List[TrackedError]:
        """Get tracked errors with optional filters."""
        errors = list(self._errors.values())
        
        if category:
            errors = [e for e in errors if e.category == category]
        if severity:
            errors = [e for e in errors if e.severity == severity]
        if resolved is not None:
            errors = [e for e in errors if e.resolved == resolved]
        
        # Sort by last seen, newest first
        errors.sort(key=lambda e: e.last_seen or e.timestamp, reverse=True)
        
        return errors[:limit]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        errors = list(self._errors.values())
        
        return {
            "total_errors": len(errors),
            "unresolved": sum(1 for e in errors if not e.resolved),
            "by_category": dict(self._error_counts),
            "by_severity": {
                s.value: sum(1 for e in errors if e.severity == s)
                for s in ErrorSeverity
            },
            "top_errors": [
                {
                    "message": e.message[:100],
                    "count": e.occurrence_count,
                    "category": e.category
                }
                for e in sorted(errors, key=lambda x: x.occurrence_count, reverse=True)[:10]
            ]
        }
    
    def resolve_error(self, error_id: str) -> bool:
        """Mark an error as resolved."""
        for error in self._errors.values():
            if error.id == error_id:
                error.resolved = True
                return True
        return False
    
    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classify error into category."""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Classification rules
        if "validation" in error_msg or error_type in ("ValidationError", "ValueError"):
            return ErrorCategory.VALIDATION
        if "auth" in error_msg or error_type in ("AuthenticationError", "Unauthorized"):
            return ErrorCategory.AUTHENTICATION
        if "permission" in error_msg or "forbidden" in error_msg:
            return ErrorCategory.AUTHORIZATION
        if "database" in error_msg or "sql" in error_msg or "postgres" in error_msg:
            return ErrorCategory.DATABASE
        if "timeout" in error_msg or error_type == "TimeoutError":
            return ErrorCategory.TIMEOUT
        if "rate" in error_msg and "limit" in error_msg:
            return ErrorCategory.RATE_LIMIT
        if "connection" in error_msg or "network" in error_msg:
            return ErrorCategory.NETWORK
        if "api" in error_msg or "request" in error_msg:
            return ErrorCategory.EXTERNAL_API
        
        return ErrorCategory.INTERNAL
    
    def _determine_severity(
        self, 
        error: Exception, 
        category: ErrorCategory
    ) -> ErrorSeverity:
        """Determine error severity."""
        # Critical categories
        if category in (ErrorCategory.DATABASE, ErrorCategory.AUTHENTICATION):
            return ErrorSeverity.CRITICAL
        
        # Warning categories
        if category in (ErrorCategory.VALIDATION, ErrorCategory.CLIENT):
            return ErrorSeverity.WARNING
        
        return ErrorSeverity.ERROR
    
    def _generate_fingerprint(self, error: Exception) -> str:
        """Generate unique fingerprint for error deduplication."""
        # Use exception type and first line of stack trace
        tb = traceback.extract_tb(error.__traceback__)
        location = ""
        if tb:
            last_frame = tb[-1]
            location = f"{last_frame.filename}:{last_frame.lineno}:{last_frame.name}"
        
        fingerprint_data = f"{type(error).__name__}:{location}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def _log_error(self, error: TrackedError):
        """Log error to standard logging."""
        log_level = {
            ErrorSeverity.DEBUG: logging.DEBUG,
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error.severity, logging.ERROR)
        
        logger.log(
            log_level,
            f"[{error.category}] {error.message}",
            extra={
                "error_id": error.id,
                "fingerprint": error.fingerprint,
                "exception_type": error.exception_type,
                "user_id": error.context.user_id,
                "request_id": error.context.request_id
            }
        )
    
    async def _run_hooks(self, error: TrackedError):
        """Run registered hooks."""
        for hook in self._hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(error)
                else:
                    hook(error)
            except Exception as e:
                logger.error(f"Error hook failed: {e}")
    
    def _cleanup_old_errors(self):
        """Remove old resolved errors to stay under limit."""
        resolved = [
            (fp, e) for fp, e in self._errors.items() if e.resolved
        ]
        resolved.sort(key=lambda x: x[1].last_seen or x[1].timestamp)
        
        # Remove oldest 10% of resolved errors
        to_remove = len(self._errors) - self._max_errors + 10
        for fp, _ in resolved[:to_remove]:
            del self._errors[fp]


# Singleton instance
_error_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """Get error tracker singleton."""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


# FastAPI exception handler
async def error_handler(request, exc):
    """FastAPI exception handler that captures errors."""
    from fastapi import Response
    
    tracker = get_error_tracker()
    
    context = ErrorContext(
        request_id=request.headers.get("X-Request-ID"),
        endpoint=str(request.url.path),
        method=request.method,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent")
    )
    
    tracked = await tracker.capture(exc, context)
    
    return Response(
        content=json.dumps({
            "error": str(exc),
            "error_id": tracked.id,
            "category": tracked.category
        }),
        status_code=500,
        media_type="application/json"
    )
