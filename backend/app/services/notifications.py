"""
Push Notifications Service
Web Push, Firebase FCM, and in-app notifications
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of notifications."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ALERT = "alert"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    IN_APP = "in_app"
    WEB_PUSH = "web_push"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Notification data model."""
    id: str
    user_id: str
    title: str
    body: str
    type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.IN_APP])
    data: Dict[str, Any] = field(default_factory=dict)
    action_url: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


@dataclass
class NotificationPreferences:
    """User notification preferences."""
    user_id: str
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = False
    whatsapp_enabled: bool = False
    quiet_hours_start: Optional[int] = None  # Hour (0-23)
    quiet_hours_end: Optional[int] = None
    categories: Dict[str, bool] = field(default_factory=dict)


class NotificationsService:
    """Service for sending and managing notifications."""
    
    # Notification templates
    TEMPLATES = {
        "project_approved": {
            "title": "Project Approved! 🎉",
            "body": "Your RWH project '{project_name}' has been approved.",
            "type": NotificationType.SUCCESS,
            "priority": NotificationPriority.HIGH
        },
        "payment_received": {
            "title": "Payment Received 💰",
            "body": "Payment of ₹{amount} received for {project_name}.",
            "type": NotificationType.SUCCESS,
            "priority": NotificationPriority.NORMAL
        },
        "verification_required": {
            "title": "Verification Needed 📸",
            "body": "Please upload photos for {project_name} verification.",
            "type": NotificationType.WARNING,
            "priority": NotificationPriority.HIGH
        },
        "tank_low": {
            "title": "Low Tank Level ⚠️",
            "body": "Tank at {project_name} is at {level}%. Consider harvesting.",
            "type": NotificationType.ALERT,
            "priority": NotificationPriority.URGENT
        },
        "maintenance_due": {
            "title": "Maintenance Due 🔧",
            "body": "{maintenance_type} is due for {project_name}.",
            "type": NotificationType.INFO,
            "priority": NotificationPriority.NORMAL
        },
        "badge_earned": {
            "title": "Badge Earned! 🏆",
            "body": "You've earned the '{badge_name}' badge!",
            "type": NotificationType.SUCCESS,
            "priority": NotificationPriority.NORMAL
        }
    }
    
    def __init__(self):
        self._notifications: Dict[str, List[Notification]] = {}
        self._preferences: Dict[str, NotificationPreferences] = {}
        self._push_subscriptions: Dict[str, Dict[str, Any]] = {}
    
    async def send(
        self,
        user_id: str,
        title: str,
        body: str,
        type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: Optional[List[NotificationChannel]] = None,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Notification:
        """Send a notification to a user."""
        import uuid
        
        channels = channels or [NotificationChannel.IN_APP]
        
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            body=body,
            type=type,
            priority=priority,
            channels=channels,
            data=data or {},
            action_url=action_url,
            image_url=image_url
        )
        
        # Check preferences
        prefs = await self.get_preferences(user_id)
        if self._is_quiet_hours(prefs) and priority != NotificationPriority.URGENT:
            # Delay until quiet hours end
            logger.info(f"Delaying notification for {user_id} (quiet hours)")
            # In production: schedule for later
        
        # Send through each channel
        for channel in channels:
            await self._send_via_channel(notification, channel, prefs)
        
        # Store in-app notification
        if NotificationChannel.IN_APP in channels:
            if user_id not in self._notifications:
                self._notifications[user_id] = []
            self._notifications[user_id].insert(0, notification)
            
            # Keep only last 100 notifications
            self._notifications[user_id] = self._notifications[user_id][:100]
        
        notification.sent_at = datetime.utcnow()
        
        return notification
    
    async def send_template(
        self,
        user_id: str,
        template_name: str,
        params: Dict[str, Any],
        channels: Optional[List[NotificationChannel]] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Notification]:
        """Send a notification using a template."""
        template = self.TEMPLATES.get(template_name)
        if not template:
            logger.error(f"Template not found: {template_name}")
            return None
        
        # Format title and body with params
        title = template["title"].format(**params)
        body = template["body"].format(**params)
        
        return await self.send(
            user_id=user_id,
            title=title,
            body=body,
            type=template.get("type", NotificationType.INFO),
            priority=template.get("priority", NotificationPriority.NORMAL),
            channels=channels,
            data=extra_data
        )
    
    async def send_bulk(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        **kwargs
    ) -> List[Notification]:
        """Send notification to multiple users."""
        tasks = [
            self.send(user_id, title, body, **kwargs)
            for user_id in user_ids
        ]
        return await asyncio.gather(*tasks)
    
    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user."""
        notifications = self._notifications.get(user_id, [])
        
        if unread_only:
            notifications = [n for n in notifications if n.read_at is None]
        
        return notifications[offset:offset + limit]
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications."""
        notifications = self._notifications.get(user_id, [])
        return sum(1 for n in notifications if n.read_at is None)
    
    async def mark_read(
        self,
        user_id: str,
        notification_ids: Optional[List[str]] = None
    ):
        """Mark notifications as read."""
        notifications = self._notifications.get(user_id, [])
        now = datetime.utcnow()
        
        for notification in notifications:
            if notification_ids is None or notification.id in notification_ids:
                notification.read_at = now
    
    async def mark_all_read(self, user_id: str):
        """Mark all notifications as read."""
        await self.mark_read(user_id, None)
    
    async def delete(self, user_id: str, notification_id: str) -> bool:
        """Delete a notification."""
        notifications = self._notifications.get(user_id, [])
        for i, n in enumerate(notifications):
            if n.id == notification_id:
                notifications.pop(i)
                return True
        return False
    
    async def register_push_subscription(
        self,
        user_id: str,
        subscription: Dict[str, Any]
    ):
        """Register a web push subscription."""
        self._push_subscriptions[user_id] = subscription
        logger.info(f"Registered push subscription for {user_id}")
    
    async def unregister_push_subscription(self, user_id: str):
        """Unregister a web push subscription."""
        self._push_subscriptions.pop(user_id, None)
    
    async def get_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences."""
        if user_id not in self._preferences:
            self._preferences[user_id] = NotificationPreferences(user_id=user_id)
        return self._preferences[user_id]
    
    async def update_preferences(
        self,
        user_id: str,
        **kwargs
    ) -> NotificationPreferences:
        """Update user notification preferences."""
        prefs = await self.get_preferences(user_id)
        for key, value in kwargs.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        return prefs
    
    async def _send_via_channel(
        self,
        notification: Notification,
        channel: NotificationChannel,
        prefs: NotificationPreferences
    ):
        """Send notification via a specific channel."""
        if channel == NotificationChannel.IN_APP:
            # Already handled in main send method
            pass
        
        elif channel == NotificationChannel.WEB_PUSH:
            if prefs.push_enabled:
                await self._send_web_push(notification)
        
        elif channel == NotificationChannel.EMAIL:
            if prefs.email_enabled:
                await self._send_email(notification)
        
        elif channel == NotificationChannel.SMS:
            if prefs.sms_enabled:
                await self._send_sms(notification)
        
        elif channel == NotificationChannel.WHATSAPP:
            if prefs.whatsapp_enabled:
                await self._send_whatsapp(notification)
    
    async def _send_web_push(self, notification: Notification):
        """Send web push notification."""
        subscription = self._push_subscriptions.get(notification.user_id)
        if not subscription:
            return
        
        # In production: use pywebpush library
        logger.info(f"Would send web push to {notification.user_id}: {notification.title}")
    
    async def _send_email(self, notification: Notification):
        """Send email notification."""
        # Use email service
        logger.info(f"Would send email to {notification.user_id}: {notification.title}")
    
    async def _send_sms(self, notification: Notification):
        """Send SMS notification."""
        logger.info(f"Would send SMS to {notification.user_id}: {notification.title}")
    
    async def _send_whatsapp(self, notification: Notification):
        """Send WhatsApp notification."""
        logger.info(f"Would send WhatsApp to {notification.user_id}: {notification.title}")
    
    def _is_quiet_hours(self, prefs: NotificationPreferences) -> bool:
        """Check if current time is within quiet hours."""
        if prefs.quiet_hours_start is None or prefs.quiet_hours_end is None:
            return False
        
        current_hour = datetime.now().hour
        start = prefs.quiet_hours_start
        end = prefs.quiet_hours_end
        
        if start <= end:
            return start <= current_hour < end
        else:
            # Spans midnight
            return current_hour >= start or current_hour < end


# Singleton instance
_notifications_service: Optional[NotificationsService] = None


def get_notifications_service() -> NotificationsService:
    """Get notifications service singleton."""
    global _notifications_service
    if _notifications_service is None:
        _notifications_service = NotificationsService()
    return _notifications_service
