"""
AWS Cost Monitoring Script
Track spending and send alerts if approaching limits
"""

import os
import json
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CostMonitor:
    """Monitor AWS spending"""
    
    def __init__(self, budget_limit=100):
        """
        Initialize cost monitor
        budget_limit: Maximum spend in USD (default 100 for free credits)
        """
        self.ce_client = boto3.client('ce', region_name='us-east-1')
        self.budgets_client = boto3.client('budgets', region_name='us-east-1')
        self.sns_client = boto3.client('sns', region_name='us-east-1')
        
        self.budget_limit = budget_limit
        self.account_id = self._get_account_id()
        
        logger.info(f"✅ Cost Monitor initialized (Budget: ${budget_limit})")
    
    def _get_account_id(self):
        """Get AWS account ID"""
        sts = boto3.client('sts', region_name='us-east-1')
        return sts.get_caller_identity()['Account']
    
    def get_current_spending(self):
        """Get current month spending"""
        try:
            today = datetime.now()
            start_date = today.replace(day=1)
            end_date = today
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            total_cost = 0
            service_costs = {}
            
            for result in response.get('ResultsByTime', []):
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    service_costs[service] = cost
                    total_cost += cost
            
            return {
                'total_cost': total_cost,
                'service_costs': service_costs,
                'period': start_date.strftime('%Y-%m-%d')
            }
        
        except Exception as e:
            logger.error(f"Error getting spending: {e}")
            return None
    
    def get_free_tier_usage(self):
        """Get free tier usage"""
        try:
            ce = boto3.client('ce', region_name='us-east-1')
            
            today = datetime.now()
            start_date = today.replace(day=1)
            
            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': today.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['AmortizedCost'],
                Filter={
                    'Dimensions': {
                        'Key': 'PURCHASE_TYPE',
                        'Values': ['Free Tier']
                    }
                }
            )
            
            total_free_cost = 0
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    cost = float(group['Metrics']['AmortizedCost']['Amount'])
                    total_free_cost += cost
            
            return total_free_cost
        
        except Exception as e:
            logger.debug(f"Could not get free tier usage: {e}")
            return None
    
    def get_forecast(self):
        """Get cost forecast for month"""
        try:
            today = datetime.now()
            start_date = (today.replace(day=1) - timedelta(days=30))
            
            response = self.ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': today.strftime('%Y-%m-%d')
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY',
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon Elastic Compute Cloud - Compute']
                    }
                }
            )
            
            forecast = None
            for item in response.get('ForecastResultsByTime', []):
                forecast = item['MeanValue']
            
            return forecast
        
        except Exception as e:
            logger.debug(f"Could not get forecast: {e}")
            return None
    
    def get_service_breakdown(self):
        """Get cost breakdown by service"""
        spending = self.get_current_spending()
        
        if not spending:
            return None
        
        return spending['service_costs']
    
    def check_budget_alert(self):
        """Check if spending is approaching budget limit"""
        spending = self.get_current_spending()
        
        if not spending:
            return None
        
        total = float(spending['total_cost'])
        percent = (total / self.budget_limit) * 100
        
        alert = {
            'total_cost': total,
            'budget_limit': self.budget_limit,
            'percent_used': percent,
            'remaining': self.budget_limit - total,
            'alert_triggered': percent > 80
        }
        
        return alert
    
    def generate_report(self):
        """Generate comprehensive cost report"""
        logger.info("\n" + "="*70)
        logger.info("💰 AWS COST MONITORING REPORT")
        logger.info("="*70 + "\n")
        
        # Current spending
        spending = self.get_current_spending()
        if spending:
            logger.info(f"📊 Current Month Spending (as of {spending['period']}):")
            logger.info(f"   Total: ${spending['total_cost']:.2f}")
            logger.info(f"   Budget: ${self.budget_limit:.2f}")
            logger.info(f"   Percent Used: {(spending['total_cost']/self.budget_limit)*100:.1f}%")
            logger.info(f"   Remaining: ${self.budget_limit - spending['total_cost']:.2f}\n")
            
            # Service breakdown
            logger.info("📈 Spending by Service:")
            for service, cost in sorted(spending['service_costs'].items(), key=lambda x: x[1], reverse=True):
                if float(cost) > 0:
                    logger.info(f"   {service}: ${cost:.2f}")
            logger.info()
        
        # Free tier usage
        free_usage = self.get_free_tier_usage()
        if free_usage is not None:
            logger.info(f"🎁 Free Tier Usage:")
            logger.info(f"   Used: ${free_usage:.2f} of free tier")
            logger.info()
        
        # Budget alert
        alert = self.check_budget_alert()
        if alert:
            logger.info(f"🚨 Budget Status:")
            logger.info(f"   Used: ${alert['total_cost']:.2f} / ${alert['budget_limit']:.2f}")
            logger.info(f"   Remaining: ${alert['remaining']:.2f}")
            
            if alert['alert_triggered']:
                logger.warning(f"   ⚠️  WARNING: Spending at {alert['percent_used']:.1f}% of budget!")
            else:
                logger.info(f"   ✅ OK: {alert['percent_used']:.1f}% of budget used")
            logger.info()
        
        logger.info("="*70 + "\n")
    
    def create_budget(self, budget_name='CloudGuard', amount=100):
        """Create AWS Budget for monitoring"""
        try:
            self.budgets_client.create_budget(
                AccountId=self.account_id,
                Budget={
                    'BudgetName': budget_name,
                    'BudgetLimit': {
                        'Amount': str(amount),
                        'Unit': 'USD'
                    },
                    'TimeUnit': 'MONTHLY',
                    'BudgetType': 'COST'
                }
            )
            
            logger.info(f"✅ Budget created: {budget_name} (${amount})")
        
        except Exception as e:
            logger.warning(f"Could not create budget: {e}")

def main():
    """Main function"""
    
    # Create monitor
    monitor = CostMonitor(budget_limit=100)  # 100 USD
    
    # Generate report
    monitor.generate_report()
    
    # Create budget
    try:
        monitor.create_budget('CloudGuard Demo', 100)
    except:
        pass

if __name__ == '__main__':
    main()