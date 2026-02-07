"""
RainForge CV Roof Detection
Satellite/drone image analysis for automatic roof area detection
"""

from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class RoofDetectionResult:
    """Result of CV roof detection."""
    area_sqm: float
    confidence: float
    material: str
    material_confidence: float
    polygon: List[Tuple[float, float]]
    obstructions: List[Dict]
    metadata: Dict


class CVRoofDetector:
    """
    Computer Vision based roof detection from satellite/drone imagery.
    Uses a stub/mock implementation for demo.
    In production, would use TensorFlow/PyTorch + Sentinel-2/Planet imagery.
    """
    
    # Material classification classes
    MATERIALS = {
        "concrete_rcc": {"runoff_coeff": 0.90, "color_profile": "gray"},
        "metal_sheet": {"runoff_coeff": 0.95, "color_profile": "silver/blue"},
        "clay_tiles": {"runoff_coeff": 0.75, "color_profile": "orange/brown"},
        "asbestos": {"runoff_coeff": 0.85, "color_profile": "gray-white"},
        "thatched": {"runoff_coeff": 0.45, "color_profile": "brown"},
        "green_roof": {"runoff_coeff": 0.35, "color_profile": "green"},
    }
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model_loaded = False
        
    def detect_roof(
        self,
        lat: float,
        lng: float,
        image_bytes: Optional[bytes] = None,
        image_url: Optional[str] = None
    ) -> RoofDetectionResult:
        """
        Detect roof area and material from satellite imagery.
        
        For demo: Returns simulated results based on location.
        In production: Would fetch Sentinel-2/Planet imagery and run ML model.
        """
        
        # Simulated detection based on location characteristics
        # This would be replaced with actual CV model inference
        
        # Generate consistent pseudo-random values based on lat/lng
        location_hash = hashlib.md5(f"{lat:.4f},{lng:.4f}".encode()).hexdigest()
        seed_val = int(location_hash[:8], 16)
        
        # Simulate roof area (50-500 sqm typical for residential/institutional)
        area_base = 50 + (seed_val % 450)
        area_sqm = float(area_base)
        
        # Simulate confidence (0.7-0.95)
        confidence = 0.70 + (seed_val % 25) / 100
        
        # Simulate material detection
        material_idx = seed_val % len(self.MATERIALS)
        material = list(self.MATERIALS.keys())[material_idx]
        material_confidence = 0.65 + (seed_val % 30) / 100
        
        # Simulate polygon (simplified bounding box)
        delta = 0.0002  # ~20m at equator
        polygon = [
            (lat - delta, lng - delta),
            (lat - delta, lng + delta),
            (lat + delta, lng + delta),
            (lat + delta, lng - delta),
        ]
        
        # Simulate obstructions (AC units, vents, tanks)
        obstructions = []
        if seed_val % 3 == 0:
            obstructions.append({
                "type": "water_tank",
                "area_sqm": 4.0,
                "location": "northwest"
            })
        if seed_val % 5 == 0:
            obstructions.append({
                "type": "ac_unit",
                "area_sqm": 1.5,
                "location": "center"
            })
        
        # Calculate usable area
        obstruction_area = sum(o["area_sqm"] for o in obstructions)
        usable_area = area_sqm - obstruction_area
        
        return RoofDetectionResult(
            area_sqm=usable_area,
            confidence=confidence,
            material=material,
            material_confidence=material_confidence,
            polygon=polygon,
            obstructions=obstructions,
            metadata={
                "source": "simulated",
                "model_version": "demo_v1",
                "raw_area_sqm": area_sqm,
                "obstruction_area_sqm": obstruction_area,
                "runoff_coefficient": self.MATERIALS[material]["runoff_coeff"],
                "imagery_date": "2026-01-15",
                "resolution_m": 0.3,
                "processing_time_ms": 1250
            }
        )
    
    def detect_from_uploaded_image(self, image_bytes: bytes) -> RoofDetectionResult:
        """
        Detect roof from user-uploaded drone/phone image.
        Uses edge detection + perspective correction.
        """
        
        # Hash image for consistent demo results
        img_hash = hashlib.sha256(image_bytes).hexdigest()
        seed_val = int(img_hash[:8], 16)
        
        # Simulated detection with higher confidence (direct photo)
        area_sqm = 80 + (seed_val % 300)
        confidence = 0.85 + (seed_val % 10) / 100
        
        # Use concrete as default for uploaded images (most common)
        material = "concrete_rcc"
        if seed_val % 4 == 0:
            material = "metal_sheet"
        elif seed_val % 6 == 0:
            material = "clay_tiles"
        
        return RoofDetectionResult(
            area_sqm=float(area_sqm),
            confidence=confidence,
            material=material,
            material_confidence=0.80,
            polygon=[],  # Not available from photo
            obstructions=[],
            metadata={
                "source": "user_upload",
                "model_version": "demo_v1",
                "image_hash": img_hash[:16],
                "runoff_coefficient": self.MATERIALS[material]["runoff_coeff"]
            }
        )
    
    def estimate_catchment_area(
        self,
        roof_result: RoofDetectionResult,
        include_gutters: bool = True,
        gutter_efficiency: float = 0.95
    ) -> Dict:
        """
        Calculate effective catchment area for RWH.
        Accounts for gutters, slope, and obstructions.
        """
        
        base_area = roof_result.area_sqm
        runoff_coeff = roof_result.metadata.get("runoff_coefficient", 0.85)
        
        # Apply gutter efficiency
        if include_gutters:
            effective_area = base_area * gutter_efficiency
        else:
            effective_area = base_area * 0.70  # Significant loss without proper gutters
        
        return {
            "raw_roof_area_sqm": roof_result.metadata.get("raw_area_sqm", base_area),
            "obstruction_area_sqm": roof_result.metadata.get("obstruction_area_sqm", 0),
            "usable_roof_area_sqm": base_area,
            "gutter_efficiency": gutter_efficiency if include_gutters else 0.70,
            "effective_catchment_sqm": round(effective_area, 1),
            "runoff_coefficient": runoff_coeff,
            "final_collection_factor": round(effective_area * runoff_coeff / base_area, 3),
            "confidence": roof_result.confidence
        }


class SatelliteImageryFetcher:
    """
    Fetch satellite imagery for roof detection.
    Supports Sentinel-2 (free) and commercial providers.
    """
    
    PROVIDERS = {
        "sentinel2": {
            "resolution_m": 10,
            "cost": "free",
            "refresh_days": 5
        },
        "planet": {
            "resolution_m": 3,
            "cost": "commercial",
            "refresh_days": 1
        },
        "maxar": {
            "resolution_m": 0.3,
            "cost": "commercial",
            "refresh_days": 3
        }
    }
    
    def fetch_imagery(
        self,
        lat: float,
        lng: float,
        provider: str = "sentinel2",
        buffer_m: int = 50
    ) -> Dict:
        """
        Fetch imagery tile for location.
        Returns metadata for demo (actual imagery would require API keys).
        """
        
        provider_info = self.PROVIDERS.get(provider, self.PROVIDERS["sentinel2"])
        
        return {
            "provider": provider,
            "center": {"lat": lat, "lng": lng},
            "buffer_m": buffer_m,
            "resolution_m": provider_info["resolution_m"],
            "tile_size_px": int(buffer_m * 2 / provider_info["resolution_m"]),
            "imagery_available": True,
            "latest_capture": "2026-01-28",
            "cloud_cover_pct": 5,
            "download_url": f"/api/v1/imagery/{lat:.4f}_{lng:.4f}.tif"
        }
