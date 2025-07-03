"""
Profiles API endpoints for user profile operations.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import json
from .auth import require_auth
from .db import ProfilesDB

profiles_bp = Blueprint('profiles', __name__)
profiles_db = ProfilesDB()


@profiles_bp.route('/api/profiles', methods=['GET'])
@require_auth
def get_profile(user_id: str):
    """Get user profile."""
    try:
        profile = profiles_db.get_profile(user_id)
        
        return jsonify({
            'success': True,
            'data': profile
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profiles_bp.route('/api/profiles', methods=['POST'])
@require_auth
def upsert_profile(user_id: str):
    """Upsert user profile."""
    try:
        data = request.get_json()
        profile = data.get('profile')
        concepts = data.get('concepts')
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'profile is required'
            }), 400
        
        success = profiles_db.upsert_profile(user_id, profile, concepts)
        
        return jsonify({
            'success': True,
            'data': {'upserted': success}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profiles_bp.route('/api/profiles/field', methods=['PUT'])
@require_auth
def update_profile_field(user_id: str):
    """Update a specific field in the profile."""
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        if not field:
            return jsonify({
                'success': False,
                'error': 'field is required'
            }), 400
        
        success = profiles_db.update_profile_field(user_id, field, value)
        
        return jsonify({
            'success': True,
            'data': {'updated': success}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profiles_bp.route('/api/profiles', methods=['DELETE'])
@require_auth
def delete_profile(user_id: str):
    """Delete user profile."""
    try:
        success = profiles_db.delete_profile(user_id)
        
        return jsonify({
            'success': True,
            'data': {'deleted': success}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profiles_bp.route('/api/profiles/concepts', methods=['GET'])
@require_auth
def get_concepts(user_id: str):
    """Get user profile concepts."""
    try:
        concepts = profiles_db.get_profile_concepts(user_id)
        
        return jsonify({
            'success': True,
            'data': concepts
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profiles_bp.route('/api/profiles/concepts', methods=['PUT'])
@require_auth
def update_concepts(user_id: str):
    """Update user concepts."""
    try:
        data = request.get_json()
        concepts = data.get('concepts')
        
        if not concepts:
            return jsonify({
                'success': False,
                'error': 'concepts is required'
            }), 400
        
        success = profiles_db.update_concepts(user_id, concepts)
        
        return jsonify({
            'success': True,
            'data': {'updated': success}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 