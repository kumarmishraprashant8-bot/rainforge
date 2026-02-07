"""Anomaly Detection Service using Isolation Forest."""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import logging

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SubmissionFeatures:
    """Features extracted from a verification submission for anomaly detection."""
    geo_distance_m: float          # Distance from expected location
    time_since_last_mins: float    # Time since installer's last submission
    submissions_today: int         # Number of submissions by installer today
    avg_photo_size_kb: float       # Average photo size (anomaly if too small/large)
    hour_of_day: int               # Hour of submission (unusual hours = flag)
    day_of_week: int               # Weekend submissions might be suspicious
    installer_rpi: float           # Installer's current RPI score


@dataclass
class AnomalyResult:
    """Result of anomaly detection analysis."""
    is_anomaly: bool
    anomaly_score: float           # -1 to 1, negative = more anomalous
    confidence: float              # 0 to 1
    contributing_factors: List[str]
    recommendation: str            # "approve", "review", "reject"


class AnomalyDetector:
    """
    ML-based anomaly detection for verification submissions.
    Uses Isolation Forest to detect statistical outliers.
    """
    
    MODEL_PATH = Path("models/anomaly_detector.pkl")
    
    def __init__(self):
        self.model: Optional['IsolationForest'] = None
        self.scaler: Optional['StandardScaler'] = None
        self.is_trained = False
        self._feature_names = [
            "geo_distance_m", "time_since_last_mins", "submissions_today",
            "avg_photo_size_kb", "hour_of_day", "day_of_week", "installer_rpi"
        ]
        
        if SKLEARN_AVAILABLE:
            self._load_model()
        else:
            logger.warning("scikit-learn not available, using rule-based detection")
    
    def _load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            if self.MODEL_PATH.exists():
                with open(self.MODEL_PATH, "rb") as f:
                    data = pickle.load(f)
                    self.model = data["model"]
                    self.scaler = data["scaler"]
                    self.is_trained = True
                    logger.info("Loaded anomaly detection model")
                    return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
        return False
    
    def _save_model(self) -> bool:
        """Save trained model to disk."""
        try:
            self.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.MODEL_PATH, "wb") as f:
                pickle.dump({
                    "model": self.model,
                    "scaler": self.scaler,
                    "trained_at": datetime.utcnow().isoformat()
                }, f)
            logger.info("Saved anomaly detection model")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def _features_to_array(self, features: SubmissionFeatures) -> np.ndarray:
        """Convert SubmissionFeatures to numpy array."""
        return np.array([[
            features.geo_distance_m,
            features.time_since_last_mins,
            features.submissions_today,
            features.avg_photo_size_kb,
            features.hour_of_day,
            features.day_of_week,
            features.installer_rpi
        ]])
    
    def train(self, historical_data: List[SubmissionFeatures], contamination: float = 0.05):
        """
        Train the anomaly detection model on historical submission data.
        
        Args:
            historical_data: List of historical submissions (mostly normal)
            contamination: Expected proportion of outliers (default 5%)
        """
        if not SKLEARN_AVAILABLE:
            logger.error("Cannot train: scikit-learn not installed")
            return
        
        if len(historical_data) < 50:
            logger.warning(f"Training with only {len(historical_data)} samples, need at least 50")
        
        # Convert to numpy array
        X = np.array([
            [f.geo_distance_m, f.time_since_last_mins, f.submissions_today,
             f.avg_photo_size_kb, f.hour_of_day, f.day_of_week, f.installer_rpi]
            for f in historical_data
        ])
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            max_samples='auto',
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled)
        self.is_trained = True
        
        self._save_model()
        logger.info(f"Trained anomaly detector on {len(historical_data)} samples")
    
    def predict(self, features: SubmissionFeatures) -> AnomalyResult:
        """
        Predict if a submission is anomalous.
        Falls back to rule-based detection if model not available.
        """
        contributing_factors = []
        
        # Always run rule-based checks
        rule_score, rule_factors = self._rule_based_check(features)
        contributing_factors.extend(rule_factors)
        
        # ML-based prediction if available
        if self.is_trained and self.model is not None and self.scaler is not None:
            X = self._features_to_array(features)
            X_scaled = self.scaler.transform(X)
            
            # Get prediction (-1 = anomaly, 1 = normal)
            prediction = self.model.predict(X_scaled)[0]
            
            # Get anomaly score (negative = more anomalous)
            anomaly_score = self.model.decision_function(X_scaled)[0]
            
            # Combine ML and rule-based scores
            is_anomaly = prediction == -1 or rule_score > 50
            confidence = min(1.0, abs(anomaly_score) + (rule_score / 100))
            
        else:
            # Fallback to pure rule-based
            is_anomaly = rule_score > 50
            anomaly_score = -rule_score / 100
            confidence = min(1.0, rule_score / 70)
        
        # Determine recommendation
        if is_anomaly and confidence > 0.7:
            recommendation = "reject"
        elif is_anomaly or confidence > 0.4:
            recommendation = "review"
        else:
            recommendation = "approve"
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=round(anomaly_score, 3),
            confidence=round(confidence, 3),
            contributing_factors=contributing_factors,
            recommendation=recommendation
        )
    
    def _rule_based_check(self, features: SubmissionFeatures) -> Tuple[float, List[str]]:
        """
        Rule-based anomaly detection (always runs as supplement to ML).
        Returns (score, factors) where score 0-100 indicates anomaly severity.
        """
        score = 0.0
        factors = []
        
        # Geo distance check
        if features.geo_distance_m > 500:
            score += 40
            factors.append(f"Large geo distance: {features.geo_distance_m:.0f}m")
        elif features.geo_distance_m > 200:
            score += 20
            factors.append(f"Moderate geo distance: {features.geo_distance_m:.0f}m")
        elif features.geo_distance_m > 100:
            score += 10
            factors.append(f"Slight geo distance: {features.geo_distance_m:.0f}m")
        
        # Rapid submissions
        if features.time_since_last_mins < 5:
            score += 30
            factors.append(f"Rapid submission: {features.time_since_last_mins:.1f}min since last")
        elif features.time_since_last_mins < 15:
            score += 15
            factors.append(f"Quick submission: {features.time_since_last_mins:.1f}min since last")
        
        # High daily submission count
        if features.submissions_today > 15:
            score += 25
            factors.append(f"Very high daily count: {features.submissions_today}")
        elif features.submissions_today > 10:
            score += 10
            factors.append(f"High daily count: {features.submissions_today}")
        
        # Unusual photo size
        if features.avg_photo_size_kb < 50:
            score += 20
            factors.append(f"Suspiciously small photos: {features.avg_photo_size_kb:.0f}KB")
        elif features.avg_photo_size_kb > 5000:
            score += 10
            factors.append(f"Unusually large photos: {features.avg_photo_size_kb:.0f}KB")
        
        # Unusual hours (midnight to 5am)
        if features.hour_of_day < 5 or features.hour_of_day > 22:
            score += 15
            factors.append(f"Unusual hour: {features.hour_of_day}:00")
        
        # Low RPI installer
        if features.installer_rpi < 50:
            score += 20
            factors.append(f"Low RPI installer: {features.installer_rpi}")
        elif features.installer_rpi < 70:
            score += 10
            factors.append(f"Medium RPI installer: {features.installer_rpi}")
        
        return (score, factors)
    
    def generate_training_data(self, n_samples: int = 1000) -> List[SubmissionFeatures]:
        """Generate synthetic training data for demo/testing."""
        np.random.seed(42)
        data = []
        
        for _ in range(n_samples):
            # Generate mostly normal submissions
            is_normal = np.random.random() > 0.05  # 95% normal
            
            if is_normal:
                features = SubmissionFeatures(
                    geo_distance_m=np.random.exponential(30),  # Most close to 0
                    time_since_last_mins=np.random.exponential(60) + 30,
                    submissions_today=np.random.poisson(3),
                    avg_photo_size_kb=np.random.normal(500, 100),
                    hour_of_day=int(np.random.normal(12, 4)) % 24,
                    day_of_week=np.random.randint(0, 7),
                    installer_rpi=np.random.normal(80, 10)
                )
            else:
                # Generate anomalous submission
                features = SubmissionFeatures(
                    geo_distance_m=np.random.uniform(200, 1000),
                    time_since_last_mins=np.random.uniform(1, 10),
                    submissions_today=np.random.randint(10, 25),
                    avg_photo_size_kb=np.random.choice([30, 50, 6000]),
                    hour_of_day=np.random.choice([2, 3, 4, 23]),
                    day_of_week=np.random.randint(0, 7),
                    installer_rpi=np.random.uniform(20, 50)
                )
            
            data.append(features)
        
        return data


# Singleton instance
_detector: Optional[AnomalyDetector] = None


def get_anomaly_detector() -> AnomalyDetector:
    """Get or create the anomaly detector singleton."""
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
    return _detector
