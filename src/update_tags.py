from flask import request, jsonify
from supabase import Client
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# Predefined tags (matching frontend)
PREDEFINED_TAGS = [
    {'tag': 'happy', 'category': 'emotion'},
    {'tag': 'sad', 'category': 'emotion'},
    {'tag': 'anxious', 'category': 'emotion'},
    {'tag': 'excited', 'category': 'emotion'},
    {'tag': 'calm', 'category': 'emotion'},
    {'tag': 'frustrated', 'category': 'emotion'},
    {'tag': 'grateful', 'category': 'emotion'},
    {'tag': 'confused', 'category': 'emotion'},
    {'tag': 'reflection', 'category': 'purpose'},
    {'tag': 'planning', 'category': 'purpose'},
    {'tag': 'venting', 'category': 'purpose'},
    {'tag': 'sharing', 'category': 'purpose'},
    {'tag': 'question', 'category': 'purpose'},
    {'tag': 'goal-setting', 'category': 'purpose'},
    {'tag': 'work', 'category': 'topic'},
    {'tag': 'personal', 'category': 'topic'},
    {'tag': 'health', 'category': 'topic'},
    {'tag': 'relationships', 'category': 'topic'},
    {'tag': 'goals', 'category': 'topic'},
    {'tag': 'daily-life', 'category': 'topic'},
    {'tag': 'learning', 'category': 'topic'},
    {'tag': 'creative', 'category': 'topic'}
]

def get_local_timestamp():
    """Get current timestamp in local timezone"""
    return datetime.now().isoformat()

def update_tags_endpoint(supabase: Client, user_id: str, user_email: str):
    """Handle updating user tags for entries"""
    try:
        data = request.get_json()
        entry_id = data.get('entryId')
        tags_user = data.get('tags_user')
        
        if not entry_id or not isinstance(tags_user, list):
            return jsonify({
                'error': 'Missing or invalid entryId or tags_user'
            }), 400
            
        # Validate tags format
        predefined_tag_names = [tag['tag'] for tag in PREDEFINED_TAGS]
        invalid_format = any(
            not isinstance(tag, str) or
            tag.strip() == '' or
            len(tag) > 50 or
            not re.match(r'^[a-z0-9_-]+$', tag)
            for tag in tags_user
        )
        
        if invalid_format:
            return jsonify({
                'error': 'Invalid tag format',
                'details': 'Tags must be non-empty strings (max 50 chars) containing only lowercase letters, numbers, underscore and hyphen',
                'suggestion': 'Example valid tags: happy, custom-tag, my_tag_123'
            }), 400
            
        # Split tags into predefined and custom for logging
        custom_tags = [tag for tag in tags_user if tag not in predefined_tag_names]
        standard_tags = [tag for tag in tags_user if tag in predefined_tag_names]
        
        logger.info(f'Updating tags for entry: {entry_id}, total: {len(tags_user)}, standard: {standard_tags}, custom: {custom_tags}')
        
        # Get local time
        local_time = get_local_timestamp()
        
        # Update tags in database
        update_data = {
            'tags_user': tags_user,
            'tags_log': {
                'timestamp': local_time,
                'standardTags': standard_tags,
                'customTags': custom_tags,
                'updatedBy': user_email
            },
            'updated_at': local_time
        }
        
        result = supabase.table('voice_entries').update(update_data).eq('id', entry_id).eq('user_id', user_id).execute()
        
        # Check for errors in the result
        if hasattr(result, 'error') and result.error:
            logger.error(f'Supabase update error: {result.error}')
            error_message = str(result.error) if result.error else 'Database update failed'
            return jsonify({
                'error': f'Failed to update tags: {error_message}'
            }), 500
            
        if not result.data or len(result.data) == 0:
            return jsonify({
                'error': 'Entry not found or access denied'
            }), 404
            
        logger.info(f'Tags updated successfully: {entry_id}, updatedAt: {result.data[0]["updated_at"]}')
        
        return jsonify({
            'success': True,
            'entry': result.data[0],
            'message': 'Tags updated successfully',
            'stats': {
                'total': len(tags_user),
                'standard': len(standard_tags),
                'custom': len(custom_tags)
            }
        })
        
    except Exception as e:
        logger.error(f'Update tags API error: {e}')
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500 