"""
EC2 and Security Group Detector
"""

import uuid
import boto3
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class EC2Detector:
    """Detect EC2 security issues"""
    
    def __init__(self):
        self.ec2_client = boto3.client('ec2')
    
    def scan(self) -> List[Dict]:
        """Scan EC2 for security issues"""
        findings = []
        
        logger.info("🔍 Scanning EC2 & Security Groups...")
        
        try:
            # Check security groups
            sg_findings = self._check_security_groups()
            findings.extend(sg_findings)
            
            # Check instances
            instance_findings = self._check_instances()
            findings.extend(instance_findings)
        
        except Exception as e:
            logger.error(f"Error scanning EC2: {e}")
        
        logger.info(f"✅ EC2 scan complete: {len(findings)} issues found")
        return findings
    
    def _check_security_groups(self) -> List[Dict]:
        """Check for overly permissive security groups"""
        findings = []
        
        try:
            response = self.ec2_client.describe_security_groups()
            
            for sg in response.get('SecurityGroups', []):
                sg_id = sg['GroupId']
                sg_name = sg['GroupName']
                
                # Check inbound rules
                for rule in sg.get('IpPermissions', []):
                    from_port = rule.get('FromPort', 0)
                    to_port = rule.get('ToPort', 65535)
                    
                    # Check for 0.0.0.0/0 (open to world)
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            findings.append({
                                'finding_id': str(uuid.uuid4()),
                                'resource_type': 'ec2',
                                'finding_type': 'open_security_group',
                                'is_public': 1,
                                'is_encrypted': 0,
                                'port_exposed': from_port,
                                'description': f'Security group "{sg_name}" allows inbound traffic from 0.0.0.0/0 on port {from_port}',
                                'resource_id': sg_id
                            })
                            logger.warning(f"  ⚠️  OPEN SG: {sg_name} (Port {from_port})")
        
        except Exception as e:
            logger.error(f"Error checking security groups: {e}")
        
        return findings
    
    def _check_instances(self) -> List[Dict]:
        """Check for EC2 instances with public IPs"""
        findings = []
        
        try:
            response = self.ec2_client.describe_instances()
            
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_id = instance['InstanceId']
                    
                    # Check for public IP
                    if instance.get('PublicIpAddress'):
                        logger.debug(f"📌 {instance_id} has public IP")
        
        except Exception as e:
            logger.error(f"Error checking instances: {e}")
        
        return findings