# Sentari App - Production Ready

A production-ready Flask application for sentiment analysis and emotional intelligence using OpenAI and Supabase.

## 🚀 Quick Start (Development)

For detailed local development instructions, see [README_LOCAL.md](README_LOCAL.md).

```bash
# Clone the repository
git clone <repository-url>
cd v4-Sentari-app

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Run the application
python app.py
```

## 🏭 Production Deployment

### Prerequisites

- Docker and Docker Compose
- SSL certificates (for HTTPS)
- Domain name (optional but recommended)
- Supabase project
- OpenAI API key

### 1. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env with your production values
nano .env
```

**Required Environment Variables:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `OPENAI_API_KEY` - Your OpenAI API key
- `FLASK_SECRET_KEY` - A strong secret key for Flask sessions
- `CORS_ORIGINS` - Comma-separated list of allowed origins

### 2. SSL Certificates

For production, you need valid SSL certificates:

```bash
# Create SSL directory
mkdir -p ssl

# Option 1: Use Let's Encrypt (recommended)
certbot certonly --standalone -d yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem

# Option 2: Self-signed (development only)
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes
```

### 3. Deploy with Docker Compose

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

Or manually:

```bash
# Build and start services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check service status
docker-compose ps
docker-compose logs -f
```

### 4. Verify Deployment

```bash
# Check application health
curl http://localhost:5000/health

# Check metrics endpoint
curl http://localhost:5000/metrics

# Access monitoring dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

## 📊 Monitoring & Observability

### Health Checks
- Application: `GET /health`
- Docker health checks configured
- Nginx health monitoring

### Metrics
- Prometheus metrics at `/metrics`
- Application performance metrics
- Custom business metrics

### Logging
- Structured JSON logging in production
- Log rotation (10MB files, 5 backups)
- Console and file output

### Logging Commands Quick Reference
```bash
# Most common - follow web app logs
docker-compose logs -f web

# Follow all services with timestamps
docker-compose logs -f -t

# Show recent logs and follow
docker-compose logs -f --tail=100 web

# Follow specific services
docker-compose logs -f web nginx redis

# Follow monitoring services
docker-compose logs -f prometheus grafana
```

### Log Output Examples
**Web Service Logs:**
```
web-1  | [2024-01-15 10:30:15] INFO - Starting Sentari application
web-1  | [2024-01-15 10:30:16] INFO - Connected to Supabase
web-1  | [2024-01-15 10:30:17] INFO - OpenAI API configured
```

**Nginx Access Logs:**
```
nginx-1 | 192.168.1.100 - - [15/Jan/2024:10:30:15 +0000] "GET /health HTTP/1.1" 200 45
nginx-1 | 192.168.1.100 - - [15/Jan/2024:10:30:16 +0000] "POST /api/analyze HTTP/1.1" 200 156
```

### Dashboards
- **Grafana**: http://localhost:3000
  - Default credentials: admin/admin
  - Pre-configured dashboards for application metrics

## 🔒 Security Features

### Production Security
- HTTPS enforcement
- Security headers (HSTS, CSP, XSS protection)
- Rate limiting (100 requests/minute per IP)
- CORS configuration
- Non-root Docker containers
- Input validation and sanitization

### Authentication
- Supabase Auth integration
- JWT token validation
- Protected API endpoints

### Data Protection
- Environment variable validation
- Secure configuration management
- Database connection pooling
- Request size limits (16MB)

## 🚀 Performance Optimizations

### Application Level
- Gunicorn WSGI server
- Worker process management
- Connection pooling
- Response compression
- Caching with Redis

### Infrastructure Level
- Nginx reverse proxy
- Load balancing
- SSL termination
- Static file serving
- Gzip compression

## 📈 Scaling Considerations

### Horizontal Scaling
```bash
# Scale web service
docker-compose up -d --scale web=3

# Use external load balancer
# Configure multiple instances
```

### Database Scaling
- Supabase handles database scaling
- Connection pooling configured
- Read replicas available

### Caching Strategy
- Redis for session storage
- Rate limiting storage
- Application-level caching

## 🔧 Maintenance

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
./deploy.sh
```

### Backup
```bash
# Backup application data
docker-compose exec postgres pg_dump -U postgres > backup.sql

# Backup configuration
tar -czf config-backup.tar.gz .env ssl/ nginx.conf
```

### Monitoring & Logs
```bash
# View application logs
docker-compose logs -f web

# Follow all service logs in real-time
docker-compose logs -f

# Follow specific services with timestamps
docker-compose logs -f -t web nginx

# Show recent logs and follow
docker-compose logs -f --tail=100 web

# Monitor resource usage
docker stats

# Check service health
docker-compose ps
```

### Logging Commands Reference
```bash
# Follow web application logs (most common)
docker-compose logs -f web

# Follow Nginx access logs
docker-compose logs -f nginx

# Follow all services with timestamps
docker-compose logs -f -t

# Show last 50 lines and follow
docker-compose logs -f --tail=50

# Follow multiple services
docker-compose logs -f web redis

# Follow monitoring services
docker-compose logs -f prometheus grafana
```

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check environment variables
docker-compose logs web

# Validate configuration
python -c "from src.config import validate_environment; validate_environment()"
```

**Health check failing:**
```bash
# Check application status
curl -v http://localhost:5000/health

# View detailed logs
docker-compose logs web
```

**Rate limiting issues:**
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Monitor rate limiting
curl -H "X-Forwarded-For: 1.2.3.4" http://localhost/api/test
```

**Logging issues:**
```bash
# Check if logs are being generated
docker-compose logs --tail=10 web

# Check log file permissions
docker-compose exec web ls -la logs/

# View real-time logs for debugging
docker-compose logs -f web

# Check Nginx access logs
docker-compose logs -f nginx
```

### Performance Issues

**High memory usage:**
- Adjust worker processes in docker-compose.yml
- Monitor with `docker stats`
- Check for memory leaks

**Slow response times:**
- Check database connection pool
- Monitor OpenAI API response times
- Review Nginx configuration

## 📚 API Documentation

### Authentication
All API endpoints require authentication via Supabase JWT tokens in the Authorization header:
```
Authorization: Bearer <jwt-token>
```

### Endpoints
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `POST /api/analyze` - Analyze text sentiment
- `POST /api/save-entry` - Save journal entry
- `POST /api/whisper` - Audio transcription

### Rate Limits
- Default: 100 requests per minute per IP
- Burst: 20 requests
- Custom limits per endpoint

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs and metrics

---

**Production Checklist:**
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations run
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] Logging configured
- [ ] Performance optimized "# vv1-Sentari-app" 
