#!/bin/bash

echo "🧹 Cleaning up ports..."

# Kill processes on common Expo ports
lsof -ti:8081,19000,19001,19002,8000,8001,8002,8003,8004,8005 | xargs kill -9 2>/dev/null

echo "✅ Ports cleaned"
echo "🚀 Starting Expo with clean cache..."

npx expo start --clear
