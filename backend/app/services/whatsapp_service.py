"""
WhatsApp Notification Service
Uses WhatsApp Cloud API (Meta Business API)
Free tier: 1000 conversations/month
"""
import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings

logger = logging.getLogger(__name__)


class MessageTemplate(str, Enum):
    """Pre-approved WhatsApp message templates."""
    VERIFICATION_REMINDER = "verification_reminder"
    PAYMENT_RECEIVED = "payment_received"
    TANK_ALERT = "tank_alert"
    BID_AWARDED = "bid_awarded"
    MAINTENANCE_DUE = "maintenance_due"
    WELCOME = "welcome"


@dataclass
class WhatsAppMessage:
    """WhatsApp message structure."""
    to: str  # Phone number with country code
    template: MessageTemplate
    parameters: Dict[str, str]
    language: str = "en"


class WhatsAppService:
    """
    WhatsApp Cloud API integration for notifications.
    
    Setup:
    1. Create Meta Developer account
    2. Create WhatsApp Business App
    3. Get API credentials
    4. Register message templates
    """
    
    API_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self):
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', None)
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        self.business_id = getattr(settings, 'WHATSAPP_BUSINESS_ID', None)
        self._enabled = bool(self.access_token and self.phone_number_id)
        
        if not self._enabled:
            logger.warning("WhatsApp not configured, notifications will be simulated")
    
    async def send_template_message(
        self,
        to_phone: str,
        template: MessageTemplate,
        parameters: Dict[str, str],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Send a template message.
        Templates must be pre-approved by Meta.
        """
        if not self._enabled:
            return self._simulate_send(to_phone, template, parameters)
        
        # Format phone number
        phone = self._format_phone(to_phone)
        
        # Build template components
        components = []
        if parameters:
            components.append({
                "type": "body",
                "parameters": [
                    {"type": "text", "text": value}
                    for value in parameters.values()
                ]
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "template",
            "template": {
                "name": template.value,
                "language": {"code": language},
                "components": components
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.API_URL}/{self.phone_number_id}/messages",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"WhatsApp sent to {phone}: {template.value}")
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "phone": phone,
                    "template": template.value
                }
                
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_text_message(
        self,
        to_phone: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Send a free-form text message.
        Only works within 24-hour conversation window.
        """
        if not self._enabled:
            return self._simulate_send(to_phone, "text", {"message": text})
        
        phone = self._format_phone(to_phone)
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {"body": text}
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.API_URL}/{self.phone_number_id}/messages",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()
                return {"success": True, "message_id": response.json()["messages"][0]["id"]}
                
        except Exception as e:
            logger.error(f"WhatsApp text send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_media_message(
        self,
        to_phone: str,
        media_url: str,
        media_type: str = "image",
        caption: str = ""
    ) -> Dict[str, Any]:
        """Send image/document via WhatsApp."""
        if not self._enabled:
            return self._simulate_send(to_phone, "media", {"url": media_url})
        
        phone = self._format_phone(to_phone)
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": media_type,
            media_type: {
                "link": media_url,
                "caption": caption
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.API_URL}/{self.phone_number_id}/messages",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()
                return {"success": True, "message_id": response.json()["messages"][0]["id"]}
                
        except Exception as e:
            logger.error(f"WhatsApp media send failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== CONVENIENCE METHODS ====================
    
    async def send_tank_alert(
        self,
        phone: str,
        tank_level: float,
        project_name: str
    ) -> Dict:
        """Send tank level alert."""
        return await self.send_template_message(
            phone,
            MessageTemplate.TANK_ALERT,
            {
                "project_name": project_name,
                "level": f"{tank_level:.0f}%",
                "status": "LOW" if tank_level < 20 else "FULL" if tank_level > 90 else "NORMAL"
            }
        )
    
    async def send_verification_reminder(
        self,
        phone: str,
        installer_name: str,
        job_id: str,
        deadline: str
    ) -> Dict:
        """Send verification reminder to installer."""
        return await self.send_template_message(
            phone,
            MessageTemplate.VERIFICATION_REMINDER,
            {
                "name": installer_name,
                "job_id": job_id,
                "deadline": deadline
            }
        )
    
    async def send_payment_notification(
        self,
        phone: str,
        amount: float,
        reference: str
    ) -> Dict:
        """Send payment received notification."""
        return await self.send_template_message(
            phone,
            MessageTemplate.PAYMENT_RECEIVED,
            {
                "amount": f"₹{amount:,.2f}",
                "reference": reference,
                "date": datetime.now().strftime("%d %b %Y")
            }
        )
    
    async def send_bid_awarded(
        self,
        phone: str,
        installer_name: str,
        job_id: str,
        amount: float
    ) -> Dict:
        """Notify installer of bid award."""
        return await self.send_template_message(
            phone,
            MessageTemplate.BID_AWARDED,
            {
                "name": installer_name,
                "job_id": job_id,
                "amount": f"₹{amount:,.2f}"
            }
        )
    
    # ==================== HELPERS ====================
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number for WhatsApp API."""
        # Remove all non-digits
        digits = ''.join(filter(str.isdigit, phone))
        
        # Add India country code if not present
        if len(digits) == 10:
            return f"91{digits}"
        elif digits.startswith("91") and len(digits) == 12:
            return digits
        elif digits.startswith("+"):
            return digits[1:]
        
        return digits
    
    def _simulate_send(
        self, 
        phone: str, 
        template: Any, 
        params: Dict
    ) -> Dict:
        """Simulate send for development."""
        logger.info(f"[SIMULATED] WhatsApp to {phone}: {template} - {params}")
        return {
            "success": True,
            "simulated": True,
            "phone": phone,
            "template": str(template),
            "params": params,
            "message_id": f"sim_{datetime.now().timestamp()}"
        }
    
    def is_enabled(self) -> bool:
        """Check if WhatsApp is configured."""
        return self._enabled


# Singleton
_whatsapp_service: Optional[WhatsAppService] = None

def get_whatsapp_service() -> WhatsAppService:
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service


# ==================== TEMPLATE DEFINITIONS ====================
# These templates must be created in Meta Business Manager
# and approved before use.

TEMPLATE_DEFINITIONS = {
    "verification_reminder": {
        "name": "verification_reminder",
        "category": "UTILITY",
        "language": "en",
        "components": [
            {
                "type": "BODY",
                "text": "Hi {{1}}, your verification for Job {{2}} is due by {{3}}. Please submit photos via the RainForge app."
            }
        ]
    },
    "payment_received": {
        "name": "payment_received",
        "category": "UTILITY",
        "language": "en",
        "components": [
            {
                "type": "BODY",
                "text": "Payment of {{1}} received. Reference: {{2}}. Date: {{3}}. Thank you for using RainForge!"
            }
        ]
    },
    "tank_alert": {
        "name": "tank_alert",
        "category": "UTILITY",
        "language": "en",
        "components": [
            {
                "type": "BODY",
                "text": "🚰 Tank Alert for {{1}}: Level is {{2}} ({{3}}). Please check your RainForge dashboard."
            }
        ]
    },
    "bid_awarded": {
        "name": "bid_awarded",
        "category": "UTILITY",
        "language": "en",
        "components": [
            {
                "type": "BODY",
                "text": "🎉 Congratulations {{1}}! Your bid for Job {{2}} worth {{3}} has been accepted. Start work within 48 hours."
            }
        ]
    }
}
