"""
QR Code Generator
Generate QR codes for projects, sensors, and certificates
"""
import io
import base64
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Try importing qrcode library
try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer
    from qrcode.image.styles.colormasks import RadialGradiantColorMask
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class QRCodeData:
    """QR Code result."""
    data_url: str  # Base64 data URL for embedding
    raw_bytes: bytes  # PNG bytes
    content: str  # The encoded content


class QRGenerator:
    """
    Generate QR codes for various RainForge entities.
    
    Use cases:
    - Project identification
    - Sensor pairing
    - Certificate verification
    - Installation tracking
    - Payment links
    """
    
    BASE_URL = "https://rainforge.gov.in"
    
    def __init__(self):
        self.qr_available = QR_AVAILABLE and PIL_AVAILABLE
    
    def generate_project_qr(
        self,
        project_id: int,
        include_logo: bool = True,
        style: str = "default"
    ) -> QRCodeData:
        """Generate QR code for project."""
        url = f"{self.BASE_URL}/project/{project_id}"
        return self._generate(url, style=style)
    
    def generate_sensor_qr(
        self,
        sensor_id: str,
        project_id: int
    ) -> QRCodeData:
        """Generate QR code for sensor pairing."""
        # JSON payload for sensor setup
        import json
        payload = json.dumps({
            "type": "sensor_pair",
            "sensor_id": sensor_id,
            "project_id": project_id,
            "app": "rainforge"
        })
        return self._generate(payload, style="rounded")
    
    def generate_certificate_qr(
        self,
        certificate_number: str
    ) -> QRCodeData:
        """Generate QR code for certificate verification."""
        url = f"{self.BASE_URL}/verify/{certificate_number}"
        return self._generate(url, style="default")
    
    def generate_payment_qr(
        self,
        upi_id: str,
        amount: float,
        project_id: int,
        note: str = "RainForge Payment"
    ) -> QRCodeData:
        """Generate UPI payment QR code."""
        # UPI deep link format
        upi_url = f"upi://pay?pa={upi_id}&pn=RainForge&am={amount:.2f}&tn={note}&tr=RF{project_id}"
        return self._generate(upi_url, style="default")
    
    def generate_installer_qr(
        self,
        installer_id: str
    ) -> QRCodeData:
        """Generate QR code for installer profile."""
        url = f"{self.BASE_URL}/installer/{installer_id}"
        return self._generate(url, style="rounded")
    
    def generate_assessment_qr(
        self,
        assessment_id: int
    ) -> QRCodeData:
        """Generate QR code for assessment report."""
        url = f"{self.BASE_URL}/assessment/{assessment_id}/report"
        return self._generate(url, style="default")
    
    def generate_custom_qr(
        self,
        content: str,
        style: str = "default"
    ) -> QRCodeData:
        """Generate custom QR code with any content."""
        return self._generate(content, style=style)
    
    def _generate(
        self,
        content: str,
        style: str = "default",
        size: int = 10,
        border: int = 2
    ) -> QRCodeData:
        """Generate QR code with specified style."""
        if not self.qr_available:
            return self._generate_fallback(content)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=border,
        )
        qr.add_data(content)
        qr.make(fit=True)
        
        # Apply style
        if style == "rounded":
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer()
            )
        elif style == "circle":
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=CircleModuleDrawer()
            )
        elif style == "gradient":
            img = qr.make_image(
                image_factory=StyledPilImage,
                color_mask=RadialGradiantColorMask(
                    center_color=(14, 165, 233),  # Primary blue
                    edge_color=(124, 58, 237)  # Purple
                )
            )
        else:
            img = qr.make_image(fill_color="#0ea5e9", back_color="white")
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        raw_bytes = buffer.getvalue()
        
        # Create data URL
        b64 = base64.b64encode(raw_bytes).decode()
        data_url = f"data:image/png;base64,{b64}"
        
        return QRCodeData(
            data_url=data_url,
            raw_bytes=raw_bytes,
            content=content
        )
    
    def _generate_fallback(self, content: str) -> QRCodeData:
        """Fallback when qrcode library not available."""
        # Use a simple SVG placeholder
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <rect width="100" height="100" fill="#f1f5f9"/>
            <text x="50" y="45" text-anchor="middle" font-size="10" fill="#64748b">QR Code</text>
            <text x="50" y="60" text-anchor="middle" font-size="8" fill="#94a3b8">(Install qrcode)</text>
        </svg>'''
        
        raw_bytes = svg.encode()
        b64 = base64.b64encode(raw_bytes).decode()
        
        return QRCodeData(
            data_url=f"data:image/svg+xml;base64,{b64}",
            raw_bytes=raw_bytes,
            content=content
        )
    
    def generate_batch(
        self,
        items: list,
        item_type: str
    ) -> list:
        """Generate QR codes for multiple items."""
        results = []
        
        for item in items:
            if item_type == "project":
                qr = self.generate_project_qr(item["id"])
            elif item_type == "sensor":
                qr = self.generate_sensor_qr(item["sensor_id"], item["project_id"])
            elif item_type == "certificate":
                qr = self.generate_certificate_qr(item["certificate_number"])
            else:
                qr = self.generate_custom_qr(str(item))
            
            results.append({
                "item": item,
                "qr": qr.data_url
            })
        
        return results


# Singleton
_qr_generator: Optional[QRGenerator] = None

def get_qr_generator() -> QRGenerator:
    global _qr_generator
    if _qr_generator is None:
        _qr_generator = QRGenerator()
    return _qr_generator
