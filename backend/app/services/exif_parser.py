"""
EXIF Parser for RainForge
Extracts GPS and metadata from verification photos
"""

from typing import Optional, Dict, Any, Tuple
import io


def extract_gps_from_exif(photo_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Extract GPS coordinates and metadata from photo EXIF data.
    
    Returns:
        {
            "lat": float,
            "lng": float,
            "timestamp": str,
            "software": str,
            "camera": str
        }
    """
    try:
        return _extract_with_pillow(photo_bytes)
    except ImportError:
        try:
            return _extract_with_exifread(photo_bytes)
        except ImportError:
            return _extract_basic(photo_bytes)
    except Exception:
        return None


def _extract_with_pillow(photo_bytes: bytes) -> Optional[Dict[str, Any]]:
    """Extract EXIF using Pillow."""
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    
    image = Image.open(io.BytesIO(photo_bytes))
    exif_data = image._getexif()
    
    if not exif_data:
        return None
    
    result = {}
    gps_info = None
    
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        
        if tag == "GPSInfo":
            gps_info = {}
            for gps_tag_id, gps_value in value.items():
                gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                gps_info[gps_tag] = gps_value
        
        elif tag == "DateTimeOriginal":
            result["timestamp"] = str(value)
        
        elif tag == "Software":
            result["software"] = str(value)
        
        elif tag == "Make":
            result["camera_make"] = str(value)
        
        elif tag == "Model":
            result["camera_model"] = str(value)
    
    if gps_info:
        lat, lng = _parse_gps_pillow(gps_info)
        if lat is not None and lng is not None:
            result["lat"] = lat
            result["lng"] = lng
    
    if result.get("camera_make") and result.get("camera_model"):
        result["camera"] = f"{result['camera_make']} {result['camera_model']}"
    
    return result if result else None


def _parse_gps_pillow(gps_info: Dict) -> Tuple[Optional[float], Optional[float]]:
    """Parse GPS data from Pillow EXIF format."""
    try:
        lat_ref = gps_info.get("GPSLatitudeRef", "N")
        lat_dms = gps_info.get("GPSLatitude")
        lng_ref = gps_info.get("GPSLongitudeRef", "E")
        lng_dms = gps_info.get("GPSLongitude")
        
        if not lat_dms or not lng_dms:
            return None, None
        
        lat = _dms_to_decimal(lat_dms, lat_ref)
        lng = _dms_to_decimal(lng_dms, lng_ref)
        
        return lat, lng
    except Exception:
        return None, None


def _dms_to_decimal(dms, ref: str) -> float:
    """Convert degrees/minutes/seconds to decimal."""
    try:
        # Handle IFDRational from Pillow
        if hasattr(dms[0], 'numerator'):
            d = float(dms[0].numerator) / float(dms[0].denominator) if dms[0].denominator else 0
            m = float(dms[1].numerator) / float(dms[1].denominator) if dms[1].denominator else 0
            s = float(dms[2].numerator) / float(dms[2].denominator) if dms[2].denominator else 0
        else:
            d, m, s = float(dms[0]), float(dms[1]), float(dms[2])
        
        decimal = d + (m / 60) + (s / 3600)
        
        if ref in ['S', 'W']:
            decimal = -decimal
        
        return round(decimal, 6)
    except Exception:
        return 0.0


def _extract_with_exifread(photo_bytes: bytes) -> Optional[Dict[str, Any]]:
    """Extract EXIF using exifread library."""
    import exifread
    
    tags = exifread.process_file(io.BytesIO(photo_bytes))
    if not tags:
        return None
    
    result = {}
    
    # GPS
    lat_ref = tags.get("GPS GPSLatitudeRef")
    lat = tags.get("GPS GPSLatitude")
    lng_ref = tags.get("GPS GPSLongitudeRef")
    lng = tags.get("GPS GPSLongitude")
    
    if lat and lng:
        result["lat"] = _exifread_dms_to_decimal(lat.values, str(lat_ref) if lat_ref else "N")
        result["lng"] = _exifread_dms_to_decimal(lng.values, str(lng_ref) if lng_ref else "E")
    
    # Other fields
    if "EXIF DateTimeOriginal" in tags:
        result["timestamp"] = str(tags["EXIF DateTimeOriginal"])
    
    if "Image Software" in tags:
        result["software"] = str(tags["Image Software"])
    
    if "Image Make" in tags and "Image Model" in tags:
        result["camera"] = f"{tags['Image Make']} {tags['Image Model']}"
    
    return result if result else None


def _exifread_dms_to_decimal(values, ref: str) -> float:
    """Convert exifread DMS format to decimal."""
    try:
        d = float(values[0].num) / float(values[0].den) if values[0].den else 0
        m = float(values[1].num) / float(values[1].den) if values[1].den else 0
        s = float(values[2].num) / float(values[2].den) if values[2].den else 0
        
        decimal = d + (m / 60) + (s / 3600)
        
        if ref in ['S', 'W']:
            decimal = -decimal
        
        return round(decimal, 6)
    except Exception:
        return 0.0


def _extract_basic(photo_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Basic EXIF extraction without external libraries.
    Very limited - only works with some JPEG formats.
    """
    try:
        # Check for JPEG
        if photo_bytes[:2] != b'\xff\xd8':
            return None
        
        # Look for EXIF marker
        exif_start = photo_bytes.find(b'Exif\x00\x00')
        if exif_start == -1:
            return None
        
        # This is a very simplified extraction
        # In practice, you'd parse the IFD structure properly
        result = {}
        
        # Try to find GPS data pattern (very rough)
        gps_pattern = b'\x01\x00\x02\x00'  # GPSLatitudeRef marker
        gps_idx = photo_bytes.find(gps_pattern)
        
        if gps_idx > 0:
            # Found potential GPS, but can't parse without proper library
            result["has_gps"] = True
        
        return result if result else None
        
    except Exception:
        return None


# Demo/seed data for testing
DEMO_EXIF_DATA = {
    "photo_valid_delhi.jpg": {
        "lat": 28.6139,
        "lng": 77.2090,
        "timestamp": "2026-02-03 10:30:00",
        "software": "Samsung Camera",
        "camera": "Samsung Galaxy S23"
    },
    "photo_fraud_faraway.jpg": {
        "lat": 19.0760,
        "lng": 72.8777,  # Mumbai, but claimed Delhi
        "timestamp": "2026-02-03 10:35:00",
        "software": "Camera",
        "camera": "iPhone 15"
    },
    "photo_edited.jpg": {
        "lat": 28.6140,
        "lng": 77.2091,
        "timestamp": "2026-02-01 14:00:00",
        "software": "Adobe Photoshop 25.0",
        "camera": "Canon EOS R5"
    },
    "photo_no_gps.jpg": {
        "timestamp": "2026-02-03 09:00:00",
        "software": "Camera",
        "camera": "Generic Phone"
    }
}
