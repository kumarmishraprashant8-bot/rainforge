"""
Push Notification Service
Web Push notifications for maintenance alerts, bid updates, and weather warnings.
"""
import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of push notifications."""
    MAINTENANCE_ALERT = "maintenance_alert"
    BID_UPDATE = "bid_update"
    PAYMENT_STATUS = "payment_status"
    WEATHER_WARNING = "weather_warning"
    SYSTEM_UPDATE = "system_update"
    CARBON_CREDIT = "carbon_credit"
    COMMUNITY = "community"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class PushSubscription:
    """User's push notification subscription."""
    subscription_id: str
    user_id: str
    endpoint: str
    p256dh_key: str
    auth_key: str
    user_agent: str
    created_at: datetime
    last_used: Optional[datetime] = None
    enabled: bool = True
    preferences: Dict[str, bool] = field(default_factory=lambda: {
        "maintenance_alert": True,
        "bid_update": True,
        "payment_status": True,
        "weather_warning": True,
        "system_update": True,
        "carbon_credit": True,
        "community": True
    })


@dataclass
class PushNotification:
    """A push notification message."""
    notification_id: str
    user_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    body: str
    icon: Optional[str]
    url: Optional[str]
    data: Dict[str, Any]
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered: bool = False
    clicked: bool = False
    dismissed: bool = False


