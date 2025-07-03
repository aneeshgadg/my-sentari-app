"""
Embeddings API endpoints for voice embeddings operations.
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Any
import json
from .auth import require_auth
from .db import VoiceEmbeddingsDB

embeddings_bp = Blueprint('embeddings', __name__)
embeddings_db = VoiceEmbeddingsDB()


@embeddings_bp.route('/api/embeddings', methods=['POST'])
@require_auth
def upsert_embedding(user_id: str):
    """Upsert an embedding for a voice entry."""
    try:
        data = request.get_json()
        entry_id = data.get('entry_id')
        text = data.get('text')
        embedding = data.get('embedding')
        
        if not all([entry_id, text, embedding]):
            return jsonify({
                'success': False,
                'error': 'entry_id, text, and embedding are required'
            }), 400
        
        if not isinstance(embedding, list):
            return jsonify({
                'success': False,
                'error': 'embedding must be a list of numbers'
            }), 400
        
        success = embeddings_db.upsert_embedding(user_id, entry_id, text, embedding)
        
        return jsonify({
            'success': True,
            'data': {'upserted': success}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@embeddings_bp.route('/api/embeddings/search', methods=['POST'])
@require_auth
def search_embeddings(user_id: str):
    """Search for similar embeddings."""
    try:
        data = request.get_json()
        query_embedding = data.get('query_embedding')
        match_threshold = data.get('match_threshold', 0.75)
        match_count = data.get('match_count', 3)
        
        if not query_embedding:
            return jsonify({
                'success': False,
                'error': 'query_embedding is required'
            }), 400
        
        if not isinstance(query_embedding, list):
            return jsonify({
                'success': False,
                'error': 'query_embedding must be a list of numbers'
            }), 400
        
        results = embeddings_db.search_similar_embeddings(
            user_id=user_id,
            query_embedding=query_embedding,
            match_threshold=match_threshold,
            match_count=match_count
        )
        
        return jsonify({
            'success': True,
            'data': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@embeddings_bp.route('/api/embeddings/<entry_id>', methods=['GET'])
@require_auth
def get_embedding(user_id: str, entry_id: str):
    """Get embedding by entry ID."""
    try:
        embedding = embeddings_db.get_embedding_by_entry_id(entry_id, user_id)
        
        if not embedding:
            return jsonify({
                'success': False,
                'error': 'Embedding not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': embedding
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@embeddings_bp.route('/api/embeddings/<entry_id>', methods=['DELETE'])
@require_auth
def delete_embedding(user_id: str, entry_id: str):
    """Delete an embedding."""
    try:
        success = embeddings_db.delete_embedding(entry_id, user_id)
        
        return jsonify({
            'success': True,
            'data': {'deleted': success}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@embeddings_bp.route('/api/embeddings', methods=['GET'])
@require_auth
def get_user_embeddings(user_id: str):
    """Get all embeddings for a user."""
    try:
        limit = request.args.get('limit', type=int)
        embeddings = embeddings_db.get_user_embeddings(user_id, limit)
        
        return jsonify({
            'success': True,
            'data': embeddings
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 