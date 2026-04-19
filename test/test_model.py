"""
Unit tests for ML Model
"""

import unittest
import numpy as np
from setup.model_training.inference import ModelInference

class TestModelInference(unittest.TestCase):
    """Test model inference"""
    
    def setUp(self):
        """Setup test fixtures"""
        try:
            self.inference = ModelInference()
        except:
            self.skipTest("Models not trained yet")
    
    def test_model_loads(self):
        """Test model loads successfully"""
        self.assertIsNotNone(self.inference.severity_model)
        self.assertIsNotNone(self.inference.risk_model)
        self.assertIsNotNone(self.inference.cost_model)
    
    def test_prediction_format(self):
        """Test prediction returns correct format"""
        # Test features
        features = [1, 0, 0, 0, 0, 2]
        
        result = self.inference.predict(features)
        
        # Check result structure
        self.assertIn('severity', result)
        self.assertIn('risk_score', result)
        self.assertIn('estimated_breach_cost', result)
    
    def test_risk_score_bounds(self):
        """Test risk score is within bounds (0-100)"""
        features = [1, 0, 0, 0, 0, 2]
        result = self.inference.predict(features)
        
        risk = result['risk_score']
        self.assertGreaterEqual(risk, 0)
        self.assertLessEqual(risk, 100)

if __name__ == '__main__':
    unittest.main()