"""
Fraud Detection Service for RainForge
Deterministic fraud detection for verification photos
"""

import math
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance in meters between two coordinates using Haversine formula.
    """
    R = 6371000  # Earth's radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


class FraudDetector:
    """
    Multi-layer fraud detection for verification submissions.
    
    Layers:
    1. EXIF metadata validation (GPS presence, timestamps)
    2. Geofence validation (photo GPS vs site location)
    3. Photo hash duplicate detection
    4. Travel/time anomaly detection
    5. Software manipulation detection
    """
    
    # Thresholds (configurable)
    GEOFENCE_PASS_M = 50      # Pass if within 50m
    GEOFENCE_WARN_M = 200     # Warning if within 200m
    GEOFENCE_FLAG_M = 500     # Flag if within 500m
    
    # Score contributions
    SCORE_NO_EXIF = 0.4
    SCORE_NO_GPS = 0.3
    SCORE_LOCATION_SEVERE = 0.6
    SCORE_LOCATION_MODERATE = 0.3
    SCORE_LOCATION_WARNING = 0.1
    SCORE_PHOTO_REUSE = 0.8
    SCORE_EXIF_VS_SUBMITTED = 0.3
    SCORE_TIMESTAMP_OLD = 0.2
    SCORE_SOFTWARE_EDITED = 0.5
    SCORE_TRAVEL_ANOMALY = 0.4
    
    def __init__(self, known_hashes: Optional[Dict[str, str]] = None):
        """
        Initialize fraud detector.
        
        Args:
            known_hashes: Dict of photo_hash -> verification_id for duplicate detection
        """
        self.known_hashes = known_hashes or {}
    
    def analyze_verification(
        self,
        photos: List[bytes],
        submitted_lat: float,
        submitted_lng: float,
        site_lat: float,
        site_lng: float,
        installer_id: Optional[int] = None,
        previous_installler_locations: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Run complete fraud analysis on verification submission.
        
        Returns:
            {
                "fraud_score": 0.0-1.0,
                "flags": ["flag1", "flag2"],
                "recommendation": "auto_approve|review|manual_review|reject",
                "details": {...}
            }
        """
        fraud_score = 0.0
        flags = []
        details = {}
        
        all_exif_data = []
        all_hashes = []
        
        for i, photo_bytes in enumerate(photos):
            # Calculate hash
            photo_hash = hashlib.sha256(photo_bytes).hexdigest()
            all_hashes.append(photo_hash)
            
            # Check for duplicates
            if photo_hash in self.known_hashes:
                flags.append(f"photo_{i}_reuse_detected")
                fraud_score += self.SCORE_PHOTO_REUSE
                details[f"photo_{i}_duplicate_of"] = self.known_hashes[photo_hash]
            
            # Extract EXIF
            exif_data = self._extract_exif(photo_bytes)
            all_exif_data.append(exif_data)
            
            if not exif_data:
                flags.append(f"photo_{i}_no_exif")
                fraud_score += self.SCORE_NO_EXIF / len(photos)
                continue
            
            # Check GPS in EXIF
            exif_lat = exif_data.get("lat")
            exif_lng = exif_data.get("lng")
            
            if exif_lat is None or exif_lng is None:
                flags.append(f"photo_{i}_no_gps")
                fraud_score += self.SCORE_NO_GPS / len(photos)
                continue
            
            # Geofence check: EXIF GPS vs site location
            geo_distance = calculate_distance(exif_lat, exif_lng, site_lat, site_lng)
            details[f"photo_{i}_geo_distance_m"] = round(geo_distance, 1)
            
            if geo_distance > self.GEOFENCE_FLAG_M:
                flags.append(f"photo_{i}_location_severe")
                fraud_score += self.SCORE_LOCATION_SEVERE / len(photos)
            elif geo_distance > self.GEOFENCE_WARN_M:
                flags.append(f"photo_{i}_location_moderate")
                fraud_score += self.SCORE_LOCATION_MODERATE / len(photos)
            elif geo_distance > self.GEOFENCE_PASS_M:
                flags.append(f"photo_{i}_location_warning")
                fraud_score += self.SCORE_LOCATION_WARNING / len(photos)
            
            # Check EXIF GPS vs submitted coordinates
            submitted_vs_exif = calculate_distance(
                exif_lat, exif_lng, submitted_lat, submitted_lng
            )
            details[f"photo_{i}_submitted_vs_exif_m"] = round(submitted_vs_exif, 1)
            
            if submitted_vs_exif > 100:
                flags.append(f"photo_{i}_submitted_vs_exif_mismatch")
                fraud_score += self.SCORE_EXIF_VS_SUBMITTED / len(photos)
            
            # Check timestamp
            timestamp = exif_data.get("timestamp")
            if timestamp:
                try:
                    photo_time = datetime.fromisoformat(timestamp)
                    age_hours = (datetime.utcnow() - photo_time).total_seconds() / 3600
                    
                    if age_hours > 48:
                        flags.append(f"photo_{i}_timestamp_old")
                        fraud_score += self.SCORE_TIMESTAMP_OLD / len(photos)
                        details[f"photo_{i}_age_hours"] = round(age_hours, 1)
                except Exception:
                    pass
            
            # Check for editing software
            software = exif_data.get("software", "").lower()
            editing_software = ["photoshop", "gimp", "lightroom", "snapseed", "picsart"]
            if any(s in software for s in editing_software):
                flags.append(f"photo_{i}_software_edited")
                fraud_score += self.SCORE_SOFTWARE_EDITED / len(photos)
                details[f"photo_{i}_software"] = exif_data.get("software")
        
        # Travel anomaly detection (if we have previous installer locations)
        if previous_installler_locations and len(previous_installler_locations) > 0:
            anomaly = self._detect_travel_anomaly(
                submitted_lat, submitted_lng,
                previous_installler_locations
            )
            if anomaly:
                flags.append("travel_anomaly")
                fraud_score += self.SCORE_TRAVEL_ANOMALY
                details["travel_anomaly"] = anomaly
        
        # Cap score at 1.0
        fraud_score = min(1.0, fraud_score)
        
        # Determine recommendation
        if fraud_score >= 0.8:
            recommendation = "reject"
        elif fraud_score >= 0.5:
            recommendation = "manual_review"
        elif fraud_score >= 0.2:
            recommendation = "review"
        else:
            recommendation = "auto_approve"
        
        return {
            "fraud_score": round(fraud_score, 3),
            "flags": flags,
            "recommendation": recommendation,
            "photo_hashes": all_hashes,
            "exif_data": all_exif_data,
            "details": details
        }
    
    def _extract_exif(self, photo_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Extract EXIF data from photo bytes.
        Returns dict with lat, lng, timestamp, software, etc.
        """
        try:
            # Try using PIL/Pillow
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            import io
            
            image = Image.open(io.BytesIO(photo_bytes))
            exif_data = image._getexif()
            
            if not exif_data:
                return None
            
            result = {}
            
            # Parse EXIF tags
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                
                if tag == "GPSInfo":
                    gps_data = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_data[gps_tag] = gps_value
                    
                    # Extract coordinates
                    lat, lng = self._parse_gps(gps_data)
                    if lat and lng:
                        result["lat"] = lat
                        result["lng"] = lng
                
                elif tag == "DateTimeOriginal":
                    result["timestamp"] = str(value)
                
                elif tag == "Software":
                    result["software"] = str(value)
                
                elif tag == "Make":
                    result["camera_make"] = str(value)
                
                elif tag == "Model":
                    result["camera_model"] = str(value)
            
            return result if result else None
            
        except ImportError:
            # Fallback: try exifread
            try:
                import exifread
                import io
                
                tags = exifread.process_file(io.BytesIO(photo_bytes))
                if not tags:
                    return None
                
                result = {}
                
                # Extract GPS
                lat_ref = tags.get("GPS GPSLatitudeRef")
                lat = tags.get("GPS GPSLatitude")
                lng_ref = tags.get("GPS GPSLongitudeRef")
                lng = tags.get("GPS GPSLongitude")
                
                if lat and lng:
                    result["lat"] = self._convert_dms_to_decimal(lat.values, str(lat_ref))
                    result["lng"] = self._convert_dms_to_decimal(lng.values, str(lng_ref))
                
                # Timestamp
                if "EXIF DateTimeOriginal" in tags:
                    result["timestamp"] = str(tags["EXIF DateTimeOriginal"])
                
                # Software
                if "Image Software" in tags:
                    result["software"] = str(tags["Image Software"])
                
                return result if result else None
                
            except ImportError:
                return None
            except Exception:
                return None
        except Exception:
            return None
    
    def _parse_gps(self, gps_data: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Parse GPS data from EXIF."""
        try:
            lat_data = gps_data.get("GPSLatitude")
            lat_ref = gps_data.get("GPSLatitudeRef")
            lng_data = gps_data.get("GPSLongitude")
            lng_ref = gps_data.get("GPSLongitudeRef")
            
            if not all([lat_data, lat_ref, lng_data, lng_ref]):
                return None, None
            
            lat = self._convert_dms_to_decimal(lat_data, lat_ref)
            lng = self._convert_dms_to_decimal(lng_data, lng_ref)
            
            return lat, lng
        except Exception:
            return None, None
    
    def _convert_dms_to_decimal(self, dms, ref: str) -> float:
        """Convert DMS (degrees, minutes, seconds) to decimal degrees."""
        try:
            if hasattr(dms[0], 'numerator'):
                # Fraction format
                d = float(dms[0].numerator) / float(dms[0].denominator)
                m = float(dms[1].numerator) / float(dms[1].denominator)
                s = float(dms[2].numerator) / float(dms[2].denominator)
            else:
                d, m, s = float(dms[0]), float(dms[1]), float(dms[2])
            
            decimal = d + (m / 60) + (s / 3600)
            
            if ref in ['S', 'W']:
                decimal = -decimal
            
            return round(decimal, 6)
        except Exception:
            return 0.0
    
    def _detect_travel_anomaly(
        self,
        current_lat: float,
        current_lng: float,
        previous_locations: List[Dict]
    ) -> Optional[Dict]:
        """
        Detect impossible travel speed (e.g., 500km in 30 minutes).
        """
        if not previous_locations:
            return None
        
        # Sort by timestamp, most recent first
        sorted_locs = sorted(
            previous_locations,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        for prev in sorted_locs[:5]:  # Check last 5 locations
            try:
                prev_lat = prev.get("lat")
                prev_lng = prev.get("lng")
                prev_time = datetime.fromisoformat(prev.get("timestamp"))
                
                if not all([prev_lat, prev_lng, prev_time]):
                    continue
                
                distance_m = calculate_distance(current_lat, current_lng, prev_lat, prev_lng)
                time_diff_hours = (datetime.utcnow() - prev_time).total_seconds() / 3600
                
                if time_diff_hours <= 0:
                    continue
                
                speed_kmh = (distance_m / 1000) / time_diff_hours
                
                # Flag if speed > 300 km/h (impossible by road)
                if speed_kmh > 300:
                    return {
                        "distance_km": round(distance_m / 1000, 1),
                        "time_hours": round(time_diff_hours, 2),
                        "implied_speed_kmh": round(speed_kmh, 0),
                        "previous_location": prev
                    }
            except Exception:
                continue
        
        return None


def compute_photo_hash(photo_bytes: bytes) -> str:
    """Compute SHA256 hash of photo for duplicate detection."""
    return hashlib.sha256(photo_bytes).hexdigest()


# Test vectors for deterministic demo
TEST_VECTORS = {
    "legitimate": {
        "site_lat": 28.6139,
        "site_lng": 77.2090,
        "photo_lat": 28.6140,
        "photo_lng": 77.2091,
        "expected_score": 0.0,
        "expected_recommendation": "auto_approve"
    },
    "location_warning": {
        "site_lat": 28.6139,
        "site_lng": 77.2090,
        "photo_lat": 28.6145,
        "photo_lng": 77.2095,
        "expected_distance_m": 75,  # Approximate
        "expected_score_range": (0.05, 0.15),
        "expected_recommendation": "auto_approve"
    },
    "location_severe": {
        "site_lat": 28.6139,
        "site_lng": 77.2090,
        "photo_lat": 28.6200,
        "photo_lng": 77.2150,
        "expected_distance_m": 900,  # Approximate
        "expected_score_range": (0.5, 0.8),
        "expected_recommendation": "manual_review"
    },
    "photo_reuse": {
        "known_hash": "abc123def456",
        "submitted_hash": "abc123def456",
        "expected_score": 0.8,
        "expected_recommendation": "reject"
    }
}
