"""
Database operations for user profiles.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseDB


class ProfilesDB(BaseDB):
    """Database operations for user profiles."""
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile."""
        result = self.client.table('profiles').select('profile').eq('user_id', user_id).single().execute()
        self.handle_supabase_error(result)
        data = self.safe_get_data(result)
        return data.get('profile') if data else None
    
    def upsert_profile(self, user_id: str, profile: Dict[str, Any], concepts: Optional[Dict[str, Any]] = None) -> bool:
        """Upsert user profile."""
        update_data = {
            'user_id': user_id,
            'profile': profile,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if concepts is not None:
            update_data['concepts'] = concepts
        
        result = self.client.table('profiles').upsert(update_data).execute()
        self.handle_supabase_error(result)
        return True
    
    def update_profile_field(self, user_id: str, field: str, value: Any) -> bool:
        """Update a specific field in the profile."""
        result = self.client.table('profiles').update({
            f'profile->{field}': value,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        return True
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete user profile."""
        result = self.client.table('profiles').delete().eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        return True
    
    def get_profile_concepts(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile concepts."""
        result = self.client.table('profiles').select('concepts').eq('user_id', user_id).single().execute()
        self.handle_supabase_error(result)
        data = self.safe_get_data(result)
        return data.get('concepts') if data else None
    
    def update_concepts(self, user_id: str, concepts: Dict[str, Any]) -> bool:
        """Update user concepts."""
        result = self.client.table('profiles').update({
            'concepts': concepts,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('user_id', user_id).execute()
        self.handle_supabase_error(result)
        return True 