"""
Core pipeline API endpoint - Microservice Integration with Local Profile Management
"""

import requests
from typing import Optional, Dict, Any
from flask import Blueprint, request, jsonify
from datetime import datetime
import os
import asyncio

from .auth import require_auth
from .profile_manager import fetch_profile, update_profile, save_profile

core_pipeline_bp = Blueprint('core_pipeline', __name__)

# Microservice configuration
CORE_SERVICE_URL = os.getenv('BACKEND_CORE_URL', 'http://localhost:5001')


def call_core_service(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a call to the core microservice
    
    Args:
        endpoint: API endpoint (e.g., '/api/process-transcript')
        data: Request data
        
    Returns:
        Response from microservice
    """
    try:
        url = f"{CORE_SERVICE_URL}{endpoint}"
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Core service call failed: {str(e)}")


@core_pipeline_bp.route('/api/core/process-transcript', methods=['POST'])
@require_auth
def process_transcript_endpoint():
    """
    Process a transcript through the core pipeline with local profile management
    
    Expected JSON payload:
    {
        "transcript": "User's transcript text",
        "meta": {
            "device": "mobile",
            "silence_ms": 1000,
            "entry_id": "entry123"
        }
    }
    """
    try:
        # Get user ID from auth
        user_id = request.user_id
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        transcript = data.get('transcript')
        if not transcript:
            return jsonify({
                'success': False,
                'error': 'Transcript is required'
            }), 400
        
        # Load profile locally
        profile = asyncio.run(fetch_profile(user_id))
        
        # Prepare data for microservice (without profile management)
        service_data = {
            'user_id': user_id,
            'transcript': transcript,
            'meta': data.get('meta', {}),
            'profile': profile  # Send current profile for processing
        }
        
        # Call microservice for core processing
        result = call_core_service('/api/process-transcript', service_data)
        
        if not result.get('success'):
            return jsonify(result), 500
        
        # Extract results from microservice
        response_text = result.get('response_text', '')
        profile_update_data = result.get('updated_profile', {})
        debug_log = result.get('debug_log', [])
        
        # Update profile locally with the results
        if profile_update_data:
            # Extract data from profile update
            inference_data = profile_update_data.get('inference', {})
            signals_data = profile_update_data.get('signals', {})
            entry_data = profile_update_data.get('entry_data', {})
            
            # Update profile with new data
            updated_profile = update_profile(
                profile=profile,
                inference=inference_data,
                signals=signals_data,
                raw_text=transcript,
                meta=data.get('meta', {})
            )
            
            # Save updated profile to database
            asyncio.run(save_profile(user_id, updated_profile))
        
        # Return response
        response_data = {
            'success': True,
            'response_text': response_text,
            'debug_log': debug_log,
            'profile_updated': True
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Pipeline processing failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/extract-signals', methods=['POST'])
@require_auth
def extract_signals_endpoint():
    """
    Extract signals from transcript
    
    Expected JSON payload:
    {
        "transcript": "User's transcript text",
        "meta": {
            "device": "mobile",
            "silence_ms": 1000,
            "entry_id": "entry123"
        },
        "profile": {
            "user_id": "user123",
            "history": [...]
        }
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Call microservice
        result = call_core_service('/api/extract-signals', data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Signal extraction failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/run-inference', methods=['POST'])
@require_auth
def run_inference_endpoint():
    """
    Run inference on signals
    
    Expected JSON payload:
    {
        "signals": {
            "cleaned_text": "...",
            "tokens": [...],
            "keywords": [...],
            "energy_level": 2,
            "comparators": [...],
            "patterns": [...],
            "subtext_notes": [...],
            "context_tags": [...],
            "concept_tags": [...]
        },
        "profile": {
            "user_id": "user123",
            "history": [...]
        }
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Call microservice
        result = call_core_service('/api/run-inference', data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Inference failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/generate-reply', methods=['POST'])
@require_auth
def generate_reply_endpoint():
    """
    Generate empathetic reply
    
    Expected JSON payload:
    {
        "transcript": "User's transcript text",
        "signals": {...},
        "inference": {...},
        "profile": {...},
        "hints": {...}
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Call microservice
        result = call_core_service('/api/generate-reply', data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Reply generation failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/generate-insight', methods=['POST'])
@require_auth
def generate_insight_endpoint():
    """
    Generate macro insight
    
    Expected JSON payload:
    {
        "profile": {
            "user_id": "user123",
            "history": [...],
            "counters": {...}
        },
        "window": 7
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Call microservice
        result = call_core_service('/api/generate-insight', data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Insight generation failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/pick-style', methods=['POST'])
@require_auth
def pick_style_endpoint():
    """
    Pick next reply style
    
    Expected JSON payload:
    {
        "last_styles": ["empathy", "curiosity", "humor"]
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Call microservice
        result = call_core_service('/api/pick-style', data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Style picking failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/tone-hint', methods=['POST'])
@require_auth
def tone_hint_endpoint():
    """
    Get tone hint for emotion
    
    Expected JSON payload:
    {
        "emotion": "excited"
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Call microservice
        result = call_core_service('/api/tone-hint', data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Tone hint failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/upsert-embedding', methods=['POST'])
@require_auth
def upsert_embedding_endpoint():
    """
    Upsert embedding to store
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "entry_id": "entry123",
        "text": "Text to embed"
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Call microservice
        result = call_core_service('/api/upsert-embedding', data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Embedding upsert failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/search-similar', methods=['POST'])
@require_auth
def search_similar_endpoint():
    """
    Search for similar embeddings
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "text": "Text to search for",
        "k": 3
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Call microservice
        result = call_core_service('/api/search-similar', data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Similar search failed: {str(e)}'
        }), 500


@core_pipeline_bp.route('/api/core/health', methods=['GET'])
def core_health_check():
    """Health check for core pipeline"""
    try:
        # Check microservice health
        response = requests.get(f"{CORE_SERVICE_URL}/health", timeout=5)
        microservice_healthy = response.status_code == 200
        
        return jsonify({
            'success': True,
            'microservice_available': microservice_healthy,
            'microservice_url': CORE_SERVICE_URL,
            'status': 'healthy' if microservice_healthy else 'microservice_unavailable'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'microservice_available': False,
            'microservice_url': CORE_SERVICE_URL,
            'status': 'microservice_unavailable',
            'error': str(e)
        }), 503 