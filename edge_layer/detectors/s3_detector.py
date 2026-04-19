"""
S3 Bucket Security Detector
"""

import uuid
import boto3
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class S3Detector:
    """Detect S3 security issues"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
    
    def scan(self) -> List[Dict]:
        """Scan S3 buckets for security issues"""
        findings = []
        
        logger.info("🔍 Scanning S3 Buckets...")
        
        try:
            # List all buckets
            response = self.s3_client.list_buckets()
            buckets = response.get('Buckets', [])
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                
                # Check if public
                public_findings = self._check_public_access(bucket_name)
                findings.extend(public_findings)
                
                # Check encryption
                encryption_findings = self._check_encryption(bucket_name)
                findings.extend(encryption_findings)
                
                # Check versioning
                versioning_findings = self._check_versioning(bucket_name)
                findings.extend(versioning_findings)
        
        except Exception as e:
            logger.error(f"Error scanning S3: {e}")
        
        logger.info(f"✅ S3 scan complete: {len(findings)} issues found")
        return findings
    
    def _check_public_access(self, bucket_name: str) -> List[Dict]:
        """Check if bucket is publicly accessible"""
        findings = []
        
        try:
            acl = self.s3_client.get_bucket_acl(Bucket=bucket_name)
            
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                
                # Check for public access
                if grantee.get('Type') == 'Group':
                    if 'AllUsers' in grantee.get('URI', ''):
                        findings.append({
                            'finding_id': str(uuid.uuid4()),
                            'resource_type': 's3',
                            'finding_type': 'public_s3_bucket',
                            'is_public': 1,
                            'is_encrypted': 0,
                            'port_exposed': 0,
                            'description': f'S3 bucket "{bucket_name}" is publicly accessible (AllUsers)',
                            'resource_id': bucket_name
                        })
                        logger.warning(f"  ⚠️  PUBLIC BUCKET: {bucket_name}")
        
        except Exception as e:
            logger.debug(f"Could not check public access for {bucket_name}: {e}")
        
        return findings
    
    def _check_encryption(self, bucket_name: str) -> List[Dict]:
        """Check if bucket has default encryption enabled"""
        findings = []
        
        try:
            response = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
            logger.debug(f"✅ {bucket_name} has encryption enabled")
        
        except self.s3_client.exceptions.ServerSideEncryptionConfigurationNotFoundError:
            findings.append({
                'finding_id': str(uuid.uuid4()),
                'resource_type': 's3',
                'finding_type': 'unencrypted_s3',
                'is_public': 0,
                'is_encrypted': 0,
                'port_exposed': 0,
                'description': f'S3 bucket "{bucket_name}" does not have default encryption enabled',
                'resource_id': bucket_name
            })
            logger.warning(f"  ⚠️  UNENCRYPTED: {bucket_name}")
        
        except Exception as e:
            logger.debug(f"Could not check encryption for {bucket_name}: {e}")
        
        return findings
    
    def _check_versioning(self, bucket_name: str) -> List[Dict]:
        """Check if bucket has versioning enabled"""
        findings = []
        
        try:
            response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
            status = response.get('Status', '')
            
            if status != 'Enabled':
                logger.debug(f"⚠️  {bucket_name} does not have versioning enabled")
        
        except Exception as e:
            logger.debug(f"Could not check versioning for {bucket_name}: {e}")
        
        return findings