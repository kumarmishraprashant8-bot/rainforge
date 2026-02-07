import joblib
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

logger = logging.getLogger(__name__)

class DemandForecaster:
    """
    ML Service for Water Demand Forecasting.
    Uses RandomForestRegressor trained on historical data.
    """
    
    def __init__(self, model_path: str = None):
        self.model = None
        self._is_trained = False
        if model_path:
            self.load_model(model_path)
        else:
            # Train a mock model on startup for demo purposes
            self._train_mock_model()

    def _train_mock_model(self):
        """Train a lightweight model on synthetic data for the hackathon demo."""
        try:
            logger.info("Training mock forecast model...")
            # Synthetic features: [Month, AvgTemp, RoofArea, Occupants]
            # Target: Monthly Demand (Liters)
            X = []
            y = []
            
            # Generate 1000 samples
            time_features = list(range(1, 13)) * 85 # Monthly patterns
            
            import random
            random.seed(42)
            
            for month in range(1000):
                 m = (month % 12) + 1
                 temp = 25 + 5 * np.sin((m-1)/12 * 2 * np.pi) + random.normalvariate(0, 2)
                 roof_area = random.uniform(50, 200)
                 occupants = random.randint(2, 6)
                 
                 # Logic: Demand = Base(135L/person/day) + Seasonality + Random
                 # Summer (months 3-5) higher demand
                 season_factor = 1.2 if m in [3, 4, 5] else 1.0
                 base_demand = occupants * 135 * 30 * season_factor
                 
                 # RWH Usage offsets demand? No, this is total demand prediction.
                 
                 X.append([m, temp, roof_area, occupants])
                 y.append(base_demand)
            
            self.model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
            self.model.fit(X, y)
            self._is_trained = True
            logger.info("Mock model trained successfully.")
            
        except Exception as e:
            logger.error(f"Failed to train mock model: {e}")

    def predict_demand(self, month: int, avg_temp: float, roof_area: float, occupants: int) -> Dict[str, Any]:
        """
        Predict water demand for specific conditions.
        """
        if not self._is_trained or not self.model:
            return {"error": "Model not trained"}
            
        try:
            # Input vector must match training features
            X_pred = [[month, avg_temp, roof_area, occupants]]
            prediction = self.model.predict(X_pred)[0]
            
            # Calculate naive confidence interval (mock)
            confidence = 0.85 + (0.1 / (1 + abs(avg_temp - 25)/10))
            
            return {
                "predicted_demand_liters": round(prediction, 0),
                "confidence_score": round(confidence, 2),
                "model_version": "v1.0-mock",
                "factors": {
                    "seasonality": "High" if month in [3,4,5] else "Normal",
                    "occupancy_impact": f"{occupants} persons"
                }
            }
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {"error": str(e)}

# Singleton
forecaster = DemandForecaster()

def get_forecaster():
    return forecaster
