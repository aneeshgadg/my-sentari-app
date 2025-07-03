#!/bin/bash

# Production Deployment Script for Sentari App
set -e

echo "🚀 Starting Sentari production deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Load environment variables safely
set -a
source .env
set +a

# Validate required environment variables
required_vars=("SUPABASE_URL" "SUPABASE_KEY" "OPENAI_API_KEY" "FLASK_SECRET_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set."
        exit 1
    fi
done

print_status "Environment variables validated."

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p ssl
mkdir -p data

# Generate SSL certificates for development (replace with real certificates in production)
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    print_warning "SSL certificates not found. Generating self-signed certificates for development..."
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Build and start services
print_status "Building and starting services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are healthy
print_status "Checking service health..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    print_status "✅ Application is healthy!"
else
    print_error "❌ Application health check failed!"
    docker-compose logs web
    exit 1
fi

# Check if Redis is running
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    print_status "✅ Redis is running!"
else
    print_error "❌ Redis is not responding!"
    exit 1
fi

# Check if Prometheus is accessible
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    print_status "✅ Prometheus is running!"
else
    print_warning "⚠️  Prometheus is not accessible (this might be normal if not configured)"
fi

# Check if Grafana is accessible
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    print_status "✅ Grafana is running!"
    print_status "Grafana is available at http://localhost:3000 (admin/admin)"
else
    print_warning "⚠️  Grafana is not accessible (this might be normal if not configured)"
fi

print_status "🎉 Deployment completed successfully!"

echo ""
echo "📋 Service URLs:"
echo "  - Application: http://localhost:5000"
echo "  - Health Check: http://localhost:5000/health"
echo "  - Metrics: http://localhost:5000/metrics"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Update and redeploy: ./deploy.sh"
echo ""
print_status "Deployment script completed!" 