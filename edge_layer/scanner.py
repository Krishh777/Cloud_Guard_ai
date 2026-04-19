"""
Edge Layer - Security Scanner
Scans your AWS account for security issues
NO DOCKER VERSION - Runs directly on your laptop
"""

import os
import json
import uuid
import boto3
import logging
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize AWS clients with your profile
session = boto3.Session(
    profile_name=os.getenv('AWS_PROFILE', 'default'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

ec2_client = session.client('ec2')
s3_client = session.client('s3')
rds_client = session.client('rds')
iam_client = session.client('iam')

FOG_API = os.getenv('FOG_API_ENDPOINT', 'http://localhost:8001')

class SecurityScanner:
    """Scans AWS for security issues"""
    
    def __init__(self):
        self.findings = []
    
    def scan_s3_buckets(self):
        """Scan S3 buckets for public access and encryption"""
        logger.info("🔍 Scanning S3 Buckets...")
        
        try:
            response = s3_client.list_buckets()
            buckets = response.get('Buckets', [])
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                
                # Check if bucket is public
                try:
                    acl = s3_client.get_bucket_acl(Bucket=bucket_name)
                    
                    for grant in acl.get('Grants', []):
                        grantee = grant.get('Grantee', {})
                        
                        # Check for public access
                        if grantee.get('Type') == 'Group' and \
                           'AllUsers' in grantee.get('URI', ''):
                            
                            self.findings.append({
                                'finding_id': str(uuid.uuid4()),
                                'resource_type': 's3',
                                'finding_type': 'public_s3_bucket',
                                'is_public': 1,
                                'is_encrypted': 0,
                                'port_exposed': 0,
                                'description': f'S3 bucket "{bucket_name}" is publicly accessible',
                                'resource_id': bucket_name
                            })
                            
                            logger.warning(f"  ⚠️  PUBLIC BUCKET FOUND: {bucket_name}")
                
                except Exception as e:
                    logger.debug(f"Could not check bucket {bucket_name}: {e}")
                
                # Check encryption
                try:
                    s3_client.get_bucket_encryption(Bucket=bucket_name)
                    logger.debug(f"✅ {bucket_name} has encryption enabled")
                except s3_client.exceptions.ServerSideEncryptionConfigurationNotFoundError:
                    self.findings.append({
                        'finding_id': str(uuid.uuid4()),
                        'resource_type': 's3',
                        'finding_type': 'unencrypted_s3',
                        'is_public': 0,
                        'is_encrypted': 0,
                        'port_exposed': 0,
                        'description': f'S3 bucket "{bucket_name}" does not have default encryption',
                        'resource_id': bucket_name
                    })
                    logger.warning(f"  ⚠️  UNENCRYPTED: {bucket_name}")
        
        except Exception as e:
            logger.error(f"Error scanning S3: {e}")
    
    def scan_security_groups(self):
        """Scan EC2 security groups for open ports"""
        logger.info("🔍 Scanning Security Groups...")
        
        try:
            response = ec2_client.describe_security_groups()
            
            for sg in response.get('SecurityGroups', []):
                sg_id = sg['GroupId']
                sg_name = sg['GroupName']
                
                # Skip default security group
                if sg_name == 'default':
                    continue
                
                # Check for open to 0.0.0.0/0
                for rule in sg.get('IpPermissions', []):
                    from_port = rule.get('FromPort', 0)
                    
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            
                            self.findings.append({
                                'finding_id': str(uuid.uuid4()),
                                'resource_type': 'ec2',
                                'finding_type': 'open_security_group',
                                'is_public': 1,
                                'is_encrypted': 0,
                                'port_exposed': from_port,
                                'description': f'Security group "{sg_name}" allows inbound traffic from 0.0.0.0/0 on port {from_port}',
                                'resource_id': sg_id
                            })
                            
                            logger.warning(f"  ⚠️  OPEN SG FOUND: {sg_name} - Port {from_port}")
        
        except Exception as e:
            logger.error(f"Error scanning security groups: {e}")
    
    def scan_rds_instances(self):
        """Scan RDS for public accessibility and encryption"""
        logger.info("🔍 Scanning RDS Instances...")
        
        try:
            response = rds_client.describe_db_instances()
            
            for db in response.get('DBInstances', []):
                db_id = db['DBInstanceIdentifier']
                is_public = 1 if db.get('PubliclyAccessible') else 0
                is_encrypted = 1 if db.get('StorageEncrypted') else 0
                port = int(db.get('Endpoint', {}).get('Port', 5432))
                
                # Check if public
                if is_public:
                    self.findings.append({
                        'finding_id': str(uuid.uuid4()),
                        'resource_type': 'rds',
                        'finding_type': 'public_rds',
                        'is_public': 1,
                        'is_encrypted': is_encrypted,
                        'port_exposed': port,
                        'description': f'RDS instance "{db_id}" is publicly accessible',
                        'resource_id': db_id
                    })
                    
                    logger.warning(f"  ⚠️  PUBLIC RDS FOUND: {db_id}")
                
                # Check if not encrypted
                if not is_encrypted:
                    self.findings.append({
                        'finding_id': str(uuid.uuid4()),
                        'resource_type': 'rds',
                        'finding_type': 'unencrypted_rds',
                        'is_public': is_public,
                        'is_encrypted': 0,
                        'port_exposed': port,
                        'description': f'RDS instance "{db_id}" does not have encryption enabled',
                        'resource_id': db_id
                    })
                    
                    logger.warning(f"  ⚠️  UNENCRYPTED RDS FOUND: {db_id}")
        
        except Exception as e:
            logger.error(f"Error scanning RDS: {e}")
    
    def scan_iam(self):
        """Scan IAM for security issues"""
        logger.info("🔍 Scanning IAM...")
        
        try:
            # List users
            response = iam_client.list_users()
            
            for user in response.get('Users', []):
                username = user['UserName']
                
                if username == 'root':
                    continue
                
                # Check MFA
                mfa_response = iam_client.list_mfa_devices(UserName=username)
                
                if not mfa_response.get('MFADevices'):
                    self.findings.append({
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
            logger.error(f"Error scanning IAM: {e}")
    
    def send_to_fog_layer(self):
        """Send findings to Fog Layer"""
        if not self.findings:
            return
        
        logger.info(f"\n📤 Sending {len(self.findings)} findings to Fog Layer...")
        
        for finding in self.findings:
            try:
                response = requests.post(
                    f"{FOG_API}/enrich",
                    json=finding,
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info(f"  ✅ {finding['finding_id']}")
                else:
                    logger.warning(f"  ⚠️  Status {response.status_code}: {finding['finding_id']}")
            
            except Exception as e:
                logger.error(f"  ❌ Failed to send: {e}")
    
    def run_scan(self):
        """Run complete security scan"""
        logger.info("\n" + "="*60)
        logger.info("🚀 STARTING CLOUDGUARD SECURITY SCAN")
        logger.info("="*60 + "\n")
        
        start_time = time.time()
        
        self.scan_s3_buckets()
        self.scan_security_groups()
        self.scan_rds_instances()
        self.scan_iam()
        
        duration = time.time() - start_time
        
        logger.info("\n" + "-"*60)
        logger.info(f"✅ SCAN COMPLETE - Found {len(self.findings)} security issues")
        logger.info(f"⏱️  Scan duration: {duration:.2f} seconds")
        logger.info("-"*60 + "\n")
        
        # Send to Fog Layer
        if self.findings:
            self.send_to_fog_layer()
        else:
            logger.info("✅ No findings detected!")

if __name__ == '__main__':
    scanner = SecurityScanner()
    scanner.run_scan()