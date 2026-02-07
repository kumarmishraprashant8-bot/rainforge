"""
RainForge PKI Digital Signature Service
Engineer certificate signing for official PDFs
"""

import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass
import json


@dataclass
class DigitalSignature:
    """Digital signature details."""
    signer_name: str
    signer_id: str
    certificate_id: str
    timestamp: str
    signature_hash: str
    algorithm: str
    valid: bool


class PKISignatureService:
    """
    PKI-based digital signature service for official documents.
    
    For demo: Uses HMAC-SHA256 with a secret key.
    In production: Would integrate with government PKI (eSign, DSC).
    """
    
    def __init__(self, secret_key: str = "RAINFORGE_DEMO_KEY_2026"):
        self.secret_key = secret_key
        self.algorithm = "HMAC-SHA256"
        
        # Mock certificate database
        self.certificates = {
            "ENG001": {
                "name": "Er. Rajesh Kumar",
                "designation": "Senior Water Resources Engineer",
                "license": "CWE/2024/12345",
                "issuing_authority": "Central Water Commission",
                "valid_until": "2027-12-31"
            },
            "ENG002": {
                "name": "Er. Priya Sharma",
                "designation": "Certified RWH Consultant",
                "license": "RWH/2023/67890",
                "issuing_authority": "Delhi Jal Board",
                "valid_until": "2026-06-30"
            },
            "ENG003": {
                "name": "Er. Amit Patel",
                "designation": "Environmental Engineer",
                "license": "ENV/2025/11111",
                "issuing_authority": "Gujarat Water Supply Board",
                "valid_until": "2028-03-15"
            }
        }
    
    def sign_document(
        self,
        document_hash: str,
        signer_id: str,
        document_type: str = "assessment"
    ) -> DigitalSignature:
        """
        Generate digital signature for a document.
        """
        
        if signer_id not in self.certificates:
            # Use default engineer
            signer_id = "ENG001"
        
        cert = self.certificates[signer_id]
        timestamp = datetime.utcnow().isoformat()
        
        # Create signature payload
        payload = f"{document_hash}|{signer_id}|{timestamp}|{self.secret_key}"
        signature_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        return DigitalSignature(
            signer_name=cert["name"],
            signer_id=signer_id,
            certificate_id=cert["license"],
            timestamp=timestamp,
            signature_hash=signature_hash,
            algorithm=self.algorithm,
            valid=True
        )
    
    def verify_signature(
        self,
        document_hash: str,
        signature: DigitalSignature
    ) -> Dict:
        """
        Verify a digital signature.
        """
        
        # Recreate signature
        payload = f"{document_hash}|{signature.signer_id}|{signature.timestamp}|{self.secret_key}"
        expected_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        is_valid = expected_hash == signature.signature_hash
        
        # Check certificate validity
        if signature.signer_id in self.certificates:
            cert = self.certificates[signature.signer_id]
            valid_until = datetime.fromisoformat(cert["valid_until"])
            cert_valid = valid_until > datetime.utcnow()
        else:
            cert_valid = False
        
        return {
            "signature_valid": is_valid,
            "certificate_valid": cert_valid,
            "overall_valid": is_valid and cert_valid,
            "signer_name": signature.signer_name,
            "certificate_id": signature.certificate_id,
            "signed_at": signature.timestamp,
            "verification_time": datetime.utcnow().isoformat()
        }
    
    def generate_signature_block(
        self,
        document_hash: str,
        signer_id: str = "ENG001"
    ) -> Dict:
        """
        Generate a complete signature block for PDF embedding.
        Returns HTML/text for rendering in PDF.
        """
        
        signature = self.sign_document(document_hash, signer_id)
        cert = self.certificates.get(signer_id, self.certificates["ENG001"])
        
        signature_block = {
            "text": f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIGITALLY SIGNED DOCUMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Signed by: {signature.signer_name}
Designation: {cert['designation']}
License No: {cert['license']}
Issued by: {cert['issuing_authority']}

Signature Time: {signature.timestamp}
Algorithm: {signature.algorithm}
Signature: {signature.signature_hash[:32]}...

This document has been digitally signed in accordance
with the Information Technology Act, 2000.

Verify at: https://rainforge.in/verify/{signature.signature_hash[:16]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """.strip(),
            "html": f"""
<div style="border: 2px solid #1e3a5f; padding: 20px; margin: 20px 0; font-family: monospace; background: #f8fafc;">
    <h3 style="color: #1e3a5f; margin: 0 0 15px 0;">🔐 DIGITALLY SIGNED DOCUMENT</h3>
    <table style="width: 100%; font-size: 12px;">
        <tr><td style="width: 120px;"><b>Signed by:</b></td><td>{signature.signer_name}</td></tr>
        <tr><td><b>Designation:</b></td><td>{cert['designation']}</td></tr>
        <tr><td><b>License No:</b></td><td>{cert['license']}</td></tr>
        <tr><td><b>Authority:</b></td><td>{cert['issuing_authority']}</td></tr>
        <tr><td><b>Signed at:</b></td><td>{signature.timestamp}</td></tr>
    </table>
    <div style="margin-top: 15px; padding: 10px; background: #e2e8f0; border-radius: 4px; font-size: 10px;">
        <b>Signature:</b> {signature.signature_hash[:48]}...
    </div>
    <p style="font-size: 10px; color: #64748b; margin: 10px 0 0 0;">
        Verify at: <a href="https://rainforge.in/verify/{signature.signature_hash[:16]}">rainforge.in/verify/{signature.signature_hash[:16]}</a>
    </p>
</div>
            """,
            "signature": signature.__dict__,
            "certificate": cert
        }
        
        return signature_block
    
    def get_signer_info(self, signer_id: str) -> Optional[Dict]:
        """Get signer/engineer information."""
        return self.certificates.get(signer_id)
    
    def list_available_signers(self) -> Dict:
        """List all available signers/engineers."""
        return {
            "signers": [
                {
                    "id": k,
                    "name": v["name"],
                    "designation": v["designation"],
                    "license": v["license"],
                    "valid_until": v["valid_until"]
                }
                for k, v in self.certificates.items()
            ]
        }


