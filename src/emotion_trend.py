from flask import request, jsonify
from supabase import Client
import openai
import os
import logging
from datetime import datetime, timedelta
from .config import OPENAI_CHAT_MODEL

logger = logging.getLogger(__name__)

##Consider asking it to determine polarity and/or compound sentiment score...
###May be useful to employ and test few-shot prompting here. Seems less effective to do zero-shot.
def analyze_emotion(text: str):
    """Analyze emotion score for given text"""
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        prompt = f"""
        Analyze the emotional tone of this text and provide a score from -1 (very negative) to 1 (very positive).
        Consider emotions like happiness, sadness, anger, excitement, anxiety, calmness, etc.
        
        Text: "{text}"
        
        Respond with only a number between -1 and 1, where:
        -1 = very negative emotions (sad, angry, anxious, frustrated)
        0 = neutral emotions
        1 = very positive emotions (happy, excited, grateful, content)
        
        Score: """
        
        response = openai.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        
        score_text = response.choices[0].message.content.strip()
        try:
            score = float(score_text)
            # Clamp to valid range
            score = max(-1.0, min(1.0, score))
            return score, f"GPT analysis: {score_text}"
        except ValueError:
            logger.warning(f"Could not parse emotion score: {score_text}")
            return 0.0, f"Parse error: {score_text}"
            
    except Exception as e:
        logger.error(f"Error in analyze_emotion: {e}")
        return 0.0, f"Error: {str(e)}"

def get_local_timestamp():
    """Get current timestamp in local timezone"""
    return datetime.now().isoformat()

##This is like the short-term check. Would be interesting to play around and check how many days is most efficient. How many days constitute a new cycle of life on average?
def emotion_trend_endpoint(supabase: Client, user_id: str):
    """Handle emotion trend analysis for the last 7 days"""
    try:
        # 7 days window
        since = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Fetch entries for last 7 days
        result = supabase.table('voice_entries').select('id, created_at, transcript_user').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        
        # Check for errors in the result
        if hasattr(result, 'error') and result.error:
            error_message = str(result.error) if result.error else 'Database fetch failed'
            return jsonify({'error': error_message}), 500
            
        entries = result.data
        if not entries:
            return jsonify({'trend': []})
            
        # Compute missing scores sequentially to stay within rate limits
        for entry in entries:
            if entry.get('emotion_score_score') is None:
                if not entry.get('transcript_user'):
                    continue
                    
                score, log = analyze_emotion(entry['transcript_user'])
                
                update_result = supabase.table('voice_entries').update({
                    'emotion_score_score': score,
                    'emotion_score_log': {
                        'timestamp': datetime.now().isoformat(),
                        'score': score,
                        'method': 'gpt_analysis'
                    }
                }).eq('id', entry['id']).eq('user_id', user_id).execute()
                
                # Check for errors in the result
                if hasattr(update_result, 'error') and update_result.error:
                    logger.error(f'Failed to update emotion score: {update_result.error}')
                    # Continue processing other entries even if one fails
                    
        # Re-fetch scores for aggregation
        scored_result = supabase.table('voice_entries').select('created_at, emotion_score_score').eq('user_id', user_id).not_.is_('emotion_score_score', 'null').order('created_at').execute()
        
        # Check for errors in the result
        if hasattr(scored_result, 'error') and scored_result.error:
            error_message = str(scored_result.error) if scored_result.error else 'Database fetch failed'
            return jsonify({'error': error_message}), 500
            
        scored_entries = scored_result.data
        if not scored_entries:
            return jsonify({'trend': []})
            
        # Build continuous timeline points per entry
        trend = [
            {
                'timestamp': entry['created_at'],
                'score': round(float(entry['emotion_score_score']), 2)
            }
            for entry in scored_entries
        ]
        
        # Sort by timestamp
        trend.sort(key=lambda x: x['timestamp'])
        
        return jsonify({'trend': trend})
        
    except Exception as e:
        logger.error(f'Emotion trend API error: {e}')
        return jsonify({'error': 'Internal server error'}), 500 