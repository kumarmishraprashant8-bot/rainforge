"""
Unified Notification Hub
Orchestrates notifications across all channels: WhatsApp, SMS, Email, Push
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

from app.services.whatsapp_service import get_whatsapp_service, MessageTemplate
from app.services.sms_service import get_sms_service

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationType(str, Enum):
    ALERT = "alert"
    REMINDER = "reminder"
    PAYMENT = "payment"
    VERIFICATION = "verification"
    BID = "bid"
    SYSTEM = "system"


@dataclass
class NotificationResult:
    """Result of sending a notification."""
    channel: NotificationChannel
    success: bool
    message_id: Optional[str]
    error: Optional[str]
    sent_at: datetime


@dataclass
class Notification:
    """Notification to be sent."""
    user_id: str
    phone: Optional[str]
    email: Optional[str]
    type: NotificationType
    title: str
    body: str
    data: Dict[str, Any]
    channels: List[NotificationChannel]
    priority: str = "normal"  # low, normal, high, critical


class NotificationHub:
    """
    Central notification orchestrator.
    Handles channel selection, fallback, and rate limiting.
    """
    
    def __init__(self):
        self.whatsapp = get_whatsapp_service()
        self.sms = get_sms_service()
        self._notifications_sent: Dict[str, int] = {}  # Rate limiting
        
    async def send(
        self,
        notification: Notification
    ) -> List[NotificationResult]:
        """
        Send notification via specified channels.
        Falls back to next channel if primary fails.
        """
        results = []
        
        for channel in notification.channels:
            try:
                if channel == NotificationChannel.WHATSAPP:
                    result = await self._send_whatsapp(notification)
                elif channel == NotificationChannel.SMS:
                    result = await self._send_sms(notification)
                elif channel == NotificationChannel.EMAIL:
                    result = await self._send_email(notification)
                elif channel == NotificationChannel.PUSH:
                    result = await self._send_push(notification)
                else:
                    result = await self._log_in_app(notification)
                
                results.append(result)
                
                # Stop if high priority and first channel succeeds
                if notification.priority in ["high", "critical"] and result.success:
                    break
                    
            except Exception as e:
                logger.error(f"Notification failed on {channel}: {e}")
                results.append(NotificationResult(
                    channel=channel,
                    success=False,
                    message_id=None,
                    error=str(e),
                    sent_at=datetime.utcnow()
                ))
        
        return results
    
    async def _send_whatsapp(self, notification: Notification) -> NotificationResult:
        """Send via WhatsApp."""
        if not notification.phone:
            return NotificationResult(
                channel=NotificationChannel.WHATSAPP,
                success=False,
                message_id=None,
                error="No phone number",
                sent_at=datetime.utcnow()
            )
        
        # Map notification type to template
        template_map = {
            NotificationType.PAYMENT: MessageTemplate.PAYMENT_RECEIVED,
            NotificationType.VERIFICATION: MessageTemplate.VERIFICATION_REMINDER,
            NotificationType.ALERT: MessageTemplate.TANK_ALERT,
            NotificationType.BID: MessageTemplate.BID_AWARDED,
        }
        
        template = template_map.get(notification.type, MessageTemplate.WELCOME)
        
        result = await self.whatsapp.send_template_message(
            to_phone=notification.phone,
            template=template,
            parameters=notification.data
        )
        
        return NotificationResult(
            channel=NotificationChannel.WHATSAPP,
            success=result.get("success", False),
            message_id=result.get("message_id"),
            error=result.get("error"),
            sent_at=datetime.utcnow()
        )
    
    async def _send_sms(self, notification: Notification) -> NotificationResult:
        """Send via SMS."""
        if not notification.phone:
            return NotificationResult(
                channel=NotificationChannel.SMS,
                success=False,
                message_id=None,
                error="No phone number",
                sent_at=datetime.utcnow()
            )
        
        # Truncate message for SMS
        message = f"{notification.title}: {notification.body}"[:160]
        
        result = await self.sms.send_sms(
            to_phone=notification.phone,
            message=message
        )
        
        return NotificationResult(
            channel=NotificationChannel.SMS,
            success=result.get("success", False),
            message_id=result.get("message_id"),
            error=result.get("error"),
            sent_at=datetime.utcnow()
        )
    
    async def _send_email(self, notification: Notification) -> NotificationResult:
        """Send via Email (placeholder)."""
        # TODO: Integrate with SendGrid/AWS SES
        logger.info(f"[EMAIL] {notification.email}: {notification.title}")
        
        return NotificationResult(
            channel=NotificationChannel.EMAIL,
            success=True,
            message_id=f"email_{datetime.now().timestamp()}",
            error=None,
            sent_at=datetime.utcnow()
        )
    
    async def _send_push(self, notification: Notification) -> NotificationResult:
        """Send push notification (placeholder)."""
        # TODO: Integrate with Firebase FCM
        logger.info(f"[PUSH] {notification.user_id}: {notification.title}")
        
        return NotificationResult(
            channel=NotificationChannel.PUSH,
            success=True,
            message_id=f"push_{datetime.now().timestamp()}",
            error=None,
            sent_at=datetime.utcnow()
        )
    
    async def _log_in_app(self, notification: Notification) -> NotificationResult:
        """Log for in-app notification (placeholder)."""
        logger.info(f"[IN_APP] {notification.user_id}: {notification.title}")
        
        return NotificationResult(
            channel=NotificationChannel.IN_APP,
            success=True,
            message_id=f"app_{datetime.now().timestamp()}",
            error=None,
            sent_at=datetime.utcnow()
        )
    
    # ==================== CONVENIENCE METHODS ====================
    
    async def send_tank_alert(
        self,
        user_id: str,
        phone: str,
        tank_level: float,
        project_name: str
    ) -> List[NotificationResult]:
        """Send tank level alert."""
        status = "LOW" if tank_level < 20 else "FULL" if tank_level > 90 else "NORMAL"
        
        notification = Notification(
            user_id=user_id,
            phone=phone,
            email=None,
            type=NotificationType.ALERT,
            title=f"Tank Alert: {project_name}",
            body=f"Tank level is {tank_level:.0f}% ({status})",
            data={
                "project_name": project_name,
                "level": f"{tank_level:.0f}%",
                "status": status
            },
            channels=[NotificationChannel.WHATSAPP, NotificationChannel.SMS],
            priority="high" if status in ["LOW", "FULL"] else "normal"
        )
        
        return await self.send(notification)
    
    async def send_payment_notification(
        self,
        user_id: str,
        phone: str,
        amount: float,
        reference: str
    ) -> List[NotificationResult]:
        """Send payment received notification."""
        notification = Notification(
            user_id=user_id,
            phone=phone,
            email=None,
            type=NotificationType.PAYMENT,
            title="Payment Received",
            body=f"₹{amount:,.2f} received (Ref: {reference})",
            data={
                "amount": f"₹{amount:,.2f}",
                "reference": reference,
                "date": datetime.now().strftime("%d %b %Y")
            },
            channels=[NotificationChannel.WHATSAPP, NotificationChannel.SMS],
            priority="normal"
        )
        
        return await self.send(notification)
    
    async def send_verification_reminder(
        self,
        user_id: str,
        phone: str,
        installer_name: str,
        job_id: str,
        deadline: str
    ) -> List[NotificationResult]:
        """Send verification reminder to installer."""
        notification = Notification(
            user_id=user_id,
            phone=phone,
            email=None,
            type=NotificationType.VERIFICATION,
            title="Verification Reminder",
            body=f"Job {job_id} verification due by {deadline}",
            data={
                "name": installer_name,
                "job_id": job_id,
                "deadline": deadline
            },
            channels=[NotificationChannel.WHATSAPP, NotificationChannel.SMS],
            priority="high"
        )
        
        return await self.send(notification)
    
    async def send_bid_notification(
        self,
        user_id: str,
        phone: str,
        installer_name: str,
        job_id: str,
        amount: float,
        awarded: bool
    ) -> List[NotificationResult]:
        """Send bid status notification."""
        notification = Notification(
            user_id=user_id,
            phone=phone,
            email=None,
            type=NotificationType.BID,
            title="Bid Awarded" if awarded else "Bid Update",
            body=f"Job {job_id} bid {'accepted' if awarded else 'updated'} for ₹{amount:,.0f}",
            data={
                "name": installer_name,
                "job_id": job_id,
                "amount": f"₹{amount:,.2f}"
            },
            channels=[NotificationChannel.WHATSAPP, NotificationChannel.SMS],
            priority="high" if awarded else "normal"
        )
        
        return await self.send(notification)
    
    async def broadcast(
        self,
        recipients: List[Dict[str, str]],
        title: str,
        body: str,
        channels: List[NotificationChannel] = None
    ) -> Dict[str, Any]:
        """Send broadcast to multiple recipients."""
        if channels is None:
            channels = [NotificationChannel.SMS]
        
        results = {"success": 0, "failed": 0, "errors": []}
        
        for recipient in recipients:
            notification = Notification(
                user_id=recipient.get("user_id", ""),
                phone=recipient.get("phone"),
                email=recipient.get("email"),
                type=NotificationType.SYSTEM,
                title=title,
                body=body,
                data={},
                channels=channels,
                priority="normal"
            )
            
            try:
                res = await self.send(notification)
                if any(r.success for r in res):
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))
            
            # Rate limiting
            await asyncio.sleep(0.1)
        
        return results


# Singleton
_notification_hub: Optional[NotificationHub] = None

def get_notification_hub() -> NotificationHub:
    global _notification_hub
    if _notification_hub is None:
        _notification_hub = NotificationHub()
    return _notification_hub
