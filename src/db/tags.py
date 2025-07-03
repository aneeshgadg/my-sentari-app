"""
Database operations for tags.
"""

from typing import List, Dict, Any
from .base import BaseDB


class TagsDB(BaseDB):
    """Database operations for tags."""
    
    def get_all_tags(self, user_id: str) -> List[str]:
        """Get all tags for a user."""
        result = self.client.table('voice_entries').select('tags_user').eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        
        data = self.safe_get_data(result) or []
        tags = []
        for entry in data:
            if entry.get('tags_user'):
                tags.extend(entry['tags_user'])
        
        # Remove duplicates and sort
        return sorted(list(set(tags)))
    
    def get_entries_by_tag(self, user_id: str, tag: str) -> List[Dict[str, Any]]:
        """Get all entries that have a specific tag."""
        result = self.client.table('voice_entries').select('*').eq('user_id', user_id).contains('tags_user', [tag]).order('created_at', desc=True).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def get_entries_by_tags(self, user_id: str, tags: List[str]) -> List[Dict[str, Any]]:
        """Get all entries that have any of the specified tags."""
        result = self.client.table('voice_entries').select('*').eq('user_id', user_id).contains('tags_user', tags).order('created_at', desc=True).execute()
        self.handle_supabase_error(result)
        return self.safe_get_data(result) or []
    
    def get_tag_usage_count(self, user_id: str) -> Dict[str, int]:
        """Get usage count for each tag."""
        result = self.client.table('voice_entries').select('tags_user').eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        
        data = self.safe_get_data(result) or []
        tag_counts = {}
        
        for entry in data:
            if entry.get('tags_user'):
                for tag in entry['tags_user']:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return tag_counts
    
    def get_popular_tags(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular tags for a user."""
        tag_counts = self.get_tag_usage_count(user_id)
        
        # Sort by count and return top tags
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'tag': tag, 'count': count} 
            for tag, count in sorted_tags[:limit]
        ] 