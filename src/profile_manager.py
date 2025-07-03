"""
Profile management for user profiles - Main Backend App
"""

import re
from datetime import datetime
from typing import List, Dict, Optional

from .db.profiles import ProfilesDB
from .auth import get_user_id_from_request


# Initialize database
profiles_db = ProfilesDB()


def create_empty_profile(user_id: str) -> Dict:
    """Create a new empty profile for a user"""
    return {
        "user_id": user_id,
        "counters": {
            "emotions": {},
            "themes": {},
            "buckets": {}
        },
        "patterns": {},
        "traits": [],
        "load_score": 0,
        "last_updated": datetime.now().isoformat(),
        "history": [],
        "last_themes": [],
        "concepts": [],
        "quirks": {},
        "last_styles": [],
        "last_energy_levels": [],
        "last_insight_count": 0,
        "last_insight_text": None,
        "last_light_nudge_count": 0
    }


async def fetch_profile(user_id: str) -> Optional[Dict]:
    """Fetch or create a user profile"""
    # Try to load from database
    profile = profiles_db.get_profile(user_id)
    
    if not profile:
        # Create new profile
        profile = create_empty_profile(user_id)
        # Save to database
        profiles_db.upsert_profile(user_id, profile)
    
    return profile


def increment_counter(obj: Dict[str, int], key: str) -> None:
    """Increment a counter in a dictionary"""
    obj[key] = obj.get(key, 0) + 1


def update_profile(
    profile: Dict,
    inference: Dict,
    signals: Dict,
    raw_text: str,
    meta: Dict
) -> Dict:
    """
    Update profile with new entry data
    
    Args:
        profile: Current user profile
        inference: Inference results
        signals: Extracted signals
        raw_text: Raw transcript text
        meta: Transcript metadata
        
    Returns:
        Updated profile
    """
    emotion = inference.get('emotion')
    theme = inference.get('theme')
    bucket = inference.get('bucket')
    
    # Initialize counters if not present
    if 'counters' not in profile:
        profile['counters'] = {'emotions': {}, 'themes': {}, 'buckets': {}}
    
    # Update counters
    increment_counter(profile['counters']['emotions'], emotion)
    increment_counter(profile['counters']['themes'], theme)
    if bucket and bucket != "unknown":
        increment_counter(profile['counters']['buckets'], bucket)

    # Initialize history if not present
    if 'history' not in profile:
        profile['history'] = []
    
    # Append history
    entry = {
        "entry_id": meta.get('entry_id'),
        "timestamp": meta.get('timestamp'),
        "emotion": emotion,
        "theme": theme,
        "text": raw_text
    }
    profile['history'].append(entry)
    if len(profile['history']) > 50:
        profile['history'].pop(0)

    # Initialize last_themes if not present
    if 'last_themes' not in profile:
        profile['last_themes'] = []
    
    # Maintain last_themes queue (size 3)
    profile['last_themes'].append(theme)
    if len(profile['last_themes']) > 3:
        profile['last_themes'].pop(0)

    # Initialize patterns if not present
    if 'patterns' not in profile:
        profile['patterns'] = {}
    
    # Update token pattern frequency
    tokens = re.findall(r'\b[a-z0-9\']+\b', raw_text.lower())
    for token in tokens:
        profile['patterns'][token] = profile['patterns'].get(token, 0) + 1

    # Timestamp
    profile['last_updated'] = datetime.now().isoformat()

    # Initialize concepts if not present
    if 'concepts' not in profile:
        profile['concepts'] = []
    
    # Store concept tags into profile
    concept_tags = signals.get('concept_tags', [])
    if concept_tags:
        existing_concepts = profile['concepts']
        profile['concepts'] = list(set(existing_concepts + concept_tags))[-50:]

    # Initialize load_score if not present
    if 'load_score' not in profile:
        profile['load_score'] = 0
    
    # Burnout load score update
    if theme in ['overworking'] or emotion == 'fatigued':
        profile['load_score'] = min(100, profile['load_score'] + 8)
    if emotion in ['calm', 'refresh', 'relief']:
        profile['load_score'] = max(0, profile['load_score'] - 5)

    return profile


async def save_profile(user_id: str, profile: Dict) -> None:
    """Save profile to database"""
    profiles_db.upsert_profile(user_id, profile) 