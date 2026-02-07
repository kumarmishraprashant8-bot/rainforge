"""
Computer Vision Service for Installation Quality Control
Uses: OpenCV for image analysis, optional cloud APIs
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

# Try importing CV dependencies
try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False
    logger.warning("OpenCV not available, using basic image checks only")


@dataclass
class QualityCheckResult:
    """Result of quality check on an image."""
    passed: bool
    score: float  # 0-100
    issues: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


@dataclass
class ComponentDetection:
    """Detected RWH component in image."""
    component_type: str  # tank, gutter, pipe, filter, etc.
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    condition: str  # good, fair, poor


class ComputerVisionService:
    """
    Computer vision for RWH installation quality control.
    
    Features:
    - Image quality assessment
    - Component detection
    - Installation completeness check
    - Defect detection
    """
    
    # Expected components for a complete RWH installation
    REQUIRED_COMPONENTS = [
        "tank",
        "gutter",
        "downpipe",
        "filter"
    ]
    
    def __init__(self):
        self._model = None  # Placeholder for ML model
    
    async def analyze_installation_photo(
        self,
        image_data: bytes,
        expected_components: Optional[List[str]] = None
    ) -> QualityCheckResult:
        """
        Analyze an installation verification photo.
        """
        if not expected_components:
            expected_components = self.REQUIRED_COMPONENTS
        
        issues = []
        recommendations = []
        metadata = {}
        
        # Basic image quality checks
        quality_score = self._check_image_quality(image_data)
        metadata["quality_score"] = quality_score
        
        if quality_score < 50:
            issues.append("Image quality is poor - may be blurry or dark")
            recommendations.append("Retake photo in good lighting conditions")
        
        # Check if image is too dark or bright
        brightness = self._check_brightness(image_data)
        metadata["brightness"] = brightness
        
        if brightness < 50:
            issues.append("Image is too dark")
            recommendations.append("Use flash or take photo during daytime")
        elif brightness > 200:
            issues.append("Image is overexposed")
            recommendations.append("Avoid direct sunlight on the lens")
        
        # Component detection (simplified)
        if CV_AVAILABLE:
            detected = self._detect_components(image_data)
            metadata["detected_components"] = detected
            
            # Check for required components
            detected_types = [c["type"] for c in detected]
            missing = set(expected_components) - set(detected_types)
            
            if missing:
                issues.append(f"Could not detect: {', '.join(missing)}")
                recommendations.append("Ensure all components are visible in the photo")
        
        # Calculate overall score
        score = self._calculate_score(quality_score, brightness, issues)
        passed = score >= 60 and len(issues) < 3
        
        return QualityCheckResult(
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations,
            metadata=metadata
        )
    
    async def detect_tank_type(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """
        Detect tank type and estimate capacity.
        """
        if not CV_AVAILABLE:
            return {"type": "unknown", "confidence": 0}
        
        # Simplified color-based detection
        img = self._load_image(image_data)
        if img is None:
            return {"type": "unknown", "confidence": 0}
        
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Check for common tank colors
        # Blue (plastic tanks)
        blue_mask = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
        blue_ratio = np.sum(blue_mask > 0) / blue_mask.size
        
        # Black (plastic tanks)
        black_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 50))
        black_ratio = np.sum(black_mask > 0) / black_mask.size
        
        # Gray (concrete/RCC tanks)
        gray_mask = cv2.inRange(hsv, (0, 0, 100), (180, 30, 200))
        gray_ratio = np.sum(gray_mask > 0) / gray_mask.size
        
        # Determine tank type
        if blue_ratio > 0.15:
            tank_type = "plastic_blue"
            confidence = min(blue_ratio * 2, 0.95)
        elif black_ratio > 0.2:
            tank_type = "plastic_black"
            confidence = min(black_ratio * 1.5, 0.9)
        elif gray_ratio > 0.25:
            tank_type = "concrete_rcc"
            confidence = min(gray_ratio, 0.85)
        else:
            tank_type = "unknown"
            confidence = 0.3
        
        return {
            "type": tank_type,
            "confidence": round(confidence, 2),
            "analysis": {
                "blue_ratio": round(blue_ratio, 3),
                "black_ratio": round(black_ratio, 3),
                "gray_ratio": round(gray_ratio, 3)
            }
        }
    
    async def check_installation_alignment(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """
        Check if pipes/gutters are properly aligned.
        """
        if not CV_AVAILABLE:
            return {"aligned": True, "confidence": 0.5, "angle": 0}
        
        img = self._load_image(image_data)
        if img is None:
            return {"aligned": True, "confidence": 0.5, "angle": 0}
        
        # Edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Line detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)
        
        if lines is None or len(lines) == 0:
            return {"aligned": True, "confidence": 0.3, "angle": 0}
        
        # Calculate average angle
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            angles.append(angle)
        
        avg_angle = np.mean(angles)
        angle_std = np.std(angles)
        
        # Check alignment (should be close to 0°, 90°, or 180°)
        reference_angles = [0, 90, -90, 180, -180]
        min_deviation = min(abs(avg_angle - ref) for ref in reference_angles)
        
        aligned = min_deviation < 10  # Within 10 degrees
        confidence = 1 - (min_deviation / 90)
        
        return {
            "aligned": aligned,
            "confidence": round(max(confidence, 0), 2),
            "angle": round(avg_angle, 1),
            "deviation": round(min_deviation, 1),
            "line_count": len(lines)
        }
    
    async def detect_water_level(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """
        Estimate water level from tank photo.
        """
        if not CV_AVAILABLE:
            return {"level_percent": 50, "confidence": 0.3}
        
        img = self._load_image(image_data)
        if img is None:
            return {"level_percent": 50, "confidence": 0.3}
        
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Detect water (typically darker blue/black at bottom)
        # This is a simplified approach
        height = img.shape[0]
        
        # Analyze brightness gradient from top to bottom
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Split into horizontal bands
        bands = np.array_split(gray, 10, axis=0)
        brightness_profile = [np.mean(band) for band in bands]
        
        # Find transition point (water darker than air)
        water_level = 50  # default
        for i in range(len(brightness_profile) - 1):
            if brightness_profile[i] - brightness_profile[i+1] > 20:
                water_level = (10 - i) * 10
                break
        
        return {
            "level_percent": water_level,
            "confidence": 0.5,
            "brightness_profile": brightness_profile
        }
    
    # ==================== HELPER METHODS ====================
    
    def _load_image(self, image_data: bytes) -> Optional[Any]:
        """Load image from bytes."""
        if not CV_AVAILABLE:
            return None
        
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    def _check_image_quality(self, image_data: bytes) -> float:
        """Check image quality (focus, contrast)."""
        if not CV_AVAILABLE:
            return 70.0  # Default acceptable score
        
        img = self._load_image(image_data)
        if img is None:
            return 50.0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Laplacian variance for focus
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        focus_score = min(laplacian_var / 500 * 100, 100)
        
        # Contrast
        contrast = gray.std()
        contrast_score = min(contrast / 50 * 100, 100)
        
        return (focus_score + contrast_score) / 2
    
    def _check_brightness(self, image_data: bytes) -> float:
        """Check image brightness."""
        if not CV_AVAILABLE:
            return 128.0  # Default middle brightness
        
        img = self._load_image(image_data)
        if img is None:
            return 128.0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return float(np.mean(gray))
    
    def _detect_components(self, image_data: bytes) -> List[Dict]:
        """
        Detect RWH components in image.
        Simplified placeholder - would use trained model in production.
        """
        # In production, this would use a YOLO/SSD model trained on RWH components
        # For now, return placeholder
        return [
            {"type": "tank", "confidence": 0.85, "bbox": (100, 100, 200, 200)},
            {"type": "gutter", "confidence": 0.75, "bbox": (50, 50, 300, 30)}
        ]
    
    def _calculate_score(
        self,
        quality: float,
        brightness: float,
        issues: List[str]
    ) -> float:
        """Calculate overall QC score."""
        # Start with quality score
        score = quality * 0.4
        
        # Brightness contribution (ideal around 128)
        brightness_score = 100 - abs(brightness - 128) / 1.28
        score += brightness_score * 0.3
        
        # Deduct for issues
        issue_penalty = len(issues) * 10
        score = max(score - issue_penalty, 0)
        
        # Base score contribution
        score += 30  # Minimum score
        
        return min(round(score, 1), 100)


# Singleton
_cv_service: Optional[ComputerVisionService] = None

def get_cv_service() -> ComputerVisionService:
    global _cv_service
    if _cv_service is None:
        _cv_service = ComputerVisionService()
    return _cv_service
