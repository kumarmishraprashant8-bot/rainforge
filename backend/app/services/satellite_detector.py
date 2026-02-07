"""
Satellite Roof Detector Service
Auto-detects roof boundaries from satellite imagery for RWH planning.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math
import uuid

logger = logging.getLogger(__name__)


class RoofType(str, Enum):
    FLAT_CONCRETE = "flat_concrete"
    SLOPED_TILE = "sloped_tile"
    METAL_SHEET = "metal_sheet"
    GREEN_ROOF = "green_roof"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class RoofPolygon:
    """Detected roof boundary polygon."""
    polygon_id: str
    coordinates: List[Tuple[float, float]]  # List of (lat, lon)
    area_sqm: float
    roof_type: RoofType
    confidence: float
    elevation_m: float
    suitable_for_rwh: bool
    suitability_score: float


@dataclass
class DetectionResult:
    """Satellite detection result for an area."""
    detection_id: str
    center_lat: float
    center_lon: float
    radius_m: float
    roofs_detected: int
    total_roof_area_sqm: float
    suitable_roofs: int
    suitable_area_sqm: float
    avg_confidence: float
    polygons: List[RoofPolygon]
    satellite_date: datetime
    processing_time_ms: int


class SatelliteDetectorService:
    """
    Mock satellite imagery processing for roof detection.
    
    In production, would integrate with:
    - Google Earth Engine
    - Mapbox Satellite
    - Planet Labs
    - Custom ML models (YOLO/Mask R-CNN)
    """
    
    # Runoff coefficients by roof type
    RUNOFF_COEFFICIENTS = {
        RoofType.FLAT_CONCRETE: 0.90,
        RoofType.SLOPED_TILE: 0.85,
        RoofType.METAL_SHEET: 0.95,
        RoofType.GREEN_ROOF: 0.30,
        RoofType.MIXED: 0.80,
        RoofType.UNKNOWN: 0.75
    }
    
    # Minimum area for RWH viability (sqm)
    MIN_VIABLE_AREA = 20.0
    
    def __init__(self):
        self._detections: Dict[str, DetectionResult] = {}
        self._cached_areas: Dict[str, List[RoofPolygon]] = {}
    
    def detect_roofs(
        self,
        center_lat: float,
        center_lon: float,
        radius_m: float = 500,
        min_confidence: float = 0.7
    ) -> DetectionResult:
        """
        Detect roofs in a circular area around a center point.
        Returns detected roof polygons with area and type.
        """
        detection_id = f"det_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        # Mock detection - generate realistic roof data
        polygons = self._mock_detect_roofs(center_lat, center_lon, radius_m)
        
        # Filter by confidence
        polygons = [p for p in polygons if p.confidence >= min_confidence]
        
        # Calculate stats
        total_area = sum(p.area_sqm for p in polygons)
        suitable = [p for p in polygons if p.suitable_for_rwh]
        suitable_area = sum(p.area_sqm for p in suitable)
        avg_conf = sum(p.confidence for p in polygons) / len(polygons) if polygons else 0
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        result = DetectionResult(
            detection_id=detection_id,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_m=radius_m,
            roofs_detected=len(polygons),
            total_roof_area_sqm=total_area,
            suitable_roofs=len(suitable),
            suitable_area_sqm=suitable_area,
            avg_confidence=avg_conf,
            polygons=polygons,
            satellite_date=datetime.now(),
            processing_time_ms=processing_time
        )
        
        self._detections[detection_id] = result
        logger.info(f"Detected {len(polygons)} roofs ({suitable_area:.0f} sqm suitable) in radius {radius_m}m")
        
        return result
    
    def _mock_detect_roofs(self, lat: float, lon: float, radius_m: float) -> List[RoofPolygon]:
        """Generate mock roof detections based on location."""
        import random
        random.seed(int(lat * 1000 + lon * 1000))  # Reproducible for same location
        
        # Estimate building density based on urban patterns
        # More buildings near city centers (lower variance in coords)
        density = random.randint(20, 80)
        num_roofs = int((radius_m / 100) ** 2 * density / 10)
        
        polygons = []
        for i in range(num_roofs):
            # Generate random position within radius
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius_m)
            
            # Convert to lat/lon offset
            lat_offset = (dist * math.cos(angle)) / 111000
            lon_offset = (dist * math.sin(angle)) / (111000 * math.cos(math.radians(lat)))
            roof_lat = lat + lat_offset
            roof_lon = lon + lon_offset
            
            # Generate roof polygon (rectangular approximation)
            width = random.uniform(5, 25)  # meters
            length = random.uniform(8, 30)  # meters
            area = width * length
            
            # Generate corner coordinates
            corners = [
                (roof_lat, roof_lon),
                (roof_lat + width/111000, roof_lon),
                (roof_lat + width/111000, roof_lon + length/(111000*math.cos(math.radians(lat)))),
                (roof_lat, roof_lon + length/(111000*math.cos(math.radians(lat))))
            ]
            
            # Assign roof type
            roof_types = list(RoofType)
            weights = [0.4, 0.25, 0.2, 0.05, 0.08, 0.02]  # Concrete most common
            roof_type = random.choices(roof_types, weights=weights)[0]
            
            # Calculate suitability
            confidence = random.uniform(0.65, 0.98)
            elevation = random.uniform(3, 30)
            
            is_suitable = (
                area >= self.MIN_VIABLE_AREA and
                roof_type != RoofType.GREEN_ROOF and
                confidence >= 0.7
            )
            
            suitability_score = 0.0
            if is_suitable:
                area_score = min(1.0, area / 100)  # Max score at 100 sqm
                type_score = self.RUNOFF_COEFFICIENTS.get(roof_type, 0.75)
                suitability_score = (area_score * 0.6 + type_score * 0.4) * confidence
            
            polygon = RoofPolygon(
                polygon_id=f"roof_{uuid.uuid4().hex[:6]}",
                coordinates=corners,
                area_sqm=area,
                roof_type=roof_type,
                confidence=confidence,
                elevation_m=elevation,
                suitable_for_rwh=is_suitable,
                suitability_score=suitability_score
            )
            polygons.append(polygon)
        
        return polygons
    
    def detect_single_address(
        self,
        lat: float,
        lon: float,
        address: str = ""
    ) -> Optional[RoofPolygon]:
        """Detect and return the roof polygon for a single address."""
        # Small radius detection
        result = self.detect_roofs(lat, lon, radius_m=50, min_confidence=0.5)
        
        if not result.polygons:
            return None
        
        # Return the closest/largest suitable roof
        suitable = [p for p in result.polygons if p.suitable_for_rwh]
        if suitable:
            return max(suitable, key=lambda p: p.area_sqm)
        
        return max(result.polygons, key=lambda p: p.area_sqm)
    
    def estimate_rwh_potential(
        self,
        detection_id: str,
        annual_rainfall_mm: float = 1200
    ) -> Dict[str, Any]:
        """Estimate RWH potential for a detection area."""
        detection = self._detections.get(detection_id)
        if not detection:
            raise ValueError(f"Detection {detection_id} not found")
        
        suitable_polygons = [p for p in detection.polygons if p.suitable_for_rwh]
        
        total_potential = 0.0
        by_type: Dict[str, Dict] = {}
        
        for polygon in suitable_polygons:
            runoff = self.RUNOFF_COEFFICIENTS.get(polygon.roof_type, 0.75)
            collection_eff = 0.80
            
            # Annual yield = Area × Rainfall × Runoff × Collection Efficiency
            yield_liters = polygon.area_sqm * annual_rainfall_mm * runoff * collection_eff
            total_potential += yield_liters
            
            type_key = polygon.roof_type.value
            if type_key not in by_type:
                by_type[type_key] = {"count": 0, "area_sqm": 0, "potential_liters": 0}
            by_type[type_key]["count"] += 1
            by_type[type_key]["area_sqm"] += polygon.area_sqm
            by_type[type_key]["potential_liters"] += yield_liters
        
        return {
            "detection_id": detection_id,
            "annual_rainfall_mm": annual_rainfall_mm,
            "total_roofs_analyzed": len(suitable_polygons),
            "total_suitable_area_sqm": detection.suitable_area_sqm,
            "total_annual_potential_liters": total_potential,
            "total_annual_potential_kl": total_potential / 1000,
            "by_roof_type": by_type,
            "avg_yield_per_roof_liters": total_potential / len(suitable_polygons) if suitable_polygons else 0,
            "equivalent_households_served": int(total_potential / (135 * 365)),  # LPCD standard
            "estimated_co2_offset_kg": total_potential * 0.00071
        }
    
    def get_ward_summary(
        self,
        ward_id: str,
        detections: List[str]
    ) -> Dict[str, Any]:
        """Generate ward-level summary from multiple detections."""
        all_polygons = []
        total_area = 0.0
        
        for det_id in detections:
            det = self._detections.get(det_id)
            if det:
                all_polygons.extend(det.polygons)
                total_area += det.total_roof_area_sqm
        
        suitable = [p for p in all_polygons if p.suitable_for_rwh]
        
        return {
            "ward_id": ward_id,
            "total_roofs": len(all_polygons),
            "suitable_roofs": len(suitable),
            "rwh_adoption_potential": f"{len(suitable)/len(all_polygons)*100:.1f}%" if all_polygons else "0%",
            "total_roof_area_sqm": total_area,
            "suitable_area_sqm": sum(p.area_sqm for p in suitable),
            "roof_type_distribution": self._get_type_distribution(all_polygons)
        }
    
    def _get_type_distribution(self, polygons: List[RoofPolygon]) -> Dict[str, float]:
        """Get percentage distribution of roof types."""
        if not polygons:
            return {}
        
        counts: Dict[str, int] = {}
        for p in polygons:
            key = p.roof_type.value
            counts[key] = counts.get(key, 0) + 1
        
        total = len(polygons)
        return {k: round(v/total*100, 1) for k, v in counts.items()}


# Singleton
_service: Optional[SatelliteDetectorService] = None

def get_satellite_detector() -> SatelliteDetectorService:
    global _service
    if _service is None:
        _service = SatelliteDetectorService()
    return _service
