from flask import request, jsonify
from supabase import Client
import openai
import os
import logging
from datetime import datetime
from .config import OPENAI_CHAT_MODEL

logger = logging.getLogger(__name__)

def classify_mini_tags(transcript: str):
    """Classify transcript into purpose, tone, and category tags"""
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        ##Should we try a different approach for the 3 tags? Should we use more, i.e. 3 tags per classification, so 9 total?
        ##Also do we need to define confidence better? Do we need a feedback system that says if it is below 0.8 then it should be run again?
        prompt = f"""
        Analyze this transcript and classify it into exactly 3 tags:
        1. Purpose (why they're speaking): reflection, planning, venting, sharing, question, goal-setting
        2. Tone (emotional state): happy, sad, anxious, excited, calm, frustrated, grateful, confused
        3. Category (topic area): work, personal, health, relationships, goals, daily-life, learning, creative
        
        Transcript: "{transcript}"
        
        
        Respond in JSON format:
        {{
            "purpose": "tag_name",
            "tone": "tag_name", 
            "category": "tag_name",
            "confidence": 0.85
        }}
        """
        
        ## Is temperature something we should tune depending on the type of user? Some users are more logical, whereas others are more emotional...
        response = openai.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        
        result = response.choices[0].message.content
        # Parse JSON response
        import json
        parsed = json.loads(result)
        
        return {
            "purpose": parsed.get("purpose", "reflection"),
            "tone": parsed.get("tone", "calm"),
            "category": parsed.get("category", "personal"),
            "confidence": parsed.get("confidence", 0.8)
        }
        
    except Exception as e:
        logger.error(f"Error in classify_mini_tags: {e}")
        return {
            "purpose": "reflection",
            "tone": "calm", 
            "category": "personal",
            "confidence": 0.5
        }

def analyze_endpoint(supabase: Client, user_id: str):
    """Handle tag analysis for transcripts"""
    try:
        data = request.get_json()
        transcript = data.get('transcript')
        entry_id = data.get('entryId')
        
        if not transcript or not isinstance(transcript, str):
            return jsonify({'error': 'Missing or invalid transcript'}), 400
            
        logger.info(f'Starting tag analysis for transcript: {transcript[:100]}...')
        
        # Classify tags
        mini = classify_mini_tags(transcript)
        selected_tags = [mini['purpose'], mini['tone'], mini['category']]
        
        logger.info(f'Tag analysis completed: {mini}')
        
        # Update entry if entryId provided
        if entry_id:
            # Check existing entry
            existing_entry = supabase.table('voice_entries').select('tags_model, tags_user').eq('id', entry_id).eq('user_id', user_id).execute()
            
            update_data = {}
            
            # Only set tags_model if it doesn't exist or is empty
            if not existing_entry.data or not existing_entry.data[0].get('tags_model'):
                update_data['tags_model'] = selected_tags
                
            # Only set tags_user if it doesn't exist or is empty  
            if not existing_entry.data or not existing_entry.data[0].get('tags_user'):
                update_data['tags_user'] = selected_tags
                
            if update_data:
                result = supabase.table('voice_entries').update({
                    'tags_model': selected_tags,
                    'tags_log': {
                        'timestamp': datetime.now().isoformat(),
                        'tags': selected_tags,
                        'confidence': mini['confidence'],
                        'reasoning': f"Tag analysis completed: {mini}"
                    }
                }).eq('id', entry_id).eq('user_id', user_id).execute()
                
                # Check for errors in the result
                if hasattr(result, 'error') and result.error:
                    logger.error(f'Failed to update entry with tags: {result.error}')
                    # Continue processing even if DB update fails
                    
        return jsonify({
            'success': True,
            'analysis': mini,
            'selectedTags': selected_tags,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Analysis API error: {e}')
        return jsonify({
            'success': False,
            'error': 'Tag analysis failed',
            'details': str(e)
        }), 500 