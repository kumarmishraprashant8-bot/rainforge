"""
RainForge Fraud Detection Service
Detects anomalies in verification submissions.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import math
import random


@dataclass
class FraudFlag:
    """Individual fraud flag."""
    type: str
    severity: str  # low, medium, high
    details: str
    score: float  # 0-100


@dataclass
class VerificationData:
    """Data submitted for verification."""
    job_id: int
    installer_id: int
    photo_url: str
    photo_hash: str
    geo_lat: float
    geo_lng: float
    expected_lat: float
    expected_lng: float
    timestamp: datetime
    device_id: Optional[str] = None


class FraudDetector:
    """
    Detects fraud in verification submissions using multiple heuristics.
    """
    
    # In-memory storage for photo hashes (would be DB in production)
    _photo_hashes: Dict[str, List[Dict]] = {}  # hash -> list of {job_id, installer_id, timestamp}
    _installer_submissions: Dict[int, List[Dict]] = {}  # installer_id -> list of submissions
    
    # Thresholds
    MAX_GEO_DISTANCE_M = 100  # Max acceptable distance from expected location
    MIN_SUBMISSION_INTERVAL_MINS = 30  # Minimum time between submissions
    SUSPICIOUS_SPEED_KMH = 100  # Max realistic travel speed
    
    @classmethod
    def calculate_photo_hash(cls, photo_data: bytes) -> str:
        """Calculate SHA256 hash of photo data."""
        return hashlib.sha256(photo_data).hexdigest()
    
    @classmethod
    def haversine_distance(cls, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in meters between two coordinates."""
        R = 6371000  # Earth radius in meters
        
        lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    @classmethod
    def check_photo_reuse(cls, verification: VerificationData) -> Optional[FraudFlag]:
        """Check if photo hash has been used before."""
        photo_hash = verification.photo_hash
        
        if photo_hash in cls._photo_hashes:
            previous = cls._photo_hashes[photo_hash]
            # Check if used for different job or by different installer
            for prev in previous:
                if prev["job_id"] != verification.job_id:
                    return FraudFlag(
                        type="photo_reuse",
                        severity="high",
                        details=f"Photo previously used for job #{prev['job_id']} by installer #{prev['installer_id']}",
                        score=90
                    )
        
        # Store for future checks
        if photo_hash not in cls._photo_hashes:
            cls._photo_hashes[photo_hash] = []
        cls._photo_hashes[photo_hash].append({
            "job_id": verification.job_id,
            "installer_id": verification.installer_id,
            "timestamp": verification.timestamp
        })
        
        return None
    
    @classmethod
    def check_geo_mismatch(cls, verification: VerificationData) -> Optional[FraudFlag]:
        """Check if geo location matches expected site location."""
        distance = cls.haversine_distance(
            verification.geo_lat, verification.geo_lng,
            verification.expected_lat, verification.expected_lng
        )
        
        if distance > cls.MAX_GEO_DISTANCE_M:
            severity = "high" if distance > 500 else "medium" if distance > 200 else "low"
            return FraudFlag(
                type="geo_mismatch",
                severity=severity,
                details=f"Photo taken {distance:.0f}m from expected location",
                score=min(100, distance / 5)  # 500m = 100 score
            )
        
        return None
    
    @classmethod
    def check_timestamp_anomaly(cls, verification: VerificationData) -> Optional[FraudFlag]:
        """Check for suspicious timestamp patterns."""
        installer_id = verification.installer_id
        
        if installer_id not in cls._installer_submissions:
            cls._installer_submissions[installer_id] = []
        
        submissions = cls._installer_submissions[installer_id]
        
        for prev in submissions[-10:]:  # Check last 10 submissions
            time_diff = (verification.timestamp - prev["timestamp"]).total_seconds() / 60
            
            if time_diff < cls.MIN_SUBMISSION_INTERVAL_MINS:
                # Check travel distance
                distance = cls.haversine_distance(
                    verification.geo_lat, verification.geo_lng,
                    prev["geo_lat"], prev["geo_lng"]
                )
                
                # Calculate required speed in km/h
                if time_diff > 0:
                    speed_kmh = (distance / 1000) / (time_diff / 60)
                    
                    if speed_kmh > cls.SUSPICIOUS_SPEED_KMH:
                        return FraudFlag(
                            type="timestamp_anomaly",
                            severity="high",
                            details=f"Impossible travel: {distance/1000:.1f}km in {time_diff:.0f}min ({speed_kmh:.0f}km/h)",
                            score=80
                        )
        
        # Store submission
        cls._installer_submissions[installer_id].append({
            "job_id": verification.job_id,
            "geo_lat": verification.geo_lat,
            "geo_lng": verification.geo_lng,
            "timestamp": verification.timestamp
        })
        
        return None
    
    @classmethod
    def check_metadata_anomaly(cls, verification: VerificationData) -> Optional[FraudFlag]:
        """Check for suspicious metadata (mock check)."""
        # In production: Check EXIF data, device fingerprint, etc.
        # For demo: Random low-probability flag
        if random.random() < 0.02:  # 2% chance
            return FraudFlag(
                type="metadata_anomaly",
                severity="low",
                details="Photo metadata inconsistencies detected",
                score=30
            )
        return None
    
    @classmethod
    def analyze(cls, verification: VerificationData) -> Dict:
        """
        Run all fraud detection checks on a verification submission.
        
        Returns:
            Dict with flags, risk_score, and recommendation
        """
        flags: List[FraudFlag] = []
        
        # Run all checks
        photo_flag = cls.check_photo_reuse(verification)
        if photo_flag:
            flags.append(photo_flag)
        
        geo_flag = cls.check_geo_mismatch(verification)
        if geo_flag:
            flags.append(geo_flag)
        
        timestamp_flag = cls.check_timestamp_anomaly(verification)
        if timestamp_flag:
            flags.append(timestamp_flag)
        
        metadata_flag = cls.check_metadata_anomaly(verification)
        if metadata_flag:
            flags.append(metadata_flag)
        
        # Calculate aggregate risk score
        if flags:
            risk_score = min(100, sum(f.score for f in flags) / len(flags) * (1 + len(flags) * 0.2))
        else:
            risk_score = 0
        
        # Determine recommendation
        if risk_score >= 70:
            recommendation = "reject"
            requires_review = True
        elif risk_score >= 40:
            recommendation = "manual_review"
            requires_review = True
        elif risk_score >= 20:
            recommendation = "approve_with_note"
            requires_review = False
        else:
            recommendation = "auto_approve"
            requires_review = False
        
        return {
            "job_id": verification.job_id,
            "installer_id": verification.installer_id,
            "risk_score": round(risk_score, 1),
            "flags": [
                {
                    "type": f.type,
                    "severity": f.severity,
                    "details": f.details,
                    "score": f.score
                }
                for f in flags
            ],
            "recommendation": recommendation,
            "requires_review": requires_review,
            "geo_distance_m": cls.haversine_distance(
                verification.geo_lat, verification.geo_lng,
                verification.expected_lat, verification.expected_lng
            ),
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def trigger_random_audit(cls, job_id: int, probability: float = 0.05) -> Optional[Dict]:
        """Trigger random audit based on probability."""
        if random.random() < probability:
            return {
                "job_id": job_id,
                "audit_type": "random",
                "reason": "Random quality assurance audit",
                "triggered_at": datetime.utcnow().isoformat()
            }
        return None
    
    @classmethod
    def clear_demo_data(cls):
        """Clear all stored data."""
        cls._photo_hashes = {}
        cls._installer_submissions = {}


# ============== DEMO ==============

def demo_fraud_detection():
    """Demo fraud detection scenarios."""
    FraudDetector.clear_demo_data()
    
    # Normal submission
    v1 = VerificationData(
        job_id=101,
        installer_id=1,
        photo_url="https://example.com/photo1.jpg",
        photo_hash="abc123",
        geo_lat=28.6139,
        geo_lng=77.2090,
        expected_lat=28.6140,
        expected_lng=77.2091,
        timestamp=datetime.utcnow()
    )
    result1 = FraudDetector.analyze(v1)
    print(f"Normal: Risk={result1['risk_score']}, Rec={result1['recommendation']}")
    
    # Geo mismatch
    v2 = VerificationData(
        job_id=102,
        installer_id=1,
        photo_url="https://example.com/photo2.jpg",
        photo_hash="def456",
        geo_lat=28.6200,  # 700m away
        geo_lng=77.2150,
        expected_lat=28.6139,
        expected_lng=77.2090,
        timestamp=datetime.utcnow()
    )
    result2 = FraudDetector.analyze(v2)
    print(f"Geo mismatch: Risk={result2['risk_score']}, Rec={result2['recommendation']}")
    
    # Photo reuse
    v3 = VerificationData(
        job_id=103,
        installer_id=2,
        photo_url="https://example.com/photo3.jpg",
        photo_hash="abc123",  # Same as v1
        geo_lat=28.6139,
        geo_lng=77.2090,
        expected_lat=28.6139,
        expected_lng=77.2090,
        timestamp=datetime.utcnow()
    )
    result3 = FraudDetector.analyze(v3)
    print(f"Photo reuse: Risk={result3['risk_score']}, Rec={result3['recommendation']}, Flags={result3['flags']}")
    
    return [result1, result2, result3]


if __name__ == "__main__":
    demo_fraud_detection()
