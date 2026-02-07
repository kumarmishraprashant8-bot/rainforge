"""
Webhook Retry Queue
Reliable webhook processing with exponential backoff
"""
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import httpx

logger = logging.getLogger(__name__)


class WebhookStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class WebhookJob:
    """Webhook job structure."""
    id: str
    url: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    method: str = "POST"
    attempts: int = 0
    max_attempts: int = 5
    status: WebhookStatus = WebhookStatus.PENDING
    created_at: datetime = None
    next_retry_at: datetime = None
    last_error: Optional[str] = None
    last_status_code: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.id is None:
            self.id = hashlib.sha256(
                f"{self.url}:{self.created_at.timestamp()}".encode()
            ).hexdigest()[:16]


class WebhookQueue:
    """
    Reliable webhook delivery with retry logic.
    
    Features:
    - Exponential backoff
    - Dead letter queue
    - Signature verification
    - Batch processing
    """
    
    # Retry intervals (exponential backoff)
    RETRY_DELAYS = [30, 60, 300, 900, 3600]  # 30s, 1m, 5m, 15m, 1h
    
    def __init__(self):
        self._queue: List[WebhookJob] = []
        self._dead_letter: List[WebhookJob] = []
        self._processing = False
        self._handlers: Dict[str, Callable] = {}
    
    async def enqueue(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        webhook_type: Optional[str] = None
    ) -> WebhookJob:
        """Add webhook to queue."""
        job = WebhookJob(
            id=None,
            url=url,
            payload=payload,
            headers=headers or {},
            next_retry_at=datetime.utcnow()
        )
        
        # Add signature if configured
        if webhook_type:
            job.headers['X-Webhook-Type'] = webhook_type
            job.headers['X-Webhook-Signature'] = self._sign_payload(payload)
        
        self._queue.append(job)
        logger.info(f"Enqueued webhook {job.id} to {url}")
        
        return job
    
    async def process_queue(self):
        """Process all pending webhooks."""
        if self._processing:
            return
        
        self._processing = True
        now = datetime.utcnow()
        
        try:
            # Get jobs ready for processing
            ready_jobs = [
                job for job in self._queue
                if job.status == WebhookStatus.PENDING 
                and job.next_retry_at <= now
            ]
            
            for job in ready_jobs:
                await self._process_job(job)
            
            # Remove completed jobs
            self._queue = [
                job for job in self._queue
                if job.status not in [WebhookStatus.SUCCESS, WebhookStatus.DEAD_LETTER]
            ]
            
        finally:
            self._processing = False
    
    async def _process_job(self, job: WebhookJob):
        """Process a single webhook job."""
        job.status = WebhookStatus.PROCESSING
        job.attempts += 1
        
        logger.info(f"Processing webhook {job.id} (attempt {job.attempts})")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=job.method,
                    url=job.url,
                    json=job.payload,
                    headers=job.headers
                )
                
                job.last_status_code = response.status_code
                
                if response.status_code in [200, 201, 202, 204]:
                    job.status = WebhookStatus.SUCCESS
                    logger.info(f"Webhook {job.id} succeeded")
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")
                    
        except Exception as e:
            logger.error(f"Webhook {job.id} failed: {e}")
            job.last_error = str(e)
            
            if job.attempts >= job.max_attempts:
                job.status = WebhookStatus.DEAD_LETTER
                self._dead_letter.append(job)
                logger.warning(f"Webhook {job.id} moved to dead letter queue")
            else:
                job.status = WebhookStatus.PENDING
                delay = self.RETRY_DELAYS[min(job.attempts - 1, len(self.RETRY_DELAYS) - 1)]
                job.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
                logger.info(f"Webhook {job.id} scheduled for retry in {delay}s")
    
    def _sign_payload(self, payload: Dict) -> str:
        """Sign webhook payload for verification."""
        from app.core.config import settings
        import hmac
        
        secret = getattr(settings, 'WEBHOOK_SECRET', 'default-secret')
        message = json.dumps(payload, sort_keys=True)
        
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            'sha256'
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "pending": len([j for j in self._queue if j.status == WebhookStatus.PENDING]),
            "processing": len([j for j in self._queue if j.status == WebhookStatus.PROCESSING]),
            "dead_letter": len(self._dead_letter),
            "total_processed": len([j for j in self._queue if j.status == WebhookStatus.SUCCESS])
        }
    
    def get_dead_letter_jobs(self) -> List[Dict]:
        """Get failed jobs for manual review."""
        return [
            {
                "id": job.id,
                "url": job.url,
                "attempts": job.attempts,
                "last_error": job.last_error,
                "created_at": job.created_at.isoformat()
            }
            for job in self._dead_letter
        ]
    
    async def retry_dead_letter(self, job_id: str) -> bool:
        """Retry a dead letter job."""
        for i, job in enumerate(self._dead_letter):
            if job.id == job_id:
                job.status = WebhookStatus.PENDING
                job.attempts = 0
                job.next_retry_at = datetime.utcnow()
                self._queue.append(job)
                self._dead_letter.pop(i)
                return True
        return False


