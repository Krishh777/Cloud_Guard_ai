"""
DynamoDB Cache Layer
Store findings temporarily with TTL
"""

import os
import json
import boto3
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DynamoDBCache:
    """Cache findings in DynamoDB"""
    
    def __init__(self):
        self.dynamodb = None
        self.table = None
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'cloudguard-cache')
        self.ttl = int(os.getenv('DYNAMODB_TTL', '3600'))  # 1 hour default
        self.enabled = os.getenv('USE_CACHE', 'True') == 'True'
        
        try:
            if self.enabled:
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=os.getenv('DYNAMODB_REGION', 'us-east-1')
                )
                self.table = self.dynamodb.Table(self.table_name)
                logger.info(f"✅ DynamoDB cache initialized: {self.table_name}")
            else:
                logger.info("⚠️  DynamoDB cache disabled (USE_CACHE=False)")
        
        except Exception as e:
            logger.warning(f"⚠️  DynamoDB not available: {e}")
            logger.info("   Continuing without caching...")
            self.enabled = False
    
    def cache_finding(self, finding: dict):
        """Save finding to DynamoDB cache"""
        if not self.enabled or not self.table:
            logger.debug(f"💾 Cache disabled, skipping: {finding.get('finding_id')}")
            return
        
        try:
            # Add TTL (expires in 1 hour)
            expiration_time = int((datetime.now() + timedelta(seconds=self.ttl)).timestamp())
            
            item = {
                'finding_id': finding['finding_id'],
                'data': json.dumps(finding),
                'ttl': expiration_time,
                'created_at': datetime.now().isoformat(),
                'severity': finding.get('severity', 'unknown'),
                'resource_type': finding.get('resource_type', 'unknown')
            }
            
            self.table.put_item(Item=item)
            logger.debug(f"💾 Cached finding: {finding['finding_id']}")
        
        except Exception as e:
            logger.warning(f"⚠️  Could not cache finding: {e}")
    
    def get_finding(self, finding_id: str):
        """Retrieve finding from cache"""
        if not self.enabled or not self.table:
            return None
        
        try:
            response = self.table.get_item(Key={'finding_id': finding_id})
            
            if 'Item' in response:
                data = json.loads(response['Item']['data'])
                logger.debug(f"✅ Retrieved from cache: {finding_id}")
                return data
            
            return None
        
        except Exception as e:
            logger.warning(f"Could not retrieve from cache: {e}")
            return None
    
    def get_findings_by_severity(self, severity: str):
        """Get all findings of specific severity from cache"""
        if not self.enabled or not self.table:
            return []
        
        try:
            response = self.table.scan(
                FilterExpression='severity = :sev',
                ExpressionAttributeValues={':sev': severity}
            )
            
            findings = []
            for item in response.get('Items', []):
                findings.append(json.loads(item['data']))
            
            logger.debug(f"Retrieved {len(findings)} findings with severity={severity}")
            return findings
        
        except Exception as e:
            logger.warning(f"Could not scan cache: {e}")
            return []
    
    def get_all_cached_findings(self):
        """Get all findings from cache"""
        if not self.enabled or not self.table:
            return []
        
        try:
            response = self.table.scan()
            
            findings = []
            for item in response.get('Items', []):
                findings.append(json.loads(item['data']))
            
            logger.info(f"Retrieved {len(findings)} findings from cache")
            return findings
        
        except Exception as e:
            logger.warning(f"Could not scan cache: {e}")
            return []
    
    def delete_finding(self, finding_id: str):
        """Delete finding from cache"""
        if not self.enabled or not self.table:
            return
        
        try:
            self.table.delete_item(Key={'finding_id': finding_id})
            logger.debug(f"🗑️  Deleted from cache: {finding_id}")
        
        except Exception as e:
            logger.warning(f"Could not delete from cache: {e}")
    
    def clear_cache(self):
        """Clear all findings from cache"""
        if not self.enabled or not self.table:
            return
        
        try:
            findings = self.get_all_cached_findings()
            
            for finding in findings:
                self.delete_finding(finding['finding_id'])
            
            logger.info(f"🗑️  Cleared {len(findings)} items from cache")
        
        except Exception as e:
            logger.warning(f"Could not clear cache: {e}")