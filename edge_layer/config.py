"""
Edge Layer Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_PROFILE = os.getenv('AWS_PROFILE', 'default')

# Scan Configuration
SCAN_INTERVAL = int(os.getenv('EDGE_SCANNER_INTERVAL', '3600'))  # 1 hour

# API Configuration
FOG_API_ENDPOINT = os.getenv('FOG_API_ENDPOINT', 'http://localhost:8001')
CLOUD_API_ENDPOINT = os.getenv('CLOUD_API_ENDPOINT', 'http://localhost:8000')

# Detectors to enable
DETECTORS = {
    'S3': True,
    'EC2': True,
    'RDS': True,
    'SecurityGroups': True,
    'IAM': True,
    'CloudTrail': False,  # Optional
}

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Feature flags
SAVE_TO_DATABASE = os.getenv('SAVE_TO_DATABASE', 'True') == 'True'
USE_CACHE = os.getenv('USE_CACHE', 'True') == 'True'
SEND_ALERTS = os.getenv('SEND_ALERTS', 'False') == 'True'