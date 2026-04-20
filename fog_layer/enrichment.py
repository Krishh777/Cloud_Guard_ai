"""
Enrichment Engine
Calculates risk scores, business impact, and recommendations
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RiskEnrichment:
    """Calculate risk metrics and recommendations"""
    
    # Risk scoring matrix
    RISK_MATRIX = {
        'public_s3_bucket': {
            'base_score': 95,
            'factors': {'is_public': 50, 'is_encrypted': -20}
        },
        'open_security_group': {
            'base_score': 90,
            'factors': {'port_exposed': 10, 'is_public': 40}
        },
        'public_rds': {
            'base_score': 85,
            'factors': {'is_encrypted': -15, 'port_exposed': 5}
        },
        'unencrypted_rds': {
            'base_score': 70,
            'factors': {'is_public': 15}
        },
        'iam_root_usage': {
            'base_score': 90,
            'factors': {}
        },
        'cloudtrail_disabled': {
            'base_score': 75,
            'factors': {}
        },
        'unencrypted_s3': {
            'base_score': 65,
            'factors': {'is_public': 20}
        },
        'mfa_not_enabled': {
            'base_score': 70,
            'factors': {}
        }
    }
    
    # Business impact mapping
    IMPACT_MAPPING = {
        'critical': {
            'priority': 1,
            'sla_hours': 1,
            'business_impact': 90,
            'min_cost': 100000
        },
        'high': {
            'priority': 2,
            'sla_hours': 4,
            'business_impact': 70,
            'min_cost': 50000
        },
        'medium': {
            'priority': 3,
            'sla_hours': 24,
            'business_impact': 40,
            'min_cost': 10000
        },
        'low': {
            'priority': 4,
            'sla_hours': 72,
            'business_impact': 20,
            'min_cost': 1000
        }
    }
    
    @staticmethod
    def calculate_risk_score(finding: dict) -> float:
        """
        Calculate risk score (0-100)
        Based on finding type, public access, encryption, port exposure
        """
        finding_type = finding.get('finding_type', 'unknown')
        
        # Get base score
        if finding_type not in RiskEnrichment.RISK_MATRIX:
            return 50  # Default medium risk
        
        config = RiskEnrichment.RISK_MATRIX[finding_type]
        score = config['base_score']
        
        # Apply factors
        for factor, weight in config['factors'].items():
            value = finding.get(factor, 0)
            score += (value * weight / 100)
        
        # Normalize to 0-100
        score = max(0, min(100, score))
        
        logger.debug(f"Risk score for {finding_type}: {score:.2f}")
        
        return round(score, 2)
    
    @staticmethod
    def estimate_breach_cost(finding: dict, risk_score: float) -> int:
        """
        Estimate financial impact of breach
        Based on finding type and risk score
        """
        finding_type = finding.get('finding_type')
        resource_type = finding.get('resource_type')
        
        # Cost estimation matrix (in dollars)
        cost_matrix = {
            'public_s3_bucket': {
                'base': 500000,  # Data breach cost
                'per_record': 150  # GDPR: $150 per record
            },
            'open_security_group': {
                'base': 250000,
                'per_record': 100
            },
            'public_rds': {
                'base': 300000,
                'per_record': 200
            },
            'unencrypted_rds': {
                'base': 100000,
                'per_record': 100
            },
            'iam_root_usage': {
                'base': 200000,
                'per_record': 50
            },
            'cloudtrail_disabled': {
                'base': 75000,
                'per_record': 0
            },
            'unencrypted_s3': {
                'base': 50000,
                'per_record': 100
            },
            'mfa_not_enabled': {
                'base': 100000,
                'per_record': 0
            }
        }
        
        # Get base cost
        if finding_type in cost_matrix:
            base_cost = cost_matrix[finding_type]['base']
        else:
            base_cost = 50000  # Default
        
        # Adjust by risk score
        adjusted_cost = int(base_cost * (risk_score / 100))
        
        logger.debug(f"Estimated breach cost: ${adjusted_cost:,}")
        
        return adjusted_cost
    
    @staticmethod
    def determine_severity(risk_score: float) -> str:
        """
        Determine severity level based on risk score
        """
        if risk_score >= 80:
            return 'critical'
        elif risk_score >= 60:
            return 'high'
        elif risk_score >= 40:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def get_recommendation(finding_type: str) -> str:
        """Get detailed fix recommendation"""
        
        recommendations = {
            'public_s3_bucket': {
                'title': '🔒 Block S3 Public Access',
                'steps': [
                    '1. Go to S3 Console → Your Bucket',
                    '2. Click "Permissions" tab',
                    '3. Scroll to "Block public access (bucket settings)"',
                    '4. Click "Edit"',
                    '5. Check ALL 4 boxes:',
                    '   - ☑ Block all public access',
                    '   - ☑ Block public ACLs',
                    '   - ☑ Block public bucket policies',
                    '   - ☑ Block public object ACLs',
                    '6. Click "Save changes"',
                    '7. ✅ Done! Bucket is now private'
                ],
                'time_to_fix': '5 minutes',
                'difficulty': 'Easy'
            },
            
            'open_security_group': {
                'title': '🔒 Restrict Security Group',
                'steps': [
                    '1. Go to EC2 Console → Security Groups',
                    '2. Find the security group',
                    '3. Click "Edit inbound rules"',
                    '4. Find rules with "0.0.0.0/0" source',
                    '5. For each rule:',
                    '   - Change Source from "Anywhere" to specific IP',
                    '   - Use CIDR: 203.0.113.0/24 (your IP range)',
                    '6. Click "Save rules"',
                    '7. ✅ Now only your IPs can connect'
                ],
                'time_to_fix': '10 minutes',
                'difficulty': 'Easy'
            },
            
            'public_rds': {
                'title': '🔒 Disable RDS Public Access',
                'steps': [
                    '1. Go to RDS Console → Databases',
                    '2. Click your database name',
                    '3. Click "Modify" button',
                    '4. Scroll to "Connectivity"',
                    '5. Find "Publicly accessible" option',
                    '6. Change to "No"',
                    '7. Choose "Apply immediately"',
                    '8. Click "Modify database"',
                    '9. ✅ Database is now private'
                ],
                'time_to_fix': '5 minutes',
                'difficulty': 'Easy'
            },
            
            'unencrypted_rds': {
                'title': '🔒 Enable RDS Encryption',
                'steps': [
                    '1. Go to RDS Console → Databases',
                    '2. Click your database name',
                    '3. Click "Modify" button',
                    '4. Scroll to "Encryption"',
                    '5. Check "Enable encryption"',
                    '6. Select KMS key (or create new)',
                    '7. Choose "Apply immediately"',
                    '8. Click "Modify database"',
                    '9. ✅ Database encryption enabled',
                    'Note: You can create snapshot before modifying'
                ],
                'time_to_fix': '15 minutes',
                'difficulty': 'Medium'
            },
            
            'iam_root_usage': {
                'title': '🔒 Remove Root Account Access Keys',
                'steps': [
                    '1. Go to IAM Console → Users',
                    '2. Click "root account"',
                    '3. Go to "Security credentials" tab',
                    '4. Find "Access keys"',
                    '5. For each access key:',
                    '   - Click the delete (X) button',
                    '   - Confirm deletion',
                    '6. ✅ Root account access keys removed',
                    'Important: Use IAM users for operations'
                ],
                'time_to_fix': '5 minutes',
                'difficulty': 'Easy'
            },
            
            'cloudtrail_disabled': {
                'title': '🔒 Enable CloudTrail Logging',
                'steps': [
                    '1. Go to CloudTrail Console',
                    '2. Click "Trails" in left sidebar',
                    '3. Click "Create trail"',
                    '4. Trail name: "organization-trail"',
                    '5. Apply trail to all regions: YES',
                    '6. Create new S3 bucket OR select existing',
                    '7. Create new CloudWatch log group',
                    '8. Click "Create trail"',
                    '9. ✅ CloudTrail enabled for audit logging'
                ],
                'time_to_fix': '10 minutes',
                'difficulty': 'Medium'
            },
            
            'unencrypted_s3': {
                'title': '🔒 Enable S3 Encryption',
                'steps': [
                    '1. Go to S3 Console → Your Bucket',
                    '2. Click "Properties" tab',
                    '3. Scroll to "Default encryption"',
                    '4. Click "Edit"',
                    '5. Check "Enable"',
                    '6. Choose encryption type:',
                    '   - SSE-S3 (free, default)',
                    '   - SSE-KMS (more control)',
                    '7. Click "Save changes"',
                    '8. ✅ S3 bucket encryption enabled'
                ],
                'time_to_fix': '5 minutes',
                'difficulty': 'Easy'
            },
            
            'mfa_not_enabled': {
                'title': '🔒 Enable MFA for IAM Users',
                'steps': [
                    '1. Go to IAM Console → Users',
                    '2. Click the IAM user',
                    '3. Go to "Security credentials" tab',
                    '4. Find "Multi-factor authentication (MFA)"',
                    '5. Click "Assign MFA device"',
                    '6. Choose MFA device:',
                    '   - Virtual authenticator (Google Authenticator)',
                    '   - Hardware security key',
                    '7. Scan QR code with authenticator app',
                    '8. Enter 6-digit code twice',
                    '9. ✅ MFA enabled for user'
                ],
                'time_to_fix': '10 minutes',
                'difficulty': 'Medium'
            }
        }
        
        return recommendations.get(
            finding_type,
            {
                'title': 'Review AWS Security Best Practices',
                'steps': ['Consult AWS documentation'],
                'time_to_fix': 'Varies',
                'difficulty': 'Unknown'
            }
        )
    
    @staticmethod
    def enrich_finding(finding: dict) -> dict:
        """
        Complete enrichment:
        - Calculate risk score
        - Determine severity
        - Estimate breach cost
        - Get recommendation
        - Add metadata
        """
        
        # Calculate metrics
        risk_score = RiskEnrichment.calculate_risk_score(finding)
        severity = RiskEnrichment.determine_severity(risk_score)
        breach_cost = RiskEnrichment.estimate_breach_cost(finding, risk_score)
        recommendation = RiskEnrichment.get_recommendation(finding.get('finding_type'))
        
        # Build enriched finding
        enriched = {
            **finding,  # Keep original fields
            'risk_score': risk_score,
            'severity': severity,
            'estimated_cost': breach_cost,
            'recommendation': recommendation,
            'enriched_at': datetime.now().isoformat(),
            'business_impact': RiskEnrichment.IMPACT_MAPPING[severity]['business_impact'],
            'priority': RiskEnrichment.IMPACT_MAPPING[severity]['priority'],
            'sla_hours': RiskEnrichment.IMPACT_MAPPING[severity]['sla_hours']
        }
        
        logger.info(f"✅ Enriched finding: {finding['finding_id']}")
        logger.info(f"   Severity: {severity} | Risk: {risk_score} | Cost: ${breach_cost:,}")
        
        return enriched
    