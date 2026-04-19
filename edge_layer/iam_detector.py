"""
IAM Security Detector
"""

import uuid
import boto3
import logging
from typing import List, Dict
import csv
from io import StringIO

logger = logging.getLogger(__name__)

class IAMDetector:
    """Detect IAM security issues"""
    
    def __init__(self):
        self.iam_client = boto3.client('iam')
    
    def scan(self) -> List[Dict]:
        """Scan IAM for security issues"""
        findings = []
        
        logger.info("🔍 Scanning IAM...")
        
        try:
            # Check MFA
            mfa_findings = self._check_mfa()
            findings.extend(mfa_findings)
            
            # Check root account
            root_findings = self._check_root_account()
            findings.extend(root_findings)
        
        except Exception as e:
            logger.error(f"Error scanning IAM: {e}")
        
        logger.info(f"✅ IAM scan complete: {len(findings)} issues found")
        return findings
    
    def _check_mfa(self) -> List[Dict]:
        """Check if MFA is enabled for users"""
        findings = []
        
        try:
            # Get all users
            response = self.iam_client.list_users()
            
            for user in response.get('Users', []):
                username = user['UserName']
                
                if username == 'root':
                    continue
                
                # Check MFA devices
                mfa_response = self.iam_client.list_mfa_devices(UserName=username)
                
                if not mfa_response.get('MFADevices'):
                    findings.append({
                        'finding_id': str(uuid.uuid4()),
                        'resource_type': 'iam',
                        'finding_type': 'mfa_not_enabled',
                        'is_public': 0,
                        'is_encrypted': 0,
                        'port_exposed': 0,
                        'description': f'IAM user "{username}" does not have MFA enabled',
                        'resource_id': username
                    })
                    logger.warning(f"  ⚠️  NO MFA: {username}")
        
        except Exception as e:
            logger.debug(f"Could not check MFA: {e}")
        
        return findings
    
    def _check_root_account(self) -> List[Dict]:
        """Check if root account has access keys"""
        findings = []
        
        try:
            # Generate credential report
            self.iam_client.generate_credential_report()
            
            import time
            time.sleep(2)  # Wait for report generation
            
            response = self.iam_client.get_credential_report()
            content = response['Content'].decode('utf-8')
            
            reader = csv.DictReader(StringIO(content))
            
            for row in reader:
                if row.get('user') == '<root_account>':
                    # Check for access keys
                    if row.get('access_key_1_active') == 'true' or row.get('access_key_2_active') == 'true':
                        findings.append({
                            'finding_id': str(uuid.uuid4()),
                            'resource_type': 'iam',
                            'finding_type': 'iam_root_usage',
                            'is_public': 1,
                            'is_encrypted': 0,
                            'port_exposed': 0,
                            'description': 'Root account has active access keys',
                            'resource_id': 'root'
                        })
                        logger.warning(f"  ⚠️  ROOT ACCOUNT HAS ACCESS KEYS")
        
        except Exception as e:
            logger.debug(f"Could not check root account: {e}")
        
        return findings