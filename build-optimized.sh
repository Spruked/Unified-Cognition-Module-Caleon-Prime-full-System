# Docker Build Optimization Script
# Run this to rebuild with optimizations

echo "🧹 Cleaning up Docker system..."
docker system prune -f

echo "🏗️  Building optimized containers..."
docker compose build --no-cache --parallel

echo "🚀 Starting services..."
docker compose up -d

echo "📊 Checking service health..."
docker compose ps

echo "📝 Showing logs (Ctrl+C to stop)..."
docker compose logs -f