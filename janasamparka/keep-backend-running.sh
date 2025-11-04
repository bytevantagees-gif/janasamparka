#!/bin/bash

echo "🚀 Starting Janasamparka Backend..."

# Start Docker Desktop if not running
if ! docker info > /dev/null 2>&1; then
    echo "📦 Starting Docker Desktop..."
    open -a Docker
    echo "⏳ Waiting for Docker to start..."
    while ! docker info > /dev/null 2>&1; do
        sleep 2
    done
    echo "✅ Docker is running"
fi

# Navigate to project directory
cd "$(dirname "$0")"

# Start backend services
echo "🔧 Starting backend services..."
docker-compose up -d db backend

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if backend is responding
echo "🔍 Checking backend health..."
if curl -s http://192.168.29.35:8000/ > /dev/null; then
    echo "✅ Backend is running at http://192.168.29.35:8000"
    echo "✅ API available at http://192.168.29.35:8000/api"
    echo ""
    echo "📱 You can now use the mobile app!"
    echo ""
    echo "To view backend logs:"
    echo "  docker logs janasamparka_backend -f"
    echo ""
    echo "To stop backend:"
    echo "  docker-compose down"
else
    echo "❌ Backend is not responding"
    echo "Checking logs..."
    docker logs janasamparka_backend --tail 20
fi
