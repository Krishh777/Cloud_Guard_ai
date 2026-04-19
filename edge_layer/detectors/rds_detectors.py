"""
RDS Database Detector
"""

import uuid
import boto3
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class RDSDetector:
    """Detect RDS security issues"""
    
    def __init__(self):
        self.rds_client = boto3.client('rds')
    
    def scan(self) -> List[Dict]:
        """Scan RDS for security issues"""
        findings = []
        
        logger.info("🔍 Scanning RDS Instances...")
        
        try:
            response = self.rds_client.describe_db_instances()
            
            for db in response.get('DBInstances', []):
                db_id = db['DBInstanceIdentifier']
                is_public = 1 if db.get('PubliclyAccessible') else 0
                is_encrypted = 1 if db.get('StorageEncrypted') else 0
                port = int(db.get('Endpoint', {}).get('Port', 5432))
                
                # Check if public
                if is_public:
                    findings.append({
                        'finding_id': str(uuid.uuid4()),
                        'resource_type': 'rds',
                        'finding_type': 'public_rds',
                        'is_public': 1,
                        'is_encrypted': is_encrypted,
                        'port_exposed': port,
                        'description': f'RDS instance "{db_id}" is publicly accessible',
                        'resource_id': db_id
                    })
                    logger.warning(f"  ⚠️  PUBLIC RDS: {db_id}")
                
                # Check if encrypted
                if not is_encrypted:
                    findings.append({
                        'finding_id': str(uuid.uuid4()),
                        'resource_type': 'rds',
                        'finding_type': 'unencrypted_rds',
                        'is_public': is_public,
                        'is_encrypted': 0,
                        'port_exposed': port,
                        'description': f'RDS instance "{db_id}" does not have encryption enabled',
                        'resource_id': db_id
                    })
                    logger.warning(f"  ⚠️  UNENCRYPTED RDS: {db_id}")
        
        except Exception as e:
            logger.error(f"Error scanning RDS: {e}")
        
        logger.info(f"✅ RDS scan complete: {len(findings)} issues found")
        return findings