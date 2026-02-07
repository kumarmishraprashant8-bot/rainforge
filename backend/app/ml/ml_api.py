"""
RainForge ML API Service
========================
FastAPI service for ML inference (image verification, predictions).

Owners: Prashant Mishra & Ishita Parmar
"""

import os
import io
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ML imports (stub - replace with actual in production)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


app = FastAPI(
    title="RainForge ML Service",
    description="ML inference API for image verification and predictions",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELS & SCHEMAS
# ============================================================

class VerificationResult(BaseModel):
    """Result of image verification."""
    tank_present_confidence: float
    diverter_present_confidence: float
    image_quality_score: float
    manipulation_detected: bool
    gps_extracted: Optional[Dict[str, float]]
    exif_data: Dict[str, Any]
    checksum_sha256: str
    model_version: str
    explanation: Dict[str, Any]


class PredictionRequest(BaseModel):
    """Request for capture prediction."""
    lat: float
    lng: float
    roof_area_sqm: float
    roof_material: str = "concrete"
    forecast_days: int = 7


class PredictionResult(BaseModel):
    """Result of capture prediction."""
    daily_predictions: List[Dict[str, Any]]
    total_predicted_capture_l: float
    confidence: float
    data_source: str
    model_version: str


class ExplainRequest(BaseModel):
    """Request for ML explanation."""
    run_id: str


# ============================================================
# IMAGE VERIFICATION MODEL (Stub)
# ============================================================

class ImageVerificationModel:
    """
    Stub implementation of image verification model.
    In production, replace with trained MobileNetV2 or similar.
    """
    
    MODEL_VERSION = "v1.0.0-stub"
    
    def __init__(self):
        self.loaded = False
        # In production: load TensorFlow/PyTorch model here
        # self.model = tf.keras.models.load_model(MODEL_PATH)
    
    def predict(self, image_bytes: bytes) -> Dict[str, float]:
        """
        Run inference on image.
        
        Returns confidence scores for:
        - tank_present: Is a water tank visible?
        - diverter_present: Is a first-flush diverter visible?
        - quality_score: Image quality (blur, lighting)
        - manipulation_score: Likelihood of image manipulation
        """
        # Stub implementation - returns reasonable demo values
        # In production: preprocess image and run through model
        
        # Generate deterministic but varied results based on image hash
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        hash_value = int(image_hash[:8], 16)
        
        # Use hash to generate pseudo-random but consistent values
        base = (hash_value % 100) / 100
        
        return {
            "tank_present": 0.75 + (base * 0.2),  # 0.75 - 0.95
            "diverter_present": 0.60 + (base * 0.3),  # 0.60 - 0.90
            "quality_score": 0.80 + (base * 0.15),  # 0.80 - 0.95
            "manipulation_score": base * 0.15,  # 0.00 - 0.15
        }
    
    def get_explanation(self, predictions: Dict[str, float]) -> Dict[str, Any]:
        """Generate explanation for predictions."""
        return {
            "model_type": "MobileNetV2 (stub)",
            "model_version": self.MODEL_VERSION,
            "interpretation": {
                "tank_present": "High confidence" if predictions["tank_present"] > 0.85 else "Moderate confidence",
                "diverter_present": "Detected" if predictions["diverter_present"] > 0.7 else "Not clearly visible",
                "image_quality": "Good" if predictions["quality_score"] > 0.8 else "Acceptable",
                "manipulation": "No manipulation detected" if predictions["manipulation_score"] < 0.2 else "Review recommended"
            },
            "thresholds_used": {
                "tank_detection": 0.85,
                "diverter_detection": 0.70,
                "quality_minimum": 0.60,
                "manipulation_alert": 0.20
            }
        }


# ============================================================
# EXIF EXTRACTION
# ============================================================

def extract_exif(image_bytes: bytes) -> Dict[str, Any]:
    """Extract EXIF data including GPS from image."""
    
    if not HAS_PIL:
        return {"error": "PIL not available", "gps": None}
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif_data = {}
        gps_info = {}
        
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                
                if tag == "GPSInfo":
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag] = gps_value
                else:
                    # Convert bytes to string for JSON serialization
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)
                    exif_data[tag] = value
        
        # Parse GPS coordinates
        gps_coords = None
        if gps_info:
            try:
                lat = gps_info.get("GPSLatitude")
                lat_ref = gps_info.get("GPSLatitudeRef")
                lng = gps_info.get("GPSLongitude")
                lng_ref = gps_info.get("GPSLongitudeRef")
                
                if lat and lng:
                    lat_deg = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
                    lng_deg = float(lng[0]) + float(lng[1])/60 + float(lng[2])/3600
                    
                    if lat_ref == "S":
                        lat_deg = -lat_deg
                    if lng_ref == "W":
                        lng_deg = -lng_deg
                    
                    gps_coords = {"lat": lat_deg, "lng": lng_deg}
            except Exception as e:
                pass
        
        return {
            "exif": exif_data,
            "gps": gps_coords,
            "image_size": image.size,
            "format": image.format,
            "mode": image.mode
        }
    
    except Exception as e:
        return {"error": str(e), "gps": None}


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points using Haversine formula (meters)."""
    import math
    
    R = 6371000  # Earth's radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


# ============================================================
# CAPTURE PREDICTION MODEL (Stub)
# ============================================================

class CapturePredictionModel:
    """
    Stub implementation of capture prediction model.
    In production, use actual weather forecast API.
    """
    
    MODEL_VERSION = "v1.0.0-stub"
    
    # Synthetic forecast data for demo (mm rainfall)
    DEMO_FORECAST = [5.0, 0.0, 12.0, 8.0, 0.0, 0.0, 3.0]  # 7 days
    
    def predict(
        self,
        lat: float,
        lng: float,
        roof_area_sqm: float,
        roof_material: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Predict capture for next N days."""
        
        # Runoff coefficients
        C = {"concrete": 0.85, "metal": 0.95, "tiles": 0.8, "asphalt": 0.7}.get(roof_material, 0.85)
        
        # Generate synthetic forecast (in production, call weather API)
        import random
        random.seed(int(lat * 100 + lng * 100))  # Deterministic for same location
        
        daily_predictions = []
        total_capture = 0
        
        for day in range(days):
            # Synthetic rainfall (more likely in monsoon months)
            base_rain = self.DEMO_FORECAST[day % 7]
            rain_mm = base_rain + random.uniform(-2, 5)
            rain_mm = max(0, rain_mm)
            
            capture_l = roof_area_sqm * rain_mm * C
            total_capture += capture_l
            
            daily_predictions.append({
                "day": day + 1,
                "date": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        .isoformat()),
                "rainfall_mm": round(rain_mm, 1),
                "capture_l": round(capture_l, 1),
                "confidence": 0.85 if day < 3 else 0.70
            })
        
        return {
            "daily_predictions": daily_predictions,
            "total_predicted_capture_l": round(total_capture, 1),
            "confidence": 0.80,
            "data_source": "synthetic (demo)",
            "model_version": self.MODEL_VERSION
        }


