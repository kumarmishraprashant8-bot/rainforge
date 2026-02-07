from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import logging

logger = logging.getLogger(__name__)

class PKIService:
    """
    Public Key Infrastructure Service for IoT Devices.
    Generates unique client certificates for mTLS authentication.
    """
    def generate_device_cert(self, device_id: str) -> dict:
        try:
            # Generate Private Key
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Create a self-signed cert (In real govt infra, this would be signed by Root CA)
            subject = issuer = x509.Name([
                x509.NameAttribute(x509.NameOID.COMMON_NAME, f"rainforge-device-{device_id}"),
                x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "RainForge Govt Platform"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                # Valid for 1 year
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True,
            ).sign(key, hashes.SHA256())

            # Serialize to PEM
            key_pem = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            cert_pem = cert.public_bytes(serialization.Encoding.PEM)
            
            return {
                "device_id": device_id,
                "cert_pem": cert_pem.decode(),
                "key_pem": key_pem.decode(),
                "expires": (datetime.datetime.utcnow() + datetime.timedelta(days=365)).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate cert for {device_id}: {e}")
            raise e

# Singleton
pki_service = PKIService()

def get_pki_service():
    return pki_service
