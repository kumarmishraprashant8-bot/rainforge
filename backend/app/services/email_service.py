"""
Email Notification Service
Supports: SendGrid, AWS SES, SMTP
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import base64

logger = logging.getLogger(__name__)

# Try importing email libraries
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import ClientError
    SES_AVAILABLE = True
except ImportError:
    SES_AVAILABLE = False


@dataclass
class EmailMessage:
    """Email message structure."""
    to: List[str]
    subject: str
    html_content: str
    text_content: Optional[str] = None
    from_email: str = "noreply@rainforge.gov.in"
    from_name: str = "RainForge"
    attachments: Optional[List[Dict]] = None
    reply_to: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None


class EmailService:
    """
    Multi-provider email service.
    
    Recommended:
    - SendGrid: Easy setup, good deliverability
    - AWS SES: Cheapest, requires AWS account
    """
    
    def __init__(self):
        from app.core.config import settings
        
        self.sendgrid_key = getattr(settings, 'SENDGRID_API_KEY', None)
        self.ses_region = getattr(settings, 'AWS_REGION', 'ap-south-1')
        self.default_from = getattr(settings, 'EMAIL_FROM', 'noreply@rainforge.gov.in')
        
        self._provider = self._detect_provider()
    
    def _detect_provider(self) -> str:
        """Detect available email provider."""
        if self.sendgrid_key and SENDGRID_AVAILABLE:
            return "sendgrid"
        elif SES_AVAILABLE:
            return "ses"
        return "mock"
    
    async def send(self, message: EmailMessage) -> Dict[str, Any]:
        """Send email via configured provider."""
        if self._provider == "sendgrid":
            return await self._send_sendgrid(message)
        elif self._provider == "ses":
            return await self._send_ses(message)
        else:
            return self._mock_send(message)
    
    async def _send_sendgrid(self, message: EmailMessage) -> Dict:
        """Send via SendGrid."""
        try:
            mail = Mail(
                from_email=(message.from_email, message.from_name),
                to_emails=message.to,
                subject=message.subject,
                html_content=message.html_content,
                plain_text_content=message.text_content
            )
            
            # Add attachments
            if message.attachments:
                for att in message.attachments:
                    attachment = Attachment(
                        FileContent(base64.b64encode(att['content']).decode()),
                        FileName(att['filename']),
                        FileType(att.get('type', 'application/octet-stream'))
                    )
                    mail.add_attachment(attachment)
            
            sg = SendGridAPIClient(self.sendgrid_key)
            response = sg.send(mail)
            
            return {
                "success": response.status_code in [200, 202],
                "status_code": response.status_code,
                "message_id": response.headers.get('X-Message-Id'),
                "provider": "sendgrid"
            }
            
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return {"success": False, "error": str(e), "provider": "sendgrid"}
    
    async def _send_ses(self, message: EmailMessage) -> Dict:
        """Send via AWS SES."""
        try:
            client = boto3.client('ses', region_name=self.ses_region)
            
            response = client.send_email(
                Source=f"{message.from_name} <{message.from_email}>",
                Destination={
                    'ToAddresses': message.to,
                    'CcAddresses': message.cc or [],
                    'BccAddresses': message.bcc or []
                },
                Message={
                    'Subject': {'Data': message.subject},
                    'Body': {
                        'Html': {'Data': message.html_content},
                        'Text': {'Data': message.text_content or message.subject}
                    }
                }
            )
            
            return {
                "success": True,
                "message_id": response['MessageId'],
                "provider": "ses"
            }
            
        except ClientError as e:
            logger.error(f"SES send failed: {e}")
            return {"success": False, "error": str(e), "provider": "ses"}
    
    def _mock_send(self, message: EmailMessage) -> Dict:
        """Mock send for development."""
        logger.info(f"[MOCK EMAIL] To: {message.to}, Subject: {message.subject}")
        return {
            "success": True,
            "simulated": True,
            "message_id": f"mock_{datetime.now().timestamp()}",
            "provider": "mock"
        }
    
    # ==================== EMAIL TEMPLATES ====================
    
    async def send_welcome(
        self,
        to_email: str,
        user_name: str
    ) -> Dict:
        """Send welcome email."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #0ea5e9; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌧️ Welcome to RainForge!</h1>
                </div>
                <div class="content">
                    <h2>Hello, {user_name}!</h2>
                    <p>Thank you for joining RainForge - India's smart rainwater harvesting platform.</p>
                    <p>With RainForge, you can:</p>
                    <ul>
                        <li>📊 Assess your rooftop's harvesting potential</li>
                        <li>🛠️ Find verified installers</li>
                        <li>📈 Monitor your water savings</li>
                        <li>🌍 Track your carbon offset</li>
                    </ul>
                    <a href="https://rainforge.gov.in/dashboard" class="button">Go to Dashboard</a>
                    <p>Need help? Reply to this email or visit our help center.</p>
                </div>
                <div class="footer">
                    <p>RainForge - Empowering Sustainable Water Management</p>
                    <p>Jal Shakti Ministry Initiative</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send(EmailMessage(
            to=[to_email],
            subject="Welcome to RainForge! 🌧️",
            html_content=html,
            text_content=f"Welcome to RainForge, {user_name}! Start your water-saving journey today."
        ))
    
    async def send_verification_approved(
        self,
        to_email: str,
        project_name: str,
        approval_date: str
    ) -> Dict:
        """Send verification approval email."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .success {{ background: #10b981; color: white; padding: 20px; text-align: center; border-radius: 10px; }}
                .content {{ padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">
                    <h1>✅ Verification Approved!</h1>
                </div>
                <div class="content">
                    <p>Great news! Your RWH installation has been verified and approved.</p>
                    <p><strong>Project:</strong> {project_name}</p>
                    <p><strong>Approved On:</strong> {approval_date}</p>
                    <p>Your milestone payment will be processed within 48 hours.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send(EmailMessage(
            to=[to_email],
            subject=f"✅ Verification Approved - {project_name}",
            html_content=html
        ))
    
    async def send_payment_receipt(
        self,
        to_email: str,
        amount: float,
        reference: str,
        project_name: str
    ) -> Dict:
        """Send payment receipt email."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .receipt {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 30px; }}
                .amount {{ font-size: 36px; color: #10b981; font-weight: bold; }}
                .details {{ margin: 20px 0; }}
                .row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💰 Payment Receipt</h1>
                <div class="receipt">
                    <p class="amount">₹{amount:,.2f}</p>
                    <div class="details">
                        <div class="row">
                            <span>Reference</span>
                            <strong>{reference}</strong>
                        </div>
                        <div class="row">
                            <span>Project</span>
                            <strong>{project_name}</strong>
                        </div>
                        <div class="row">
                            <span>Date</span>
                            <strong>{datetime.now().strftime('%d %b %Y, %H:%M')}</strong>
                        </div>
                        <div class="row">
                            <span>Status</span>
                            <strong style="color: #10b981;">Completed</strong>
                        </div>
                    </div>
                </div>
                <p style="color: #64748b; font-size: 12px;">This is an auto-generated receipt. Keep for your records.</p>
            </div>
        </body>
        </html>
        """
        
        return await self.send(EmailMessage(
            to=[to_email],
            subject=f"Payment Receipt - ₹{amount:,.2f} - {reference}",
            html_content=html
        ))
    
    async def send_tank_alert(
        self,
        to_email: str,
        project_name: str,
        tank_level: float,
        status: str
    ) -> Dict:
        """Send tank level alert email."""
        color = "#ef4444" if status == "LOW" else "#3b82f6" if status == "FULL" else "#10b981"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert {{ background: {color}; color: white; padding: 20px; text-align: center; border-radius: 10px; }}
                .level {{ font-size: 48px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div class="alert">
                    <h1>🚰 Tank Alert: {status}</h1>
                    <p class="level">{tank_level:.0f}%</p>
                    <p>{project_name}</p>
                </div>
                <p style="margin-top: 20px;">
                    {'Your tank is running low. Consider checking for leaks or scheduling a refill.' if status == 'LOW' else 'Your tank is nearly full. Great water harvesting!' if status == 'FULL' else 'Tank level is normal.'}
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send(EmailMessage(
            to=[to_email],
            subject=f"🚰 Tank Alert: {project_name} - {status} ({tank_level:.0f}%)",
            html_content=html
        ))


# Singleton
_email_service: Optional[EmailService] = None

def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
