from flask import request, jsonify
from supabase import Client
import logging
from functools import wraps
import inspect

logger = logging.getLogger(__name__)

def get_user_from_token(supabase: Client, token: str):
    """Get user from Supabase token"""
    try:
        # Verify the token with Supabase
        user = supabase.auth.get_user(token)
        return user.user if user else None
    except Exception as e:
        logger.error(f"Error getting user from token: {e}")
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
            
        token = auth_header.split(' ')[1]
        
        # Get supabase client from app context
        from flask import current_app
        supabase = current_app.config.get('SUPABASE_CLIENT')
        
        if not supabase:
            return jsonify({'error': 'Database connection not available'}), 500
            
        # Verify user
        user = get_user_from_token(supabase, token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
            
        # Add user to request context
        request.user = user
        
        # Check if the function expects user_id as the first parameter
        sig = inspect.signature(f)
        params = list(sig.parameters.keys())
        
        # If the function expects user_id as the first parameter, pass it
        if params and params[0] == 'user_id':
            return f(user.id, *args, **kwargs)
        else:
            # Otherwise, call the function without passing user_id
            return f(*args, **kwargs)
        
    return decorated_function

def get_user_id_from_request():
    """Get user ID from the current request"""
    if hasattr(request, 'user'):
        return request.user.id
    return None

def get_user_email_from_request():
    """Get user email from the current request"""
    if hasattr(request, 'user'):
        return request.user.email
    return None 