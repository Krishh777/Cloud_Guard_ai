#!/bin/bash

# Cleanup CloudGuard AWS Resources

echo "🧹 CloudGuard AWS Cleanup"
echo "=========================="
echo ""

AWS_REGION="us-east-1"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

read -p "⚠️  This will delete AWS resources. Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo -e "${RED}Deleting AWS Resources...${NC}"
echo ""

# Delete DynamoDB table
echo "Deleting DynamoDB table: cloudguard-cache"
aws dynamodb delete-table \
    --table-name cloudguard-cache \
    --region $AWS_REGION 2>/dev/null && echo "✅ DynamoDB table deleted" || echo "⚠️  Could not delete table"

# Delete SNS topic
echo "Deleting SNS topic: cloudguard-alerts"
SNS_ARN=$(aws sns list-topics --query 'Topics[?contains(TopicArn, `cloudguard-alerts`)].TopicArn' --output text --region $AWS_REGION)
if [ -n "$SNS_ARN" ]; then
    aws sns delete-topic --topic-arn $SNS_ARN --region $AWS_REGION && echo "✅ SNS topic deleted" || echo "⚠️  Could not delete topic"
fi

# Note about RDS
echo -e "${YELLOW}⚠️  Note: RDS database not deleted (data safety)${NC}"
echo "   To delete manually:"
echo "   aws rds delete-db-instance --db-instance-identifier cloudguard-db --skip-final-snapshot"

# Note about S3
echo -e "${YELLOW}⚠️  Note: S3 bucket not deleted (data safety)${NC}"
echo "   To delete manually:"
echo "   aws s3 rb s3://cloudguard-scan-logs-* --force"

echo ""
echo "=============================="
echo "✅ Cleanup complete!"
echo ""