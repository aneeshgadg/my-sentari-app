"""
Base database class with common functionality for all database operations.
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions


class BaseDB:
    """Base class for all database operations."""
    
    def __init__(self):
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get or create Supabase client."""
        if self._client is None:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            
            options = ClientOptions(
                schema='public',
                headers={
                    'X-Client-Info': 'sentri-backend'
                }
            )
            
            self._client = create_client(url, key, options)
        
        return self._client
    
    def handle_supabase_error(self, result: Any) -> None:
        """Handle Supabase API response errors."""
        if hasattr(result, 'error') and result.error:
            error_msg = str(result.error)
            raise Exception(f"Database error: {error_msg}")
    
    def safe_get_data(self, result: Any) -> Any:
        """Safely extract data from Supabase response."""
        if hasattr(result, 'data'):
            return result.data
        return result 