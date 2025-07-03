"""
Database operations for voice entries.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseDB


class VoiceEntriesDB(BaseDB):
    """Database operations for voice entries."""
    
    def get_user_entries(self, user_id: str, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all entries for a user."""
        query = self.client.table('voice_entries').select('*').eq('user_id', user_id).order('created_at', desc=True)
        
        if offset > 0:
            query = query.range(offset, offset + (limit or 100) - 1)
        elif limit:
            query = query.limit(limit)
        
        result = query.execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def get_entry_by_id(self, entry_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific entry by ID."""
        result = self.client.table('voice_entries').select('*').eq('id', entry_id).eq('user_id', user_id).single().execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result)
    
    def search_entries(self, user_id: str, query_text: str, limit: int = 20, similarity_threshold: float = 0.12) -> List[Dict[str, Any]]:
        """Search entries using vector similarity."""
        result = self.client.rpc('search_voice_entries', {
            'query_text': query_text,
            'user_id_input': user_id,
            'match_limit': limit,
            'similarity_threshold': similarity_threshold
        }).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def search_entries_by_tag(self, user_id: str, tag: str) -> List[Dict[str, Any]]:
        """Search entries by tag."""
        result = self.client.table('voice_entries').select('*').eq('user_id', user_id).contains('tags_user', [tag]).order('created_at', desc=True).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def search_entries_text(self, user_id: str, text: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search entries by text using ILIKE."""
        result = self.client.table('voice_entries').select('*').eq('user_id', user_id).ilike('transcript_user', f'%{text}%').order('created_at', desc=True).limit(limit).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def get_entries_with_filters(self, user_id: str, tags: Optional[List[str]] = None, 
                                start_date: Optional[str] = None, end_date: Optional[str] = None,
                                limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get entries with filters."""
        query = self.client.table('voice_entries').select('*').eq('user_id', user_id).order('created_at', desc=True)
        
        if tags:
            query = query.contains('tags_user', tags)
        if start_date:
            query = query.gte('created_at', start_date)
        if end_date:
            query = query.lte('created_at', end_date)
        
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def get_recent_emoji_entries(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent entries with emojis."""
        result = self.client.table('voice_entries').select('id, entry_emoji, transcript_user, created_at').eq('user_id', user_id).not_.is_('entry_emoji', 'null').order('created_at', desc=True).limit(limit).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def soft_delete_entry(self, entry_id: str, user_id: str) -> bool:
        """Soft delete an entry."""
        result = self.client.rpc('soft_delete_voice_entry', {
            'entry_id': entry_id,
            'uid': user_id
        }).execute()
        self.handle_supabase_error(result)
        return True
    
    def update_entry_transcript(self, entry_id: str, user_id: str, transcript: str) -> Dict[str, Any]:
        """Update entry transcript."""
        result = self.client.table('voice_entries').update({
            'transcript_user': transcript,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', entry_id).eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result)[0] if self.safe_get_data(result) else {}
    
    def update_entry_tags(self, entry_id: str, user_id: str, tags: List[str]) -> Dict[str, Any]:
        """Update entry tags."""
        result = self.client.table('voice_entries').update({
            'tags_user': tags,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', entry_id).eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result)[0] if self.safe_get_data(result) else {}
    
    def update_entry_field(self, entry_id: str, user_id: str, field: str, value: Any) -> Dict[str, Any]:
        """Update a specific field in an entry."""
        update_data = {
            field: value,
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self.client.table('voice_entries').update(update_data).eq('id', entry_id).eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result)[0] if self.safe_get_data(result) else {}
    
    def get_available_tags(self, user_id: str) -> List[str]:
        """Get all available tags for a user."""
        result = self.client.table('voice_entries').select('tags_user').eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        
        data = self.safe_get_data(result) or []
        tags = []
        for entry in data:
            if entry.get('tags_user'):
                tags.extend(entry['tags_user'])
        
        # Remove duplicates and sort
        return sorted(list(set(tags))) 