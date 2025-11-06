#!/bin/bash
# EchoStack Docker Test Script
# Tests the complete Docker setup and functionality

set -e

echo "🧪 Testing EchoStack Docker Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Test 1: Check if Docker is running
echo "1. Checking Docker..."
if docker info >/dev/null 2>&1; then
    print_status "Docker is running"
else
    print_error "Docker is not running"
    exit 1
fi

# Test 2: Check if docker-compose exists
echo "2. Checking Docker Compose..."
if command -v docker-compose >/dev/null 2>&1; then
    print_status "Docker Compose is available"
else
    print_error "Docker Compose is not available"
    exit 1
fi

# Test 3: Build the services
echo "3. Building Docker services..."
if docker-compose build --quiet; then
    print_status "Services built successfully"
else
    print_error "Failed to build services"
    exit 1
fi

# Test 4: Start services
echo "4. Starting services..."
if docker-compose up -d; then
    print_status "Services started successfully"
else
    print_error "Failed to start services"
    docker-compose logs
    exit 1
fi

# Wait for services to be ready
echo "5. Waiting for services to be ready..."
sleep 30

# Test 5: Check service health
echo "6. Checking service health..."

# Check EchoStack
if curl -f http://localhost:8003/health >/dev/null 2>&1; then
    print_status "EchoStack service is healthy"
else
    print_warning "EchoStack service health check failed"
fi

# Check PostgreSQL
if docker-compose exec -T echostack_db pg_isready -U echostack >/dev/null 2>&1; then
    print_status "PostgreSQL is healthy"
else
    print_warning "PostgreSQL health check failed"
fi

# Check Redis
if docker-compose exec -T echostack_redis redis-cli ping | grep -q PONG; then
    print_status "Redis is healthy"
else
    print_warning "Redis health check failed"
fi

# Test 6: Test API endpoints
echo "7. Testing API endpoints..."

# Test root endpoint
if curl -f http://localhost:8003/ >/dev/null 2>&1; then
    print_status "API root endpoint accessible"
else
    print_warning "API root endpoint not accessible"
fi

# Test docs endpoint
if curl -f http://localhost:8003/docs >/dev/null 2>&1; then
    print_status "API documentation accessible"
else
    print_warning "API documentation not accessible"
fi

# Test 7: Test Python imports in container
echo "8. Testing Python module imports..."
if docker-compose exec -T echostack python -c "
import sys
sys.path.append('/app')
try:
    import echostack_module.tracelogger
    import echostack_module.dashboard
    import echostack_module.vault_sync
    import echostack_module.alert_manager
    print('All modules imported successfully')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
" >/dev/null 2>&1; then
    print_status "Python modules import successfully"
else
    print_error "Python module import failed"
fi

# Test 8: Test vault synchronization
echo "9. Testing vault synchronization..."
if docker-compose exec -T echostack python -c "
from echostack_module.vault_sync import VaultSynchronizer
sync = VaultSynchronizer()
result = sync.perform_sync()
print(f'Vault sync completed: {len(result.get(\"vaults_processed\", 0))} vaults processed')
" >/dev/null 2>&1; then
    print_status "Vault synchronization works"
else
    print_warning "Vault synchronization test failed"
fi

# Test 9: Check logs for errors
echo "10. Checking logs for errors..."
if docker-compose logs echostack 2>&1 | grep -i error | head -5 | grep -q .; then
    print_warning "Found errors in logs:"
    docker-compose logs echostack 2>&1 | grep -i error | head -3
else
    print_status "No errors found in logs"
fi

# Cleanup
echo "11. Cleaning up..."
docker-compose down -v >/dev/null 2>&1
print_status "Cleanup completed"

echo ""
echo -e "${GREEN}🎉 Docker setup test completed!${NC}"
echo ""
echo "If all tests passed, your EchoStack Docker setup is ready for deployment."
echo "Run 'make prod' to start the production environment."
echo "Run 'make prod-monitoring' to include monitoring stack."