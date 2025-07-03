"""
Entries API endpoints for voice entries operations.
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Any, Optional
import json
from .auth import require_auth
from .db import VoiceEntriesDB

entries_bp = Blueprint('entries', __name__)
entries_db = VoiceEntriesDB()


@entries_bp.route('/api/entries', methods=['GET'])
@require_auth
def get_entries(user_id: str):
    """Get user entries with optional filters."""
    try:
        # Get query parameters
        limit = request.args.get('limit', type=int, default=10)
        offset = request.args.get('offset', type=int, default=0)
        tags = request.args.getlist('tags')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # If tags are provided, use filtered endpoint
        if tags or start_date or end_date:
            entries = entries_db.get_entries_with_filters(
                user_id=user_id,
                tags=tags if tags else None,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset
            )
        else:
            entries = entries_db.get_user_entries(
                user_id=user_id,
                limit=limit,
                offset=offset
            )
        
        return jsonify({
            'success': True,
            'data': entries
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@entries_bp.route('/api/entries/<entry_id>', methods=['GET'])
@require_auth
def get_entry(user_id: str, entry_id: str):
    """Get a specific entry by ID."""
    try:
        entry = entries_db.get_entry_by_id(entry_id, user_id)
        
        if not entry:
            return jsonify({
                'success': False,
                'error': 'Entry not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': entry
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@entries_bp.route('/api/entries/search', methods=['POST'])
@require_auth
def search_entries(user_id: str):
    """Search entries by text or tags."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Check if query looks like a tag
        tag_candidate = query.lower()
        if query.startswith('#'):
            tag_candidate = query[1:].lower()
        
        # Try tag search first
        tag_entries = entries_db.search_entries_by_tag(user_id, tag_candidate)
        
        # Try vector search
        try:
            vector_entries = entries_db.search_entries(
                user_id=user_id,
                query_text=query,
                limit=20,
                similarity_threshold=0.12
            )
        except Exception:
            # Fallback to text search
            vector_entries = entries_db.search_entries_text(user_id, query, 20)
        
        # Combine and deduplicate results
        all_entries = tag_entries + vector_entries
        seen_ids = set()
        unique_entries = []
        
        for entry in all_entries:
            if entry['id'] not in seen_ids:
                unique_entries.append(entry)
                seen_ids.add(entry['id'])
        
        return jsonify({
            'success': True,
            'data': unique_entries
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@entries_bp.route('/api/entries/<entry_id>', methods=['DELETE'])
@require_auth
def delete_entry(user_id: str, entry_id: str):
    """Soft delete an entry."""
    try:
        success = entries_db.soft_delete_entry(entry_id, user_id)
        
        return jsonify({
            'success': True,
            'data': {'deleted': success}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@entries_bp.route('/api/entries/<entry_id>/transcript', methods=['PUT'])
@require_auth
def update_transcript(user_id: str, entry_id: str):
    """Update entry transcript."""
    try:
        data = request.get_json()
        transcript = data.get('transcript')
        
        if not transcript:
            return jsonify({
                'success': False,
                'error': 'Transcript is required'
            }), 400
        
        updated_entry = entries_db.update_entry_transcript(entry_id, user_id, transcript)
        
        return jsonify({
            'success': True,
            'data': updated_entry
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@entries_bp.route('/api/entries/<entry_id>/tags', methods=['PUT'])
@require_auth
def update_tags(user_id: str, entry_id: str):
    """Update entry tags."""
    try:
        data = request.get_json()
        tags = data.get('tags', [])
        
        if not isinstance(tags, list):
            return jsonify({
                'success': False,
                'error': 'Tags must be a list'
            }), 400
        
        updated_entry = entries_db.update_entry_tags(entry_id, user_id, tags)
        
        return jsonify({
            'success': True,
            'data': updated_entry
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@entries_bp.route('/api/entries/<entry_id>/field', methods=['PUT'])
@require_auth
def update_field(user_id: str, entry_id: str):
    """Update a specific field in an entry."""
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        if not field:
            return jsonify({
                'success': False,
                'error': 'field is required'
            }), 400
        
        updated_entry = entries_db.update_entry_field(entry_id, user_id, field, value)
        
        return jsonify({
            'success': True,
            'data': updated_entry
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@entries_bp.route('/api/entries/recent-emoji', methods=['GET'])
@require_auth
def get_recent_emoji_entries(user_id: str):
    """Get recent entries with emojis."""
    try:
        limit = request.args.get('limit', type=int, default=50)
        entries = entries_db.get_recent_emoji_entries(user_id, limit)
        
        return jsonify({
            'success': True,
            'data': entries
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@entries_bp.route('/api/entries/tags', methods=['GET'])
@require_auth
def get_available_tags(user_id: str):
    """Get all available tags for a user."""
    try:
        tags = entries_db.get_available_tags(user_id)
        
        return jsonify({
            'success': True,
            'data': tags
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 