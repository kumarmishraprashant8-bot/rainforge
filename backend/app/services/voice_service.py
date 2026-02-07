"""
Voice Alert Service
Twilio Voice API for critical alerts
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try importing Twilio
try:
    from twilio.rest import Client as TwilioClient
    from twilio.twiml.voice_response import VoiceResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


@dataclass
class VoiceCall:
    """Voice call result."""
    call_sid: str
    to_phone: str
    status: str
    duration: Optional[int] = None
    provider: str = "twilio"


class VoiceAlertService:
    """
    Voice call service for critical alerts.
    
    Use cases:
    - Tank critically low (< 10%)
    - Payment failures
    - Security alerts
    - Emergency notifications
    """
    
    def __init__(self):
        from app.core.config import settings
        
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        self.base_url = getattr(settings, 'APP_BASE_URL', 'https://rainforge.gov.in')
        
        self._client = None
        if TWILIO_AVAILABLE and self.account_sid and self.auth_token:
            self._client = TwilioClient(self.account_sid, self.auth_token)
    
    async def make_call(
        self,
        to_phone: str,
        message: str,
        language: str = "en-IN",
        voice: str = "Polly.Aditi"  # Indian English voice
    ) -> Dict[str, Any]:
        """
        Make a voice call with text-to-speech message.
        """
        to_phone = self._format_phone(to_phone)
        
        if not self._client:
            return self._mock_call(to_phone, message)
        
        try:
            # Create TwiML for the call
            twiml = VoiceResponse()
            twiml.say(message, voice=voice, language=language)
            twiml.pause(length=1)
            twiml.say("Press 1 to acknowledge, or 2 to call back.", voice=voice)
            twiml.gather(num_digits=1, timeout=10)
            
            call = self._client.calls.create(
                to=to_phone,
                from_=self.from_number,
                twiml=str(twiml)
            )
            
            logger.info(f"Voice call initiated: {call.sid}")
            
            return {
                "success": True,
                "call_sid": call.sid,
                "to": to_phone,
                "status": call.status,
                "provider": "twilio"
            }
            
        except Exception as e:
            logger.error(f"Voice call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "twilio"
            }
    
    async def tank_critical_alert(
        self,
        to_phone: str,
        project_name: str,
        tank_level: float
    ) -> Dict[str, Any]:
        """Send critical tank level voice alert."""
        message = f"""
        Alert from RainForge.
        Your tank {project_name} is critically low at {tank_level:.0f} percent.
        Please check for leaks or usage issues immediately.
        This is an automated alert.
        """
        
        return await self.make_call(to_phone, message)
    
    async def security_alert(
        self,
        to_phone: str,
        alert_type: str,
        details: str
    ) -> Dict[str, Any]:
        """Send security alert voice call."""
        message = f"""
        Security Alert from RainForge.
        Alert type: {alert_type}.
        {details}.
        Please log in to your dashboard immediately to review.
        """
        
        return await self.make_call(to_phone, message)
    
    async def payment_alert(
        self,
        to_phone: str,
        amount: float,
        status: str
    ) -> Dict[str, Any]:
        """Send payment status voice alert."""
        if status == "failed":
            message = f"""
            RainForge Payment Alert.
            Your payment of {amount:.0f} rupees has failed.
            Please check your payment method and try again.
            """
        else:
            message = f"""
            RainForge Payment Confirmation.
            Your payment of {amount:.0f} rupees has been received.
            Thank you for using RainForge.
            """
        
        return await self.make_call(to_phone, message)
    
    async def verification_reminder(
        self,
        to_phone: str,
        project_name: str,
        days_overdue: int
    ) -> Dict[str, Any]:
        """Send verification reminder voice call."""
        message = f"""
        RainForge Verification Reminder.
        Your project {project_name} verification is {days_overdue} days overdue.
        Please complete verification to continue receiving payments.
        Upload photos through the RainForge app.
        """
        
        return await self.make_call(to_phone, message)
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number for Twilio."""
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) == 10:
            phone = f"+91{phone}"
        elif not phone.startswith('+'):
            phone = f"+{phone}"
        return phone
    
    def _mock_call(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Mock voice call for development."""
        logger.info(f"[MOCK VOICE CALL] To: {to_phone}")
        logger.info(f"[MOCK MESSAGE] {message[:100]}...")
        
        return {
            "success": True,
            "simulated": True,
            "call_sid": f"MOCK_{datetime.now().timestamp()}",
            "to": to_phone,
            "status": "completed",
            "provider": "mock"
        }


# Singleton
_voice_service: Optional[VoiceAlertService] = None

def get_voice_service() -> VoiceAlertService:
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceAlertService()
    return _voice_service
