from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

def run_pipeline(text: str, user_id: str):
    """Run the core pipeline for text processing"""
    try:
        # This is a simplified version of the pipeline
        # In a real implementation, this would call the actual pipeline logic
        
        logger.info(f'Running pipeline for user {user_id} with text: {text[:100]}...')
        
        # Mock pipeline result - replace with actual pipeline logic
        result = {
            'entryId': f'entry_{user_id}_{hash(text) % 10000}',
            'reply': f'Processed: {text[:50]}...',
            'success': True
        }
        
        logger.info(f'Pipeline result: {result}')
        return result
        
    except Exception as e:
        logger.error(f'Pipeline error: {e}')
        return {
            'error': 'Pipeline failed',
            'details': str(e)
        }

def run_pipeline_endpoint():
    """Handle pipeline execution requests"""
    try:
        data = request.get_json()
        text = data.get('text')
        user_id = data.get('userId', 'demo')
        
        if not text or not isinstance(text, str) or len(text) == 0:
            return jsonify({'error': 'text required'}), 400
            
        result = run_pipeline(text, user_id)
        
        if 'error' in result:
            return jsonify(result), 500
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'Run pipeline API error: {e}')
        return jsonify({'error': 'Internal server error'}), 500 