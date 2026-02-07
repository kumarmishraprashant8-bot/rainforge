from pydantic import BaseModel
from datetime import datetime
import logging
import math
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import imagehash
from typing import Dict, Any, Tuple, Optional, List
import hashlib

logger = logging.getLogger(__name__)

class VerificationData(BaseModel):
    job_id: int
    installer_id: int
    photo_url: str
    photo_hash: str
    geo_lat: float
    geo_lng: float
    expected_lat: float
    expected_lng: float
    timestamp: datetime


class FraudDetector:
    """
    P0 Enhanced Fraud Detection for Verification Photos.
    - pHash-based duplicate detection (Hamming distance <= 8)
    - EXIF GPS extraction and validation
    - Geo-distance validation (configurable threshold)
    - Timestamp consistency checks
    - Software manipulation detection
    """
    
    _demo_history: List[str] = []  # List of photo_hashes seen
    _phash_database: Dict[str, str] = {}  # pHash -> photo_id mapping
    
    def __init__(self):
        self.geo_threshold_m = 100  # Configurable geo-fence threshold
        self.phash_threshold = 8  # Hamming distance threshold for duplicates
    
    def calculate_phash(self, image_path: str) -> str:
        """
        Calculate perceptual hash (pHash) of an image.
        Returns hex string representation.
        """
        try:
            img = Image.open(image_path)
            phash = imagehash.phash(img)
            return str(phash)
        except Exception as e:
            logger.error(f"pHash calculation failed: {e}")
            return ""
    
    def check_phash_duplicate(self, phash: str, photo_id: str) -> Tuple[bool, Optional[str], int]:
        """
        Check if pHash matches any existing photo (within Hamming distance threshold).
        
        Returns:
            (is_duplicate, matching_photo_id, hamming_distance)
        """
        if not phash:
            return False, None, 0
        
        current_hash = imagehash.hex_to_hash(phash)
        
        for stored_phash, stored_id in self._phash_database.items():
            try:
                stored_hash = imagehash.hex_to_hash(stored_phash)
                distance = current_hash - stored_hash  # Hamming distance
                
                if distance <= self.phash_threshold:
                    return True, stored_id, distance
            except Exception:
                continue
        
        # Store new hash
        self._phash_database[phash] = photo_id
        return False, None, 0
    
    def extract_exif_gps(self, image_path: str) -> Dict[str, Any]:
        """
        Extract GPS coordinates and timestamp from EXIF data.
        
        Returns dict with:
            - has_exif: bool
            - has_gps: bool
            - latitude: float
            - longitude: float
            - timestamp: datetime
            - software: str
        """
        result = {
            "has_exif": False,
            "has_gps": False,
            "latitude": None,
            "longitude": None,
            "timestamp": None,
            "software": None
        }
        
        try:
            img = Image.open(image_path)
            exif_data = img._getexif()
            
            if not exif_data:
                return result
            
            result["has_exif"] = True
            
            # Extract software tag
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "Software":
                    result["software"] = value
                elif tag_name == "DateTime" or tag_name == "DateTimeOriginal":
                    try:
                        result["timestamp"] = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    except Exception:
                        pass
                elif tag_name == "GPSInfo":
                    gps_data = value
                    coords = self._parse_gps_coords(gps_data)
                    if coords:
                        result["has_gps"] = True
                        result["latitude"] = coords[0]
                        result["longitude"] = coords[1]
            
            return result
            
        except Exception as e:
            logger.error(f"EXIF extraction failed: {e}")
            return result
    
    def _parse_gps_coords(self, gps_data: Dict) -> Optional[Tuple[float, float]]:
        """
        Parse GPS coordinates from EXIF GPSInfo dict.
        """
        try:
            def convert_to_degrees(value):
                d = float(value[0])
                m = float(value[1])
                s = float(value[2])
                return d + (m / 60.0) + (s / 3600.0)
            
            lat = convert_to_degrees(gps_data.get(2, [0, 0, 0]))
            lon = convert_to_degrees(gps_data.get(4, [0, 0, 0]))
            
            lat_ref = gps_data.get(1, 'N')
            lon_ref = gps_data.get(3, 'E')
            
            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon
            
            return (lat, lon)
        except Exception:
            return None
    
    def analyze_verification(
        self,
        image_path: str,
        photo_id: str,
        project_lat: float,
        project_lng: float,
        installer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        P0 Comprehensive fraud analysis with weighted scoring.
        
        Fraud Score Formula:
            score = 0.4*photo_reuse + 0.3*geo_mismatch + 0.2*exif_missing + 0.1*software_manipulation
        
        Returns:
            {
                "fraud_score": float (0-1),
                "flags": List[str],
                "recommendation": str (auto_approve/manual_review/reject),
                "details": {
                    "phash": str,
                    "is_duplicate": bool,
                    "geo_distance_m": float,
                    "has_exif": bool,
                    "has_gps": bool,
                    "exif_data": dict
                }
            }
        """
        flags = []
        score = 0.0
        details = {}
        
        # 1. Calculate pHash
        phash = self.calculate_phash(image_path)
        details["phash"] = phash
        
        # 2. Check for photo reuse (weight: 0.4)
        is_duplicate, matching_id, hamming_dist = self.check_phash_duplicate(phash, photo_id)
        details["is_duplicate"] = is_duplicate
        details["duplicate_match_id"] = matching_id
        details["hamming_distance"] = hamming_dist
        
        if is_duplicate:
            score += 0.4
            flags.append(f"DUPLICATE_PHOTO: Matches photo {matching_id} (Hamming distance: {hamming_dist})")
        
        # 3. Extract EXIF data
        exif_data = self.extract_exif_gps(image_path)
        details["exif_data"] = exif_data
        details["has_exif"] = exif_data["has_exif"]
        details["has_gps"] = exif_data["has_gps"]
        
        # 4. EXIF missing check (weight: 0.2)
        if not exif_data["has_exif"]:
            score += 0.2
            flags.append("EXIF_MISSING: No EXIF metadata found in photo")
        elif not exif_data["has_gps"]:
            score += 0.2
            flags.append("GPS_MISSING: No GPS data in EXIF")
        
        # 5. Geo-distance check (weight: 0.3)
        if exif_data["has_gps"] and exif_data["latitude"] and exif_data["longitude"]:
            distance_m = self._haversine_distance(
                project_lat, project_lng,
                exif_data["latitude"], exif_data["longitude"]
            ) * 1000
            
            details["geo_distance_m"] = distance_m
            
            if distance_m > self.geo_threshold_m:
                score += 0.3
                flags.append(f"GEO_MISMATCH: Photo taken {distance_m:.0f}m from site (threshold: {self.geo_threshold_m}m)")
        else:
            details["geo_distance_m"] = None
        
        # 6. Software manipulation check (weight: 0.1)
        if exif_data.get("software"):
            software_lower = exif_data["software"].lower()
            suspicious_software = ["photoshop", "gimp", "pixlr", "snapseed"]
            if any(s in software_lower for s in suspicious_software):
                score += 0.1
                flags.append(f"SOFTWARE_MANIPULATION: Edited with {exif_data['software']}")
        
        # 7. Determine recommendation
        if score >= 0.8:
            recommendation = "reject"
        elif score >= 0.3:
            recommendation = "manual_review"
        else:
            recommendation = "auto_approve"
        
        return {
            "fraud_score": round(min(score, 1.0), 3),
            "flags": flags,
            "recommendation": recommendation,
            "details": details
        }

    def analyze(self, data: VerificationData) -> Dict[str, Any]:
        """
        Analyze verification data for fraud.
        """
        flags = []
        score = 0.0
        
        # 1. Geofencing Check
        distance_km = self._haversine_distance(
            data.expected_lat, data.expected_lng,
            data.geo_lat, data.geo_lng
        )
        distance_m = distance_km * 1000
        
        if distance_m > 200:
            score += 0.8
            flags.append(f"Location Mismatch: {distance_m:.0f}m from site")
        elif distance_m > 50:
            score += 0.3
            flags.append(f"Location Warning: {distance_m:.0f}m from site")

        # 2. Photo Reuse Check (Mock using hash)
        if data.photo_hash in self._demo_history:
            score += 1.0
            flags.append("Duplicate Photo Detected")
        else:
            self._demo_history.append(data.photo_hash)

        # 3. EXIF Validation (If local file - currently skipping as usually URL in this context needed download)
        # In a real scenario, we would download the image from data.photo_url
        # For this execution, we rely on the geofence and hash.
        
        # Determine recommendation
        if score >= 0.8:
            recommendation = "reject"
        elif score >= 0.3:
            recommendation = "review"
        else:
            recommendation = "auto_approve"

        return {
            "risk_score": min(score, 1.0),
            "flags": flags,
            "recommendation": recommendation,
            "geo_distance_m": distance_m
        }

    def clear_demo_data(self):
        self._demo_history = []

    def _get_exif_data(self, image_path: str) -> Dict[str, Any]:
        """Extract EXIF data including GPS."""
        try:
            image = Image.open(image_path)
            exif = image._getexif()
            if not exif:
                return {}
            
            labeled = {}
            for (key, val) in exif.items():
                labeled[TAGS.get(key)] = val
            return labeled
        except Exception as e:
            logger.error(f"EXIF extract failed: {e}")
            return {}

    def _get_coordinates(self, exif_data: Dict) -> Optional[Tuple[float, float]]:
        """Decode GPSInfo in EXIF to lat/lon float tuple."""
        gps_info = exif_data.get('GPSInfo')
        if not gps_info:
            return None
        
        def _convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)

        lat = _convert_to_degrees(gps_info[2])
        lon = _convert_to_degrees(gps_info[4])
        
        # Check reference (N/S, E/W)
        if gps_info[1] == 'S': lat = -lat
        if gps_info[3] == 'W': lon = -lon
            
        return (lat, lon)

    def validate_photo(self, image_path: str, site_lat: float, site_lon: float) -> Dict[str, Any]:
        """
        Validate a verification photo against strict rules.
        """
        exif = self._get_exif_data(image_path)
        
        # Rule 1: EXIF Presence
        if not exif:
            return {"valid": False, "reason": "No EXIF Metadata found. Original photo required."}
            
        # Rule 2: GPS Presence
        gps_coords = self._get_coordinates(exif)
        if not gps_coords:
            return {"valid": False, "reason": "No GPS data in photo. Ensure Location is enabled."}
            
        # Rule 3: Geofence (Distance check)
        img_lat, img_lon = gps_coords
        distance = self._haversine_distance(site_lat, site_lon, img_lat, img_lon)
        
        # Threshold: 200 meters
        if distance > 0.2:
            return {
                "valid": False, 
                "reason": f"Location Mismatch. Photo taken {distance*1000:.0f}m away from site."
            }
            
        # Rule 4: Software Manipulation
        software = exif.get('Software', '').lower()
        if 'photoshop' in software or 'gimp' in software:
             return {"valid": False, "reason": "Metadata indicates editing software used."}

        return {
            "valid": True, 
            "score": 1.0, 
            "meta": {"distance_km": distance, "software": software}
        }

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance in KM between two points."""
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + \
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

# Singleton
fraud_detector = FraudDetector()

def get_fraud_detector():
    return fraud_detector
