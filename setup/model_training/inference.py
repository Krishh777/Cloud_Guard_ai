"""
Load trained model and make predictions
Used by Cloud Layer
"""

import os
import json
import joblib
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ModelInference:
    """Load and use trained models"""
    
    def __init__(self, models_dir='./setup/model_training/output'):
        self.models_dir = models_dir
        self.severity_model = None
        self.risk_model = None
        self.cost_model = None
        self.encoders = None
        self.metadata = None
        
        self._load_models()
    
    def _load_models(self):
        """Load saved models"""
        try:
            self.severity_model = joblib.load(
                os.path.join(self.models_dir, 'severity_model.pkl')
            )
            self.risk_model = joblib.load(
                os.path.join(self.models_dir, 'risk_model.pkl')
            )
            self.cost_model = joblib.load(
                os.path.join(self.models_dir, 'cost_model.pkl')
            )
            self.encoders = joblib.load(
                os.path.join(self.models_dir, 'encoders.pkl')
            )
            
            with open(os.path.join(self.models_dir, 'metadata.json')) as f:
                self.metadata = json.load(f)
            
            logger.info("✅ Models loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            raise
    
    def predict(self, features):
        """Make prediction on features"""
        try:
            X = np.array([features])
            
            severity = self.severity_model.predict(X)[0]
            risk_score = float(self.risk_model.predict(X)[0])
            breach_cost = float(self.cost_model.predict(X)[0])
            
            # Clamp values
            risk_score = max(0, min(100, risk_score))
            breach_cost = max(0, breach_cost)
            
            return {
                'severity': severity,
                'risk_score': risk_score,
                'estimated_breach_cost': int(breach_cost),
                'model_version': self.metadata.get('model_version'),
                'confidence': 0.85
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None


if __name__ == '__main__':
    # Test
    inference = ModelInference()
    
    # Test features
    test_features = [1, 0, 0, 0, 0, 2]  # public S3 bucket
    
    result = inference.predict(test_features)
    print(json.dumps(result, indent=2))