"""
Tags API endpoints for tag operations.
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Any
import json
from .auth import require_auth
from .db import TagsDB

tags_bp = Blueprint('tags', __name__)
tags_db = TagsDB()


@tags_bp.route('/api/tags', methods=['GET'])
@require_auth
def get_all_tags(user_id: str):
    """Get all tags for a user."""
    try:
        tags = tags_db.get_all_tags(user_id)
        
        return jsonify({
            'success': True,
            'data': tags
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tags_bp.route('/api/tags/<tag>', methods=['GET'])
@require_auth
def get_entries_by_tag(user_id: str, tag: str):
    """Get all entries that have a specific tag."""
    try:
        entries = tags_db.get_entries_by_tag(user_id, tag)
        
        return jsonify({
            'success': True,
            'data': entries
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tags_bp.route('/api/tags/search', methods=['POST'])
@require_auth
def get_entries_by_tags(user_id: str):
    """Get all entries that have any of the specified tags."""
    try:
        data = request.get_json()
        tags = data.get('tags', [])
        
        if not isinstance(tags, list):
            return jsonify({
                'success': False,
                'error': 'tags must be a list'
            }), 400
        
        entries = tags_db.get_entries_by_tags(user_id, tags)
        
        return jsonify({
            'success': True,
            'data': entries
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tags_bp.route('/api/tags/usage', methods=['GET'])
@require_auth
def get_tag_usage_count(user_id: str):
    """Get usage count for each tag."""
    try:
        tag_counts = tags_db.get_tag_usage_count(user_id)
        
        return jsonify({
            'success': True,
            'data': tag_counts
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tags_bp.route('/api/tags/popular', methods=['GET'])
@require_auth
def get_popular_tags(user_id: str):
    """Get most popular tags for a user."""
    try:
        limit = request.args.get('limit', type=int, default=10)
        popular_tags = tags_db.get_popular_tags(user_id, limit)
        
        return jsonify({
            'success': True,
            'data': popular_tags
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 