#!/bin/bash
# Fast backend rebuild script using Docker BuildKit cache

set -e

echo "🚀 Fast Backend Rebuild Script"
echo "================================"
echo ""

# Enable BuildKit for faster builds with cache
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

cd "$(dirname "$0")"

echo "📦 Building backend with BuildKit cache..."
docker compose build backend

echo ""
echo "🔄 Restarting backend container..."
docker compose up -d backend

echo ""
echo "⏳ Waiting for backend to start..."
sleep 5

echo ""
echo "📋 Backend logs (last 20 lines):"
docker compose logs --tail=20 backend

echo ""
echo "✅ Done! Check logs above for any errors."
echo ""
echo "💡 Tips:"
echo "  - This script uses Docker BuildKit cache to speed up rebuilds"
echo "  - Only changed layers will be rebuilt"
echo "  - Pip packages are cached in /root/.cache/pip mount"
echo "  - Run 'docker compose logs -f backend' to follow logs"
