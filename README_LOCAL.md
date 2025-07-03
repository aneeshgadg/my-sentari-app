# Sentari App - Local Development Guide

This guide will help you set up and run the Sentari app locally for development and testing.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Git** - [Download here](https://git-scm.com/downloads)
- **Docker Desktop** (optional, for containerized development) - [Download here](https://www.docker.com/products/docker-desktop/)
- **OpenSSL** (for SSL certificates) - [Download here](https://slproweb.com/products/Win32OpenSSL.html)

### Option 1: Local Python Development (Recommended for Development)

#### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd v4-Sentari-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Environment Configuration

```bash
# Copy environment template
copy env.example .env

# Edit .env with your development values
notepad .env
```

**Required Environment Variables for Local Development:**
```env
# Environment
ENVIRONMENT=development
FLASK_ENV=development

# Flask Configuration
FLASK_SECRET_KEY=dev-secret-key-change-in-production
FLASK_DEBUG=true

# Database Configuration
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_DATABASE_URL=your-supabase-database-url

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_WHISPER_MODEL=whisper-1

# Security Configuration (Development)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
MAX_CONTENT_LENGTH=16777216

# Rate Limiting (Development - more lenient)
RATE_LIMIT_DEFAULT="1000 per minute"
RATE_LIMIT_STORAGE_URL=memory://

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FORMAT=standard

# Performance Configuration
WORKER_PROCESSES=1
WORKER_THREADS=1

# Monitoring Configuration
ENABLE_METRICS=false
METRICS_PORT=9090
```

#### 3. Run the Application

```bash
# Start the Flask development server
python app.py
```

The application will be available at:
- **Main App**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **API Documentation**: http://localhost:5000/api/

### Option 2: Docker Development (Recommended for Testing Production-like Environment)

#### 1. Setup with Docker

```bash
# Clone the repository
git clone <repository-url>
cd v4-Sentari-app

# Copy environment template
copy env.example .env

# Edit .env with your development values
notepad .env
```

#### 2. Create Development Docker Compose

Create a `docker-compose.dev.yml` file:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
      - /app/venv
    environment:
      - ENVIRONMENT=development
      - FLASK_ENV=development
      - DATABASE_URL=${SUPABASE_DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - CORS_ORIGINS=http://localhost:3000,http://localhost:3001
      - RATE_LIMIT_STORAGE_URL=memory://
      - ENABLE_METRICS=false
      - LOG_LEVEL=DEBUG
    command: python app.py
    networks:
      - sentari-dev

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data
    command: redis-server --appendonly yes
    networks:
      - sentari-dev

volumes:
  redis_dev_data:

networks:
  sentari-dev:
    driver: bridge
```
---
#### Generate random secret key for flask
>>> import secrets
>>> secrets.token_urlsafe(16)
>>> secrets.token_hex(16)
---

#### 3. Run with Docker

```bash
# Build and start services
docker-compose -f docker-compose.dev.yml up --build

# Or run in background
docker-compose -f docker-compose.dev.yml up -d --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f web
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v
```

### Manual API Testing

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

#### 2. Test Authentication
```bash
# Test protected endpoint without auth
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I am feeling happy today"}'
```

#### 3. Test with Authentication
```bash
# Get JWT token from Supabase (you'll need to implement this)
# Then test with auth
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"text": "I am feeling happy today"}'
```

#### 4. Test Whisper (Audio Transcription)
```bash
curl -X POST http://localhost:5000/api/whisper \
  -F "audio=@path/to/your/audio/file.wav"
```

### Using Postman or Insomnia

1. **Import the API Collection** (create a `Sentari_API.postman_collection.json` file)
2. **Set up environment variables**:
   - `base_url`: http://localhost:5000
   - `jwt_token`: Your Supabase JWT token
3. **Test endpoints**:
   - `GET {{base_url}}/health`
   - `POST {{base_url}}/api/analyze`
   - `POST {{base_url}}/api/save-entry`
   - `POST {{base_url}}/api/whisper`

## 🔧 Development Tools

### Code Quality

```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Database Management

```bash
# Access Supabase dashboard
# Go to: https://supabase.com/dashboard
# Select your project
# Go to SQL Editor or Table Editor

# Test database connection
python -c "
from src.config import validate_environment
validate_environment()
print('Database configuration is valid!')
"
```

### Logging and Debugging

```bash
# View application logs
# If running locally: Check console output
# If running with Docker:
docker-compose -f docker-compose.dev.yml logs -f web

# Follow all development logs
docker-compose -f docker-compose.dev.yml logs -f

# Follow with timestamps
docker-compose -f docker-compose.dev.yml logs -f -t web

# Show recent logs and follow
docker-compose -f docker-compose.dev.yml logs -f --tail=100 web

# Enable debug mode
export FLASK_DEBUG=true
python app.py
```

### Logging Commands for Development
```bash
# Follow Flask app logs (most common)
docker-compose -f docker-compose.dev.yml logs -f web

# Follow all services
docker-compose -f docker-compose.dev.yml logs -f

# Follow with timestamps
docker-compose -f docker-compose.dev.yml logs -f -t

# Show last 50 lines and follow
docker-compose -f docker-compose.dev.yml logs -f --tail=50

# Follow multiple services
docker-compose -f docker-compose.dev.yml logs -f web redis
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Make sure you're in the correct directory
cd v4-Sentari-app

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

#### 2. Environment Variables Not Loading
```bash
# Check if .env file exists
ls -la .env

# Verify environment variables are loaded
python -c "import os; print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))"
```

#### 3. Port Already in Use
```bash
# Check what's using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # macOS/Linux

# Kill the process or use a different port
export FLASK_RUN_PORT=5001
python app.py
```

#### 4. Docker Issues
```bash
# Clean up Docker
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f

# Rebuild from scratch
docker-compose -f docker-compose.dev.yml up --build
```

#### 5. OpenAI API Issues
```bash
# Test OpenAI connection
python -c "
import openai
openai.api_key = 'your-api-key'
try:
    response = openai.ChatCompletion.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Hello'}]
    )
    print('OpenAI connection successful!')
except Exception as e:
    print(f'OpenAI error: {e}')
"
```

### Performance Issues

#### 1. Slow Response Times
- Check OpenAI API response times
- Monitor database connection pool
- Enable caching with Redis

#### 2. Memory Issues
- Monitor memory usage with `docker stats`
- Check for memory leaks in long-running processes
- Adjust worker processes in configuration

## 📚 API Reference (Local Development)

### Authentication
For local development, you can temporarily disable authentication by modifying the auth decorators.

### Endpoints

#### Health Check
```http
GET /health
```

#### Analyze Text
```http
POST /api/analyze
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "text": "I am feeling happy today"
}
```

#### Save Entry
```http
POST /api/save-entry
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "content": "Today was a great day...",
  "emotion": "happy",
  "tags": ["work", "success"]
}
```

#### Audio Transcription
```http
POST /api/whisper
Content-Type: multipart/form-data

