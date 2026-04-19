#!/bin/bash

# AWS Cost Monitoring Helper Script

echo "🚀 CloudGuard AI - Cost Monitoring"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Show menu
echo "Select an option:"
echo "1️⃣  Show current spending"
echo "2️⃣  Show service breakdown"
echo "3️⃣  Show billing dashboard"
echo "4️⃣  Create budget alert"
echo "5️⃣  Run Python cost monitor"
echo "6️⃣  Exit"
echo ""

read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo -e "${BLUE}📊 Current Month Spending...${NC}"
        aws ce get-cost-and-usage \
            --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
            --granularity MONTHLY \
            --metrics "UnblendedCost" \
            --group-by Type=DIMENSION,Key=SERVICE \
            --query 'ResultsByTime[0].Groups[*].[Keys[0],Metrics.UnblendedCost.Amount]' \
            --output table
        ;;
    
    2)
        echo -e "${BLUE}📈 Service Breakdown...${NC}"
        aws ce get-cost-and-usage \
            --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
            --granularity DAILY \
            --metrics "UnblendedCost" \
            --group-by Type=DIMENSION,Key=SERVICE \
            --query 'ResultsByTime[*].[TimePeriod.Start,Groups[*].[Keys[0],Metrics.UnblendedCost.Amount]]' \
            --output table
        ;;
    
    3)
        echo -e "${BLUE}💳 Opening AWS Billing Dashboard...${NC}"
        if command -v open &> /dev/null; then
            open "https://console.aws.amazon.com/billing/home"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "https://console.aws.amazon.com/billing/home"
        else
            echo "Visit: https://console.aws.amazon.com/billing/home"
        fi
        ;;
    
    4)
        echo -e "${BLUE}🚨 Creating Budget Alert...${NC}"
        read -p "Enter budget name (default: CloudGuard): " budget_name
        budget_name=${budget_name:-CloudGuard}
        
        read -p "Enter budget amount in USD (default: 100): " budget_amount
        budget_amount=${budget_amount:-100}
        
        python scripts/monitor_costs.py
        ;;
    
    5)
        echo -e "${BLUE}📊 Running Cost Monitor...${NC}"
        python scripts/monitor_costs.py
        ;;
    
    6)
        echo "Goodbye!"
        exit 0
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "Done! ✅"