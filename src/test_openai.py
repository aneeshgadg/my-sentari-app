from flask import request, jsonify
import openai
import os
import logging
from .config import OPENAI_CHAT_MODEL

logger = logging.getLogger(__name__)

def test_openai_endpoint():
    """Test OpenAI API connection"""
    try:
        # Check if API key is configured
        if not os.getenv('OPENAI_API_KEY'):
            return jsonify({
                'success': False,
                'error': 'OpenAI API key not configured',
                'message': 'Please add OPENAI_API_KEY to your environment variables'
            }), 400
            
        # Test OpenAI connection
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Simple test request
        response = openai.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a test assistant. Respond with exactly: "OpenAI connection successful"'
                },
                {
                    'role': 'user',
                    'content': 'Test connection'
                }
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'message': 'OpenAI API key is working correctly',
            'testResponse': result,
            'model': OPENAI_CHAT_MODEL,
            'apiKeyFormat': os.getenv('OPENAI_API_KEY')[:10] + '...'
        })
        
    except Exception as e:
        logger.error(f'OpenAI test error: {e}')
        
        return jsonify({
            'success': False,
            'error': 'OpenAI API test failed',
            'details': str(e),
            'message': 'Check your API key and credits'
        }), 500 