audio: <audio-file>
```

## 🔄 Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# Test locally
python app.py

# Run tests
pytest

# Commit changes
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature
```

### 2. Testing Changes
```bash
# Test with different environments
export ENVIRONMENT=development
python app.py

# Test with Docker
docker-compose -f docker-compose.dev.yml up --build
```

### 3. Debugging
```bash
# Enable debug mode
export FLASK_DEBUG=true
export LOG_LEVEL=DEBUG

# if you edit with windows system run below befor copying
dos2unix .env

# Run with debugger
python -m pdb app.py

# Use logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Development Checklist

Before committing code:

- [ ] Code is formatted with Black
- [ ] Linting passes with Flake8
- [ ] Type checking passes with MyPy
- [ ] All tests pass
- [ ] Environment variables are properly configured
- [ ] Documentation is updated
- [ ] No sensitive data in commits
- [ ] API endpoints tested manually
- [ ] Error handling tested
- [ ] Performance impact considered

## 🆘 Getting Help

### Local Development Issues
1. Check the troubleshooting section above
2. Review application logs
3. Verify environment configuration
4. Test individual components

### API Issues
1. Check authentication tokens
2. Verify request format
3. Test with Postman/Insomnia
4. Review error responses

### Database Issues
1. Check Supabase connection
2. Verify table schemas
3. Test with Supabase dashboard
4. Review database logs

---

**Happy Coding! 🚀**

For production deployment, see the main [README.md](README.md) file. 

