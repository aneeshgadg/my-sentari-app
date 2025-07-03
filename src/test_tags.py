from flask import request, jsonify
import openai
import os
import logging
from datetime import datetime
from .config import OPENAI_CHAT_MODEL

logger = logging.getLogger(__name__)

def classify_tags(transcript: str):
    """Classify tags for given transcript"""
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        prompt = f"""
        Analyze this transcript and generate relevant tags.
        Consider emotions, topics, and themes.
        
        Transcript: "{transcript}"
        
        Respond with a JSON object containing:
        - selectedTags: array of relevant tags
        - confidence: confidence score (0-1)
        - reasoning: brief explanation
        - emotionScore: emotional tone score (-1 to 1)
        """
        
        response = openai.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        result = response.choices[0].message.content
        
        # Parse JSON response
        import json
        parsed = json.loads(result)
        
        return {
            "selectedTags": parsed.get("selectedTags", []),
            "confidence": parsed.get("confidence", 0.8),
            "reasoning": parsed.get("reasoning", "Analysis completed"),
            "emotionScore": parsed.get("emotionScore", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Error in classify_tags: {e}")
        return {
            "selectedTags": ["reflection", "personal"],
            "confidence": 0.5,
            "reasoning": f"Error in analysis: {str(e)}",
            "emotionScore": 0.0
        }

def test_tags_endpoint():
    """Test tag classification functionality"""
    try:
        if request.method == 'GET':
            logger.info('Testing tag classification...')
            
            # Test with sample transcript
            test_transcript = "I feel really happy today and want to plan my future goals. I'm excited about the possibilities ahead."
            
            logger.info(f'Test transcript: {test_transcript}')
            
            # Call tag classification
            result = classify_tags(test_transcript)
            
            logger.info(f'Tag classification result: {result}')
            
            return jsonify({
                'success': True,
                'message': 'Tag classification test completed',
                'testTranscript': test_transcript,
                'result': {
                    'selectedTags': result['selectedTags'],
                    'confidence': result['confidence'],
                    'reasoning': result['reasoning'],
                    'emotionScore': result['emotionScore'],
                    'tagCount': len(result['selectedTags'])
                },
                'timestamp': datetime.now().isoformat()
            })
            
        elif request.method == 'POST':
            data = request.get_json()
            transcript = data.get('transcript')
            
            if not transcript:
                return jsonify({
                    'success': False,
                    'error': 'Missing transcript'
                }), 400
                
            logger.info(f'Testing custom transcript: {transcript[:100]}...')
            
            result = classify_tags(transcript)
            
            return jsonify({
                'success': True,
                'message': 'Custom transcript analysis completed',
                'result': {
                    'selectedTags': result['selectedTags'],
                    'confidence': result['confidence'],
                    'reasoning': result['reasoning'],
                    'emotionScore': result['emotionScore'],
                    'tagCount': len(result['selectedTags'])
                }
            })
            
    except Exception as e:
        logger.error(f'Tag classification test error: {e}')
        
        return jsonify({
            'success': False,
            'error': 'Tag classification test failed',
            'details': str(e),
            'message': 'Check your OpenAI API key configuration'
        }), 500 