"""
API endpoint tests
"""

import unittest
from fastapi.testclient import TestClient

class TestCloudLayerAPI(unittest.TestCase):
    """Test Cloud Layer API"""
    
    def setUp(self):
        """Setup test client"""
        try:
            from cloud_layer.main_with_custom_model import app
            self.client = TestClient(app)
        except:
            self.skipTest("Cloud Layer not available")
    
    def test_health_check(self):
        """Test health endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

class TestFogLayerAPI(unittest.TestCase):
    """Test Fog Layer API"""
    
    def setUp(self):
        """Setup test client"""
        try:
            from fog_layer.main import app
            self.client = TestClient(app)
        except:
            self.skipTest("Fog Layer not available")
    
    def test_health_check(self):
        """Test health endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()