#!/bin/bash
# ISS Module Deployment Script for Prometheus Prime Integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="iss-controller"
IMAGE_NAME="iss-module"
VERSION="1.0.0"
NETWORK_NAME="prometheus-prime"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking deployment requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f .env ]]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warning "Please edit .env file with your specific configuration"
    fi
    
    # Create necessary directories
    mkdir -p data/logs data/vault exports monitoring
    
    log_success "Environment setup complete"
}

build_image() {
    log_info "Building Docker image..."
    
    docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .
    
    if [[ $? -eq 0 ]]; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

create_network() {
    log_info "Creating Docker network if it doesn't exist..."
    
    if ! docker network ls | grep -q ${NETWORK_NAME}; then
        docker network create ${NETWORK_NAME}
        log_success "Created network: ${NETWORK_NAME}"
    else
        log_info "Network ${NETWORK_NAME} already exists"
    fi
}

deploy_services() {
    log_info "Deploying services with Docker Compose..."
    
    # Pull external images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    if [[ $? -eq 0 ]]; then
        log_success "Services deployed successfully"
    else
        log_error "Failed to deploy services"
        exit 1
    fi
}

wait_for_health() {
    log_info "Waiting for services to become healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose ps | grep -q "healthy"; then
            log_success "Services are healthy"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: Waiting for services..."
        sleep 10
        ((attempt++))
    done
    
    log_warning "Services may not be fully healthy yet"
    return 1
}

show_status() {
    log_info "Service status:"
    docker-compose ps
    
    echo ""
    log_info "Service URLs:"
    echo "  ISS Controller: http://localhost:8003"
    echo "  Health Check:   http://localhost:8003/health"
    echo "  API Docs:       http://localhost:8003/docs"
    echo "  API Gateway:    http://localhost:8000"
    echo "  Consul UI:      http://localhost:8500"
    echo "  Prometheus:     http://localhost:9090"
    echo "  Redis:          localhost:6379"
}

stop_services() {
    log_info "Stopping services..."
    docker-compose down
    log_success "Services stopped"
}

cleanup() {
    log_info "Cleaning up..."
    docker-compose down -v --remove-orphans
    docker rmi ${IMAGE_NAME}:latest ${IMAGE_NAME}:${VERSION} 2>/dev/null || true
    log_success "Cleanup complete"
}

# Main deployment functions
deploy() {
    log_info "Starting ISS Module deployment for Prometheus Prime..."
    
    check_requirements
    setup_environment
    build_image
    create_network
    deploy_services
    wait_for_health
    show_status
    
    log_success "ISS Module deployed successfully!"
    log_info "You can now integrate with Prometheus Prime API Gateway"
}

# Command line interface
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "stop")
        stop_services
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "build")
        check_requirements
        build_image
        ;;
    "logs")
        docker-compose logs -f ${2:-}
        ;;
    "shell")
        docker-compose exec iss-controller /bin/bash
        ;;
    "test")
        log_info "Running integration tests..."
        # Add test commands here
        curl -f http://localhost:8003/health || log_error "Health check failed"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|status|cleanup|build|logs|shell|test}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy all services"
        echo "  stop    - Stop all services"
        echo "  status  - Show service status"
        echo "  cleanup - Stop services and remove containers/images"
        echo "  build   - Build Docker image only"
        echo "  logs    - Show service logs (optionally specify service)"
        echo "  shell   - Open shell in ISS Controller container"
        echo "  test    - Run basic integration tests"
        exit 1
        ;;
esac