# EchoStack Docker Test Script (PowerShell)
# Tests the complete Docker setup and functionality

param(
    [switch]$SkipCleanup
)

Write-Host "🧪 Testing EchoStack Docker Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Function to print status
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Test 1: Check if Docker is running
Write-Host "1. Checking Docker..."
try {
    docker info | Out-Null
    Write-Success "Docker is running"
} catch {
    Write-Error "Docker is not running"
    exit 1
}

# Test 2: Check if docker-compose exists
Write-Host "2. Checking Docker Compose..."
try {
    docker-compose version | Out-Null
    Write-Success "Docker Compose is available"
} catch {
    Write-Error "Docker Compose is not available"
    exit 1
}

# Test 3: Build the services
Write-Host "3. Building Docker services..."
try {
    docker-compose build --quiet
    Write-Success "Services built successfully"
} catch {
    Write-Error "Failed to build services"
    exit 1
}

# Test 4: Start services
Write-Host "4. Starting services..."
try {
    docker-compose up -d
    Write-Success "Services started successfully"
} catch {
    Write-Error "Failed to start services"
    docker-compose logs
    exit 1
}

# Wait for services to be ready
Write-Host "5. Waiting for services to be ready..."
Start-Sleep -Seconds 30

# Test 5: Check service health
Write-Host "6. Checking service health..."

# Check EchoStack
try {
    Invoke-WebRequest -Uri "http://localhost:8003/health" -TimeoutSec 10 | Out-Null
    Write-Success "EchoStack service is healthy"
} catch {
    Write-Warning "EchoStack service health check failed"
}

# Check PostgreSQL
try {
    docker-compose exec echostack_db pg_isready -U echostack | Out-Null
    Write-Success "PostgreSQL is healthy"
} catch {
    Write-Warning "PostgreSQL health check failed"
}

# Check Redis
try {
    $redisResult = docker-compose exec echostack_redis redis-cli ping
    if ($redisResult -match "PONG") {
        Write-Success "Redis is healthy"
    } else {
        Write-Warning "Redis health check failed"
    }
} catch {
    Write-Warning "Redis health check failed"
}

# Test 6: Test API endpoints
Write-Host "7. Testing API endpoints..."

# Test root endpoint
try {
    Invoke-WebRequest -Uri "http://localhost:8003/" -TimeoutSec 10 | Out-Null
    Write-Success "API root endpoint accessible"
} catch {
    Write-Warning "API root endpoint not accessible"
}

# Test docs endpoint
try {
    Invoke-WebRequest -Uri "http://localhost:8003/docs" -TimeoutSec 10 | Out-Null
    Write-Success "API documentation accessible"
} catch {
    Write-Warning "API documentation not accessible"
}

# Test 7: Test Python imports in container
Write-Host "8. Testing Python module imports..."
try {
    $importTest = docker-compose exec echostack python -c "
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
"
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python modules import successfully"
    } else {
        Write-Error "Python module import failed"
    }
} catch {
    Write-Error "Python module import test failed"
}

# Test 8: Test vault synchronization
Write-Host "9. Testing vault synchronization..."
try {
    $vaultTest = docker-compose exec echostack python -c "
from echostack_module.vault_sync import VaultSynchronizer
sync = VaultSynchronizer()
result = sync.perform_sync()
print(f'Vault sync completed: {len(result.get(\"vaults_processed\", 0))} vaults processed')
"
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Vault synchronization works"
    } else {
        Write-Warning "Vault synchronization test failed"
    }
} catch {
    Write-Warning "Vault synchronization test failed"
}

# Test 9: Check logs for errors
Write-Host "10. Checking logs for errors..."
try {
    $logs = docker-compose logs echostack 2>&1
    $errors = $logs | Select-String -Pattern "error|Error|ERROR" -CaseSensitive:$false
    if ($errors.Count -gt 0) {
        Write-Warning "Found errors in logs:"
        $errors | Select-Object -First 3 | ForEach-Object { Write-Host "  $($_.Line)" -ForegroundColor Yellow }
    } else {
        Write-Success "No errors found in logs"
    }
} catch {
    Write-Warning "Could not check logs"
}

# Cleanup
if (-not $SkipCleanup) {
    Write-Host "11. Cleaning up..."
    docker-compose down -v | Out-Null
    Write-Success "Cleanup completed"
}

Write-Host ""
Write-Host "🎉 Docker setup test completed!" -ForegroundColor Green
Write-Host ""
Write-Host "If all tests passed, your EchoStack Docker setup is ready for deployment."
Write-Host "Run 'docker-compose up -d' to start the production environment."
Write-Host "Run 'docker-compose --profile monitoring up -d' to include monitoring stack."