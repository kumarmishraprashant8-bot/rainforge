"""ML Yield Prediction Service using scikit-learn."""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import logging

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class YieldFeatures:
    """Features for yield prediction."""
    roof_area_sqm: float
    surface_type: str  # concrete, metal, tile, other
    monthly_rainfall_mm: float
    temperature_avg: float
    month: int  # 1-12
    latitude: float
    longitude: float
    tank_capacity_liters: float
    runoff_coefficient: float  # from surface type


@dataclass
class YieldPrediction:
    """Yield prediction result."""
    predicted_liters: float
    confidence_low: float
    confidence_high: float
    forecast_period_days: int
    model_version: str
    factors: Dict[str, float]  # Feature importances


class YieldPredictor:
    """
    ML model for predicting rainwater harvesting yield.
    Uses RandomForest with weather and site features.
    """
    
    MODEL_PATH = Path("models/yield_predictor.pkl")
    MODEL_VERSION = "1.0.0"
    
    # Runoff coefficients by surface type
    RUNOFF_COEFFICIENTS = {
        "metal": 0.90,
        "concrete": 0.85,
        "tile": 0.75,
        "asphalt": 0.80,
        "other": 0.70
    }
    
    # Average monthly rainfall by region (demo data for India)
    MONTHLY_RAINFALL_AVG = {
        1: 15, 2: 20, 3: 25, 4: 30, 5: 50,
        6: 180, 7: 280, 8: 260, 9: 180, 10: 80,
        11: 30, 12: 15
    }
    
    def __init__(self):
        self.model: Optional[Pipeline] = None
        self.is_trained = False
        self.feature_importances: Dict[str, float] = {}
        
        if SKLEARN_AVAILABLE:
            self._load_model()
    
    def _load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            if self.MODEL_PATH.exists():
                with open(self.MODEL_PATH, "rb") as f:
                    data = pickle.load(f)
                    self.model = data["model"]
                    self.feature_importances = data.get("importances", {})
                    self.is_trained = True
                    logger.info("Loaded yield prediction model")
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
                    "importances": self.feature_importances,
                    "version": self.MODEL_VERSION,
                    "trained_at": datetime.utcnow().isoformat()
                }, f)
            logger.info("Saved yield prediction model")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def _features_to_array(self, features: YieldFeatures) -> np.ndarray:
        """Convert features to array format."""
        # Encode month as cyclical features
        month_sin = np.sin(2 * np.pi * features.month / 12)
        month_cos = np.cos(2 * np.pi * features.month / 12)
        
        # Surface type encoding (one-hot would be done in pipeline)
        surface_encoded = list(self.RUNOFF_COEFFICIENTS.keys()).index(
            features.surface_type if features.surface_type in self.RUNOFF_COEFFICIENTS 
            else "other"
        )
        
        return np.array([[
            features.roof_area_sqm,
            features.monthly_rainfall_mm,
            features.temperature_avg,
            month_sin,
            month_cos,
            features.latitude,
            features.longitude,
            features.tank_capacity_liters,
            features.runoff_coefficient,
            surface_encoded
        ]])
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train the yield prediction model.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target values (liters/month)
        """
        if not SKLEARN_AVAILABLE:
            logger.error("Cannot train: scikit-learn not installed")
            return
        
        logger.info(f"Training yield predictor on {len(X)} samples...")
        
        # Create pipeline with preprocessing
        self.model = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            ))
        ])
        
        # Split for evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X, y, cv=5, scoring='neg_mean_absolute_error'
        )
        
        logger.info(f"Model trained - MAE: {mae:.2f}L, CV MAE: {-cv_scores.mean():.2f}L")
        
        # Store feature importances
        feature_names = [
            "roof_area", "rainfall", "temperature", "month_sin", "month_cos",
            "latitude", "longitude", "tank_capacity", "runoff_coef", "surface"
        ]
        importances = self.model.named_steps['regressor'].feature_importances_
        self.feature_importances = dict(zip(feature_names, importances))
        
        self.is_trained = True
        self._save_model()
    
    def predict(self, features: YieldFeatures, forecast_days: int = 30) -> YieldPrediction:
        """
        Predict yield for given features.
        Falls back to physics-based calculation if model not trained.
        """
        # Physics-based baseline calculation
        baseline = self._physics_based_prediction(features, forecast_days)
        
        if self.is_trained and self.model is not None:
            try:
                X = self._features_to_array(features)
                prediction = self.model.predict(X)[0]
                
                # Scale to forecast period
                daily_prediction = prediction / 30
                period_prediction = daily_prediction * forecast_days
                
                # Confidence interval (approximate)
                std_estimate = abs(period_prediction - baseline) * 0.3 + period_prediction * 0.1
                
                return YieldPrediction(
                    predicted_liters=round(period_prediction, 1),
                    confidence_low=round(max(0, period_prediction - 2 * std_estimate), 1),
                    confidence_high=round(period_prediction + 2 * std_estimate, 1),
                    forecast_period_days=forecast_days,
                    model_version=self.MODEL_VERSION,
                    factors=self.feature_importances
                )
            except Exception as e:
                logger.error(f"ML prediction failed: {e}, using physics-based")
        
        # Fallback to physics-based
        return YieldPrediction(
            predicted_liters=round(baseline, 1),
            confidence_low=round(baseline * 0.7, 1),
            confidence_high=round(baseline * 1.3, 1),
            forecast_period_days=forecast_days,
            model_version="physics-v1",
            factors={"rainfall": 0.5, "roof_area": 0.3, "runoff": 0.2}
        )
    
    def _physics_based_prediction(self, features: YieldFeatures, days: int) -> float:
        """
        Calculate yield using the rational method.
        Q = C * I * A * efficiency
        """
        collection_efficiency = 0.85  # First-flush + losses
        
        # Daily rainfall (convert monthly to daily)
        daily_rainfall_mm = features.monthly_rainfall_mm / 30
        
        # Calculate daily yield
        daily_yield = (
            features.roof_area_sqm *      # m²
            daily_rainfall_mm *            # mm = L/m²
            features.runoff_coefficient *  # dimensionless
            collection_efficiency          # dimensionless
        )
        
        return daily_yield * days
    
    def generate_training_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data based on physics model."""
        np.random.seed(42)
        
        X_list = []
        y_list = []
        
        for _ in range(n_samples):
            # Random site parameters
            roof_area = np.random.uniform(50, 500)
            surface_type = np.random.choice(list(self.RUNOFF_COEFFICIENTS.keys()))
            runoff_coef = self.RUNOFF_COEFFICIENTS[surface_type]
            month = np.random.randint(1, 13)
            
            # Seasonal rainfall with noise
            base_rainfall = self.MONTHLY_RAINFALL_AVG[month]
            rainfall = max(0, base_rainfall * np.random.uniform(0.5, 1.5))
            
            temperature = 25 + 10 * np.sin(2 * np.pi * (month - 4) / 12)
            temperature += np.random.normal(0, 3)
            
            # Random Indian coordinates
            lat = np.random.uniform(8, 35)
            lng = np.random.uniform(68, 97)
            tank_capacity = np.random.uniform(5000, 50000)
            
            features = YieldFeatures(
                roof_area_sqm=roof_area,
                surface_type=surface_type,
                monthly_rainfall_mm=rainfall,
                temperature_avg=temperature,
                month=month,
                latitude=lat,
                longitude=lng,
                tank_capacity_liters=tank_capacity,
                runoff_coefficient=runoff_coef
            )
            
            # Calculate "true" yield with noise
            true_yield = self._physics_based_prediction(features, 30)
            noisy_yield = true_yield * np.random.uniform(0.8, 1.2)
            
            X_list.append(self._features_to_array(features).flatten())
            y_list.append(noisy_yield)
        
        return np.array(X_list), np.array(y_list)
    
    def get_forecast(
        self, 
        roof_area: float, 
        surface_type: str, 
        latitude: float, 
        longitude: float,
        tank_capacity: float = 10000,
        days_ahead: int = 7
    ) -> List[Dict]:
        """Get multi-day forecast."""
        forecasts = []
        today = datetime.now()
        
        for day_offset in range(days_ahead):
            forecast_date = today + timedelta(days=day_offset)
            month = forecast_date.month
            
            features = YieldFeatures(
                roof_area_sqm=roof_area,
                surface_type=surface_type,
                monthly_rainfall_mm=self.MONTHLY_RAINFALL_AVG.get(month, 50),
                temperature_avg=28,  # Would come from weather API
                month=month,
                latitude=latitude,
                longitude=longitude,
                tank_capacity_liters=tank_capacity,
                runoff_coefficient=self.RUNOFF_COEFFICIENTS.get(surface_type, 0.7)
            )
            
            prediction = self.predict(features, forecast_days=1)
            
            forecasts.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "predicted_liters": prediction.predicted_liters,
                "confidence_low": prediction.confidence_low,
                "confidence_high": prediction.confidence_high
            })
        
        return forecasts


# Singleton instance
_predictor: Optional[YieldPredictor] = None


def get_yield_predictor() -> YieldPredictor:
    """Get or create the yield predictor singleton."""
    global _predictor
    if _predictor is None:
        _predictor = YieldPredictor()
    return _predictor
