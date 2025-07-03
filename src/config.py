import os
from dotenv import load_dotenv
from typing import Optional
import logging

# Load environment variables from .env file
load_dotenv()

# Environment detection
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_DEVELOPMENT = ENVIRONMENT == 'development'

# OpenAI Model Configuration
OPENAI_CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini')
OPENAI_EMBED_MODEL = os.getenv('OPENAI_EMBED_MODEL', 'text-embedding-3-small')
OPENAI_WHISPER_MODEL = os.getenv('OPENAI_WHISPER_MODEL', 'whisper-1')

# API Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Backend-Core Microservice Configuration
BACKEND_CORE_URL = os.getenv('BACKEND_CORE_URL', 'http://localhost:5001')

# Flask Configuration
FLASK_ENV = ENVIRONMENT
FLASK_DEBUG = not IS_PRODUCTION
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Security Configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Rate Limiting
RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per minute')
RATE_LIMIT_STORAGE_URL = os.getenv('RATE_LIMIT_STORAGE_URL', 'memory://')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO' if IS_PRODUCTION else 'DEBUG')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_POOL_SIZE = int(os.getenv('DATABASE_POOL_SIZE', '10'))
DATABASE_MAX_OVERFLOW = int(os.getenv('DATABASE_MAX_OVERFLOW', '20'))

# Performance Configuration
WORKER_PROCESSES = int(os.getenv('WORKER_PROCESSES', '4'))
WORKER_THREADS = int(os.getenv('WORKER_THREADS', '2'))

# Monitoring Configuration
ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
METRICS_PORT = int(os.getenv('METRICS_PORT', '9090'))

def validate_environment() -> None:
    """Validate that all required environment variables are set."""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY', 
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Optional variables with warnings
    optional_vars = [
        'SUPABASE_DATABASE_URL',
        'FLASK_SECRET_KEY'
    ]
    
    for var in optional_vars:
        if not os.getenv(var):
            print(f"Warning: Optional environment variable {var} is not set.")

def get_cors_config() -> dict:
    """Get CORS configuration based on environment."""
    if IS_PRODUCTION:
        return {
            'origins': CORS_ORIGINS,
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization'],
            'supports_credentials': True
        }
    else:
        return {
            'origins': '*',
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization']
        }

def get_logging_config() -> dict:
    """Get logging configuration based on environment."""
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': LOG_FORMAT,
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': LOG_LEVEL,
                'formatter': 'json' if IS_PRODUCTION else 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': LOG_LEVEL,
                'formatter': 'json' if IS_PRODUCTION else 'standard',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': LOG_LEVEL,
                'propagate': False
            }
        }
    } 