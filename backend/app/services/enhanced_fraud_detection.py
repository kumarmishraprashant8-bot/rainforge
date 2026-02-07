"""
RainForge Enhanced Fraud Detection
Perceptual hashing, travel anomaly, photo sequence validation
"""

import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate Haversine distance between two points in meters."""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad, lat2_rad = radians(lat1), radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


class PerceptualHasher:
    """
    Perceptual image hashing (pHash) for duplicate detection.
    Creates hash that's similar for visually similar images.
    """
    
    def __init__(self, hash_size: int = 8):
        self.hash_size = hash_size
    
    def compute_phash(self, image_bytes: bytes) -> str:
        """
        Compute perceptual hash of an image.
        Similar images will have similar hashes (small Hamming distance).
        """
        try:
            # Try to use imagehash library if available
            from PIL import Image
            import imagehash
            import io
            
            img = Image.open(io.BytesIO(image_bytes))
            phash = imagehash.phash(img, hash_size=self.hash_size)
            return str(phash)
        except ImportError:
            # Fallback: use SHA256 + truncate (less robust but works)
            return hashlib.sha256(image_bytes).hexdigest()[:16]
    
    def compute_dhash(self, image_bytes: bytes) -> str:
        """Compute difference hash (faster, still robust)."""
        try:
            from PIL import Image
            import imagehash
            import io
            
            img = Image.open(io.BytesIO(image_bytes))
            dhash = imagehash.dhash(img, hash_size=self.hash_size)
            return str(dhash)
        except ImportError:
            return hashlib.sha256(image_bytes).hexdigest()[:16]
    
    def hamming_distance(self, hash1: str, hash2: str) -> int:
        """Calculate Hamming distance between two hashes."""
        if len(hash1) != len(hash2):
            return 999  # Incompatible
        
        # Convert hex to binary and count differences
        try:
            bin1 = bin(int(hash1, 16))[2:].zfill(len(hash1) * 4)
            bin2 = bin(int(hash2, 16))[2:].zfill(len(hash2) * 4)
            return sum(c1 != c2 for c1, c2 in zip(bin1, bin2))
        except:
            return 999
    
    def is_duplicate(self, hash1: str, hash2: str, threshold: int = 10) -> bool:
        """Check if two images are perceptually similar."""
        return self.hamming_distance(hash1, hash2) <= threshold


class FraudDetector:
    """
    Enhanced fraud detection with multiple heuristics.
    """
    
    def __init__(self, known_hashes: Optional[Dict[str, str]] = None):
        self.known_hashes = known_hashes or {}
        self.hasher = PerceptualHasher()
        
        # Fraud weights
        self.WEIGHTS = {
            "photo_reuse": 0.9,
            "perceptual_duplicate": 0.8,
            "geo_mismatch_severe": 0.7,
            "geo_mismatch_moderate": 0.4,
            "travel_anomaly": 0.6,
            "missing_exif": 0.3,
            "timestamp_mismatch": 0.4,
            "device_mismatch": 0.3,
            "photo_sequence_violation": 0.5,
            "unusual_submission_time": 0.2,
        }
    
    def analyze_verification(
        self,
        photos: List[bytes],
        submitted_lat: float,
        submitted_lng: float,
        site_lat: float,
        site_lng: float,
        installer_base_lat: Optional[float] = None,
        installer_base_lng: Optional[float] = None,
        previous_photo_hashes: Optional[List[str]] = None,
        milestone: str = "installation_complete"
    ) -> Dict:
        """
        Comprehensive fraud analysis for verification submission.
        Returns risk score, flags, and recommendation.
        """
        
        flags = []
        score = 0.0
        details = []
        
        # 1. Photo hash analysis (SHA256 + pHash)
        for i, photo in enumerate(photos):
            sha_hash = hashlib.sha256(photo).hexdigest()
            p_hash = self.hasher.compute_phash(photo)
            
            # Exact duplicate check (SHA256)
            if sha_hash in self.known_hashes:
                flags.append(f"photo_{i}_exact_reuse")
                score += self.WEIGHTS["photo_reuse"]
                details.append({
                    "check": "exact_duplicate",
                    "photo_index": i,
                    "matched_verification": self.known_hashes[sha_hash],
                    "severity": "critical"
                })
            
            # Perceptual duplicate check
            for known_phash, ver_id in self.known_hashes.items():
                if self.hasher.is_duplicate(p_hash, known_phash):
                    flags.append(f"photo_{i}_perceptual_match")
                    score += self.WEIGHTS["perceptual_duplicate"]
                    details.append({
                        "check": "perceptual_duplicate",
                        "photo_index": i,
                        "hamming_distance": self.hasher.hamming_distance(p_hash, known_phash),
                        "matched_verification": ver_id,
                        "severity": "high"
                    })
                    break
        
        # 2. Geo-mismatch detection
        geo_distance = calculate_distance(submitted_lat, submitted_lng, site_lat, site_lng)
        
        if geo_distance > 500:  # >500m is severe
            flags.append("geo_mismatch_severe")
            score += self.WEIGHTS["geo_mismatch_severe"]
            details.append({
                "check": "geo_mismatch",
                "distance_m": round(geo_distance, 0),
                "threshold_m": 500,
                "severity": "critical"
            })
        elif geo_distance > 150:  # >150m is moderate
            flags.append("geo_mismatch_moderate")
            score += self.WEIGHTS["geo_mismatch_moderate"]
            details.append({
                "check": "geo_mismatch",
                "distance_m": round(geo_distance, 0),
                "threshold_m": 150,
                "severity": "medium"
            })
        
        # 3. Travel anomaly detection
        if installer_base_lat and installer_base_lng:
            travel_distance = calculate_distance(
                installer_base_lat, installer_base_lng,
                submitted_lat, submitted_lng
            )
            
            # If installer traveled > 200km for a job, flag it
            if travel_distance > 200000:
                flags.append("travel_anomaly")
                score += self.WEIGHTS["travel_anomaly"]
                details.append({
                    "check": "travel_anomaly",
                    "distance_km": round(travel_distance / 1000, 1),
                    "installer_base": f"{installer_base_lat},{installer_base_lng}",
                    "severity": "high"
                })
        
        # 4. Photo sequence validation (for progressive milestones)
        if previous_photo_hashes and milestone != "before":
            # Check that current photos are different from previous milestone
            for i, photo in enumerate(photos):
                p_hash = self.hasher.compute_phash(photo)
                for prev_hash in previous_photo_hashes:
                    if self.hasher.is_duplicate(p_hash, prev_hash, threshold=5):
                        flags.append("photo_sequence_violation")
                        score += self.WEIGHTS["photo_sequence_violation"]
                        details.append({
                            "check": "photo_sequence",
                            "message": "Current photo too similar to previous milestone",
                            "severity": "medium"
                        })
                        break
        
        # 5. Unusual submission time (late night submissions are suspicious)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            flags.append("unusual_submission_time")
            score += self.WEIGHTS["unusual_submission_time"]
            details.append({
                "check": "submission_time",
                "hour": current_hour,
                "message": "Submission outside normal working hours",
                "severity": "low"
            })
        
        # Calculate final score (cap at 1.0)
        final_score = min(1.0, score)
        
        # Determine recommendation
        if final_score >= 0.8:
            recommendation = "reject"
            status = "fraud_flagged"
        elif final_score >= 0.5:
            recommendation = "manual_review"
            status = "pending_review"
        elif final_score >= 0.2:
            recommendation = "review"
            status = "low_risk"
        else:
            recommendation = "auto_approve"
            status = "clean"
        
        return {
            "fraud_score": round(final_score, 2),
            "risk_level": self._risk_level(final_score),
            "flags": flags,
            "recommendation": recommendation,
            "status": status,
            "checks_performed": len(details),
            "details": details,
            "geo_distance_m": round(geo_distance, 0),
            "confidence": 0.92 if len(photos) > 0 else 0.5
        }
    
    def _risk_level(self, score: float) -> str:
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        return "clean"


class ConfidenceCalculator:
    """
    Calculate confidence/uncertainty scores for assessments.
    Government needs to trust the results.
    """
    
    def calculate_assessment_confidence(
        self,
        data_sources: Dict,
        roof_area_source: str,
        has_site_visit: bool = False
    ) -> Dict:
        """
        Calculate confidence score for assessment results.
        Returns confidence percentage and factors.
        """
        
        factors = []
        score = 0.0
        max_score = 0.0
        
        # Rainfall data source (30 points max)
        max_score += 30
        rainfall_source = data_sources.get("rainfall", {}).get("source", "estimated")
        if rainfall_source == "IMD":
            score += 30
            factors.append({"factor": "rainfall_source", "value": "IMD Official", "points": 30})
        elif rainfall_source == "Open-Meteo":
            score += 22
            factors.append({"factor": "rainfall_source", "value": "Open-Meteo Reanalysis", "points": 22})
        else:
            score += 10
            factors.append({"factor": "rainfall_source", "value": "Estimated", "points": 10})
        
        # Roof area measurement (25 points max)
        max_score += 25
        if roof_area_source == "lidar":
            score += 25
            factors.append({"factor": "roof_measurement", "value": "LiDAR/Survey", "points": 25})
        elif roof_area_source == "satellite_cv":
            score += 20
            factors.append({"factor": "roof_measurement", "value": "Satellite + CV", "points": 20})
        elif roof_area_source == "user_measured":
            score += 15
            factors.append({"factor": "roof_measurement", "value": "User Measured", "points": 15})
        else:
            score += 8
            factors.append({"factor": "roof_measurement", "value": "User Estimate", "points": 8})
        
        # Site visit verification (20 points max)
        max_score += 20
        if has_site_visit:
            score += 20
            factors.append({"factor": "site_verification", "value": "Engineer Verified", "points": 20})
        else:
            score += 5
            factors.append({"factor": "site_verification", "value": "Remote Only", "points": 5})
        
        # Subsidy data (15 points max)
        max_score += 15
        subsidy_source = data_sources.get("subsidy", {}).get("scheme_name", "")
        if "Jal Board" in subsidy_source or "BWSSB" in subsidy_source:
            score += 15
            factors.append({"factor": "subsidy_source", "value": "Official State Scheme", "points": 15})
        elif subsidy_source:
            score += 10
            factors.append({"factor": "subsidy_source", "value": "Central Scheme", "points": 10})
        else:
            score += 5
            factors.append({"factor": "subsidy_source", "value": "Default", "points": 5})
        
        # Groundwater data (10 points max)
        max_score += 10
        gw_source = data_sources.get("groundwater", {}).get("source", "")
        if gw_source == "CGWB":
            score += 10
            factors.append({"factor": "groundwater_data", "value": "CGWB Official", "points": 10})
        else:
            score += 3
            factors.append({"factor": "groundwater_data", "value": "Unavailable", "points": 3})
        
        confidence_pct = round((score / max_score) * 100, 1)
        
        return {
            "confidence_pct": confidence_pct,
            "confidence_grade": self._confidence_grade(confidence_pct),
            "score": score,
            "max_score": max_score,
            "factors": factors,
            "recommendation": self._confidence_recommendation(confidence_pct)
        }
    
    def _confidence_grade(self, pct: float) -> str:
        if pct >= 90:
            return "A"
        elif pct >= 75:
            return "B"
        elif pct >= 60:
            return "C"
        elif pct >= 45:
            return "D"
        return "F"
    
    def _confidence_recommendation(self, pct: float) -> str:
        if pct >= 80:
            return "High confidence - suitable for government approval"
        elif pct >= 60:
            return "Moderate confidence - recommend site verification"
        else:
            return "Low confidence - require engineer site visit before approval"


class TankQRValidator:
    """
    Tank QR/serial number validation.
    Each installed tank has a unique ID that must be scanned at verification.
    """
    
    def __init__(self):
        # In production, this would be a database lookup
        self.registered_tanks = {}
    
    def register_tank(self, tank_serial: str, job_id: str, installer_id: int) -> Dict:
        """Register a tank serial number at installation."""
        self.registered_tanks[tank_serial] = {
            "job_id": job_id,
            "installer_id": installer_id,
            "registered_at": datetime.utcnow().isoformat(),
            "verified": False
        }
        return {"success": True, "tank_serial": tank_serial}
    
    def validate_tank_scan(self, tank_serial: str, job_id: str) -> Dict:
        """Validate a tank QR scan during verification."""
        
        if tank_serial not in self.registered_tanks:
            return {
                "valid": False,
                "error": "Unregistered tank serial",
                "fraud_flag": True
            }
        
        tank_info = self.registered_tanks[tank_serial]
        
        if tank_info["job_id"] != job_id:
            return {
                "valid": False,
                "error": "Tank registered for different job",
                "expected_job": tank_info["job_id"],
                "fraud_flag": True
            }
        
        if tank_info["verified"]:
            return {
                "valid": False,
                "error": "Tank already verified",
                "verified_at": tank_info.get("verified_at"),
                "fraud_flag": True
            }
        
        # Mark as verified
        tank_info["verified"] = True
        tank_info["verified_at"] = datetime.utcnow().isoformat()
        
        return {
            "valid": True,
            "tank_serial": tank_serial,
            "job_id": job_id,
            "installer_id": tank_info["installer_id"],
            "fraud_flag": False
        }