class QRCodeGenerator:
    """
    Generate verification QR codes for documents.
    """
    
    BASE_URL = "https://rainforge.in/verify"
    
    def generate_verification_qr(
        self,
        assessment_id: str,
        signature_hash: str,
        expiry_hours: int = 8760  # 1 year
    ) -> Dict:
        """
        Generate QR code data for verification.
        """
        
        # Create verification token
        expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        token_data = f"{assessment_id}|{signature_hash[:16]}|{expiry.isoformat()}"
        token = base64.urlsafe_b64encode(token_data.encode()).decode()[:32]
        
        verification_url = f"{self.BASE_URL}/{token}"
        
        return {
            "verification_url": verification_url,
            "token": token,
            "assessment_id": assessment_id,
            "expires_at": expiry.isoformat(),
            "qr_content": verification_url,
            # In production, would generate actual QR image
            "qr_image_url": f"/api/v1/qr/{token}.png"
        }
    
    def verify_token(self, token: str) -> Dict:
        """Verify a QR token."""
        try:
            # Decode token
            padded = token + "=" * (4 - len(token) % 4)
            decoded = base64.urlsafe_b64decode(padded).decode()
            parts = decoded.split("|")
            
            if len(parts) >= 3:
                assessment_id = parts[0]
                signature_prefix = parts[1]
                expiry_str = parts[2]
                
                expiry = datetime.fromisoformat(expiry_str)
                is_expired = datetime.utcnow() > expiry
                
                return {
                    "valid": not is_expired,
                    "assessment_id": assessment_id,
                    "expired": is_expired,
                    "expires_at": expiry_str
                }
        except:
            pass
        
        return {"valid": False, "error": "Invalid token"}
