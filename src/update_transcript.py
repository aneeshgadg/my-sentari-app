from flask import request, jsonify
from supabase import Client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_local_timestamp():
    """Get current timestamp in local timezone"""
    return datetime.now().isoformat()

def update_transcript_endpoint(supabase: Client, user_id: str):
    """Handle updating user transcripts for entries"""
    try:
        data = request.get_json()
        entry_id = data.get('entryId')
        transcript_user = data.get('transcript_user')
        
        if not entry_id or not isinstance(transcript_user, str):
            return jsonify({
                'error': 'Missing or invalid entryId or transcript_user'
            }), 400
            
        logger.info(f'Updating transcript for entry: {entry_id}, newLength: {len(transcript_user)}')
        
        # Update transcript_user and explicitly set updated_at to local time
        update_data = {
            'transcript_user': transcript_user.strip(),
            'updated_at': get_local_timestamp()
        }
        
        result = supabase.table('voice_entries').update(update_data).eq('id', entry_id).eq('user_id', user_id).execute()
        
        # Check for errors in the result
        if hasattr(result, 'error') and result.error:
            logger.error(f'Supabase update error: {result.error}')
            error_message = str(result.error) if result.error else 'Database update failed'
            return jsonify({
                'error': f'Failed to update transcript: {error_message}'
            }), 500
            
        if not result.data or len(result.data) == 0:
            return jsonify({
                'error': 'Entry not found or access denied'
            }), 404
            
        logger.info(f'Transcript updated successfully: {entry_id}, updatedAt: {result.data[0]["updated_at"]}')
        
        return jsonify({
            'success': True,
            'entry': result.data[0],
            'message': 'Transcript updated successfully'
        })
        
    except Exception as e:
        logger.error(f'Update transcript API error: {e}')
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500 