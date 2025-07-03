import os
import signal
import sys
from src.app_factory import create_app
from src.config import IS_PRODUCTION, WORKER_PROCESSES, WORKER_THREADS

# Create the Flask application
app = create_app()

# Import modular endpoints after app creation
from src.analyze import analyze_endpoint
from src.save_entry import save_entry_endpoint
from src.emotion_trend import emotion_trend_endpoint
from src.pick_emoji import pick_emoji_endpoint
from src.pick_emoji_batch import pick_emoji_batch_endpoint
from src.run_pipeline import run_pipeline_endpoint
from src.empathy import empathy_endpoint
from src.update_tags import update_tags_endpoint
from src.update_transcript import update_transcript_endpoint
from src.test_openai import test_openai_endpoint
from src.test_tags import test_tags_endpoint
from src.whisper import whisper_endpoint
from src.auth import require_auth, get_user_id_from_request, get_user_email_from_request

# Import new database API blueprints
from src.entries import entries_bp
from src.embeddings import embeddings_bp
from src.profiles import profiles_bp
from src.tags import tags_bp

# Import core pipeline blueprint
from src.core_pipeline import core_pipeline_bp

# Get Supabase client from app config
supabase = app.config['SUPABASE_CLIENT']

@app.route('/')
def hello():
    return 'Hello, Sentari!'

# API Routes with authentication
@app.route('/api/analyze', methods=['POST'])
@require_auth
def analyze():
    user_id = get_user_id_from_request()
    return analyze_endpoint(supabase, user_id)

@app.route('/api/save-entry', methods=['POST'])
@require_auth
def save_entry():
    user_id = get_user_id_from_request()
    return save_entry_endpoint(supabase, user_id)

@app.route('/api/emotion-trend', methods=['POST'])
@require_auth
def emotion_trend():
    user_id = get_user_id_from_request()
    return emotion_trend_endpoint(supabase, user_id)

@app.route('/api/pick-emoji', methods=['POST'])
@require_auth
def pick_emoji():
    user_id = get_user_id_from_request()
    return pick_emoji_endpoint(supabase, user_id)

@app.route('/api/pick-emoji-batch', methods=['POST'])
@require_auth
def pick_emoji_batch():
    user_id = get_user_id_from_request()
    return pick_emoji_batch_endpoint(supabase, user_id)

@app.route('/api/run', methods=['POST'])
def run_pipeline():
    return run_pipeline_endpoint()

@app.route('/api/empathy', methods=['POST'])
def empathy():
    return empathy_endpoint()

@app.route('/api/update-tags', methods=['POST'])
@require_auth
def update_tags():
    user_id = get_user_id_from_request()
    user_email = get_user_email_from_request()
    return update_tags_endpoint(supabase, user_id, user_email)

@app.route('/api/update-transcript', methods=['POST'])
@require_auth
def update_transcript():
    user_id = get_user_id_from_request()
    return update_transcript_endpoint(supabase, user_id)

@app.route('/api/test-openai', methods=['GET'])
def test_openai():
    return test_openai_endpoint()

@app.route('/api/test-tags', methods=['GET', 'POST'])
def test_tags():
    return test_tags_endpoint()

# Whisper endpoint (audio transcription) - using modular implementation
@app.route('/api/whisper', methods=['POST'])
def whisper():
    return whisper_endpoint()

def signal_handler(sig, frame):
    """Handle graceful shutdown."""
    app.logger.info("Received shutdown signal, shutting down gracefully...")
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if IS_PRODUCTION:
        # Use Gunicorn for production
        from gunicorn.app.base import BaseApplication
        
        class GunicornApp(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key, value)
            
            def load(self):
                return self.application
        
        options = {
            'bind': '0.0.0.0:5000',
            'workers': WORKER_PROCESSES,
            'worker_class': 'sync',
            'worker_connections': 1000,
            'max_requests': 1000,
            'max_requests_jitter': 50,
            'timeout': 30,
            'keepalive': 2,
            'preload_app': True,
        }
        
        GunicornApp(app, options).run()
    else:
        # Use Flask development server for development
        app.run(host='0.0.0.0', port=8000, debug=True)