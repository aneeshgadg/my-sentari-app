from flask import request, jsonify
from supabase import Client
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

def get_local_timestamp():
    """Get current timestamp in local timezone"""
    return datetime.now().isoformat()

def save_entry_endpoint(supabase: Client, user_id: str):
    """Handle saving voice entries to database"""
    try:
        data = request.get_json()
        logger.info(f'Incoming request body: {data}')
        logger.info(f'User authenticated: {user_id}')
        
        # Extract fields from request
        transcript_raw = data.get('transcript_raw')
        transcript_user = data.get('transcript_user')
        language_detected = data.get('language_detected')
        language_rendered = data.get('language_rendered', 'en')
        tags_model = data.get('tags_model', [])
        tags_user = data.get('tags_user', [])
        category = data.get('category', 'uncategorized')
        audio_duration = data.get('audio_duration', 0)
        client_timestamp = data.get('client_timestamp')
        
        # Use client supplied local time if provided, else fallback to server-local time
        local_time = client_timestamp or get_local_timestamp()
        
        # Basic validation
        if audio_duration < 1:
            return jsonify({'error': 'Recording too short (less than 1 second).'}), 400
            
        if not transcript_raw or transcript_raw.strip() == '':
            return jsonify({'error': 'No speech detected in recording.'}), 400
            
        # Generate unique ID for the entry
        entry_id = str(uuid.uuid4())
            
        # Insert entry into database
        entry_data = {
            'id': entry_id,
            'user_id': user_id,
            'transcript_raw': transcript_raw,
            'transcript_user': transcript_user,
            'language_detected': language_detected,
            'language_rendered': language_rendered,
            'tags_model': tags_model,
            'tags_user': tags_user,
            'category': category,
            'audio_duration': audio_duration,
            'created_at': local_time,
            'updated_at': local_time
        }
        
        result = supabase.table('voice_entries').insert([entry_data]).execute()
        
        # Check for errors in the result
        if hasattr(result, 'error') and result.error:
            logger.error(f'Supabase insert error: {result.error}')
            error_message = str(result.error) if result.error else 'Database insert failed'
            return jsonify({'error': error_message}), 500
            
        logger.info(f'Entry saved successfully: {result.data}')
        return jsonify({'success': True, 'entry': result.data})
        
    except Exception as e:
        logger.error(f'Save entry API error: {e}')
        return jsonify({'error': 'Failed to save entry', 'details': str(e)}), 500 