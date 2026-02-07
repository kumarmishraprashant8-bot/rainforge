"""
OCR Service for Receipt and Document Processing
Uses: Tesseract (local), Google Vision API, AWS Textract
"""
import httpx
import logging
import base64
import re
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from io import BytesIO

logger = logging.getLogger(__name__)

# Try importing optional dependencies
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Tesseract not available, using cloud OCR only")


@dataclass
class ExtractedReceipt:
    """Parsed receipt data."""
    merchant_name: Optional[str]
    date: Optional[datetime]
    total_amount: Optional[float]
    currency: str
    items: List[Dict[str, Any]]
    raw_text: str
    confidence: float


@dataclass
class ExtractedDocument:
    """Generic document extraction."""
    document_type: str
    fields: Dict[str, Any]
    raw_text: str
    confidence: float


class OCRService:
    """
    Multi-provider OCR service for document processing.
    
    Use cases:
    - Payment receipt verification
    - Invoice processing
    - ID document extraction
    """
    
    def __init__(self):
        self.google_vision_key = None  # Add to settings
        self.aws_textract = None  # Add AWS credentials
    
    async def extract_receipt(
        self,
        image_data: bytes,
        use_cloud: bool = False
    ) -> ExtractedReceipt:
        """
        Extract payment receipt information.
        """
        # Get raw text
        if use_cloud:
            raw_text = await self._ocr_google_vision(image_data)
        else:
            raw_text = self._ocr_tesseract(image_data)
        
        # Parse receipt structure
        return self._parse_receipt(raw_text)
    
    async def extract_text(
        self,
        image_data: bytes,
        language: str = "eng"
    ) -> str:
        """Simple text extraction."""
        if TESSERACT_AVAILABLE:
            return self._ocr_tesseract(image_data, language)
        return await self._ocr_google_vision(image_data)
    
    def _ocr_tesseract(
        self, 
        image_data: bytes, 
        language: str = "eng+hin"
    ) -> str:
        """Local OCR using Tesseract."""
        if not TESSERACT_AVAILABLE:
            return ""
        
        try:
            image = Image.open(BytesIO(image_data))
            
            # Preprocessing for better OCR
            image = image.convert('L')  # Grayscale
            
            # OCR with custom config
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(
                image, 
                lang=language, 
                config=custom_config
            )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""
    
    async def _ocr_google_vision(self, image_data: bytes) -> str:
        """Cloud OCR using Google Vision API."""
        if not self.google_vision_key:
            logger.warning("Google Vision API key not configured")
            return self._ocr_tesseract(image_data) if TESSERACT_AVAILABLE else ""
        
        try:
            image_b64 = base64.b64encode(image_data).decode()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"https://vision.googleapis.com/v1/images:annotate?key={self.google_vision_key}",
                    json={
                        "requests": [{
                            "image": {"content": image_b64},
                            "features": [{"type": "TEXT_DETECTION"}]
                        }]
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                annotations = result.get("responses", [{}])[0]
                full_text = annotations.get("fullTextAnnotation", {})
                return full_text.get("text", "")
                
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {e}")
            return ""
    
    def _parse_receipt(self, raw_text: str) -> ExtractedReceipt:
        """Parse receipt structure from raw text."""
        lines = raw_text.split('\n')
        
        # Extract merchant (usually first non-empty line)
        merchant = None
        for line in lines[:5]:
            if line.strip() and len(line) > 3:
                merchant = line.strip()
                break
        
        # Extract date
        date = self._extract_date(raw_text)
        
        # Extract total amount
        total, currency = self._extract_amount(raw_text)
        
        # Extract line items
        items = self._extract_items(raw_text)
        
        # Calculate confidence based on what we found
        confidence = 0.0
        if merchant:
            confidence += 0.25
        if date:
            confidence += 0.25
        if total:
            confidence += 0.3
        if items:
            confidence += 0.2
        
        return ExtractedReceipt(
            merchant_name=merchant,
            date=date,
            total_amount=total,
            currency=currency,
            items=items,
            raw_text=raw_text,
            confidence=confidence
        )
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from text."""
        # Common date patterns
        patterns = [
            r'(\d{2}[-/]\d{2}[-/]\d{4})',  # DD-MM-YYYY
            r'(\d{4}[-/]\d{2}[-/]\d{2})',  # YYYY-MM-DD
            r'(\d{2}[-/]\d{2}[-/]\d{2})',  # DD-MM-YY
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',  # 12 Jan 2024
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Try different formats
                    for fmt in ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%y', '%d %b %Y', '%d %B %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except:
                    pass
        
        return None
    
    def _extract_amount(self, text: str) -> Tuple[Optional[float], str]:
        """Extract total amount from text."""
        currency = "INR"
        
        # Look for total/grand total patterns
        total_patterns = [
            r'(?:total|grand\s*total|amount|net\s*amount)[:\s]*(?:rs\.?|₹|inr)?\s*([\d,]+\.?\d*)',
            r'(?:rs\.?|₹|inr)\s*([\d,]+\.?\d*)\s*(?:total)?',
            r'([\d,]+\.?\d*)\s*(?:rs\.?|₹)',
        ]
        
        amounts = []
        for pattern in total_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    amounts.append(amount)
                except ValueError:
                    continue
        
        if amounts:
            # Usually the largest amount is the total
            return max(amounts), currency
        
        return None, currency
    
    def _extract_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from receipt."""
        items = []
        lines = text.split('\n')
        
        # Look for patterns like "Item Name  Qty  Price"
        item_pattern = r'^(.+?)\s+(\d+)\s*[xX]?\s*([\d,]+\.?\d*)\s*$'
        
        for line in lines:
            match = re.match(item_pattern, line.strip())
            if match:
                items.append({
                    "name": match.group(1).strip(),
                    "quantity": int(match.group(2)),
                    "price": float(match.group(3).replace(',', ''))
                })
        
        return items
    
    async def verify_payment_receipt(
        self,
        image_data: bytes,
        expected_amount: float,
        tolerance: float = 0.05
    ) -> Dict[str, Any]:
        """
        Verify a payment receipt matches expected amount.
        Used for milestone payment verification.
        """
        receipt = await self.extract_receipt(image_data)
        
        if not receipt.total_amount:
            return {
                "verified": False,
                "reason": "Could not extract amount from receipt",
                "confidence": receipt.confidence,
                "extracted_amount": None
            }
        
        # Check if amount matches within tolerance
        diff = abs(receipt.total_amount - expected_amount)
        diff_percent = diff / expected_amount if expected_amount > 0 else 0
        
        verified = diff_percent <= tolerance
        
        return {
            "verified": verified,
            "expected_amount": expected_amount,
            "extracted_amount": receipt.total_amount,
            "difference": diff,
            "difference_percent": diff_percent * 100,
            "merchant": receipt.merchant_name,
            "date": receipt.date.isoformat() if receipt.date else None,
            "confidence": receipt.confidence,
            "reason": "Amount matches" if verified else f"Amount difference: {diff:.2f}"
        }


# Singleton
_ocr_service: Optional[OCRService] = None

def get_ocr_service() -> OCRService:
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
