#!/bin/bash

# Start all CloudGuard AI services

echo "🚀 Starting CloudGuard AI..."
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p logs

echo -e "${BLUE}Starting services...${NC}"
echo ""

# Terminal 1: PostgreSQL (if running locally)
echo -e "${GREEN}1. PostgreSQL${NC}"
if command -v psql &> /dev/null; then
    echo "   ✅ PostgreSQL available"
else
    echo "   ⚠️  PostgreSQL not found. Make sure RDS is accessible."
fi

# Terminal 2: Cloud Layer
echo -e "${GREEN}2. Cloud Layer (Port 8000)${NC}"
python cloud_layer/main_with_custom_model.py > logs/cloud_layer.log 2>&1 &
CLOUD_PID=$!
echo "   PID: $CLOUD_PID"

sleep 5

# Terminal 3: Fog Layer
echo -e "${GREEN}3. Fog Layer (Port 8001)${NC}"
python fog_layer/main.py > logs/fog_layer.log 2>&1 &
FOG_PID=$!
echo "   PID: $FOG_PID"

sleep 5

# Terminal 4: Dashboard
echo -e "${GREEN}4. Dashboard (Port 8501)${NC}"
streamlit run dashboard/app.py > logs/dashboard.log 2>&1 &
DASH_PID=$!
echo "   PID: $DASH_PID"

echo ""
echo "=============================="
echo "✅ All services started!"
echo "=============================="
echo ""
echo "📊 Access URLs:"
echo "   - Dashboard: http://localhost:8501"
echo "   - Cloud API: http://localhost:8000/docs"
echo "   - Fog API: http://localhost:8001/docs"
echo ""
echo "📋 Process IDs:"
echo "   - Cloud Layer: $CLOUD_PID"
echo "   - Fog Layer: $FOG_PID"
echo "   - Dashboard: $DASH_PID"
echo ""
echo "🛑 To stop all services:"
echo "   ./scripts/stop_all.sh"
echo ""