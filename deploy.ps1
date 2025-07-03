# Production Deployment Script for Sentari App (Windows PowerShell)
param(
    [switch]$SkipValidation
)

Write-Host "🚀 Starting Sentari production deployment..." -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Error ".env file not found. Please copy env.example to .env and configure it."
    exit 1
}

# Load environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Validate required environment variables
$requiredVars = @("SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY", "FLASK_SECRET_KEY")
foreach ($var in $requiredVars) {
    if (-not (Get-Variable -Name "env:$var" -ErrorAction SilentlyContinue).Value) {
        Write-Error "Required environment variable $var is not set."
        exit 1
    }
}

Write-Status "Environment variables validated."

# Create necessary directories
Write-Status "Creating necessary directories..."
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "ssl" | Out-Null
New-Item -ItemType Directory -Force -Path "data" | Out-Null

# Generate SSL certificates for development (replace with real certificates in production)
if (-not (Test-Path "ssl/cert.pem") -or -not (Test-Path "ssl/key.pem")) {
    Write-Warning "SSL certificates not found. Generating self-signed certificates for development..."
    
    # Check if OpenSSL is available
    try {
        $opensslVersion = openssl version 2>$null
        if ($LASTEXITCODE -eq 0) {
            openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        } else {
            Write-Warning "OpenSSL not found. Please install OpenSSL or manually create SSL certificates."
        }
    } catch {
        Write-Warning "OpenSSL not available. Please install OpenSSL or manually create SSL certificates."
    }
}

# Build and start services
Write-Status "Building and starting services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
Write-Status "Waiting for services to be ready..."
Start-Sleep -Seconds 30

# Check if services are healthy
Write-Status "Checking service health..."
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 10
    if ($healthResponse.StatusCode -eq 200) {
        Write-Status "✅ Application is healthy!"
    } else {
        Write-Error "❌ Application health check failed!"
        docker-compose logs web
        exit 1
    }
} catch {
    Write-Error "❌ Application health check failed!"
    docker-compose logs web
    exit 1
}

# Check if Redis is running
try {
    $redisResponse = docker-compose exec -T redis redis-cli ping 2>$null
    if ($redisResponse -eq "PONG") {
        Write-Status "✅ Redis is running!"
    } else {
        Write-Error "❌ Redis is not responding!"
        exit 1
    }
} catch {
    Write-Error "❌ Redis is not responding!"
    exit 1
}

# Check if Prometheus is accessible
try {
    $prometheusResponse = Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -UseBasicParsing -TimeoutSec 5
    if ($prometheusResponse.StatusCode -eq 200) {
        Write-Status "✅ Prometheus is running!"
    } else {
        Write-Warning "⚠️  Prometheus is not accessible (this might be normal if not configured)"
    }
} catch {
    Write-Warning "⚠️  Prometheus is not accessible (this might be normal if not configured)"
}

# Check if Grafana is accessible
try {
    $grafanaResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5
    if ($grafanaResponse.StatusCode -eq 200) {
        Write-Status "✅ Grafana is running!"
        Write-Status "Grafana is available at http://localhost:3000 (admin/admin)"
    } else {
        Write-Warning "⚠️  Grafana is not accessible (this might be normal if not configured)"
    }
} catch {
    Write-Warning "⚠️  Grafana is not accessible (this might be normal if not configured)"
}

Write-Status "🎉 Deployment completed successfully!"

Write-Host ""
Write-Host "📋 Service URLs:" -ForegroundColor Cyan
Write-Host "  - Application: http://localhost:5000"
Write-Host "  - Health Check: http://localhost:5000/health"
Write-Host "  - Metrics: http://localhost:5000/metrics"
Write-Host "  - Prometheus: http://localhost:9090"
Write-Host "  - Grafana: http://localhost:3000"
Write-Host ""
Write-Host "📝 Useful commands:" -ForegroundColor Cyan
Write-Host "  - View logs: docker-compose logs -f"
Write-Host "  - Stop services: docker-compose down"
Write-Host "  - Restart services: docker-compose restart"
Write-Host "  - Update and redeploy: .\deploy.ps1"
Write-Host ""
Write-Status "Deployment script completed!" 