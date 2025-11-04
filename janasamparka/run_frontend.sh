#!/bin/bash

# Quick start script for admin dashboard
cd "$(dirname "$0")/admin-dashboard"

echo "🎨 Starting Janasamparka Admin Dashboard"
echo "========================================"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm packages..."
    npm install
fi

echo ""
echo "🚀 Starting Vite development server..."
echo "   Dashboard: http://localhost:3000"
echo ""
npm run dev