# ============================================================
# API ENDPOINTS
# ============================================================

# Model instances
verification_model = ImageVerificationModel()
prediction_model = CapturePredictionModel()

# Store for explanations (in production, use Redis/DB)
explanation_store: Dict[str, Dict] = {}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ml_service",
        "version": "2.0.0",
        "models": {
            "verification": verification_model.MODEL_VERSION,
            "prediction": prediction_model.MODEL_VERSION
        }
    }


@app.post("/verify/image", response_model=VerificationResult)
async def verify_image(
    file: UploadFile = File(...),
    expected_lat: Optional[float] = Form(None),
    expected_lng: Optional[float] = Form(None)
):
    """
    Verify uploaded image for RWH installation.
    
    Checks for:
    - Tank presence
    - Diverter presence
    - Image quality
    - Image manipulation
    - GPS metadata vs expected location
    """
    
    # Read image
    image_bytes = await file.read()
    
    # Calculate checksum
    checksum = hashlib.sha256(image_bytes).hexdigest()
    
    # Extract EXIF
    exif_result = extract_exif(image_bytes)
    gps_extracted = exif_result.get("gps")
    
    # Run ML inference
    predictions = verification_model.predict(image_bytes)
    explanation = verification_model.get_explanation(predictions)
    
    # Check GPS match if expected location provided
    gps_match = True
    distance_m = None
    if expected_lat and expected_lng and gps_extracted:
        distance_m = calculate_distance(
            expected_lat, expected_lng,
            gps_extracted["lat"], gps_extracted["lng"]
        )
        gps_match = distance_m <= 50  # 50 meter threshold
        explanation["gps_check"] = {
            "expected": {"lat": expected_lat, "lng": expected_lng},
            "extracted": gps_extracted,
            "distance_m": round(distance_m, 1),
            "within_threshold": gps_match
        }
    
    # Store explanation for later retrieval
    run_id = f"ver_{checksum[:12]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    explanation_store[run_id] = {
        "type": "verification",
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "predictions": predictions,
        "explanation": explanation,
        "checksum": checksum
    }
    explanation["run_id"] = run_id
    
    return VerificationResult(
        tank_present_confidence=round(predictions["tank_present"], 4),
        diverter_present_confidence=round(predictions["diverter_present"], 4),
        image_quality_score=round(predictions["quality_score"], 4),
        manipulation_detected=predictions["manipulation_score"] > 0.2,
        gps_extracted=gps_extracted,
        exif_data={
            k: str(v)[:100] for k, v in exif_result.get("exif", {}).items()
            if k in ["Make", "Model", "DateTime", "Software"]
        },
        checksum_sha256=checksum,
        model_version=verification_model.MODEL_VERSION,
        explanation=explanation
    )


@app.post("/predict/capture", response_model=PredictionResult)
async def predict_capture(request: PredictionRequest):
    """
    Predict rainwater capture for next N days.
    
    Uses weather forecast to estimate daily capture.
    """
    
    result = prediction_model.predict(
        lat=request.lat,
        lng=request.lng,
        roof_area_sqm=request.roof_area_sqm,
        roof_material=request.roof_material,
        days=request.forecast_days
    )
    
    # Store explanation
    run_id = f"pred_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    explanation_store[run_id] = {
        "type": "prediction",
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "request": request.dict(),
        "result": result
    }
    
    return PredictionResult(**result)


@app.get("/explain/{run_id}")
async def get_explanation(run_id: str):
    """
    Get detailed explanation for a previous ML run.
    
    Provides:
    - Model version and type
    - Input data used
    - Calculation steps
    - Confidence scores
    - Data sources
    """
    
    if run_id not in explanation_store:
        raise HTTPException(status_code=404, detail=f"Run ID {run_id} not found")
    
    return explanation_store[run_id]


@app.get("/models")
async def list_models():
    """List available ML models and their versions."""
    return {
        "models": [
            {
                "name": "image_verification",
                "version": verification_model.MODEL_VERSION,
                "type": "classification",
                "description": "Detects tank and diverter presence in images"
            },
            {
                "name": "capture_prediction",
                "version": prediction_model.MODEL_VERSION,
                "type": "regression",
                "description": "Predicts daily rainwater capture based on forecast"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