# ==================== PAYMENT WEBHOOK HANDLERS ====================

class PaymentWebhookHandler:
    """Handle incoming payment webhooks."""
    
    def __init__(self):
        self.handlers = {
            "razorpay": self._handle_razorpay,
            "stripe": self._handle_stripe,
            "paytm": self._handle_paytm
        }
    
    async def handle(
        self,
        provider: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Route webhook to appropriate handler."""
        handler = self.handlers.get(provider)
        if not handler:
            raise ValueError(f"Unknown provider: {provider}")
        
        return await handler(payload, signature)
    
    async def _handle_razorpay(
        self,
        payload: Dict,
        signature: Optional[str]
    ) -> Dict:
        """Handle Razorpay webhooks."""
        event = payload.get("event")
        
        if event == "payment.captured":
            payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
            return {
                "action": "payment_captured",
                "payment_id": payment.get("id"),
                "amount": payment.get("amount") / 100,  # Convert paise to rupees
                "order_id": payment.get("order_id"),
                "status": "success"
            }
        
        elif event == "payment.failed":
            payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
            return {
                "action": "payment_failed",
                "payment_id": payment.get("id"),
                "error": payment.get("error_description"),
                "status": "failed"
            }
        
        elif event == "refund.created":
            refund = payload.get("payload", {}).get("refund", {}).get("entity", {})
            return {
                "action": "refund_created",
                "refund_id": refund.get("id"),
                "amount": refund.get("amount") / 100,
                "status": "success"
            }
        
        return {"action": "unknown", "event": event}
    
    async def _handle_stripe(
        self,
        payload: Dict,
        signature: Optional[str]
    ) -> Dict:
        """Handle Stripe webhooks."""
        event_type = payload.get("type")
        data = payload.get("data", {}).get("object", {})
        
        if event_type == "payment_intent.succeeded":
            return {
                "action": "payment_captured",
                "payment_id": data.get("id"),
                "amount": data.get("amount") / 100,
                "status": "success"
            }
        
        elif event_type == "payment_intent.payment_failed":
            return {
                "action": "payment_failed",
                "payment_id": data.get("id"),
                "error": data.get("last_payment_error", {}).get("message"),
                "status": "failed"
            }
        
        return {"action": "unknown", "event": event_type}
    
    async def _handle_paytm(
        self,
        payload: Dict,
        signature: Optional[str]
    ) -> Dict:
        """Handle Paytm webhooks."""
        status = payload.get("STATUS")
        
        if status == "TXN_SUCCESS":
            return {
                "action": "payment_captured",
                "payment_id": payload.get("TXNID"),
                "amount": float(payload.get("TXNAMOUNT", 0)),
                "order_id": payload.get("ORDERID"),
                "status": "success"
            }
        
        elif status == "TXN_FAILURE":
            return {
                "action": "payment_failed",
                "payment_id": payload.get("TXNID"),
                "error": payload.get("RESPMSG"),
                "status": "failed"
            }
        
        return {"action": "unknown", "status": status}


# Singleton instances
_webhook_queue: Optional[WebhookQueue] = None
_payment_handler: Optional[PaymentWebhookHandler] = None

def get_webhook_queue() -> WebhookQueue:
    global _webhook_queue
    if _webhook_queue is None:
        _webhook_queue = WebhookQueue()
    return _webhook_queue

def get_payment_handler() -> PaymentWebhookHandler:
    global _payment_handler
    if _payment_handler is None:
        _payment_handler = PaymentWebhookHandler()
    return _payment_handler
