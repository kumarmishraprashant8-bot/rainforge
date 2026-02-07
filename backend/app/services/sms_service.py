"""
SMS Notification Service
Supports: Twilio, MSG91 (India), AWS SNS
"""
import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import base64

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSProvider(str, Enum):
    TWILIO = "twilio"
    MSG91 = "msg91"
    AWS_SNS = "aws_sns"


@dataclass
class SMSMessage:
    """SMS message structure."""
    to: str
    body: str
    sender_id: str = "RAINFRG"


class SMSService:
    """
    Multi-provider SMS service.
    
    Recommended for India: MSG91 (best delivery rates)
    International: Twilio
    """
    
    # API Endpoints
    TWILIO_API = "https://api.twilio.com/2010-04-01"
    MSG91_API = "https://control.msg91.com/api/v5"
    
    def __init__(self, provider: SMSProvider = SMSProvider.MSG91):
        self.provider = provider
        
        # Twilio credentials
        self.twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.twilio_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        
        # MSG91 credentials
        self.msg91_key = getattr(settings, 'MSG91_AUTH_KEY', None)
        self.msg91_sender = getattr(settings, 'MSG91_SENDER_ID', 'RAINFRG')
        self.msg91_route = getattr(settings, 'MSG91_ROUTE', '4')  # Transactional
        
        self._enabled = self._check_enabled()
        
        if not self._enabled:
            logger.warning(f"SMS ({provider}) not configured, will simulate")
    
    def _check_enabled(self) -> bool:
        """Check if provider is configured."""
        if self.provider == SMSProvider.TWILIO:
            return bool(self.twilio_sid and self.twilio_token)
        elif self.provider == SMSProvider.MSG91:
            return bool(self.msg91_key)
        return False
    
    async def send_sms(
        self,
        to_phone: str,
        message: str,
        sender_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS via configured provider."""
        phone = self._format_phone(to_phone)
        
        if not self._enabled:
            return self._simulate_send(phone, message)
        
        if self.provider == SMSProvider.TWILIO:
            return await self._send_twilio(phone, message)
        elif self.provider == SMSProvider.MSG91:
            return await self._send_msg91(phone, message, sender_id)
        else:
            return {"success": False, "error": "Unknown provider"}
    
    async def _send_twilio(self, to: str, message: str) -> Dict:
        """Send via Twilio."""
        try:
            auth = base64.b64encode(
                f"{self.twilio_sid}:{self.twilio_token}".encode()
            ).decode()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.TWILIO_API}/Accounts/{self.twilio_sid}/Messages.json",
                    headers={
                        "Authorization": f"Basic {auth}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={
                        "To": f"+{to}",
                        "From": self.twilio_phone,
                        "Body": message
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "success": True,
                    "message_id": result.get("sid"),
                    "status": result.get("status"),
                    "provider": "twilio"
                }
                
        except Exception as e:
            logger.error(f"Twilio send failed: {e}")
            return {"success": False, "error": str(e), "provider": "twilio"}
    
    async def _send_msg91(
        self, 
        to: str, 
        message: str, 
        sender_id: Optional[str] = None
    ) -> Dict:
        """Send via MSG91 (India)."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.MSG91_API}/flow/",
                    headers={
                        "authkey": self.msg91_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "sender": sender_id or self.msg91_sender,
                        "route": self.msg91_route,
                        "country": "91",
                        "sms": [
                            {
                                "message": message,
                                "to": [to.lstrip("91")]
                            }
                        ]
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "success": result.get("type") == "success",
                    "message_id": result.get("request_id"),
                    "provider": "msg91"
                }
                
        except Exception as e:
            logger.error(f"MSG91 send failed: {e}")
            return {"success": False, "error": str(e), "provider": "msg91"}
    
    # ==================== CONVENIENCE METHODS ====================
    
    async def send_otp(self, phone: str, otp: str) -> Dict:
        """Send OTP for verification."""
        message = f"Your RainForge verification code is {otp}. Valid for 10 minutes. Do not share."
        return await self.send_sms(phone, message)
    
    async def send_tank_alert(
        self,
        phone: str,
        tank_level: float,
        project_name: str
    ) -> Dict:
        """Send tank level alert."""
        status = "LOW" if tank_level < 20 else "FULL" if tank_level > 90 else "OK"
        message = f"RainForge Alert: {project_name} tank at {tank_level:.0f}% ({status}). Check app for details."
        return await self.send_sms(phone, message)
    
    async def send_payment_alert(
        self,
        phone: str,
        amount: float,
        reference: str
    ) -> Dict:
        """Send payment notification."""
        message = f"RainForge: Payment of Rs.{amount:,.0f} received. Ref: {reference}. Thank you!"
        return await self.send_sms(phone, message)
    
    async def send_verification_reminder(
        self,
        phone: str,
        job_id: str,
        deadline: str
    ) -> Dict:
        """Remind installer to submit verification."""
        message = f"RainForge: Job {job_id} verification due by {deadline}. Please submit photos in app."
        return await self.send_sms(phone, message)
    
    async def send_bid_notification(
        self,
        phone: str,
        job_id: str,
        status: str
    ) -> Dict:
        """Notify about bid status."""
        message = f"RainForge: Your bid for Job {job_id} has been {status}. Check app for details."
        return await self.send_sms(phone, message)
    
    # ==================== HELPERS ====================
    
    def _format_phone(self, phone: str) -> str:
        """Format phone for SMS."""
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) == 10:
            return f"91{digits}"
        elif digits.startswith("0"):
            return f"91{digits[1:]}"
        
        return digits
    
    def _simulate_send(self, phone: str, message: str) -> Dict:
        """Simulate SMS for development."""
        logger.info(f"[SIMULATED] SMS to {phone}: {message[:50]}...")
        return {
            "success": True,
            "simulated": True,
            "phone": phone,
            "message_preview": message[:50],
            "message_id": f"sim_{datetime.now().timestamp()}"
        }
    
    def is_enabled(self) -> bool:
        return self._enabled


# ==================== BULK SMS ====================

class BulkSMSService:
    """Send SMS to multiple recipients."""
    
    def __init__(self, sms_service: SMSService):
        self.sms = sms_service
    
    async def send_broadcast(
        self,
        phones: list[str],
        message: str,
        batch_size: int = 50
    ) -> Dict:
        """Send same message to multiple recipients."""
        import asyncio
        
        results = {"success": 0, "failed": 0, "errors": []}
        
        for i in range(0, len(phones), batch_size):
            batch = phones[i:i + batch_size]
            tasks = [self.sms.send_sms(phone, message) for phone in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for phone, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["errors"].append(str(result))
                elif result.get("success"):
                    results["success"] += 1
                else:
                    results["failed"] += 1
            
            # Rate limiting pause
            await asyncio.sleep(1)
        
        return results


# Singleton
_sms_service: Optional[SMSService] = None

def get_sms_service(provider: SMSProvider = SMSProvider.MSG91) -> SMSService:
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService(provider)
    return _sms_service
