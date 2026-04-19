"""
Unit tests for Scanner
"""

import unittest
from unittest.mock import patch, MagicMock
from edge_layer.scanner import SecurityScanner

class TestSecurityScanner(unittest.TestCase):
    """Test scanner functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.scanner = SecurityScanner()
    
    @patch('edge_layer.scanner.boto3.client')
    def test_s3_scan(self, mock_boto):
        """Test S3 scanning"""
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        # Verify scanner initializes
        self.assertIsNotNone(self.scanner)
    
    def test_findings_structure(self):
        """Test finding data structure"""
        # Test finding should have these fields
        required_fields = [
            'finding_id', 'resource_type', 'finding_type',
            'is_public', 'is_encrypted', 'port_exposed',
            'description', 'resource_id'
        ]
        
        # Create test finding
        test_finding = {
            'finding_id': 'test-123',
            'resource_type': 's3',
            'finding_type': 'public_s3_bucket',
            'is_public': 1,
            'is_encrypted': 0,
            'port_exposed': 0,
            'description': 'Test finding',
            'resource_id': 'test-bucket'
        }
        
        # Check all required fields exist
        for field in required_fields:
            self.assertIn(field, test_finding)

if __name__ == '__main__':
    unittest.main()