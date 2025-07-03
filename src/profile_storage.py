"""
Profile storage interface - Main Backend App
"""

from typing import Optional, Dict
from .db.profiles import ProfilesDB


# Initialize database
profiles_db = ProfilesDB()


async def load_profile(user_id: str) -> Optional[Dict]:
    """
    Load profile from database
    
    Args:
        user_id: User identifier
        
    Returns:
        Profile dict if found, None otherwise
    """
    return profiles_db.get_profile(user_id)


async def save_profile_to_storage(user_id: str, profile: Dict) -> None:
    """
    Save profile to database
    
    Args:
        user_id: User identifier
        profile: Profile dict to save
    """
    profiles_db.upsert_profile(user_id, profile)


async def delete_profile_from_storage(user_id: str) -> None:
    """
    Delete profile from database
    
    Args:
        user_id: User identifier
    """
    profiles_db.delete_profile(user_id)


async def update_profile_field(user_id: str, field: str, value) -> None:
    """
    Update a specific field in the profile
    
    Args:
        user_id: User identifier
        field: Field name to update
        value: New value for the field
    """
    profiles_db.update_profile_field(user_id, field, value)


async def get_profile_concepts(user_id: str) -> Optional[list]:
    """
    Get profile concepts
    
    Args:
        user_id: User identifier
        
    Returns:
        List of concepts if found, None otherwise
    """
    profile = await load_profile(user_id)
    return profile.get('concepts') if profile else None


async def update_profile_concepts(user_id: str, concepts: list) -> None:
    """
    Update profile concepts
    
    Args:
        user_id: User identifier
        concepts: List of concepts to update
    """
    await update_profile_field(user_id, 'concepts', concepts) 