class PushNotificationService:
    """
    Web Push notification service.
    
    Features:
    - Subscription management
    - Notification preferences
    - Delivery tracking
    - Batch notifications
    - Priority-based delivery
    """
    
    # VAPID keys would be loaded from environment in production
    VAPID_PUBLIC_KEY = "BEl62iUYgUivxIkv69yViEuiBYlP6TVjKz3v9GRE8nCjWP8FqPWP5xbT7M7z4LYN6YKG9p"
    VAPID_PRIVATE_KEY = "mock_private_key"
    VAPID_CLAIMS = {
        "sub": "mailto:notifications@rainforge.app"
    }
    
    # Icons for notification types
    ICONS = {
        NotificationType.MAINTENANCE_ALERT: "/icons/maintenance.png",
        NotificationType.BID_UPDATE: "/icons/bid.png",
        NotificationType.PAYMENT_STATUS: "/icons/payment.png",
        NotificationType.WEATHER_WARNING: "/icons/weather.png",
        NotificationType.SYSTEM_UPDATE: "/icons/system.png",
        NotificationType.CARBON_CREDIT: "/icons/carbon.png",
        NotificationType.COMMUNITY: "/icons/community.png"
    }
    
    def __init__(self):
        self._subscriptions: Dict[str, PushSubscription] = {}
        self._notifications: Dict[str, PushNotification] = {}
        self._user_subscriptions: Dict[str, List[str]] = {}  # user_id -> [subscription_ids]
        
    def subscribe(
        self,
        user_id: str,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
        user_agent: str = ""
    ) -> PushSubscription:
        """Register a new push subscription for a user."""
        # Generate subscription ID from endpoint hash
        subscription_id = hashlib.sha256(endpoint.encode()).hexdigest()[:16]
        
        subscription = PushSubscription(
            subscription_id=subscription_id,
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh_key,
            auth_key=auth_key,
            user_agent=user_agent,
            created_at=datetime.now()
        )
        
        self._subscriptions[subscription_id] = subscription
        
        # Track by user
        if user_id not in self._user_subscriptions:
            self._user_subscriptions[user_id] = []
        if subscription_id not in self._user_subscriptions[user_id]:
            self._user_subscriptions[user_id].append(subscription_id)
        
        logger.info(f"New push subscription for user {user_id}: {subscription_id}")
        
        return subscription
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a push subscription."""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        # Remove from user mapping
        user_id = subscription.user_id
        if user_id in self._user_subscriptions:
            self._user_subscriptions[user_id] = [
                s for s in self._user_subscriptions[user_id] if s != subscription_id
            ]
        
        del self._subscriptions[subscription_id]
        logger.info(f"Removed subscription {subscription_id}")
        
        return True
    
    def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, bool]
    ) -> List[PushSubscription]:
        """Update notification preferences for all user's subscriptions."""
        sub_ids = self._user_subscriptions.get(user_id, [])
        updated = []
        
        for sub_id in sub_ids:
            subscription = self._subscriptions.get(sub_id)
            if subscription:
                subscription.preferences.update(preferences)
                updated.append(subscription)
        
        return updated
    
    def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        body: str,
        url: Optional[str] = None,
        data: Optional[Dict] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> Optional[PushNotification]:
        """Send a push notification to a user."""
        sub_ids = self._user_subscriptions.get(user_id, [])
        if not sub_ids:
            logger.warning(f"No subscriptions found for user {user_id}")
            return None
        
        # Check preferences
        valid_subs = []
        for sub_id in sub_ids:
            sub = self._subscriptions.get(sub_id)
            if sub and sub.enabled:
                if sub.preferences.get(notification_type.value, True):
                    valid_subs.append(sub)
        
        if not valid_subs:
            logger.info(f"User {user_id} has disabled {notification_type.value} notifications")
            return None
        
        # Create notification record
        notification_id = f"notif_{uuid.uuid4().hex[:8]}"
        
        notification = PushNotification(
            notification_id=notification_id,
            user_id=user_id,
            notification_type=notification_type,
            priority=priority,
            title=title,
            body=body,
            icon=self.ICONS.get(notification_type),
            url=url,
            data=data or {},
            created_at=datetime.now()
        )
        
        # Send to all valid subscriptions (mock)
        for sub in valid_subs:
            self._send_to_endpoint(sub, notification)
            sub.last_used = datetime.now()
        
        notification.sent_at = datetime.now()
        notification.delivered = True  # Mock - assume delivery
        
        self._notifications[notification_id] = notification
        
        logger.info(f"Sent notification {notification_id} to user {user_id}: {title}")
        
        return notification
    
    def _send_to_endpoint(self, subscription: PushSubscription, notification: PushNotification):
        """
        Send notification to push endpoint.
        This is a mock implementation - real implementation would use pywebpush.
        """
        payload = {
            "title": notification.title,
            "body": notification.body,
            "icon": notification.icon,
            "url": notification.url,
            "data": {
                "notification_id": notification.notification_id,
                "type": notification.notification_type.value,
                **notification.data
            },
            "tag": notification.notification_type.value,
            "requireInteraction": notification.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT],
            "timestamp": notification.created_at.timestamp() * 1000
        }
        
        # In production, would use:
        # webpush(
        #     subscription_info={
        #         "endpoint": subscription.endpoint,
        #         "keys": {
        #             "p256dh": subscription.p256dh_key,
        #             "auth": subscription.auth_key
        #         }
        #     },
        #     data=json.dumps(payload),
        #     vapid_private_key=self.VAPID_PRIVATE_KEY,
        #     vapid_claims=self.VAPID_CLAIMS
        # )
        
        logger.debug(f"Mock push to {subscription.endpoint[:50]}...")
    
    def send_maintenance_alert(
        self,
        user_id: str,
        site_id: str,
        component: str,
        severity: str,
        message: str
    ) -> Optional[PushNotification]:
        """Send a maintenance alert notification."""
        emoji = "🔴" if severity == "critical" else "🟡" if severity == "warning" else "ℹ️"
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.MAINTENANCE_ALERT,
            title=f"{emoji} Maintenance Alert: {component.title()}",
            body=message,
            url=f"/monitoring/{site_id}",
            data={
                "site_id": site_id,
                "component": component,
                "severity": severity
            },
            priority=NotificationPriority.HIGH if severity == "critical" else NotificationPriority.NORMAL
        )
    
    def send_bid_update(
        self,
        user_id: str,
        job_id: str,
        bid_id: str,
        update_type: str,  # new_bid, outbid, bid_won, bid_lost
        message: str
    ) -> Optional[PushNotification]:
        """Send a bid-related notification."""
        titles = {
            "new_bid": "📥 New Bid Received",
            "outbid": "⚠️ You've Been Outbid",
            "bid_won": "🎉 Your Bid Won!",
            "bid_lost": "😔 Bid Not Selected"
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.BID_UPDATE,
            title=titles.get(update_type, "Bid Update"),
            body=message,
            url=f"/marketplace/jobs/{job_id}",
            data={
                "job_id": job_id,
                "bid_id": bid_id,
                "update_type": update_type
            },
            priority=NotificationPriority.HIGH if update_type == "bid_won" else NotificationPriority.NORMAL
        )
    
    def send_payment_notification(
        self,
        user_id: str,
        payment_id: str,
        status: str,  # milestone_released, escrow_created, payment_received
        amount_inr: float
    ) -> Optional[PushNotification]:
        """Send a payment status notification."""
        messages = {
            "milestone_released": f"Milestone payment of ₹{amount_inr:,.0f} released!",
            "escrow_created": f"Escrow of ₹{amount_inr:,.0f} created for your job",
            "payment_received": f"You received ₹{amount_inr:,.0f}"
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.PAYMENT_STATUS,
            title="💰 Payment Update",
            body=messages.get(status, f"Payment status: {status}"),
            url=f"/payments/{payment_id}",
            data={
                "payment_id": payment_id,
                "status": status,
                "amount_inr": amount_inr
            },
            priority=NotificationPriority.HIGH
        )
    
    def send_weather_warning(
        self,
        user_ids: List[str],
        location: str,
        warning_type: str,
        message: str
    ) -> int:
        """Send weather warning to multiple users (bulk)."""
        sent_count = 0
        
        for user_id in user_ids:
            result = self.send_notification(
                user_id=user_id,
                notification_type=NotificationType.WEATHER_WARNING,
                title=f"🌧️ Weather Alert: {location}",
                body=message,
                url="/monitoring",
                data={
                    "location": location,
                    "warning_type": warning_type
                },
                priority=NotificationPriority.URGENT
            )
            if result:
                sent_count += 1
        
        return sent_count
    
    def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Dict]:
        """Get notification history for a user."""
        user_notifs = [
            n for n in self._notifications.values()
            if n.user_id == user_id
        ]
        
        if unread_only:
            user_notifs = [n for n in user_notifs if not n.clicked and not n.dismissed]
        
        # Sort by created_at descending
        user_notifs.sort(key=lambda n: n.created_at, reverse=True)
        
        return [
            {
                "notification_id": n.notification_id,
                "type": n.notification_type.value,
                "priority": n.priority.value,
                "title": n.title,
                "body": n.body,
                "url": n.url,
                "created_at": n.created_at.isoformat(),
                "clicked": n.clicked,
                "dismissed": n.dismissed
            }
            for n in user_notifs[:limit]
        ]
    
    def mark_as_clicked(self, notification_id: str) -> bool:
        """Mark a notification as clicked."""
        notification = self._notifications.get(notification_id)
        if notification:
            notification.clicked = True
            return True
        return False
    
    def mark_as_dismissed(self, notification_id: str) -> bool:
        """Mark a notification as dismissed."""
        notification = self._notifications.get(notification_id)
        if notification:
            notification.dismissed = True
            return True
        return False
    
    def get_vapid_public_key(self) -> str:
        """Get the VAPID public key for client-side subscription."""
        return self.VAPID_PUBLIC_KEY


# Singleton
_service: Optional[PushNotificationService] = None


def get_push_notification_service() -> PushNotificationService:
    """Get or create the push notification service singleton."""
    global _service
    if _service is None:
        _service = PushNotificationService()
    return _service
