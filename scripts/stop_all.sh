#!/bin/bash

# Stop all CloudGuard AI services

echo "🛑 Stopping CloudGuard AI..."
echo "=============================="
echo ""

# Kill processes
pkill -f "python cloud_layer"
pkill -f "python fog_layer"
pkill -f "streamlit"

echo "✅ All services stopped!"
echo ""