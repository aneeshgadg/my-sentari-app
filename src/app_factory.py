import os
import logging
import logging.config
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flask_talisman import Talisman
from prometheus_client import make_wsgi_app
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from supabase import create_client, Client
import openai
import structlog

from .config import (
    validate_environment, get_cors_config, get_logging_config,
    IS_PRODUCTION, FLASK_SECRET_KEY, MAX_CONTENT_LENGTH,
    RATE_LIMIT_DEFAULT, RATE_LIMIT_STORAGE_URL, ENABLE_METRICS
)

def create_app(test_config=None):
    """Application factory pattern for creating Flask app instances."""
    
    # Validate environment variables
    validate_environment()
    
    # Create Flask app
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure app
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=FLASK_SECRET_KEY,
            MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH,
        )
    else:
        app.config.update(test_config)
    
    # Ensure logs directory exists
    try:
        os.makedirs('logs')
    except OSError:
        pass
    
    # Configure logging
    logging.config.dictConfig(get_logging_config())
    
    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if IS_PRODUCTION else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase: Client = create_client(supabase_url, supabase_key)
    app.config['SUPABASE_CLIENT'] = supabase
    
    # Initialize OpenAI client
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # Configure CORS
    cors_config = get_cors_config()
    CORS(app, **cors_config)
    
    # Configure security headers
    if IS_PRODUCTION:
        Talisman(
            app,
            content_security_policy={
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline'",
                'style-src': "'self' 'unsafe-inline'",
                'img-src': "'self' data: https:",
                'connect-src': "'self' https:",
            },
            force_https=True
        )
    
    # Configure compression
    Compress(app)
    
    # Configure rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[RATE_LIMIT_DEFAULT],
        storage_uri=RATE_LIMIT_STORAGE_URL,
        strategy="fixed-window"
    )
    app.config['LIMITER'] = limiter
    
    # Configure simple health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
    
    # Configure proxy fix for proper IP detection behind load balancers
    if IS_PRODUCTION:
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=1,
            x_prefix=1
        )
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add metrics endpoint if enabled
    if ENABLE_METRICS:
        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
            '/metrics': make_wsgi_app()
        })
    
    return app

def register_blueprints(app):
    """Register all application blueprints."""
    from .entries import entries_bp
    from .embeddings import embeddings_bp
    from .profiles import profiles_bp
    from .tags import tags_bp
    from .core_pipeline import core_pipeline_bp
    
    app.register_blueprint(entries_bp)
    app.register_blueprint(embeddings_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(core_pipeline_bp)

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be processed.',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required.',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied.',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'status_code': 404
        }), 404
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded.',
            'status_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled Exception: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }), 500 