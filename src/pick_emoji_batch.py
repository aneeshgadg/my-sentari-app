from flask import request, jsonify
from supabase import Client
import openai
import os
import logging
from datetime import datetime, timedelta
from .config import OPENAI_CHAT_MODEL

logger = logging.getLogger(__name__)

def pick_funky_emoji(transcript: str):
    """Generate a funky emoji based on transcript content"""
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        prompt = f"""
        Based on this transcript, pick ONE emoji that best represents the mood, emotion, or theme.
        Choose a fun, expressive emoji that captures the essence of what they're saying.
        
        Transcript: "{transcript}"
        
        Respond with only the emoji character, no text or explanation.
        """
        
        response = openai.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=10
        )
        
        emoji = response.choices[0].message.content.strip()
        
        # Validate that it's actually an emoji
        if len(emoji) > 4:  # Most emojis are 1-4 characters
            emoji = "😊"  # Fallback emoji
            
        return {
            "emoji": emoji,
            "source": "funky_emoji_v1"
        }
        
    except Exception as e:
        logger.error(f"Error in pick_funky_emoji: {e}")
        return {
            "emoji": "😊",
            "source": "fallback"
        }

def get_local_timestamp():
    """Get current timestamp in local timezone"""
    return datetime.now().isoformat()

def pick_emoji_batch_endpoint(supabase: Client, user_id: str):
    """Handle batch emoji generation for multiple entries"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 15)
        
        # Validate and clamp limit
        if isinstance(limit, int) and limit > 0:
            limit = min(limit, 50)
        else:
            limit = 15
            
        # Fetch latest entries (limit) regardless of emoji
        fetch_result = supabase.table('voice_entries').select('id, transcript_raw, transcript_user, entry_emoji, created_at').eq('user_id', user_id).is_('entry_emoji', 'null').limit(limit).execute()
        
        # Check for errors in the result
        if hasattr(fetch_result, 'error') and fetch_result.error:
            logger.error(f'Batch fetch error: {fetch_result.error}')
            error_message = str(fetch_result.error) if fetch_result.error else 'Database fetch failed'
            return jsonify({'error': error_message}), 500
            
        entries = fetch_result.data
        if not entries:
            return jsonify({'processed': 0, 'message': 'No entries need emoji'})
            
        processed = 0
        results = []
        
        for entry in entries:
            # Skip if emoji already exists
            if entry.get('entry_emoji'):
                results.append({'id': entry['id'], 'skipped': 'already_has_emoji'})
                continue
                
            # 7-day window check
            created_at = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
            now = datetime.now().replace(tzinfo=created_at.tzinfo)
            if now - created_at > timedelta(days=7):
                results.append({'id': entry['id'], 'skipped': 'older_than_7_days'})
                continue
                
            transcript = entry.get('transcript_user', '')
            if not transcript:
                results.append({'id': entry['id'], 'skipped': 'no_transcript'})
                continue
                
            try:
                emoji_result = pick_funky_emoji(transcript)
                
                update_result = supabase.table('voice_entries').update({
                    'entry_emoji': emoji_result['emoji'],
                    'emoji_source': emoji_result['source'],
                    'emoji_log': {
                        'timestamp': datetime.now().isoformat(),
                        'emoji': emoji_result['emoji'],
                        'source': 'batch_generation',
                        'transcript_length': len(transcript)
                    },
                    'updated_at': get_local_timestamp()
                }).eq('id', entry['id']).eq('user_id', user_id).execute()
                
                # Check for errors in the result
                if hasattr(update_result, 'error') and update_result.error:
                    error_message = str(update_result.error) if update_result.error else 'Database update failed'
                    results.append({'id': entry['id'], 'error': error_message})
                    logger.error(f'Failed to update entry {entry["id"]}: {error_message}')
                else:
                    processed += 1
                    results.append({'id': entry['id'], 'emoji': emoji_result['emoji']})
                    
            except Exception as e:
                results.append({'id': entry['id'], 'error': str(e)})
                
        return jsonify({
            'processed': processed,
            'total': len(entries),
            'results': results
        })
        
    except Exception as e:
        logger.error(f'Batch API error: {e}')
        return jsonify({'error': 'Internal error'}), 500 