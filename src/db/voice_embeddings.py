"""
Database operations for voice embeddings.
"""

from typing import List, Dict, Any, Optional
from .base import BaseDB


class VoiceEmbeddingsDB(BaseDB):
    """Database operations for voice embeddings."""
    
    def upsert_embedding(self, user_id: str, entry_id: str, text: str, embedding: List[float]) -> bool:
        """Upsert an embedding for a voice entry."""
        result = self.client.table('voice_embeddings').upsert({
            'user_id': user_id,
            'entry_id': entry_id,
            'text': text,
            'embedding': embedding
        }).execute()
        self.handle_supabase_error(result)
        return True
    
    def search_similar_embeddings(self, user_id: str, query_embedding: List[float], 
                                 match_threshold: float = 0.75, match_count: int = 3) -> List[Dict[str, Any]]:
        """Search for similar embeddings using vector similarity."""
        result = self.client.rpc('match_embeddings', {
            'query_embedding': query_embedding,
            'match_threshold': match_threshold,
            'match_count': match_count,
            'p_user_id': user_id
        }).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def get_embedding_by_entry_id(self, entry_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get embedding by entry ID."""
        result = self.client.table('voice_embeddings').select('*').eq('entry_id', entry_id).eq('user_id', user_id).single().execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result)
    
    def delete_embedding(self, entry_id: str, user_id: str) -> bool:
        """Delete an embedding."""
        result = self.client.table('voice_embeddings').delete().eq('entry_id', entry_id).eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        return True
    
    def get_user_embeddings(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all embeddings for a user."""
        query = self.client.table('voice_embeddings').select('*').eq('user_id', user_id)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or [] 