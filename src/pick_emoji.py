from flask import request, jsonify
from supabase import Client
import openai
import os
import logging
from datetime import datetime, timedelta
from .config import OPENAI_CHAT_MODEL

logger = logging.getLogger(__name__)


##Emojis add fun to the response, but wondering if it's efficient to do it like this or ask at a different stage, like when we generate the insights.
##Doing it separately may skew the answer away from the original interpretation (that coul be a good thing too, but we must test...)
##This is another place where I think it could be interesting to test few-shot prompting to enhance results.
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

##Check if this same emoji has been used recently...
def pick_emoji_endpoint(supabase: Client, user_id: str):
    """Handle emoji generation for entries"""
    try:
        data = request.get_json()
        transcript = data.get('transcript')
        entry_id = data.get('entryId')
        
        if not entry_id or not isinstance(entry_id, str):
            return jsonify({'error': 'Missing or invalid entryId'}), 400
            
        # Fetch entry to enforce 7-day limit & avoid duplicates
        entry_result = supabase.table('voice_entries').select('id, transcript_raw, transcript_user, entry_emoji, created_at').eq('id', entry_id).eq('user_id', user_id).single().execute()
        
        # Check for errors in the result
        if hasattr(entry_result, 'error') and entry_result.error:
            logger.error(f'Failed to fetch entry meta: {entry_result.error}')
            return jsonify({'error': 'Entry not found or access denied'}), 404
            
        entry_meta = entry_result.data
        
        # Skip if emoji already exists to prevent re-compute
        if entry_meta.get('entry_emoji'):
            logger.info('Emoji already exists, skipping GPT call')
            return jsonify({
                'success': True,
                'emoji': entry_meta['entry_emoji'],
                'source': 'funky_emoji_v1',
                'skipped': True
            })
            
        # Decide which transcript to use
        transcript_to_use = None
        if transcript and isinstance(transcript, str) and transcript.strip():
            transcript_to_use = transcript.strip()
        elif entry_meta.get('transcript_user') and isinstance(entry_meta['transcript_user'], str):
            transcript_to_use = entry_meta['transcript_user']
            
        if not transcript_to_use:
            return jsonify({'error': 'Transcript not found for entry'}), 400
            
        # 7-day limit check
        created_at = datetime.fromisoformat(entry_meta['created_at'].replace('Z', '+00:00'))
        now = datetime.now().replace(tzinfo=created_at.tzinfo)
        seven_days_ago = now - timedelta(days=7)
        
        if created_at < seven_days_ago:
            logger.info('Entry older than 7 days, skipping emoji generation')
            return jsonify({'success': False, 'reason': 'older_than_7_days'})
            
        # Get emoji from GPT
        emoji_result = pick_funky_emoji(transcript_to_use)
        logger.info(f'Funky emoji selected: {emoji_result}')
        
        # Update entry with emoji
        update_result = supabase.table('voice_entries').update({
            'entry_emoji': emoji_result['emoji'],
            'emoji_source': emoji_result['source'],
            'emoji_log': {
                'timestamp': datetime.now().isoformat(),
                'emoji': emoji_result['emoji'],
                'source': emoji_result['source'],
                'transcript_length': len(transcript)
            },
            'updated_at': get_local_timestamp()
        }).eq('id', entry_id).eq('user_id', user_id).execute()
        
        # Check for errors in the result
        if hasattr(update_result, 'error') and update_result.error:
            logger.error(f'Failed to update entry with emoji: {update_result.error}')
            error_message = str(update_result.error)
            
            # Handle missing column error gracefully
            if 'column' in error_message and 'does not exist' in error_message:
                logger.warning('Database missing columns for emoji, returning result without DB update')
            else:
                return jsonify({'error': 'Failed to save emoji to database'}), 500
                
        return jsonify({
            'success': True,
            'emoji': emoji_result['emoji'],
            'source': emoji_result['source']
        })
        
    except Exception as e:
        logger.error(f'Pick Emoji API error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 