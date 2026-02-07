"""
Batch Operations Service
Bulk approve, reject, archive, and process operations
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


class BatchOperation(str, Enum):
    """Types of batch operations."""
    APPROVE = "approve"
    REJECT = "reject"
    ARCHIVE = "archive"
    DELETE = "delete"
    UPDATE_STATUS = "update_status"
    ASSIGN = "assign"
    EXPORT = "export"
    NOTIFY = "notify"
    VERIFY = "verify"


class EntityType(str, Enum):
    """Entity types that support batch operations."""
    PROJECT = "project"
    ASSESSMENT = "assessment"
    PAYMENT = "payment"
    VERIFICATION = "verification"
    INSTALLER = "installer"
    USER = "user"
    SENSOR = "sensor"


@dataclass
class BatchResult:
    """Result of a batch operation."""
    total: int
    succeeded: int
    failed: int
    skipped: int
    errors: List[Dict[str, Any]]
    duration_ms: float
    
    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0
        return (self.succeeded / self.total) * 100


@dataclass
class BatchJob:
    """Batch job tracking."""
    id: str
    operation: BatchOperation
    entity_type: EntityType
    entity_ids: List[int]
    params: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[BatchResult] = None
    user_id: str = ""


class BatchOperationsService:
    """Service for handling bulk operations."""
    
    def __init__(self):
        self._jobs: Dict[str, BatchJob] = {}
        self._processors = {
            EntityType.PROJECT: self._process_project_operation,
            EntityType.ASSESSMENT: self._process_assessment_operation,
            EntityType.PAYMENT: self._process_payment_operation,
            EntityType.VERIFICATION: self._process_verification_operation,
            EntityType.INSTALLER: self._process_installer_operation,
        }
    
    async def execute(
        self,
        operation: BatchOperation,
        entity_type: EntityType,
        entity_ids: List[int],
        params: Optional[Dict[str, Any]] = None,
        user_id: str = "",
        dry_run: bool = False
    ) -> BatchResult:
        """
        Execute a batch operation on multiple entities.
        
        Args:
            operation: Type of operation to perform
            entity_type: Type of entities to operate on
            entity_ids: List of entity IDs
            params: Additional parameters for the operation
            user_id: User performing the operation
            dry_run: If True, validate only without executing
        """
        start_time = datetime.now()
        params = params or {}
        
        # Validate operation is allowed
        self._validate_operation(operation, entity_type)
        
        # Initialize counters
        succeeded = 0
        failed = 0
        skipped = 0
        errors = []
        
        # Get processor for entity type
        processor = self._processors.get(entity_type)
        if not processor:
            raise ValueError(f"No processor for entity type: {entity_type}")
        
        # Process each entity
        for entity_id in entity_ids:
            try:
                if dry_run:
                    # Just validate
                    valid = await self._validate_entity(entity_type, entity_id, operation)
                    if valid:
                        succeeded += 1
                    else:
                        skipped += 1
                else:
                    # Execute operation
                    success = await processor(operation, entity_id, params, user_id)
                    if success:
                        succeeded += 1
                    else:
                        skipped += 1
            except Exception as e:
                failed += 1
                errors.append({
                    "entity_id": entity_id,
                    "error": str(e),
                    "type": type(e).__name__
                })
                logger.error(f"Batch operation failed for {entity_type}:{entity_id}: {e}")
        
        # Calculate duration
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log audit
        await self._log_batch_audit(
            operation, entity_type, entity_ids, 
            succeeded, failed, user_id
        )
        
        return BatchResult(
            total=len(entity_ids),
            succeeded=succeeded,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration_ms=duration_ms
        )
    
    async def execute_async(
        self,
        operation: BatchOperation,
        entity_type: EntityType,
        entity_ids: List[int],
        params: Optional[Dict[str, Any]] = None,
        user_id: str = ""
    ) -> str:
        """
        Start a batch operation asynchronously.
        Returns job ID for tracking.
        """
        import uuid
        
        job_id = str(uuid.uuid4())
        job = BatchJob(
            id=job_id,
            operation=operation,
            entity_type=entity_type,
            entity_ids=entity_ids,
            params=params or {},
            created_at=datetime.now(),
            user_id=user_id,
            status="pending"
        )
        
        self._jobs[job_id] = job
        
        # Start background task
        asyncio.create_task(self._run_job(job_id))
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get status of a batch job."""
        return self._jobs.get(job_id)
    
    async def _run_job(self, job_id: str):
        """Run a batch job in background."""
        job = self._jobs.get(job_id)
        if not job:
            return
        
        job.status = "running"
        job.started_at = datetime.now()
        
        try:
            result = await self.execute(
                job.operation,
                job.entity_type,
                job.entity_ids,
                job.params,
                job.user_id
            )
            job.result = result
            job.status = "completed"
        except Exception as e:
            job.status = "failed"
            job.result = BatchResult(
                total=len(job.entity_ids),
                succeeded=0,
                failed=len(job.entity_ids),
                skipped=0,
                errors=[{"error": str(e)}],
                duration_ms=0
            )
        finally:
            job.completed_at = datetime.now()
    
    def _validate_operation(self, operation: BatchOperation, entity_type: EntityType):
        """Validate that operation is allowed for entity type."""
        allowed_ops = {
            EntityType.PROJECT: {
                BatchOperation.APPROVE, BatchOperation.REJECT,
                BatchOperation.ARCHIVE, BatchOperation.UPDATE_STATUS,
                BatchOperation.ASSIGN, BatchOperation.EXPORT
            },
            EntityType.ASSESSMENT: {
                BatchOperation.APPROVE, BatchOperation.REJECT,
                BatchOperation.EXPORT
            },
            EntityType.PAYMENT: {
                BatchOperation.APPROVE, BatchOperation.REJECT,
                BatchOperation.EXPORT
            },
            EntityType.VERIFICATION: {
                BatchOperation.APPROVE, BatchOperation.REJECT,
                BatchOperation.VERIFY
            },
            EntityType.INSTALLER: {
                BatchOperation.APPROVE, BatchOperation.REJECT,
                BatchOperation.ARCHIVE, BatchOperation.NOTIFY
            }
        }
        
        if operation not in allowed_ops.get(entity_type, set()):
            raise ValueError(
                f"Operation {operation} not allowed for {entity_type}"
            )
    
    async def _validate_entity(
        self, 
        entity_type: EntityType, 
        entity_id: int,
        operation: BatchOperation
    ) -> bool:
        """Validate entity exists and can be operated on."""
        # In real implementation, check database
        return True
    
    async def _process_project_operation(
        self,
        operation: BatchOperation,
        project_id: int,
        params: Dict[str, Any],
        user_id: str
    ) -> bool:
        """Process operation on a project."""
        if operation == BatchOperation.APPROVE:
            # Update project status to approved
            logger.info(f"Approving project {project_id}")
            return True
        
        elif operation == BatchOperation.REJECT:
            reason = params.get("reason", "No reason provided")
            logger.info(f"Rejecting project {project_id}: {reason}")
            return True
        
        elif operation == BatchOperation.ARCHIVE:
            logger.info(f"Archiving project {project_id}")
            return True
        
        elif operation == BatchOperation.UPDATE_STATUS:
            new_status = params.get("status")
            if not new_status:
                raise ValueError("Status parameter required")
            logger.info(f"Updating project {project_id} status to {new_status}")
            return True
        
        elif operation == BatchOperation.ASSIGN:
            installer_id = params.get("installer_id")
            if not installer_id:
                raise ValueError("Installer ID required")
            logger.info(f"Assigning project {project_id} to installer {installer_id}")
            return True
        
        return False
    
    async def _process_assessment_operation(
        self,
        operation: BatchOperation,
        assessment_id: int,
        params: Dict[str, Any],
        user_id: str
    ) -> bool:
        """Process operation on an assessment."""
        if operation == BatchOperation.APPROVE:
            logger.info(f"Approving assessment {assessment_id}")
            return True
        
        elif operation == BatchOperation.REJECT:
            logger.info(f"Rejecting assessment {assessment_id}")
            return True
        
        return False
    
    async def _process_payment_operation(
        self,
        operation: BatchOperation,
        payment_id: int,
        params: Dict[str, Any],
        user_id: str
    ) -> bool:
        """Process operation on a payment."""
        if operation == BatchOperation.APPROVE:
            logger.info(f"Approving payment {payment_id}")
            return True
        
        elif operation == BatchOperation.REJECT:
            logger.info(f"Rejecting payment {payment_id}")
            return True
        
        return False
    
    async def _process_verification_operation(
        self,
        operation: BatchOperation,
        verification_id: int,
        params: Dict[str, Any],
        user_id: str
    ) -> bool:
        """Process operation on a verification."""
        if operation == BatchOperation.APPROVE:
            logger.info(f"Approving verification {verification_id}")
            return True
        
        elif operation == BatchOperation.REJECT:
            reason = params.get("reason", "Does not meet requirements")
            logger.info(f"Rejecting verification {verification_id}: {reason}")
            return True
        
        elif operation == BatchOperation.VERIFY:
            logger.info(f"Auto-verifying {verification_id}")
            return True
        
        return False
    
    async def _process_installer_operation(
        self,
        operation: BatchOperation,
        installer_id: int,
        params: Dict[str, Any],
        user_id: str
    ) -> bool:
        """Process operation on an installer."""
        if operation == BatchOperation.APPROVE:
            logger.info(f"Approving installer {installer_id}")
            return True
        
        elif operation == BatchOperation.REJECT:
            logger.info(f"Rejecting installer {installer_id}")
            return True
        
        elif operation == BatchOperation.NOTIFY:
            message = params.get("message", "")
            logger.info(f"Notifying installer {installer_id}: {message}")
            return True
        
        return False
    
    async def _log_batch_audit(
        self,
        operation: BatchOperation,
        entity_type: EntityType,
        entity_ids: List[int],
        succeeded: int,
        failed: int,
        user_id: str
    ):
        """Log batch operation to audit trail."""
        logger.info(
            f"Batch {operation} on {entity_type}: "
            f"{succeeded} succeeded, {failed} failed, "
            f"by user {user_id}"
        )


# Singleton instance
_batch_service: Optional[BatchOperationsService] = None


def get_batch_service() -> BatchOperationsService:
    """Get batch operations service singleton."""
    global _batch_service
    if _batch_service is None:
        _batch_service = BatchOperationsService()
    return _batch_service
